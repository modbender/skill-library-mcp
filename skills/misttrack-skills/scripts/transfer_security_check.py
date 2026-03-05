#!/usr/bin/env python3
"""
transfer_security_check.py — 转账地址 AML 安全检测（MistTrack 集成）

将 MistTrack 风险评分集成到以下技能的转账流程中：
  - bitget-wallet-skill   (转账 / Swap 前检测收款方地址)
  - Trust Wallet wallet-core  (构建含 toAddress 签名交易前检测)
  - Trust Wallet trust-web3-provider (处理 eth_sendTransaction / ton_sendTransaction 前检测)

用法：
  python3 scripts/transfer_security_check.py --address <address> --chain <chain_code>
  python3 scripts/transfer_security_check.py --address <address> --chain eth --json

支持的 chain 代码：
  # bitget-wallet-skill 格式：
  eth, sol, bnb, trx, base, arbitrum, optimism, matic, ton, suinet, avax, zksync, ltc, doge, bch
  # Trust Wallet wallet-core CoinType 格式（别名）：
  bitcoin, btc, solana, tron, polygon, smartchain, bsc, tonchain

不支持的链（MistTrack 未收录，返回 exit 3）：
  aptos, cosmos, atom

Exit codes：
  0  ALLOW  — 低风险，可以继续转账
  1  WARN   — 中/高风险，需用户二次确认
  2  BLOCK  — 严重风险，建议拒绝转账
  3  ERROR  — API 不可用、参数错误或链不支持

环境变量：
  MISTTRACK_API_KEY  — MistTrack API 密鑰（优先于 --api-key 参数）

示例：
  export MISTTRACK_API_KEY=your_key
  # Bitget Wallet 流程
  python3 scripts/transfer_security_check.py --address 0x... --chain eth
  # Trust Wallet wallet-core 流程
  python3 scripts/transfer_security_check.py --address 1A... --chain bitcoin
  python3 scripts/transfer_security_check.py --address 0x... --chain polygon --json
"""

import argparse
import json
import os
import sys
import time
from typing import Optional

import requests

# ─── Constants ───────────────────────────────────────────────────────────────

BASE_URL = "https://openapi.misttrack.io"
REQUEST_TIMEOUT = 30  # seconds

# Map chain identifiers → MistTrack coin parameter
# Covers both bitget-wallet-skill chain codes and Trust Wallet wallet-core CoinType names
CHAIN_TO_COIN: dict[str, str] = {
    # ── bitget-wallet-skill chain codes ─────────────────────────────────────
    "eth": "ETH",
    "sol": "SOL",
    "bnb": "BNB",
    "trx": "TRX",
    "base": "ETH-Base",
    "arbitrum": "ETH-Arbitrum",
    "optimism": "ETH-Optimism",
    "matic": "POL-Polygon",
    "ton": "TON",
    "suinet": "SUI",
    "avax": "AVAX-Avalanche",
    "zksync": "ETH-zkSync",
    "ltc": "LTC",
    "doge": "DOGE",
    "bch": "BCH",
    # ── Trust Wallet wallet-core CoinType aliases ────────────────────────────
    "bitcoin": "BTC",           # CoinType.bitcoin
    "btc": "BTC",               # short alias
    "solana": "SOL",            # CoinType.solana (alias for sol)
    "tron": "TRX",              # CoinType.tron (alias for trx)
    "polygon": "POL-Polygon",   # CoinType.polygon (alias for matic)
    "smartchain": "BNB",        # CoinType.smartChain
    "bsc": "BNB",               # common BSC abbreviation
    "tonchain": "TON",          # alias distinguishing from bitget's 'ton'
}

# Chains that are not yet supported by MistTrack — exit cleanly with an explanation
UNSUPPORTED_CHAINS: dict[str, str] = {
    "aptos": "MistTrack 暂不支持 Aptos (APT) 链地址查询。请人工核实收款方身份。",
    "cosmos": "MistTrack 暂不支持 Cosmos Hub (ATOM) 原生代币地址查询。请人工核实收款方身份。",
    "atom": "MistTrack 暂不支持 Cosmos Hub (ATOM) 原生代币地址查询。请人工核实收款方身份。",
}

# Risk level → decision mapping
RISK_DECISION: dict[str, str] = {
    "Low": "ALLOW",
    "Moderate": "WARN",
    "High": "WARN",
    "Severe": "BLOCK",
}

# Exit codes
EXIT_ALLOW = 0
EXIT_WARN = 1
EXIT_BLOCK = 2
EXIT_ERROR = 3

