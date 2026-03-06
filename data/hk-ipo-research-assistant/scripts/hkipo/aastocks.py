"""AAStocks IPO 数据源适配器。

数据源: https://www.aastocks.com/tc/stocks/market/ipo/
港股最全面的 IPO 数据网站之一。

主要功能:
- 获取即将上市/已上市的 IPO 列表
- 获取 IPO 详细信息（公司资料、招股资料）
- 获取孖展供应信息（招股期间）
- 获取机构投资者信息
- 获取中签率数据
- 获取暗盘行情（通过 WebSocket）

数据来源：服务端渲染 HTML，需要解析 HTML 提取数据。
返回纯数据字典，不做评分或判断。

注意：
- AAStocks 使用服务端渲染，所有数据嵌入 HTML 页面
- 暗盘实时行情需要 WebSocket 连接
- 部分数据（如孖展）只在招股期间可用
"""

import re
import sys
from typing import Any, Optional

import httpx
from bs4 import BeautifulSoup

# 常量
BASE_URL = "https://www.aastocks.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
}

def _parse_number(text: str) -> float:
    """解析数字，处理逗号分隔"""
    if not text or text == "N/A":
        return 0.0
    try:
        return float(text.replace(",", "").strip())
    except ValueError:
        return 0.0

def _parse_int(text: str) -> int:
    """解析整数"""
    if not text or text == "N/A":
        return 0
    try:
        return int(text.replace(",", "").strip())
    except ValueError:
        return 0

def _extract_text(element) -> str:
    """从 BeautifulSoup 元素提取文本"""
    if element is None:
        return ""
    return element.get_text(strip=True)

def get_upcoming_ipos() -> list[dict]:
    """获取即将上市的 IPO 列表。
    
    Returns:
        IPO 列表，每个元素包含基本信息
    """
    # 使用 upcomingipo 页面，包含 tblGMUpcoming 表格
    url = f"{BASE_URL}/tc/stocks/market/ipo/upcomingipo/company-summary"
    
    try:
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            response = client.get(url, headers=HEADERS)
            response.raise_for_status()
    except httpx.HTTPError as e:
        print(f"Error fetching upcoming IPOs: {e}", file=sys.stderr)
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    ipos = []
    
    # 查找即将上市的 IPO 表格 (tblGMUpcoming)
    table = soup.find("table", id="tblGMUpcoming")
    if not table:
        # 尝试另一个表格
        table = soup.find("table", id="tblUpcoming")
    
    if not table:
        return []
    
    tbody = table.find("tbody")
    if not tbody:
        return []
    
    for row in tbody.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 8:
            continue
        
        # 提取股票代码和名称
        link = cells[1].find("a")
        if not link:
            continue
        
        href = link.get("href", "")
        symbol_match = re.search(r"symbol=(\d+)", href)
        symbol = symbol_match.group(1) if symbol_match else ""
        
        name_tc = link.get_text(strip=True)
        
        # 提取代码
        code_span = cells[1].find("span", class_="cls")
        code_text = _extract_text(code_span)  # 如 "02649.HK"
        
        # 提取行业
        industry_link = cells[2].find("a")
        industry = _extract_text(industry_link) if industry_link else _extract_text(cells[2])
        
        # 提取其他字段
        offer_price = _extract_text(cells[3])
        lot_size = _parse_int(_extract_text(cells[4]))
        entry_fee = _parse_number(_extract_text(cells[5]))
        subscription_deadline = _extract_text(cells[6])
        grey_market_date = _extract_text(cells[7])
        listing_date = _extract_text(cells[8]) if len(cells) > 8 else ""
        
        ipos.append({
            "symbol": symbol,
            "name_tc": name_tc,
            "code": code_text,
            "industry": industry,
            "offer_price_range": offer_price,
            "lot_size": lot_size,
            "entry_fee": entry_fee,
            "subscription_deadline": subscription_deadline,
            "grey_market_date": grey_market_date,
            "listing_date": listing_date,
        })
    
    return ipos

