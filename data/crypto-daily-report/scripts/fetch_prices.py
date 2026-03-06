#!/usr/bin/env python3
"""
获取现货价格（BTC/ETH/SOL）+ HYPE 合约价格
错误处理：单个 symbol 失败不中断，标记 N/A，最多重试2次
"""
import urllib.request
import urllib.error
import json
import time

SPOT_SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
FUTURES_SYMBOLS = ['HYPEUSDT']
MAX_RETRIES = 2
TIMEOUT = 8

def fetch_with_retry(url, retries=MAX_RETRIES):
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            return json.loads(urllib.request.urlopen(req, timeout=TIMEOUT).read())
        except urllib.error.HTTPError as e:
            err = f"HTTP {e.code}"
        except urllib.error.URLError as e:
            err = f"URLError: {e.reason}"
        except Exception as e:
            err = str(e)
        if attempt < retries:
            time.sleep(1.5 ** attempt)
    return None, err

results = []

for s in SPOT_SYMBOLS:
    url = f'https://api.binance.com/api/v3/ticker/24hr?symbol={s}'
    d = fetch_with_retry(url)
    if isinstance(d, tuple):  # 失败
        results.append({'symbol': s.replace('USDT',''), 'error': d[1], 'type': 'spot'})
    else:
        results.append({
            'symbol': s.replace('USDT', ''),
            'price': float(d['lastPrice']),
            'change': float(d['priceChangePercent']),
            'type': 'spot'
        })

for s in FUTURES_SYMBOLS:
    url = f'https://fapi.binance.com/fapi/v1/ticker/24hr?symbol={s}'
    d = fetch_with_retry(url)
    if isinstance(d, tuple):
        results.append({'symbol': s.replace('USDT',''), 'error': d[1], 'type': 'futures'})
    else:
        results.append({
            'symbol': s.replace('USDT', ''),
            'price': float(d['lastPrice']),
            'change': float(d['priceChangePercent']),
            'type': 'futures'
        })

for r in results:
    if 'error' in r:
        tag = '（合约）' if r['type'] == 'futures' else ''
        print(f"{r['symbol']}: [DATA UNAVAILABLE]{tag}  # {r['error']}")
    else:
        sign = '+' if r['change'] > 0 else ''
        tag = '（合约）' if r['type'] == 'futures' else ''
        print(f"{r['symbol']}: ${r['price']:,.2f} {sign}{r['change']:.2f}%{tag}")
