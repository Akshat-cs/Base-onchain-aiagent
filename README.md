# Base Chain AI Trading Agent 🚀

An intelligent cryptocurrency trading bot for the Base blockchain that uses Anthropic's Claude AI to make sophisticated trading decisions based on real-time market data and comprehensive token analysis.

## ✨ Features

- **AI-Powered Decisions**: Uses Claude AI to analyze tokens and make Buy/Sell/Hold/Avoid decisions
- **Real-Time Data**: Fetches live market data from Bitquery API
- **Base Chain Focus**: Specifically designed for Base blockchain ecosystem
- **Risk Management**: Built-in risk assessment and portfolio diversification
- **Comprehensive Analysis**: Analyzes market cap, liquidity, volatility, holder concentration, and more
- **Paper Trading Mode**: Test strategies without real money
- **Detailed Logging**: Track all decisions and analysis

## 🛠️ Tech Stack

- **Python 3.8+**
- **Anthropic Claude API** - AI decision making
- **Bitquery API** - Base chain data
- **asyncio** - Async operations
- **GraphQL** - Data queries
- **WebSocket** - Real-time streams

## 📋 Prerequisites

1. **Python 3.8 or higher**
2. **Claude API Key** from [Anthropic Console](https://console.anthropic.com)
3. **Bitquery API Token** from [Bitquery.io](https://bitquery.io)
4. **Base Chain Wallet Address** to monitor

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd base-chain-ai-trading-agent
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Setup

Create a `.env` file in the project root:

```bash
# Required API Keys
CLAUDE_API_KEY=your_claude_api_key
BITQUERY_TOKEN=your-bitquery-token-here
WALLET_ADDRESS=your-wallet-address
```

### 4. Run the Trading Agent

```bash
python base_main.py
```

## 📊 What It Analyzes

### Token Metrics

- **Current Price** - Latest USD price
- **Market Cap** - Total market valuation
- **Supply Data** - Circulating and total supply
- **Trading Volume** - 24h trading activity
- **Liquidity** - Available liquidity in USD
- **Volatility** - Price stability analysis
- **Holder Distribution** - Top holder concentration
- **Trading Activity** - Unique buyers, sellers, trade count

### AI Decision Criteria

- **Market Cap Range**: Prefers $1M-$100M (growth sweet spot)
- **Liquidity Threshold**: Minimum $50K for safe entry/exit
- **Volatility Assessment**: Moderate volatility preferred
- **Whale Risk**: Avoids tokens with >50% top holder concentration
- **Base Ecosystem Fit**: Considers utility in Base DeFi

## 🤖 AI Decision Types

| Decision  | Description                                 | Action                            |
| --------- | ------------------------------------------- | --------------------------------- |
| **Buy**   | Strong fundamentals, good entry opportunity | Execute purchase(not implemented) |
| **Sell**  | Risk factors or profit-taking signal        | Execute sale(not implemented)     |
| **Hold**  | Maintain current position                   | No action                         |
| **Avoid** | High risk or poor fundamentals              | Skip token                        |
