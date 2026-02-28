"""
Decides whether to act on an opportunity based on:
- Minimum spread threshold (after estimated fees)
- Current capital available
- Dynamic position sizing (bigger spread = bigger bet)
"""
from dataclasses import dataclass
from config import MIN_SPREAD, MAX_POSITION_PCT, MIN_BALANCE_USDC
from bot.monitor import ArbOpportunity
from bot.logger import get_logger

log = get_logger("strategy")

# Estimated taker fee at ~50/50 markets (worst case)
ESTIMATED_FEE = 0.015  # 1.5% per side = 3% round trip


@dataclass
class TradeDecision:
    execute: bool
    size_up: float      # USDC to spend on UP
    size_down: float    # USDC to spend on DOWN
    net_profit_est: float
    reason: str


def decide(opp: ArbOpportunity, capital_usdc: float) -> TradeDecision:
    """Given an opportunity and available capital, decide trade size."""

    # Net spread after fees
    net_spread = opp.spread - (ESTIMATED_FEE * 2)

    if net_spread <= 0:
        return TradeDecision(
            execute=False,
            size_up=0, size_down=0, net_profit_est=0,
            reason=f"Spread {opp.spread:.3f} eaten by fees ({ESTIMATED_FEE*2:.3f})"
        )

    if opp.spread < MIN_SPREAD:
        return TradeDecision(
            execute=False,
            size_up=0, size_down=0, net_profit_est=0,
            reason=f"Spread {opp.spread*100:.1f}% below minimum {MIN_SPREAD*100:.1f}%"
        )

    available = capital_usdc - MIN_BALANCE_USDC
    if available <= 0:
        return TradeDecision(
            execute=False,
            size_up=0, size_down=0, net_profit_est=0,
            reason=f"Capital {capital_usdc:.4f} at/below safety floor"
        )

    # Dynamic sizing: scale position with spread size
    # Small spread (3%) → 30% of capital
    # Large spread (8%+) → 80% of capital
    position_pct = min(MAX_POSITION_PCT, opp.spread * 10)
    total_spend = available * position_pct

    # Split between UP and DOWN proportionally to their prices
    total_price = opp.price_up + opp.price_down
    size_up = total_spend * (opp.price_up / total_price)
    size_down = total_spend * (opp.price_down / total_price)

    # Estimated profit = spread * total_spend (one side always pays $1)
    net_profit_est = net_spread * total_spend

    return TradeDecision(
        execute=True,
        size_up=round(size_up, 4),
        size_down=round(size_down, 4),
        net_profit_est=round(net_profit_est, 6),
        reason=f"Net spread {net_spread*100:.2f}%, position {position_pct*100:.0f}% of capital"
    )
