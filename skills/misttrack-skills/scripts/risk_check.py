#!/usr/bin/env python3
"""
MistTrack 单地址风险评分检查脚本

用法:
    export MISTTRACK_API_KEY=YOUR_KEY
    python risk_check.py --address 0x... --coin ETH
    python risk_check.py --txid 0x... --coin ETH

    # 也可通过命令行参数传入（优先级低于环境变量）
    python risk_check.py --address 0x... --coin ETH --api-key YOUR_KEY
"""

import argparse
import os
import requests
import json
import sys


BASE_URL = "https://openapi.misttrack.io"

RISK_LEVEL_COLOR = {
    "Low": "\033[32m",       # 绿色
    "Moderate": "\033[33m",  # 黄色
    "High": "\033[91m",      # 橙红色
    "Severe": "\033[31m",    # 红色
}
RESET = "\033[0m"


def get_risk_score(coin: str, api_key: str, address: str = None, txid: str = None) -> dict:
    """调用 v2/risk_score 接口获取风险评分"""
    params = {"coin": coin, "api_key": api_key}
    if address:
        params["address"] = address
    elif txid:
        params["txid"] = txid
    else:
        raise ValueError("address 或 txid 至少传一个")

    response = requests.get(f"{BASE_URL}/v2/risk_score", params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def get_address_labels(coin: str, address: str, api_key: str) -> dict:
    """调用 v1/address_labels 接口获取地址标签"""
    params = {"coin": coin, "address": address, "api_key": api_key}
    response = requests.get(f"{BASE_URL}/v1/address_labels", params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def print_risk_report(data: dict, target: str):
    """格式化打印风险报告"""
    score = data.get("score", 0)
    risk_level = data.get("risk_level", "Unknown")
    hacking_event = data.get("hacking_event", "")
    detail_list = data.get("detail_list", [])
    risk_detail = data.get("risk_detail", [])
    risk_report_url = data.get("risk_report_url", "")

    color = RISK_LEVEL_COLOR.get(risk_level, "")

    print(f"\n{'='*60}")
    print(f"  MistTrack AML 风险分析报告")
    print(f"{'='*60}")
    print(f"  目标地址/交易: {target}")
    print(f"  风险评分:      {color}{score}{RESET}")
    print(f"  风险级别:      {color}{risk_level}{RESET}")

    if hacking_event:
        print(f"  安全事件:      {hacking_event}")

    if detail_list:
        print(f"\n  风险描述:")
        for item in detail_list:
            print(f"    • {item}")

    if risk_detail:
        print(f"\n  风险详情:")
        print(f"  {'实体':<25} {'风险类型':<20} {'暴露方式':<10} {'跳数':<6} {'金额(USD)':<15} {'占比%'}")
        print(f"  {'-'*90}")
        for item in risk_detail:
            entity = item.get("entity", "")[:24]
            risk_type = item.get("risk_type", "")
            exposure = item.get("exposure_type", "")
            hop_num = item.get("hop_num", 0)
            volume = item.get("volume", 0)
            percent = item.get("percent", 0)
            print(f"  {entity:<25} {risk_type:<20} {exposure:<10} {hop_num:<6} {volume:<15,.2f} {percent:.3f}%")

    if risk_report_url:
        print(f"\n  PDF 报告: {risk_report_url}")

    print(f"{'='*60}")

    # 根据风险级别给出操作建议
    recommendations = {
        "Severe": "⛔ 建议：禁止提现和交易，立即上报该地址！",
        "High":   "⚠️  建议：保持高度监控，需人工复核后决策。",
        "Moderate": "⚡ 建议：适度监管，建议进一步调查交易来源。",
        "Low":    "✅ 建议：风险较低，可正常处理。",
    }
    if risk_level in recommendations:
        print(f"\n  {recommendations[risk_level]}\n")


def main():
    parser = argparse.ArgumentParser(description="MistTrack 地址风险评分检查工具")
    parser.add_argument("--address", help="要查询的地址")
    parser.add_argument("--txid", help="要查询的交易哈希")
    parser.add_argument("--coin", required=True, help="代币类型（如 ETH、BTC、TRX、USDT-TRC20）")
    parser.add_argument("--api-key", dest="api_key", help="MistTrack API Key（优先使用环境变量 MISTTRACK_API_KEY）")
    parser.add_argument("--with-labels", action="store_true", help="同时获取地址标签信息")
    parser.add_argument("--json", action="store_true", dest="json_output", help="输出原始 JSON 数据")

    args = parser.parse_args()

    # 优先从环境变量获取 API Key
    api_key = os.environ.get("MISTTRACK_API_KEY") or args.api_key
    if not api_key:
        print("错误：请设置环境变量 MISTTRACK_API_KEY 或使用 --api-key 参数", file=sys.stderr)
        sys.exit(1)

    if not args.address and not args.txid:
        print("错误：--address 或 --txid 至少提供一个", file=sys.stderr)
        sys.exit(1)

    target = args.address or args.txid

    try:
        # 获取地址标签（可选）
        if args.with_labels and args.address:
            print(f"正在获取地址标签: {args.address}...")
            label_result = get_address_labels(args.coin, args.address, api_key)
            if label_result.get("success"):
                label_data = label_result.get("data", {})
                print(f"标签: {label_data.get('label_list', [])}, 类型: {label_data.get('label_type', '')}")
            else:
                print(f"标签查询失败: {label_result.get('msg')}")

        # 获取风险评分
        print(f"正在查询风险评分: {target}...")
        result = get_risk_score(
            coin=args.coin,
            api_key=api_key,
            address=args.address,
            txid=args.txid,
        )

        if args.json_output:
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return

        if not result.get("success"):
            print(f"查询失败: {result.get('msg')}", file=sys.stderr)
            sys.exit(1)

        print_risk_report(result.get("data", {}), target)

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 402:
            print("错误：MistTrack 订阅已过期，请续订。", file=sys.stderr)
        elif e.response.status_code == 429:
            print("错误：已超过速率限制，请降低请求频率。", file=sys.stderr)
        else:
            print(f"HTTP 错误: {e}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
