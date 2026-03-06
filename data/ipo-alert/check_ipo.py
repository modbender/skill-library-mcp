#!/usr/bin/env python3
"""
IPO Alert - 38.co.kr 공모주 청약/신규상장 알림
Usage:
  python3 check_ipo.py daily      # 일일 체크 (청약 D-1, 당일 알림)
  python3 check_ipo.py weekly     # 주간 요약 (다음주 일정)
  python3 check_ipo.py list       # 현재 일정 출력 (테스트용)
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, date
from pathlib import Path

STATE_FILE = Path.home() / ".config/ipo-alert/state.json"
BASE_URL = "https://www.38.co.kr/html/fund/index.htm"

def fetch_page(url: str) -> str:
    """Fetch page with EUC-KR encoding."""
    result = subprocess.run(
        ["curl", "-s", url],
        capture_output=True
    )
    # Convert from EUC-KR to UTF-8
    try:
        return result.stdout.decode("euc-kr", errors="replace")
    except:
        return result.stdout.decode("utf-8", errors="replace")

def parse_subscription_schedule() -> list:
    """Parse 공모주청약일정 (o=k)."""
    html = fetch_page(f"{BASE_URL}?o=k")
    items = []
    
    # Find table rows with IPO data
    # Pattern handles: 종목명 (with optional extra font tags like (유가)), 일정, 확정공모가, 희망공모가, 경쟁률, 주간사
    pattern = r"<td[^>]*>\s*&nbsp;<a[^>]*href=\"[^\"]*no=(\d+)[^\"]*\"[^>]*>(?:<font[^>]*>)?([^<]+)(?:</font>)?(?:<font[^>]*>[^<]*</font>)?</a></td>\s*<td[^>]*>\s*(\d{4}\.\d{2}\.\d{2}~\d{2}\.\d{2})\s*</td>\s*<td[^>]*>([^<]*)</td>\s*<td[^>]*>([^<]*)</td>\s*<td[^>]*>([^<]*)</td>\s*<td[^>]*>([^<]*)</td>"
    
    for match in re.finditer(pattern, html, re.DOTALL):
        item_id = match.group(1).strip()
        name = match.group(2).strip()
        date_range = match.group(3).strip()
        confirmed_price = match.group(4).strip().replace("&nbsp;", "").strip()
        expected_price = match.group(5).strip().replace("&nbsp;", "").strip()
        competition = match.group(6).strip().replace("&nbsp;", "").strip()
        underwriter = match.group(7).strip().replace("&nbsp;", "").strip()
        
        # Parse start date
        try:
            start_str = date_range.split("~")[0]  # "2026.03.16"
            start_date = datetime.strptime(start_str, "%Y.%m.%d").date()
        except:
            continue
        
        items.append({
            "type": "subscription",
            "name": name,
            "url": f"https://www.38.co.kr/html/fund/?o=v&no={item_id}",
            "date_range": date_range,
            "start_date": start_date.isoformat(),
            "confirmed_price": confirmed_price if confirmed_price and confirmed_price != "-" else None,
            "expected_price": expected_price if expected_price and expected_price != "-" else None,
            "competition": competition if competition else None,
            "underwriter": underwriter
        })
    
    return items

def parse_new_listing() -> list:
    """Parse 신규상장 (o=nw)."""
    html = fetch_page(f"{BASE_URL}?o=nw")
    items = []
    
    # Pattern for 신규상장
    pattern = r'<td[^>]*><a[^>]*href=\"[^\"]*no=(\d+)[^\"]*\"[^>]*>(?:<font[^>]*>)?([^<]+)(?:<font[^>]*>[^<]*</font>)?(?:</font>)?</a></td>\s*<td[^>]*>\s*(\d{4}/\d{2}/\d{2})\s*</td>\s*<td[^>]*>([^<]*)</td>\s*<td[^>]*>[^<]*</td>\s*<td[^>]*>([^<]*)</td>'
    
    for match in re.finditer(pattern, html, re.DOTALL):
        item_id = match.group(1).strip()
        name = match.group(2).strip()
        # Remove (유가) suffix for cleaner name but keep original
        name = re.sub(r'<font[^>]*>[^<]*</font>', '', name).strip()
        listing_date_str = match.group(3).strip()
        current_price = match.group(4).strip().replace("&nbsp;", "").strip()
        ipo_price = match.group(5).strip().replace("&nbsp;", "").strip()
        
        try:
            listing_date = datetime.strptime(listing_date_str, "%Y/%m/%d").date()
        except:
            continue
        
        items.append({
            "type": "listing",
            "name": name,
            "url": f"https://www.38.co.kr/html/fund/?o=v&no={item_id}",
            "listing_date": listing_date.isoformat(),
            "current_price": current_price if current_price and current_price != "-" else None,
            "ipo_price": ipo_price if ipo_price and ipo_price != "-" else None
        })
    
    return items

def load_state() -> dict:
    """Load state from file."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"notified_subscriptions": [], "notified_listings": [], "last_check": None}

