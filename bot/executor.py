"""
Executes trades on Polymarket CLOB.
Places UP and DOWN orders simultaneously (parallel) to minimize slippage.
"""
import asyncio
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType, Side
from py_clob_client.constants import POLYGON
from config import API_KEY, API_SECRET, API_PASSPHRASE, PRIVATE_KEY, CLOB_HOST
from bot.monitor import ArbOpportunity
from bot.strategy import TradeDecision
from bot.logger import get_logger

log = get_logger("executor")


def build_client() -> ClobClient:
    return ClobClient(
        host=CLOB_HOST,
        chain_id=POLYGON,
        key=PRIVATE_KEY,
        creds={
            "apiKey": API_KEY,
            "secret": API_SECRET,
            "passphrase": API_PASSPHRASE,
        },
    )


async def place_order(client: ClobClient, token_id: str, price: float, size: float, label: str) -> dict:
    """Place a single taker order (market buy)."""
    try:
        order_args = OrderArgs(
            token_id=token_id,
            price=price,
            size=size,
            side=Side.BUY,
        )
        order = client.create_and_post_order(order_args)
        log.info(f"  {label} order placed: {size:.4f} USDC @ {price:.3f} | id={order.get('orderID', '?')[:12]}")
        return order
    except Exception as e:
        log.error(f"  {label} order FAILED: {e}")
        return {}


async def execute_arb(opp: ArbOpportunity, decision: TradeDecision) -> bool:
    """
    Execute both legs of the arb simultaneously.
    Returns True if both legs filled successfully.
    """
    client = build_client()

    log.info(f"Executing arb on: {opp.market_question[:60]}")
    log.info(f"  UP:   {decision.size_up:.4f} USDC @ {opp.price_up:.3f}")
    log.info(f"  DOWN: {decision.size_down:.4f} USDC @ {opp.price_down:.3f}")
    log.info(f"  Est. profit: {decision.net_profit_est:.4f} USDC")

    # Place BOTH orders simultaneously
    up_result, down_result = await asyncio.gather(
        place_order(client, opp.token_id_up, opp.price_up, decision.size_up, "UP"),
        place_order(client, opp.token_id_down, opp.price_down, decision.size_down, "DOWN"),
    )

    success = bool(up_result and down_result)
    if success:
        log.info(f"Both legs filled. Arb locked.")
    else:
        log.warning(f"Partial fill — manual review needed")

    return success
