#!/usr/bin/env python3
"""OpenClaw wrapper for ku-portal-mcp — Korea University KUPID portal."""

import asyncio
import json
import os
import sys
from pathlib import Path

CREDS_FILE = Path.home() / ".config" / "ku-portal" / "credentials.json"

def load_credentials():
    """Load KUPID credentials from config file."""
    if not CREDS_FILE.exists():
        print(f"❌ 자격 증명 파일 없음: {CREDS_FILE}")
        print('{"id": "your-kupid-id", "pw": "your-kupid-password"} 형식으로 생성하세요.')
        sys.exit(1)
    with open(CREDS_FILE) as f:
        creds = json.load(f)
    os.environ["KU_PORTAL_ID"] = creds["id"]
    os.environ["KU_PORTAL_PW"] = creds["pw"]


def format_seats(rooms):
    """Format library seat data."""
    lines = []
    for r in rooms:
        pct = round(r.in_use / r.total_seats * 100) if r.total_seats > 0 else 0
        nb = "💻" if r.is_notebook_allowed else ""
        lines.append(f"  {r.room_name} {nb} | 잔여 {r.available}석 / 전체 {r.total_seats}석 (사용 {r.in_use}석, {pct}%) | {r.operating_hours}")
    return "\n".join(lines)


async def cmd_library(args):
    """도서관 좌석 현황 (로그인 불필요)."""
    from ku_portal_mcp.library import fetch_all_seats, fetch_library_seats, LIBRARY_CODES

    name_filter = None
    if "--name" in args:
        idx = args.index("--name")
        name_filter = args[idx + 1] if idx + 1 < len(args) else None

    if name_filter:
        # Find matching library code
        lib_code = None
        for code, name in LIBRARY_CODES.items():
            if name_filter in name:
                lib_code = code
                break
        if lib_code is None:
            print(f"❌ '{name_filter}' 도서관을 찾을 수 없습니다.")
            print(f"가능한 도서관: {', '.join(LIBRARY_CODES.values())}")
            return
        rooms = await fetch_library_seats(lib_code)
        print(f"📚 {LIBRARY_CODES[lib_code]} 좌석 현황:")
        print(format_seats(rooms))
    else:
        all_data = await fetch_all_seats()
        total_available = 0
        total_seats = 0
        for lib_code, rooms in all_data.items():
            lib_name = LIBRARY_CODES.get(lib_code, f"도서관 {lib_code}")
            print(f"\n📚 {lib_name}:")
            print(format_seats(rooms))
            for r in rooms:
                total_available += r.available
                total_seats += r.total_seats
        if total_seats > 0:
            usage = round((total_seats - total_available) / total_seats * 100)
            print(f"\n📊 전체: {total_available}/{total_seats} 잔여 ({usage}% 사용중)")


async def cmd_notices(args):
    """공지사항 목록/상세."""
    load_credentials()
    from ku_portal_mcp.auth import login
    from ku_portal_mcp.scraper import fetch_notice_list, fetch_notice_detail

    session = await login()

    if "--detail" in args:
        idx = args.index("--detail")
        msg_id = args[idx + 1]
        # Need to find the NoticeItem first
        notices = await fetch_notice_list(session, kind="11", count=50)
        item = next((n for n in notices if n.message_id == msg_id), None)
        if not item:
            # Try other kinds
            for k in ["89", "88"]:
                notices = await fetch_notice_list(session, kind=k, count=50)
                item = next((n for n in notices if n.message_id == msg_id), None)
                if item:
                    break
        if not item:
            print(f"❌ ID {msg_id} 공지를 찾을 수 없습니다.")
            return
        detail = await fetch_notice_detail(session, item)
        print(f"📌 {detail.title}")
        print(f"작성자: {detail.writer} | 날짜: {detail.date}")
        print(f"URL: {detail.url}")
        if detail.attachments:
            print(f"첨부: {', '.join(a.get('name', '') for a in detail.attachments)}")
        print(f"\n{detail.content}")
    else:
        limit = 10
        if "--limit" in args:
            idx = args.index("--limit")
            limit = int(args[idx + 1])
        notices = await fetch_notice_list(session, kind="11", count=limit)
        print("📋 공지사항:")
        for n in notices:
            print(f"  [{n.index}] {n.title} ({n.date}) - {n.writer} [ID: {n.message_id}]")


