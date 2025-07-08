import anthropic
import os
from dotenv import load_dotenv
import config

load_dotenv()

# Initialize Claude client
client = anthropic.Anthropic(
    api_key=config.CLAUDE_API_KEY,  # You'll need to add this to config
)

def analyze_token_and_decide(token_data):
    """
    Enhanced AI decision making for Base chain tokens using Claude
    """
    
    # Helper function to format values safely
    def safe_format(value, prefix="", suffix=""):
        if value == "Unknown" or value is None:
            return "Unknown"
        try:
            if isinstance(value, (int, float)):
                return f"{prefix}{value:,.2f}{suffix}"
            else:
                return str(value)
        except:
            return "Unknown"
    
    # Format values safely
    market_cap_str = safe_format(token_data['market_cap'], "$")
    volume_str = safe_format(token_data.get('trading_volume', 'Unknown'), "$")
    liquidity_str = safe_format(token_data['liquidity_usd'], "$")
    avg_price_str = safe_format(token_data.get('avg_price', 'Unknown'), "$")
    
    prompt = f"""Analyze this Base chain token and make a trading decision:

TOKEN DETAILS:
• Name: {token_data['name']}
• Symbol: {token_data['symbol']}
• Market Cap: {market_cap_str}
• Trading Volume (24h): {volume_str}
• Liquidity (USD): {liquidity_str}
• Price Volatility: {token_data['volatility']}
• Average Price: {avg_price_str}

TRADING METRICS:
• Unique Buyers: {token_data.get('unique_buyers', 'Unknown')}
• Total Trades: {token_data.get('total_trades', 'Unknown')}
• Top Holder Concentration: {token_data['holder_concentration']}%

PORTFOLIO STATUS:
• Currently Holding: {token_data['wallet_holds_token']}

DECISION CRITERIA for Base Chain Trading:
1. Market Cap: Prefer $1M-$100M range (sweet spot for growth)
2. Liquidity: Minimum $50K for safe entry/exit
3. Volatility: Moderate volatility preferred (not too stable, not too wild)
4. Holder Concentration: Avoid if top holder has >50% (whale risk)
5. Trading Activity: Look for sustained volume and buyer interest
6. Base Chain Ecosystem: Consider if token has utility in Base DeFi

RISK ASSESSMENT:
• High Risk: New tokens (<24h), extreme volatility, whale concentration >70%
• Medium Risk: Moderate metrics, some red flags but manageable
• Low Risk: Established tokens, good liquidity, distributed ownership

Note: If data is "Unknown", consider this as a risk factor but don't automatically avoid.

Based on this analysis, decide whether to 'Buy', 'Sell', 'Hold', or 'Avoid'.

Respond with ONLY ONE WORD: Buy, Sell, Hold, or Avoid."""

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",  # Latest Claude model
            max_tokens=10,
            temperature=0.1,  # Low temperature for consistent decisions
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        decision = response.content[0].text.strip()
        
        # Validate response
        valid_decisions = ["Buy", "Sell", "Hold", "Avoid"]
        if decision not in valid_decisions:
            print(f"Claude returned invalid decision: {decision}, defaulting to Hold")
            return "Hold"
            
        return decision

    except Exception as e:
        print(f"Error from Claude API: {e}")
        return "Hold"  # Default to safe option

def get_detailed_analysis(token_data):
    """
    Get a detailed explanation of the trading decision using Claude
    """
    
    # Helper function to format values safely
    def safe_format(value, prefix="", suffix=""):
        if value == "Unknown" or value is None:
            return "Unknown"
        try:
            if isinstance(value, (int, float)):
                return f"{prefix}{value:,.2f}{suffix}"
            else:
                return str(value)
        except:
            return "Unknown"
    
    market_cap_str = safe_format(token_data['market_cap'], "$")
    volume_str = safe_format(token_data.get('trading_volume', 'Unknown'), "$")
    
    prompt = f"""Provide a detailed analysis of this Base chain token:

TOKEN: {token_data['name']} ({token_data['symbol']})
Market Cap: {market_cap_str}
Volume: {volume_str}
Volatility: {token_data['volatility']}
Holder Concentration: {token_data['holder_concentration']}%

Provide:
1. Risk Level (Low/Medium/High)
2. Key Strengths
3. Main Concerns  
4. Recommendation Reasoning

Keep response under 200 words."""

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=200,
            temperature=0.3,
            messages=[
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
        )

        return response.content[0].text.strip()

    except Exception as e:
        print(f"Error getting detailed analysis from Claude: {e}")
        return "Analysis unavailable due to API error."

def analyze_portfolio_allocation(current_holdings, new_token_data):
    """
    Analyze if buying this token fits portfolio diversification strategy using Claude
    """
    prompt = f"""Portfolio Analysis for Base Chain:

CURRENT HOLDINGS: {len(current_holdings)} tokens
NEW TOKEN: {new_token_data['symbol']}
New Token Market Cap: ${new_token_data['market_cap']}

DIVERSIFICATION RULES:
• Max 20% in any single token
• Prefer mix of market caps (large, mid, small)
• Limit exposure to high-risk tokens

Should this token be added to portfolio? Consider:
1. Diversification impact
2. Risk balance
3. Market cap distribution

Respond: Yes, No, or Reduce_Other_Positions"""

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=20,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.content[0].text.strip()

    except Exception as e:
        print(f"Error in portfolio analysis with Claude: {e}")
        return "No"

def get_market_sentiment_analysis(trending_tokens_data):
    """
    Analyze overall Base chain market sentiment using Claude
    """
    prompt = f"""Analyze the current Base chain market sentiment based on these trending tokens:

TRENDING TOKENS DATA:
{trending_tokens_data}

Provide:
1. Overall Market Sentiment (Bullish/Bearish/Neutral)
2. Key Market Trends
3. Risk Factors
4. Trading Recommendations

Keep response under 150 words."""

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=150,
            temperature=0.4,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.content[0].text.strip()

    except Exception as e:
        print(f"Error getting market sentiment from Claude: {e}")
        return "Market sentiment analysis unavailable."