def get_listed_ipos(limit: int = 20) -> list[dict]:
    """获取最近已上市的 IPO 列表。
    
    Args:
        limit: 最大返回数量
    
    Returns:
        已上市 IPO 列表
    """
    url = f"{BASE_URL}/tc/stocks/market/ipo/listedipo.aspx"
    
    try:
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            response = client.get(url, headers=HEADERS)
            response.raise_for_status()
    except httpx.HTTPError as e:
        print(f"Error fetching listed IPOs: {e}", file=sys.stderr)
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    ipos = []
    
    # 查找已上市 IPO 表格
    table = soup.find("table", id="tblListedIPO")
    if not table:
        # 尝试通用选择器
        tables = soup.find_all("table", class_="ns2")
        table = tables[0] if tables else None
    
    if not table:
        return []
    
    tbody = table.find("tbody")
    if not tbody:
        return []
    
    for row in tbody.find_all("tr")[:limit]:
        cells = row.find_all("td")
        if len(cells) < 5:
            continue
        
        # 提取股票信息
        link = cells[0].find("a") or cells[1].find("a")
        if not link:
            continue
        
        href = link.get("href", "")
        symbol_match = re.search(r"symbol=(\d+)", href)
        symbol = symbol_match.group(1) if symbol_match else ""
        name_tc = link.get_text(strip=True)
        
        ipos.append({
            "symbol": symbol,
            "name_tc": name_tc,
        })
    
    return ipos

def get_ipo_detail(symbol: str) -> dict | None:
    """获取 IPO 详细信息。
    
    Args:
        symbol: 股票代码 (如 "02649")
    
    Returns:
        IPO 详细信息字典，失败返回 None
    """
    url = f"{BASE_URL}/tc/stocks/market/ipo/upcomingipo/company-summary?symbol={symbol}"
    
    try:
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            response = client.get(url, headers=HEADERS)
            response.raise_for_status()
    except httpx.HTTPError as e:
        print(f"Error fetching IPO detail for {symbol}: {e}", file=sys.stderr)
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 提取公司名称
    title_div = soup.find("div", class_="title")
    if not title_div:
        return None
    
    title_text = title_div.get_text(separator="\n", strip=True)
    lines = title_text.split("\n")
    name_tc = lines[0].split("(")[0].strip() if lines else ""
    name_en = lines[1] if len(lines) > 1 else ""
    
    result = {
        "symbol": symbol,
        "name_tc": name_tc,
        "name_en": name_en,
    }
    
    # 提取招股日程表
    schedule_table = None
    for table in soup.find_all("table", class_="ns2"):
        if table.find("td", string=re.compile("招股日期")):
            schedule_table = table
            break
    
    if schedule_table:
        for row in schedule_table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) >= 2:
                label = _extract_text(cells[0])
                value = _extract_text(cells[1])
                
                if "招股日期" in label:
                    result["subscription_period"] = value
                elif "定價日期" in label:
                    result["pricing_date"] = value
                elif "公佈售股結果" in label:
                    result["result_date"] = value
                elif "退票寄發" in label:
                    result["refund_date"] = value
                elif "上市日期" in label:
                    result["listing_date"] = value
    
    # 提取基本公司资料
    company_table = None
    for table in soup.find_all("table", class_="ns2"):
        if table.find("td", string=re.compile("上市市場")):
            company_table = table
            break
    
    if company_table:
        for row in company_table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) >= 2:
                label = _extract_text(cells[0])
                value = _extract_text(cells[1])
                
                if "上市市場" in label:
                    result["market"] = value
                elif "行業" in label:
                    result["industry"] = value
                elif "背景" in label:
                    result["background"] = value
                elif "業務主要地區" in label:
                    result["main_region"] = value
                elif "網址" in label:
                    link = cells[1].find("a")
                    result["website"] = link.get("href", "") if link else value
    
    # 提取招股资料 (IPOInfo 表格)
    ipo_info_table = soup.find("table", id="IPOInfo")
    if ipo_info_table:
        for row in ipo_info_table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) >= 2:
                label = _extract_text(cells[0])
                value = _extract_text(cells[1])
                
                if "每手股數" in label:
                    result["lot_size"] = _parse_int(value)
                elif "招股價" in label:
                    result["offer_price_range"] = value
                elif "上市市值" in label:
                    result["market_cap_range"] = value
                elif "香港配售股份" in label:
                    result["public_offer_shares"] = value
                elif "保薦人" in label:
                    sponsors = [a.get_text(strip=True) for a in cells[1].find_all("a")]
                    result["sponsors"] = sponsors if sponsors else [value]
                elif "包銷商" in label:
                    # 包销商可能没有链接，用 br 分隔
                    underwriters_text = cells[1].get_text(separator="\n", strip=True)
                    underwriters = [u.strip() for u in underwriters_text.split("\n") if u.strip()]
                    result["underwriters"] = underwriters
                elif "eIPO" in label:
                    link = cells[1].find("a")
                    result["eipo_link"] = link.get("href", "") if link else value
    
    # 提取孖展供应数据
    margin_table = soup.find("table", id="tblMargin")
    if margin_table:
        margin_data = []
        tbody = margin_table.find("tbody")
        if tbody:
            for row in tbody.find_all("tr"):
                # 检查是否是"暂无数据"行
                msg_cell = row.find("td", class_="msg")
                if msg_cell:
                    continue
                
                cells = row.find_all("td")
                if len(cells) >= 4:
                    margin_data.append({
                        "broker": _extract_text(cells[0]),
                        "margin_rate": _extract_text(cells[1]),
                        "interest_rate": _extract_text(cells[2]),
                        "financing_amount": _extract_text(cells[3]),
                    })
        result["margin_data"] = margin_data
    
    # 提取机构投资者
    investor_table = soup.find("table", id="tblInvestor")
    if investor_table:
        investors = []
        tbody = investor_table.find("tbody")
        if tbody:
            for row in tbody.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) >= 3:
                    investors.append({
                        "name": _extract_text(cells[0]),
                        "type": _extract_text(cells[1]),
                        "amount": _extract_text(cells[2]),
                    })
        result["institutional_investors"] = investors
    
    return result

