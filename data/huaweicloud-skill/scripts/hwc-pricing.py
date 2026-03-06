#!/usr/bin/env python3
"""
华为云价格计算脚本
用于根据资源清单估算月度成本

使用方法:
    python hwc-pricing.py --input resources.json --output cost.md

环境变量:
    HWC_ACCESS_KEY - 华为云 AK
    HWC_SECRET_KEY - 华为云 SK
"""

import json
import os
import argparse
from datetime import datetime
from typing import Dict, List, Any

# 参考价格表（华北-北京四，包月价格）
# 实际价格请以华为云官网为准
PRICE_TABLE = {
    "cn-north-4": {
        "ecs": {
            "s6.small.1": {"hourly": 0.09, "monthly": 45},
            "s6.medium.2": {"hourly": 0.13, "monthly": 68},
            "s6.large.2": {"hourly": 0.26, "monthly": 130},
            "s6.xlarge.2": {"hourly": 0.52, "monthly": 260},
            "s6.2xlarge.2": {"hourly": 1.04, "monthly": 520},
            "c6.xlarge.4": {"hourly": 0.80, "monthly": 400},
            "c6.2xlarge.4": {"hourly": 1.60, "monthly": 800},
            "m6.xlarge.8": {"hourly": 1.20, "monthly": 600},
        },
        "rds": {
            "rds.mysql.c6.large.2": {"hourly": 0.68, "monthly": 340},
            "rds.mysql.c6.xlarge.2": {"hourly": 1.36, "monthly": 680},
            "rds.mysql.c6.2xlarge.2": {"hourly": 2.72, "monthly": 1360},
            "rds.mysql.c6.large.2.ha": {"hourly": 1.36, "monthly": 680},
            "rds.mysql.c6.xlarge.2.ha": {"hourly": 2.72, "monthly": 1360},
        },
        "dcs": {
            "redis.single.xu1.large.2.2": {"hourly": 0.08, "monthly": 58},
            "redis.ha.xu1.large.r2.2": {"hourly": 0.16, "monthly": 116},
            "redis.ha.xu1.large.r2.4": {"hourly": 0.32, "monthly": 232},
            "redis.ha.xu1.large.r2.8": {"hourly": 0.64, "monthly": 464},
        },
        "eip": {
            "bandwidth": {
                1: {"monthly": 23},
                2: {"monthly": 46},
                5: {"monthly": 115},
                10: {"monthly": 230},
                20: {"monthly": 460},
                50: {"monthly": 1150},
                100: {"monthly": 2300},
            },
            "traffic": {"per_gb": 0.80},
        },
        "elb": {
            "shared": {"hourly": 0.05, "monthly": 36},
            "dedicated": {"hourly": 0.30, "monthly": 216},
        },
        "evs": {
            "SATA": {"per_gb_monthly": 0.20},
            "SAS": {"per_gb_monthly": 0.30},
            "SSD": {"per_gb_monthly": 0.35},
            "ESSD": {"per_gb_monthly": 0.50},
        },
        "obs": {
            "standard": {"per_gb_monthly": 0.12},
            "infrequent": {"per_gb_monthly": 0.08},
            "archive": {"per_gb_monthly": 0.033},
        },
    },
}


