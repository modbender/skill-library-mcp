#!/usr/bin/env python3
"""
On-chain portfolio indexer with blockchain explorer API support.

Usage:
    python indexer.py --address 0x...
    python indexer.py --address 0x... --chain base
    python indexer.py --address 0x... --output json
"""

import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime

# ============================================================================
# Chain Configurations
# ============================================================================

CHAIN_CONFIGS = {
    "ethereum": {
        "name": "Ethereum",
        "chain_id": 1,
        "rpcs": ["https://cloudflare-eth.com", "https://mainnet.gateway.fm"],
        "alchemy_template": "https://eth-mainnet.g.alchemy.com/v2/{api_key}",
        "explorer_api": "https://api.etherscan.io/v2/api",
        "explorer_env_key": "ETHERSCAN_API_KEY",
    },
    "base": {
        "name": "Base",
        "chain_id": 8453,
        "rpcs": ["https://mainnet.base.org", "https://base.llamarpc.com"],
        "alchemy_template": "https://base-mainnet.g.alchemy.com/v2/{api_key}",
        "explorer_api": "https://api.basescan.org/api",
        "explorer_env_key": "BASESCAN_API_KEY",
    },
}

# Price symbol to CoinGecko ID mapping
SYMBOL_TO_COINGECKO = {
    "ETH": "ethereum", "WETH": "ethereum", "USDC": "usd-coin",
    "USDT": "tether", "DAI": "dai", "LINK": "chainlink",
    "UNI": "uniswap", "AAVE": "aave", "stETH": "staked-ether",
}


# ============================================================================
# Blockchain Explorer API (Primary - Requires Free API Key)
# ============================================================================

def get_explorer_api_key(chain: str) -> str:
    """Get explorer API key from environment or config."""
    config = CHAIN_CONFIGS.get(chain, CHAIN_CONFIGS["ethereum"])
    env_key = config.get("explorer_env_key", "ETHERSCAN_API_KEY")
    
    # Check environment variable
    api_key = os.environ.get(env_key) or os.environ.get("ETHERSCAN_API_KEY")
    if api_key:
        return api_key
    
    # Check config file
    cfg = get_config()
    return cfg.get("portfolio", {}).get("etherscan_api_key", "")


def get_balance_from_explorer(address: str, chain: str = "ethereum") -> float:
    """Get native balance using blockchain explorer API."""
    config = CHAIN_CONFIGS.get(chain, CHAIN_CONFIGS["ethereum"])
    api_key = get_explorer_api_key(chain)
    
    if not api_key:
        print(f"⚠️ 未配置 {chain} 链的区块链浏览器 API Key", file=sys.stderr)
        return 0
    
    # Etherscan V2 API format
    url = f"{config['explorer_api']}?chainid={config['chain_id']}&module=account&action=balance&address={address}&apikey={api_key}"
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Web3-Investor/0.3.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            if data.get("status") == "1":
                return int(data.get("result", "0")) / 1e18
            else:
                print(f"⚠️ Explorer API 返回错误: {data.get('message', 'Unknown')}", file=sys.stderr)
    except Exception as e:
        print(f"⚠️ Explorer API 请求失败: {e}", file=sys.stderr)
    return 0


def get_tokens_from_explorer(address: str, chain: str = "ethereum") -> list:
    """Get token list using blockchain explorer API."""
    config = CHAIN_CONFIGS.get(chain, CHAIN_CONFIGS["ethereum"])
    api_key = get_explorer_api_key(chain)
    
    if not api_key:
        return []
    
    url = f"{config['explorer_api']}?chainid={config['chain_id']}&module=account&action=tokenlist&address={address}&apikey={api_key}"
    
    tokens = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Web3-Investor/0.3.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            if data.get("status") == "1" and data.get("result"):
                for t in data["result"]:
                    try:
                        decimals = int(t.get("tokenDecimal", 18))
                        balance = int(t.get("value", "0")) / (10 ** decimals)
                        if balance > 0:
                            tokens.append({
                                "address": t.get("contractAddress", ""),
                                "symbol": t.get("tokenSymbol", "?"),
                                "name": t.get("tokenName", "?"),
                                "balance": balance,
                                "decimals": decimals
                            })
                    except (ValueError, TypeError):
                        continue
    except Exception as e:
        print(f"⚠️ Token list 请求失败: {e}", file=sys.stderr)
    return tokens


# ============================================================================
# RPC Fallback (Secondary)
# ============================================================================

def get_rpc_url(chain: str) -> str:
    """Get RPC URL with environment/config fallback."""
    env_var = f"WEB3_INVESTOR_{chain.upper()}_RPC_URL"
    rpc = os.environ.get(env_var) or os.environ.get("WEB3_INVESTOR_RPC_URL")
    if rpc:
        return rpc
    
    alchemy_key = os.environ.get("ALCHEMY_API_KEY")
    if alchemy_key:
        return CHAIN_CONFIGS[chain]["alchemy_template"].format(api_key=alchemy_key)
    
    return CHAIN_CONFIGS[chain]["rpcs"][0]