async def cmd_schedules(args):
    """학사일정."""
    load_credentials()
    from ku_portal_mcp.auth import login
    from ku_portal_mcp.scraper import fetch_notice_list, fetch_notice_detail

    session = await login()

    if "--detail" in args:
        idx = args.index("--detail")
        msg_id = args[idx + 1]
        detail = await fetch_notice_detail(session, msg_id, kind="89")
        print(f"📅 {detail.title}")
        print(f"날짜: {detail.date}")
        print(f"\n{detail.content}")
    else:
        limit = 10
        if "--limit" in args:
            idx = args.index("--limit")
            limit = int(args[idx + 1])
        items = await fetch_notice_list(session, kind="89", count=limit)
        print("📅 학사일정:")
        for n in items:
            print(f"  [{n.index}] {n.title} ({n.date}) [ID: {n.message_id}]")


async def cmd_scholarships(args):
    """장학공지."""
    load_credentials()
    from ku_portal_mcp.auth import login
    from ku_portal_mcp.scraper import fetch_notice_list

    session = await login()
    limit = 10
    if "--limit" in args:
        idx = args.index("--limit")
        limit = int(args[idx + 1])
    items = await fetch_notice_list(session, kind="88", count=limit)
    print("🎓 장학공지:")
    for n in items:
        print(f"  [{n.index}] {n.title} ({n.date}) - {n.writer} [ID: {n.message_id}]")


async def cmd_search(args):
    """통합 검색."""
    load_credentials()
    from ku_portal_mcp.auth import login
    from ku_portal_mcp.scraper import fetch_notice_list

    if not args:
        print("❌ 검색어를 입력하세요.")
        return

    keyword = args[0]
    session = await login()

    for kind, label in [("11", "공지사항"), ("89", "학사일정"), ("88", "장학공지")]:
        items = await fetch_notice_list(session, kind=kind, count=20)
        matches = [n for n in items if keyword in n.title]
        if matches:
            print(f"\n🔍 {label} ({len(matches)}건):")
            for n in matches:
                print(f"  [{n.index}] {n.title} ({n.date}) [ID: {n.message_id}]")

    if not any(keyword in n.title for items_list in [[]] for n in items_list):
        pass  # summary handled above


async def cmd_timetable(args):
    """시간표."""
    load_credentials()
    from ku_portal_mcp.auth import login
    from ku_portal_mcp.timetable import fetch_timetable_day, fetch_full_timetable, timetable_to_ics

    session = await login()

    if "--ics" in args:
        timetable = await fetch_full_timetable(session)
        ics_content = timetable_to_ics(timetable)
        out_path = Path.home() / "Downloads" / "ku_timetable.ics"
        out_path.write_text(ics_content)
        print(f"📥 ICS 파일 생성: {out_path}")
        return

    day_filter = None
    if "--day" in args:
        idx = args.index("--day")
        day_filter = args[idx + 1] if idx + 1 < len(args) else None

    day_names = {1: "월", 2: "화", 3: "수", 4: "목", 5: "금"}

    if day_filter:
        day_map = {"월": 1, "화": 2, "수": 3, "목": 4, "금": 5}
        day_num = day_map.get(day_filter, 1)
        entries = await fetch_timetable_day(session, day_num)
        print(f"📅 {day_filter}요일 시간표:")
        for e in entries:
            print(f"  {e.start_time}-{e.end_time} | {e.subject_name} | {e.classroom}")
    else:
        entries = await fetch_full_timetable(session)
        print("📅 주간 시간표:")
        by_day = {}
        for e in entries:
            by_day.setdefault(e.day_of_week, []).append(e)
        for day_num in sorted(by_day.keys()):
            day_label = day_names.get(day_num, str(day_num))
            print(f"\n  {day_label}요일:")
            for e in by_day[day_num]:
                print(f"    {e.start_time}-{e.end_time} | {e.subject_name} | {e.classroom}")


async def cmd_courses(args):
    """개설과목 검색."""
    load_credentials()
    from ku_portal_mcp.auth import login
    from ku_portal_mcp.courses import search_courses, fetch_departments, COLLEGE_CODES

    session = await login()

    college = None
    dept = None
    if "--college" in args:
        idx = args.index("--college")
        college = args[idx + 1] if idx + 1 < len(args) else None
    if "--dept" in args:
        idx = args.index("--dept")
        dept = args[idx + 1] if idx + 1 < len(args) else None

    if not college:
        print("📖 단과대 목록:")
        for code, name in COLLEGE_CODES.items():
            print(f"  {code}: {name}")
        return

    # Find college code
    col_code = None
    for code, name in COLLEGE_CODES.items():
        if college in name:
            col_code = code
            break

    if col_code is None:
        print(f"❌ '{college}' 단과대를 찾을 수 없습니다.")
        return

    if not dept:
        depts = await fetch_departments(session, col_code)
        print(f"📖 {college} 학과 목록:")
        for d in depts:
            print(f"  {d}")
        return

    courses = await search_courses(session, col_code, dept)
    print(f"📖 {college} {dept} 개설과목:")
    for c in courses:
        print(f"  {c}")


