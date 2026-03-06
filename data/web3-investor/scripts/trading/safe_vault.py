#!/usr/bin/env python3
"""
Safe Vault - Secure transaction signing and execution (v0.2.0)

Features:
- Balance pre-check before transaction preparation
- Deposit preview for Aave/Compound/Lido
- Whitelist and limit protection
- Local signing capability

Usage:
    python safe_vault.py --check-balance --address 0x... --chain ethereum
    python safe_vault.py --preview-deposit --protocol aave --asset USDC --amount 1000
    python safe_vault.py --prepare-tx --to 0x... --value 0 --data 0x...
"""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
import urllib.request
import urllib.error

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "..", "..", "config", "config.json")
WHITELIST_PATH = os.path.join(SCRIPT_DIR, "..", "..", "config", "whitelist.json")
PROTOCOLS_PATH = os.path.join(SCRIPT_DIR, "..", "..", "config", "protocols.json")

# Chain configurations
CHAIN_CONFIGS = {
    "ethereum": {
        "chain_id": 1,
        "rpcs": ["https://cloudflare-eth.com", "https://mainnet.gateway.fm"],
        "explorer_api": "https://api.etherscan.io/v2/api",
        "explorer_env_key": "ETHERSCAN_API_KEY",
        "native_token": "ETH"
    },
    "base": {
        "chain_id": 8453,
        "rpcs": ["https://mainnet.base.org"],
        "explorer_api": "https://api.basescan.org/api",
        "explorer_env_key": "BASESCAN_API_KEY",
        "native_token": "ETH"
    }
}

# Known token addresses (Ethereum mainnet)
KNOWN_TOKENS = {
    "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    "DAI": "0x6B175474E89094C44Da98b954EesdeeAC495271d0F",
    "WETH": "0xC02aaA39b223FE8D0A0e5C4F27ead9083C756Cc2",
    "stETH": "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84",
    "rETH": "0xae78736Cd615f374D3085123A210448E74Fc6393",
}

# Protocol contract addresses (Ethereum mainnet)
PROTOCOL_CONTRACTS = {
    "aave": {
        "pool": "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2",
        "pool_proxy": "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"
    },
    "compound": {
        "comet": "0xc3d688B66703497DAA19211EEdff47f25384cdc3"
    },
    "lido": {
        "steth": "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84"
    }
}

# Error messages
ERROR_MESSAGES = {
    "NO_PRIVATE_KEY": "❌ 无法签名交易：未配置私钥。请设置 WEB3_INVESTOR_PRIVATE_KEY 环境变量。",
    "WHITELIST_BLOCKED": "⛔ 交易被拒绝：目标地址不在白名单中。",
    "EXCEEDS_LIMIT": "⚠️ 交易金额超过限额。当前限额为 ${limit} USD。",
    "SIMULATION_FAILED": "🔴 交易模拟失败：{reason}",
    "RPC_ERROR": "📡 无法连接到区块链网络：{error}",
    "INSUFFICIENT_BALANCE": "💰 余额不足：需要 {need} {token}，实际余额 {balance}。",
    "INVALID_ADDRESS": "📛 无效的地址格式：{address}",
    "SIGNING_UNAVAILABLE": "🔐 本地签名功能不可用。请安装 eth-account。",
    "UNKNOWN_PROTOCOL": "❓ 未知的协议：{protocol}。支持的协议：aave, compound, lido",
    "UNKNOWN_TOKEN": "❓ 未知的代币：{token}。已知代币：USDC, USDT, DAI, WETH, stETH, rETH",
}


# ============================================================================
# Utility Functions
# ============================================================================

def load_config() -> dict:
    """Load configuration."""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {"trading": {"mode": "simulation", "whitelist_enabled": True, "default_limit_usd": 100}}


def load_whitelist() -> dict:
    """Load whitelist."""
    if os.path.exists(WHITELIST_PATH):
        with open(WHITELIST_PATH) as f:
            return json.load(f)
    return {"addresses": [], "enabled": True}


def load_protocols() -> dict:
    """Load protocol registry."""
    if os.path.exists(PROTOCOLS_PATH):
        with open(PROTOCOLS_PATH) as f:
            return json.load(f)
    return {"protocols": {}}


