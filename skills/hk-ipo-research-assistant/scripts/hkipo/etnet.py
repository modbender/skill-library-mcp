"""
etnet 经济通保荐人数据源

抓取 etnet 港股 IPO 保荐人表现数据。
数据来源: https://www.etnet.com.hk/www/tc/stocks/ipo-sponsor-performance.php
"""

import re
from dataclasses import dataclass
from typing import Optional

import httpx
from bs4 import BeautifulSoup


# 常量
ETNET_SPONSOR_URL = "https://www.etnet.com.hk/www/tc/stocks/ipo-sponsor-performance.php"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


@dataclass
class SponsorStats:
    """保荐人统计数据

    Attributes:
        sponsor_name: 保荐人名称
        sponsor_id: etnet 内部 ID (用于详情页链接)
        ipo_count: 保荐数目
        first_day_up_rate: 首日上升机率 (百分比数值, 如 72.00)
        first_day_up_count: 首日上升数目
        first_day_down_count: 首日下跌数目
        first_day_unchanged_count: 首日不变数目
        avg_first_day_change: 平均首日升跌 (百分比数值, 如 +39.34)
        best_stock: 最佳表现股票 (代码+名称+涨幅)
        worst_stock: 最差表现股票 (代码+名称+涨幅)
    """

    sponsor_name: str
    sponsor_id: Optional[int]
    ipo_count: int
    first_day_up_rate: float
    first_day_up_count: int
    first_day_down_count: int
    first_day_unchanged_count: int
    avg_first_day_change: float
    best_stock: Optional[dict]  # {"code": "02635", "name": "諾比侃", "change": "+363.750%"}
    worst_stock: Optional[dict]

    def to_dict(self) -> dict:
        """转换为字典，用于 JSON 序列化"""
        return {
            "sponsor_name": self.sponsor_name,
            "sponsor_id": self.sponsor_id,
            "ipo_count": self.ipo_count,
            "first_day_up_rate": self.first_day_up_rate,
            "first_day_up_count": self.first_day_up_count,
            "first_day_down_count": self.first_day_down_count,
            "first_day_unchanged_count": self.first_day_unchanged_count,
            "avg_first_day_change": self.avg_first_day_change,
            "best_stock": self.best_stock,
            "worst_stock": self.worst_stock,
        }


def _parse_count(text: str) -> int:
    """解析数目字符串 (如 '50間' -> 50)"""
    match = re.search(r"(\d+)", text)
    return int(match.group(1)) if match else 0


def _parse_percentage(text: str) -> float:
    """解析百分比字符串 (如 '72.00%' 或 '+39.34%' -> 72.00 或 39.34)"""
    match = re.search(r"([+-]?\d+\.?\d*)", text)
    return float(match.group(1)) if match else 0.0


def _parse_stock_info(text: str) -> Optional[dict]:
    """解析股票信息 (如 '02635 諾比侃<br> (+363.750%)' -> dict)"""
    if not text or text.strip() == "":
        return None
    
    # 处理 HTML 换行和空格
    text = text.replace("\n", " ").replace("<br>", " ").replace("<br/>", " ")
    text = re.sub(r"\s+", " ", text).strip()
    
    # 匹配: 代码 名称 (涨跌幅)
    match = re.match(r"(\d{5})\s+(.+?)\s*\(([+-]?\d+\.?\d*%)\)", text)
    if match:
        return {
            "code": match.group(1),
            "name": match.group(2).strip(),
            "change": match.group(3),
        }
    return None


def _extract_sponsor_id(href: str) -> Optional[int]:
    """从链接中提取保荐人 ID"""
    match = re.search(r"id=(\d+)", href)
    return int(match.group(1)) if match else None


def _fetch_page(page: int = 1) -> str:
    """获取指定页面的 HTML 内容"""
    url = ETNET_SPONSOR_URL
    if page > 1:
        url = f"{ETNET_SPONSOR_URL}?page={page}"
    
    headers = {"User-Agent": USER_AGENT}
    response = httpx.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text


