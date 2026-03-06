#!/usr/bin/env python3
"""
broadcast_signed_tx.py
直接广播已签名交易到链上（Broadcast Signed Transaction）

适用场景：交易已在客户端完成签名，只需广播，不需要私钥。

支持链：
  EVM 系：ETH(1) / BSC(56) / Base(8453) / Arbitrum(42161) / xLayer(196)

用法:
  python broadcast_signed_tx.py --chain 56 --address 0x... --signed-tx 0x...
  python broadcast_signed_tx.py --chain 1  --address 0x... --signed-tx 0x... --mev
  python broadcast_signed_tx.py --chain 56 --address 0x... --signed-tx 0x... --json-only

环境变量:
  OKX_ACCESS_KEY   - OKX Web3 API Key
  OKX_SECRET_KEY   - OKX Secret Key
  OKX_PASSPHRASE   - OKX Passphrase
"""

import argparse
import base64
import hashlib
import hmac
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

try:
    import requests
except ImportError:
    print("[ERROR] 缺少依赖: requests，请执行 pip install requests", file=sys.stderr)
    sys.exit(1)


# ──────────────────────────────────────────────────────────────
# 链配置（仅用于输出链名和区块浏览器链接，不影响广播逻辑）
# 新增链只需在此处追加，无需修改其他代码
# ──────────────────────────────────────────────────────────────

@dataclass
class ChainInfo:
    name:     str
    explorer: str   # tx hash 前缀，拼接 hash 即得完整链接


CHAIN_INFO: dict[str, ChainInfo] = {
    "1":     ChainInfo("Ethereum",  "https://etherscan.io/tx/"),
    "56":    ChainInfo("BSC",       "https://bscscan.com/tx/"),
    "8453":  ChainInfo("Base",      "https://basescan.org/tx/"),
    "42161": ChainInfo("Arbitrum",  "https://arbiscan.io/tx/"),
    "196":   ChainInfo("xLayer",    "https://www.oklink.com/xlayer/tx/"),
    "501":   ChainInfo("Solana",    "https://solscan.io/tx/"),
}

# OKX 广播接口
OKX_BASE_URL   = "https://web3.okx.com"
BROADCAST_PATH = "/api/v6/dex/pre-transaction/broadcast-transaction"

# 请求超时（秒）
REQUEST_TIMEOUT = 30


# ──────────────────────────────────────────────────────────────
# OKX API 鉴权
# ──────────────────────────────────────────────────────────────

def _okx_sign(secret_key: str, timestamp: str, method: str,
              path: str, body: str = "") -> str:
    prehash = timestamp + method + path + body
    mac = hmac.new(
        secret_key.encode("utf-8"),
        prehash.encode("utf-8"),
        hashlib.sha256,
    )
    return base64.b64encode(mac.digest()).decode("ascii")


def _okx_headers(api_key: str, secret_key: str, passphrase: str,
                 method: str, path: str, body: str = "") -> dict:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    sign = _okx_sign(secret_key, timestamp, method, path, body)
    return {
        "OK-ACCESS-KEY":        api_key,
        "OK-ACCESS-SIGN":       sign,
        "OK-ACCESS-PASSPHRASE": passphrase,
        "OK-ACCESS-TIMESTAMP":  timestamp,
        "Content-Type":         "application/json",
    }


# ──────────────────────────────────────────────────────────────
# 参数校验
# ──────────────────────────────────────────────────────────────

# 非 EVM 链：address 和 signedTx 不以 0x 开头（如 SOL 使用 base58 编码）
_NON_EVM_CHAINS = {"501"}


def _validate(chain_index: str, address: str, signed_tx: str) -> None:
    if not chain_index.strip():
        raise ValueError("chain_index 不能为空，示例：56（BSC）/ 1（ETH）/ 501（Solana）")
    if not address:
        raise ValueError("address 不能为空")
    if not signed_tx:
        raise ValueError("signed_tx 不能为空")

    if chain_index not in _NON_EVM_CHAINS:
        # EVM 链：address 和 signedTx 必须以 0x 开头
        if not address.startswith("0x"):
            raise ValueError("address 格式错误：EVM 链地址必须以 0x 开头")
        if not signed_tx.startswith("0x"):
            raise ValueError("signed_tx 格式错误：EVM 链签名交易必须以 0x 开头")


