#!/usr/bin/env python3
"""
A股基础数据一键获取脚本
用法: python3 fetch_stock_data.py <股票代码>
示例: python3 fetch_stock_data.py 300442
      python3 fetch_stock_data.py 600519
"""

import sys
import json
import subprocess

def install_if_missing(pkg):
    try:
        __import__(pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

install_if_missing("akshare")
install_if_missing("pandas")

import akshare as ak
import pandas as pd

def fetch_stock_data(symbol: str) -> dict:
    result = {"symbol": symbol, "errors": []}

    # 1. 基本信息
    try:
        info = ak.stock_individual_info_em(symbol=symbol)
        result["basic_info"] = info.to_dict(orient="records")
    except Exception as e:
        result["errors"].append(f"basic_info: {e}")

    # 2. 利润表（最近8期）
    try:
        income = ak.stock_profit_sheet_by_report_em(symbol=symbol)
        result["income_statement"] = income.head(8).to_dict(orient="records")
    except Exception as e:
        result["errors"].append(f"income_statement: {e}")

    # 3. 资产负债表
    try:
        balance = ak.stock_balance_sheet_by_report_em(symbol=symbol)
        result["balance_sheet"] = balance.head(4).to_dict(orient="records")
    except Exception as e:
        result["errors"].append(f"balance_sheet: {e}")

    # 4. 现金流量表
    try:
        cashflow = ak.stock_cash_flow_sheet_by_report_em(symbol=symbol)
        result["cash_flow"] = cashflow.head(4).to_dict(orient="records")
    except Exception as e:
        result["errors"].append(f"cash_flow: {e}")

    # 5. 财务指标（ROE/毛利率/净利润率）
    try:
        indicator = ak.stock_financial_analysis_indicator(symbol=symbol)
        result["financial_indicators"] = indicator.head(8).to_dict(orient="records")
    except Exception as e:
        result["errors"].append(f"financial_indicators: {e}")

    # 6. 大股东持仓
    try:
        holders = ak.stock_main_sh_holders_date_em(symbol=symbol)
        result["major_holders"] = holders.head(10).to_dict(orient="records")
    except Exception as e:
        try:
            holders = ak.stock_main_sz_holders_date_em(symbol=symbol)
            result["major_holders"] = holders.head(10).to_dict(orient="records")
        except Exception as e2:
            result["errors"].append(f"major_holders: {e2}")

    # 7. 历史行情（近90天）
    try:
        hist = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq")
        result["price_history_90d"] = hist.tail(90).to_dict(orient="records")
    except Exception as e:
        result["errors"].append(f"price_history: {e}")

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 fetch_stock_data.py <股票代码>")
        print("示例: python3 fetch_stock_data.py 300442")
        sys.exit(1)

    symbol = sys.argv[1].strip().lstrip("sz").lstrip("sh").lstrip("SZ").lstrip("SH")
    print(f"正在获取 {symbol} 的数据...", file=sys.stderr)

    data = fetch_stock_data(symbol)

    # 输出JSON（供子智能体读取）
    output_file = f"/tmp/stock_{symbol}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, default=str, indent=2)

    print(f"数据已保存至 {output_file}", file=sys.stderr)
    print(json.dumps({"file": output_file, "symbol": symbol, "errors": data["errors"]}, ensure_ascii=False))
