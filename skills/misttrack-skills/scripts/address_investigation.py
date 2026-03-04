#!/usr/bin/env python3
"""
MistTrack 完整地址调查脚本

对指定地址进行全方位 AML 调查，依次调用以下接口：
1. v1/address_labels    - 地址标签（实体身份）
2. v1/address_overview  - 地址概览（余额/交易统计）
3. v2/risk_score        - 风险评分 (KYT/KYA)
4. v1/address_trace     - 地址画像（平台交互/恶意事件/关联信息）
5. v1/transactions_investigation - 交易调查（转入/转出明细）
6. v1/address_counterparty       - 交易对手分析

用法:
    export MISTTRACK_API_KEY=YOUR_KEY
    python address_investigation.py --address 0x... --coin ETH
    python address_investigation.py --address 0x... --coin ETH --json

    # 也可通过命令行参数传入（优先级低于环境变量）
    python address_investigation.py --address 0x... --coin ETH --api-key YOUR_KEY
"""

import argparse
import os
import requests
import json
import sys
from datetime import datetime
from typing import Optional


BASE_URL = "https://openapi.misttrack.io"


def api_get(endpoint: str, params: dict) -> dict:
    """发送 GET 请求并返回 JSON 响应"""
    response = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def investigate_address(coin: str, address: str, api_key: str) -> dict:
    """
    对地址进行全面调查，聚合所有 API 结果

    Returns:
        包含所有调查结果的字典
    """
    base_params = {"coin": coin, "address": address, "api_key": api_key}
    report = {"address": address, "coin": coin}

    # 1. 地址标签
    print("  [1/6] 获取地址标签...")
    try:
        result = api_get("v1/address_labels", base_params)
        report["labels"] = result.get("data") if result.get("success") else {"error": result.get("msg")}
    except Exception as e:
        report["labels"] = {"error": str(e)}

    # 2. 地址概览
    print("  [2/6] 获取地址概览...")
    try:
        result = api_get("v1/address_overview", base_params)
        report["overview"] = result.get("data") if result.get("success") else {"error": result.get("msg")}
    except Exception as e:
        report["overview"] = {"error": str(e)}

    # 3. 风险评分
    print("  [3/6] 获取风险评分...")
    try:
        result = api_get("v2/risk_score", base_params)
        report["risk_score"] = result.get("data") if result.get("success") else {"error": result.get("msg")}
    except Exception as e:
        report["risk_score"] = {"error": str(e)}

    # 4. 地址画像
    print("  [4/6] 获取地址画像...")
    try:
        result = api_get("v1/address_trace", base_params)
        report["address_trace"] = result.get("data") if result.get("success") else {"error": result.get("msg")}
    except Exception as e:
        report["address_trace"] = {"error": str(e)}

    # 5. 交易调查
    print("  [5/6] 获取交易调查（第一页）...")
    try:
        params = dict(base_params)
        params["page"] = 1
        result = api_get("v1/transactions_investigation", params)
        report["transactions"] = result.get("data") if result.get("success") else {"error": result.get("msg")}
    except Exception as e:
        report["transactions"] = {"error": str(e)}

    # 6. 交易对手分析
    print("  [6/6] 获取交易对手分析...")
    try:
        result = api_get("v1/address_counterparty", base_params)
        if result.get("success"):
            report["counterparty"] = result.get("address_counterparty_list", [])
        else:
            report["counterparty"] = {"error": result.get("msg")}
    except Exception as e:
        report["counterparty"] = {"error": str(e)}

    return report