# ──────────────────────────────────────────────────────────────
# 核心广播函数
# ──────────────────────────────────────────────────────────────

def broadcast_signed_transaction(
    chain_index: str,
    address: str,
    signed_tx: str,
    enable_mev_protection: bool = False,
    api_key: Optional[str] = None,
    secret_key: Optional[str] = None,
    passphrase: Optional[str] = None,
    timeout: int = REQUEST_TIMEOUT,
) -> dict:
    """
    广播已签名交易到链上。

    Args:
        chain_index:           链 ID（字符串），如 "56"（BSC）、"1"（ETH）
        address:               发送方地址
        signed_tx:             已签名的交易（EVM 链为 0x 开头的 hex）
        enable_mev_protection: 是否开启 MEV 保护（默认 False）
        api_key / secret_key / passphrase: OKX API 凭证（优先使用参数，其次读环境变量）
        timeout:               HTTP 请求超时秒数

    Returns:
        dict，包含：
            success (bool)
            order_id (str)
            tx_hash (str)
            chain_index (str)
            chain_name (str)
            explorer_url (str | None)
            error (str | None)  - 失败时的原因
    """
    # 从环境变量填充凭证（参数优先）
    api_key    = api_key    or os.environ.get("OKX_ACCESS_KEY", "")
    secret_key = secret_key or os.environ.get("OKX_SECRET_KEY", "")
    passphrase = passphrase or os.environ.get("OKX_PASSPHRASE", "")

    if not all([api_key, secret_key, passphrase]):
        return _fail(
            chain_index, address, signed_tx,
            "缺少 OKX API 凭证，请设置环境变量：\n"
            "  OKX_ACCESS_KEY / OKX_SECRET_KEY / OKX_PASSPHRASE\n"
            "（必须使用 OKX Web3 API Key，普通交易 Key 会返回 401）"
        )

    # 参数校验
    try:
        _validate(chain_index, address, signed_tx)
    except ValueError as e:
        return _fail(chain_index, address, signed_tx, str(e))

    # 构造请求体
    body_dict: dict = {
        "chainIndex": chain_index,
        "address":    address,
        "signedTx":   signed_tx,
    }
    if enable_mev_protection:
        body_dict["extraData"] = json.dumps({"enableMevProtection": True})

    body_str = json.dumps(body_dict, separators=(",", ":"), ensure_ascii=False)
    headers  = _okx_headers(api_key, secret_key, passphrase,
                            "POST", BROADCAST_PATH, body_str)

    # 发起请求
    try:
        resp = requests.post(
            OKX_BASE_URL + BROADCAST_PATH,
            headers=headers,
            data=body_str.encode("utf-8"),
            timeout=timeout,
        )
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return _fail(chain_index, address, signed_tx,
                     f"HTTP 错误 {resp.status_code}: {resp.text[:300]}")
    except requests.exceptions.RequestException as e:
        return _fail(chain_index, address, signed_tx, f"网络请求异常: {e}")

    # 解析响应
    try:
        data = resp.json()
    except ValueError:
        return _fail(chain_index, address, signed_tx,
                     f"响应解析失败，原始内容: {resp.text[:300]}")

    if data.get("code") != "0":
        return _fail(chain_index, address, signed_tx,
                     f"广播失败（code={data.get('code')}）: {data.get('msg', '')}")

    items = data.get("data") or []
    if not items:
        return _fail(chain_index, address, signed_tx, "广播 API 返回空 data")

    item       = items[0]
    order_id   = item.get("orderId", "")
    tx_hash    = item.get("txHash", "")
    chain_info = CHAIN_INFO.get(chain_index)

    return {
        "success":      True,
        "order_id":     order_id,
        "tx_hash":      tx_hash,
        "chain_index":  chain_index,
        "chain_name":   chain_info.name if chain_info else f"Chain-{chain_index}",
        "explorer_url": (chain_info.explorer + tx_hash) if (chain_info and tx_hash) else None,
        "mev_enabled":  enable_mev_protection,
        "error":        None,
    }


