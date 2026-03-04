#!/usr/bin/env python3
"""
A股资讯数据查询脚本 - QGData Pro版本
基于qgdata API提供专业的A股分钟级数据查询服务
"""

import argparse
import json
import os
import sys
from typing import Dict, List, Optional, Any

try:
    import qgdata as ts
except ImportError:
    print("错误: 未安装qgdata包", file=sys.stderr)
    print("请运行: pip install qgdata", file=sys.stderr)
    sys.exit(1)

def load_token() -> Optional[str]:
    """加载API token"""
    # 优先从环境变量获取
    token = os.environ.get("QGDATA_TOKEN")
    if token:
        return token.strip()

    # 从.env文件获取
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

    return None

def init_qgdata() -> Any:
    """初始化qgdata连接"""
    token = load_token()
    if not token:
        raise ValueError("未找到QGDATA_TOKEN。请设置环境变量或在~/.openclaw/.env中配置")

    ts.set_token(token)
    return ts.pro_api(timeout=30.0)

def get_minute_data(symbol: str, freq: str = "5min", start_date: str = None,
                   fields: str = None, order_by: str = "trade_time",
                   sort: str = "asc", limit: int = 500) -> Dict[str, Any]:
    """获取分钟级K线数据"""
    pro = init_qgdata()

    if fields is None:
        fields = "ts_code,trade_time,open,close,high,low,vol,amount"

    try:
        df = pro.stk_mins(
            ts_code=symbol,
            freq=freq,
            start_date=start_date,
            fields=fields,
            order_by=order_by,
            sort=sort,
            limit=limit,
        )

        return {
            "symbol": symbol,
            "freq": freq,
            "start_date": start_date,
            "data": df.to_dict('records') if not df.empty else [],
            "total": len(df),
            "fields": fields.split(','),
            "provider": "qgdata"
        }

    except Exception as e:
        return {
            "error": f"获取分钟数据失败: {str(e)}",
            "symbol": symbol,
            "freq": freq,
            "provider": "qgdata"
        }

def get_realtime_data(symbol: str) -> Dict[str, Any]:
    """获取实时股价数据"""
    try:
        pro = init_qgdata()
        # 这里可以根据实际API添加实时数据查询
        # 暂时返回基本信息
        return {
            "symbol": symbol,
            "message": "实时数据查询功能开发中",
            "note": "分钟级K线数据已支持实时查询",
            "provider": "qgdata"
        }
    except Exception as e:
        return {
            "error": f"获取实时数据失败: {str(e)}",
            "symbol": symbol,
            "provider": "qgdata"
        }

def get_trades_data(symbol: str, limit: int = 10) -> Dict[str, Any]:
    """获取成交明细数据"""
    try:
        pro = init_qgdata()
        # 这里可以根据实际API添加成交明细查询
        # 暂时返回基本信息
        return {
            "symbol": symbol,
            "message": "成交明细查询功能开发中",
            "note": "分钟级K线数据包含成交量信息",
            "limit": limit,
            "provider": "qgdata"
        }
    except Exception as e:
        return {
            "error": f"获取成交明细失败: {str(e)}",
            "symbol": symbol,
            "provider": "qgdata"
        }

def format_output(data: Dict[str, Any], format_type: str = "json") -> None:
    """格式化输出结果"""
    if format_type == "json":
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif format_type == "dataframe":
        if "data" in data and data["data"]:
            import pandas as pd
            df = pd.DataFrame(data["data"])
            print(df.to_string())
        else:
            print("无数据可显示")

def main():
    parser = argparse.ArgumentParser(description="A股资讯数据查询 - QGData Pro版本")
    parser.add_argument("--symbol", required=True, help="股票代码，如 000001.SZ")
    parser.add_argument("--freq", default="5min",
                       choices=["1min", "5min", "15min", "30min", "60min"],
                       help="K线频率 (默认: 5min)")
    parser.add_argument("--start-date", help="开始日期，如 20260227")
    parser.add_argument("--fields", help="查询字段，用逗号分隔")
    parser.add_argument("--order-by", default="trade_time", help="排序字段")
    parser.add_argument("--sort", default="asc", choices=["asc", "desc"], help="排序方向")
    parser.add_argument("--limit", type=int, default=500, help="结果数量限制")
    parser.add_argument("--realtime", action="store_true", help="获取实时数据")
    parser.add_argument("--trades", action="store_true", help="获取成交明细")
    parser.add_argument("--format", default="json", choices=["json", "dataframe"], help="输出格式")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")

    args = parser.parse_args()

    try:
        if args.debug:
            print(f"调试信息: symbol={args.symbol}, freq={args.freq}", file=sys.stderr)

        if args.realtime:
            # 实时数据查询
            result = get_realtime_data(args.symbol)
        elif args.trades:
            # 成交明细查询
            result = get_trades_data(args.symbol, args.limit)
        else:
            # 分钟K线数据查询
            result = get_minute_data(
                symbol=args.symbol,
                freq=args.freq,
                start_date=args.start_date,
                fields=args.fields,
                order_by=args.order_by,
                sort=args.sort,
                limit=args.limit
            )

        format_output(result, args.format)

    except ValueError as e:
        print(f"配置错误: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"查询失败: {e}", file=sys.stderr)
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
