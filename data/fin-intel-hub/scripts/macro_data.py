import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class MacroIndicator:
    series_id: str
    title: str
    latest_value: float
    latest_date: str
    units: str
    frequency: str

class FREDClient:
    """Client for fetching macroeconomic data from FRED (Federal Reserve Economic Data)."""
    
    BASE_URL = "https://api.stlouisfed.org/fred"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize with FRED API key.
        
        Args:
            api_key: FRED API key. If None, reads from FRED_API_KEY env var.
                     Get free key at: https://fred.stlouisfed.org/docs/api/api_key.html
        """
        self.api_key = api_key or os.getenv("FRED_API_KEY")
        if not self.api_key:
            print("Warning: FRED_API_KEY not set. Some features limited. Get key at: https://fred.stlouisfed.org/docs/api/api_key.html")
        self.session = requests.Session()
    
    def get_series(self, series_id: str, observation_start: Optional[str] = None) -> Dict:
        """
        Get data for a specific FRED series.
        
        Common series IDs:
        - DFF: Effective Federal Funds Rate
        - CPIAUCSL: Consumer Price Index (All Urban Consumers)
        - UNRATE: Unemployment Rate
        - GDP: Gross Domestic Product
        - T10Y2Y: 10-Year Treasury Constant Maturity Minus 2-Year
        """
        if not self.api_key:
            return {"error": "FRED_API_KEY required"}
        
        url = f"{self.BASE_URL}/series/observations"
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "sort_order": "desc",
            "limit": 100
        }
        
        if observation_start:
            params["observation_start"] = observation_start
        
        try:
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            observations = data.get("observations", [])
            if not observations:
                return {"series_id": series_id, "error": "No data found"}
            
            # Get latest non-null value
            latest = None
            for obs in observations:
                if obs.get("value") and obs["value"] != ".":
                    latest = obs
                    break
            
            if not latest:
                return {"series_id": series_id, "error": "No valid data"}
            
            return {
                "series_id": series_id,
                "latest_value": float(latest["value"]),
                "latest_date": latest["date"],
                "observations": [
                    {"date": o["date"], "value": float(o["value"]) if o["value"] and o["value"] != "." else None}
                    for o in observations[:30]  # Last 30 data points
                ]
            }
            
        except Exception as e:
            print(f"FRED API error: {e}")
            return {"series_id": series_id, "error": str(e)}
    
    def get_macro_dashboard(self) -> Dict[str, Any]:
        """
        Get key macroeconomic indicators dashboard.
        
        Returns:
            Dictionary with key economic indicators
        """
        indicators = {
            "fed_funds_rate": "DFF",           # Fed rate
            "cpi": "CPIAUCSL",                 # Inflation
            "unemployment": "UNRATE",          # Jobs
            "gdp_growth": "A191RL1Q225SBEA",   # Real GDP growth
            "yield_spread": "T10Y2Y",          # Recession indicator
            "consumer_sentiment": "UMCSENT",   # Consumer confidence
        }
        
        dashboard = {
            "generated_at": datetime.now().isoformat(),
            "indicators": {}
        }
        
        for name, series_id in indicators.items():
            data = self.get_series(series_id)
            if "error" not in data:
                dashboard["indicators"][name] = {
                    "value": data["latest_value"],
                    "date": data["latest_date"],
                    "recent_history": data["observations"][:5]
                }
            else:
                dashboard["indicators"][name] = {"error": data["error"]}
        
        return dashboard
    
    def get_series_info(self, series_id: str) -> Dict:
        """Get metadata about a series."""
        if not self.api_key:
            return {"error": "FRED_API_KEY required"}
        
        url = f"{self.BASE_URL}/series"
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json"
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            series = data.get("seriess", [{}])[0]
            return {
                "id": series.get("id"),
                "title": series.get("title"),
                "units": series.get("units"),
                "frequency": series.get("frequency"),
                "seasonal_adjustment": series.get("seasonal_adjustment"),
                "last_updated": series.get("last_updated"),
                "notes": series.get("notes", "")[:500]  # Truncate long notes
            }
            
        except Exception as e:
            return {"error": str(e)}


def get_fed_rate() -> Dict:
    """Get current Federal Funds Rate."""
    client = FREDClient()
    return client.get_series("DFF")


def get_cpi() -> Dict:
    """Get latest Consumer Price Index."""
    client = FREDClient()
    return client.get_series("CPIAUCSL")


def get_unemployment() -> Dict:
    """Get unemployment rate."""
    client = FREDClient()
    return client.get_series("UNRATE")


def get_macro_dashboard() -> Dict:
    """Get full macro dashboard."""
    client = FREDClient()
    return client.get_macro_dashboard()


if __name__ == "__main__":
    # Test
    print("Testing macro data...")
    
    dashboard = get_macro_dashboard()
    print(f"\nMacro Dashboard Generated: {dashboard['generated_at']}")
    
    for indicator, data in dashboard["indicators"].items():
        if "value" in data:
            print(f"{indicator}: {data['value']} (as of {data['date']})")
        else:
            print(f"{indicator}: Error - {data.get('error')}")
