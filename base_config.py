# Configuration for Base Chain AI Trading Agent
# IMPORTANT: Move these to environment variables for security!

import os
from dotenv import load_dotenv

load_dotenv()

# API Keys - Move to environment variables!
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "your-claude-api-key-here")  # Add this
BITQUERY_TOKEN = os.getenv("BITQUERY_TOKEN", "your-bitquery-token-here")

# Base Chain Configuration
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS", "your-base-wallet-address-here")
BASE_CHAIN_ID = 8453  # Base mainnet chain ID

# Base Chain Token Addresses
BASE_WETH = "0x4200000000000000000000000000000000000006"  # Wrapped ETH on Base
BASE_USDC = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"  # USDC on Base

# Trading Parameters
MAX_TOKENS_TO_ANALYZE = 10  # Limit API calls
ANALYSIS_INTERVAL = 120  # Seconds between analysis cycles
MIN_LIQUIDITY_USD = 50000  # Minimum liquidity for trading
MAX_HOLDER_CONCENTRATION = 50  # Max % for top holder
MIN_MARKET_CAP = 100000  # Minimum market cap ($100K)
MAX_MARKET_CAP = 100000000  # Maximum market cap ($100M)

# Risk Management
MAX_POSITION_SIZE_PCT = 20  # Max % of portfolio in single token
STOP_LOSS_PCT = 10  # Stop loss percentage
TAKE_PROFIT_PCT = 50  # Take profit percentage

# Base Chain RPC URLs (for future trade execution)
BASE_RPC_URLS = [
    "https://mainnet.base.org",
    "https://base-mainnet.public.blastapi.io",
    "https://base.meowrpc.com"
]

# DEX Router Addresses on Base (for future trade execution)
UNISWAP_V3_ROUTER = "0x2626664c2603336E57B271c5C0b26F421741e481"
PANCAKESWAP_ROUTER = "0x8cFe327CEc66d1C090Dd72bd0FF11d690C33a2Eb"

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FILE = "base_trading_agent.log"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# Notification Settings
ENABLE_TELEGRAM_NOTIFICATIONS = False
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Safety Settings
ENABLE_PAPER_TRADING = True  # Set to True for testing
ENABLE_REAL_TRADING = False  # Set to True only when ready for real trades
MAX_DAILY_TRADES = 10  # Limit number of trades per day
TRADING_HOURS = {
    "start": 0,  # 24-hour format, 0 = midnight UTC
    "end": 23    # 23 = 11 PM UTC
}

# Advanced Features
ENABLE_SENTIMENT_ANALYSIS = False  # Future feature
ENABLE_TECHNICAL_INDICATORS = False  # Future feature
ENABLE_SOCIAL_METRICS = False  # Future feature

# Database Configuration (for future trade history tracking)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///base_trading.db")

# Webhook Configuration (for future integrations)
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

# Performance Tracking
TRACK_PERFORMANCE = True
BENCHMARK_TOKEN = BASE_WETH  # Compare performance against WETH

print("Base Chain Trading Agent Configuration Loaded")
print(f"Paper Trading: {ENABLE_PAPER_TRADING}")
print(f"Real Trading: {ENABLE_REAL_TRADING}")
print(f"Wallet: {WALLET_ADDRESS[:6]}...{WALLET_ADDRESS[-4:] if WALLET_ADDRESS != 'your-base-wallet-address-here' else 'NOT_SET'}")