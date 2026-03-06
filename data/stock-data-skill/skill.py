#!/usr/bin/env python3
"""
Stock Data - Simplywall.st Data Fetcher for OpenClaw
Fetches comprehensive stock data from Simplywall.st

Direct HTTP fetch (no API key required)
"""

import json
import re
import asyncio
from datetime import datetime, timezone
from typing import Optional, Dict, Any

try:
    import aiohttp
except ImportError:
    raise ImportError('aiohttp required: pip install aiohttp')


def get_stock_url(ticker: str, exchange: Optional[str] = None) -> str:
    """Construct URL for stock page based on exchange"""
    ticker_lower = ticker.lower()
    exchange = (exchange or 'idx').lower()

    patterns = {
        'idx': f'https://simplywall.st/stock/idx/{ticker_lower}',
        'nasdaq': f'https://simplywall.st/stocks/us/any/nasdaq-{ticker_lower}/{ticker_lower}',
        'nyse': f'https://simplywall.st/stocks/us/any/nyse-{ticker_lower}/{ticker_lower}',
        'asx': f'https://simplywall.st/stock/asx/{ticker_lower}',
        'lse': f'https://simplywall.st/stock/lse/{ticker_lower}',
        'tsx': f'https://simplywall.st/stock/tsx/{ticker_lower}',
        'sgx': f'https://simplywall.st/stock/sgx/{ticker_lower}',
        'tse': f'https://simplywall.st/stock/tse/{ticker_lower}',
        'hkse': f'https://simplywall.st/stock/hkse/{ticker_lower}',
        'krx': f'https://simplywall.st/stock/krx/{ticker_lower}',
    }
    return patterns.get(exchange, patterns['idx'])


def parse_react_state(html: str) -> Dict:
    """Extract and parse __REACT_QUERY_STATE__ from HTML"""
    match = re.search(r'window\.__REACT_QUERY_STATE__\s*=\s*(\{[\s\S]+?\});?\s*</script>', html)
    if not match:
        return {}

    json_str = match.group(1)
    # Fix undefined values in JSON
    json_str = re.sub(r':undefined([,\]}])', r':null\1', json_str)
    json_str = re.sub(r'([,\[{])undefined([,\]}])', r'\1null\2', json_str)

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return {}


def extract_data(state: Dict, ticker: str) -> Dict:
    """Extract structured stock data from React Query state"""
    result = {
        'ticker': ticker.upper(),
        'exchange': None,
        'company': {},
        'price': {},
        'valuation': {},
        'financials': {},
        'dividend': {},
        'forecast': {},
        'snowflake': {},
        'recentEvents': [],
        'fetchedAt': datetime.now(timezone.utc).isoformat()
    }

    for query in state.get('queries', []):
        qd = query.get('state', {}).get('data', {})

        # Company info
        if 'Company' in qd:
            info = qd['Company'].get('data', {}).get('info', {})
            result['exchange'] = info.get('exchange_symbol')
            result['company'] = {
                'name': info.get('name'),
                'description': info.get('short_description'),
                'country': info.get('country'),
                'founded': info.get('year_founded'),
                'website': info.get('url')
            }

        # Analysis data (valuation, financials, dividend, forecast)
        if 'data' in qd and 'analysis' in qd.get('data', {}):
            a = qd['data']['analysis'].get('data', {})
            ext = a.get('extended', {}).get('data', {}).get('analysis', {})

            result['valuation'] = {
                'marketCap': a.get('market_cap'),
                'peRatio': a.get('pe'),
                'pbRatio': a.get('pb'),
                'pegRatio': a.get('peg'),
                'intrinsicDiscount': a.get('intrinsic_discount'),
                'status': 'overvalued' if (a.get('intrinsic_discount') or 0) < 0 else 'undervalued'
            }
            result['financials'] = {
                'eps': a.get('eps'),
                'roe': a.get('roe'),
                'roa': a.get('roa'),
                'debtEquity': a.get('debt_equity')
            }
            result['dividend'] = {
                'yield': a.get('dividend', {}).get('current'),
                'futureYield': a.get('dividend', {}).get('future'),
                'payingYears': ext.get('dividend', {}).get('dividend_paying_years'),
                'payoutRatio': ext.get('dividend', {}).get('payout_ratio')
            }
            result['forecast'] = {
                'earningsGrowth1Y': a.get('future', {}).get('growth_1y'),
                'roe1Y': a.get('future', {}).get('roe_1y'),
                'analystCount': a.get('analyst_count')
            }

        # Snowflake & Price data
        if qd.get('snowflake', {}).get('data', {}).get('axes'):
            axes = qd['snowflake']['data']['axes']
            result['snowflake'] = {
                'value': axes[0] if len(axes) > 0 else None,
                'future': axes[1] if len(axes) > 1 else None,
                'past': axes[2] if len(axes) > 2 else None,
                'health': axes[3] if len(axes) > 3 else None,
                'dividend': axes[4] if len(axes) > 4 else None
            }
            result['price'] = {
                'lastSharePrice': qd.get('last_share_price'),
                'currency': qd.get('currency_iso'),
                'return7D': qd.get('return_7d'),
                'return1Yr': qd.get('return_1yr_abs')
            }
            # Recent events
            events = qd.get('events', {}).get('data', [])
            result['recentEvents'] = [
                {'title': e.get('title'), 'description': (e.get('description') or '')[:200]}
                for e in events[:5]
            ]

    return result


async def fetch_stock(ticker: str, exchange: Optional[str] = None) -> Dict:
    """Main function to fetch stock data"""
    url = get_stock_url(ticker, exchange)

    print(f'[stock_data] Fetching: {url}')

    # Direct HTTP fetch
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            if resp.status != 200:
                return {'success': False, 'error': f'HTTP error {resp.status}'}

            html = await resp.text()
            print(f'[stock_data] HTML length: {len(html)}')

            # Parse SimplyWall.st data from HTML
            state = parse_react_state(html)
            data = extract_data(state, ticker)
            data['url'] = url
            data['data_source'] = 'direct_http'

            return {'success': True, 'data': data}


# OpenClaw skill interface
async def execute(params: Dict) -> Dict:
    """OpenClaw skill executor"""
    ticker = params.get('ticker')
    if not ticker:
        return {'success': False, 'error': 'ticker parameter is required'}

    try:
        return await fetch_stock(ticker, params.get('exchange'))
    except Exception as e:
        return {'success': False, 'error': str(e)}


# Skill metadata
METADATA = {
    'name': 'stock_data',
    'description': 'Fetch comprehensive stock data from Simplywall.st',
    'category': 'finance',
    'tags': ['stock', 'valuation', 'analysis', 'simplywall', 'investment'],
    'triggers': ['saham', 'stock', 'cek saham', 'valuation', 'dividend', 'analisa'],
    'requiredEnvVars': [],  # No API key required - direct HTTP fetch
    'version': '1.3.0',
    'changelog': 'v1.3.0 - Switch to direct HTTP fetch (no API key required)',
    'author': 'OpenClaw Community'
}


if __name__ == '__main__':
    import sys
    ticker = sys.argv[1] if len(sys.argv) > 1 else 'ADRO'
    exchange = sys.argv[2] if len(sys.argv) > 2 else 'IDX'

    print(f'Stock Data Skill Test: {ticker} ({exchange})\n')
    result = asyncio.run(execute({'ticker': ticker, 'exchange': exchange}))
    print(json.dumps(result, indent=2, default=str))