def _parse_sponsor_row(row) -> Optional[SponsorStats]:
    """解析表格中的一行数据"""
    cells = row.find_all("td")
    if len(cells) < 9:
        return None
    
    # 第一列: 保荐人名称和链接
    name_cell = cells[0]
    link = name_cell.find("a")
    if not link:
        return None
    
    sponsor_name = link.get_text(strip=True)
    sponsor_id = _extract_sponsor_id(link.get("href", ""))
    
    # 第二列: 保荐数目
    ipo_count = _parse_count(cells[1].get_text(strip=True))
    
    # 第三列: 首日上升机率
    first_day_up_rate = _parse_percentage(cells[2].get_text(strip=True))
    
    # 第四列: 首日上升数目
    first_day_up_count = _parse_count(cells[3].get_text(strip=True))
    
    # 第五列: 首日下跌数目
    first_day_down_count = _parse_count(cells[4].get_text(strip=True))
    
    # 第六列: 首日不变数目
    first_day_unchanged_count = _parse_count(cells[5].get_text(strip=True))
    
    # 第七列: 平均首日升跌
    avg_first_day_change = _parse_percentage(cells[6].get_text(strip=True))
    
    # 第八列: 最佳表现股票
    best_stock_text = cells[7].get_text(" ", strip=True)
    best_stock = _parse_stock_info(best_stock_text)
    
    # 第九列: 最差表现股票
    worst_stock_text = cells[8].get_text(" ", strip=True)
    worst_stock = _parse_stock_info(worst_stock_text)
    
    return SponsorStats(
        sponsor_name=sponsor_name,
        sponsor_id=sponsor_id,
        ipo_count=ipo_count,
        first_day_up_rate=first_day_up_rate,
        first_day_up_count=first_day_up_count,
        first_day_down_count=first_day_down_count,
        first_day_unchanged_count=first_day_unchanged_count,
        avg_first_day_change=avg_first_day_change,
        best_stock=best_stock,
        worst_stock=worst_stock,
    )


def _get_total_pages(html: str) -> int:
    """获取总页数"""
    soup = BeautifulSoup(html, "html.parser")
    # 查找分页链接
    pagination = soup.select(".pagination a")
    max_page = 1
    for link in pagination:
        href = link.get("href", "")
        match = re.search(r"page=(\d+)", href)
        if match:
            page_num = int(match.group(1))
            max_page = max(max_page, page_num)
    return max_page


def fetch_sponsor_rankings(fetch_all_pages: bool = True) -> list[SponsorStats]:
    """获取所有保荐人排名

    从 etnet 抓取港股 IPO 保荐人表现数据，按保荐数目排序。

    Args:
        fetch_all_pages: 是否抓取所有页面 (默认 True，约 4 页)

    Returns:
        SponsorStats 列表，按保荐数目降序排列

    Raises:
        requests.RequestException: 网络请求失败
    """
    sponsors = []
    
    # 获取第一页并确定总页数
    html = _fetch_page(1)
    total_pages = _get_total_pages(html) if fetch_all_pages else 1
    
    # 解析所有页面
    for page in range(1, total_pages + 1):
        if page > 1:
            html = _fetch_page(page)
        
        soup = BeautifulSoup(html, "html.parser")
        
        # 查找数据行 (class="row")
        rows = soup.select("tr.row")
        
        for row in rows:
            sponsor = _parse_sponsor_row(row)
            if sponsor:
                sponsors.append(sponsor)
    
    return sponsors


