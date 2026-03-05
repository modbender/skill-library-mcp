#!/usr/bin/env python3
"""
Outlook 日历读取脚本 - Token 模式
1. 用 Playwright + Cookie 打开 Outlook Web，拦截 Bearer Token
2. 用 requests + Bearer Token 调 OWA REST API
3. Token 缓存到 data/token.json，有效期内复用
"""
import json, time, sys, argparse, requests, re, subprocess
from pathlib import Path
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).parent
OUTLOOK_DIR = Path.home() / ".outlook"
with open(OUTLOOK_DIR / "config.json") as f:
    cfg = json.load(f)

COOKIE_FILE = OUTLOOK_DIR / "cookies.json"
TOKEN_FILE = OUTLOOK_DIR / "token.json"
TOKEN_TTL = 3600  # Token 复用 1 小时


def get_date_range(args):
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if args.today:
        return today.strftime("%Y-%m-%d"), (today + timedelta(days=1)).strftime("%Y-%m-%d")
    elif args.tomorrow:
        t = today + timedelta(days=1)
        return t.strftime("%Y-%m-%d"), (t + timedelta(days=1)).strftime("%Y-%m-%d")
    elif args.week:
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=7)
        return monday.strftime("%Y-%m-%d"), sunday.strftime("%Y-%m-%d")
    elif args.month:
        year, month = map(int, args.month.split("-"))
        start = datetime(year, month, 1)
        end = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
        return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
    elif args.range:
        return args.range[0], args.range[1]
    else:
        return today.strftime("%Y-%m-%d"), (today + timedelta(days=1)).strftime("%Y-%m-%d")


def load_cached_token():
    if not TOKEN_FILE.exists():
        return None
    with open(TOKEN_FILE) as f:
        data = json.load(f)
    if time.time() - data.get("saved_at", 0) < TOKEN_TTL:
        return data.get("bearer")
    return None