async def cmd_syllabus(args):
    """강의계획서."""
    load_credentials()
    from ku_portal_mcp.auth import login
    from ku_portal_mcp.courses import fetch_syllabus

    if not args:
        print("❌ 과목 코드를 입력하세요. 예: COSE101")
        return

    session = await login()
    result = await fetch_syllabus(session, args[0])
    print(result)


async def cmd_mycourses(args):
    """내 수강신청 내역."""
    load_credentials()
    from ku_portal_mcp.auth import login
    from ku_portal_mcp.courses import fetch_my_courses

    session = await login()
    courses = await fetch_my_courses(session)
    print("📚 내 수강과목:")
    total_credits = 0
    for c in courses:
        print(f"  {c}")


async def cmd_lms(args):
    """LMS 명령."""
    load_credentials()
    from ku_portal_mcp.lms import (
        lms_login, fetch_lms_courses, fetch_lms_assignments,
        fetch_lms_modules, fetch_lms_todo, fetch_lms_dashboard,
        fetch_lms_grades, fetch_lms_submissions, fetch_lms_quizzes,
    )

    if not args:
        print("❌ LMS 하위 명령: courses, assignments, modules, todo, dashboard, grades, submissions, quizzes")
        return

    subcmd = args[0]
    rest = args[1:]

    lms_session = await lms_login(os.environ["KU_PORTAL_ID"], os.environ["KU_PORTAL_PW"])

    if subcmd == "courses":
        courses = await fetch_lms_courses(lms_session)
        print("📚 LMS 수강과목:")
        for c in courses:
            print(f"  {c}")

    elif subcmd == "assignments":
        if not rest:
            print("❌ course_id를 입력하세요.")
            return
        assignments = await fetch_lms_assignments(lms_session, int(rest[0]))
        print("📝 과제 목록:")
        for a in assignments:
            print(f"  {a}")

    elif subcmd == "modules":
        if not rest:
            print("❌ course_id를 입력하세요.")
            return
        modules = await fetch_lms_modules(lms_session, int(rest[0]))
        print("📖 강의자료:")
        for m in modules:
            print(f"  {m}")

    elif subcmd == "todo":
        todo = await fetch_lms_todo(lms_session)
        print("✅ 할 일:")
        for t in todo:
            print(f"  {t}")

    elif subcmd == "dashboard":
        dashboard = await fetch_lms_dashboard(lms_session)
        print("📊 대시보드:")
        print(dashboard)

    elif subcmd == "grades":
        if not rest:
            print("❌ course_id를 입력하세요.")
            return
        grades = await fetch_lms_grades(lms_session, int(rest[0]))
        print("📊 성적:")
        for g in grades:
            print(f"  {g}")

    elif subcmd == "submissions":
        if not rest:
            print("❌ course_id를 입력하세요.")
            return
        subs = await fetch_lms_submissions(lms_session, int(rest[0]))
        print("📋 제출 현황:")
        for s in subs:
            print(f"  {s}")

    elif subcmd == "quizzes":
        if not rest:
            print("❌ course_id를 입력하세요.")
            return
        quizzes = await fetch_lms_quizzes(lms_session, int(rest[0]))
        print("📝 퀴즈:")
        for q in quizzes:
            print(f"  {q}")
    else:
        print(f"❌ 알 수 없는 LMS 명령: {subcmd}")


