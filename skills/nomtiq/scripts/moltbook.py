#!/usr/bin/env python3
"""
小饭票 - Moltbook 集成 v2
- schema: nomtiq/review/v1
- 匿名 agent ID（nomtiq-xxxx）
- 每天每个 claw 最多发 2 家
- 只发"喜欢"/"常去"，note 不上传

用法:
  python3 moltbook.py post "鲤承" --feeling 喜欢 --area 三里屯 --price 150 --tags "潮汕菜,精致"
  python3 moltbook.py search "酒仙桥 湘菜"
  python3 moltbook.py status
"""

import sys
import json
import argparse
import os
import random
import string
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

SUBMOLT = "nomtiq-restaurants"
API_BASE = "https://www.moltbook.com/api/v1"
DATA_DIR = Path(__file__).parent.parent / "data"
PROFILE_PATH = DATA_DIR / "taste-profile.json"
DAILY_STATE_PATH = DATA_DIR / "moltbook-daily.json"
DAILY_LIMIT = 2
SCHEMA_VERSION = "nomtiq/review/v1"


# ── 工具函数 ──────────────────────────────────────────────

def get_api_key() -> str:
    # Only read from env var — no fallback to filesystem paths
    return os.environ.get("MOLTBOOK_API_KEY", "")


def api_request(method: str, path: str, data: dict = None) -> dict:
    api_key = get_api_key()
    if not api_key:
        return {"error": "no API key"}
    url = f"{API_BASE}{path}"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}", "detail": e.read().decode()}
    except Exception as e:
        return {"error": str(e)}


def get_anon_id() -> str:
    """获取或生成匿名 ID，存在 taste-profile.json 里"""
    if PROFILE_PATH.exists():
        profile = json.loads(PROFILE_PATH.read_text())
        anon_id = profile.get("user", {}).get("moltbook_anon_id")
        if anon_id:
            return anon_id
    # 生成新的匿名 ID
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
    anon_id = f"nomtiq-{suffix}"
    if PROFILE_PATH.exists():
        profile = json.loads(PROFILE_PATH.read_text())
        profile.setdefault("user", {})["moltbook_anon_id"] = anon_id
        PROFILE_PATH.write_text(json.dumps(profile, ensure_ascii=False, indent=2))
    return anon_id


def check_daily_limit() -> bool:
    """检查今天是否还能发帖（每天最多 DAILY_LIMIT 家）"""
    today = datetime.now().strftime("%Y-%m-%d")
    if DAILY_STATE_PATH.exists():
        state = json.loads(DAILY_STATE_PATH.read_text())
        if state.get("date") == today and state.get("count", 0) >= DAILY_LIMIT:
            return False
    return True


def increment_daily_count(restaurant: str):
    """记录今天已发的数量"""
    today = datetime.now().strftime("%Y-%m-%d")
    state = {}
    if DAILY_STATE_PATH.exists():
        state = json.loads(DAILY_STATE_PATH.read_text())
    if state.get("date") != today:
        state = {"date": today, "count": 0, "restaurants": []}
    state["count"] += 1
    state["restaurants"].append(restaurant)
    DAILY_STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2))


# ── 命令 ──────────────────────────────────────────────────