def calculate_cost(resources: Dict[str, Any]) -> Dict[str, Any]:
    """计算资源成本"""
    region = resources.get("region", "cn-north-4")
    billing_mode = resources.get("billing_mode", "monthly")

    if region not in PRICE_TABLE:
        raise ValueError(f"不支持的 region: {region}")

    prices = PRICE_TABLE[region]
    items = []
    total = 0

    for res in resources.get("resources", []):
        res_type = res["type"]
        spec = res.get("spec", "")
        count = res.get("count", 1)

        if res_type == "ecs":
            price_info = prices["ecs"].get(spec, {})
            unit_price = price_info.get(billing_mode, 0)
            cost = unit_price * count
            items.append({
                "type": "ECS",
                "spec": spec,
                "unit_price": unit_price,
                "count": count,
                "cost": cost,
            })
            total += cost

        elif res_type == "rds":
            price_info = prices["rds"].get(spec, {})
            unit_price = price_info.get(billing_mode, 0)
            cost = unit_price * count
            # 加存储费用
            storage = res.get("storage", 100)
            storage_cost = storage * prices["evs"]["SSD"]["per_gb_monthly"]
            cost += storage_cost
            items.append({
                "type": "RDS MySQL",
                "spec": spec,
                "unit_price": unit_price,
                "count": count,
                "cost": cost,
            })
            total += cost

        elif res_type == "dcs":
            price_info = prices["dcs"].get(spec, {})
            unit_price = price_info.get(billing_mode, 0)
            cost = unit_price * count
            items.append({
                "type": "DCS Redis",
                "spec": spec,
                "unit_price": unit_price,
                "count": count,
                "cost": cost,
            })
            total += cost

        elif res_type == "eip":
            bandwidth = res.get("bandwidth", 5)
            bw_prices = prices["eip"]["bandwidth"]
            # 找最接近的带宽档位
            bw_key = min(bw_prices.keys(), key=lambda x: abs(x - bandwidth))
            unit_price = bw_prices[bw_key]["monthly"]
            cost = unit_price * count
            items.append({
                "type": "EIP",
                "spec": f"{bandwidth}Mbps",
                "unit_price": unit_price,
                "count": count,
                "cost": cost,
            })
            total += cost

        elif res_type == "elb":
            lb_type = res.get("lb_type", "shared")
            price_info = prices["elb"].get(lb_type, {})
            unit_price = price_info.get(billing_mode, 0)
            cost = unit_price * count
            items.append({
                "type": "ELB",
                "spec": lb_type,
                "unit_price": unit_price,
                "count": count,
                "cost": cost,
            })
            total += cost

        elif res_type == "evs":
            disk_type = res.get("disk_type", "SSD")
            size = res.get("size", 100)
            unit_price = prices["evs"][disk_type]["per_gb_monthly"]
            cost = unit_price * size * count
            items.append({
                "type": "EVS",
                "spec": f"{disk_type} {size}GB",
                "unit_price": unit_price,
                "count": count,
                "cost": cost,
            })
            total += cost

        elif res_type == "obs":
            storage_class = res.get("storage_class", "standard")
            size = res.get("size", 100)
            unit_price = prices["obs"][storage_class]["per_gb_monthly"]
            cost = unit_price * size
            items.append({
                "type": "OBS",
                "spec": f"{storage_class} {size}GB",
                "unit_price": unit_price,
                "count": 1,
                "cost": cost,
            })
            total += cost

    return {
        "region": region,
        "billing_mode": billing_mode,
        "items": items,
        "total": total,
        "generated_at": datetime.now().isoformat(),
    }


def format_markdown(result: Dict[str, Any]) -> str:
    """格式化为 Markdown"""
    lines = [
        "## 成本预估（月度）",
        "",
        f"**区域**: {result['region']}",
        f"**计费模式**: {result['billing_mode']}",
        "",
        "| 资源类型 | 规格 | 单价(元) | 数量 | 月费用(元) |",
        "|----------|------|----------|------|-----------|",
    ]

    for item in result["items"]:
        lines.append(
            f"| {item['type']} | {item['spec']} | {item['unit_price']:.2f} | "
            f"{item['count']} | {item['cost']:.2f} |"
        )

    lines.append(f"| **合计** | | | | **¥{result['total']:.2f}** |")
    lines.append("")
    lines.append("*价格仅供参考，以实际账单为准*")
    lines.append(f"*生成时间: {result['generated_at']}*")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="华为云价格计算")
    parser.add_argument("--input", "-i", required=True, help="资源清单 JSON 文件")
    parser.add_argument("--output", "-o", help="输出 Markdown 文件")
    parser.add_argument(
        "--billing", "-b", choices=["monthly", "hourly"],
        default="monthly", help="计费模式"
    )

    args = parser.parse_args()

    # 读取资源清单
    with open(args.input, "r", encoding="utf-8") as f:
        resources = json.load(f)

    resources["billing_mode"] = args.billing

    # 计算成本
    result = calculate_cost(resources)

    # 输出
    md_content = format_markdown(result)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"成本报告已保存到: {args.output}")
    else:
        print(md_content)


if __name__ == "__main__":
    main()
