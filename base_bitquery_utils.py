import requests
import json
import os
from dotenv import load_dotenv
import asyncio
from gql import Client, gql
from gql.transport.websockets import WebsocketsTransport
import base_config as config

load_dotenv()

BITQUERY_REST_URL = "https://streaming.bitquery.io/eap"
BITQUERY_WS_URL = "wss://streaming.bitquery.io/eap"
BITQUERY_TOKEN = config.BITQUERY_TOKEN
wallet_address = config.WALLET_ADDRESS

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {BITQUERY_TOKEN}"
}

### ----------- REST API Queries for BASE CHAIN ----------- ###

def run_bitquery(query: str, variables: dict = {}):
    payload = json.dumps({
        "query": query,
        "variables": json.dumps(variables)
    })
    response = requests.post(BITQUERY_REST_URL, headers=HEADERS, data=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Query failed with status {response.status_code}: {response.text}")

# 1. Get Top Trending Tokens on Base (Last 1 Hour)
def get_trending_tokens():
    # Calculate 1 hour ago timestamp
    from datetime import datetime, timedelta
    one_hour_ago = (datetime.utcnow() - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    query = f"""
    query TrendingTokens {{
      EVM(network: base, dataset: realtime) {{
        DEXTradeByTokens(
          limit: {{count: 10}}
          orderBy: {{descendingByField: "buyers"}}
          where: {{Trade: {{Currency: {{SmartContract: {{notIn: ["0x4200000000000000000000000000000000000006", "0x0000000000000000000000000000000000000000"]}}}}}}, Block: {{Time: {{since: "{one_hour_ago}"}}}}}}
        ) {{
          Trade {{
            Currency {{
              Name
              Symbol
              SmartContract
            }}
          }}
          buyers: uniq(of: Trade_Buyer)
          sellers: uniq(of: Trade_Seller)
          trades: count
          volume: sum(of: Trade_Side_AmountInUSD)
        }}
      }}
    }}
    """
    return run_bitquery(query)

# 2. Get Token Volatility (Updated query)
def get_token_volatility(token_address: str):
    query = f"""
    query TokenVolatility {{
      EVM(network: base, dataset: realtime) {{
        DEXTradeByTokens(
          where: {{Trade: {{Currency: {{SmartContract: {{is: "{token_address}"}}}}, Side: {{Currency: {{SmartContract: {{is: "0x4200000000000000000000000000000000000006"}}}}, AmountInUSD: {{gt: "100"}}}}}}}}
        ) {{
          volatility: standard_deviation(of: Trade_PriceInUSD)
          avg_price: average(of: Trade_PriceInUSD)
          Trade {{
            max_price: PriceInUSD(maximum: Trade_PriceInUSD)
            min_price: PriceInUSD(minimum: Trade_PriceInUSD)
          }}
        }}
      }}
    }}
    """
    return run_bitquery(query)

# 3. Get Token Market Cap (latest price and calculate with supply)
def get_token_price_and_marketcap(token_address: str):
    query = f"""
    query TokenMarketData {{
      EVM(network: base, dataset: realtime) {{
        DEXTradeByTokens(
          where: {{Trade: {{Currency: {{SmartContract: {{is: "{token_address}"}}}}}}}}
          orderBy: {{descending: Block_Time}}
          limit: {{count: 1}}
        ) {{
          Trade {{
            PriceInUSD
            Currency {{
              Name
              Symbol
              SmartContract
            }}
          }}
        }}
      }}
    }}
    """
    return run_bitquery(query)

# 4. Get Wallet Balances on Base
def get_wallet_balances(wallet_address: str):
    query = f"""
    query WalletBalances {{
      EVM(network: base, dataset: combined, aggregates: yes) {{
        BalanceUpdates(
          where: {{ BalanceUpdate: {{ Address: {{ is: "{wallet_address}" }} }} }}
          orderBy: {{ descendingByField: "balance" }}
        ) {{
          BalanceUpdate {{
            Address
          }}
          Currency {{
            Name
            Symbol
            SmartContract
          }}
          balance: sum(of: BalanceUpdate_Amount, selectWhere: {{ gt: "0" }})
        }}
      }}
    }}
    """
    return run_bitquery(query)

# 5. Get Top Token Holders
def get_top_holders(token_address: str):
    query = f"""
    query TopHolders {{
      EVM(network: base, dataset: combined, aggregates: yes) {{
        BalanceUpdates(
          orderBy: {{ descendingByField: "balance" }}
          limit: {{ count: 50 }}
          where: {{
            Currency: {{ SmartContract: {{ is: "{token_address}" }} }}
          }}
        ) {{
          BalanceUpdate {{
            Address
          }}
          Currency {{
            Name
            Symbol
            SmartContract
          }}
          balance: sum(of: BalanceUpdate_Amount, selectWhere: {{ gt: "0" }})
        }}
      }}
    }}
    """
    return run_bitquery(query)

# 6. Get Token Supply for Market Cap Calculation
def get_token_supply(token_address: str):
    query = f"""
    query TokenSupply {{
      EVM(network: base, dataset: combined) {{
        Transfers(
          where: {{Transfer: {{Currency: {{SmartContract: {{is: "{token_address}"}}}}, Success: true}}}}
        ) {{
          minted: sum(of: Transfer_Amount, if: {{Transfer: {{Sender: {{is: "0x0000000000000000000000000000000000000000"}}}}}})
          burned: sum(
            of: Transfer_Amount
            if: {{Transfer: {{Receiver: {{is: "0x0000000000000000000000000000000000000000"}}}}}}
          )
        }}
      }}
    }}
    """
    return run_bitquery(query)

### ----------- WebSocket Stream for Base Chain ----------- ###

async def subscribe_to_base_trades():
    token = BITQUERY_TOKEN
    ws_url = f"wss://streaming.bitquery.io/eap?token={token}"

    transport = WebsocketsTransport(
        url=ws_url,
        headers={"Sec-WebSocket-Protocol": "graphql-ws"}
    )

    query = gql("""
    subscription BaseTradesStream {
      EVM(network: base) {
        DEXTrades {
          Block {
            Time
            Number
          }
          Transaction {
            Hash
          }
          Trade {
            Buy {
              Amount
              PriceInUSD
              Currency {
                Symbol
                SmartContract
              }
              Buyer
            }
            Sell {
              Amount
              PriceInUSD
              Currency {
                Symbol
                SmartContract
              }
              Seller
            }
            Dex {
              ProtocolName
              ProtocolFamily
            }
          }
        }
      }
    }
    """)

    await transport.connect()
    print("Connected to Base Chain Trade Stream")

    try:
        async for result in transport.subscribe(query):
            print(result)
    except asyncio.CancelledError:
        print("Subscription cancelled.")
    finally:
        await transport.close()
        print("Transport closed")

# Helper function to calculate market cap
def calculate_market_cap(token_address: str):
    """Calculate market cap = price * circulating supply"""
    try:
        # Get current price
        price_data = get_token_price_and_marketcap(token_address)
        trades = price_data.get("data", {}).get("EVM", {}).get("DEXTradeByTokens", [])
        
        if not trades:
            return "Unknown"
            
        current_price = trades[0].get("Trade", {}).get("PriceInUSD", 0)
        
        # Get token supply
        supply_data = get_token_supply(token_address)
        transfers = supply_data.get("data", {}).get("EVM", {}).get("Transfers", [])
        
        if not transfers:
            return "Unknown"
            
        minted = float(transfers[0].get("minted", 0))
        burned = float(transfers[0].get("burned", 0))
        circulating_supply = minted - burned
        
        if current_price and circulating_supply:
            market_cap = current_price * circulating_supply
            return market_cap
        else:
            return "Unknown"
            
    except Exception as e:
        print(f"Error calculating market cap: {e}")
        return "Unknown"