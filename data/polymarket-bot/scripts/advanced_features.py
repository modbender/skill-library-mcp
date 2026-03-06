# advanced_features.py
from strategy_logic import PolymarketArbitrageBot  # Import for extension
import requests
import asyncio

class PolymarketCopyTradingBot(PolymarketArbitrageBot):
    async def monitor_leaderboard_and_copy(self, category='crypto'):
        url = "https://data-api.polymarket.com/leaderboards"
        params = {"category": category}  # Filter by category like crypto
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            leaderboard = response.json()
            top_traders = leaderboard['traders'][:3]  # Top 3 traders
            
            while True:
                for trader in top_traders:
                    trades_url = f"https://data-api.polymarket.com/traders/{trader['id']}/trades"
                    trades_response = requests.get(trades_url)
                    trades = trades_response.json()
                    for trade in trades:
                        # Mirror trade with 10% of your balance
                        if not self.dry_run:
                            amount = trade['amount'] * 0.10  # Proportional amount
                            self.place_order(trade['market_id'], trade['side'], amount)
                        print(f"Copied trade: {trade}")
                await asyncio.sleep(30)  # Monitor every 30 seconds
        except Exception as e:
            print(f"Error in copy trading: {e}")

# Example usage
if __name__ == "__main__":
    api_creds = {}  # Load from auth_setup.py or env
    copy_bot = PolymarketCopyTradingBot(api_creds, dry_run=True)
    asyncio.run(copy_bot.monitor_leaderboard_and_copy(category='crypto'))