def run_login_and_notify():
    """自动执行 login.py，监听 MFA 数字并通知用户，等待登录完成"""
    STATUS_FILE = OUTLOOK_DIR / "login_status.txt"
    login_script = BASE_DIR / "login.py"
    STATUS_FILE.write_text("")
    proc = subprocess.Popen(
        [sys.executable, str(login_script)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print("[AUTH] Cookie 已过期，正在自动重新登录...", flush=True)
    notified_number = False
    for _ in range(150):
        time.sleep(2)
        try:
            content = STATUS_FILE.read_text()
        except:
            content = ""
        if not notified_number:
            import re as _re
            m = _re.search(r"\[NUMBER:(\d+)\]", content)
            if m:
                print(f"[MFA] 请在 Microsoft Authenticator 上选择数字：【{m.group(1)}】", flush=True)
                notified_number = True
        if "[DONE]" in content:
            proc.wait()
            print("[AUTH] 登录成功，继续执行...", flush=True)
            return
    proc.kill()
    print("[AUTH_FAILED] 登录超时，请手动运行 login.py", flush=True)
    sys.exit(1)


def fetch_token_via_playwright():
    if not COOKIE_FILE.exists():
        run_login_and_notify()

    with open(COOKIE_FILE) as f:
        saved_cookies = json.load(f)

    owa_token = None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        ctx.add_cookies(saved_cookies)

        def handle_request(req):
            nonlocal owa_token
            if owa_token:
                return
            auth = req.headers.get("authorization", "")
            if auth.startswith("Bearer ") and "outlook.office.com" in req.url:
                owa_token = auth[7:]

        ctx.on("request", handle_request)
        page = ctx.new_page()
        page.goto("https://outlook.office.com/calendar/view/month", timeout=30000)
        page.wait_for_load_state("load", timeout=20000)
        time.sleep(10)

        if "login.microsoftonline.com" in page.url:
            browser.close()
            run_login_and_notify()
            return fetch_token_via_playwright()

        browser.close()

    if not owa_token:
        print("[AUTH_FAILED] 未能获取 Bearer Token，请重新运行 login.py", file=sys.stderr)
        sys.exit(1)

    TOKEN_FILE.parent.mkdir(exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        json.dump({"bearer": owa_token, "saved_at": time.time()}, f)

    return owa_token


def get_token():
    token = load_cached_token()
    if token:
        return token
    return fetch_token_via_playwright()


def fetch_calendar_api(start_date, end_date, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }
    params = {
        "startDateTime": f"{start_date}T00:00:00",
        "endDateTime": f"{end_date}T23:59:59",
        "$select": "Subject,Start,End,Organizer,ShowAs,IsAllDay",
        "$orderby": "Start/DateTime",
        "$top": 100,
    }
    resp = requests.get(
        "https://outlook.office.com/api/v2.0/me/CalendarView",
        headers=headers,
        params=params,
        timeout=15,
    )
    if resp.status_code == 401:
        return None, "token_expired"
    if not resp.ok:
        return None, f"api_error:{resp.status_code}:{resp.text[:300]}"
    return resp.json().get("value", []), None


def parse_events(raw_events):
    from zoneinfo import ZoneInfo
    _UTC = ZoneInfo("UTC")
    _SH = ZoneInfo("Asia/Shanghai")

    def to_sh(dt_str):
        """把 API 返回的 UTC 字符串转成上海时间字符串"""
        if not dt_str:
            return ""
        try:
            dt_utc = datetime.strptime(dt_str[:16], "%Y-%m-%dT%H:%M").replace(tzinfo=_UTC)
            return dt_utc.astimezone(_SH).strftime("%Y-%m-%d %H:%M")
        except Exception:
            return dt_str[:16].replace("T", " ")

    events = []
    for e in raw_events:
        start_str = to_sh(e.get("Start", {}).get("DateTime", ""))
        end_str = to_sh(e.get("End", {}).get("DateTime", ""))
        try:
            start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
            end_dt = datetime.strptime(end_str, "%Y-%m-%d %H:%M")
            duration = round((end_dt - start_dt).total_seconds() / 3600, 2)
        except:
            duration = 0
        organizer = e.get("Organizer", {}).get("EmailAddress", {}).get("Name", "")
        show_as = e.get("ShowAs", "Unknown")
        status_map = {"Busy": "Busy", "Tentative": "Tentative", "Free": "Free", "Oof": "Out of Office"}
        events.append({
            "subject": e.get("Subject", "无标题"),
            "start": start_str,
            "end": end_str,
            "duration_hours": duration,
            "status": status_map.get(show_as, show_as),
            "organizer": organizer,
            "is_all_day": e.get("IsAllDay", False),
        })
    return events


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--today", action="store_true")
    parser.add_argument("--tomorrow", action="store_true")
    parser.add_argument("--week", action="store_true")
    parser.add_argument("--month", type=str)
    parser.add_argument("--range", nargs=2, metavar=("START", "END"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    start_date, end_date = get_date_range(args)

    token = get_token()
    raw_events, err = fetch_calendar_api(start_date, end_date, token)

    if err == "token_expired":
        if TOKEN_FILE.exists():
            TOKEN_FILE.unlink()
        token = fetch_token_via_playwright()
        raw_events, err = fetch_calendar_api(start_date, end_date, token)

    if err:
        print(f"[ERROR] {err}", file=sys.stderr)
        sys.exit(1)

    events = parse_events(raw_events)

    if args.json:
        print(json.dumps(events, ensure_ascii=False, indent=2))
    else:
        print(f"\n📅 {start_date} ~ {end_date} 日历事件（共 {len(events)} 个）\n")
        total_hours = sum(e["duration_hours"] for e in events if e["status"] in ["Busy", "Tentative"])
        for e in events:
            icon = {"Busy": "🔵", "Tentative": "🟡", "Free": "⚪", "Out of Office": "🔴"}.get(e["status"], "❓")
            tag = "（全天）" if e["is_all_day"] else f"({e['duration_hours']}h)"
            print(f"{icon} {e['start']} {tag} | {e['subject']}")
            if e["organizer"]:
                print(f"   组织者: {e['organizer']}")
        print(f"\n⏱ 会议总时长（Busy+Tentative）: {total_hours:.1f} 小时")


if __name__ == "__main__":
    main()