# ANSI colours (disabled when JSON mode is active)
COLOUR = {
    "green": "\033[32m",
    "yellow": "\033[33m",
    "orange": "\033[91m",
    "red": "\033[31m",
    "bold": "\033[1m",
    "reset": "\033[0m",
}

RISK_COLOUR = {
    "Low": COLOUR["green"],
    "Moderate": COLOUR["yellow"],
    "High": COLOUR["orange"],
    "Severe": COLOUR["red"],
}

# ─── API helpers ─────────────────────────────────────────────────────────────


def _get(endpoint: str, params: dict) -> dict:
    """Perform a GET request to MistTrack API, raising on HTTP errors."""
    url = f"{BASE_URL}/{endpoint}"
    resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def get_risk_score(coin: str, address: str, api_key: str) -> dict:
    """
    Call v2/risk_score (synchronous) for the given address.
    Returns the full API response dict.
    """
    return _get(
        "v2/risk_score",
        {"coin": coin, "address": address, "api_key": api_key},
    )


def get_address_labels(coin: str, address: str, api_key: str) -> dict:
    """
    Call v1/address_labels for the given address.
    Returns the full API response dict.
    """
    return _get(
        "v1/address_labels",
        {"coin": coin, "address": address, "api_key": api_key},
    )


# ─── Decision logic ──────────────────────────────────────────────────────────


def decide(
    score: int,
    risk_level: str,
    label_type: str,
    label_list: list,
) -> str:
    """
    Determine ALLOW / WARN / BLOCK based on risk score and address labels.

    Special case: known exchange deposit addresses (label_type == "exchange")
    with Low or Moderate risk are treated as ALLOW — users commonly send funds
    to Binance / Coinbase / OKX deposit addresses which may have moderate scores
    due to aggregated exchange activity, not personal risk.
    """
    decision = RISK_DECISION.get(risk_level, "WARN")

    # Whitelist: verified exchange addresses at Low/Moderate score
    if label_type == "exchange" and decision in ("ALLOW", "WARN") and score <= 70:
        decision = "ALLOW"

    return decision


# ─── Output helpers ───────────────────────────────────────────────────────────


def print_result(
    decision: str,
    score: int,
    risk_level: str,
    detail_list: list,
    label_type: str,
    label_list: list,
    risk_report_url: str,
    address: str,
    coin: str,
    chain: str,
    json_output: bool,
) -> None:
    result = {
        "decision": decision,
        "score": score,
        "risk_level": risk_level,
        "detail_list": detail_list,
        "label_type": label_type,
        "label_list": label_list,
        "risk_report_url": risk_report_url,
        "address": address,
        "coin": coin,
        "chain": chain,
    }

    if json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # Human-readable output
    c = COLOUR
    rc = RISK_COLOUR.get(risk_level, "")

    decision_icon = {"ALLOW": "✅", "WARN": "⚠️ ", "BLOCK": "❌"}.get(decision, "❓")

    print(f"\n{c['bold']}收款地址安全检测报告{c['reset']}")
    print("─" * 50)
    print(f"地址：      {address}")
    print(f"链 / 代币：  {chain} ({coin})")

    labels_str = ", ".join(label_list) if label_list else "—"
    print(f"地址标签：  {labels_str} [{label_type or '未知'}]")
    print(
        f"风险评分：  {rc}{score} ({risk_level}){c['reset']}"
    )
    if detail_list:
        print(f"风险描述：  {', '.join(detail_list)}")
    if risk_report_url:
        print(f"详细报告：  {risk_report_url}")
    print("─" * 50)
    print(f"决策：      {decision_icon} {decision}")

    if decision == "ALLOW":
        print(f"{c['green']}该地址风险等级低，可以继续转账。{c['reset']}")
    elif decision == "WARN":
        print(
            f"{c['yellow']}该地址存在 {risk_level} 风险，请确认收款方身份后再继续。\n"
            f"如需继续请明确回复确认。{c['reset']}"
        )
    elif decision == "BLOCK":
        print(
            f"{c['red']}该地址存在严重风险 (Severe)，强烈建议取消本次转账。\n"
            f"请勿向此地址发送任何资产。{c['reset']}"
        )
    print()


def print_error(message: str, json_output: bool) -> None:
    if json_output:
        print(json.dumps({"decision": "ERROR", "error": message}, ensure_ascii=False, indent=2))
    else:
        print(f"\n⚠️  地址安全检测失败\n错误原因：{message}", file=sys.stderr)
        print("无法验证收款地址风险，请由用户决定是否继续转账。\n", file=sys.stderr)