def get_allotment_results() -> list[dict]:
    """获取最近 IPO 的中签率数据。
    
    Returns:
        中签率数据列表
    """
    # 从 upcomingipo 详情页获取中签率数据
    url = f"{BASE_URL}/tc/stocks/market/ipo/upcomingipo/company-summary"
    
    try:
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            response = client.get(url, headers=HEADERS)
            response.raise_for_status()
    except httpx.HTTPError as e:
        print(f"Error fetching allotment results: {e}", file=sys.stderr)
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 查找中签率表格
    table = soup.find("table", id="tblAllotmentResult")
    if not table:
        return []
    
    results = []
    tbody = table.find("tbody")
    if tbody:
        for row in tbody.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) >= 4:
                link = cells[0].find("a")
                if not link:
                    continue
                
                href = link.get("href", "")
                symbol_match = re.search(r"symbol=(\d+)", href)
                symbol = symbol_match.group(1) if symbol_match else ""
                
                results.append({
                    "symbol": symbol,
                    "name": link.get_text(strip=True),
                    "over_subscription_ratio": _parse_number(_extract_text(cells[1])),
                    "one_lot_success_rate": _extract_text(cells[2]),
                    "guaranteed_lots": _extract_text(cells[3]),
                })
    
    return results

def get_grey_market_schedule() -> list[dict]:
    """获取暗盘交易时间表。
    
    Returns:
        暗盘时间表列表
    """
    url = f"{BASE_URL}/tc/stocks/market/ipo/greymarket.aspx"
    
    try:
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            response = client.get(url, headers=HEADERS)
            response.raise_for_status()
    except httpx.HTTPError as e:
        print(f"Error fetching grey market schedule: {e}", file=sys.stderr)
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    schedule = []
    
    # 查找今日暗盘表格
    today_table = soup.find("table", id="tblGMToday")
    if today_table:
        tbody = today_table.find("tbody")
        if tbody:
            for row in tbody.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) >= 5:
                    link = cells[1].find("a")
                    if link:
                        href = link.get("href", "")
                        symbol_match = re.search(r"symbol=(\d+)", href)
                        symbol = symbol_match.group(1) if symbol_match else ""
                        
                        schedule.append({
                            "symbol": symbol,
                            "name": link.get_text(strip=True),
                            "type": "today",
                            "offer_price": _extract_text(cells[3]),
                        })
    
    # 查找即将暗盘表格
    upcoming_table = soup.find("table", id="tblGMUpcoming")
    if upcoming_table:
        tbody = upcoming_table.find("tbody")
        if tbody:
            for row in tbody.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) >= 8:
                    link = cells[1].find("a")
                    if link:
                        href = link.get("href", "")
                        symbol_match = re.search(r"symbol=(\d+)", href)
                        symbol = symbol_match.group(1) if symbol_match else ""
                        
                        gm_date = _extract_text(cells[7])
                        if "此股票沒有暗盤" in gm_date:
                            gm_date = None
                        
                        schedule.append({
                            "symbol": symbol,
                            "name": link.get_text(strip=True),
                            "type": "upcoming",
                            "grey_market_date": gm_date,
                            "listing_date": _extract_text(cells[8]) if len(cells) > 8 else "",
                        })
    
    return schedule

