#!/usr/bin/env python3
"""
小饭票 Moltbook 监控 — 动态回帖间隔管理

用法:
  python3 moltbook_monitor.py check              # 检查是否需要回复，输出待回复评论
  python3 moltbook_monitor.py update --count 5   # 更新评论数和间隔
  python3 moltbook_monitor.py status             # 查看当前状态
  python3 moltbook_monitor.py watch <post_id>    # 开始监控一个新帖子
"""

import sys
import json
import argparse
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

STATE_PATH = Path(__file__).parent.parent.parent.parent.parent / \
    ".openclaw/workspace/memory/moltbook-monitor-state.json"
# 简化路径
STATE_PATH = Path.home() / ".openclaw/workspace/memory/moltbook-monitor-state.json"
CREDS_PATH = None  # Credentials read from MOLTBOOK_API_KEY env var only
API_BASE = "https://www.moltbook.com/api/v1"

# 间隔序列（分钟）
INTERVAL_STEPS = [10, 20, 40, 60, 120]


def get_api_key() -> str:
    # Read only from environment variable — no filesystem credential fallback
    return os.environ.get("MOLTBOOK_API_KEY", "")


def api_get(path: str) -> dict:
    api_key = get_api_key()
    req = urllib.request.Request(
        f"{API_BASE}{path}",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}


def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {}


def save_state(state: dict):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2))


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def minutes_since(iso_str: str) -> float:
    if not iso_str:
        return 9999
    t = datetime.fromisoformat(iso_str)
    if t.tzinfo is None:
        t = t.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - t).total_seconds() / 60


def cmd_watch(post_id: str):
    """开始监控一个新帖子（发帖后立即调用）"""
    state = load_state()
    state["active_post_id"] = post_id
    state["last_comment_count"] = 0
    state["current_interval_minutes"] = INTERVAL_STEPS[0]
    state["last_check_time"] = None
    state["last_reply_time"] = None
    state["mode"] = "active"
    state["post_url"] = f"https://www.moltbook.com/post/{post_id}"
    save_state(state)
    print(json.dumps({"status": "watching", "post_id": post_id,
                      "interval_minutes": INTERVAL_STEPS[0]}, ensure_ascii=False))


def cmd_check():
    """检查是否需要回复，输出待回复评论列表"""
    state = load_state()

    if not state.get("active_post_id") or state.get("mode") == "maintenance":
        print(json.dumps({"action": "none", "reason": state.get("mode", "no_active_post")},
                         ensure_ascii=False))
        return

    interval = state.get("current_interval_minutes", 120)
    last_reply = state.get("last_reply_time")
    elapsed = minutes_since(last_reply)

    if elapsed < interval:
        print(json.dumps({
            "action": "wait",
            "next_reply_in_minutes": round(interval - elapsed, 1),
            "current_interval": interval,
        }, ensure_ascii=False))
        return

    # 获取评论
    post_id = state["active_post_id"]
    result = api_get(f"/posts/{post_id}/comments?sort=new&limit=50")
    comments = result.get("comments", [])
    current_count = len(comments)

    # 找出 nomtiq 还没回复的评论（非 nomtiq 发的）
    unanswered = []
    nomtiq_replied_to = set()
    for c in comments:
        if c["author"]["name"] == "nomtiq" and c.get("parent_id"):
            nomtiq_replied_to.add(c["parent_id"])

    for c in comments:
        if c["author"]["name"] != "nomtiq" and c["id"] not in nomtiq_replied_to:
            unanswered.append({
                "id": c["id"],
                "author": c["author"]["name"],
                "content": c["content"],
            })

    # 更新检查时间
    state["last_check_time"] = now_iso()
    save_state(state)

    print(json.dumps({
        "action": "reply" if unanswered else "none",
        "post_id": post_id,
        "current_count": current_count,
        "last_count": state.get("last_comment_count", 0),
        "unanswered": unanswered,
        "current_interval": interval,
    }, ensure_ascii=False, indent=2))


def cmd_update(new_count: int):
    """回复完成后更新状态，调整间隔"""
    state = load_state()
    last_count = state.get("last_comment_count", 0)
    current_interval = state.get("current_interval_minutes", INTERVAL_STEPS[0])

    if new_count > last_count:
        # 评论增加，保持当前间隔
        next_interval = current_interval
        trend = "growing"
    else:
        # 评论没增加，升级间隔
        idx = INTERVAL_STEPS.index(current_interval) if current_interval in INTERVAL_STEPS else 0
        next_idx = min(idx + 1, len(INTERVAL_STEPS) - 1)
        next_interval = INTERVAL_STEPS[next_idx]
        trend = "cooling"

    state["last_comment_count"] = new_count
    state["current_interval_minutes"] = next_interval
    state["last_reply_time"] = now_iso()

    if next_interval >= 120:
        state["mode"] = "maintenance"

    save_state(state)
    print(json.dumps({
        "trend": trend,
        "new_interval_minutes": next_interval,
        "mode": state["mode"],
        "comment_count": new_count,
    }, ensure_ascii=False))


def cmd_status():
    state = load_state()
    if not state:
        print(json.dumps({"status": "no_state"}, ensure_ascii=False))
        return
    interval = state.get("current_interval_minutes", 120)
    elapsed = minutes_since(state.get("last_reply_time"))
    state["elapsed_since_last_reply_minutes"] = round(elapsed, 1)
    state["next_reply_in_minutes"] = max(0, round(interval - elapsed, 1))
    print(json.dumps(state, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Moltbook 动态回帖监控")
    sub = parser.add_subparsers(dest="command")

    watch_p = sub.add_parser("watch", help="开始监控新帖子")
    watch_p.add_argument("post_id")

    sub.add_parser("check", help="检查是否需要回复")

    update_p = sub.add_parser("update", help="更新状态")
    update_p.add_argument("--count", type=int, required=True, help="当前评论总数")

    sub.add_parser("status", help="查看状态")

    args = parser.parse_args()

    if args.command == "watch":
        cmd_watch(args.post_id)
    elif args.command == "check":
        cmd_check()
    elif args.command == "update":
        cmd_update(args.count)
    elif args.command == "status":
        cmd_status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
