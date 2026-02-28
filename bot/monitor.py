"""
Monitors Polymarket CLOB for UP/DOWN arb opportunities across multiple
assets and timeframes simultaneously (async).
"""
import asyncio
import aiohttp
from typing import Optional
from dataclasses import dataclass
from config import GAMMA_HOST, ASSETS, SCAN_INTERVAL
from bot.logger import get_logger

log = get_logger("monitor")


@dataclass
class ArbOpportunity:
    market_question: str
    token_id_up: str
    token_id_down: str
    price_up: float
    price_down: float
    spread: float          # 1.0 - (price_up + price_down) — guaranteed profit per $1
    condition_id: str


async def fetch_active_markets(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch all active BTC/ETH/SOL/XRP Up/Down markets from Gamma API."""
    keywords = [f"{asset} Up or Down" for asset in ASSETS]
    markets = []

    for keyword in keywords:
        try:
            url = f"{GAMMA_HOST}/markets"
            params = {
                "active": "true",
                "closed": "false",
                "tag": "crypto",
                "limit": 100,
            }
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # Filter to Up/Down markets for our assets
                    for m in data:
                        q = m.get("question", "")
                        if any(asset in q for asset in ASSETS) and "Up or Down" in q:
                            markets.append(m)
        except Exception as e:
            log.warning(f"Error fetching markets for {keyword}: {e}")

    # Deduplicate by condition_id
    seen = set()
    unique = []
    for m in markets:
        cid = m.get("conditionId")
        if cid and cid not in seen:
            seen.add(cid)
            unique.append(m)

    log.debug(f"Found {len(unique)} active Up/Down markets")
    return unique


async def get_best_prices(session: aiohttp.ClientSession, token_id: str) -> Optional[float]:
    """Get the best ask price for a token from the CLOB orderbook."""
    try:
        url = f"https://clob.polymarket.com/book"
        params = {"token_id": token_id}
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=3)) as resp:
            if resp.status == 200:
                book = await resp.json()
                asks = book.get("asks", [])
                if asks:
                    # Best ask = lowest price someone is willing to sell at
                    return float(min(asks, key=lambda x: float(x["price"]))["price"])
    except Exception as e:
        log.debug(f"Error fetching price for {token_id}: {e}")
    return None


async def scan_market(session: aiohttp.ClientSession, market: dict) -> Optional[ArbOpportunity]:
    """Check a single market for an arb opportunity."""
    try:
        tokens = market.get("tokens", [])
        if len(tokens) < 2:
            return None

        up_token = next((t for t in tokens if t.get("outcome", "").upper() == "UP"), None)
        down_token = next((t for t in tokens if t.get("outcome", "").upper() == "DOWN"), None)

        if not up_token or not down_token:
            return None

        # Fetch both prices in parallel
        price_up, price_down = await asyncio.gather(
            get_best_prices(session, up_token["token_id"]),
            get_best_prices(session, down_token["token_id"]),
        )

        if price_up is None or price_down is None:
            return None

        total = price_up + price_down
        spread = 1.0 - total

        if spread > 0:
            return ArbOpportunity(
                market_question=market.get("question", ""),
                token_id_up=up_token["token_id"],
                token_id_down=down_token["token_id"],
                price_up=price_up,
                price_down=price_down,
                spread=spread,
                condition_id=market.get("conditionId", ""),
            )
    except Exception as e:
        log.debug(f"Error scanning market: {e}")
    return None


async def find_best_opportunity(session: aiohttp.ClientSession) -> Optional[ArbOpportunity]:
    """Scan ALL active markets simultaneously, return the best opportunity."""
    markets = await fetch_active_markets(session)
    if not markets:
        return None

    # Scan all markets in parallel
    results = await asyncio.gather(*[scan_market(session, m) for m in markets])

    opportunities = [r for r in results if r is not None]

    if not opportunities:
        return None

    # Return the one with the biggest spread
    best = max(opportunities, key=lambda o: o.spread)
    return best


async def monitor_loop(opportunity_queue: asyncio.Queue):
    """Continuously scan for opportunities and push them to the queue."""
    async with aiohttp.ClientSession() as session:
        log.info(f"Monitor started — scanning {len(ASSETS)} assets across all timeframes")
        while True:
            try:
                opp = await find_best_opportunity(session)
                if opp:
                    log.info(
                        f"Opportunity: {opp.market_question[:60]} | "
                        f"UP={opp.price_up:.3f} DOWN={opp.price_down:.3f} "
                        f"SPREAD={opp.spread:.3f} ({opp.spread*100:.1f}%)"
                    )
                    await opportunity_queue.put(opp)
                else:
                    log.debug("No opportunities found this scan")
            except Exception as e:
                log.error(f"Monitor error: {e}")

            await asyncio.sleep(SCAN_INTERVAL)
