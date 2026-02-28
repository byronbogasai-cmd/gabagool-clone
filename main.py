"""
Gabagool Clone — Polymarket UP/DOWN Spread Arbitrage Bot
=========================================================
Strategy:
  1. Monitor BTC/ETH/SOL/XRP Up/Down markets simultaneously
  2. When UP_price + DOWN_price < 1.00 (after fees), both sides are bought
  3. One side always resolves to $1.00 → guaranteed profit
  4. All profits are compounded automatically

Usage:
  python main.py --capital 5.00          # Start with $5 USDC
  python main.py --capital 5.00 --dry    # Dry run (no real orders)
  python main.py --summary               # Show P&L summary
"""
import asyncio
import argparse
import signal
from config import MIN_SPREAD
from bot.monitor import monitor_loop, ArbOpportunity
from bot.strategy import decide
from bot.executor import execute_arb
from bot.tracker import initialize, record_trade, get_capital, print_summary
from bot.logger import get_logger

log = get_logger("main")
running = True


def handle_exit(sig, frame):
    global running
    log.info("Shutting down bot...")
    running = False
    print_summary()


async def trade_loop(opportunity_queue: asyncio.Queue, dry_run: bool):
    """Consume opportunities and execute trades."""
    while running:
        try:
            opp: ArbOpportunity = await asyncio.wait_for(
                opportunity_queue.get(), timeout=5.0
            )
        except asyncio.TimeoutError:
            continue

        capital = get_capital()
        decision = decide(opp, capital)

        if not decision.execute:
            log.debug(f"Skipped: {decision.reason}")
            continue

        log.info(f"TRADE | {decision.reason}")

        if dry_run:
            log.info(f"[DRY RUN] Would trade: UP={decision.size_up:.4f} DOWN={decision.size_down:.4f}")
            record_trade(opp.market_question, decision.net_profit_est, success=True)
            continue

        success = await execute_arb(opp, decision)
        record_trade(opp.market_question, decision.net_profit_est, success=success)


async def run(initial_capital: float, dry_run: bool):
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    initialize(initial_capital)
    log.info(f"Bot starting | Capital: ${initial_capital:.4f} | Min spread: {MIN_SPREAD*100:.1f}% | Dry: {dry_run}")

    queue = asyncio.Queue(maxsize=10)

    await asyncio.gather(
        monitor_loop(queue),
        trade_loop(queue, dry_run),
    )


def main():
    parser = argparse.ArgumentParser(description="Gabagool Clone — Polymarket Arb Bot")
    parser.add_argument("--capital", type=float, default=5.0, help="Starting capital in USDC")
    parser.add_argument("--dry", action="store_true", help="Dry run — monitor only, no real trades")
    parser.add_argument("--summary", action="store_true", help="Print P&L summary and exit")
    args = parser.parse_args()

    if args.summary:
        print_summary()
        return

    asyncio.run(run(args.capital, args.dry))


if __name__ == "__main__":
    main()