async def cmd_menu(args):
    """학생식당 메뉴 조회 (koreapas.com, 로그인 불필요)."""
    import httpx
    from bs4 import BeautifulSoup, NavigableString
    from datetime import date as dt_date
    import re

    target_date = None
    restaurant_filter = None
    if "--date" in args:
        idx = args.index("--date")
        target_date = args[idx + 1] if idx + 1 < len(args) else None
    if "--restaurant" in args:
        idx = args.index("--restaurant")
        restaurant_filter = args[idx + 1] if idx + 1 < len(args) else None
    if not target_date:
        target_date = str(dt_date.today())

    SKIP = re.compile(r"원산지|알레르기|제공되는 메뉴|리뷰 쓰기|「|」|· \d|식단 업데이트|^\s*$")
    ICON = re.compile(r"^(restaurant|help_outline|open_in_new|expand_more|expand_less|arrow_forward_ios)$")

    def clean(t):
        return t.replace("?", "₩").strip()

    def extract_meals(box_bottom):
        meals = {}
        for ms in box_bottom.find_all("span", class_="medu"):
            meal_base = clean(ms.get_text(strip=True))
            parent = ms.parent  # medu span의 div
            sibs = [s for s in parent.next_siblings if not isinstance(s, NavigableString)]

            # 다음 div가 A/B 구분자인지 확인
            suffix = ""
            menu_div = None
            for sib in sibs:
                sib_text = sib.get_text(strip=True)
                if sib_text in ("A", "B", "C", "D"):
                    suffix = f" {sib_text}"
                elif sib_text and not SKIP.search(sib_text) and not ICON.match(sib_text):
                    menu_div = sib
                    break

            meal_type = meal_base + suffix
            if menu_div:
                items = [clean(l) for l in menu_div.get_text(separator="\n", strip=True).splitlines()
                         if clean(l) and not SKIP.search(clean(l)) and not ICON.match(clean(l))]
                if items:
                    meals[meal_type] = items

        # b 태그 (크림슨테이블 등 고정메뉴)
        if not meals:
            for b in box_bottom.find_all("b"):
                bt = clean(b.get_text(strip=True))
                if not any(e in bt for e in ["🍛", "🍗", "🍙"]):
                    continue
                items = []
                for sib in b.next_siblings:
                    if isinstance(sib, NavigableString):
                        line = clean(str(sib))
                        if line and not SKIP.search(line) and not ICON.match(line):
                            items.append(line)
                    elif hasattr(sib, 'find') and sib.find("b"):
                        break
                    elif hasattr(sib, 'get_text'):
                        for line in sib.get_text(separator="\n", strip=True).splitlines():
                            line = clean(line)
                            if line and not SKIP.search(line) and not ICON.match(line):
                                items.append(line)
                if items:
                    meals[bt] = items
        return meals

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get("https://www.koreapas.com/m/sik.php")
        html = resp.content.decode("euc-kr", errors="replace")

    soup = BeautifulSoup(html, "lxml")
    menu_list = soup.find(class_="menu-list")
    if not menu_list:
        print("❌ 메뉴 정보를 가져올 수 없어요.")
        return

    children = [c for c in menu_list.children if not isinstance(c, NavigableString)]
    current_date = target_date  # date_big 이전 = 오늘
    current_rest = None
    results = {target_date: []}

    for child in children:
        classes = child.get("class") or []

        if "date_big" in classes:
            m = re.match(r"(\d{4}-\d{2}-\d{2})", child.get_text(strip=True))
            if m:
                current_date = m.group(1)
                if current_date not in results:
                    results[current_date] = []
            continue

        if "box_top" in classes:
            rest_text = child.get_text(strip=True)
            current_rest = re.sub(r"restaurant|help_outline", "", rest_text).strip()
            continue

        if "box_bottom" in classes and current_rest and current_date in results:
            meals = extract_meals(child)
            if meals:
                existing = next((r for r in results[current_date] if r[0] == current_rest), None)
                if existing:
                    existing[1].update(meals)
                else:
                    results[current_date].append([current_rest, meals])

    data = results.get(target_date, [])
    if restaurant_filter:
        data = [(r, m) for r, m in data if restaurant_filter in r]

    if not data:
        print(f"🍽️ {target_date} 메뉴 정보가 없어요.")
        return

    print(f"🍽️ {target_date} 고려대 학식\n")
    for rest_name, meals in data:
        if meals:
            print(f"🏫 {rest_name}")
            for meal_type, items in meals.items():
                print(f"  {meal_type}")
                for item in items:
                    print(f"    · {item}")
            print()


COMMANDS = {
    "library": cmd_library,
    "notices": cmd_notices,
    "schedules": cmd_schedules,
    "scholarships": cmd_scholarships,
    "search": cmd_search,
    "timetable": cmd_timetable,
    "courses": cmd_courses,
    "syllabus": cmd_syllabus,
    "mycourses": cmd_mycourses,
    "lms": cmd_lms,
    "menu": cmd_menu,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("사용법: ku_query.py <command> [options]")
        print()
        print("명령어:")
        print("  library     도서관 좌석 현황 (로그인 불필요)")
        print("  notices     공지사항")
        print("  schedules   학사일정")
        print("  scholarships 장학공지")
        print("  search      통합 검색")
        print("  timetable   시간표")
        print("  courses     개설과목 검색")
        print("  syllabus    강의계획서")
        print("  mycourses   내 수강과목")
        print("  lms         LMS (courses|assignments|modules|todo|dashboard|grades|submissions|quizzes)")
        return

    cmd = sys.argv[1]
    if cmd not in COMMANDS:
        print(f"❌ 알 수 없는 명령: {cmd}")
        print(f"가능한 명령: {', '.join(COMMANDS.keys())}")
        sys.exit(1)

    asyncio.run(COMMANDS[cmd](sys.argv[2:]))


if __name__ == "__main__":
    main()