# ─── Main ────────────────────────────────────────────────────────────────────


def parse_args() -> argparse.Namespace:
    all_supported = sorted(set(list(CHAIN_TO_COIN.keys()) + list(UNSUPPORTED_CHAINS.keys())))
    parser = argparse.ArgumentParser(
        description=(
            "检测转账目标地址的 AML 风险\n"
            "支持 Bitget Wallet Skill 和 Trust Wallet Skills (wallet-core / trust-web3-provider) 集成"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--address", "-a",
        required=True,
        help="收款地址（转账目标地址）",
    )
    parser.add_argument(
        "--chain", "-c",
        required=True,
        choices=all_supported,
        help=(
            f"链标识符（bitget-wallet-skill 或 Trust Wallet CoinType 格式）\n"
            f"支持（有 MistTrack 数据）：{', '.join(sorted(CHAIN_TO_COIN.keys()))}\n"
            f"不支持（exit 3）：{', '.join(sorted(UNSUPPORTED_CHAINS.keys()))}"
        ),
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="MistTrack API Key（低于环境变量 MISTTRACK_API_KEY 优先级）",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="以 JSON 格式输出结果（适合 Agent 机器解析）",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # 1. Handle unsupported chains first
    if args.chain in UNSUPPORTED_CHAINS:
        print_error(UNSUPPORTED_CHAINS[args.chain], args.json_output)
        sys.exit(EXIT_ERROR)

    # 2. Resolve API key
    api_key: Optional[str] = os.environ.get("MISTTRACK_API_KEY") or args.api_key
    if not api_key:
        print_error(
            "未设置 MISTTRACK_API_KEY 环境变量，也未提供 --api-key 参数。\n"
            "请先执行：export MISTTRACK_API_KEY=your_api_key",
            args.json_output,
        )
        sys.exit(EXIT_ERROR)

    # 2. Map chain → coin
    coin = CHAIN_TO_COIN[args.chain]
    address = args.address.strip()

    # 3. Call MistTrack APIs
    try:
        # 3a. Risk score (primary signal)
        risk_resp = get_risk_score(coin, address, api_key)

        if not risk_resp.get("success"):
            msg = risk_resp.get("msg", "未知错误")
            print_error(f"MistTrack API 返回失败：{msg}", args.json_output)
            sys.exit(EXIT_ERROR)

        data = risk_resp.get("data", {})
        score: int = data.get("score", 0)
        risk_level: str = data.get("risk_level", "Low")
        detail_list: list = data.get("detail_list", [])
        risk_report_url: str = data.get("risk_report_url", "")

        # 3b. Address labels (for whitelist logic)
        label_type = ""
        label_list: list = []
        try:
            label_resp = get_address_labels(coin, address, api_key)
            if label_resp.get("success"):
                label_data = label_resp.get("data", {})
                label_type = label_data.get("label_type", "")
                label_list = label_data.get("label_list", [])
        except Exception:
            # Labels are supplementary; don't fail if unavailable
            pass

    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else "?"
        if status == 402:
            print_error("MistTrack 订阅已过期，请前往 https://dashboard.misttrack.io 续订。", args.json_output)
        elif status == 429:
            print_error("已超过 MistTrack API 速率限制，请稍后重试。", args.json_output)
        else:
            print_error(f"HTTP 请求失败（状态码 {status}）：{e}", args.json_output)
        sys.exit(EXIT_ERROR)

    except requests.exceptions.Timeout:
        print_error("MistTrack API 请求超时（30s），请检查网络连接后重试。", args.json_output)
        sys.exit(EXIT_ERROR)

    except requests.exceptions.RequestException as e:
        print_error(f"网络请求错误：{e}", args.json_output)
        sys.exit(EXIT_ERROR)

    # 4. Make decision
    decision = decide(score, risk_level, label_type, label_list)

    # 5. Print result
    print_result(
        decision=decision,
        score=score,
        risk_level=risk_level,
        detail_list=detail_list,
        label_type=label_type,
        label_list=label_list,
        risk_report_url=risk_report_url,
        address=address,
        coin=coin,
        chain=args.chain,
        json_output=args.json_output,
    )

    # 6. Exit with appropriate code
    exit_map = {"ALLOW": EXIT_ALLOW, "WARN": EXIT_WARN, "BLOCK": EXIT_BLOCK}
    sys.exit(exit_map.get(decision, EXIT_ERROR))


if __name__ == "__main__":
    main()