def get_balance_rpc(address: str, chain: str) -> float:
    """Get native balance via RPC (fallback)."""
    try:
        payload = {"jsonrpc": "2.0", "method": "eth_getBalance", "params": [address, "latest"], "id": 1}
        req = urllib.request.Request(get_rpc_url(chain), data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            return int(result.get("result", "0x0"), 16) / 1e18
    except Exception as e:
        print(f"⚠️ RPC error: {e}", file=sys.stderr)
    return 0


# ============================================================================
# Prices
# ============================================================================

def get_prices(tokens: list) -> dict:
    """Get prices from CoinGecko."""
    ids = {SYMBOL_TO_COINGECKO.get(t.get("symbol", "").upper()) for t in tokens}
    ids.discard(None)
    if not ids:
        return {}
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(ids)}&vs_currencies=usd"
        with urllib.request.urlopen(url, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"⚠️ Price error: {e}", file=sys.stderr)
    return {}


# ============================================================================
# Portfolio Builder
# ============================================================================

def build_portfolio(address: str, chain: str, native: float, tokens: list, source: str) -> dict:
    """Build portfolio response."""
    prices = get_prices(tokens)
    eth_price = prices.get("ethereum", {}).get("usd", 2000)
    
    total = native * eth_price
    for t in tokens:
        price_id = SYMBOL_TO_COINGECKO.get(t.get("symbol", "").upper())
        t["price_usd"] = prices.get(price_id, {}).get("usd", 0) if price_id else 0
        t["value_usd"] = t.get("balance", 0) * t.get("price_usd", 0)
        total += t["value_usd"]
    
    all_tokens = [{
        "address": "0x0000000000000000000000000000000000000000",
        "symbol": "ETH", "name": "Ethereum",
        "balance": native, "price_usd": eth_price, "value_usd": native * eth_price
    }] + [t for t in tokens if t.get("value_usd", 0) > 0.01]
    all_tokens.sort(key=lambda x: x.get("value_usd", 0), reverse=True)
    
    return {
        "address": address.lower(), "chain": chain,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total_value_usd": round(total, 2), "tokens": all_tokens,
        "defi_positions": [], "expiring_positions": [], "data_source": source
    }


def get_portfolio(address: str, chain: str = "ethereum") -> dict:
    """Get portfolio with automatic method selection (explorer first, then RPC)."""
    chain = chain.lower()
    
    # Try explorer API first
    print(f"🔍 查询 {chain} 链资产（使用区块链浏览器）...", file=sys.stderr)
    native = get_balance_from_explorer(address, chain)
    tokens = get_tokens_from_explorer(address, chain)
    
    if native > 0 or tokens:
        print(f"✅ 区块链浏览器查询成功！", file=sys.stderr)
        return build_portfolio(address, chain, native, tokens, "explorer")
    
    # Fallback to RPC
    print(f"⚠️ 浏览器无数据，使用 RPC 节点...", file=sys.stderr)
    native = get_balance_rpc(address, chain)
    return build_portfolio(address, chain, native, [], "rpc")


# ============================================================================
# Output Formatting
# ============================================================================

def format_report(portfolio: dict, fmt: str = "markdown") -> str:
    """Format portfolio as report."""
    if fmt == "json":
        return json.dumps(portfolio, indent=2, ensure_ascii=False)
    
    lines = [
        f"# 📊 投资组合报告",
        f"\n| 项目 | 值 |", f"|------|-----|",
        f"| 地址 | `{portfolio['address']}` |",
        f"| 链 | {portfolio['chain'].title()} |",
        f"| 总价值 | **${portfolio['total_value_usd']:,.2f}** |",
        f"| 数据源 | {portfolio['data_source']} |",
        f"\n---\n", "## 🪙 代币持仓\n",
        "| 代币 | 余额 | 价格 | 价值 |", "|------|------|------|------|"
    ]
    for t in portfolio.get("tokens", []):
        lines.append(f"| {t.get('symbol', '?')} | {t.get('balance', 0):.4f} | ${t.get('price_usd', 0):.2f} | ${t.get('value_usd', 0):,.2f} |")
    return "\n".join(lines)


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Portfolio indexer")
    parser.add_argument("--address", required=True, help="Wallet address")
    parser.add_argument("--chain", default="ethereum", choices=["ethereum", "base"])
    parser.add_argument("--output", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()
    
    portfolio = get_portfolio(args.address, args.chain)
    print(format_report(portfolio, args.output))


if __name__ == "__main__":
    main()