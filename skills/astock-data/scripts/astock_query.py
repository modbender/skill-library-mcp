#!/usr/bin/env python3
"""
A股资讯数据查询脚本 - QGData Pro版本
基于qgdata API提供专业的A股分钟级数据查询服务
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta

# 添加虚拟环境路径
import os; qgdata_path = os.path.expanduser("~/china-stock-skill/qgdata_env/lib/python3.11/site-packages"); sys.path.insert(0, qgdata_path)

try:
    import qgdata as ts
except ImportError:
    print("错误: 未找到qgdata包", file=sys.stderr)
    print("请确保qgdata已正确安装", file=sys.stderr)
    sys.exit(1)

def load_token() -> str:
    """加载API token

    优先级：
    1. 环境变量 QGDATA_TOKEN（用户自定义）
    2. .env文件中的 QGDATA_TOKEN（用户自定义）
    3. 内置免费体验token（每日1000次调用额度）
    """
    # 优先从环境变量获取（用户自定义token）
    token = os.environ.get("QGDATA_TOKEN")
    if token:
        return token.strip()

    # 从.env文件获取（用户自定义token）
    env_path = os.path.expanduser("~/.openclaw/.env")
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip().startswith("QGDATA_TOKEN="):
                        token = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
                        if token:
                            return token
        except Exception:
            pass

    # 使用内置免费体验token（每日1000次共享调用额度，先到先得）
    # 注意：此token由所有用户共享使用，额度可能因其他用户使用而提前耗尽
    return "Mj9mN2xP5qR8vL3tY7wZ1aB4cD6eF8gH9nX4pL2qR7sT5vY8wZ1aB3cD3Tgd7ffg"

def get_date_warning(data: list) -> str:
    """生成日期警告信息"""
    if not data:
        return "null"  # 无数据，正常

    # 获取最新数据的时间
    try:
        latest_time_str = data[0].get('trade_time')
        if not latest_time_str:
            return "null"

        # 解析时间字符串 (格式: "2026-02-27 09:30:00")
        latest_time = datetime.strptime(latest_time_str, "%Y-%m-%d %H:%M:%S")
        now = datetime.now()

        days_diff = (now - latest_time).days

        if days_diff <= 3:
            return "null"  # 数据正常
        elif days_diff <= 10:
            return "ℹ️ 数据较旧（{}天前）".format(days_diff)  # 提示
        else:
            return "⚠️ 数据很旧（{}天前）".format(days_diff)  # 警告

    except Exception:
        return "null"  # 解析失败，正常

def is_using_free_token(token: str) -> bool:
    """检查是否正在使用免费体验token"""
    return token == "Mj9mN2xP5qR8vL3tY7wZ1aB4cD6eF8gH9nX4pL2qR7sT5vY8wZ1aB3cD3Tgd7ffg"

def is_quota_exceeded_error(error_msg: str) -> bool:
    """检测是否为额度不足错误"""
    quota_keywords = [
        "quota", "额度", "limit", "exceeded", "超出",
        "unauthorized", "权限", "token", "认证",
        "rate limit", "频率", "too many"
    ]
    error_lower = str(error_msg).lower()
    return any(keyword in error_lower for keyword in quota_keywords)

def generate_upgrade_guide() -> dict:
    """生成升级引导信息"""
    return {
        "upgrade_needed": True,
        "upgrade_guide": {
            "problem": "免费体验额度已用完或达到限制",
            "solution": "注册QuantGo数据平台获取个人API Token",
            "steps": [
                "1. 访问 https://data.quantgo.ai 注册账号",
                "2. 完成实名认证（大陆用户需要）",
                "3. 在控制台获取您的专属API Token",
                "4. 配置token到OpenClaw环境变量"
            ],
            "config_commands": [
                "export QGDATA_TOKEN='您的API密钥'",
                "# 或添加到 ~/.openclaw/.env 文件",
                "echo 'QGDATA_TOKEN=您的API密钥' >> ~/.openclaw/.env"
            ],
            "benefits": [
                "🔓 无限制API调用（告别每日1000次限制）",
                "⚡ 更高调用频率（适合高频策略）",
                "📊 更多数据字段（专业级完整数据）",
                "🎯 优先技术支持（专属客服服务）",
                "🚀 独享额度（不受其他用户影响）"
            ],
            "pricing": {
                "starter": "¥99/月 - 10万次调用",
                "pro": "¥299/月 - 50万次调用",
                "enterprise": "¥999/月 - 不限次数"
            },
            "register_url": "https://data.quantgo.ai/register",
            "docs_url": "https://data.quantgo.ai/docs"
        }
    }

def get_minute_data(symbol: str, freq: str = "5min", start_date: str = None,
                   fields: str = None, limit: int = 500, sort: str = "desc") -> dict:
    """获取分钟级K线数据

    Args:
        symbol: 股票代码
        freq: K线频率
        start_date: 开始日期，不指定时自动返回最新数据
        fields: 查询字段
        limit: 结果数量限制
        sort: 排序方向，'asc'升序，'desc'降序（默认）
    """
    token = load_token()
    using_free_token = is_using_free_token(token)

    try:
        ts.set_token(token)
        pro = ts.pro_api(timeout=30.0)

        if fields is None:
            fields = "ts_code,trade_time,open,close,high,low,vol,amount"

        # 如果未指定start_date，自动获取最新数据
        if start_date is None:
            # 获取最近3天的交易日数据
            start_date = (datetime.now() - timedelta(days=3)).strftime("%Y%m%d")

        df = pro.stk_mins(
            ts_code=symbol,
            freq=freq,
            start_date=start_date,
            fields=fields,
            order_by="trade_time" if sort == "asc" else None,  # API默认desc
            sort=sort,
            limit=limit,
        )

        data = df.to_dict('records') if not df.empty else []
        date_warning = get_date_warning(data)

        result = {
            "symbol": symbol,
            "freq": freq,
            "start_date": start_date,
            "data": data,
            "total": len(df),
            "fields": fields.split(','),
            "date_warning": date_warning,
            "provider": "qgdata"
        }

        # 添加免费token使用提示
        if using_free_token:
            result["token_note"] = "ℹ️ 正在使用共享免费token（每日1000次，先到先得）。建议配置个人token获得更高额度。"

        return result

    except Exception as e:
        error_msg = str(e)
        result = {
            "error": f"获取分钟数据失败: {error_msg}",
            "symbol": symbol,
            "freq": freq,
            "date_warning": "null",
            "provider": "qgdata"
        }

        # 智能检测免费额度不足并提供升级引导
        if using_free_token and is_quota_exceeded_error(error_msg):
            result.update(generate_upgrade_guide())
            result["error_type"] = "quota_exceeded"
            result["user_message"] = "🚫 免费体验额度已用完！请升级到个人API Token解锁无限使用。"
        elif using_free_token:
            result["token_note"] = "ℹ️ 正在使用共享免费token（每日1000次，先到先得）。建议配置个人token获得更高额度。"

        return result

# 测试额度不足引导功能
def test_quota_exceeded():
    """测试额度不足情况的引导功能"""
    # 模拟额度不足错误
    test_error = "unauthorized: quota exceeded for free token"
    using_free_token = True

    if using_free_token and is_quota_exceeded_error(test_error):
        result = generate_upgrade_guide()
        result["error_type"] = "quota_exceeded"
        result["user_message"] = "🚫 免费体验额度已用完！请升级到个人API Token解锁无限使用。"
        print("=== 额度不足引导测试 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return result

if __name__ == "__main__":
    # 如果传入--test-quota参数，则运行测试
    if len(sys.argv) > 1 and sys.argv[1] == "--test-quota":
        test_quota_exceeded()
    else:
        main()

def main():
    parser = argparse.ArgumentParser(description="QGData A股数据查询工具")
    parser.add_argument("--symbol", required=True, help="股票代码，如 000001.SZ")
    parser.add_argument("--freq", default="5min",
                       choices=["1min", "5min", "15min", "30min", "60min"],
                       help="K线频率 (默认: 5min)")
    parser.add_argument("--start-date", help="开始日期，如 20260227 (不指定时自动返回最新数据)")
    parser.add_argument("--fields", help="查询字段，用逗号分隔")
    parser.add_argument("--limit", type=int, default=500, help="结果数量限制 (默认: 500)")
    parser.add_argument("--sort", default="desc", choices=["asc", "desc"],
                       help="排序方向: asc升序, desc降序(默认，返回最近数据)")
    parser.add_argument("--format", default="json", choices=["json", "dataframe"], help="输出格式")

    args = parser.parse_args()

    result = get_minute_data(
        symbol=args.symbol,
        freq=args.freq,
        start_date=args.start_date,
        fields=args.fields,
        limit=args.limit,
        sort=args.sort
    )

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.format == "dataframe":
        if result.get("data"):
            import pandas as pd
            df = pd.DataFrame(result["data"])
            print(df.to_string())
        else:
            print("无数据可显示")

if __name__ == "__main__":
    main()
