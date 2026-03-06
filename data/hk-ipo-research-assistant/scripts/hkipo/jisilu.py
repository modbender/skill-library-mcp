"""集思录港股打新数据源适配器。

数据源: https://www.jisilu.cn/data/new_stock/hkipo/
返回纯数据字典/列表，不做评分或判断。

注意：部分字段（如 issue_pe_range, jsl_first_incr_rt 等）需要集思录会员才能查看，
非会员返回 HTML 链接形式，本模块会将其处理为 None。
"""

import re
import sys
import time
from typing import Any

import httpx

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
API_URL = "https://www.jisilu.cn/data/new_stock/hkipo/"


def _is_member_locked(value: Any) -> bool:
    """检查字段是否被会员锁定。"""
    if value is None:
        return False
    if isinstance(value, str) and ("会员" in value or "/setting/member/" in value):
        return True
    return False


def _clean_value(value: Any) -> Any:
    """清理字段值，会员锁定的返回 None。"""
    if value is None or value == "":
        return None
    if _is_member_locked(value):
        return None
    return value


def _parse_float(value: Any) -> float | None:
    """解析浮点数，失败返回 None。"""
    if value is None:
        return None
    if _is_member_locked(value):
        return None
    try:
        # 处理类似 "2886.00" 的字符串
        return float(str(value).replace(",", ""))
    except (ValueError, TypeError):
        return None


def _parse_date(value: str | None) -> str | None:
    """解析日期字段，返回 YYYY-MM-DD 格式或原样返回。"""
    if not value:
        return None
    # 如果已经是 YYYY-MM-DD 格式
    if re.match(r"^\d{4}-\d{2}-\d{2}$", value):
        return value
    return None


def _normalize_stock(raw: dict) -> dict:
    """将集思录原始字段标准化为统一命名。
    
    Args:
        raw: 集思录 API 返回的 cell 字典
        
    Returns:
        标准化后的字典
    """
    return {
        # 基本信息
        "code": raw.get("stock_cd"),
        "name": raw.get("stock_nm"),
        "market": raw.get("market"),
        
        # 日期（使用 ISO 格式）
        "apply_date": _parse_date(raw.get("apply_dt2")),
        "apply_end_date": _parse_date(raw.get("apply_end_dt2")),
        "listing_date": _parse_date(raw.get("list_dt2")),
        "gray_trade_date": _parse_date(raw.get("gray_dt")),
        
        # 日期（显示格式）
        "apply_date_display": _clean_value(raw.get("apply_dt")),
        "apply_end_date_display": _clean_value(raw.get("apply_end_dt")),
        "listing_date_display": _clean_value(raw.get("list_dt")),
        
        # 价格信息
        "price_range": _clean_value(raw.get("price_range")),
        "issue_price": _parse_float(raw.get("issue_price")),
        "issue_pe_range": _clean_value(raw.get("issue_pe_range")),  # 会员字段
        
        # 费用与规模
        "entry_fee": _parse_float(raw.get("single_draw_money")),  # 单签认购金额
        "total_shares": _clean_value(raw.get("total_shares")),  # 总发行量（亿股）
        "raise_money": _clean_value(raw.get("raise_money")),  # 募资金额（亿港元）
        "market_cap": _clean_value(raw.get("total_values")),  # 总市值（亿港元）
        
        # 中签与回报
        "lucky_draw_rate": _parse_float(raw.get("lucky_draw_rt")),  # 中签率
        "oversubscription_rate": _clean_value(raw.get("above_rt")),  # 超额认购倍数（会员字段）
        "jsl_oversubscription_rate": _clean_value(raw.get("jsl_above_rt")),  # 集思录预测超购（会员）
        
        # 涨跌幅
        "gray_return": _parse_float(raw.get("gray_incr_rt")),  # 暗盘涨幅 %
        "gray_return_alt": _parse_float(raw.get("gray_incr_rt2")),  # 暗盘涨幅2 %
        "first_day_return": _parse_float(raw.get("first_incr_rt")),  # 首日涨幅 %
        "total_return": _parse_float(raw.get("total_incr_rt")),  # 累计涨幅 %
        "jsl_first_day_return": _clean_value(raw.get("jsl_first_incr_rt")),  # 集思录预测首日涨幅（会员）
        
        # 绿鞋
        "greenshoe_rate": _clean_value(raw.get("green_rt")),  # 绿鞋比例（会员字段）
        "greenshoe_amount": _parse_float(raw.get("green_amount")),  # 绿鞋金额
        
        # 承销商与参考
        "underwriter": _clean_value(raw.get("underwriter")),
        "reference_company": _clean_value(raw.get("ref_company")),  # 参考公司（会员字段）
        
        # 集思录分析
        "jsl_advice": _clean_value(raw.get("jsl_advise")),  # 集思录建议
        "yx_rate": raw.get("yx_rate"),  # 一鱼多吃比例
        
        # 状态
        "status": raw.get("status_cd"),  # N=新股申购中, L=已上市
        "ipo_result": _clean_value(raw.get("iporesult")),  # 中签结果
        "is_applying": raw.get("apply_flg") == 1,
        "is_listed": raw.get("list_flg") == 1,
        
        # 链接
        "prospectus_url": _clean_value(raw.get("prospectus")),
        "notes": _clean_value(raw.get("notes")),
    }