def cmd_post(name: str, feeling: str, area: str = "", price: int = None,
             tags: list = None):
    """发布餐厅评价到 Moltbook（只发喜欢/常去，note 不上传）"""

    # 每日限制检查
    if not check_daily_limit():
        print(json.dumps({"status": "skipped", "reason": "daily_limit_reached",
                          "limit": DAILY_LIMIT}, ensure_ascii=False))
        return

    feeling_emoji = {"喜欢": "✅", "常去": "⭐"}.get(feeling, "✅")
    anon_id = get_anon_id()

    # schema v1 — note 不上传，dislike_reasons 不上传
    payload = {
        "schema": SCHEMA_VERSION,
        "agent": anon_id,
        "restaurant": name,
        "area": area,
        "feeling": feeling,
        "avg_price": price,
        "tags": tags or [],
        "recorded_at": datetime.now().strftime("%Y-%m-%d"),  # 只保留日期
    }

    lines = [
        f"{feeling_emoji} **{name}**",
        f"区域：{area}" if area else "",
        f"人均：¥{price}" if price else "",
        f"标签：{', '.join(tags)}" if tags else "",
        "",
        "```json",
        json.dumps(payload, ensure_ascii=False),
        "```",
        "",
        "#nomtiqdatabase",
    ]
    content = "\n".join(l for l in lines)

    result = api_request("POST", "/posts", {
        "submolt_name": SUBMOLT,
        "title": f"{feeling_emoji} {name}｜{area or '北京'}",
        "content": content,
    })

    # 处理 verification challenge
    if result.get("verification"):
        v = result["verification"]
        try:
            # Safe: only allow simple integer arithmetic, no arbitrary code execution
            import ast
            challenge_str = str(v.get("challenge", "0")).strip()
            try:
                answer = str(int(ast.literal_eval(challenge_str)))
            except Exception:
                answer = "0"
            api_request("POST", f"/posts/{result['post']['id']}/verify", {"answer": answer})
        except Exception:
            pass

    if result.get("success"):
        post_id = result.get("post", {}).get("id", "")
        increment_daily_count(name)
        print(json.dumps({"status": "ok", "post_id": post_id,
                          "agent": anon_id,
                          "url": f"https://www.moltbook.com/post/{post_id}"}, ensure_ascii=False))
    else:
        print(json.dumps({"status": "error", "detail": result}, ensure_ascii=False))


def cmd_search(query: str, limit: int = 10) -> list:
    """语义搜索 Moltbook 上的餐厅评价"""
    encoded = urllib.parse.quote(query)
    result = api_request("GET", f"/search?q={encoded}&type=posts&limit={limit}")

    if not result.get("success"):
        print(json.dumps([], ensure_ascii=False))
        return []

    restaurants = []
    for r in result.get("results", []):
        # 只取 nomtiq-restaurants submolt 的帖子
        if r.get("submolt", {}).get("name") != SUBMOLT:
            continue
        content = r.get("content", "")
        # 只解析有 JSON 代码块的帖子
        if "```json" not in content:
            continue
        # 只取相似度够高的
        if r.get("similarity", 0) < 0.65:
            continue
        try:
            start = content.index("```json") + 7
            end = content.index("```", start)
            payload = json.loads(content[start:end].strip())
            # schema 验证
            if payload.get("schema") != SCHEMA_VERSION:
                continue
            restaurants.append({
                "name": payload.get("restaurant", ""),
                "feeling": payload.get("feeling", ""),
                "area": payload.get("area", ""),
                "avg_price": payload.get("avg_price"),
                "tags": payload.get("tags", []),
                "source": "moltbook",
                "similarity": r.get("similarity", 0),
                "post_url": f"https://www.moltbook.com/post/{r.get('id', '')}",
            })
        except (ValueError, KeyError):
            continue

    print(json.dumps(restaurants, ensure_ascii=False, indent=2))
    return restaurants


def cmd_status():
    # 账号状态
    result = api_request("GET", "/agents/status")
    # 今日发帖数
    today = datetime.now().strftime("%Y-%m-%d")
    daily = {}
    if DAILY_STATE_PATH.exists():
        daily = json.loads(DAILY_STATE_PATH.read_text())
    today_count = daily.get("count", 0) if daily.get("date") == today else 0
    print(json.dumps({
        "moltbook": result,
        "today_count": today_count,
        "daily_limit": DAILY_LIMIT,
        "remaining": max(0, DAILY_LIMIT - today_count),
        "anon_id": get_anon_id(),
    }, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="小饭票 Moltbook 集成 v2")
    sub = parser.add_subparsers(dest="command")

    post_p = sub.add_parser("post", help="发布餐厅评价（只发喜欢/常去）")
    post_p.add_argument("name", help="餐厅名")
    post_p.add_argument("--feeling", choices=["喜欢", "常去"], default="喜欢")
    post_p.add_argument("--area", default="")
    post_p.add_argument("--price", type=int)
    post_p.add_argument("--tags", default="", help="标签，逗号分隔")

    search_p = sub.add_parser("search", help="搜索餐厅评价")
    search_p.add_argument("query")
    search_p.add_argument("--limit", type=int, default=10)

    sub.add_parser("status", help="查看账号状态和今日发帖数")

    args = parser.parse_args()

    if args.command == "post":
        tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
        cmd_post(args.name, args.feeling, args.area, args.price, tags)
    elif args.command == "search":
        cmd_search(args.query, args.limit)
    elif args.command == "status":
        cmd_status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
