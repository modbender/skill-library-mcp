import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Security imports
from .security_utils import (
    sanitize_ticker, validate_numeric, alpha_vantage_limiter,
    SecureLogger, safe_api_call, ValidationError
)

logger = SecureLogger("market_data")

@dataclass
class PricePoint:
    date: str
    open_price: float
    high: float
    low: float
    close: float
    volume: int

@dataclass
class EarningsEvent:
    date: str
    eps_estimate: Optional[float]
    eps_actual: Optional[float]
    revenue_estimate: Optional[float]
    revenue_actual: Optional[float]
    surprise_pct: Optional[float]

class MarketDataClient:
    """Client for fetching market data from Alpha Vantage."""
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize with optional API key.
        
        Args:
            api_key: Alpha Vantage API key. If None, tries ALPHA_VANTAGE_API_KEY env var.
                     If no key available, methods will return empty results with helpful message.
        """
        self.api_key = api_key or os.getenv("ALPHA_VANTAGE_API_KEY")
        self.has_api_key = bool(self.api_key)
        
        if not self.has_api_key:
            logger.info("Alpha Vantage API key not provided. US stock features limited. "
                       "Consider using yahoo_finance module for free stock data, "
                       "or get free key at: https://www.alphavantage.co/support/#api-key")
    
    @alpha_vantage_limiter
    def get_price_history(
        self, 
        ticker: str, 
        days: int = 30,
        interval: str = "daily"
    ) -> List[PricePoint]:
        """
        Get historical price data from Alpha Vantage.
        
        Note: Requires Alpha Vantage API key. For free stock data without API key,
        use yahoo_finance module instead.
        
        Args:
            ticker: Stock symbol
            days: Number of days of history
            interval: 'daily', 'weekly', 'monthly', 'intraday'
        """
        # Check if API key available
        if not self.has_api_key:
            logger.warning("Alpha Vantage API key required for stock data. "
                          "Use yahoo_finance.get_price_history() for free alternative, "
                          "or set ALPHA_VANTAGE_API_KEY environment variable.")
            return []
        
        # Input validation
        clean_ticker = sanitize_ticker(ticker)
        if not clean_ticker:
            logger.error(f"Invalid ticker symbol: {ticker}")
            return []
        
        if not validate_numeric(days, min_val=1, max_val=5000):
            logger.error(f"Invalid days parameter: {days}")
            return []
        
        if interval == "intraday":
            function = "TIME_SERIES_INTRADAY"
            extra_params = {"interval": "60min"}
        elif interval == "weekly":
            function = "TIME_SERIES_WEEKLY"
            extra_params = {}
        elif interval == "monthly":
            function = "TIME_SERIES_MONTHLY"
            extra_params = {}
        else:
            function = "TIME_SERIES_DAILY"
            extra_params = {}
        
        params = {
            "function": function,
            "symbol": clean_ticker,
            "apikey": self.api_key,
            "outputsize": "compact" if days <= 100 else "full",
            **extra_params
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # Find the time series key
            time_series_key = None
            for key in data.keys():
                if "Time Series" in key:
                    time_series_key = key
                    break
            
            if not time_series_key:
                print(f"No time series data found for {ticker}")
                return []
            
            time_series = data[time_series_key]
            
            prices = []
            for date_str, values in list(time_series.items())[:days]:
                try:
                    prices.append(PricePoint(
                        date=date_str,
                        open_price=float(values.get("1. open", 0)),
                        high=float(values.get("2. high", 0)),
                        low=float(values.get("3. low", 0)),
                        close=float(values.get("4. close", 0)),
                        volume=int(values.get("5. volume", 0))
                    ))
                except (ValueError, TypeError) as e:
                    continue
            
            return sorted(prices, key=lambda x: x.date)
            
        except Exception as e:
            print(f"Error fetching price history: {e}")
            return []
    
    def get_earnings_calendar(
        self, 
        ticker: Optional[str] = None,
        horizon: str = "3month"
    ) -> List[EarningsEvent]:
        """
        Get earnings calendar.
        
        Args:
            ticker: Specific ticker (optional, returns all if None)
            horizon: '3month', '6month', '12month'
        """
        params = {
            "function": "EARNINGS_CALENDAR",
            "apikey": self.api_key,
            "horizon": horizon
        }
        
        if ticker:
            params["symbol"] = ticker
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            earnings = []
            for entry in data.get("earningsCalendar", []):
                try:
                    earnings.append(EarningsEvent(
                        date=entry.get("reportDate", ""),
                        eps_estimate=float(entry["epsEstimate"]) if entry.get("epsEstimate") else None,
                        eps_actual=float(entry["epsActual"]) if entry.get("epsActual") else None,
                        revenue_estimate=float(entry["revenueEstimate"]) if entry.get("revenueEstimate") else None,
                        revenue_actual=float(entry["revenueActual"]) if entry.get("revenueActual") else None,
                        surprise_pct=float(entry["surprisePercentage"]) if entry.get("surprisePercentage") else None
                    ))
                except (ValueError, TypeError):
                    continue
            
            return earnings
            
        except Exception as e:
            print(f"Error fetching earnings calendar: {e}")
            return []
    
    def get_quote(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get real-time quote."""
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": ticker,
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            quote = data.get("Global Quote", {})
            if not quote:
                return None
            
            return {
                "symbol": quote.get("01. symbol"),
                "price": float(quote.get("05. price", 0)),
                "change": float(quote.get("09. change", 0)),
                "change_percent": quote.get("10. change percent", ""),
                "volume": int(quote.get("06. volume", 0)),
                "latest_trading_day": quote.get("07. latest trading day")
            }
            
        except Exception as e:
            print(f"Error fetching quote: {e}")
            return None
    
    def get_company_overview(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get company fundamentals and overview."""
        params = {
            "function": "OVERVIEW",
            "symbol": ticker,
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data or "Symbol" not in data:
                return None
            
            return {
                "symbol": data.get("Symbol"),
                "name": data.get("Name"),
                "description": data.get("Description"),
                "sector": data.get("Sector"),
                "industry": data.get("Industry"),
                "market_cap": data.get("MarketCapitalization"),
                "pe_ratio": data.get("PERatio"),
                "dividend_yield": data.get("DividendYield"),
                "52_week_high": data.get("52WeekHigh"),
                "52_week_low": data.get("52WeekLow"),
                "analyst_target_price": data.get("AnalystTargetPrice")
            }
            
        except Exception as e:
            print(f"Error fetching company overview: {e}")
            return None


def get_price_history(ticker: str, days: int = 30) -> List[Dict]:
    """Convenience function to get price history as dicts."""
    client = MarketDataClient()
    prices = client.get_price_history(ticker, days)
    return [
        {
            "date": p.date,
            "open": p.open_price,
            "high": p.high,
            "low": p.low,
            "close": p.close,
            "volume": p.volume
        }
        for p in prices
    ]


def get_quote(ticker: str) -> Optional[Dict]:
    """Get real-time quote."""
    client = MarketDataClient()
    return client.get_quote(ticker)


def get_company_overview(ticker: str) -> Optional[Dict]:
    """Get company fundamentals."""
    client = MarketDataClient()
    return client.get_company_overview(ticker)


if __name__ == "__main__":
    # Test
    print("Testing market data for AAPL...")
    quote = get_quote("AAPL")
    if quote:
        print(f"AAPL: ${quote['price']} ({quote['change_percent']})")
