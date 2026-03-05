"""
Claw Trader Lite: Market Intelligence (Read-Only)
Free version for market monitoring without execution risk
"""

import requests
import os
from typing import Dict, List, Optional

class MarketMonitor:
    """Read-only market and account monitoring"""
    
    def __init__(self):
        self.platforms = {
            'hyperliquid': HyperliquidMonitor(),
            'lnmarkets': LNMarketsMonitor()
        }
    
    def get_price(self, asset: str, platform: str = "hyperliquid") -> float:
        """Get current price for an asset"""
        return self.platforms[platform].get_price(asset)
    
    def get_prices(self, assets: List[str], platform: str = "hyperliquid") -> Dict[str, float]:
        """Get prices for multiple assets"""
        return {asset: self.get_price(asset, platform) for asset in assets}
    
    def get_balance(self, platform: str) -> float:
        """Get account balance (requires credentials)"""
        return self.platforms[platform].get_balance()
    
    def get_positions(self, platform: str) -> List[Dict]:
        """Get open positions (requires credentials)"""
        return self.platforms[platform].get_positions()


class HyperliquidMonitor:
    """Hyperliquid read-only client"""
    
    def __init__(self):
        self.base_url = "https://api.hyperliquid.xyz"
    
    def get_price(self, coin: str) -> float:
        """Get current mid price"""
        response = requests.post(
            f"{self.base_url}/info",
            json={"type": "allMids"},
            timeout=10
        )
        mids = response.json()
        return float(mids.get(coin, 0))
    
    def get_balance(self) -> float:
        """Get account balance (requires account address)"""
        account_address = os.getenv("HYPERLIQUID_ACCOUNT_ADDRESS")
        if not account_address:
            raise ValueError("Set HYPERLIQUID_ACCOUNT_ADDRESS to monitor balance")
        
        response = requests.post(
            f"{self.base_url}/info",
            json={"type": "clearinghouseState", "user": account_address},
            timeout=10
        )
        state = response.json()
        return float(state.get('marginSummary', {}).get('accountValue', 0))
    
    def get_positions(self) -> List[Dict]:
        """Get open positions"""
        account_address = os.getenv("HYPERLIQUID_ACCOUNT_ADDRESS")
        if not account_address:
            return []
        
        response = requests.post(
            f"{self.base_url}/info",
            json={"type": "clearinghouseState", "user": account_address},
            timeout=10
        )
        state = response.json()
        return state.get('assetPositions', [])


class LNMarketsMonitor:
    """LNMarkets read-only client"""
    
    def __init__(self):
        self.base_url = "https://api.lnmarkets.com"
    
    def get_price(self, asset: str = "BTC") -> float:
        """Get BTC/USD price"""
        # LNMarkets public ticker endpoint
        response = requests.get(
            f"{self.base_url}/v3/futures/ticker",
            timeout=10
        )
        ticker = response.json()
        return float(ticker.get('index', 0))
    
    def get_balance(self) -> int:
        """Get balance (requires auth - returns 0 in lite)"""
        # Lite version doesn't include authenticated endpoints
        return 0
    
    def get_positions(self) -> List[Dict]:
        """Get positions (requires auth - returns empty in lite)"""
        return []


def create_monitor() -> MarketMonitor:
    """Factory function to create market monitor"""
    return MarketMonitor()


if __name__ == "__main__":
    # Example usage
    monitor = create_monitor()
    
    print("🦞 Claw Trader Lite - Market Monitor")
    print("=" * 40)
    
    # Check prices
    print("\n📊 Live Markets:")
    for asset in ["BTC", "ETH", "SOL", "AVAX"]:
        try:
            if asset == "BTC":
                price = monitor.get_price(asset, "lnmarkets")
            else:
                price = monitor.get_price(asset, "hyperliquid")
            print(f"  {asset}: ${price:,.2f}")
        except Exception as e:
            print(f"  {asset}: Error - {e}")
    
    print("\n" + "=" * 40)
    print("✅ Read-only monitoring active")
    print("\n⚠️ For live execution, upgrade to Claw Pro")
    print("   Message @Opennnclawww_bot with 'buy'")
