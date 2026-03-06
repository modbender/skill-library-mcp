"""
Sentry-AI: Multi-Chain Meme Scanner
Scans new token pools on Solana/Base chains
"""
import requests
import time
import json

CHAINS = {
    'solana': 'https://api.dexscreener.com/latest/dex/tokens/solana',
    'base': 'https://api.dexscreener.com/latest/dex/tokens/base'
}

def scan_chain(chain_name, limit=10):
    """Scan new pools on a specific chain"""
    url = CHAINS.get(chain_name)
    if not url:
        return []
    
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        
        pairs = data.get('pairs', [])[:limit]
        
        results = []
        for pair in pairs:
            liquidity = pair.get('liquidity', {}).get('usd', 0)
            if liquidity < 1000:
                continue
            
            results.append({
                'chain': chain_name,
                'symbol': pair.get('baseToken', {}).get('symbol', 'UNKNOWN'),
                'name': pair.get('baseToken', {}).get('name', 'Unknown'),
                'address': pair.get('baseToken', {}).get('address', ''),
                'price': pair.get('priceUsd', '0'),
                'liquidity': liquidity,
                'volume24h': pair.get('volume', {}).get('h24', 0),
                'url': pair.get('url', '')
            })
        
        return results
        
    except Exception as e:
        print(f"Error scanning {chain_name}: {e}")
        return []

def scan_all():
    """Scan all supported chains"""
    all_results = []
    
    for chain in CHAINS.keys():
        pools = scan_chain(chain)
        all_results.extend(pools)
    
    return all_results

def calculate_risk_score(token_data):
    """
    Calculate risk score based on multiple factors
    Returns 0-100 score
    """
    score = 50  # Base score
    
    # Liquidity factor
    liquidity = token_data.get('liquidity', 0)
    if liquidity > 100000:
        score += 20
    elif liquidity > 50000:
        score += 10
    
    # Volume factor
    volume = token_data.get('volume24h', 0)
    if volume > 100000:
        score += 15
    elif volume > 50000:
        score += 10
    
    # Risk adjustments
    if liquidity < 10000:
        score -= 30
    if volume < 1000:
        score -= 20
    
    return max(0, min(100, score))

if __name__ == "__main__":
    print("[SENTRY-AI] Starting scan...")
    
    results = scan_all()
    
    print(f"Found {len(results)} pools")
    
    for token in results:
        risk = calculate_risk_score(token)
        status = "SAFE" if risk >= 70 else "RISKY"
        
        print(f"[{status}] {token['symbol']} - Risk Score: {risk}/100")
        print(f"  Liquidity: ${token['liquidity']:,.0f}")
        print(f"  URL: {token['url']}")
        print()
