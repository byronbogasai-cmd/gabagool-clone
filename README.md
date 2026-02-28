# Gabagool Clone — Polymarket Arb Bot

Spread arbitrage bot for Polymarket BTC/ETH/SOL/XRP Up/Down markets.

## Strategy

When `price_UP + price_DOWN < $1.00`, buying both sides guarantees profit regardless of direction.

## Setup

```bash
cp .env.example .env
# Fill in your Polymarket API credentials

pip install -r requirements.txt

python main.py --capital 5.00 --dry   # Test without real trades
python main.py --capital 5.00         # Live trading
python main.py --summary              # View P&L
```

## Deploy (Google Cloud Free Tier)

```bash
bash deploy/setup.sh
```