def get_sponsor_performance(symbol: str) -> list[dict]:
    """获取 IPO 保荐人历史表现。
    
    Args:
        symbol: 股票代码
    
    Returns:
        保荐人历史表现列表
    """
    detail = get_ipo_detail(symbol)
    if not detail:
        return []
    
    url = f"{BASE_URL}/tc/stocks/market/ipo/upcomingipo/company-summary?symbol={symbol}"
    
    try:
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            response = client.get(url, headers=HEADERS)
            response.raise_for_status()
    except httpx.HTTPError as e:
        print(f"Error fetching sponsor performance for {symbol}: {e}", file=sys.stderr)
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 查找保荐人表现表格
    table = soup.find("table", id="tblSponsor")
    if not table:
        return []
    
    results = []
    tbody = table.find("tbody")
    if tbody:
        for row in tbody.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) >= 4:
                results.append({
                    "sponsor": _extract_text(cells[0]),
                    "company": _extract_text(cells[1]),
                    "first_day_return": _extract_text(cells[2]),
                    "cumulative_return": _extract_text(cells[3]),
                })
    
    return results

# CLI 入口
if __name__ == "__main__":
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python aastocks.py <command> [args]")
        print("Commands:")
        print("  upcoming         获取即将上市 IPO 列表")
        print("  listed           获取已上市 IPO 列表")
        print("  detail <symbol>  获取 IPO 详细信息")
        print("  allotment        获取中签率数据")
        print("  greymarket       获取暗盘时间表")
        print("  sponsor <symbol> 获取保荐人历史表现")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "upcoming":
        result = get_upcoming_ipos()
    elif command == "listed":
        result = get_listed_ipos()
    elif command == "detail":
        if len(sys.argv) < 3:
            print("Please provide symbol", file=sys.stderr)
            sys.exit(1)
        result = get_ipo_detail(sys.argv[2])
    elif command == "allotment":
        result = get_allotment_results()
    elif command == "greymarket":
        result = get_grey_market_schedule()
    elif command == "sponsor":
        if len(sys.argv) < 3:
            print("Please provide symbol", file=sys.stderr)
            sys.exit(1)
        result = get_sponsor_performance(sys.argv[2])
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
