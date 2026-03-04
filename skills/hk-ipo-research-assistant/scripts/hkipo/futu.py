"""
富途 (Futu/Moomoo) 数据源适配器

抓取富途网页端的港股新股数据，包括已上市新股的首日表现、暗盘涨跌幅等。
数据来源: https://www.futunn.com/quote/hk/ipo
"""

import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import httpx


# 常量
FUTU_IPO_URL = "https://www.futunn.com/quote/hk/ipo"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


@dataclass
class FutuListedIPO:
    """富途已上市新股数据结构
    
    Attributes:
        code: 股票代码 (如 "09981")
        name: 股票名称
        ipo_price: 发行价 (港元)
        current_price: 当前价格 (港元)
        first_day_change: 首日涨跌幅 (如 "+2.94%")
        dark_change: 暗盘涨跌幅 (如 "+4.93%")
        total_change: 累计涨跌幅 (相对发行价, 如 "+9.51%")
        listing_date: 上市日期
        market_cap: 市值 (港元)
        industry: 行业
    """
    code: str
    name: str
    ipo_price: Optional[float]
    current_price: Optional[float]
    first_day_change: str
    dark_change: str
    total_change: str
    listing_date: str
    market_cap: str
    industry: str
    
    def to_dict(self) -> dict:
        """转换为字典，用于 JSON 序列化"""
        return {
            "code": self.code,
            "name": self.name,
            "ipo_price": self.ipo_price,
            "current_price": self.current_price,
            "first_day_change": self.first_day_change,
            "dark_change": self.dark_change,
            "total_change": self.total_change,
            "listing_date": self.listing_date,
            "market_cap": self.market_cap,
            "industry": self.industry,
        }


def _parse_price(price_str: str) -> Optional[float]:
    """解析价格字符串为浮点数"""
    if not price_str or price_str == "--":
        return None
    try:
        return float(price_str)
    except (ValueError, TypeError):
        return None


def _timestamp_to_date(timestamp_ms: int) -> str:
    """将毫秒时间戳转换为日期字符串"""
    if not timestamp_ms:
        return ""
    try:
        dt = datetime.fromtimestamp(timestamp_ms / 1000)
        return dt.strftime("%Y-%m-%d")
    except (ValueError, OSError):
        return ""


