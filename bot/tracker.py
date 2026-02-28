"""
P&L tracker — logs every trade and tracks capital over time.
Handles compounding: capital = initial + all profits reinvested.
"""
import json
import os
from datetime import datetime
from bot.logger import get_logger

log = get_logger("tracker")

LEDGER_FILE = "ledger.json"


def load_ledger() -> dict:
    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE) as f:
            return json.load(f)
    return {
        "initial_capital": 0,
        "current_capital": 0,
        "total_trades": 0,
        "winning_trades": 0,
        "total_profit": 0,
        "trades": [],
    }


def save_ledger(ledger: dict):
    with open(LEDGER_FILE, "w") as f:
        json.dump(ledger, f, indent=2)


def initialize(capital_usdc: float):
    ledger = load_ledger()
    if ledger["initial_capital"] == 0:
        ledger["initial_capital"] = capital_usdc
        ledger["current_capital"] = capital_usdc
        save_ledger(ledger)
        log.info(f"Tracker initialized with ${capital_usdc:.4f} USDC")
    return ledger


def record_trade(market: str, profit_estimate: float, success: bool):
    ledger = load_ledger()
    ledger["total_trades"] += 1

    if success:
        ledger["winning_trades"] += 1
        ledger["total_profit"] += profit_estimate
        if True:  # COMPOUND always on
            ledger["current_capital"] += profit_estimate

    trade = {
        "ts": datetime.utcnow().isoformat(),
        "market": market[:80],
        "profit_est": round(profit_estimate, 6),
        "success": success,
        "capital_after": round(ledger["current_capital"], 6),
    }
    ledger["trades"].append(trade)
    save_ledger(ledger)

    win_rate = ledger["winning_trades"] / ledger["total_trades"] * 100
    total_return = ((ledger["current_capital"] / ledger["initial_capital"]) - 1) * 100
    log.info(
        f"P&L | Capital: ${ledger['current_capital']:.4f} | "
        f"Return: {total_return:+.2f}% | "
        f"Win rate: {win_rate:.1f}% ({ledger['winning_trades']}/{ledger['total_trades']})"
    )


def get_capital() -> float:
    return load_ledger().get("current_capital", 0)


def print_summary():
    ledger = load_ledger()
    if not ledger["initial_capital"]:
        return
    total_return = ((ledger["current_capital"] / ledger["initial_capital"]) - 1) * 100
    print(f"""
╔═══════════════════════════════════╗
║         BOT P&L SUMMARY          ║
╠═══════════════════════════════════╣
║ Initial capital:  ${ledger['initial_capital']:.4f}         ║
║ Current capital:  ${ledger['current_capital']:.4f}         ║
║ Total profit:     ${ledger['total_profit']:.4f}         ║
║ Return:           {total_return:+.2f}%             ║
║ Total trades:     {ledger['total_trades']}                 ║
║ Win rate:         {ledger['winning_trades']/max(ledger['total_trades'],1)*100:.1f}%               ║
╚═══════════════════════════════════╝
""")
