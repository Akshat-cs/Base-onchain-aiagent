import asyncio
import threading
import time
import os
from dotenv import load_dotenv

from base_bitquery_utils import (
    get_trending_tokens,
    get_token_volatility,
    get_token_price_and_marketcap,
    get_wallet_balances,
    get_top_holders,
    calculate_market_cap,
    subscribe_to_base_trades
)
from ai_decision import analyze_token_and_decide

load_dotenv()

WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")
BASE_WETH_ADDRESS = "0x4200000000000000000000000000000000000006"  # Wrapped ETH on Base

### ----------- AI Trading Loop for Base Chain ----------- ###

def ai_trading_loop():
    print("Starting Base Chain AI Trading Loop...")

    while True:
        try:
            print("\n" + "="*60)
            print("Fetching trending tokens on Base...")
            
            # Get trending tokens
            trending_data = get_trending_tokens()
            tokens = trending_data.get("data", {}).get("EVM", {}).get("DEXTradeByTokens", [])
            
            if not tokens:
                print("No trending tokens found on Base.")
                time.sleep(30)
                continue

            print(f"Found {len(tokens)} trending tokens")
            
            # Get wallet balances
            print("Fetching wallet balances...")
            wallet_data = get_wallet_balances(WALLET_ADDRESS)
            balances = wallet_data.get("data", {}).get("EVM", {}).get("BalanceUpdates", [])

            owned_tokens = set()
            for balance in balances:
                currency = balance.get("Currency", {})
                smart_contract = currency.get("SmartContract")
                if smart_contract:
                    owned_tokens.add(smart_contract.lower())

            print(f"Wallet holds {len(owned_tokens)} different tokens")

            # Analyze each trending token
            for i, token_data in enumerate(tokens[:5], 1):  # Limit to top 5 for demo
                try:
                    currency = token_data["Trade"]["Currency"]
                    token_address = currency["SmartContract"]
                    symbol = currency["Symbol"]
                    name = currency["Name"]
                    
                    # Skip tokens with invalid addresses
                    if not token_address or token_address == "" or len(token_address) < 10:
                        print(f"\n[{i}/5] Skipping {symbol} - Invalid address: {token_address}")
                        continue
                    
                    buyers = token_data.get("buyers", 0)
                    volume = token_data.get("volume", 0)
                    trades = token_data.get("trades", 0)

                    print(f"\n[{i}/5] Analyzing: {symbol} ({name})")
                    print(f"  Address: {token_address}")
                    
                    # Safe formatting for volume (handle non-numeric values)
                    try:
                        volume_str = f"${float(volume):,.2f}" if volume != "Unknown" and volume is not None else "Unknown"
                    except (ValueError, TypeError):
                        volume_str = "Unknown"
                    
                    print(f"  Buyers: {buyers}, Volume: {volume_str}, Trades: {trades}")

                    # Get token volatility with error handling
                    print("  Fetching volatility data...")
                    try:
                        volatility_data = get_token_volatility(token_address)
                        volatility_info = volatility_data.get("data", {}).get("EVM", {}).get("DEXTradeByTokens", [])
                        
                        if volatility_info:
                            volatility = volatility_info[0].get("volatility", "Unknown")
                            avg_price = volatility_info[0].get("avg_price", "Unknown")
                            
                            # Get max/min prices from Trade object
                            trade_data = volatility_info[0].get("Trade", {})
                            max_price = trade_data.get("max_price", "Unknown")
                            min_price = trade_data.get("min_price", "Unknown")
                            
                            # Convert to float if possible
                            try:
                                if volatility != "Unknown" and volatility is not None:
                                    volatility = round(float(volatility), 4)
                            except (ValueError, TypeError):
                                volatility = "Unknown"
                                
                            try:
                                if avg_price != "Unknown" and avg_price is not None:
                                    avg_price = round(float(avg_price), 6)
                            except (ValueError, TypeError):
                                avg_price = "Unknown"
                        else:
                            volatility = "Unknown"
                            avg_price = "Unknown"
                    except Exception as e:
                        print(f"    Warning: Could not fetch volatility data - {e}")
                        volatility = "Unknown"
                        avg_price = "Unknown"

                    # Get market cap with error handling
                    print("  Calculating market cap...")
                    try:
                        market_cap = calculate_market_cap(token_address)
                    except Exception as e:
                        print(f"    Warning: Could not calculate market cap - {e}")
                        market_cap = "Unknown"

                    # Get top holders for concentration analysis with error handling
                    print("  Analyzing holder concentration...")
                    try:
                        holders_data = get_top_holders(token_address)
                        holders = holders_data.get("data", {}).get("EVM", {}).get("BalanceUpdates", [])
                        
                        holder_concentration = "Unknown"
                        if len(holders) >= 2:
                            try:
                                top_holder_balance = float(holders[0].get("balance", 0))
                                total_balance = sum(float(h.get("balance", 0)) for h in holders[:10])  # Top 10 holders
                                
                                if total_balance > 0:
                                    holder_concentration = round(100 * top_holder_balance / total_balance, 2)
                            except (ValueError, TypeError):
                                holder_concentration = "Unknown"
                    except Exception as e:
                        print(f"    Warning: Could not analyze holders - {e}")
                        holder_concentration = "Unknown"

                    # Get liquidity info (from volume data we already have)
                    liquidity_usd = volume  # Use trading volume as liquidity proxy

                    # Check if wallet holds this token
                    wallet_holds_token = token_address.lower() in owned_tokens

                    # Prepare data for AI decision
                    token_analysis_data = {
                        "name": name,
                        "symbol": symbol,
                        "market_cap": market_cap,
                        "liquidity_usd": liquidity_usd,
                        "volatility": volatility,
                        "holder_concentration": holder_concentration,
                        "wallet_holds_token": wallet_holds_token,
                        "trading_volume": volume,
                        "unique_buyers": buyers,
                        "total_trades": trades,
                        "avg_price": avg_price
                    }

                    # Safe formatting for market cap
                    try:
                        if isinstance(market_cap, (int, float)) and market_cap != "Unknown":
                            market_cap_str = f"${float(market_cap):,.2f}"
                        else:
                            market_cap_str = str(market_cap)
                    except (ValueError, TypeError):
                        market_cap_str = "Unknown"

                    print(f"  Market Cap: {market_cap_str}")
                    print(f"  Volatility: {volatility}")
                    print(f"  Top Holder %: {holder_concentration}%")
                    print(f"  Wallet Holds: {'Yes' if wallet_holds_token else 'No'}")

                    # Get AI decision
                    print("  Getting AI decision...")
                    decision = analyze_token_and_decide(token_analysis_data)
                    
                    print(f"  🤖 AI Decision: {decision}")

                    # Execute trading logic based on decision
                    if decision == "Buy":
                        if wallet_holds_token:
                            print(f"  ✅ Already holding {symbol}, considering additional purchase...")
                        else:
                            print(f"  🚀 Would execute BUY order for {symbol}")
                            # TODO: Implement actual buy logic here
                            
                    elif decision == "Sell":
                        if wallet_holds_token:
                            print(f"  📉 Would execute SELL order for {symbol}")
                            # TODO: Implement actual sell logic here
                        else:
                            print(f"  ⚠️  Cannot SELL {symbol}, wallet doesn't hold it")
                            
                    elif decision == "Hold":
                        if wallet_holds_token:
                            print(f"  🤝 Holding position in {symbol}")
                        else:
                            print(f"  ⌛ Monitoring {symbol}, not taking action")
                            
                    elif decision == "Avoid":
                        print(f"  🚫 Avoiding {symbol} due to risk factors")
                    else:
                        print(f"  ❓ Uncertain about {symbol}, holding off for now")

                except Exception as e:
                    print(f"  ❌ Error analyzing token: {e}")
                    continue

            print(f"\n{'='*60}")
            print("Analysis complete. Waiting 120 seconds before next cycle...")
            time.sleep(120)  # Wait 2 minutes before next analysis

        except Exception as e:
            print(f"Error in trading loop: {e}")
            time.sleep(60)  # Wait 1 minute on error

### ----------- Stream Listener for Base Chain ----------- ###

async def run_base_trade_stream():
    print("Starting Base Chain DEX Trade Stream...")
    await subscribe_to_base_trades()

### ----------- Entry Point ----------- ###

if __name__ == "__main__":
    try:
        print("🔷 Base Chain AI Trading Agent Starting...")
        print(f"📍 Monitoring wallet: {WALLET_ADDRESS}")
        print(f"🌐 Network: Base Chain")
        print(f"💱 Base currency: WETH ({BASE_WETH_ADDRESS})")
        
        # Uncomment to run trade stream in background
        # trade_stream_thread = threading.Thread(
        #     target=lambda: asyncio.run(run_base_trade_stream()), 
        #     daemon=True
        # )
        # trade_stream_thread.start()

        # Run AI Trading Loop (blocking)
        ai_trading_loop()

    except KeyboardInterrupt:
        print("\n🛑 Shutting down Base Chain Trading Agent...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")