def format_timestamp(ts: Optional[int]) -> str:
    """将 Unix 时间戳转换为可读时间"""
    if not ts:
        return "N/A"
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def print_investigation_report(report: dict):
    """格式化打印调查报告"""
    address = report.get("address", "")
    coin = report.get("coin", "")

    print(f"\n{'='*70}")
    print(f"  MistTrack 地址完整调查报告")
    print(f"{'='*70}")
    print(f"  地址: {address}")
    print(f"  代币: {coin}")

    # 标签信息
    labels = report.get("labels", {})
    if not labels.get("error"):
        print(f"\n  📋 地址标签")
        print(f"  {'-'*50}")
        label_list = labels.get("label_list", [])
        label_type = labels.get("label_type", "")
        print(f"  标签: {', '.join(label_list) if label_list else '无'}")
        if label_type:
            print(f"  类型: {label_type}")

    # 概览信息
    overview = report.get("overview", {})
    if not overview.get("error"):
        print(f"\n  📊 地址概览")
        print(f"  {'-'*50}")
        print(f"  余额:       {overview.get('balance', 0):,.4f} {coin}")
        print(f"  总交易数:   {overview.get('txs_count', 0):,}")
        print(f"  总接收:     {overview.get('total_received', 0):,.4f}")
        print(f"  总发送:     {overview.get('total_spent', 0):,.4f}")
        print(f"  首次交易:   {format_timestamp(overview.get('first_seen'))}")
        print(f"  最近交易:   {format_timestamp(overview.get('last_seen'))}")

    # 风险评分
    risk = report.get("risk_score", {})
    if not risk.get("error"):
        score = risk.get("score", 0)
        risk_level = risk.get("risk_level", "Unknown")
        detail_list = risk.get("detail_list", [])
        hacking_event = risk.get("hacking_event", "")

        level_emoji = {"Low": "✅", "Moderate": "⚡", "High": "⚠️", "Severe": "⛔"}.get(risk_level, "❓")
        print(f"\n  🔍 风险评分 (AML)")
        print(f"  {'-'*50}")
        print(f"  评分:   {score}/100")
        print(f"  级别:   {level_emoji} {risk_level}")
        if hacking_event:
            print(f"  安全事件: {hacking_event}")
        if detail_list:
            print(f"  风险描述:")
            for item in detail_list:
                print(f"    • {item}")

        # 风险详情（Top 5）
        risk_detail = risk.get("risk_detail", [])
        if risk_detail:
            print(f"  风险关联实体（Top 5）:")
            for item in risk_detail[:5]:
                entity = item.get("entity", "")
                risk_type = item.get("risk_type", "")
                volume = item.get("volume", 0)
                hop_num = item.get("hop_num", 0)
                exposure_type = item.get("exposure_type", "")
                percent = item.get("percent", 0)
                print(f"    • {entity} [{risk_type}] {exposure_type} {hop_num}跳 ${volume:,.2f} ({percent:.2f}%)")

    # 地址画像
    trace = report.get("address_trace", {})
    if trace and not trace.get("error"):
        print(f"\n  🔗 地址画像")
        print(f"  {'-'*50}")
        first_address = trace.get("first_address", "")
        if first_address:
            print(f"  Gas 来源: {first_address}")

        use_platform = trace.get("use_platform", {})
        for platform_type in ["exchange", "dex", "mixer", "nft"]:
            platform = use_platform.get(platform_type, {})
            count = platform.get("count", 0)
            if count > 0:
                items = platform.get(f"{platform_type}_list", [])
                print(f"  {platform_type.upper()} ({count}): {', '.join(items[:5])}")

        malicious_event = trace.get("malicious_event", {})
        has_malicious = any(
            malicious_event.get(k, {}).get("count", 0) > 0
            for k in ["phishing", "ransom", "stealing", "laundering"]
        )
        if has_malicious:
            print(f"  ⚠️ 恶意事件:")
            for event_type in ["phishing", "ransom", "stealing", "laundering"]:
                event = malicious_event.get(event_type, {})
                if event.get("count", 0) > 0:
                    items = event.get(f"{event_type}_list", [])
                    print(f"    - {event_type}: {', '.join(items[:3])}")

        relation_info = trace.get("relation_info", {})
        ens_list = relation_info.get("ens", {}).get("ens_list", [])
        twitter_list = relation_info.get("twitter", {}).get("twitter_list", [])
        if ens_list:
            print(f"  ENS: {', '.join(ens_list)}")
        if twitter_list:
            print(f"  Twitter: {', '.join(twitter_list)}")

    # 交易概要
    transactions = report.get("transactions", {})
    if transactions and not transactions.get("error"):
        print(f"\n  💸 交易调查")
        print(f"  {'-'*50}")
        total_pages = transactions.get("total_pages", 1)
        transactions_on_page = transactions.get("transactions_on_page", 0)
        print(f"  总页数: {total_pages}, 当前页条目: {transactions_on_page}")

        out_txs = transactions.get("out", [])
        if out_txs:
            print(f"  转出目标（Top 5）:")
            for tx in out_txs[:5]:
                label = tx.get("label") or tx.get("address", "")[:20]
                amount = tx.get("amount", 0)
                tx_type = tx.get("type", 1)
                type_labels = {1: "普通地址", 2: "恶意地址", 3: "实体地址", 4: "合约"}
                type_str = type_labels.get(tx_type, "")
                print(f"    → {label} [{type_str}] {amount:,.4f}")

        in_txs = transactions.get("in", [])
        if in_txs:
            print(f"  转入来源（Top 5）:")
            for tx in in_txs[:5]:
                label = tx.get("label") or tx.get("address", "")[:20]
                amount = tx.get("amount", 0)
                tx_type = tx.get("type", 1)
                type_labels = {1: "普通地址", 2: "恶意地址", 3: "实体地址", 4: "合约"}
                type_str = type_labels.get(tx_type, "")
                print(f"    ← {label} [{type_str}] {amount:,.4f}")

    # 交易对手
    counterparty = report.get("counterparty", [])
    if counterparty and isinstance(counterparty, list):
        print(f"\n  🤝 主要交易对手（Top 5）")
        print(f"  {'-'*50}")
        for item in counterparty[:5]:
            name = item.get("name", "")
            amount = item.get("amount", 0)
            percent = item.get("percent", 0)
            print(f"  {name:<25} ${amount:>15,.2f}  ({percent:.3f}%)")

    # 风险报告链接
    risk_report_url = report.get("risk_score", {}).get("risk_report_url", "")
    if risk_report_url:
        print(f"\n  📄 PDF 风险报告: {risk_report_url}")

    print(f"\n{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(description="MistTrack 地址完整调查工具")
    parser.add_argument("--address", required=True, help="要调查的地址")
    parser.add_argument("--coin", required=True, help="代币类型（如 ETH、BTC、TRX）")
    parser.add_argument("--api-key", dest="api_key", help="MistTrack API Key（优先使用环境变量 MISTTRACK_API_KEY）")
    parser.add_argument("--json", action="store_true", dest="json_output", help="输出原始 JSON 数据")
    parser.add_argument("--output", "-o", help="将 JSON 结果保存到文件")

    args = parser.parse_args()

    # 优先从环境变量获取 API Key
    api_key = os.environ.get("MISTTRACK_API_KEY") or args.api_key
    if not api_key:
        print("错误：请设置环境变量 MISTTRACK_API_KEY 或使用 --api-key 参数", file=sys.stderr)
        sys.exit(1)

    print(f"\n正在对地址进行全面调查: {args.address}")
    print(f"代币: {args.coin}")
    print(f"{'='*60}")

    try:
        report = investigate_address(
            coin=args.coin,
            address=args.address,
            api_key=api_key,
        )

        if args.json_output or args.output:
            json_str = json.dumps(report, indent=2, ensure_ascii=False)
            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(json_str)
                print(f"\n结果已保存至: {args.output}")
            if args.json_output:
                print(json_str)
        else:
            print_investigation_report(report)

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
