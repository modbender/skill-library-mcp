
import requests
import json
import os
import sys

# --- Configuration ---
# API Endpoints (using CoinGecko for crypto, placeholder for stocks)
COINGECKO_API_BASE = "https://api.coingecko.com/api/v3"
# For stocks, a free, reliable API is harder to come by without registration/limits.
# Alpha Vantage is an option, but requires an API key and has rate limits.
# For this example, we'll use a placeholder and emphasize secure API key handling.
STOCK_API_BASE = "https://www.alphavantage.co/query"

# --- Helper Functions ---
def get_env_variable(var_name, optional=False):
    """Get an environment variable, or raise an error if not found and not optional."""
    value = os.getenv(var_name)
    if value is None and not optional:
        print(f"Error: Environment variable {var_name} not set.", file=sys.stderr)
        sys.exit(1)
    return value

def fetch_crypto_price(coin_id, currency='usd'):
    """Fetches the current price of a cryptocurrency from CoinGecko."""
    try:
        url = f"{COINGECKO_API_BASE}/simple/price?ids={coin_id}&vs_currencies={currency}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        return data.get(coin_id, {}).get(currency)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {coin_id} price from CoinGecko: {e}", file=sys.stderr)
        return None

def fetch_stock_price(symbol):
    """Fetches the current price of a stock from a placeholder API.
    In a real-world scenario, this would use a service like Alpha Vantage or similar.
    Requires an API key for most reliable services.
    """
    # Placeholder for Alpha Vantage or similar. Requires API_KEY.
    # Example: https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=IBM&apikey=YOUR_API_KEY
    # For demonstration, returning a dummy value.
    print(f"Warning: Using dummy stock price for {symbol}. Integrate a real stock API for production.", file=sys.stderr)
    return 150.00 # Dummy price

def get_eth_balance(address):
    """Fetches Ethereum balance for a given address using Etherscan API.
    Requires ETHERSCAN_API_KEY environment variable.
    """
    etherscan_api_key = get_env_variable("ETHERSCAN_API_KEY", optional=True)
    if not etherscan_api_key:
        print("Warning: ETHERSCAN_API_KEY not set. Using dummy ETH balance.", file=sys.stderr)
        return 1.5 # Dummy balance

    try:
        url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={etherscan_api_key}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data["status"] == "1":
            # Balance is returned in Wei, convert to Ether
            return int(data["result"]) / 10**18
        else:
            print(f"Etherscan API error for {address}: {data.get('message', 'Unknown error')}", file=sys.stderr)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching ETH balance for {address}: {e}", file=sys.stderr)
        return None

# --- Main Logic ---
def main():
    portfolio_file = "portfolio.json"
    portfolio_data = {"crypto": [], "stocks": []}

    if not os.path.exists(portfolio_file):
        print(f"Error: {portfolio_file} not found. Please create it with your assets.", file=sys.stderr)
        print("Example content for portfolio.json:")
        print(json.dumps({
            "crypto": [
                {"type": "ETH", "address": "0xYourEthereumAddressHere", "coin_id": "ethereum"},
                {"type": "BTC", "coin_id": "bitcoin", "amount": 0.05}
            ],
            "stocks": [
                {"symbol": "AAPL", "shares": 10},
                {"symbol": "GOOGL", "shares": 5}
            ]
        }, indent=2))
        sys.exit(1)

    try:
        with open(portfolio_file, "r") as f:
            portfolio_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error parsing {portfolio_file}: {e}", file=sys.stderr)
        sys.exit(1)

    total_portfolio_value = 0.0
    output_lines = []

    output_lines.append("\n--- Cryptocurrency Holdings ---")
    for item in portfolio_data.get("crypto", []):
        asset_type = item.get("type")
        coin_id = item.get("coin_id")

        if asset_type == "ETH" and "address" in item:
            address = item["address"]
            balance = get_eth_balance(address)
            if balance is not None:
                price_usd = fetch_crypto_price(coin_id)
                if price_usd:
                    value_usd = balance * price_usd
                    total_portfolio_value += value_usd
                    output_lines.append(f"  {asset_type} ({address[:6]}...{address[-4:]}): {balance:.4f} ETH (Value: ${value_usd:.2f})")
                else:
                    output_lines.append(f"  {asset_type} ({address[:6]}...{address[-4:]}): {balance:.4f} ETH (Price unavailable)")
            else:
                output_lines.append(f"  {asset_type} ({address[:6]}...{address[-4:]}): Balance unavailable")
        elif "amount" in item and coin_id:
            amount = item["amount"]
            price_usd = fetch_crypto_price(coin_id)
            if price_usd:
                value_usd = amount * price_usd
                total_portfolio_value += value_usd
                output_lines.append(f"  {coin_id.capitalize()}: {amount:.4f} (Value: ${value_usd:.2f})")
            else:
                output_lines.append(f"  {coin_id.capitalize()}: {amount:.4f} (Price unavailable)")
        else:
            output_lines.append(f"  Invalid crypto entry: {item}")

    output_lines.append("\n--- Stock Holdings ---")
    for item in portfolio_data.get("stocks", []):
        symbol = item.get("symbol")
        shares = item.get("shares", 0)
        if symbol and shares > 0:
            price = fetch_stock_price(symbol)
            if price:
                value_usd = shares * price
                total_portfolio_value += value_usd
                output_lines.append(f"  {symbol}: {shares} shares @ ${price:.2f}/share (Value: ${value_usd:.2f})")
            else:
                output_lines.append(f"  {symbol}: {shares} shares (Price unavailable)")
        else:
            output_lines.append(f"  Invalid stock entry: {item}")

    output_lines.append(f"\n--- Total Portfolio Value: ${total_portfolio_value:.2f} ---")

    print("\n".join(output_lines))

if __name__ == "__main__":
    main()
