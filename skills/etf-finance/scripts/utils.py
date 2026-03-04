#!/usr/bin/env python3
"""
Utility functions for etf-investor skill.
"""
import json
import os
from datetime import datetime
from config import POSITIONS_FILE, ALERTS_FILE, PRICES_FILE


def load_positions():
    """Load positions from JSON file."""
    if not os.path.exists(POSITIONS_FILE):
        return []
    try:
        with open(POSITIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_positions(positions):
    """Save positions to JSON file."""
    with open(POSITIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(positions, f, indent=2, ensure_ascii=False)


def load_alerts():
    """Load alerts from JSON file."""
    if not os.path.exists(ALERTS_FILE):
        return []
    try:
        with open(ALERTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_alerts(alerts):
    """Save alerts to JSON file."""
    with open(ALERTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(alerts, f, indent=2, ensure_ascii=False)


def get_price(symbol):
    """Get current price for a symbol using 腾讯财经 (Tencent Finance) for Chinese stocks, yfinance for US stocks."""
    # 判断是中国股票还是美股
    # 中国A股: 6位数字代码 (如 512400, 513050)
    # 美股: 字母代码 (如 SPY, QQQ)
    
    if symbol.isdigit() and len(symbol) == 6:
        # 中国A股 - 使用腾讯财经
        return get_price_tencent(symbol)
    else:
        # 美股 - 使用 yfinance
        return get_price_yahoo(symbol)


def get_price_tencent(symbol):
    """Get current price for Chinese A-shares using 腾讯财经 API."""
    import urllib.request
    import json
    
    # 添加市场前缀: 上海 sh, 深圳 sz
    if symbol.startswith(('6', '5')):
        market = 'sh' + symbol
    else:
        market = 'sz' + symbol
    
    url = f'https://qt.gtimg.cn/q={market}'
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read().decode('gbk', errors='ignore')
            
            # 解析返回数据格式: v_sh512400="1~512400~512400~2.264~..."
            if '~' in data:
                parts = data.split('~')
                if len(parts) > 3:
                    price = float(parts[3])
                    return price
            return None
    except Exception as e:
        print(f"Error getting price from 腾讯财经 for {symbol}: {e}")
        return None


def get_price_yahoo(symbol):
    """Get current price for US stocks using yfinance."""
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        info = ticker.info
        if info and 'regularMarketPrice' in info:
            return info['regularMarketPrice']
        elif info and 'currentPrice' in info:
            return info['currentPrice']
        elif info and 'previousClose' in info:
            return info['previousClose']
        else:
            # Try fast_info as fallback
            fast_info = ticker.fast_info
            if fast_info and 'last_price' in fast_info:
                return fast_info['last_price']
            return None
    except Exception as e:
        print(f"Error getting price from Yahoo for {symbol}: {e}")
        return None


def format_currency(value):
    """Format value as currency string."""
    if value is None:
        return "N/A"
    return f"${value:,.2f}"


def format_percentage(value):
    """Format value as percentage string."""
    if value is None:
        return "N/A"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}%"


def calculate_pnl(position, current_price):
    """Calculate profit/loss for a position."""
    if not position or current_price is None:
        return {
            'cost': None,
            'value': None,
            'pnl': None,
            'pnl_pct': None
        }

    cost = position['buy_price'] * position['quantity']
    value = current_price * position['quantity']
    pnl = value - cost
    pnl_pct = ((current_price - position['buy_price']) / position['buy_price']) * 100

    return {
        'cost': cost,
        'value': value,
        'pnl': pnl,
        'pnl_pct': pnl_pct
    }


def find_position(symbol, positions):
    """Find a position by symbol."""
    for pos in positions:
        if pos['symbol'].upper() == symbol.upper():
            return pos
    return None


def find_alert(symbol, alerts):
    """Find alerts by symbol."""
    found = []
    for alert in alerts:
        if alert['symbol'].upper() == symbol.upper():
            found.append(alert)
    return found
