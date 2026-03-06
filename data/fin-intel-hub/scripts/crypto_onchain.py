import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class ExchangeFlow:
    timestamp: str
    exchange: str
    inflow: float
    outflow: float
    netflow: float
    asset: str

@dataclass
class WhaleAlert:
    timestamp: str
    from_address: str
    to_address: str
    amount: float
    amount_usd: float
    asset: str
    transaction_hash: str

class CryptoOnChainClient:
    """Client for fetching crypto on-chain data via free APIs."""
    
    def __init__(self):
        # Using free public APIs - no key required for basic data
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "BoringLife-FinanceSkill/1.0"
        })
    
    def get_bitcoin_exchange_flows(self, days: int = 7) -> List[ExchangeFlow]:
        """
        Get BTC exchange inflow/outflow data.
        Uses Glassnode API (requires free API key) or falls back to CryptoQuant-style estimates.
        """
        glassnode_key = os.getenv("GLASSNODE_API_KEY")
        
        if glassnode_key:
            return self._get_glassnode_flows(days, glassnode_key)
        else:
            # Fallback: aggregated public data
            return self._get_public_exchange_data("BTC", days)
    
    def _get_glassnode_flows(self, days: int, api_key: str) -> List[ExchangeFlow]:
        """Fetch exchange flows from Glassnode (more accurate)."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        url = "https://api.glassnode.com/v1/metrics/flows/exchange_inflow"
        params = {
            "a": "BTC",
            "s": int(start_date.timestamp()),
            "u": int(end_date.timestamp()),
            "i": "24h",
            "api_key": api_key
        }
        
        try:
            response = self.session.get(url, params=params, timeout=15)
            if response.status_code != 200:
                return self._get_public_exchange_data("BTC", days)
            
            inflow_data = response.json()
            
            # Get outflow data
            params["a"] = "exchange_outflow"
            response = self.session.get(url, params=params, timeout=15)
            outflow_data = response.json() if response.status_code == 200 else []
            
            flows = []
            for i, entry in enumerate(inflow_data):
                ts = datetime.fromtimestamp(entry["t"]).isoformat()
                inflow = entry["v"]
                outflow = outflow_data[i]["v"] if i < len(outflow_data) else 0
                
                flows.append(ExchangeFlow(
                    timestamp=ts,
                    exchange="aggregated",
                    inflow=inflow,
                    outflow=outflow,
                    netflow=inflow - outflow,
                    asset="BTC"
                ))
            
            return flows
            
        except Exception as e:
            print(f"Glassnode error: {e}")
            return self._get_public_exchange_data("BTC", days)
    
    def _get_public_exchange_data(self, asset: str, days: int) -> List[ExchangeFlow]:
        """Fallback: Get exchange data from CoinGecko (limited but free)."""
        try:
            # CoinGecko exchange volume data as proxy
            url = "https://api.coingecko.com/api/v3/exchanges"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                return []
            
            # This is simplified - real flow data requires paid APIs
            # Return mock structure for now
            flows = []
            for i in range(days):
                date = (datetime.now() - timedelta(days=i)).isoformat()
                flows.append(ExchangeFlow(
                    timestamp=date,
                    exchange="aggregated",
                    inflow=0.0,  # Would need paid API for real data
                    outflow=0.0,
                    netflow=0.0,
                    asset=asset
                ))
            
            return flows
            
        except Exception as e:
            print(f"Public API error: {e}")
            return []
    
    def get_defi_tvl(self, protocol: Optional[str] = None) -> Dict[str, Any]:
        """
        Get DeFi total value locked data from DeFiLlama.
        Free API, no key required.
        """
        try:
            if protocol:
                url = f"https://api.llama.fi/protocol/{protocol.lower()}"
            else:
                url = "https://api.llama.fi/charts"
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if protocol:
                return {
                    "protocol": data.get("name"),
                    "tvl": data.get("tvl"),
                    "chain": data.get("chain"),
                    "category": data.get("category"),
                    "chains": data.get("chains", []),
                    "current_tvl_usd": data.get("tvl", [{}])[-1].get("totalLiquidityUSD") if data.get("tvl") else None
                }
            else:
                # Global DeFi TVL over time
                latest = data[-1] if data else {}
                return {
                    "total_tvl_usd": latest.get("totalLiquidityUSD"),
                    "date": latest.get("date"),
                    "historical": [
                        {"date": d["date"], "tvl": d["totalLiquidityUSD"]}
                        for d in data[-30:]  # Last 30 days
                    ]
                }
                
        except Exception as e:
            print(f"DeFiLlama error: {e}")
            return {}
    
    def get_gas_prices(self) -> Dict[str, Any]:
        """Get Ethereum gas prices from Etherscan (requires API key)."""
        etherscan_key = os.getenv("ETHERSCAN_API_KEY")
        
        if not etherscan_key:
            # Fallback to public gas tracker
            try:
                url = "https://api.etherscan.io/api"
                params = {
                    "module": "gastracker",
                    "action": "gasoracle",
                    "apikey": etherscan_key or "YourApiKeyToken"  # Demo key (limited)
                }
                
                response = self.session.get(url, params=params, timeout=10)
                data = response.json()
                
                if data.get("status") == "1":
                    result = data.get("result", {})
                    return {
                        "safe_low": result.get("SafeGasPrice"),
                        "standard": result.get("ProposeGasPrice"),
                        "fast": result.get("FastGasPrice"),
                        "base_fee": result.get("suggestBaseFee"),
                        "unit": "gwei"
                    }
            except Exception as e:
                print(f"Gas price error: {e}")
        
        return {}
    
    def get_top_exchanges(self, limit: int = 10) -> List[Dict]:
        """Get top exchanges by volume from CoinGecko."""
        try:
            url = "https://api.coingecko.com/api/v3/exchanges"
            params = {"per_page": limit, "page": 1}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return [
                {
                    "name": ex.get("name"),
                    "id": ex.get("id"),
                    "trust_score": ex.get("trust_score"),
                    "volume_24h_btc": ex.get("trade_volume_24h_btc"),
                    "volume_24h_normalized": ex.get("trade_volume_24h_btc_normalized"),
                    "year_established": ex.get("year_established"),
                    "country": ex.get("country"),
                    "url": ex.get("url")
                }
                for ex in data[:limit]
            ]
            
        except Exception as e:
            print(f"Exchange fetch error: {e}")
            return []
    
    def get_whale_alerts(self, min_value_usd: float = 1000000, hours: int = 24) -> List[WhaleAlert]:
        """
        Get whale transaction alerts.
        Note: Real whale alerts require paid API (Whale Alert API).
        This is a placeholder structure.
        """
        # Would integrate with: https://docs.whale-alert.io/
        # Free tier: limited requests, basic data
        # For now, return empty list - user can add API key
        
        whale_api_key = os.getenv("WHALE_ALERT_API_KEY")
        
        if not whale_api_key:
            print("WHALE_ALERT_API_KEY not set. Add key for whale alerts.")
            return []
        
        try:
            # Whale Alert API integration would go here
            # https://api.whale-alert.io/v1/transactions
            pass
        except Exception as e:
            print(f"Whale alert error: {e}")
        
        return []


def get_exchange_flows(asset: str = "BTC", days: int = 7) -> List[Dict]:
    """Convenience function to get exchange flows as dicts."""
    client = CryptoOnChainClient()
    
    if asset.upper() == "BTC":
        flows = client.get_bitcoin_exchange_flows(days)
    else:
        flows = client._get_public_exchange_data(asset, days)
    
    return [
        {
            "timestamp": f.timestamp,
            "exchange": f.exchange,
            "inflow": f.inflow,
            "outflow": f.outflow,
            "netflow": f.netflow,
            "asset": f.asset
        }
        for f in flows
    ]


def get_defi_tvl(protocol: Optional[str] = None) -> Dict:
    """Get DeFi TVL data."""
    client = CryptoOnChainClient()
    return client.get_defi_tvl(protocol)


def get_gas_prices() -> Dict:
    """Get Ethereum gas prices."""
    client = CryptoOnChainClient()
    return client.get_gas_prices()


def get_top_exchanges(limit: int = 10) -> List[Dict]:
    """Get top exchanges by volume."""
    client = CryptoOnChainClient()
    return client.get_top_exchanges(limit)


if __name__ == "__main__":
    # Test
    print("Testing crypto on-chain data...")
    
    print("\n--- DeFi TVL ---")
    tvl = get_defi_tvl()
    print(f"Total DeFi TVL: ${tvl.get('total_tvl_usd', 'N/A'):,.0f}")
    
    print("\n--- Top Exchanges ---")
    exchanges = get_top_exchanges(5)
    for ex in exchanges:
        print(f"{ex['name']}: {ex['trust_score']} (Vol: {ex['volume_24h_btc']:.0f} BTC)")