def fetch_jisilu_history(limit: int = 100) -> list[dict]:
    """获取集思录港股打新历史数据。
    
    Args:
        limit: 最大返回条数，默认 100
        
    Returns:
        标准化后的 IPO 数据列表，按申购日期倒序排列
        
    Raises:
        httpx.HTTPError: 网络请求失败时
    """
    for attempt in range(3):
        try:
            resp = httpx.get(API_URL, headers=HEADERS, timeout=20, follow_redirects=True)
            resp.raise_for_status()
            data = resp.json()
            
            rows = data.get("rows", [])
            result = []
            
            for row in rows[:limit]:
                cell = row.get("cell", {})
                if cell:
                    result.append(_normalize_stock(cell))
            
            return result
            
        except (httpx.RemoteProtocolError, httpx.ConnectError, httpx.ReadTimeout) as e:
            if attempt < 2:
                time.sleep(1)
                continue
            raise e
        except Exception as e:
            print(f"集思录数据获取失败: {e}", file=sys.stderr)
            return []
    
    return []


def get_jisilu_stock(code: str) -> dict | None:
    """获取指定股票代码的集思录数据。
    
    Args:
        code: 港股代码（如 "03268" 或 "3268"）
        
    Returns:
        标准化后的股票数据字典，未找到返回 None
    """
    # 规范化股票代码为 5 位
    code = code.zfill(5)
    
    history = fetch_jisilu_history(limit=200)
    for stock in history:
        if stock.get("code") == code:
            return stock
    
    return None


def main(argv=None):
    import argparse
    import json
    
    parser = argparse.ArgumentParser(
        description="集思录港股打新历史数据",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python jisilu.py list                    # 最近 20 条
  python jisilu.py list --limit 50         # 最近 50 条
  python jisilu.py list --sponsor 招银国际  # 按保荐人筛选
  python jisilu.py detail 02692            # 单只详情
  python jisilu.py list --json             # JSON 输出
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # list 命令
    list_parser = subparsers.add_parser("list", help="历史 IPO 列表")
    list_parser.add_argument("--limit", type=int, default=20, help="返回数量")
    list_parser.add_argument("--sponsor", help="按保荐人筛选")
    list_parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    
    # detail 命令
    detail_parser = subparsers.add_parser("detail", help="单只股票详情")
    detail_parser.add_argument("code", help="股票代码")
    detail_parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    
    args = parser.parse_args(argv)
    
    if args.command == "list":
        history = fetch_jisilu_history(limit=args.limit)
        
        # 按保荐人筛选
        if args.sponsor:
            history = [h for h in history if args.sponsor in (h.get("underwriter") or "")]
        
        if args.json:
            print(json.dumps(history, ensure_ascii=False, indent=2))
        else:
            print(f"{'代码':<8} {'名称':<12} {'保荐人':<12} {'入场费':>8} {'首日涨幅':>10} {'超购倍数':>10}")
            print("-" * 70)
            for ipo in history:
                code = ipo.get('code', '')
                name = ipo.get('name', '')[:10]
                sponsor = (ipo.get('underwriter') or '')[:10]
                entry = ipo.get('entry_fee')
                entry_str = f"{entry:.0f}" if entry else "-"
                ret = ipo.get('first_day_return')
                ret_str = f"{ret:+.1f}%" if ret else "-"
                oversub = ipo.get('oversubscription_rate')
                oversub_str = f"{oversub}x" if oversub else "-"
                print(f"{code:<8} {name:<12} {sponsor:<12} {entry_str:>8} {ret_str:>10} {oversub_str:>10}")
    
    elif args.command == "detail":
        stock = get_jisilu_stock(args.code)
        if stock:
            if args.json:
                print(json.dumps(stock, ensure_ascii=False, indent=2))
            else:
                print(f"股票: {stock['code']} {stock['name']}")
                print(f"保荐人: {stock.get('underwriter', '-')}")
                print(f"入场费: {stock.get('entry_fee', '-')} HKD")
                print(f"发行价: {stock.get('issue_price', '-')} HKD")
                print(f"超购倍数: {stock.get('oversubscription_rate', '-')}x")
                print(f"首日涨幅: {stock.get('first_day_return', '-')}%")
                print(f"暗盘涨幅: {stock.get('gray_market_return', '-')}%")
                print(f"上市日期: {stock.get('listing_date', '-')}")
        else:
            print(f"未找到: {args.code}")
            sys.exit(1)


if __name__ == "__main__":
    main()
