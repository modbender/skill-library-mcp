#!/usr/bin/env python3
"""
从 GeckoTerminal 获取 Solana 链上 trending pools
筛选：24h涨幅>50% 或 量>$50万，FDV<$5000万
错误处理：GeckoTerminal 失败时降级到 DEXScreener token-boosts
"""
import urllib.request
import urllib.error
import json
import time
import sys

MAX_RETRIES = 2
TIMEOUT = 10

def human_number(n):
    n = float(n or 0)
    if n >= 1_000_000:
        return f'${n/1_000_000:.1f}M'
    elif n >= 1_000:
        return f'${n/1_000:.0f}K'
    else:
        return f'${n:.0f}'

def fetch_json(url, headers=None, retries=MAX_RETRIES):
    _headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
    if headers:
        _headers.update(headers)
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=_headers)
            return json.loads(urllib.request.urlopen(req, timeout=TIMEOUT).read())
        except urllib.error.HTTPError as e:
            err = f"HTTP {e.code}"
        except urllib.error.URLError as e:
            err = f"Timeout/URLError: {e.reason}"
        except Exception as e:
            err = str(e)
        if attempt < retries:
            time.sleep(1.5 ** attempt)
    return None, err

def parse_geckoterminal(data):
    pools = data.get('data', [])
    results = []
    for p in pools:
        attr = p.get('attributes', {})
        name = attr.get('name', '').split(' / ')[0]
        change_24h = float(attr.get('price_change_percentage', {}).get('h24', 0) or 0)
        vol_24h = float(attr.get('volume_usd', {}).get('h24', 0) or 0)
        fdv = float(attr.get('fdv_usd', 0) or 0)
        pool_id = p.get('id', '').split('_')[-1]
        url = f"https://www.geckoterminal.com/solana/pools/{pool_id}"
        if (change_24h > 50 or vol_24h > 500_000) and (fdv < 50_000_000 or fdv == 0):
            results.append({'name': name, 'change_24h': change_24h,
                            'vol_24h': vol_24h, 'fdv': fdv, 'url': url})
    results.sort(key=lambda x: x['change_24h'], reverse=True)
    return results[:5]

def parse_dexscreener(data):
    """降级数据源：DEXScreener token boosts（按推广金额排序，非涨幅）"""
    items = data if isinstance(data, list) else []
    results = []
    for x in items[:5]:
        chain = x.get('chainId', '')
        if chain != 'solana':
            continue
        addr = x.get('tokenAddress', '')
        desc = x.get('description', addr[:12])
        url = x.get('url', f'https://dexscreener.com/solana/{addr}')
        results.append({'name': desc[:20], 'change_24h': None,
                        'vol_24h': None, 'fdv': None, 'url': url})
    return results

# --- 主逻辑 ---
# 优先：GeckoTerminal
data = fetch_json('https://api.geckoterminal.com/api/v2/networks/solana/trending_pools?page=1')

if isinstance(data, tuple):
    # GeckoTerminal 失败，降级到 DEXScreener
    print(f"⚠️ GeckoTerminal 不可用（{data[1]}），降级到 DEXScreener", file=sys.stderr)
    data2 = fetch_json('https://api.dexscreener.com/token-boosts/top/v1')
    if isinstance(data2, tuple):
        print("今日 Meme 数据暂时不可用（GeckoTerminal & DEXScreener 均无响应）")
        sys.exit(0)
    results = parse_dexscreener(data2)
    source = 'DEXScreener（降级）'
else:
    results = parse_geckoterminal(data)
    source = 'GeckoTerminal Solana'

if not results:
    print("今日 Meme 市场无明显飙升标的")
else:
    print(f"# 来源: {source}")
    for r in results:
        if r['change_24h'] is not None:
            sign = '+' if r['change_24h'] > 0 else ''
            vol_str = human_number(r['vol_24h']) if r['vol_24h'] else 'N/A'
            fdv_str = human_number(r['fdv']) if r['fdv'] else 'N/A'
            print(f"{r['name']} · {sign}{r['change_24h']:.0f}% · 量 {vol_str} · FDV {fdv_str}")
        else:
            print(f"{r['name']} · [涨幅数据不可用]")
        print(f"→ {r['url']}")
        print()
