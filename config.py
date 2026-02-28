import os
from dotenv import load_dotenv

load_dotenv()

# Polymarket CLOB API
CLOB_HOST = "https://clob.polymarket.com"
GAMMA_HOST = "https://gamma-api.polymarket.com"

# Credentials
API_KEY = os.getenv("POLY_API_KEY")
API_SECRET = os.getenv("POLY_API_SECRET")
API_PASSPHRASE = os.getenv("POLY_API_PASSPHRASE")
PRIVATE_KEY = os.getenv("POLY_PRIVATE_KEY")
WALLET_ADDRESS = os.getenv("POLY_WALLET_ADDRESS")

# Strategy parameters
MIN_SPREAD = float(os.getenv("MIN_SPREAD", "0.030"))      # 3% minimum gap
MAX_POSITION_PCT = float(os.getenv("MAX_POSITION_SIZE", "0.80"))
COMPOUND = os.getenv("COMPOUND", "true").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Assets to monitor (gabagool22 style: 4 assets x 3 timeframes)
ASSETS = ["BTC", "ETH", "SOL", "XRP"]

# How often to scan for opportunities (seconds)
SCAN_INTERVAL = 1.0

# Minimum USDC balance to keep (safety floor, don't bet below this)
MIN_BALANCE_USDC = 0.50
