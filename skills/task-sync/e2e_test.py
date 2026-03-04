#!/usr/bin/env python3
"""
Comprehensive E2E test for TickTick <-> Google Tasks bidirectional sync.

Tests 1-10 as specified in the test plan.
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta

# ── Setup paths ──
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_BIN = os.environ.get("PYTHON_BIN", sys.executable or "python3")
SYNC_SCRIPT = os.path.join(BASE_DIR, "sync.py")

sys.path.insert(0, BASE_DIR)
from utils.google_api import GoogleAPI
from utils.ticktick_api import TickTickAPI

# ── Load config ──
with open(os.path.join(BASE_DIR, "config.json")) as f:
    cfg = json.load(f)

google = GoogleAPI(cfg["google_token"])
ticktick = TickTickAPI(cfg["ticktick_token"], cfg["ticktick_api_base"])

TIMESTAMP = int(time.time())
MY_TASKS_CN = "\u6211\u7684\u4efb\u52a1"

# TickTick project ID to test with. Override via TT_PROJECT_ID if needed.
TT_PROJECT_ID = os.environ.get("TT_PROJECT_ID", "69896b6a8f08b86b38c8e5a7")

# Google "My Tasks" list ID (from sync_db: maps to TT_PROJECT_ID)
G_MY_TASKS_LIST_ID = None
for gid, tid in json.load(open(cfg["sync_db"])).get("lists", {}).items():
    if tid == TT_PROJECT_ID:
        G_MY_TASKS_LIST_ID = gid
        break

if not G_MY_TASKS_LIST_ID:
    # Fallback: find by name
    for l in google.get_lists():
        if MY_TASKS_CN in l.get("title", "") or l.get("title", "").lower() == "my tasks":
            G_MY_TASKS_LIST_ID = l["id"]
            break

assert G_MY_TASKS_LIST_ID, "Could not find Google My Tasks list ID"

print(f"Google My Tasks list ID: {G_MY_TASKS_LIST_ID}")
print(f"TickTick project ID: {TT_PROJECT_ID}")
print(f"Timestamp: {TIMESTAMP}")
print()


# ── Helpers ──

def run_sync():
    """Run sync.py and return output."""
    result = subprocess.run(
        [PYTHON_BIN, SYNC_SCRIPT],
        capture_output=True, text=True, cwd=BASE_DIR, timeout=120,
    )
    if result.returncode != 0:
        print(f"  SYNC STDERR: {result.stderr[:500]}")
    return result.returncode == 0


def wait_api(seconds=2):
    """Give APIs time to propagate."""
    time.sleep(seconds)


def find_tt_task_by_title(project_id, title_substring):
    """Find a TickTick task by partial title match."""
    tasks = ticktick.get_tasks(project_id) or []
    for t in tasks:
        if title_substring in t.get("title", ""):
            return t
    return None


def find_g_task_by_title(list_id, title_substring, show_completed=False):
    """Find a Google task by partial title match."""
    tasks = google.get_tasks(list_id, show_completed=show_completed)
    for t in tasks:
        if title_substring in t.get("title", ""):
            return t
    return None


def find_g_list_by_name(name):
    """Find a Google list by exact name."""
    for l in google.get_lists():
        if l.get("title") == name:
            return l
    return None


# ── Test tracking ──
results = []
cleanup_tasks = []  # (service, list/project_id, task_id) for cleanup


def record(test_num, description, passed, notes=""):
    status = "PASS" if passed else "FAIL"
    results.append((test_num, description, status, notes))
    print(f"  => Test {test_num}: {status} {f'- {notes}' if notes else ''}")
    print()


# ═══════════════════════════════════════════════════════════════
# TEST 1: New task created in Google -> syncs to TickTick
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("TEST 1: Google -> TickTick (new task)")
print("=" * 60)

test1_title = f"Test_G2T_{TIMESTAMP}"
print(f"  Creating Google task: {test1_title}")
g_task_1 = google.create_task(G_MY_TASKS_LIST_ID, test1_title)
assert g_task_1, "Failed to create Google task for Test 1"
print(f"  Google task ID: {g_task_1['id']}")
cleanup_tasks.append(("google", G_MY_TASKS_LIST_ID, g_task_1["id"]))

wait_api()
print("  Running sync...")
sync_ok = run_sync()
wait_api()

# Verify task appears in TickTick
tt_task_1 = find_tt_task_by_title(TT_PROJECT_ID, test1_title)
if tt_task_1:
    print(f"  Found in TickTick: {tt_task_1['title']} (id: {tt_task_1['id']})")
    cleanup_tasks.append(("ticktick", TT_PROJECT_ID, tt_task_1["id"]))
    record(1, "Google -> TickTick new task", True)
else:
    # Check all projects
    projects = ticktick.get_projects()
    found_in = None
    for p in projects:
        t = find_tt_task_by_title(p["id"], test1_title)
        if t:
            found_in = p
            tt_task_1 = t
            break
    # Also check inbox
    if not tt_task_1:
        t = find_tt_task_by_title("inbox", test1_title)
        if t:
            tt_task_1 = t
            found_in = {"id": "inbox", "name": "Inbox"}

    if tt_task_1:
        cleanup_tasks.append(("ticktick", found_in["id"], tt_task_1["id"]))
        record(1, "Google -> TickTick new task", True,
               f"Found in project '{found_in.get('name', found_in['id'])}'")
    else:
        record(1, "Google -> TickTick new task", False, "Task not found in TickTick")


# ═══════════════════════════════════════════════════════════════
# TEST 2: New task created in TickTick -> syncs to Google
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("TEST 2: TickTick -> Google (new task)")
print("=" * 60)

test2_title = f"Test_T2G_{TIMESTAMP}"
print(f"  Creating TickTick task: {test2_title}")
tt_task_2 = ticktick.create_task(TT_PROJECT_ID, test2_title)
assert tt_task_2 and "id" in tt_task_2, "Failed to create TickTick task for Test 2"
print(f"  TickTick task ID: {tt_task_2['id']}")
cleanup_tasks.append(("ticktick", TT_PROJECT_ID, tt_task_2["id"]))

wait_api()
print("  Running sync...")
sync_ok = run_sync()
wait_api()

# Verify task appears in Google
g_task_2 = find_g_task_by_title(G_MY_TASKS_LIST_ID, test2_title)
if g_task_2:
    print(f"  Found in Google: {g_task_2['title']} (id: {g_task_2['id']})")
    cleanup_tasks.append(("google", G_MY_TASKS_LIST_ID, g_task_2["id"]))
    record(2, "TickTick -> Google new task", True)
else:
    record(2, "TickTick -> Google new task", False, "Task not found in Google")


# ═══════════════════════════════════════════════════════════════
# TEST 3: Complete task in Google -> completes in TickTick
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("TEST 3: Complete in Google -> TickTick")
print("=" * 60)

if g_task_1 and tt_task_1:
    print(f"  Completing Google task: {test1_title}")
    google.update_task(G_MY_TASKS_LIST_ID, g_task_1["id"], status="completed")
    wait_api()

    print("  Running sync...")
    sync_ok = run_sync()
    wait_api()

    # Verify: task should be gone from TickTick active tasks
    tt_check = find_tt_task_by_title(TT_PROJECT_ID, test1_title)
    if tt_check is None:
        record(3, "Complete Google -> TickTick", True, "Task gone from TickTick active")
    else:
        # Check if status changed
        status = tt_check.get("status", 0)
        if status == 2:  # completed in TickTick
            record(3, "Complete Google -> TickTick", True, "Task marked completed in TickTick")
        else:
            record(3, "Complete Google -> TickTick", False,
                   f"Task still active in TickTick (status={status})")
else:
    record(3, "Complete Google -> TickTick", False, "Prerequisite tasks missing")


# ═══════════════════════════════════════════════════════════════
# TEST 4: Complete task in TickTick -> completes in Google
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("TEST 4: Complete in TickTick -> Google")
print("=" * 60)

if tt_task_2 and g_task_2:
    print(f"  Completing TickTick task: {test2_title}")
    ticktick.complete_task(TT_PROJECT_ID, tt_task_2["id"])
    wait_api()

    print("  Running sync...")
    sync_ok = run_sync()
    wait_api()

    # Verify: Google task should be completed
    g_check = find_g_task_by_title(G_MY_TASKS_LIST_ID, test2_title, show_completed=True)
    if g_check and g_check.get("status") == "completed":
        record(4, "Complete TickTick -> Google", True, "Google task status=completed")
    elif g_check:
        record(4, "Complete TickTick -> Google", False,
               f"Google task status={g_check.get('status')}")
    else:
        record(4, "Complete TickTick -> Google", False, "Task not found in Google")
else:
    record(4, "Complete TickTick -> Google", False, "Prerequisite tasks missing")


# ═══════════════════════════════════════════════════════════════
# TEST 5: Task with due date in Google -> date forwarded to
#          TickTick, cleared from Google
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("TEST 5: Due date Google -> TickTick (forward & clear)")
print("=" * 60)

test5_title = f"Test_DueDate_G_{TIMESTAMP}"
test5_due = "2026-03-01T00:00:00.000Z"
print(f"  Creating Google task with due date: {test5_title} (due: {test5_due})")
g_task_5 = google.create_task(G_MY_TASKS_LIST_ID, test5_title, due_date=test5_due)
assert g_task_5, "Failed to create Google task for Test 5"
print(f"  Google task ID: {g_task_5['id']}, due: {g_task_5.get('due')}")
cleanup_tasks.append(("google", G_MY_TASKS_LIST_ID, g_task_5["id"]))

wait_api()
print("  Running sync...")
sync_ok = run_sync()
wait_api(3)

# Verify: TickTick task has the date
tt_task_5 = find_tt_task_by_title(TT_PROJECT_ID, test5_title)
test5_tt_ok = False
test5_g_ok = False

if tt_task_5:
    tt_due = tt_task_5.get("dueDate", "")
    print(f"  TickTick task dueDate: {tt_due}")
    cleanup_tasks.append(("ticktick", TT_PROJECT_ID, tt_task_5["id"]))
    if "2026-03-01" in str(tt_due):
        test5_tt_ok = True
    else:
        print(f"  WARNING: Expected 2026-03-01 in dueDate, got: {tt_due}")
else:
    # Check inbox too
    tt_task_5 = find_tt_task_by_title("inbox", test5_title)
    if tt_task_5:
        tt_due = tt_task_5.get("dueDate", "")
        print(f"  TickTick task dueDate: {tt_due}")
        cleanup_tasks.append(("ticktick", "inbox", tt_task_5["id"]))
        if "2026-03-01" in str(tt_due):
            test5_tt_ok = True

# Verify: Google task date is cleared
g_task_5_after = find_g_task_by_title(G_MY_TASKS_LIST_ID, test5_title)
if g_task_5_after:
    g_due_after = g_task_5_after.get("due")
    print(f"  Google task due after sync: {g_due_after}")
    if g_due_after is None:
        test5_g_ok = True
    else:
        print(f"  WARNING: Google due date not cleared: {g_due_after}")

if test5_tt_ok and test5_g_ok:
    record(5, "Due date forwarded to TickTick, cleared from Google", True)
elif test5_tt_ok:
    record(5, "Due date forwarded to TickTick, cleared from Google", False,
           "Date in TickTick OK but not cleared from Google")
elif test5_g_ok:
    record(5, "Due date forwarded to TickTick, cleared from Google", False,
           "Date cleared from Google but not found in TickTick")
else:
    record(5, "Due date forwarded to TickTick, cleared from Google", False,
           f"TT task found: {tt_task_5 is not None}, G date cleared: {test5_g_ok}")


# ═══════════════════════════════════════════════════════════════
# TEST 6: Task with due date in TickTick -> "All" list WITH
#          date, regular list WITHOUT date
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("TEST 6: TickTick due date -> All list WITH date, regular WITHOUT")
print("=" * 60)

test6_title = f"Test_DueDate_T_{TIMESTAMP}"
test6_due = "2026-03-05T00:00:00+0000"
print(f"  Creating TickTick task with due date: {test6_title} (due: {test6_due})")
tt_task_6 = ticktick.create_task(TT_PROJECT_ID, test6_title, due_date=test6_due)
assert tt_task_6 and "id" in tt_task_6, "Failed to create TickTick task for Test 6"
print(f"  TickTick task ID: {tt_task_6['id']}")
cleanup_tasks.append(("ticktick", TT_PROJECT_ID, tt_task_6["id"]))

wait_api()
print("  Running sync...")
sync_ok = run_sync()
wait_api(3)

# Find "All" list
all_list = find_g_list_by_name("All")
test6_regular_ok = False
test6_all_ok = False

# Check regular list: should have NO date
g_task_6_regular = find_g_task_by_title(G_MY_TASKS_LIST_ID, test6_title)
if g_task_6_regular:
    g_due_regular = g_task_6_regular.get("due")
    print(f"  Regular list task due: {g_due_regular}")
    cleanup_tasks.append(("google", G_MY_TASKS_LIST_ID, g_task_6_regular["id"]))
    if g_due_regular is None:
        test6_regular_ok = True
    else:
        print(f"  WARNING: Regular list should have NO date, got: {g_due_regular}")
else:
    print("  WARNING: Task not found in Google regular list")

# Check "All" list: should have the date
if all_list:
    g_task_6_all = find_g_task_by_title(all_list["id"], test6_title)
    if g_task_6_all:
        g_due_all = g_task_6_all.get("due")
        print(f"  'All' list task due: {g_due_all}")
        cleanup_tasks.append(("google", all_list["id"], g_task_6_all["id"]))
        if g_due_all and "2026-03-05" in g_due_all:
            test6_all_ok = True
        else:
            print(f"  WARNING: 'All' list should have date, got: {g_due_all}")
    else:
        print("  WARNING: Task not found in 'All' list")
else:
    print("  WARNING: 'All' list not found")

if test6_regular_ok and test6_all_ok:
    record(6, "TickTick date -> All WITH date, regular WITHOUT", True)
elif test6_regular_ok:
    record(6, "TickTick date -> All WITH date, regular WITHOUT", False,
           "Regular list OK (no date), but All list date missing")
elif test6_all_ok:
    record(6, "TickTick date -> All WITH date, regular WITHOUT", False,
           "All list OK (has date), but regular list has unexpected date")
else:
    record(6, "TickTick date -> All WITH date, regular WITHOUT", False,
           f"Regular found: {g_task_6_regular is not None}, All list found: {all_list is not None}")


# ═══════════════════════════════════════════════════════════════
# TEST 7: Smart list "Today" contains overdue/today tasks
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("TEST 7: Smart list 'Today' contains overdue/today tasks")
print("=" * 60)

# Create a TickTick task with today's date
test7_title = f"Test_Today_{TIMESTAMP}"
today_str = datetime.now().strftime("%Y-%m-%dT00:00:00+0000")
print(f"  Creating TickTick task with today's date: {test7_title} (due: {today_str})")
tt_task_7 = ticktick.create_task(TT_PROJECT_ID, test7_title, due_date=today_str)
assert tt_task_7 and "id" in tt_task_7, "Failed to create TickTick task for Test 7"
print(f"  TickTick task ID: {tt_task_7['id']}")
cleanup_tasks.append(("ticktick", TT_PROJECT_ID, tt_task_7["id"]))

wait_api()
print("  Running sync...")
sync_ok = run_sync()
wait_api(3)

today_list = find_g_list_by_name("Today")
if today_list:
    g_task_7 = find_g_task_by_title(today_list["id"], test7_title)
    if g_task_7:
        print(f"  Found in 'Today' list: {g_task_7['title']}")
        cleanup_tasks.append(("google", today_list["id"], g_task_7["id"]))
        record(7, "Smart list 'Today' contains today's tasks", True)
    else:
        # List all tasks in Today list for debugging
        all_today = google.get_tasks(today_list["id"])
        print(f"  Tasks in Today list ({len(all_today)}):")
        for t in all_today[:5]:
            print(f"    - {t['title']}")
        record(7, "Smart list 'Today' contains today's tasks", False,
               "Task not found in Today list")
else:
    record(7, "Smart list 'Today' contains today's tasks", False,
           "Today list not found")


# ═══════════════════════════════════════════════════════════════
# TEST 8: Smart list "Next 7 Days" contains upcoming tasks
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("TEST 8: Smart list 'Next 7 Days' contains upcoming tasks")
print("=" * 60)

# Create a TickTick task with date 3 days from now
test8_title = f"Test_Next7_{TIMESTAMP}"
next3_str = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%dT00:00:00+0000")
print(f"  Creating TickTick task 3 days out: {test8_title} (due: {next3_str})")
tt_task_8 = ticktick.create_task(TT_PROJECT_ID, test8_title, due_date=next3_str)
assert tt_task_8 and "id" in tt_task_8, "Failed to create TickTick task for Test 8"
print(f"  TickTick task ID: {tt_task_8['id']}")
cleanup_tasks.append(("ticktick", TT_PROJECT_ID, tt_task_8["id"]))

wait_api()
print("  Running sync...")
sync_ok = run_sync()
wait_api(3)

next7_list = find_g_list_by_name("Next 7 Days")
if next7_list:
    g_task_8 = find_g_task_by_title(next7_list["id"], test8_title)
    if g_task_8:
        print(f"  Found in 'Next 7 Days' list: {g_task_8['title']}")
        cleanup_tasks.append(("google", next7_list["id"], g_task_8["id"]))
        record(8, "Smart list 'Next 7 Days' contains upcoming tasks", True)
    else:
        all_next7 = google.get_tasks(next7_list["id"])
        print(f"  Tasks in Next 7 Days list ({len(all_next7)}):")
        for t in all_next7[:5]:
            print(f"    - {t['title']}")
        record(8, "Smart list 'Next 7 Days' contains upcoming tasks", False,
               "Task not found in Next 7 Days list")
else:
    record(8, "Smart list 'Next 7 Days' contains upcoming tasks", False,
           "Next 7 Days list not found")


# ═══════════════════════════════════════════════════════════════
# TEST 9: Priority sync - TickTick high priority -> Google [★]
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("TEST 9: Priority sync - TickTick priority=5 -> Google [★]")
print("=" * 60)

test9_title = f"Test_Priority_{TIMESTAMP}"
print(f"  Creating TickTick task with priority=5: {test9_title}")
tt_task_9_body = {
    "title": test9_title,
    "projectId": TT_PROJECT_ID,
    "priority": 5,
}
# Use the raw _request to set priority
tt_task_9 = ticktick._request("/task", "POST", tt_task_9_body)
assert tt_task_9 and "id" in tt_task_9, "Failed to create TickTick task for Test 9"
print(f"  TickTick task ID: {tt_task_9['id']}, priority: {tt_task_9.get('priority')}")
cleanup_tasks.append(("ticktick", TT_PROJECT_ID, tt_task_9["id"]))

wait_api()
print("  Running sync...")
sync_ok = run_sync()
wait_api(3)

# Find the Google task - should have [★] prefix
g_task_9 = find_g_task_by_title(G_MY_TASKS_LIST_ID, test9_title)
if not g_task_9:
    # Try with prefix
    g_task_9 = find_g_task_by_title(G_MY_TASKS_LIST_ID, f"[★] {test9_title}")

if g_task_9:
    print(f"  Found in Google: '{g_task_9['title']}'")
    cleanup_tasks.append(("google", G_MY_TASKS_LIST_ID, g_task_9["id"]))
    if g_task_9["title"].startswith("[★]"):
        record(9, "Priority 5 -> [★] prefix", True)
    else:
        record(9, "Priority 5 -> [★] prefix", False,
               f"Title is '{g_task_9['title']}', expected [★] prefix")
else:
    record(9, "Priority 5 -> [★] prefix", False, "Task not found in Google")


# ═══════════════════════════════════════════════════════════════
# TEST 10: No smart list names create TickTick projects
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("TEST 10: No smart list names create TickTick projects")
print("=" * 60)

projects = ticktick.get_projects()
project_names = [p.get("name", "") for p in projects]
print(f"  TickTick projects: {project_names}")

bad_names = [n for n in project_names if n in ("Today", "Next 7 Days", "All")]
if not bad_names:
    record(10, "No smart list names in TickTick projects", True,
           f"Projects: {project_names}")
else:
    record(10, "No smart list names in TickTick projects", False,
           f"Found unwanted projects: {bad_names}")


# ═══════════════════════════════════════════════════════════════
# TEST 11: Medium priority (priority=3) -> Google [!] prefix
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("TEST 11: Priority sync - TickTick priority=3 -> Google [!]")
print("=" * 60)

test11_title = f"Test_MedPriority_{TIMESTAMP}"
print(f"  Creating TickTick task with priority=3: {test11_title}")
tt_task_11_body = {
    "title": test11_title,
    "projectId": TT_PROJECT_ID,
    "priority": 3,
}
tt_task_11 = ticktick._request("/task", "POST", tt_task_11_body)
assert tt_task_11 and "id" in tt_task_11, "Failed to create TickTick task for Test 11"
print(f"  TickTick task ID: {tt_task_11['id']}, priority: {tt_task_11.get('priority')}")
cleanup_tasks.append(("ticktick", TT_PROJECT_ID, tt_task_11["id"]))

wait_api()
print("  Running sync...")
sync_ok = run_sync()
wait_api(3)

g_task_11 = find_g_task_by_title(G_MY_TASKS_LIST_ID, test11_title)
if not g_task_11:
    g_task_11 = find_g_task_by_title(G_MY_TASKS_LIST_ID, f"[!] {test11_title}")

if g_task_11:
    print(f"  Found in Google: '{g_task_11['title']}'")
    cleanup_tasks.append(("google", G_MY_TASKS_LIST_ID, g_task_11["id"]))
    if g_task_11["title"].startswith("[!]"):
        record(11, "Priority 3 -> [!] prefix", True)
    else:
        record(11, "Priority 3 -> [!] prefix", False,
               f"Title is '{g_task_11['title']}', expected [!] prefix")
else:
    record(11, "Priority 3 -> [!] prefix", False, "Task not found in Google")


# ═══════════════════════════════════════════════════════════════
# TEST 12: Task with notes/content sync (Google -> TickTick)
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("TEST 12: Task with notes sync (Google -> TickTick)")
print("=" * 60)

test12_title = f"Test_Notes_{TIMESTAMP}"
test12_notes = f"Test notes content {TIMESTAMP}"
print(f"  Creating Google task with notes: {test12_title}")
g_task_12 = google.create_task(G_MY_TASKS_LIST_ID, test12_title, notes=test12_notes)
assert g_task_12, "Failed to create Google task for Test 12"
print(f"  Google task ID: {g_task_12['id']}")
cleanup_tasks.append(("google", G_MY_TASKS_LIST_ID, g_task_12["id"]))

wait_api()
print("  Running sync...")
sync_ok = run_sync()
wait_api(3)

tt_task_12 = find_tt_task_by_title(TT_PROJECT_ID, test12_title)
if not tt_task_12:
    tt_task_12 = find_tt_task_by_title("inbox", test12_title)

if tt_task_12:
    tt_content = tt_task_12.get("content", "")
    print(f"  TickTick task content: '{tt_content}'")
    cleanup_tasks.append(("ticktick", TT_PROJECT_ID, tt_task_12["id"]))
    if test12_notes in tt_content:
        record(12, "Notes sync Google -> TickTick", True)
    else:
        record(12, "Notes sync Google -> TickTick", False,
               f"Expected '{test12_notes}', got '{tt_content}'")
else:
    record(12, "Notes sync Google -> TickTick", False, "Task not found in TickTick")


# ═══════════════════════════════════════════════════════════════
# TEST 13: Idempotency - running sync twice creates no duplicates
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("TEST 13: Idempotency - sync twice, no duplicates")
print("=" * 60)

# Count current tasks in Google and TickTick
g_tasks_before = google.get_tasks(G_MY_TASKS_LIST_ID)
tt_tasks_before = ticktick.get_tasks(TT_PROJECT_ID) or []
g_count_before = len(g_tasks_before)
tt_count_before = len(tt_tasks_before)
print(f"  Before: Google={g_count_before}, TickTick={tt_count_before}")

print("  Running sync (1st)...")
run_sync()
wait_api(2)
print("  Running sync (2nd)...")
run_sync()
wait_api(2)

g_tasks_after = google.get_tasks(G_MY_TASKS_LIST_ID)
tt_tasks_after = ticktick.get_tasks(TT_PROJECT_ID) or []
g_count_after = len(g_tasks_after)
tt_count_after = len(tt_tasks_after)
print(f"  After:  Google={g_count_after}, TickTick={tt_count_after}")

if g_count_after == g_count_before and tt_count_after == tt_count_before:
    record(13, "Idempotency - no duplicates after double sync", True)
else:
    record(13, "Idempotency - no duplicates after double sync", False,
           f"Google {g_count_before}->{g_count_after}, TT {tt_count_before}->{tt_count_after}")


# ═══════════════════════════════════════════════════════════════
# TEST 14: New list creation (Google -> TickTick project)
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("TEST 14: New Google list -> creates TickTick project")
print("=" * 60)

test14_list_name = f"TestList_{TIMESTAMP}"
print(f"  Creating Google list: {test14_list_name}")
g_list_14 = google.create_list(test14_list_name)
assert g_list_14, "Failed to create Google list for Test 14"
print(f"  Google list ID: {g_list_14['id']}")

wait_api()
print("  Running sync...")
sync_ok = run_sync()
wait_api(3)

# Check if TickTick project was created
projects_after = ticktick.get_projects()
tt_proj_14 = next((p for p in projects_after if p.get("name") == test14_list_name), None)
if tt_proj_14:
    print(f"  Found TickTick project: {tt_proj_14['name']} ({tt_proj_14['id']})")
    record(14, "New Google list -> TickTick project", True)
else:
    project_names = [p.get("name", "") for p in projects_after]
    record(14, "New Google list -> TickTick project", False,
           f"Project not found. Existing: {project_names}")


# ═══════════════════════════════════════════════════════════════
# TEST 15: Stale smart list task removal after completion
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("TEST 15: Stale smart list task removed after completion")
print("=" * 60)

# Test 7 created a task with today's date that should be in "Today" list
# Complete that task in TickTick, then verify it's removed from "Today"
if tt_task_7 and today_list:
    print(f"  Completing TickTick task: {test7_title}")
    ticktick.complete_task(TT_PROJECT_ID, tt_task_7["id"])
    wait_api()

    print("  Running sync...")
    sync_ok = run_sync()
    wait_api(3)

    # Task should be gone from "Today" smart list
    g_stale = find_g_task_by_title(today_list["id"], test7_title)
    if g_stale is None:
        record(15, "Stale task removed from smart list", True)
    else:
        g_stale_status = g_stale.get("status", "")
        if g_stale_status == "completed":
            record(15, "Stale task removed from smart list", True,
                   "Task completed (not deleted) in smart list")
        else:
            record(15, "Stale task removed from smart list", False,
                   f"Task still active in Today list (status={g_stale_status})")
else:
    record(15, "Stale task removed from smart list", False,
           f"Prerequisites missing: tt_task_7={tt_task_7 is not None}, today_list={today_list is not None}")


# ═══════════════════════════════════════════════════════════════
# CLEANUP: Complete all test tasks
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 60)
print("CLEANUP: Completing test tasks")
print("=" * 60)

for service, list_id, task_id in cleanup_tasks:
    try:
        if service == "google":
            google.update_task(list_id, task_id, status="completed")
            print(f"  Completed Google task {task_id[:20]}...")
        elif service == "ticktick":
            ticktick.complete_task(list_id, task_id)
            print(f"  Completed TickTick task {task_id[:20]}...")
    except Exception as e:
        print(f"  Cleanup error ({service} {task_id[:20]}): {e}")

# Clean up test list from Test 14
if g_list_14:
    try:
        google.service.tasklists().delete(tasklist=g_list_14["id"]).execute()
        print(f"  Deleted Google list: {test14_list_name}")
    except Exception as e:
        print(f"  Cleanup error (delete list): {e}")

# Final sync to propagate completions
wait_api()
print("  Running final sync to propagate completions...")
run_sync()


# ═══════════════════════════════════════════════════════════════
# RESULTS TABLE
# ═══════════════════════════════════════════════════════════════
print()
print()
print("=" * 80)
print("TEST RESULTS")
print("=" * 80)
print(f"{'Test':<6} {'Description':<55} {'Result':<7} {'Notes'}")
print("-" * 80)
for test_num, desc, status, notes in results:
    print(f"{test_num:<6} {desc:<55} {status:<7} {notes}")
print("-" * 80)

passed = sum(1 for _, _, s, _ in results if s == "PASS")
failed = sum(1 for _, _, s, _ in results if s == "FAIL")
print(f"\nTotal: {passed} PASS, {failed} FAIL out of {len(results)} tests")