def _fail(chain_index: str, address: str, signed_tx: str, error: str) -> dict:
    chain_info = CHAIN_INFO.get(chain_index)
    return {
        "success":      False,
        "order_id":     "",
        "tx_hash":      "",
        "chain_index":  chain_index,
        "chain_name":   chain_info.name if chain_info else f"Chain-{chain_index}",
        "explorer_url": None,
        "mev_enabled":  False,
        "error":        error,
    }


# ──────────────────────────────────────────────────────────────
# 输出格式化
# ──────────────────────────────────────────────────────────────

def print_result(result: dict, json_only: bool = False) -> None:
    if json_only:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    sep = "=" * 62
    if result["success"]:
        print(f"\n{sep}")
        print(f"  ✅ {result['chain_name']} 广播成功")
        print(sep)
        print(f"  Order ID  : {result['order_id']}")
        print(f"  Tx Hash   : {result['tx_hash']}")
        if result["explorer_url"]:
            print(f"  浏览器    : {result['explorer_url']}")
        if result["mev_enabled"]:
            print(f"  MEV 保护  : ✅ 已开启")
        print(f"{sep}\n")
    else:
        print(f"\n{sep}")
        print(f"  ❌ 广播失败（Chain-{result['chain_index']}）")
        print(sep)
        print(f"  错误原因  : {result['error']}")
        print(f"{sep}\n")

    # 同时输出机器可读 JSON，供 AI 解析
    print(json.dumps(result, ensure_ascii=False, indent=2))


# ──────────────────────────────────────────────────────────────
# CLI 入口
# ──────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="直接广播已签名交易到链上（无需私钥）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # BSC 广播
  python broadcast_signed_tx.py --chain 56 --address 0x... --signed-tx 0x...

  # ETH 开启 MEV 保护
  python broadcast_signed_tx.py --chain 1 --address 0x... --signed-tx 0x... --mev

  # 仅输出 JSON（适合 AI 解析）
  python broadcast_signed_tx.py --chain 56 --address 0x... --signed-tx 0x... --json-only

支持的链（完整列表见 CHAIN_INFO）:
  1=ETH  56=BSC  8453=Base  42161=Arbitrum  196=xLayer  501=Solana  其他链直接传 chainIndex 即可
        """
    )
    parser.add_argument("--chain",      required=True,
                        help="链 ID，如 56（BSC）/ 1（ETH）/ 8453（Base）")
    parser.add_argument("--address",    required=True,
                        help="发送方钱包地址")
    parser.add_argument("--signed-tx",  required=True, dest="signed_tx",
                        help="已签名的交易（EVM 链为 0x 开头的 hex）")
    parser.add_argument("--mev",        action="store_true",
                        help="开启 MEV 保护（防三明治攻击）")
    parser.add_argument("--json-only",  action="store_true",
                        help="仅输出 JSON，适合被 AI 解析")
    parser.add_argument("--api-key",    default="",
                        help="OKX API Key（默认读 OKX_ACCESS_KEY 环境变量）")
    parser.add_argument("--secret-key", default="", dest="secret_key",
                        help="OKX Secret Key（默认读 OKX_SECRET_KEY 环境变量）")
    parser.add_argument("--passphrase", default="",
                        help="OKX Passphrase（默认读 OKX_PASSPHRASE 环境变量）")

    args = parser.parse_args()

    result = broadcast_signed_transaction(
        chain_index           = args.chain,
        address               = args.address,
        signed_tx             = args.signed_tx,
        enable_mev_protection = args.mev,
        api_key               = args.api_key or None,
        secret_key            = args.secret_key or None,
        passphrase            = args.passphrase or None,
    )

    print_result(result, json_only=args.json_only)

    if not result["success"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
