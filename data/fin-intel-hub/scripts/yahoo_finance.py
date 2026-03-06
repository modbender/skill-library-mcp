import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class StockPrice:
    date: str
    open_price: float
    high: float
    low: float
    close: float
    volume: int
    adjusted_close: float

@dataclass
class StockInfo:
    symbol: str
    name: str
    currency: str
    market: str
    sector: Optional[str]
    industry: Optional[str]
    market_cap: Optional[float]
    pe_ratio: Optional[float]
    dividend_yield: Optional[float]
    fifty_two_week_high: Optional[float]
    fifty_two_week_low: Optional[float]

class YahooFinanceClient:
    """Client for fetching global stock data from Yahoo Finance."""
    
    BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart"
    
    # Market suffix mappings
    MARKET_SUFFIXES = {
        "hong_kong": ".HK",
        "tokyo": ".T",
        "taiwan": ".TW",
        "korea": ".KS",
        "shanghai": ".SS",  # Or .SH
        "shenzhen": ".SZ",
        "singapore": ".SI",
        "australia": ".AX",
        "london": ".L",
        "germany": ".DE",
        "paris": ".PA",
        "toronto": ".TO",
        "bombay": ".BO",
        "nse": ".NS",
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def get_price_history(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d"
    ) -> List[StockPrice]:
        """
        Get historical price data for any global stock.
        
        Args:
            symbol: Yahoo Finance symbol (e.g., '0700.HK', '7203.T', 'AAPL')
            period: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'
            interval: '1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'
        
        Returns:
            List of StockPrice objects
        """
        url = f"{self.BASE_URL}/{symbol}"
        params = {
            "period1": int((datetime.now() - self._parse_period(period)).timestamp()),
            "period2": int(datetime.now().timestamp()),
            "interval": interval,
            "events": "history",
            "includeAdjustedClose": "true"
        }
        
        try:
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if "chart" not in data or "result" not in data["chart"] or not data["chart"]["result"]:
                print(f"No data found for {symbol}")
                return []
            
            result = data["chart"]["result"][0]
            timestamps = result.get("timestamp", [])
            quote = result.get("indicators", {}).get("quote", [{}])[0]
            adjclose = result.get("indicators", {}).get("adjclose", [{}])[0].get("adjclose", [])
            
            prices = []
            for i, ts in enumerate(timestamps):
                try:
                    prices.append(StockPrice(
                        date=datetime.fromtimestamp(ts).strftime("%Y-%m-%d"),
                        open_price=quote.get("open", [])[i] or 0,
                        high=quote.get("high", [])[i] or 0,
                        low=quote.get("low", [])[i] or 0,
                        close=quote.get("close", [])[i] or 0,
                        volume=int(quote.get("volume", [])[i] or 0),
                        adjusted_close=adjclose[i] if i < len(adjclose) else (quote.get("close", [])[i] or 0)
                    ))
                except (IndexError, TypeError):
                    continue
            
            return prices
            
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return []
    
    def _parse_period(self, period: str) -> datetime:
        """Convert period string to datetime."""
        now = datetime.now()
        
        if period == "1d":
            return now - timedelta(days=1)
        elif period == "5d":
            return now - timedelta(days=5)
        elif period == "1mo":
            return now - timedelta(days=30)
        elif period == "3mo":
            return now - timedelta(days=90)
        elif period == "6mo":
            return now - timedelta(days=180)
        elif period == "1y":
            return now - timedelta(days=365)
        elif period == "2y":
            return now - timedelta(days=730)
        elif period == "5y":
            return now - timedelta(days=1825)
        elif period == "ytd":
            return datetime(now.year, 1, 1)
        elif period == "max":
            return now - timedelta(days=365*20)
        else:
            return now - timedelta(days=365)
    
    def get_stock_info(self, symbol: str) -> Optional[StockInfo]:
        """Get company/stock metadata."""
        url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{symbol}"
        params = {
            "modules": "assetProfile,summaryDetail,price"
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            result = data.get("quoteSummary", {}).get("result", [{}])[0]
            
            profile = result.get("assetProfile", {})
            summary = result.get("summaryDetail", {})
            price = result.get("price", {})
            
            return StockInfo(
                symbol=symbol,
                name=price.get("longName") or price.get("shortName", symbol),
                currency=price.get("currency", "USD"),
                market=price.get("exchangeName", "Unknown"),
                sector=profile.get("sector"),
                industry=profile.get("industry"),
                market_cap=summary.get("marketCap", {}).get("raw") if isinstance(summary.get("marketCap"), dict) else summary.get("marketCap"),
                pe_ratio=summary.get("trailingPE", {}).get("raw") if isinstance(summary.get("trailingPE"), dict) else summary.get("trailingPE"),
                dividend_yield=summary.get("dividendYield", {}).get("raw") if isinstance(summary.get("dividendYield"), dict) else summary.get("dividendYield"),
                fifty_two_week_high=summary.get("fiftyTwoWeekHigh", {}).get("raw") if isinstance(summary.get("fiftyTwoWeekHigh"), dict) else summary.get("fiftyTwoWeekHigh"),
                fifty_two_week_low=summary.get("fiftyTwoWeekLow", {}).get("raw") if isinstance(summary.get("fiftyTwoWeekLow"), dict) else summary.get("fiftyTwoWeekLow")
            )
            
        except Exception as e:
            print(f"Error fetching info for {symbol}: {e}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[Dict]:
        """Get real-time quote."""
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        params = {"interval": "1d", "range": "1d"}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if "chart" not in data or "result" not in data["chart"] or not data["chart"]["result"]:
                return None
            
            meta = data["chart"]["result"][0].get("meta", {})
            
            return {
                "symbol": symbol,
                "price": meta.get("regularMarketPrice"),
                "previous_close": meta.get("previousClose"),
                "currency": meta.get("currency"),
                "exchange": meta.get("exchangeName"),
                "market_state": meta.get("marketState")
            }
            
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return None


def get_price_history(symbol: str, period: str = "1y") -> List[Dict]:
    """Convenience function to get price history as dicts."""
    client = YahooFinanceClient()
    prices = client.get_price_history(symbol, period)
    return [
        {
            "date": p.date,
            "open": p.open_price,
            "high": p.high,
            "low": p.low,
            "close": p.close,
            "volume": p.volume,
            "adjusted_close": p.adjusted_close
        }
        for p in prices
    ]


def get_stock_info(symbol: str) -> Optional[Dict]:
    """Get stock information."""
    client = YahooFinanceClient()
    info = client.get_stock_info(symbol)
    if info:
        return {
            "symbol": info.symbol,
            "name": info.name,
            "currency": info.currency,
            "market": info.market,
            "sector": info.sector,
            "industry": info.industry,
            "market_cap": info.market_cap,
            "pe_ratio": info.pe_ratio,
            "dividend_yield": info.dividend_yield,
            "52_week_high": info.fifty_two_week_high,
            "52_week_low": info.fifty_two_week_low
        }
    return None


def get_current_price(symbol: str) -> Optional[Dict]:
    """Get current price quote."""
    client = YahooFinanceClient()
    return client.get_current_price(symbol)


# Helper functions for Asian markets
def get_hong_kong_stock(code: str, **kwargs) -> List[Dict]:
    """
    Get Hong Kong stock data.
    
    Args:
        code: Stock code (e.g., '0700' for Tencent, '3690' for Meituan)
    """
    symbol = f"{code}.HK"
    return get_price_history(symbol, **kwargs)


def get_tokyo_stock(code: str, **kwargs) -> List[Dict]:
    """
    Get Tokyo Stock Exchange data.
    
    Args:
        code: Stock code (e.g., '7203' for Toyota, '6758' for Sony)
    """
    symbol = f"{code}.T"
    return get_price_history(symbol, **kwargs)


def get_taiwan_stock(code: str, **kwargs) -> List[Dict]:
    """
    Get Taiwan Stock Exchange data.
    
    Args:
        code: Stock code (e.g., '2330' for TSMC, '2317' for Foxconn)
    """
    symbol = f"{code}.TW"
    return get_price_history(symbol, **kwargs)


def get_korea_stock(code: str, **kwargs) -> List[Dict]:
    """
    Get Korea Exchange data.
    
    Args:
        code: Stock code (e.g., '005930' for Samsung, '035420' for Naver)
    """
    symbol = f"{code}.KS"
    return get_price_history(symbol, **kwargs)


def get_shanghai_stock(code: str, **kwargs) -> List[Dict]:
    """
    Get Shanghai Stock Exchange data.
    
    Args:
        code: Stock code (e.g., '600519' for Kweichow Moutai)
    """
    symbol = f"{code}.SS"
    return get_price_history(symbol, **kwargs)


def get_shenzhen_stock(code: str, **kwargs) -> List[Dict]:
    """
    Get Shenzhen Stock Exchange data.
    
    Args:
        code: Stock code (e.g., '000001' for Ping An Bank)
    """
    symbol = f"{code}.SZ"
    return get_price_history(symbol, **kwargs)


# ============================================================================
# INDICES - Major Global Stock Market Indices
# ============================================================================

MAJOR_INDICES = {
    # US Indices
    "sp500": "^GSPC",           # S&P 500
    "dow_jones": "^DJI",        # Dow Jones Industrial Average
    "nasdaq": "^IXIC",          # Nasdaq Composite
    "russell2000": "^RUT",      # Russell 2000
    "vix": "^VIX",              # Volatility Index (Fear index)
    
    # Asian Indices
    "nikkei225": "^N225",       # Japan Nikkei 225
    "hang_seng": "^HSI",        # Hong Kong Hang Seng
    "shanghai_composite": "000001.SS",  # Shanghai Composite
    "csi300": "000300.SS",      # China CSI 300
    "taiwan_weighted": "^TWII", # Taiwan Weighted Index
    "kospi": "^KS11",           # Korea KOSPI
    "sensex": "^BSESN",         # India BSE Sensex
    "nifty50": "^NSEI",         # India NIFTY 50
    "straits_times": "^STI",    # Singapore Straits Times
    
    # European Indices
    "ftse100": "^FTSE",         # UK FTSE 100
    "dax": "^GDAXI",            # Germany DAX
    "cac40": "^FCHI",           # France CAC 40
    "euro_stoxx50": "^STOXX50E", # Euro Stoxx 50
    
    # Other
    "asx200": "^AXJO",          # Australia ASX 200
    "tsx": "^GSPTSE",           # Canada TSX Composite
}

def get_index(symbol_key: str, **kwargs) -> List[Dict]:
    """
    Get major stock market index data.
    
    Args:
        symbol_key: Key from MAJOR_INDICES (e.g., 'sp500', 'nikkei225', 'hang_seng')
    """
    if symbol_key not in MAJOR_INDICES:
        raise ValueError(f"Unknown index: {symbol_key}. Available: {list(MAJOR_INDICES.keys())}")
    
    return get_price_history(MAJOR_INDICES[symbol_key], **kwargs)


def get_sp500(**kwargs) -> List[Dict]:
    """Get S&P 500 index data."""
    return get_index("sp500", **kwargs)


def get_nasdaq(**kwargs) -> List[Dict]:
    """Get Nasdaq Composite index data."""
    return get_index("nasdaq", **kwargs)


def get_dow_jones(**kwargs) -> List[Dict]:
    """Get Dow Jones Industrial Average data."""
    return get_index("dow_jones", **kwargs)


def get_nikkei225(**kwargs) -> List[Dict]:
    """Get Nikkei 225 index data."""
    return get_index("nikkei225", **kwargs)


def get_hang_seng(**kwargs) -> List[Dict]:
    """Get Hang Seng index data."""
    return get_index("hang_seng", **kwargs)


def get_vix(**kwargs) -> List[Dict]:
    """Get VIX (Volatility/Fear) index data."""
    return get_index("vix", **kwargs)


# ============================================================================
# FUTURES - Stock Index Futures & Commodity Futures
# ============================================================================

FUTURES = {
    # Stock Index Futures
    "es": "ES=F",       # E-mini S&P 500 Futures
    "nq": "NQ=F",       # E-mini Nasdaq 100 Futures
    "ym": "YM=F",       # E-mini Dow Futures
    "rty": "RTY=F",     # E-mini Russell 2000 Futures
    "nikkei_futures": "NKD=F",  # Nikkei 225 Futures
    
    # Commodity Futures
    "crude_oil": "CL=F",        # WTI Crude Oil
    "brent_oil": "BZ=F",        # Brent Crude Oil
    "natural_gas": "NG=F",      # Natural Gas
    "gold": "GC=F",             # Gold
    "silver": "SI=F",           # Silver
    "copper": "HG=F",           # Copper
    "platinum": "PL=F",         # Platinum
    "palladium": "PA=F",        # Palladium
    
    # Agriculture Futures
    "corn": "ZC=F",             # Corn
    "wheat": "ZW=F",            # Wheat
    "soybeans": "ZS=F",         # Soybeans
    "coffee": "KC=F",           # Coffee
    "sugar": "SB=F",            # Sugar
    "cotton": "CT=F",           # Cotton
}

def get_future(symbol_key: str, **kwargs) -> List[Dict]:
    """
    Get futures data.
    
    Args:
        symbol_key: Key from FUTURES (e.g., 'es', 'crude_oil', 'gold')
    """
    if symbol_key not in FUTURES:
        raise ValueError(f"Unknown future: {symbol_key}. Available: {list(FUTURES.keys())}")
    
    return get_price_history(FUTURES[symbol_key], **kwargs)


def get_sp500_futures(**kwargs) -> List[Dict]:
    """Get E-mini S&P 500 Futures."""
    return get_future("es", **kwargs)


def get_crude_oil(**kwargs) -> List[Dict]:
    """Get WTI Crude Oil Futures."""
    return get_future("crude_oil", **kwargs)


def get_gold(**kwargs) -> List[Dict]:
    """Get Gold Futures."""
    return get_future("gold", **kwargs)


def get_silver(**kwargs) -> List[Dict]:
    """Get Silver Futures."""
    return get_future("silver", **kwargs)


def get_natural_gas(**kwargs) -> List[Dict]:
    """Get Natural Gas Futures."""
    return get_future("natural_gas", **kwargs)


# ============================================================================
# COMMODITIES - Spot Prices (via Yahoo Finance ETFs/ETNs as proxy)
# ============================================================================

COMMODITY_ETFS = {
    # Precious Metals
    "gold_spot": "GLD",         # SPDR Gold Trust
    "silver_spot": "SLV",       # iShares Silver Trust
    "gold_miners": "GDX",       # VanEck Gold Miners ETF
    "junior_gold": "GDXJ",      # VanEck Junior Gold Miners
    
    # Oil & Gas
    "oil_etf": "USO",           # United States Oil Fund
    "brent_etf": "BNO",         # United States Brent Oil Fund
    "natural_gas_etf": "UNG",   # United States Natural Gas Fund
    
    # Broad Commodities
    "commodities_broad": "DBC", # Invesco DB Commodity Tracking
    "agriculture": "DBA",       # Invesco DB Agriculture Fund
    "base_metals": "DBB",       # Invesco DB Base Metals Fund
    "energy": "DBE",            # Invesco DB Energy Fund
    
    # Others
    "uranium": "URA",           # Global X Uranium ETF
    "lithium": "LIT",           # Global X Lithium & Battery Tech
    "copper_miners": "COPX",    # Global X Copper Miners ETF
}

def get_commodity_etf(symbol_key: str, **kwargs) -> List[Dict]:
    """
    Get commodity ETF data (as proxy for commodity prices).
    
    Args:
        symbol_key: Key from COMMODITY_ETFS
    """
    if symbol_key not in COMMODITY_ETFS:
        raise ValueError(f"Unknown commodity ETF: {symbol_key}")
    
    return get_price_history(COMMODITY_ETFS[symbol_key], **kwargs)


def get_gold_etf(**kwargs) -> List[Dict]:
    """Get SPDR Gold Trust (GLD) - Gold price proxy."""
    return get_commodity_etf("gold_spot", **kwargs)


def get_silver_etf(**kwargs) -> List[Dict]:
    """Get iShares Silver Trust (SLV) - Silver price proxy."""
    return get_commodity_etf("silver_spot", **kwargs)


def get_oil_etf(**kwargs) -> List[Dict]:
    """Get US Oil Fund (USO) - Oil price proxy."""
    return get_commodity_etf("oil_etf", **kwargs)


def list_available_indices() -> Dict[str, str]:
    """List all available indices."""
    return MAJOR_INDICES.copy()


def list_available_futures() -> Dict[str, str]:
    """List all available futures."""
    return FUTURES.copy()


def list_available_commodity_etfs() -> Dict[str, str]:
    """List all available commodity ETFs."""
    return COMMODITY_ETFS.copy()


if __name__ == "__main__":
    # Test examples
    print("Testing Asian market data...")
    
    # Hong Kong - Tencent
    print("\n--- Hong Kong: Tencent (0700.HK) ---")
    tencent = get_current_price("0700.HK")
    if tencent:
        print(f"Tencent: {tencent['price']} {tencent['currency']}")
    
    # Japan - Toyota
    print("\n--- Japan: Toyota (7203.T) ---")
    toyota = get_current_price("7203.T")
    if toyota:
        print(f"Toyota: {toyota['price']} {toyota['currency']}")
    
    # Taiwan - TSMC
    print("\n--- Taiwan: TSMC (2330.TW) ---")
    tsmc = get_current_price("2330.TW")
    if tsmc:
        print(f"TSMC: {tsmc['price']} {tsmc['currency']}")
    
    # Korea - Samsung
    print("\n--- Korea: Samsung (005930.KS) ---")
    samsung = get_current_price("005930.KS")
    if samsung:
        print(f"Samsung: {samsung['price']} {samsung['currency']}")
