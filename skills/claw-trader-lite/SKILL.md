To create the file yourself:



\# Create the directory

mkdir -p ~/.openclaw/workspace/skills/claw-trader-lite



\# Create the file

cat > ~/.openclaw/workspace/skills/claw-trader-lite/SKILL.md << 'EOF'

---

name: claw-trader-lite

description: |

&nbsp; Free read-only market monitoring for Hyperliquid and LN Markets. 

&nbsp; Track real-time prices, view public balances, and monitor positions 

&nbsp; across DeFi and Bitcoin derivatives platforms. Zero private keys required.

env:

&nbsp; HYPERLIQUID\_ACCOUNT\_ADDRESS:

&nbsp;   description: "Optional: Your Hyperliquid wallet address to view balance/positions (e.g., 0x...)"

&nbsp;   required: false

---



\# Claw Trader Lite



\*\*Free read-only market intelligence for Hyperliquid and LN Markets.\*\*



Monitor real-time prices, track your portfolio, and view positions across DeFi and Bitcoin derivatives platforms. Perfect for keeping tabs on your trades without execution risk.



---



\## What It Does



Claw Trader Lite provides \*\*read-only\*\* access to market data and account information. It can view prices, balances, and positions but \*\*cannot execute trades\*\*—making it safe to use anywhere.



\### Platforms Supported



\- \*\*Hyperliquid\*\* - DeFi perpetuals (ETH, SOL, AVAX, and 100+ altcoins)

\- \*\*LN Markets\*\* - Bitcoin derivatives via Lightning Network



---



\## Key Features



✅ \*\*Real-Time Price Feeds\*\* - Live market data for BTC, ETH, SOL, and major assets  

✅ \*\*Portfolio Overview\*\* - View balances and open positions at a glance  

✅ \*\*Zero Risk\*\* - Read-only access, no private keys or API secrets needed  

✅ \*\*Lightweight\*\* - Minimal dependencies, runs anywhere  

✅ \*\*Free Forever\*\* - No costs, no limits, no catch  



---



\## Installation



```bash

pip install requests





Quick Start



from claw\_lite import create\_monitor



\# Create monitor

monitor = create\_monitor()



\# Check current prices

btc\_price = monitor.get\_price("BTC", "lnmarkets")

eth\_price = monitor.get\_price("ETH", "hyperliquid")

sol\_price = monitor.get\_price("SOL", "hyperliquid")



print(f"BTC: ${btc\_price:,.2f}")

print(f"ETH: ${eth\_price:,.2f}")

print(f"SOL: ${sol\_price:,.2f}")





Usage Examples



Get Single Asset Price



\# Bitcoin price from LN Markets

btc\_price = monitor.get\_price("BTC", "lnmarkets")



\# Ethereum price from Hyperliquid

eth\_price = monitor.get\_price("ETH", "hyperliquid")



Get Multiple Prices



assets = \["BTC", "ETH", "SOL", "AVAX"]

prices = monitor.get\_prices(assets, "hyperliquid")



for asset, price in prices.items():

&nbsp;   print(f"{asset}: ${price:,.2f}")



View Account Balance (Hyperliquid)



Note: Requires setting your public wallet address



export HYPERLIQUID\_ACCOUNT\_ADDRESS="0xYourAddressHere"



balance = monitor.get\_balance("hyperliquid")

print(f"Account Value: ${balance:,.2f}")



View Open Positions (Hyperliquid)



positions = monitor.get\_positions("hyperliquid")



for pos in positions:

&nbsp;   print(f"{pos\['coin']}: {pos\['size']} @ ${pos\['entryPx']}")





Platform-Specific Notes



Hyperliquid



• Supports 100+ altcoins

• Balance/positions require HYPERLIQUID\_ACCOUNT\_ADDRESS env var

• Uses public API endpoints (no authentication needed for prices)

LN Markets



• Bitcoin-focused

• Price data is public

• Balances/positions require authenticated API (not included in Lite version)



API Reference



create\_monitor()



Factory function to create a new MarketMonitor instance.



Returns: MarketMonitor object



MarketMonitor.get\_price(asset, platform)



Get current price for an asset.



Parameters:



• asset (str): Asset symbol (e.g., "BTC", "ETH", "SOL")

• platform (str): Platform name ("hyperliquid" or "lnmarkets")

Returns: float - Current price in USD



MarketMonitor.get\_prices(assets, platform)



Get prices for multiple assets at once.



Parameters:



• assets (List\[str]): List of asset symbols

• platform (str): Platform name

Returns: Dict\[str, float] - Mapping of asset symbols to prices



MarketMonitor.get\_balance(platform)



Get account balance.



Parameters:



• platform (str): Platform name

Returns: float - Account balance in USD



Claw 🦞, \[2/18/2026 2:55 PM]

Note: Requires HYPERLIQUID\_ACCOUNT\_ADDRESS for Hyperliquid



MarketMonitor.get\_positions(platform)



Get open positions.



Parameters:



• platform (str): Platform name

Returns: List\[Dict] - List of position dictionaries



Note: Requires HYPERLIQUID\_ACCOUNT\_ADDRESS for Hyperliquid





Environment Variables



| Variable                    | Required | Description                                                |

| --------------------------- | -------- | ---------------------------------------------------------- |

| HYPERLIQUID\_ACCOUNT\_ADDRESS | Optional | Your Hyperliquid wallet address to view balances/positions |





Limitations



This is a Lite read-only version:



• ✅ View prices, balances, positions

• ❌ Cannot execute trades

• ❌ Cannot place orders

• ❌ Cannot manage positions

For trading execution, build your own integration or use platform-specific SDKs.





Troubleshooting



"Error fetching price"



• Check internet connection

• Verify asset symbol is correct (case-sensitive on some platforms)

• Try again (may be temporary API issue)

"HYPERLIQUID\_ACCOUNT\_ADDRESS not set"



• Export your wallet address: export HYPERLIQUID\_ACCOUNT\_ADDRESS="0x..."

• Or pass directly in code (not recommended for shared environments)

Balance shows 0 for LN Markets



• LN Markets requires authentication for balance data

• Lite version only provides public price feeds for LN Markets



Technical Details



Dependencies:



• requests - HTTP library for API calls

Data Sources:



• Hyperliquid Public API (https://api.hyperliquid.xyz)

• LN Markets Public API (https://api.lnmarkets.com)

License: MIT





About



Built for traders who want simple, free market monitoring without complexity or risk.



🦞 Free forever. No signup. No API keys.