def fetch_futu_listed_ipos(limit: int = 50) -> list[FutuListedIPO]:
    """获取富途已上市新股列表
    
    从富途网页抓取已上市港股新股数据，包含首日涨幅、暗盘涨幅等关键指标。
    
    Args:
        limit: 返回的最大记录数，默认50条
        
    Returns:
        FutuListedIPO 列表，按上市日期倒序排列
        
    Raises:
        requests.RequestException: 网络请求失败
        ValueError: 页面解析失败
        
    Example:
        >>> ipos = fetch_futu_listed_ipos(limit=10)
        >>> for ipo in ipos:
        ...     print(f"{ipo.code} {ipo.name}: 首日{ipo.first_day_change}, 暗盘{ipo.dark_change}")
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
    }
    
    response = httpx.get(FUTU_IPO_URL, headers=headers, timeout=30)
    response.raise_for_status()
    
    # 从 HTML 中提取 __INITIAL_STATE__ JSON
    pattern = r'__INITIAL_STATE__\s*=\s*(\{.*?\});'
    match = re.search(pattern, response.text, re.DOTALL)
    
    if not match:
        raise ValueError("无法在页面中找到 __INITIAL_STATE__ 数据")
    
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 解析失败: {e}")
    
    # 提取已上市新股列表
    ipo_list = data.get("ipo_finished_list", {}).get("list", [])
    
    if not ipo_list:
        return []
    
    results: list[FutuListedIPO] = []
    
    for item in ipo_list[:limit]:
        # 跳过 ETF (instrumentType=4)
        if item.get("instrumentType") == 4:
            continue
            
        ipo = FutuListedIPO(
            code=item.get("stockCode", ""),
            name=item.get("name", ""),
            ipo_price=_parse_price(item.get("ipoPrice", "")),
            current_price=_parse_price(item.get("price", "")),
            first_day_change=item.get("firstDayPcr", "--"),
            dark_change=item.get("darkChangeRatio", "--"),
            total_change=item.get("ipoPriceChangeRatio", "--"),
            listing_date=_timestamp_to_date(item.get("listingDate", 0)),
            market_cap=item.get("marketVal", "--"),
            industry=item.get("industry", "--"),
        )
        results.append(ipo)
    
    return results


def fetch_futu_recent_performance(days: int = 30) -> list[dict]:
    """获取近期新股表现统计
    
    返回最近上市新股的表现数据，用于分析打新收益。
    
    Args:
        days: 统计最近多少天上市的新股
        
    Returns:
        包含统计信息的字典列表
    """
    ipos = fetch_futu_listed_ipos(limit=100)
    
    cutoff = datetime.now().timestamp() - (days * 86400)
    results = []
    
    for ipo in ipos:
        if not ipo.listing_date:
            continue
        try:
            listing_ts = datetime.strptime(ipo.listing_date, "%Y-%m-%d").timestamp()
            if listing_ts >= cutoff:
                results.append({
                    "code": ipo.code,
                    "name": ipo.name,
                    "listing_date": ipo.listing_date,
                    "ipo_price": ipo.ipo_price,
                    "first_day_change": ipo.first_day_change,
                    "dark_change": ipo.dark_change,
                    "total_change": ipo.total_change,
                })
        except ValueError:
            continue
    
    return results


def main(argv=None):
    """CLI 入口"""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="富途港股新股数据",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python futu.py list                    # 已上市新股列表
  python futu.py list --limit 5          # 限制数量
  python futu.py performance             # 近期表现
  python futu.py performance --days 60   # 近 60 天表现
  python futu.py list --json             # JSON 输出
""",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # list 命令
    list_parser = subparsers.add_parser("list", help="已上市新股列表")
    list_parser.add_argument("--limit", type=int, default=20, help="返回数量 (默认 20)")
    list_parser.add_argument("--json", action="store_true", help="JSON 格式输出")

    # performance 命令
    perf_parser = subparsers.add_parser("performance", help="近期新股表现统计")
    perf_parser.add_argument("--days", type=int, default=30, help="统计天数 (默认 30)")
    perf_parser.add_argument("--json", action="store_true", help="JSON 格式输出")

    args = parser.parse_args(argv)

    try:
        if args.command == "list":
            ipos = fetch_futu_listed_ipos(limit=args.limit)
            if args.json:
                print(json.dumps([ipo.to_dict() for ipo in ipos], ensure_ascii=False, indent=2))
            else:
                print(f"{'代码':<8} {'名称':<12} {'发行价':>8} {'首日涨幅':>10} {'暗盘涨幅':>10} {'累计涨幅':>10} {'上市日期':<12}")
                print("-" * 78)
                for ipo in ipos:
                    price_str = f"{ipo.ipo_price:.2f}" if ipo.ipo_price else "--"
                    print(f"{ipo.code:<8} {ipo.name:<12} {price_str:>8} {ipo.first_day_change:>10} {ipo.dark_change:>10} {ipo.total_change:>10} {ipo.listing_date:<12}")

        elif args.command == "performance":
            results = fetch_futu_recent_performance(days=args.days)
            if args.json:
                print(json.dumps(results, ensure_ascii=False, indent=2))
            else:
                print(f"=== 近 {args.days} 天新股表现 ===\n")
                print(f"{'代码':<8} {'名称':<12} {'发行价':>8} {'首日涨幅':>10} {'暗盘涨幅':>10} {'上市日期':<12}")
                print("-" * 68)
                for r in results:
                    price_str = f"{r['ipo_price']:.2f}" if r['ipo_price'] else "--"
                    print(f"{r['code']:<8} {r['name']:<12} {price_str:>8} {r['first_day_change']:>10} {r['dark_change']:>10} {r['listing_date']:<12}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
