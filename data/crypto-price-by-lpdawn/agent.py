#!/home/openclaw_admin/.openclaw/venv/bin/python
import ccxt
import sys

def get_price(symbol):
    try:
        exchange = ccxt.binance()
        ticker = exchange.fetch_ticker(symbol + '/USDT')
        price = ticker['last']
        change = ticker['percentage']
        return f"{symbol.upper()} 当前价格: ${price:,.2f} USDT\n24h涨跌: {change:+.2f}%"
    except Exception as e:
        return f"查询失败: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        symbol = sys.argv[1].upper()
        print(get_price(symbol))
    else:
        print(get_price("BTC"))
