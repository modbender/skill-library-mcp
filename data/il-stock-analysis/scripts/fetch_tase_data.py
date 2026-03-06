#!/usr/bin/env python3
"""
fetch_tase_data.py - Fetch TASE stock data via APIs
Usage:
    python3 fetch_tase_data.py ALRT
    python3 fetch_tase_data.py ALRT --type price
    python3 fetch_tase_data.py "בנק לאומי" --type fundamental
"""

import sys
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import urllib.request
import urllib.error

# Hebrew to ticker mapping
HEBREW_TO_TICKER = {
    "בנק לאומי": "LUMI",
    "בנק הפועלים": "POLI",
    "בנק דיסקונט": "DSCT",
    "אלביט": "ALRT",
    "טבע": "TEVA",
    "פלאפון": "PELEOT",
}

# ETF number to ticker mapping
ETF_TO_TICKER = {
    "510893": "TA25",
    "770001": "TA35",
}


def normalize_ticker(identifier: str) -> str:
    """Convert Hebrew name or ETF number to TASE ticker."""
    # Check Hebrew to ticker mapping
    if identifier in HEBREW_TO_TICKER:
        return HEBREW_TO_TICKER[identifier]
    
    # Check ETF mapping
    if identifier in ETF_TO_TICKER:
        return ETF_TO_TICKER[identifier]
    
    # Normalize and add .TA suffix
    ticker = identifier.upper()
    if not any(ticker.endswith(suffix) for suffix in [".TA", ".IL"]):
        ticker = f"{ticker}.TA"
    
    return ticker


def fetch_finnhub(ticker: str) -> Optional[Dict[str, Any]]:
    """Fetch data from Finnhub API."""
    api_key = os.getenv("FINNHUB_API_KEY")
    if not api_key:
        return None
    
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={api_key}"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            
            return {
                "source": "Finnhub",
                "ticker": ticker,
                "price": data.get("c"),
                "high": data.get("h"),
                "low": data.get("l"),
                "open": data.get("o"),
                "previous_close": data.get("pc"),
                "volume": data.get("v"),
                "timestamp": data.get("t"),
                "currency": "ILS"
            }
    except (urllib.error.URLError, json.JSONDecodeError, KeyError):
        return None


def fetch_alpha_vantage(ticker: str) -> Optional[Dict[str, Any]]:
    """Fetch data from Alpha Vantage API."""
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
    
    try:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={api_key}"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            
            quote = data.get("Global Quote", {})
            return {
                "source": "Alpha Vantage",
                "ticker": ticker,
                "price": float(quote.get("05. price", 0) or 0),
                "change": float(quote.get("09. change", 0) or 0),
                "change_percent": quote.get("10. change percent", ""),
                "timestamp": datetime.now().isoformat()
            }
    except (urllib.error.URLError, json.JSONDecodeError, ValueError):
        return None


def fetch_mock_data(ticker: str) -> Dict[str, Any]:
    """Return mock data template."""
    return {
        "source": "Template - Live API Not Configured",
        "ticker": ticker,
        "price": None,
        "currency": "ILS",
        "message": "Set FINNHUB_API_KEY environment variable for live data",
        "setup_instructions": "1. Get free API key from finnhub.io\n2. export FINNHUB_API_KEY=your_key\n3. Re-run this script"
    }


def fetch_price_data(ticker: str) -> Dict[str, Any]:
    """Fetch price data from available sources."""
    # Try Finnhub first
    if os.getenv("FINNHUB_API_KEY"):
        result = fetch_finnhub(ticker)
        if result:
            return result
    
    # Try Alpha Vantage
    result = fetch_alpha_vantage(ticker)
    if result:
        return result
    
    # Return mock data
    return fetch_mock_data(ticker)


def fetch_fundamental_data(ticker: str) -> Dict[str, Any]:
    """Return fundamental data template."""
    return {
        "ticker": ticker,
        "source": "Template - Requires Configured API",
        "financial_metrics": {
            "revenue": None,
            "net_income": None,
            "eps": None,
            "pe_ratio": None,
            "book_value": None,
            "roe": None,
            "dividend_yield": None
        },
        "message": "Configure FINNHUB_API_KEY to fetch real fundamental data"
    }


def fetch_technical_data(ticker: str) -> Dict[str, Any]:
    """Return technical data template."""
    return {
        "ticker": ticker,
        "source": "Template - Requires Historical Price Data",
        "technical_indicators": {
            "moving_average_20": None,
            "moving_average_50": None,
            "moving_average_200": None,
            "rsi": None,
            "macd": None,
            "bollinger_bands": None
        },
        "message": "Configure API with historical price data for technical analysis"
    }


def main():
    if len(sys.argv) < 2:
        print('{"error": "Usage: fetch_tase_data.py <ticker> [--type price|fundamental|technical|all]"}')
        sys.exit(1)
    
    identifier = sys.argv[1]
    data_type = "price"
    
    # Parse --type argument
    if "--type" in sys.argv:
        idx = sys.argv.index("--type")
        if idx + 1 < len(sys.argv):
            data_type = sys.argv[idx + 1]
    
    # Normalize identifier
    ticker = normalize_ticker(identifier)
    
    # Fetch data based on type
    result = {}
    
    if data_type in ["price", "all"]:
        result["price_data"] = fetch_price_data(ticker)
    
    if data_type in ["fundamental", "all"]:
        result["fundamental_data"] = fetch_fundamental_data(ticker)
    
    if data_type in ["technical", "all"]:
        result["technical_data"] = fetch_technical_data(ticker)
    
    if data_type not in ["price", "fundamental", "technical", "all"]:
        result = {"error": f"Unknown data type: {data_type}"}
    
    # Add metadata
    if not result:
        result = {"price_data": fetch_price_data(ticker)}
    
    result["ticker"] = ticker
    result["identifier"] = identifier
    result["timestamp"] = datetime.now().isoformat()
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