def get_rpc_url(chain: str) -> str:
    """Get RPC URL for chain."""
    env_var = f"WEB3_INVESTOR_{chain.upper()}_RPC_URL"
    rpc = os.environ.get(env_var) or os.environ.get("WEB3_INVESTOR_RPC_URL")
    if rpc:
        return rpc
    
    alchemy_key = os.environ.get("ALCHEMY_API_KEY")
    if alchemy_key:
        return f"https://eth-mainnet.g.alchemy.com/v2/{alchemy_key}"
    
    return CHAIN_CONFIGS.get(chain, CHAIN_CONFIGS["ethereum"])["rpcs"][0]


def get_chain_id(chain: str) -> int:
    """Get chain ID for chain name."""
    return CHAIN_CONFIGS.get(chain, CHAIN_CONFIGS["ethereum"])["chain_id"]


# ============================================================================
# Balance Pre-Check
# ============================================================================

def get_native_balance(address: str, chain: str = "ethereum") -> float:
    """
    Get native token balance (ETH) for an address.
    
    Returns balance in ETH (not wei).
    """
    rpc_url = get_rpc_url(chain)
    
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [address, "latest"],
        "id": 1
    }
    
    try:
        req = urllib.request.Request(
            rpc_url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            balance_wei = int(result.get("result", "0x0"), 16)
            return balance_wei / 1e18
    except Exception as e:
        print(f"⚠️ 无法获取余额: {e}", file=sys.stderr)
        return 0


def get_erc20_balance(wallet: str, token: str, chain: str = "ethereum") -> float:
    """
    Get ERC20 token balance for an address.
    
    Args:
        wallet: Wallet address
        token: Token symbol or address
        chain: Blockchain name
    
    Returns:
        Balance as float (normalized by decimals)
    """
    # Resolve token address
    if token.upper() in KNOWN_TOKENS:
        token_address = KNOWN_TOKENS[token.upper()]
    elif token.startswith("0x"):
        token_address = token
    else:
        return 0
    
    rpc_url = get_rpc_url(chain)
    
    # ERC20 balanceOf(address) call
    # selector: 0x70a08231 + padded address
    data = "0x70a08231" + wallet[2:].lower().zfill(64)
    
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_call",
        "params": [{"to": token_address, "data": data}, "latest"],
        "id": 1
    }
    
    try:
        req = urllib.request.Request(
            rpc_url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            balance_raw = int(result.get("result", "0x0"), 16)
            # Assume 18 decimals for most tokens, 6 for USDC/USDT
            decimals = 6 if token.upper() in ["USDC", "USDT"] else 18
            return balance_raw / (10 ** decimals)
    except Exception as e:
        print(f"⚠️ 无法获取代币余额: {e}", file=sys.stderr)
        return 0


def check_balance_before_deposit(
    wallet: str,
    token: str,
    amount: float,
    chain: str = "ethereum"
) -> Dict[str, Any]:
    """
    Check if wallet has sufficient balance for deposit.
    
    Returns:
        dict with sufficient (bool), balance, needed, message
    """
    result = {
        "sufficient": False,
        "token": token,
        "chain": chain,
        "needed": amount,
        "balance": 0,
        "message": ""
    }
    
    # Check native token (ETH)
    if token.upper() in ["ETH", "WETH"]:
        balance = get_native_balance(wallet, chain)
        result["balance"] = balance
        
        if balance >= amount:
            result["sufficient"] = True
            result["message"] = f"✅ 余额充足：{balance:.4f} ETH >= {amount} ETH"
        else:
            result["message"] = ERROR_MESSAGES["INSUFFICIENT_BALANCE"].format(
                need=amount, token="ETH", balance=balance
            )
        return result
    
    # Check ERC20 token
    balance = get_erc20_balance(wallet, token, chain)
    result["balance"] = balance
    
    if balance >= amount:
        result["sufficient"] = True
        result["message"] = f"✅ 余额充足：{balance:.4f} {token} >= {amount} {token}"
    else:
        result["message"] = ERROR_MESSAGES["INSUFFICIENT_BALANCE"].format(
            need=amount, token=token, balance=balance
        )
    
    return result


# ============================================================================
# Deposit Preview (Calldata Generation)
# ============================================================================

def encode_uint256(value: int) -> str:
    """Encode uint256 for calldata."""
    return hex(value)[2:].zfill(64)


def encode_address(address: str) -> str:
    """Encode address for calldata."""
    return address[2:].lower().zfill(64)


def generate_aave_deposit_calldata(
    asset: str,
    amount: float,
    on_behalf_of: str = None,
    referral_code: int = 0
) -> Dict[str, Any]:
    """
    Generate calldata for Aave V3 supply (deposit).
    
    Function: supply(address asset, uint256 amount, address onBehalfOf, uint16 referralCode)
    Selector: 0x617ba037
    """
    # Resolve asset address
    if asset.upper() in KNOWN_TOKENS:
        asset_address = KNOWN_TOKENS[asset.upper()]
    elif asset.startswith("0x"):
        asset_address = asset
    else:
        return {"error": ERROR_MESSAGES["UNKNOWN_TOKEN"].format(token=asset)}
    
    # Convert amount to wei (assume 18 decimals, 6 for stablecoins)
    decimals = 6 if asset.upper() in ["USDC", "USDT"] else 18
    amount_wei = int(amount * (10 ** decimals))
    
    # onBehalfOf defaults to caller (we'll use a placeholder)
    on_behalf = on_behalf_of or "0x0000000000000000000000000000000000000001"
    
    # Build calldata
    selector = "617ba037"  # supply(address,uint256,address,uint16)
    calldata = "0x" + selector + \
               encode_address(asset_address) + \
               encode_uint256(amount_wei) + \
               encode_address(on_behalf) + \
               encode_uint256(referral_code)
    
    return {
        "protocol": "aave",
        "method": "supply",
        "to": PROTOCOL_CONTRACTS["aave"]["pool"],
        "asset": asset_address,
        "amount": amount,
        "amount_wei": amount_wei,
        "calldata": calldata,
        "description": f"Deposit {amount} {asset} to Aave V3"
    }


def generate_compound_deposit_calldata(
    asset: str,
    amount: float
) -> Dict[str, Any]:
    """
    Generate calldata for Compound V3 supply (deposit).
    
    Function: supply(address asset, uint256 amount)
    Selector: 0xd0e30db0 (for deposit)
    Note: Compound V3 uses different pattern
    """
    # Compound V3 Comet uses: supply(address asset, uint256 amount)
    if asset.upper() in KNOWN_TOKENS:
        asset_address = KNOWN_TOKENS[asset.upper()]
    elif asset.startswith("0x"):
        asset_address = asset
    else:
        return {"error": ERROR_MESSAGES["UNKNOWN_TOKEN"].format(token=asset)}
    
    decimals = 6 if asset.upper() in ["USDC", "USDT"] else 18
    amount_wei = int(amount * (10 ** decimals))
    
    # Compound V3 supply selector
    selector = "0xe8eda9df"  # supply(address,uint256)
    calldata = "0x" + selector + \
               encode_address(asset_address) + \
               encode_uint256(amount_wei)
    
    return {
        "protocol": "compound",
        "method": "supply",
        "to": PROTOCOL_CONTRACTS["compound"]["comet"],
        "asset": asset_address,
        "amount": amount,
        "amount_wei": amount_wei,
        "calldata": calldata,
        "description": f"Deposit {amount} {asset} to Compound V3"
    }


def generate_lido_deposit_calldata(
    amount: float
) -> Dict[str, Any]:
    """
    Generate calldata for Lido stETH deposit.
    
    Function: submit(address _referral) - sends ETH and receives stETH
    Selector: 0x386497fd
    """
    amount_wei = int(amount * 1e18)
    
    # Lido submit selector with empty referral
    selector = "386497fd"  # submit(address)
    calldata = "0x" + selector + encode_address("0x0000000000000000000000000000000000000000")
    
    return {
        "protocol": "lido",
        "method": "submit",
        "to": PROTOCOL_CONTRACTS["lido"]["steth"],
        "asset": "ETH",
        "amount": amount,
        "amount_wei": amount_wei,
        "calldata": calldata,
        "value_wei": amount_wei,  # Need to send ETH
        "description": f"Stake {amount} ETH with Lido to receive stETH"
    }


def preview_deposit(
    protocol: str,
    asset: str,
    amount: float,
    wallet: str = None,
    chain: str = "ethereum"
) -> Dict[str, Any]:
    """
    Generate deposit preview with calldata and balance check.
    
    Args:
        protocol: Protocol name (aave, compound, lido)
        asset: Asset symbol or address
        amount: Amount to deposit
        wallet: Wallet address for balance check
        chain: Blockchain name
    
    Returns:
        dict with calldata, balance check, and execution preview
    """
    protocol_lower = protocol.lower()
    
    # Generate calldata based on protocol
    if protocol_lower == "aave":
        calldata_result = generate_aave_deposit_calldata(asset, amount)
    elif protocol_lower == "compound":
        calldata_result = generate_compound_deposit_calldata(asset, amount)
    elif protocol_lower == "lido":
        calldata_result = generate_lido_deposit_calldata(amount)
    else:
        return {
            "error": ERROR_MESSAGES["UNKNOWN_PROTOCOL"].format(protocol=protocol),
            "supported_protocols": ["aave", "compound", "lido"]
        }
    
    if "error" in calldata_result:
        return calldata_result
    
    result = {
        "protocol": protocol_lower,
        "asset": asset,
        "amount": amount,
        "chain": chain,
        "calldata": calldata_result,
        "preview": {
            "to": calldata_result["to"],
            "value": calldata_result.get("value_wei", 0),
            "data": calldata_result["calldata"],
            "gas_estimate": 250000  # Estimated gas for deposit
        }
    }
    
    # Balance check if wallet provided
    if wallet:
        balance_check = check_balance_before_deposit(
            wallet=wallet,
            token=asset,
            amount=amount,
            chain=chain
        )
        result["balance_check"] = balance_check
        
        if not balance_check["sufficient"]:
            result["can_execute"] = False
            result["warning"] = balance_check["message"]
        else:
            result["can_execute"] = True
    else:
        result["balance_check"] = {"checked": False, "message": "Wallet not provided"}
        result["can_execute"] = None  # Unknown
    
    return result


# ============================================================================
# Whitelist & Security
# ============================================================================

def check_whitelist(address: str, amount_usd: float = 0) -> dict:
    """Check if address is in whitelist and within limits."""
    config = load_config()
    whitelist = load_whitelist()
    
    if not config["trading"].get("whitelist_enabled", True):
        return {"allowed": True, "reason": "Whitelist disabled", "limit": float("inf")}
    
    if not whitelist.get("enabled", True):
        return {"allowed": True, "reason": "Whitelist disabled", "limit": float("inf")}
    
    address_lower = address.lower()
    
    for entry in whitelist.get("addresses", []):
        if entry.get("address", "").lower() == address_lower:
            limit = entry.get("max_amount_usd", config["trading"].get("default_limit_usd", 100))
            if amount_usd <= limit:
                return {"allowed": True, "reason": f"Within limit", "limit": limit}
            else:
                return {"allowed": False, "reason": f"Exceeds limit", "limit": limit}
    
    return {"allowed": False, "reason": "Address not in whitelist", "limit": 0}


def get_eth_price_usd() -> float:
    """Get current ETH price from CoinGecko."""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data["ethereum"]["usd"]
    except:
        return 2000


# ============================================================================
# Transaction Preparation
# ============================================================================

def prepare_transaction(
    to: str,
    value: str = "0",
    data: str = "0x",
    gas_limit: int = 300000,
    description: str = "",
    chain: str = "ethereum"
) -> dict:
    """Prepare a transaction for signing."""
    config = load_config()
    mode = config["trading"].get("mode", "simulation")
    
    # Estimate value in USD
    try:
        value_eth = float(value) / 1e18
        value_usd = value_eth * get_eth_price_usd()
    except:
        value_usd = 0
    
    # Check whitelist
    whitelist_result = check_whitelist(to, value_usd)
    
    # Generate request
    request_id = str(uuid.uuid4())
    request = {
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "mode": mode,
        "chain": chain,
        "chain_id": get_chain_id(chain),
        "transaction": {
            "to": to,
            "value": value,
            "data": data,
            "gas_limit": gas_limit,
            "chain_id": get_chain_id(chain),
        },
        "value_usd": round(value_usd, 2),
        "whitelist": whitelist_result,
        "description": description,
        "approval_required": mode == "simulation" or not whitelist_result["allowed"]
    }
    
    return request


# ============================================================================
# CLI
# ============================================================================

def format_preview_output(result: Dict) -> str:
    """Format deposit preview for display."""
    if "error" in result:
        return f"❌ 错误: {result['error']}"
    
    lines = [
        f"# 📋 存款预览 - {result['protocol'].upper()}",
        "",
        f"| 项目 | 值 |",
        f"|------|-----|",
        f"| 协议 | {result['protocol']} |",
        f"| 资产 | {result['asset']} |",
        f"| 金额 | {result['amount']} |",
        f"| 链 | {result['chain']} |",
        "",
        "## 交易数据",
        f"- **To**: `{result['preview']['to']}`",
        f"- **Value**: {result['preview']['value']} wei",
        f"- **Data**: `{result['preview']['data'][:60]}...`",
        f"- **Gas Estimate**: {result['preview']['gas_estimate']:,}",
    ]
    
    if result.get("balance_check"):
        bc = result["balance_check"]
        lines.extend([
            "",
            "## 余额检查",
            f"- **余额**: {bc.get('balance', 'N/A')} {bc.get('token', '')}",
            f"- **状态**: {bc.get('message', 'N/A')}",
        ])
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Safe Vault - Secure transaction manager (v0.2.0)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Check balance
    balance_parser = subparsers.add_parser("balance", help="Check wallet balance")
    balance_parser.add_argument("--wallet", "-w", required=True, help="Wallet address")
    balance_parser.add_argument("--token", "-t", default="ETH", help="Token symbol or address")
    balance_parser.add_argument("--chain", "-c", default="ethereum", help="Blockchain")
    balance_parser.add_argument("--json", action="store_true", help="JSON output")
    
    # Preview deposit
    preview_parser = subparsers.add_parser("preview-deposit", help="Preview deposit transaction")
    preview_parser.add_argument("--protocol", "-p", required=True, 
                                choices=["aave", "compound", "lido"],
                                help="Protocol name")
    preview_parser.add_argument("--asset", "-a", required=True, help="Asset symbol")
    preview_parser.add_argument("--amount", "-m", type=float, required=True, help="Amount to deposit")
    preview_parser.add_argument("--wallet", "-w", help="Wallet for balance check")
    preview_parser.add_argument("--chain", "-c", default="ethereum", help="Blockchain")
    preview_parser.add_argument("--json", action="store_true", help="JSON output")
    
    # Prepare transaction
    tx_parser = subparsers.add_parser("prepare-tx", help="Prepare transaction")
    tx_parser.add_argument("--to", required=True, help="Target address")
    tx_parser.add_argument("--value", default="0", help="Value in wei")
    tx_parser.add_argument("--data", default="0x", help="Calldata")
    tx_parser.add_argument("--chain", default="ethereum", help="Blockchain")
    tx_parser.add_argument("--json", action="store_true", help="JSON output")
    
    # Check signing capability
    subparsers.add_parser("check-signing", help="Check local signing capability")
    
    args = parser.parse_args()
    
    if args.command == "balance":
        result = check_balance_before_deposit(
            wallet=args.wallet,
            token=args.token,
            amount=0,  # Just checking balance
            chain=args.chain
        )
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"💰 {args.token} 余额: {result['balance']:.6f}")
    
    elif args.command == "preview-deposit":
        result = preview_deposit(
            protocol=args.protocol,
            asset=args.asset,
            amount=args.amount,
            wallet=args.wallet,
            chain=args.chain
        )
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(format_preview_output(result))
    
    elif args.command == "prepare-tx":
        result = prepare_transaction(
            to=args.to,
            value=args.value,
            data=args.data,
            chain=args.chain
        )
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"✅ 交易已准备")
            print(f"   To: {result['transaction']['to']}")
            print(f"   Value: {result['transaction']['value']} wei (${result['value_usd']})")
    
    elif args.command == "check-signing":
        try:
            from eth_account import Account
            pk = os.environ.get("WEB3_INVESTOR_PRIVATE_KEY")
            print("✅ eth-account 已安装")
            print(f"   私钥配置: {'✅ 是' if pk else '❌ 否'}")
        except ImportError:
            print("❌ eth-account 未安装")
            print("   运行: pip install eth-account")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()