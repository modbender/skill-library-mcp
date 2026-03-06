#!/usr/bin/env python3
"""
巴菲特基本面分析 - 数据采集脚本
================================
自动获取一家上市公司的全面财务数据，输出结构化JSON供分析使用。

用法：
    python3 fetch_company_data.py "贵州茅台"
    python3 fetch_company_data.py "600519"
    python3 fetch_company_data.py "比亚迪" --peers "长城汽车,长安汽车"
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime

ENV = os.environ.copy()
ENV["PATH"] = "/home/node/.local/bin:" + ENV.get("PATH", "")

def mcporter(tool, **kwargs):
    """调用 mcporter MCP 工具"""
    args = " ".join(f"{k}={v}" for k, v in kwargs.items())
    cmd = f"mcporter call {tool} {args}"
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=ENV, timeout=60)
        if r.stdout.strip():
            return json.loads(r.stdout)
    except (json.JSONDecodeError, subprocess.TimeoutExpired) as e:
        pass
    return None


def mcporter_to_file(tool, out_path, **kwargs):
    """大数据量 API 先写文件再解析"""
    args = " ".join(f"{k}={v}" for k, v in kwargs.items())
    cmd = f"mcporter call {tool} {args}"
    try:
        with open(out_path, "w") as f:
            subprocess.run(cmd, shell=True, stdout=f, stderr=subprocess.DEVNULL, env=ENV, timeout=60)
        if os.path.getsize(out_path) > 2:
            with open(out_path) as f:
                return json.load(f)
    except (json.JSONDecodeError, subprocess.TimeoutExpired, OSError):
        pass
    return None


def safe_first(data):
    """安全取第一个元素"""
    if isinstance(data, list) and data:
        return data[0]
    if isinstance(data, dict):
        return data
    return {}


def fetch_company_data(keyword):
    """获取公司全面数据"""
    result = {
        "keyword": keyword,
        "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "errors": []
    }

    # ━━━ 1. 公司基本信息 ━━━
    print(f"[1/10] 公司基本信息...", flush=True)
    info = mcporter("fintool-company.get_company_base_info", keyword=keyword)
    if info:
        result["company_info"] = info
        result["name"] = info.get("security_name", keyword)
    else:
        result["company_info"] = {}
        result["name"] = keyword
        result["errors"].append("公司基本信息获取失败")

    # ━━━ 2. 行业分类 ━━━
    print(f"[2/10] 行业分类...", flush=True)
    industry = mcporter("fintool-company.get_stock_industry_sws", keyword=keyword)
    result["industry"] = safe_first(industry) if industry else {}
    # 从行业数据中获取证券代码
    if result["industry"].get("security_code"):
        result["code"] = result["industry"]["security_code"]
    time.sleep(0.2)

    # ━━━ 3. 所属板块 ━━━
    print(f"[3/10] 所属板块...", flush=True)
    plates = mcporter("fintool-plates.get_stock_plate", keyword=keyword)
    if isinstance(plates, list):
        result["plates"] = [{"name": p.get("plate_name", ""), "profile": p.get("stock_profiles", "")[:200]} for p in plates[:5]]
    else:
        result["plates"] = []

    # ━━━ 4. 核心财务指标（多期） ━━━
    print(f"[4/10] 核心财务指标...", flush=True)
    metrics = mcporter_to_file("fintool-company.get_financial_analytics_metric", "/tmp/fam_raw.json", keyword=keyword)
    if isinstance(metrics, list):
        result["financial_metrics"] = metrics[:4]  # 最近4期
    else:
        result["financial_metrics"] = []
        result["errors"].append("财务指标获取失败")
    time.sleep(0.2)

    # ━━━ 5. 利润表（多期） ━━━
    print(f"[5/10] 利润表...", flush=True)
    income_statements = []
    for end_date in ["2025-12-31", "2025-09-30", "2025-06-30", "2024-12-31", "2024-06-30", "2023-12-31"]:
        inc = mcporter("fintool-company.get_income_statement", keyword=keyword, end_date=end_date)
        if inc:
            item = safe_first(inc)
            if item and item.get("end_date"):
                existing_dates = [x.get("end_date") for x in income_statements]
                if item["end_date"] not in existing_dates:
                    income_statements.append(item)
        time.sleep(0.15)
    result["income_statements"] = income_statements

    # ━━━ 6. 资产负债表 ━━━
    print(f"[6/10] 资产负债表...", flush=True)
    balance_sheets = []
    for end_date in ["2025-12-31", "2025-09-30", "2024-12-31", "2023-12-31"]:
        bs = mcporter("fintool-company.get_balance_sheet", keyword=keyword, end_date=end_date)
        if bs:
            item = safe_first(bs)
            if item and item.get("end_date"):
                existing_dates = [x.get("end_date") for x in balance_sheets]
                if item["end_date"] not in existing_dates:
                    balance_sheets.append(item)
        time.sleep(0.15)
    result["balance_sheets"] = balance_sheets

    # ━━━ 7. 现金流量表 ━━━
    print(f"[7/10] 现金流量表...", flush=True)
    cash_flows = []
    for end_date in ["2025-12-31", "2025-09-30", "2024-12-31", "2024-06-30", "2023-12-31"]:
        cf = mcporter("fintool-company.get_cash_flow", keyword=keyword, end_date=end_date)
        if cf:
            item = safe_first(cf)
            if item and item.get("end_date"):
                existing_dates = [x.get("end_date") for x in cash_flows]
                if item["end_date"] not in existing_dates:
                    cash_flows.append(item)
        time.sleep(0.15)
    result["cash_flows"] = cash_flows

    # ━━━ 8. 估值指标 ━━━
    print(f"[8/10] 估值指标...", flush=True)
    val = mcporter("fintool-company.get_valuation_metrics_daily", keyword=keyword, end_date="2026-02-17")
    result["valuation"] = safe_first(val) if val else {}
    time.sleep(0.2)

    # ━━━ 9. 实时行情 ━━━
    print(f"[9/10] 实时行情...", flush=True)
    snap = mcporter("fintool-quote.get_snapshot", keyword=keyword)
    if snap:
        result["snapshot"] = snap
    else:
        result["snapshot"] = {}
    time.sleep(0.2)

    # ━━━ 10. 股东信息 ━━━
    print(f"[10/10] 股东信息...", flush=True)
    holders = mcporter("fintool-company.get_share_holder_info", keyword=keyword)
    if isinstance(holders, list):
        result["top_holders"] = holders[:10]
    else:
        result["top_holders"] = []

    # ━━━ 同行业公司列表 ━━━
    if result.get("industry", {}).get("second_industry_name"):
        ind_name = result["industry"]["second_industry_name"].rstrip("ⅡⅢⅠ").strip()
        print(f"[+] 同行业板块: {ind_name}", flush=True)
        peers_data = mcporter("fintool-plates.get_plate_stocks", keyword=ind_name)
        if isinstance(peers_data, dict) and "stocks" in peers_data:
            stocks = peers_data["stocks"]
            # 取前10，按市值排序（如果有）
            result["industry_peers"] = [
                {
                    "code": s.get("security_code"),
                    "name": s.get("security_name", "").strip(),
                    "price": s.get("last_price"),
                    "change": s.get("price_change_rate"),
                    "market_cap": s.get("market_value"),
                    "pe": s.get("pe_ratio"),
                }
                for s in stocks[:15]
            ]
        else:
            result["industry_peers"] = []

    return result


def main():
    if len(sys.argv) < 2:
        print("用法: python3 fetch_company_data.py <公司名或代码> [--peers 可比公司1,可比公司2]")
        sys.exit(1)

    keyword = sys.argv[1]
    print(f"━━━ 采集 {keyword} 财务数据 ━━━", flush=True)

    data = fetch_company_data(keyword)

    # 确定输出文件名
    code = data.get("code", data.get("name", keyword))
    name = data.get("name", keyword)
    # 安全文件名
    safe_name = code.replace("/", "_").replace(" ", "_")
    out_path = f"/tmp/buffett_analysis_{safe_name}.json"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n━━━ 完成 ━━━")
    print(f"公司: {name} ({code})")
    print(f"利润表: {len(data['income_statements'])} 期")
    print(f"资产负债表: {len(data['balance_sheets'])} 期")
    print(f"现金流量表: {len(data['cash_flows'])} 期")
    print(f"财务指标: {len(data['financial_metrics'])} 期")
    print(f"同行业: {len(data.get('industry_peers', []))} 家")
    if data["errors"]:
        print(f"⚠️ 错误: {data['errors']}")
    print(f"输出: {out_path}")


if __name__ == "__main__":
    main()
