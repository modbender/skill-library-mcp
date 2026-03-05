#!/usr/bin/env python3
"""
Stock Price Query Script
查询 A 股（沪深）、港股、美股的实时行情数据。
使用腾讯财经 API (qt.gtimg.cn) 获取数据，无需 API Key，无需特殊 Header。

用法:
    python3 stock_query.py <stock_code> [market]

参数:
    stock_code: 股票代码，如 600519, AAPL, 00700
    market:     可选，市场标识 (sh/sz/hk/us)，不提供则自动识别

示例:
    python3 stock_query.py 600519
    python3 stock_query.py 600519 sh
    python3 stock_query.py AAPL us
    python3 stock_query.py 00700 hk
"""

import sys
import json
import re
import time
import urllib.request
import urllib.error

# 输入校验正则：股票代码只允许字母和数字，最长 10 字符
VALID_CODE_PATTERN = re.compile(r'^[A-Za-z0-9]{1,10}$')
# 市场标识白名单
VALID_MARKETS = {"sh", "sz", "hk", "us"}


def validate_input(code: str, market: str | None) -> str | None:
    """校验输入参数，防止注入攻击。返回 None 表示合法，否则返回错误信息。"""
    if not VALID_CODE_PATTERN.match(code):
        return (
            f"非法的股票代码 '{code}'。"
            "股票代码仅允许字母和数字，长度 1-10 位。"
        )
    if market is not None and market not in VALID_MARKETS:
        return (
            f"非法的市场标识 '{market}'。"
            f"仅支持: {', '.join(sorted(VALID_MARKETS))}。"
        )
    return None


def detect_market(code: str) -> str:
    """根据股票代码自动识别市场"""
    code = code.strip().upper()

    # 已带市场前缀
    if code.startswith("SH"):
        return "sh"
    if code.startswith("SZ"):
        return "sz"
    if code.startswith("HK"):
        return "hk"

    # 纯英文字母 -> 美股
    if re.match(r'^[A-Z]{1,5}$', code):
        return "us"

    # 纯数字判断
    digits = re.sub(r'[^0-9]', '', code)
    if len(digits) == 6:
        if digits.startswith('6'):
            return "sh"
        elif digits.startswith(('0', '3')):
            return "sz"
        else:
            return "sh"
    elif 1 <= len(digits) <= 5:
        return "hk"

    return "unknown"


def clean_code(code: str) -> str:
    """清理股票代码，去除市场前缀"""
    code = code.strip().upper()
    for prefix in ["SH", "SZ", "HK"]:
        if code.startswith(prefix):
            return code[len(prefix):]
    return code


def build_tencent_symbol(code: str, market: str) -> str:
    """构建腾讯财经 API 的股票符号"""
    code = clean_code(code)
    if market == "sh":
        return f"sh{code}"
    elif market == "sz":
        return f"sz{code}"
    elif market == "hk":
        return f"hk{code.zfill(5)}"
    elif market == "us":
        return f"us{code.upper()}"
    return code


def parse_stock(raw: str, code: str, market: str) -> dict:
    """解析腾讯财经 API 返回的行情数据（各市场格式统一）

    通用字段索引:
    [1]:  名称
    [2]:  代码
    [3]:  当前价格
    [4]:  昨收
    [5]:  今开
    [6]:  成交量（手/股）
    [30]: 时间
    [31]: 涨跌额
    [32]: 涨跌幅(%)
    [33]: 最高
    [34]: 最低
    [37]: 成交额
    """
    parts = raw.split("~")
    if len(parts) < 35:
        return {"status": "error", "message": "数据解析失败，返回数据不完整"}

    name = parts[1].strip()
    if not name:
        return {
            "status": "error",
            "message": f"未找到股票 {clean_code(code)}，请检查代码是否正确",
        }

    current_price = float(parts[3]) if parts[3] else 0
    prev_close = float(parts[4]) if parts[4] else 0
    open_price = float(parts[5]) if parts[5] else 0
    volume_raw = parts[6].strip() if parts[6] else "0"
    volume = int(float(volume_raw))

    time_str = parts[30].strip() if len(parts) > 30 and parts[30] else ""
    change = float(parts[31]) if len(parts) > 31 and parts[31] else 0
    change_pct = float(parts[32]) if len(parts) > 32 and parts[32] else 0
    high = float(parts[33]) if len(parts) > 33 and parts[33] else 0
    low = float(parts[34]) if len(parts) > 34 and parts[34] else 0
    amount_raw = parts[37].strip() if len(parts) > 37 and parts[37] else "0"
    amount = float(amount_raw) if amount_raw else 0

    # A 股成交量单位为手（1 手 = 100 股），成交额单位为万元
    if market in ("sh", "sz"):
        volume = volume * 100
        amount = amount * 10000

    display_code = clean_code(code)
    if market == "hk":
        display_code = display_code.zfill(5)
    elif market == "us":
        display_code = display_code.upper()

    return {
        "code": display_code,
        "name": name,
        "market": market,
        "current_price": current_price,
        "change": change,
        "change_percent": change_pct,
        "open": open_price,
        "high": high,
        "low": low,
        "prev_close": prev_close,
        "volume": volume,
        "amount": amount,
        "time": time_str,
        "status": "success",
    }


def fetch_stock(code: str, market: str, retry: bool = True) -> dict:
    """获取股票实时行情"""
    symbol = build_tencent_symbol(code, market)
    url = f"https://qt.gtimg.cn/q={symbol}"

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("gbk", errors="ignore")

        # 检查返回数据是否为空
        if '=""' in raw or not raw.strip():
            return {
                "status": "error",
                "message": f"未找到股票 {clean_code(code)}，请检查代码是否正确",
            }

        return parse_stock(raw, code, market)

    except urllib.error.HTTPError as e:
        if e.code == 429 and retry:
            time.sleep(1)
            return fetch_stock(code, market, retry=False)
        return {"status": "error", "message": f"HTTP 请求失败: {e.code} {e.reason}"}
    except urllib.error.URLError as e:
        return {"status": "error", "message": f"网络请求失败: {str(e.reason)}"}
    except Exception as e:
        return {"status": "error", "message": f"查询异常: {str(e)}"}


def main():
    if len(sys.argv) < 2:
        print(json.dumps(
            {"status": "error", "message": "用法: python3 stock_query.py <stock_code> [market]"},
            ensure_ascii=False,
        ))
        sys.exit(1)

    code = sys.argv[1].strip()
    market = sys.argv[2].strip().lower() if len(sys.argv) > 2 else None

    # 输入安全校验：仅允许字母、数字和白名单市场标识
    validation_error = validate_input(code, market)
    if validation_error:
        print(json.dumps(
            {"status": "error", "message": validation_error},
            ensure_ascii=False,
        ))
        sys.exit(1)

    if not market:
        market = detect_market(code)

    if market == "unknown":
        print(json.dumps(
            {
                "status": "error",
                "message": "无法识别该股票代码，请确认后重试。"
                           "支持 A 股（6 位数字）、港股（5 位数字）、美股（英文字母）。",
            },
            ensure_ascii=False,
        ))
        sys.exit(1)

    result = fetch_stock(code, market)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if result.get("status") != "success":
        sys.exit(1)


if __name__ == "__main__":
    main()
