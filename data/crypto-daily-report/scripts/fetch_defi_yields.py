#!/usr/bin/env python3
"""
从 DeFiLlama yields API 获取主流协议生息机会
错误处理：超时/失败时降级到缓存或输出提示
"""
import urllib.request
import urllib.error
import json
import time
import sys

TOP_N = int(sys.argv[1]) if len(sys.argv) > 1 else 5
MIN_TVL = 10_000_000
MAX_RETRIES = 2
TIMEOUT = 15

KNOWN_PROTOCOLS = [
    'aave', 'compound', 'morpho', 'spark', 'fluid',
    'pendle', 'ethena', 'maker', 'sky', 'sparklend',
    'curve', 'convex', 'yearn', 'notional'
]

# 备用：若 DeFiLlama 不可用时展示的静态提示
FALLBACK_MSG = "[DATA UNAVAILABLE] DeFiLlama 暂时无响应，请访问 https://defillama.com/yields 查看最新收益率"

def fetch_with_retry(url, retries=MAX_RETRIES):
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            return json.loads(urllib.request.urlopen(req, timeout=TIMEOUT).read())
        except urllib.error.HTTPError as e:
            err = f"HTTP {e.code}"
        except urllib.error.URLError as e:
            err = f"Timeout: {e.reason}"
        except Exception as e:
            err = str(e)
        if attempt < retries:
            time.sleep(2 ** attempt)
    return None, err

data = fetch_with_retry('https://yields.llama.fi/pools')

if isinstance(data, tuple):
    print(FALLBACK_MSG, file=sys.stderr)
    print(FALLBACK_MSG)
    sys.exit(0)

pools = data.get('data', [])
filtered = [
    p for p in pools
    if any(k in p.get('project', '').lower() for k in KNOWN_PROTOCOLS)
    and float(p.get('apy', 0) or 0) > 0
    and float(p.get('tvlUsd', 0) or 0) >= MIN_TVL
]
filtered.sort(key=lambda x: float(x.get('apy', 0) or 0), reverse=True)

for p in filtered[:TOP_N]:
    project = p.get('project', '')
    symbol = p.get('symbol', '')
    chain = p.get('chain', '')
    apy = float(p.get('apy', 0) or 0)
    tvl = float(p.get('tvlUsd', 0) or 0)
    tvl_str = f'${tvl/1_000_000:.0f}M' if tvl >= 1_000_000 else f'${tvl/1_000:.0f}K'
    print(f"{project} · {symbol} · {chain} | APY {apy:.1f}% | TVL {tvl_str}")
