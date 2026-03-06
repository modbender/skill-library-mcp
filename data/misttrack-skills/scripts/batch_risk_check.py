#!/usr/bin/env python3
"""
MistTrack 批量异步风险评分脚本

使用异步模式批量查询多个地址的 AML 风险评分，适合大批量检测场景。

用法:
    export MISTTRACK_API_KEY=YOUR_KEY

    # 从命令行传入地址列表（逗号分隔）
    python batch_risk_check.py --addresses 0x1...,0x2...,0x3... --coin ETH

    # 从文件读取地址列表（每行一个地址）
    python batch_risk_check.py --input addresses.txt --coin ETH

    # 输出结果到 CSV 文件
    python batch_risk_check.py --input addresses.txt --coin ETH --output results.csv

    # 也可通过命令行参数传入（优先级低于环境变量）
    python batch_risk_check.py --addresses 0x1...,0x2... --coin ETH --api-key YOUR_KEY
"""

import argparse
import os
import requests
import time
import csv
import json
import sys
from typing import List, Optional


BASE_URL = "https://openapi.misttrack.io"


def create_task(coin: str, api_key: str, address: str = None, txid: str = None) -> dict:
    """创建异步风险评分任务"""
    payload = {"coin": coin, "api_key": api_key}
    if address:
        payload["address"] = address
    elif txid:
        payload["txid"] = txid
    else:
        raise ValueError("address 或 txid 至少传一个")

    response = requests.post(
        f"{BASE_URL}/v2/risk_score_create_task",
        headers={"Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def query_task(coin: str, api_key: str, address: str = None, txid: str = None) -> dict:
    """查询异步风险评分任务结果（此接口无速率限制）"""
    params = {"coin": coin, "api_key": api_key}
    if address:
        params["address"] = address
    elif txid:
        params["txid"] = txid

    response = requests.get(
        f"{BASE_URL}/v2/risk_score_query_task",
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def check_address_async(
    coin: str,
    api_key: str,
    address: str,
    max_wait: int = 60,
    poll_interval: int = 3,
) -> Optional[dict]:
    """
    对单个地址进行异步风险评分检查

    Args:
        coin: 代币类型
        api_key: API 密钥
        address: 要查询的地址
        max_wait: 最大等待时间（秒）
        poll_interval: 轮询间隔（秒）

    Returns:
        风险评分数据字典，或 None（如果超时/失败）
    """
    # 创建任务
    create_result = create_task(coin=coin, api_key=api_key, address=address)
    if not create_result.get("success"):
        print(f"  ❌ 创建任务失败 [{address}]: {create_result.get('msg')}")
        return None

    has_result = create_result.get("data", {}).get("has_result", False)

    # 如果没有缓存，等待一段时间
    if not has_result:
        time.sleep(poll_interval)

    # 轮询结果
    elapsed = 0
    while elapsed < max_wait:
        query_result = query_task(coin=coin, api_key=api_key, address=address)

        if query_result.get("msg") == "TaskUnderRunning":
            time.sleep(poll_interval)
            elapsed += poll_interval
            continue

        if query_result.get("success") and query_result.get("data"):
            return query_result.get("data")

        print(f"  ❌ 查询失败 [{address}]: {query_result.get('msg')}")
        return None

    print(f"  ⏰ 超时 [{address}]：超过 {max_wait} 秒未获得结果")
    return None


def batch_check(
    addresses: List[str],
    coin: str,
    api_key: str,
    output_file: Optional[str] = None,
    verbose: bool = True,
) -> List[dict]:
    """
    批量检测地址风险评分

    Args:
        addresses: 地址列表
        coin: 代币类型
        api_key: API 密钥
        output_file: 输出 CSV 文件路径（可选）
        verbose: 是否打印详细信息

    Returns:
        结果列表，每项包含 address 和风险数据
    """
    results = []
    total = len(addresses)

    print(f"\n开始批量风险评分检测，共 {total} 个地址，代币: {coin}")
    print(f"{'='*60}")

    for idx, address in enumerate(addresses, 1):
        address = address.strip()
        if not address:
            continue

        if verbose:
            print(f"[{idx}/{total}] 正在检测: {address[:20]}...")

        try:
            data = check_address_async(coin=coin, api_key=api_key, address=address)

            if data:
                score = data.get("score", 0)
                risk_level = data.get("risk_level", "Unknown")
                detail_list = ", ".join(data.get("detail_list", []))

                result = {
                    "address": address,
                    "score": score,
                    "risk_level": risk_level,
                    "detail_list": detail_list,
                    "hacking_event": data.get("hacking_event", ""),
                    "risk_report_url": data.get("risk_report_url", ""),
                }
                results.append(result)

                if verbose:
                    level_emoji = {"Low": "✅", "Moderate": "⚡", "High": "⚠️", "Severe": "⛔"}.get(risk_level, "❓")
                    print(f"       {level_emoji} 评分: {score}, 级别: {risk_level}")
                    if detail_list:
                        print(f"       风险: {detail_list}")
            else:
                results.append({
                    "address": address,
                    "score": None,
                    "risk_level": "Error",
                    "detail_list": "查询失败",
                    "hacking_event": "",
                    "risk_report_url": "",
                })

        except Exception as e:
            print(f"  ❌ 异常 [{address}]: {e}")
            results.append({
                "address": address,
                "score": None,
                "risk_level": "Error",
                "detail_list": str(e),
                "hacking_event": "",
                "risk_report_url": "",
            })

        # 防止触发速率限制
        if idx < total:
            time.sleep(1.1)

    # 统计概要
    print(f"\n{'='*60}")
    print(f"  检测完成！共 {len(results)} 个地址")
    for level in ["Severe", "High", "Moderate", "Low"]:
        count = sum(1 for r in results if r.get("risk_level") == level)
        if count > 0:
            print(f"  {level}: {count} 个")
    print(f"{'='*60}\n")

    # 写入 CSV 文件
    if output_file:
        fieldnames = ["address", "score", "risk_level", "detail_list", "hacking_event", "risk_report_url"]
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"结果已保存至: {output_file}")

    return results


def main():
    parser = argparse.ArgumentParser(description="MistTrack 批量异步风险评分工具")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--addresses", help="地址列表（逗号分隔）")
    group.add_argument("--input", "-i", help="包含地址的文件路径（每行一个地址）")
    parser.add_argument("--coin", required=True, help="代币类型（如 ETH、BTC、TRX）")
    parser.add_argument("--api-key", dest="api_key", help="MistTrack API Key（优先使用环境变量 MISTTRACK_API_KEY）")
    parser.add_argument("--output", "-o", help="结果输出到 CSV 文件")
    parser.add_argument("--json", action="store_true", dest="json_output", help="JSON 格式输出")
    parser.add_argument("--quiet", "-q", action="store_true", help="静默模式，减少输出")

    args = parser.parse_args()

    # 优先从环境变量获取 API Key
    api_key = os.environ.get("MISTTRACK_API_KEY") or args.api_key
    if not api_key:
        print("错误：请设置环境变量 MISTTRACK_API_KEY 或使用 --api-key 参数", file=sys.stderr)
        sys.exit(1)

    # 获取地址列表
    if args.addresses:
        addresses = [a.strip() for a in args.addresses.split(",") if a.strip()]
    else:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                addresses = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        except FileNotFoundError:
            print(f"错误：文件不存在: {args.input}", file=sys.stderr)
            sys.exit(1)

    if not addresses:
        print("错误：未找到任何有效地址", file=sys.stderr)
        sys.exit(1)

    results = batch_check(
        addresses=addresses,
        coin=args.coin,
        api_key=api_key,
        output_file=args.output,
        verbose=not args.quiet,
    )

    if args.json_output:
        print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
