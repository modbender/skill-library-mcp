"""Market sentiment data sources.

Provides market sentiment indicators for HK IPO analysis:
- HSI (Hang Seng Index) - market sentiment gauge
- Sponsor historical performance from AASTOCKS
"""

import json
import sys
from typing import Optional

try:
    import requests
    from requests.exceptions import RequestException, Timeout, ConnectionError as ReqConnectionError
    from bs4 import BeautifulSoup
except ImportError:
    requests = None
    RequestException = Exception
    Timeout = Exception
    ReqConnectionError = Exception
    BeautifulSoup = None


# Constants
AASTOCKS_BASE_URL = "https://www.aastocks.com"
YAHOO_FINANCE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/^HSI"
DEFAULT_TIMEOUT = 15
USER_AGENT = "Mozilla/5.0 (compatible; HKIPOResearch/1.0)"


def _fmt(value: Optional[float], decimals: int = 2) -> str:
    """Format numeric value, return 'N/A' if None."""
    if value is None or not isinstance(value, (int, float)):
        return "N/A"
    return f"{value:.{decimals}f}"


def get_hsi() -> dict:
    """Get market sentiment via HSI (Hang Seng Index) data.
    
    Returns:
        dict with keys: index, price, change, change_pct, interpretation
        On error: {"error": "message"}
    """
    if requests is None:
        return {"error": "requests library not installed"}
    
    headers = {"User-Agent": USER_AGENT}
    
    try:
        resp = requests.get(YAHOO_FINANCE_URL, headers=headers, timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        
        result = data.get("chart", {}).get("result", [])
        if not result:
            return {"error": "No data returned from Yahoo Finance"}
        
        meta = result[0].get("meta", {})
        
        price = meta.get("regularMarketPrice")
        prev_close = meta.get("previousClose")
        
        if price is None or prev_close is None:
            return {"error": "Missing price data"}
        
        change = round(price - prev_close, 2)
        change_pct = round((price / prev_close - 1) * 100, 2) if prev_close else 0
        
        return {
            "index": "HSI",
            "price": price,
            "previous_close": prev_close,
            "change": change,
            "change_pct": change_pct,
            "day_high": meta.get("regularMarketDayHigh"),
            "day_low": meta.get("regularMarketDayLow"),
            "52w_high": meta.get("fiftyTwoWeekHigh"),
            "52w_low": meta.get("fiftyTwoWeekLow"),
            "interpretation": _interpret_hsi_change(change_pct)
        }
    except Timeout:
        return {"error": "Request timed out"}
    except ReqConnectionError:
        return {"error": "Connection failed"}
    except RequestException as e:
        return {"error": f"Request failed: {e}"}
    except (KeyError, ValueError, TypeError) as e:
        return {"error": f"Parse error: {e}"}


# Alias for backward compatibility
get_vhsi = get_hsi


def _interpret_hsi_change(change_pct: float) -> str:
    """Provide interpretation of HSI daily change."""
    if change_pct > 3:
        return "大涨，市场极度乐观"
    elif change_pct > 1:
        return "上涨，市场乐观"
    elif change_pct > 0:
        return "小涨，市场偏乐观"
    elif change_pct > -1:
        return "平稳，市场中性"
    elif change_pct > -3:
        return "下跌，市场谨慎"
    else:
        return "大跌，市场恐慌"


def get_all_sponsors() -> dict[str, str]:
    """Get all available sponsors from AASTOCKS dropdown.
    
    Returns:
        dict mapping sponsor name to sponsor id, empty dict on error
    """
    if requests is None or BeautifulSoup is None:
        return {}
    
    url = f"{AASTOCKS_BASE_URL}/sc/stocks/market/ipo/sponsor.aspx"
    headers = {"User-Agent": USER_AGENT}
    
    try:
        resp = requests.get(url, headers=headers, timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()
        resp.encoding = 'utf-8'
        
        soup = BeautifulSoup(resp.text, 'lxml')
        select = soup.find('select', {'id': 'cp_ddlSponsor'})
        if not select:
            return {}
        
        sponsors = {}
        for option in select.find_all('option'):
            value = option.get('value', '')
            name = option.get_text(strip=True)
            if value and value.isdigit() and name and name != '所有保荐人':
                sponsors[name] = value
        return sponsors
    except (RequestException, ValueError, AttributeError):
        return {}


def get_sponsor_detail(sponsor_id: str) -> Optional[dict]:
    """Get detailed stats for a specific sponsor by ID.
    
    Args:
        sponsor_id: The sponsor ID from AASTOCKS (must be numeric)
        
    Returns:
        dict with sponsor stats or None on error
    """
    if requests is None or BeautifulSoup is None:
        return None
    
    # Validate sponsor_id to prevent injection
    if not sponsor_id or not sponsor_id.isdigit():
        return None
    
    url = f"{AASTOCKS_BASE_URL}/sc/stocks/market/ipo/sponsor.aspx"
    params = {"s": "1", "o": "", "s2": "0", "o2": "0", "f1": sponsor_id, "f2": "", "page": "1"}
    headers = {"User-Agent": USER_AGENT}
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()
        resp.encoding = 'utf-8'
        
        soup = BeautifulSoup(resp.text, 'lxml')
        
        table = soup.find('table', {'id': 'tblData'})
        if not table:
            return None
        
        tbody = table.find('tbody')
        if not tbody:
            return None
        
        rows = tbody.find_all('tr')
        if not rows:
            return None
            
        up_count = 0
        down_count = 0
        first_day_returns: list[float] = []
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 6:
                perf_text = cells[5].get_text(strip=True)
                perf = _parse_pct(perf_text)
                if perf is not None:
                    first_day_returns.append(perf)
                    if perf > 0:
                        up_count += 1
                    elif perf < 0:
                        down_count += 1
        
        valid_count = len(first_day_returns)
        avg_first_day = round(sum(first_day_returns) / valid_count, 2) if valid_count > 0 else 0
        win_rate = round(up_count / valid_count * 100, 1) if valid_count > 0 else 0
        
        return {
            "ipo_count": len(rows),
            "valid_count": valid_count,
            "up_count": up_count,
            "down_count": down_count,
            "avg_first_day": avg_first_day,
            "win_rate": win_rate
        }
    except (RequestException, ValueError, AttributeError):
        return None


def _fallback_to_etnet() -> list[dict]:
    """Fallback to etnet data source when AASTOCKS fails."""
    try:
        from etnet import fetch_sponsor_rankings
        sponsors = fetch_sponsor_rankings()
        if sponsors:
            return [
                {
                    "name": s.sponsor_name,
                    "ipo_count": s.ipo_count,
                    "up_count": s.first_day_up_count,
                    "down_count": s.first_day_down_count,
                    "avg_first_day": s.avg_first_day_change,
                    "avg_cumulative": None,
                    "best_stock": s.best_stock.get("name") if s.best_stock else "N/A",
                    "best_return": float(s.best_stock.get("change", "0").replace("%", "").replace("+", "")) if s.best_stock else None,
                    "worst_stock": s.worst_stock.get("name") if s.worst_stock else "N/A",
                    "worst_return": float(s.worst_stock.get("change", "0").replace("%", "").replace("+", "")) if s.worst_stock else None,
                    "win_rate": s.first_day_up_rate,
                    "source": "etnet"
                }
                for s in sponsors
            ]
    except (ImportError, Exception):
        pass
    return []


def get_sponsor_history() -> list[dict]:
    """Get sponsor historical IPO performance from AASTOCKS (top 10).
    
    Falls back to etnet if AASTOCKS fails.
    
    Returns:
        List of dicts with sponsor performance data, or [{"error": "..."}] on error
    """
    if requests is None or BeautifulSoup is None:
        return [{"error": "requests or beautifulsoup4 not installed"}]
    
    url = f"{AASTOCKS_BASE_URL}/sc/stocks/market/ipo/sponsor.aspx"
    headers = {"User-Agent": USER_AGENT}
    
    try:
        resp = requests.get(url, headers=headers, timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()
        resp.encoding = 'utf-8'
        
        soup = BeautifulSoup(resp.text, 'lxml')
        
        table = soup.find('table', {'id': 'tblSummary'})
        if not table:
            # Fallback to etnet
            fallback = _fallback_to_etnet()
            if fallback:
                return fallback
            return [{"error": "Could not find sponsor summary table"}]
        
        tbody = table.find('tbody')
        if not tbody:
            fallback = _fallback_to_etnet()
            if fallback:
                return fallback
            return [{"error": "Could not find table body"}]
            
        rows = tbody.find_all('tr')
        sponsors = []
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 10:
                try:
                    ipo_count = _parse_int(cells[1].get_text(strip=True))
                    up_count = _parse_int(cells[2].get_text(strip=True))
                    
                    sponsor = {
                        "name": cells[0].get_text(strip=True),
                        "ipo_count": ipo_count,
                        "up_count": up_count,
                        "down_count": _parse_int(cells[3].get_text(strip=True)),
                        "avg_first_day": _parse_pct(cells[4].get_text(strip=True)),
                        "avg_cumulative": _parse_pct(cells[5].get_text(strip=True)),
                        "best_stock": cells[6].get_text(strip=True),
                        "best_return": _parse_pct(cells[7].get_text(strip=True)),
                        "worst_stock": cells[8].get_text(strip=True),
                        "worst_return": _parse_pct(cells[9].get_text(strip=True)),
                        "win_rate": round(up_count / ipo_count * 100, 1) if ipo_count > 0 else 0,
                        "source": "aastocks"
                    }
                    sponsors.append(sponsor)
                except (IndexError, ValueError, ZeroDivisionError):
                    continue
        
        if not sponsors:
            fallback = _fallback_to_etnet()
            if fallback:
                return fallback
            return [{"error": "No sponsor data found"}]
        
        return sponsors
    except Timeout:
        fallback = _fallback_to_etnet()
        if fallback:
            return fallback
        return [{"error": "Request timed out"}]
    except ReqConnectionError:
        fallback = _fallback_to_etnet()
        if fallback:
            return fallback
        return [{"error": "Connection failed"}]
    except RequestException as e:
        fallback = _fallback_to_etnet()
        if fallback:
            return fallback
        return [{"error": f"Request failed: {e}"}]


def _parse_int(s: str) -> int:
    """Parse integer from string, return 0 if failed."""
    try:
        return int(s.replace(',', '').strip())
    except (ValueError, AttributeError):
        return 0


def _parse_pct(s: str) -> Optional[float]:
    """Parse percentage from string like '+12.5%' or '-3.2%'."""
    try:
        cleaned = s.replace('%', '').replace('+', '').strip()
        return float(cleaned)
    except (ValueError, AttributeError):
        return None


def _normalize_sponsor_name(name: str) -> str:
    """Normalize sponsor name for matching (simplified Chinese, remove suffixes)."""
    # Common traditional -> simplified mappings for sponsor names
    t2s = {
        '證': '证', '國': '国', '際': '际', '銀': '银', '華': '华',
        '東': '东', '業': '业', '資': '资', '產': '产', '開': '开',
        '發': '发', '創': '创', '亞': '亚', '萬': '万', '廣': '广',
        '進': '进', '達': '达', '馬': '马', '財': '财', '貿': '贸',
        '實': '实', '電': '电', '訊': '讯', '對': '对', '環': '环',
        '聯': '联', '網': '网', '點': '点', '無': '无', '與': '与',
    }
    result = name
    for t, s in t2s.items():
        result = result.replace(t, s)
    # Remove common suffixes
    for suffix in ['有限公司', '有限责任公司', '股份有限公司']:
        result = result.replace(suffix, '')
    return result.strip().lower()


def search_sponsor(sponsors: list[dict], name: str) -> Optional[dict]:
    """Find a sponsor by name (partial match, handles traditional/simplified Chinese).
    
    Args:
        sponsors: List of sponsor dicts from get_sponsor_history()
        name: Sponsor name to search (can be partial)
        
    Returns:
        Matching sponsor dict or None
    """
    # Reject empty/blank names early
    if not name or not name.strip():
        return None
    
    name_normalized = _normalize_sponsor_name(name)
    if not name_normalized:
        return None
    
    # Try matching in provided list first (top 10 from summary)
    for s in sponsors:
        sponsor_normalized = _normalize_sponsor_name(s.get("name", ""))
        if sponsor_normalized and (name_normalized in sponsor_normalized or sponsor_normalized in name_normalized):
            return s
    
    # Not in top 10? Try full sponsor list from AASTOCKS
    all_sponsors = get_all_sponsors()
    for sponsor_name, sponsor_id in all_sponsors.items():
        sponsor_normalized = _normalize_sponsor_name(sponsor_name)
        if sponsor_normalized and (name_normalized in sponsor_normalized or sponsor_normalized in name_normalized):
            detail = get_sponsor_detail(sponsor_id)
            if detail:
                return {
                    "name": sponsor_name,
                    **detail,
                    "avg_cumulative": None,
                    "best_stock": "N/A",
                    "best_return": None,
                    "worst_stock": "N/A", 
                    "worst_return": None,
                }
    
    return None


def main(argv: Optional[list[str]] = None) -> None:
    """CLI interface for sentiment data."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Market sentiment data for HK IPO")
    parser.add_argument("command", choices=["vhsi", "sponsor", "sponsor-search"],
                        help="Data to fetch")
    parser.add_argument("--name", "-n", help="Sponsor name to search")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args(argv)
    
    if args.command == "vhsi":
        data = get_hsi()
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            if "error" in data:
                print(f"Error: {data['error']}", file=sys.stderr)
                sys.exit(1)
            print(f"恒生指数 (HSI): {_fmt(data.get('price'))}")
            print(f"变动: {data.get('change', 0):+.2f} ({data.get('change_pct', 0):+.2f}%)")
            print(f"今日区间: {_fmt(data.get('day_low'))} - {_fmt(data.get('day_high'))}")
            print(f"52周区间: {_fmt(data.get('52w_low'))} - {_fmt(data.get('52w_high'))}")
            print(f"市场情绪: {data.get('interpretation', 'N/A')}")
    
    elif args.command == "sponsor":
        sponsors = get_sponsor_history()
        if sponsors and "error" in sponsors[0]:
            print(f"Error: {sponsors[0]['error']}", file=sys.stderr)
            sys.exit(1)
        
        if args.json:
            print(json.dumps(sponsors, ensure_ascii=False, indent=2))
        else:
            print(f"{'保荐人':<20} {'IPO数':>6} {'首日上涨':>8} {'首日下跌':>8} {'胜率':>8} {'平均首日':>10}")
            print("-" * 70)
            for s in sponsors[:20]:
                avg = s.get('avg_first_day')
                avg_str = f"{avg:.2f}" if avg is not None else "N/A"
                print(f"{s['name']:<20} {s['ipo_count']:>6} {s['up_count']:>8} {s['down_count']:>8} {s['win_rate']:>7.1f}% {avg_str:>10}")
    
    elif args.command == "sponsor-search":
        if not args.name:
            print("Error: --name required for sponsor-search", file=sys.stderr)
            sys.exit(1)
        
        sponsors = get_sponsor_history()
        if sponsors and "error" in sponsors[0]:
            print(f"Error: {sponsors[0]['error']}", file=sys.stderr)
            sys.exit(1)
        
        result = search_sponsor(sponsors, args.name)
        if result:
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(f"保荐人: {result['name']}")
                print(f"IPO 数量: {result['ipo_count']}")
                print(f"首日上涨: {result['up_count']} ({result['win_rate']:.1f}%)")
                print(f"首日下跌: {result['down_count']}")
                avg_first = result.get('avg_first_day')
                print(f"平均首日表现: {_fmt(avg_first)}%")
                avg_cum = result.get('avg_cumulative')
                print(f"平均累计表现: {_fmt(avg_cum)}%")
                print(f"最佳: {result.get('best_stock', 'N/A')}")
                print(f"最差: {result.get('worst_stock', 'N/A')}")
        else:
            print(f"未找到保荐人: {args.name}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
