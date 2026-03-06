#!/usr/bin/env python3
"""
PlusE Financial Data CLI

Usage: python plusefin.py <command> [args]

Commands:
  ticker <symbol>              - Get stock ticker data
  price-history <ticker> <period> - Get price history (e.g., "6mo", "1y")
  options <symbol> [num]       - Get options chain
  statements <symbol> [type]   - Get financial statements (income/balance/cash)
  earnings <symbol>            - Get earnings history
  news <symbol>                - Get stock news
  holders <symbol>             - Get institutional holders
  top25 <symbol>               - Get top 25 holders
  insiders <symbol>            - Get insider trading data
  sentiment                    - Get market sentiment index
  sentiment-history [days]     - Get historical sentiment
  prediction <symbol>          - Get price prediction
  fred <series_id>             - Get FRED economic data
  fred-search <query>          - Search FRED series
  news-market                  - Get CNBC market news
  news-social <keywords>       - Get social media discussions

Environment:
  PLUSEFIN_API_KEY - Your PlusE API key (required)
"""

import os
import sys
import urllib.request
import urllib.error

API_KEY = os.environ.get("PLUSEFIN_API_KEY", "")
BASE_URL = "https://mcp.plusefin.com/api"


def request(endpoint, params=None):
    url = f"{BASE_URL}{endpoint}"
    if params:
        query = "&".join(f"{k}={v}" for k, v in params.items() if v is not None and v != "")
        if query:
            url += "?" + query
    
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Python/urllib")
    if API_KEY:
        req.add_header("Authorization", f"Bearer {API_KEY}")
    else:
        return "Error: PLUSEFIN_API_KEY environment variable not set"
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else "No error details"
        return f"Error: HTTP {e.code} - {error_body}"
    except urllib.error.URLError as e:
        return f"Error: URL error - {e.reason}"
    except Exception as e:
        return f"Error: {str(e)}"


def print_help():
    print(__doc__)


def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    
    commands = {
        "ticker": lambda: request(f"/tools/ticker/{sys.argv[2]}") if len(sys.argv) > 2 else "Error: symbol required",
        
        "price-history": lambda: request("/tools/price-history", {
            "ticker": sys.argv[2] if len(sys.argv) > 2 else None,
            "period": sys.argv[3] if len(sys.argv) > 3 else "6mo"
        }) if len(sys.argv) > 2 else "Error: ticker required",
        
        "options": lambda: request(f"/tools/options/{sys.argv[2]}", {
            "num_options": sys.argv[3] if len(sys.argv) > 3 else "20"
        }) if len(sys.argv) > 2 else "Error: symbol required",
        
        "options-analyze": lambda: request(f"/tools/options/analyze/{sys.argv[2]}") if len(sys.argv) > 2 else "Error: symbol required",
        
        "statements": lambda: request(f"/tools/statements/{sys.argv[2]}", {
            "type": sys.argv[3] if len(sys.argv) > 3 else "income",
            "frequency": sys.argv[4] if len(sys.argv) > 4 else "quarterly"
        }) if len(sys.argv) > 2 else "Error: symbol required",
        
        "earnings": lambda: request(f"/tools/earnings/{sys.argv[2]}") if len(sys.argv) > 2 else "Error: symbol required",
        
        "news": lambda: request(f"/tools/news/{sys.argv[2]}") if len(sys.argv) > 2 else "Error: symbol required",
        
        "holders": lambda: request(f"/tools/holders/{sys.argv[2]}") if len(sys.argv) > 2 else "Error: symbol required",
        
        "top25": lambda: request(f"/tools/top25/{sys.argv[2]}") if len(sys.argv) > 2 else "Error: symbol required",
        
        "insiders": lambda: request(f"/tools/insiders/{sys.argv[2]}") if len(sys.argv) > 2 else "Error: symbol required",
        
        "sentiment": lambda: request("/tools/sentiment"),
        
        "sentiment-history": lambda: request("/tools/sentiment/history", {
            "days": sys.argv[2] if len(sys.argv) > 2 else "10"
        }),
        
        "sentiment-trend": lambda: request("/tools/sentiment/trend", {
            "days": sys.argv[2] if len(sys.argv) > 2 else "10"
        }),
        
        "prediction": lambda: request(f"/tools/prediction/{sys.argv[2]}") if len(sys.argv) > 2 else "Error: symbol required",
        
        "fred": lambda: request(f"/tools/fred/{sys.argv[2]}") if len(sys.argv) > 2 else "Error: series_id required",
        
        "fred-search": lambda: request("/tools/fred/search", {
            "q": sys.argv[2] if len(sys.argv) > 2 else None
        }) if len(sys.argv) > 2 else "Error: query required",
        
        "news-market": lambda: request("/tools/news/market"),
        
        "news-social": lambda: request("/tools/news/social", {
            "keywords": sys.argv[2] if len(sys.argv) > 2 else None
        }) if len(sys.argv) > 2 else "Error: keywords required",
        
        "help": lambda: print_help() or "",
        
        "--help": lambda: print_help() or "",
        
        "-h": lambda: print_help() or "",
    }
    
    if cmd in commands:
        result = commands[cmd]()
        if result:
            print(result)
    else:
        print(f"Unknown command: {cmd}")
        print("Run 'python plusefin.py help' for usage information")
        sys.exit(1)


if __name__ == "__main__":
    main()