def save_state(state: dict):
    """Save state to file."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def get_weekday_kr(d: date) -> str:
    """Get Korean weekday name."""
    weekdays = ["월", "화", "수", "목", "금", "토", "일"]
    return weekdays[d.weekday()]

def format_date_with_weekday(date_range: str, start_date_str: str) -> str:
    """Format date range with weekday info. e.g., 2026.02.23~02.24 -> 02/23(일)~24(월)"""
    try:
        start_date = datetime.fromisoformat(start_date_str).date()
        parts = date_range.split("~")
        start_part = parts[0]  # "2026.02.23"
        end_part = parts[1]    # "02.24"
        
        # Parse end date
        year = start_date.year
        end_month, end_day = int(end_part.split(".")[0]), int(end_part.split(".")[1])
        end_date = date(year, end_month, end_day)
        
        start_wd = get_weekday_kr(start_date)
        end_wd = get_weekday_kr(end_date)
        
        return f"{start_date.month:02d}/{start_date.day:02d}({start_wd})~{end_date.day:02d}({end_wd})"
    except:
        return date_range

def format_subscription(item: dict) -> str:
    """Format subscription item for notification."""
    price = item.get("confirmed_price") or item.get("expected_price") or "-"
    date_str = format_date_with_weekday(item['date_range'], item['start_date'])
    url = item.get('url', '')
    name_with_link = f"[{item['name']}]({url})" if url else item['name']
    return f"📋 {name_with_link}\n   청약: {date_str}\n   공모가: {price}\n   주간사: {item['underwriter']}"

def format_listing(item: dict) -> str:
    """Format listing item for notification."""
    price = item.get("ipo_price") or "-"
    try:
        listing_date = datetime.fromisoformat(item['listing_date']).date()
        wd = get_weekday_kr(listing_date)
        date_str = f"{listing_date.month:02d}/{listing_date.day:02d}({wd})"
    except:
        date_str = item['listing_date']
    url = item.get('url', '')
    name_with_link = f"[{item['name']}]({url})" if url else item['name']
    return f"🔔 {name_with_link}\n   상장일: {date_str}\n   공모가: {price}"

def daily_check():
    """Daily check - notify for D-1 and D-day subscriptions."""
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    
    state = load_state()
    subscriptions = parse_subscription_schedule()
    listings = parse_new_listing()
    
    alerts = []
    
    # Check subscriptions
    for item in subscriptions:
        start_date = datetime.fromisoformat(item["start_date"]).date()
        key = f"{item['name']}_{item['start_date']}"
        
        # D-1 alert
        if start_date == tomorrow:
            d1_key = f"{key}_d1"
            if d1_key not in state["notified_subscriptions"]:
                alerts.append(f"⏰ [내일 청약 시작]\n{format_subscription(item)}")
                state["notified_subscriptions"].append(d1_key)
        
        # D-day alert
        if start_date == today:
            d0_key = f"{key}_d0"
            if d0_key not in state["notified_subscriptions"]:
                alerts.append(f"🚀 [오늘 청약 시작]\n{format_subscription(item)}")
                state["notified_subscriptions"].append(d0_key)
    
    # Check listings (D-1 and D-day)
    for item in listings:
        listing_date = datetime.fromisoformat(item["listing_date"]).date()
        key = f"{item['name']}_{item['listing_date']}"
        
        if listing_date == tomorrow:
            d1_key = f"{key}_listing_d1"
            if d1_key not in state["notified_listings"]:
                alerts.append(f"⏰ [내일 신규상장]\n{format_listing(item)}")
                state["notified_listings"].append(d1_key)
        
        if listing_date == today:
            d0_key = f"{key}_listing_d0"
            if d0_key not in state["notified_listings"]:
                alerts.append(f"🎉 [오늘 신규상장]\n{format_listing(item)}")
                state["notified_listings"].append(d0_key)
    
    state["last_check"] = datetime.now().isoformat()
    save_state(state)
    
    # Clean old notifications (older than 30 days)
    cutoff = (today - timedelta(days=30)).isoformat()
    state["notified_subscriptions"] = [k for k in state["notified_subscriptions"] if k.split("_")[1] >= cutoff]
    state["notified_listings"] = [k for k in state["notified_listings"] if k.split("_")[1] >= cutoff]
    save_state(state)
    
    if alerts:
        print("\n\n".join(alerts))
    else:
        print("공모주/상장 알림 없음")

def weekly_summary():
    """Weekly summary - list next week's schedule."""
    today = datetime.now().date()
    # Next Monday to Friday
    days_until_monday = (7 - today.weekday()) % 7
    if days_until_monday == 0:
        days_until_monday = 7
    next_monday = today + timedelta(days=days_until_monday)
    next_friday = next_monday + timedelta(days=4)
    
    subscriptions = parse_subscription_schedule()
    listings = parse_new_listing()
    
    week_subscriptions = []
    week_listings = []
    
    for item in subscriptions:
        start_date = datetime.fromisoformat(item["start_date"]).date()
        if next_monday <= start_date <= next_friday:
            week_subscriptions.append(item)
    
    for item in listings:
        listing_date = datetime.fromisoformat(item["listing_date"]).date()
        if next_monday <= listing_date <= next_friday:
            week_listings.append(item)
    
    # Sort by date
    week_subscriptions.sort(key=lambda x: x["start_date"])
    week_listings.sort(key=lambda x: x["listing_date"])
    
    output = [f"📅 다음주 공모주 일정 ({next_monday.strftime('%m/%d')} ~ {next_friday.strftime('%m/%d')})"]
    output.append("")
    
    if week_subscriptions:
        output.append("【청약 일정】")
        for item in week_subscriptions:
            output.append(format_subscription(item))
            output.append("")
    else:
        output.append("【청약 일정】 없음")
        output.append("")
    
    if week_listings:
        output.append("【신규상장】")
        for item in week_listings:
            output.append(format_listing(item))
            output.append("")
    else:
        output.append("【신규상장】 없음")
    
    print("\n".join(output))

def list_all():
    """List all current schedules."""
    subscriptions = parse_subscription_schedule()
    listings = parse_new_listing()
    
    print("=== 공모주청약 일정 ===")
    for item in subscriptions[:10]:
        print(format_subscription(item))
        print()
    
    print("\n=== 신규상장 ===")
    for item in listings[:10]:
        print(format_listing(item))
        print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "daily":
        daily_check()
    elif cmd == "weekly":
        weekly_summary()
    elif cmd == "list":
        list_all()
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)