def get_sponsor_stats(name: str, sponsors: Optional[list[SponsorStats]] = None) -> Optional[SponsorStats]:
    """按名称模糊查找单个保荐人

    支持常见别名匹配，如:
    - "中金" -> "中國國際金融香港證券有限公司"
    - "CICC" -> "中國國際金融香港證券有限公司"
    - "高盛" -> "高盛(亞洲)有限責任公司"
    - "Morgan Stanley" -> "摩根士丹利亞洲有限公司"

    Args:
        name: 保荐人名称 (支持部分匹配，不区分大小写，支持常见别名)
        sponsors: 可选，已有的保荐人列表 (避免重复请求)

    Returns:
        匹配的 SponsorStats，未找到返回 None
    """
    if sponsors is None:
        sponsors = fetch_sponsor_rankings(fetch_all_pages=True)
    
    name_lower = name.lower()
    
    # 别名映射 (简称 -> 全称关键词)
    aliases = {
        "中金": "中國國際金融",
        "cicc": "中國國際金融",
        "高盛": "高盛",
        "goldman": "高盛",
        "摩根士丹利": "摩根士丹利",
        "morgan stanley": "摩根士丹利",
        "大摩": "摩根士丹利",
        "中信": "中信",
        "citic": "中信",
        "华泰": "華泰",
        "海通": "海通",
        "招银": "招銀",
        "ubs": "UBS",
        "瑞银": "UBS",
    }
    
    # 检查是否有别名匹配
    search_term = aliases.get(name_lower, name)
    
    for sponsor in sponsors:
        if search_term.lower() in sponsor.sponsor_name.lower():
            return sponsor
    
    # 如果别名没匹配到，用原始名称再试一次
    if search_term != name:
        for sponsor in sponsors:
            if name_lower in sponsor.sponsor_name.lower():
                return sponsor
    
    return None


def get_top_sponsors(limit: int = 10) -> list[SponsorStats]:
    """获取保荐数目最多的前 N 个保荐人

    Args:
        limit: 返回数量限制

    Returns:
        SponsorStats 列表
    """
    sponsors = fetch_sponsor_rankings(fetch_all_pages=True)
    return sponsors[:limit]


def get_sponsors_by_up_rate(min_rate: float = 70.0) -> list[SponsorStats]:
    """获取首日上升机率超过指定值的保荐人

    Args:
        min_rate: 最低首日上升机率 (默认 70%)

    Returns:
        SponsorStats 列表，按首日上升机率降序
    """
    sponsors = fetch_sponsor_rankings(fetch_all_pages=True)
    filtered = [s for s in sponsors if s.first_day_up_rate >= min_rate]
    return sorted(filtered, key=lambda x: x.first_day_up_rate, reverse=True)


# CLI 测试
if __name__ == "__main__":
    import json

    print("=== 测试 fetch_sponsor_rankings() ===")
    sponsors = fetch_sponsor_rankings()
    print(f"共获取 {len(sponsors)} 个保荐人\n")

    print("=== 前 5 个保荐人 ===")
    for i, s in enumerate(sponsors[:5], 1):
        print(f"{i}. {s.sponsor_name}")
        print(f"   保荐数目: {s.ipo_count}间, 首日上升率: {s.first_day_up_rate}%")
        print(f"   上升/下跌/不变: {s.first_day_up_count}/{s.first_day_down_count}/{s.first_day_unchanged_count}")
        print(f"   平均首日升跌: {s.avg_first_day_change:+.2f}%")
        if s.best_stock:
            print(f"   最佳: {s.best_stock['code']} {s.best_stock['name']} ({s.best_stock['change']})")
        if s.worst_stock:
            print(f"   最差: {s.worst_stock['code']} {s.worst_stock['name']} ({s.worst_stock['change']})")
        print()

    print("=== 测试 get_sponsor_stats('中金') ===")
    cicc = get_sponsor_stats("中金")
    if cicc:
        print(f"找到: {cicc.sponsor_name}")
        print(f"保荐数目: {cicc.ipo_count}间")
        print(json.dumps(cicc.to_dict(), ensure_ascii=False, indent=2))
    else:
        print("未找到")

    print("\n=== 测试 get_sponsors_by_up_rate(80.0) ===")
    high_rate = get_sponsors_by_up_rate(80.0)
    print(f"首日上升率 >= 80% 的保荐人: {len(high_rate)} 个")
    for s in high_rate[:3]:
        print(f"  - {s.sponsor_name}: {s.first_day_up_rate}%")
