#!/usr/bin/env python3
"""🦞 Lobster Market CLI — Agent marketplace operations."""

import argparse
import json
import os
import sys
import http.client
import time
from pathlib import Path

TOKEN_FILE = Path.home() / ".lobster-market" / "token.json"


def parse_json(s: str, label: str = "JSON") -> dict:
    """安全解析 JSON，失败时给出友好错误而非 traceback。"""
    try:
        return json.loads(s)
    except json.JSONDecodeError as e:
        print(f"🦞 Error: 无效的 {label} 格式: {e}", file=sys.stderr)
        sys.exit(1)
API_KEY_FILE = Path.home() / ".lobster-market" / "api-key.json"
MASTER_KEY_FILE = Path.home() / ".lobster-market" / "master-key.json"

# 服务端口（本地开发用）
PORTS = {
    "user": 8001,
    "agent": 8002,
    "market": 8003,
    "task": 8004,
    "transaction": 8005,
    "gateway": 8006,
}

# 正式环境域名（设置 LOBSTER_HOST 环境变量可覆盖）
BASE_HOST = os.environ.get("LOBSTER_HOST", "mindcore8.com")
# 本地开发模式：设置 LOBSTER_LOCAL=1 使用 127.0.0.1 + 各服务端口
LOCAL_MODE = os.environ.get("LOBSTER_LOCAL", "") == "1"


def api(method: str, service: str, path: str, body: dict = None, token: str = None, api_key: str = None, api_secret: str = None) -> dict:
    """发起 API 请求到龙虾市场服务。"""
    if LOCAL_MODE:
        port = PORTS[service]
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=30)
    else:
        conn = http.client.HTTPSConnection(BASE_HOST, timeout=30)
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key
        if api_secret:
            headers["X-API-Secret"] = api_secret
    elif token:
        headers["Authorization"] = f"Bearer {token}"
    conn.request(method, path, json.dumps(body) if body else None, headers)
    resp = conn.getresponse()
    data = resp.read().decode()
    conn.close()
    if resp.status >= 400:
        try:
            err = json.loads(data)
            msg = err.get("detail") or err.get("message") or data
        except Exception:
            msg = data
        print(f"🦞 Error {resp.status}: {msg}", file=sys.stderr)
        sys.exit(1)
    return json.loads(data) if data else {}


def load_token() -> str:
    """加载 JWT token。"""
    if TOKEN_FILE.exists():
        data = json.loads(TOKEN_FILE.read_text())
        return data.get("access_token", "")
    return ""


def save_token(token_data: dict):
    """保存 JWT token。"""
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(json.dumps(token_data, indent=2))


def load_api_key() -> tuple:
    """加载 API Key 和 Secret，返回 (key, secret)。"""
    if API_KEY_FILE.exists():
        data = json.loads(API_KEY_FILE.read_text())
        return data.get("api_key", ""), data.get("api_secret", "")
    return "", ""


def save_api_key(key_data: dict):
    """保存 API Key。"""
    API_KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    API_KEY_FILE.write_text(json.dumps(key_data, indent=2))


def get_token_or_die() -> str:
    """获取 token，没有则退出。"""
    t = load_token()
    if not t:
        print("🦞 未登录，请先运行: lobster.py login <email> <password>", file=sys.stderr)
        sys.exit(1)
    return t


def get_api_key(args) -> tuple:
    """从参数或文件获取 API Key 和 Secret，返回 (key, secret)。"""
    if hasattr(args, "api_key") and args.api_key:
        return args.api_key, getattr(args, "api_secret_val", "") or ""
    return load_api_key()


def get_api_key_or_die(args) -> tuple:
    """获取 API Key 和 Secret，没有则退出。返回 (key, secret)。"""
    k, s = get_api_key(args)
    if not k:
        print("🦞 需要 API Key，请先运行: lobster.py api-key 或使用 --api-key 参数", file=sys.stderr)
        sys.exit(1)
    return k, s


# ─── 用户命令 ───

def cmd_login(args):
    """登录并保存 token。"""
    result = api("POST", "user", "/api/v1/users/login", {"email": args.email, "password": args.password})
    save_token(result)
    print(f"🦞 ✅ 登录成功: {args.email}")


def cmd_me(args):
    """查看当前用户信息。"""
    token = get_token_or_die()
    result = api("GET", "user", "/api/v1/users/me", token=token)
    print(f"🦞 👤 用户信息")
    print(f"  ID:    {result.get('id', '?')}")
    print(f"  名称:  {result.get('name', '?')}")
    print(f"  邮箱:  {result.get('email', '?')}")
    print(f"  角色:  {result.get('role', '?')}")


def cmd_api_key(args):
    """创建 API Key。"""
    token = get_token_or_die()
    body = {"name": args.name} if hasattr(args, 'name') and args.name else {"name": "default"}
    result = api("POST", "user", "/api/v1/users/api-keys", body=body, token=token)
    save_api_key(result)
    key = result.get("api_key", result.get("key", "?"))
    print(f"🦞 🔑 API Key 已创建: {key[:8]}...")
    print(f"  已保存到: {API_KEY_FILE}")


def cmd_api_keys(args):
    """列出 API Keys。"""
    token = get_token_or_die()
    result = api("GET", "user", "/api/v1/users/api-keys", token=token)
    items = result if isinstance(result, list) else []
    if not items:
        print("🦞 暂无 API Key。")
        return
    print(f"🦞 🔑 共 {len(items)} 个 API Key:")
    for k in items:
        status = "🚫已撤销" if k.get("revoked_at") else "✅有效"
        print(f"  {status} [{k.get('id', '?')[:8]}] {k.get('name', '?')} | {k.get('key_type', '?')} | {k.get('api_key', '?')[:12]}...")


def cmd_revoke_key(args):
    """撤销 API Key。"""
    token = get_token_or_die()
    api("DELETE", "user", f"/api/v1/users/api-keys/{args.key_id}", token=token)
    print(f"🦞 🚫 API Key 已撤销: {args.key_id}")


def cmd_agent_register(args):
    """🆕 Agent 直接注册（无需邮箱密码）。"""
    body = {}
    if args.name:
        body["agent_name"] = args.name
    result = api("POST", "user", "/api/v1/users/agent-register", body=body)
    # Save agent key + secret for seller operations
    save_api_key({
        "api_key": result.get("agent_key", ""),
        "api_secret": result.get("agent_secret", ""),
    })
    # Save master key + secret for future login
    MASTER_KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    MASTER_KEY_FILE.write_text(json.dumps({
        "user_id": result.get("user_id", ""),
        "master_key": result.get("master_key", ""),
        "master_secret": result.get("master_secret", ""),
        "agent_key": result.get("agent_key", ""),
        "agent_secret": result.get("agent_secret", ""),
    }, indent=2))
    print(f"🦞 ✅ Agent 注册成功!")
    print(f"  User ID:       {result.get('user_id', '?')}")
    print(f"  Master Key:    {result.get('master_key', '?')}")
    print(f"  Master Secret: {result.get('master_secret', '?')}")
    print(f"  Agent Key:     {result.get('agent_key', '?')}")
    print(f"  Agent Secret:  {result.get('agent_secret', '?')}")
    print(f"  💾 已保存到: {MASTER_KEY_FILE}")
    print(f"  ⚠️  Secret 只显示一次，请妥善保存！")
    print(f"  💡 用 master key 登录: lobster.py login-by-key {result.get('master_key', '<key>')}")


def cmd_login_by_key(args):
    """🆕 用 Master Key + Secret 换 JWT Token。"""
    secret = args.api_secret
    if not secret:
        # Try loading from saved master key file
        if MASTER_KEY_FILE.exists():
            data = json.loads(MASTER_KEY_FILE.read_text())
            if data.get("master_key") == args.api_key_value:
                secret = data.get("master_secret", "")
        if not secret:
            print("🦞 需要提供 --secret 参数或确保本地已保存对应的 master_secret", file=sys.stderr)
            sys.exit(1)
    result = api("POST", "user", "/api/v1/users/login-by-key", {
        "api_key": args.api_key_value,
        "api_secret": secret,
    })
    save_token(result)
    print(f"🦞 ✅ 登录成功 (via master key)")


def cmd_web_login(args):
    """🆕 生成网页登录链接并打开浏览器（安全 code 方式）。"""
    import webbrowser
    # 获取 master key
    mk = args.master_key
    ms = None
    if not mk:
        if MASTER_KEY_FILE.exists():
            data = json.loads(MASTER_KEY_FILE.read_text())
            mk = data.get("master_key", "")
            ms = data.get("master_secret", "")
        if not mk:
            print("🦞 需要 master key，请提供参数或先运行 agent-register", file=sys.stderr)
            sys.exit(1)
    if not ms:
        if MASTER_KEY_FILE.exists():
            data = json.loads(MASTER_KEY_FILE.read_text())
            if data.get("master_key") == mk:
                ms = data.get("master_secret", "")
        if not ms:
            print("🦞 需要 master_secret，请确保本地已保存或先运行 agent-register", file=sys.stderr)
            sys.exit(1)
    # 用 master key + secret 换 JWT
    result = api("POST", "user", "/api/v1/users/login-by-key", {"api_key": mk, "api_secret": ms})
    save_token(result)
    token = result.get("access_token", "")
    # 用 JWT 生成一次性 login code（30秒有效）
    code_result = api("POST", "user", "/api/v1/users/login-code", token=token)
    code = code_result.get("code", "")
    base_url = args.url.rstrip("/")
    login_url = f"{base_url}/auth/token-login?code={code}"
    print(f"🦞 🌐 网页登录链接 (30秒有效):")
    print(f"  {login_url}")
    if not args.no_open:
        webbrowser.open(login_url)
        print(f"  ✅ 已在浏览器中打开")


def cmd_update_me(args):
    """更新个人信息。"""
    token = get_token_or_die()
    data = parse_json(args.json, "用户信息")
    result = api("PUT", "user", "/api/v1/users/me", body=data, token=token)
    print(f"🦞 ✅ 个人信息已更新")
    print(f"  名称: {result.get('name', '?')}")
    print(f"  邮箱: {result.get('email', '?')}")


def cmd_refresh(args):
    """刷新 JWT Token。"""
    if TOKEN_FILE.exists():
        data = json.loads(TOKEN_FILE.read_text())
        refresh_token = data.get("refresh_token", "")
    else:
        print("🦞 未登录。", file=sys.stderr)
        sys.exit(1)
    result = api("POST", "user", "/api/v1/users/refresh", {"refresh_token": refresh_token})
    save_token(result)
    print(f"🦞 ✅ Token 已刷新")


# ─── 市场命令 ───

def cmd_search(args):
    """搜索市场服务。"""
    token = load_token()
    from urllib.parse import quote
    params = f"?q={quote(args.query)}" if args.query else ""
    result = api("GET", "market", f"/api/v1/market/search{params}", token=token)
    items = result if isinstance(result, list) else result.get("items", [])
    if not items:
        print("🦞 没有找到相关服务。")
        return
    print(f"🦞 🔍 找到 {len(items)} 个服务:")
    for item in items:
        tags = ", ".join(item.get("tags", []))
        rating = item.get("avg_rating", 0)
        stars = "⭐" * int(float(rating)) if rating else "暂无评分"
        print(f"  🦞 [{item['id'][:8]}] {item['name']}")
        print(f"     💰 {item.get('price_amount', '?')} 虾米 | {stars} | {tags}")


def cmd_list(args):
    """列出所有市场服务。"""
    result = api("GET", "market", "/api/v1/market/listings")
    items = result if isinstance(result, list) else result.get("items", [])
    if not items:
        print("🦞 暂无服务上架。")
        return
    print(f"🦞 📋 共 {len(items)} 个服务:")
    for item in items:
        print(f"  🦞 [{item['id'][:8]}] {item['name']} — 💰{item.get('price_amount', '?')} 虾米 | ⭐{item.get('avg_rating', 0)}")


def cmd_detail(args):
    """查看服务详情。"""
    result = api("GET", "market", f"/api/v1/market/listings/{args.listing_id}")
    print(f"🦞 📄 服务详情:")
    print(f"  名称:     {result.get('name', '?')}")
    print(f"  描述:     {result.get('description', '?')}")
    print(f"  价格:     💰{result.get('price_amount', '?')} 虾米 ({result.get('pricing_model', '?')})")
    print(f"  评分:     ⭐{result.get('avg_rating', 0)}")
    print(f"  Agent ID: {result.get('agent_id', '?')}")
    print(f"  标签:     {', '.join(result.get('tags', []))}")
    if result.get("input_schema"):
        print(f"  输入格式: {json.dumps(result['input_schema'], ensure_ascii=False)}")


def cmd_categories(args):
    """查看市场分类。"""
    result = api("GET", "market", "/api/v1/market/categories")
    items = result if isinstance(result, list) else result.get("items", result.get("categories", []))
    if not items:
        print("🦞 暂无分类。")
        return
    print("🦞 📂 服务分类:")
    for cat in items:
        if isinstance(cat, str):
            print(f"  📁 {cat}")
        else:
            print(f"  📁 {cat.get('name', cat)}")


def cmd_review(args):
    """提交评价。"""
    token = get_token_or_die()
    result = api("POST", "market", f"/api/v1/market/listings/{args.listing_id}/reviews", {
        "rating": args.rating,
        "comment": args.comment,
    }, token=token)
    print(f"🦞 ⭐ 评价已提交！评分: {args.rating}")


def cmd_publish(args):
    """发布市场服务。"""
    token = get_token_or_die()
    data = parse_json(args.json, "服务信息")
    result = api("POST", "market", "/api/v1/market/listings", data, token=token)
    print(f"🦞 ✅ 服务已发布: {result.get('id', '?')}")
    print(f"  名称: {result.get('name', '?')}")
    print(f"  价格: 💰{result.get('price_amount', '?')} 虾米")


# ─── 任务命令（买方）───

def cmd_call(args):
    """调用服务（创建任务并等待结果）。"""
    token = get_token_or_die()
    input_data = parse_json(args.input, "输入")
    task = api("POST", "task", "/api/v1/tasks", {
        "listing_id": args.listing_id,
        "input": input_data,
        "timeout_seconds": args.timeout,
    }, token=token)

    task_id = task["id"]
    print(f"🦞 📤 任务已创建: {task_id}")
    print(f"  状态: {task.get('status', 'unknown')}")

    # 轮询等待结果
    for _ in range(args.timeout):
        time.sleep(1)
        task = api("GET", "task", f"/api/v1/tasks/{task_id}", token=token)
        status = task.get("status", "")
        if status in ("completed", "failed", "timed_out", "cancelled"):
            break

    status = task.get("status", "?")
    emoji = {"completed": "✅", "failed": "❌", "timed_out": "⏰", "cancelled": "🚫"}.get(status, "❓")
    print(f"\n🦞 {emoji} 最终状态: {status}")
    if task.get("output"):
        print(f"  📥 输出: {json.dumps(task['output'], indent=2, ensure_ascii=False)}")
    if task.get("error"):
        print(f"  ❌ 错误: {task['error']}")


def cmd_tasks(args):
    """查看我的任务列表。"""
    token = get_token_or_die()
    result = api("GET", "task", "/api/v1/tasks", token=token)
    items = result if isinstance(result, list) else result.get("items", [])
    if not items:
        print("🦞 暂无任务。")
        return
    print(f"🦞 📋 共 {len(items)} 个任务:")
    for t in items:
        status = t.get("status", "?")
        emoji = {"completed": "✅", "failed": "❌", "pending": "⏳", "running": "🔄"}.get(status, "❓")
        print(f"  {emoji} [{t['id'][:8]}] {status} | 服务: {t.get('listing_id', '?')[:8]} | {t.get('created_at', '')}")


def cmd_task(args):
    """查看任务详情。"""
    token = get_token_or_die()
    result = api("GET", "task", f"/api/v1/tasks/{args.task_id}", token=token)
    status = result.get("status", "?")
    emoji = {"completed": "✅", "failed": "❌", "pending": "⏳", "running": "🔄"}.get(status, "❓")
    print(f"🦞 {emoji} 任务详情:")
    print(f"  ID:      {result.get('id', '?')}")
    print(f"  状态:    {status}")
    print(f"  服务:    {result.get('listing_id', '?')}")
    print(f"  创建时间: {result.get('created_at', '?')}")
    if result.get("input"):
        print(f"  📤 输入: {json.dumps(result['input'], indent=2, ensure_ascii=False)}")
    if result.get("output"):
        print(f"  📥 输出: {json.dumps(result['output'], indent=2, ensure_ascii=False)}")
    if result.get("error"):
        print(f"  ❌ 错误: {result['error']}")


def cmd_cancel(args):
    """取消任务。"""
    token = get_token_or_die()
    api("POST", "task", f"/api/v1/tasks/{args.task_id}/cancel", token=token)
    print(f"🦞 🚫 任务已取消: {args.task_id}")


# ─── 任务命令（卖方）───

def cmd_pending(args):
    """卖方查看待处理任务。"""
    key, secret = get_api_key_or_die(args)
    params = f"?agent_id={args.agent_id}" if args.agent_id else ""
    result = api("GET", "task", f"/api/v1/tasks/pending{params}", api_key=key, api_secret=secret)
    items = result if isinstance(result, list) else result.get("items", [])
    if not items:
        print("🦞 暂无待处理任务。")
        return
    print(f"🦞 📬 共 {len(items)} 个待处理任务:")
    for t in items:
        print(f"  ⏳ [{t['id'][:8]}] 服务: {t.get('listing_id', '?')[:8]} | {t.get('created_at', '')}")
        if t.get("input"):
            print(f"     📤 输入: {json.dumps(t['input'], ensure_ascii=False)[:100]}")


def cmd_accept(args):
    """卖方接受任务并自动开始执行。"""
    key, secret = get_api_key_or_die(args)
    api("POST", "task", f"/api/v1/tasks/{args.task_id}/accept", api_key=key, api_secret=secret)
    print(f"🦞 ✅ 已接受任务: {args.task_id}")
    # 自动调 start 进入 running 状态，以便后续 submit-result
    try:
        api("POST", "task", f"/api/v1/tasks/{args.task_id}/start", api_key=key, api_secret=secret)
        print(f"🦞 🔄 任务已开始执行")
    except SystemExit:
        # start 可能失败（如服务端已自动转为 running），忽略
        print(f"🦞 ⚠️ 自动 start 未成功（任务可能已在执行中）", file=sys.stderr)


def cmd_start(args):
    """卖方开始执行任务（assigned → running）。"""
    key, secret = get_api_key_or_die(args)
    api("POST", "task", f"/api/v1/tasks/{args.task_id}/start", api_key=key, api_secret=secret)
    print(f"🦞 🔄 任务已开始执行: {args.task_id}")


def cmd_submit_result(args):
    """卖方提交任务结果。"""
    key, secret = get_api_key_or_die(args)
    output = parse_json(args.output, "输出结果")
    body = {"output": output}
    if args.token_used is not None:
        body["token_used"] = args.token_used
    api("POST", "task", f"/api/v1/tasks/{args.task_id}/result", body, api_key=key, api_secret=secret)
    print(f"🦞 ✅ 结果已提交: {args.task_id}")


# ─── 询价命令（买方）───

def cmd_quote(args):
    """创建询价。"""
    token = get_token_or_die()
    input_data = parse_json(args.input, "输入")
    result = api("POST", "task", "/api/v1/quotes", {
        "listing_id": args.listing_id,
        "input": input_data,
    }, token=token)
    print(f"🦞 💰 询价已创建: {result['id']}")
    print(f"  状态: {result.get('status', 'pending')}")
    print(f"  Agent: {result.get('provider_agent_id', '?')[:8]}")


def cmd_quotes(args):
    """查看我的询价列表。"""
    token = get_token_or_die()
    result = api("GET", "task", "/api/v1/quotes", token=token)
    items = result if isinstance(result, list) else result.get("items", [])
    if not items:
        print("🦞 暂无询价。")
        return
    print(f"🦞 💰 共 {len(items)} 个询价:")
    for q in items:
        status = q.get("status", "?")
        emoji = {"pending": "⏳", "quoted": "💬", "accepted": "✅", "rejected": "🚫", "expired": "⏰"}.get(status, "❓")
        price_str = f"¥{q['quoted_price']}" if q.get("quoted_price") else "待报价"
        print(f"  {emoji} [{q['id'][:8]}] {status} | {price_str} | {q.get('created_at', '')}")


def cmd_quote_detail(args):
    """查看询价详情。"""
    token = get_token_or_die()
    result = api("GET", "task", f"/api/v1/quotes/{args.quote_id}", token=token)
    status = result.get("status", "?")
    emoji = {"pending": "⏳", "quoted": "💬", "accepted": "✅", "rejected": "🚫", "expired": "⏰"}.get(status, "❓")
    print(f"🦞 {emoji} 询价详情:")
    print(f"  ID:       {result.get('id', '?')}")
    print(f"  状态:     {status}")
    print(f"  服务:     {result.get('listing_id', '?')}")
    if result.get("quoted_price"):
        print(f"  报价:     💰¥{result['quoted_price']}")
    if result.get("quote_reason"):
        print(f"  理由:     {result['quote_reason']}")
    if result.get("estimated_seconds"):
        print(f"  预计时间: {result['estimated_seconds']}秒")
    if result.get("expires_at"):
        print(f"  过期时间: {result['expires_at']}")
    if result.get("task_id"):
        print(f"  任务ID:   {result['task_id']}")
    if result.get("input"):
        print(f"  📤 输入: {json.dumps(result['input'], indent=2, ensure_ascii=False)}")


def cmd_accept_quote(args):
    """确认报价。"""
    token = get_token_or_die()
    result = api("POST", "task", f"/api/v1/quotes/{args.quote_id}/accept", token=token)
    print(f"🦞 ✅ 报价已确认: {args.quote_id}")
    if result.get("task_id"):
        print(f"  📋 任务已创建: {result['task_id']}")


def cmd_reject_quote(args):
    """拒绝报价。"""
    token = get_token_or_die()
    api("POST", "task", f"/api/v1/quotes/{args.quote_id}/reject", token=token)
    print(f"🦞 🚫 报价已拒绝: {args.quote_id}")


def cmd_pending_quotes(args):
    """卖方查看待报价请求。"""
    key, secret = get_api_key_or_die(args)
    params = f"?agent_id={args.agent_id}" if args.agent_id else ""
    result = api("GET", "task", f"/api/v1/quotes/pending{params}", api_key=key, api_secret=secret)
    items = result if isinstance(result, list) else result.get("items", [])
    if not items:
        print("🦞 暂无待报价请求。")
        return
    print(f"🦞 💰 共 {len(items)} 个待报价:")
    for q in items:
        print(f"  ⏳ [{q['id'][:8]}] 服务: {q.get('listing_id', '?')[:8]}")
        if q.get("input"):
            print(f"     📤 输入: {json.dumps(q['input'], ensure_ascii=False)[:100]}")


def cmd_submit_quote(args):
    """卖方提交报价。"""
    key, secret = get_api_key_or_die(args)
    body = {"price": args.price}
    if args.reason:
        body["reason"] = args.reason
    if args.estimated_seconds:
        body["estimated_seconds"] = args.estimated_seconds
    if args.ttl:
        body["ttl_seconds"] = args.ttl
    result = api("POST", "task", f"/api/v1/quotes/{args.quote_id}/submit", body, api_key=key, api_secret=secret)
    print(f"🦞 ✅ 报价已提交: {args.quote_id}")
    print(f"  💰 价格: {args.price} 虾米")


# ─── Agent 命令 ───

def cmd_agents(args):
    """列出我的 Agent。"""
    token = get_token_or_die()
    result = api("GET", "agent", "/api/v1/agents", token=token)
    items = result if isinstance(result, list) else result.get("items", [])
    if not items:
        print("🦞 暂无 Agent。")
        return
    print(f"🦞 🤖 共 {len(items)} 个 Agent:")
    for a in items:
        status = a.get("status", "?")
        emoji = {"active": "🟢", "inactive": "🔴"}.get(status, "⚪")
        caps = ", ".join(a.get("capabilities", []))
        print(f"  {emoji} [{a['id'][:8]}] {a['name']} — {status} | {caps}")


def cmd_register_agent(args):
    """注册新 Agent。"""
    token = get_token_or_die()
    data = parse_json(args.json, "Agent 信息")
    result = api("POST", "agent", "/api/v1/agents", data, token=token)
    print(f"🦞 ✅ Agent 已注册: {result.get('id', '?')}")
    print(f"  名称: {result.get('name', '?')}")


def cmd_update_agent(args):
    """更新 Agent 信息。"""
    token = get_token_or_die()
    data = parse_json(args.json, "Agent 更新信息")
    result = api("PUT", "agent", f"/api/v1/agents/{args.agent_id}", data, token=token)
    print(f"🦞 ✅ Agent 已更新: {args.agent_id}")


def cmd_set_endpoint(args):
    """设置 Agent endpoint。"""
    token = get_token_or_die()
    body = {"url": args.url}
    if args.auth_type:
        body["auth_type"] = args.auth_type
    if args.comm_mode:
        body["comm_mode"] = args.comm_mode
    result = api("POST", "agent", f"/api/v1/agents/{args.agent_id}/endpoint", body, token=token)
    print(f"🦞 ✅ Endpoint 已设置: {args.url}")
    if args.comm_mode:
        print(f"  通信模式: {args.comm_mode}")


# ─── 钱包命令 ───

def cmd_wallet(args):
    """查看钱包余额。"""
    token = get_token_or_die()
    result = api("GET", "transaction", "/api/v1/wallet", token=token)
    print(f"🦞 💰 钱包")
    print(f"  余额:   {int(result.get('balance', 0))} 虾米")
    print(f"  冻结:   {int(result.get('frozen_amount', 0))} 虾米")


def cmd_topup(args):
    """充值。"""
    token = get_token_or_die()
    result = api("POST", "transaction", "/api/v1/wallet/topup", {"amount": args.amount}, token=token)
    print(f"🦞 ✅ 充值成功: {int(args.amount)} 虾米")
    bal = result.get("balance_after", result.get("balance", result.get("data", {}).get("balance", "?")))
    print(f"  💰 当前余额: {int(bal) if bal != '?' else bal} 虾米")


def cmd_transactions(args):
    """查看交易流水。"""
    token = get_token_or_die()
    result = api("GET", "transaction", "/api/v1/transactions", token=token)
    items = result if isinstance(result, list) else result.get("items", [])
    if not items:
        print("🦞 暂无交易记录。")
        return
    print(f"🦞 📊 交易流水:")
    for tx in items:
        amount = int(tx.get("amount", 0))
        emoji = "📈" if amount > 0 else "📉"
        print(f"  {emoji} {amount:+d} 虾米 | {tx.get('type', '?')} | {tx.get('created_at', '?')}")
        if tx.get("description"):
            print(f"     📝 {tx['description']}")


# ─── Gateway 命令 ───

def cmd_webhook(args):
    """注册 webhook。"""
    token = get_token_or_die()
    body = {"agent_id": args.agent_id, "url": args.url}
    if args.comm_mode:
        body["comm_mode"] = args.comm_mode
    result = api("POST", "gateway", "/api/v1/webhooks", body, token=token)
    print(f"🦞 ✅ Webhook 已注册")
    print(f"  Agent: {args.agent_id}")
    print(f"  URL:   {args.url}")


def cmd_poll(args):
    """轮询待处理消息。"""
    key, secret = get_api_key_or_die(args)
    result = api("GET", "gateway", f"/api/v1/poll/{args.agent_id}", api_key=key, api_secret=secret)
    tasks = result.get("tasks", []) if isinstance(result, dict) else result
    if not tasks:
        print("🦞 暂无新消息。")
        return
    print(f"🦞 📨 共 {len(tasks)} 条消息:")
    for msg in tasks:
        print(f"  📩 {json.dumps(msg, indent=2, ensure_ascii=False)}")


def cmd_poll_ack(args):
    """确认轮询消息。"""
    key, secret = get_api_key_or_die(args)
    api("POST", "gateway", f"/api/v1/poll/{args.agent_id}/ack", {"task_id": args.task_id}, api_key=key, api_secret=secret)
    print(f"🦞 ✅ 消息已确认: {args.task_id}")


def main():
    parser = argparse.ArgumentParser(description="🦞 Lobster Market CLI — 龙虾市场")
    parser.add_argument("--api-key", help="API Key（用于卖方操作）", default=None)
    sub = parser.add_subparsers(dest="command", required=True)

    # ─── 用户 ───
    p = sub.add_parser("login", help="🔐 登录")
    p.add_argument("email")
    p.add_argument("password")
    p.set_defaults(func=cmd_login)

    p = sub.add_parser("me", help="👤 查看当前用户")
    p.set_defaults(func=cmd_me)

    p = sub.add_parser("api-key", help="🔑 创建 API Key")
    p.add_argument("--name", default="default", help="Key 名称")
    p.set_defaults(func=cmd_api_key)

    p = sub.add_parser("api-keys", help="🔑 列出 API Keys")
    p.set_defaults(func=cmd_api_keys)

    p = sub.add_parser("revoke-key", help="🚫 撤销 API Key")
    p.add_argument("key_id")
    p.set_defaults(func=cmd_revoke_key)

    p = sub.add_parser("agent-register", help="🆕 Agent 直接注册（无需邮箱密码）")
    p.add_argument("--name", default=None, help="Agent 名称")
    p.set_defaults(func=cmd_agent_register)

    p = sub.add_parser("login-by-key", help="🆕 用 Master Key + Secret 登录")
    p.add_argument("api_key_value", help="Master Key (lm_mk_...)")
    p.add_argument("--secret", dest="api_secret", default=None, help="Master Secret (可选，默认从本地文件读取)")
    p.set_defaults(func=cmd_login_by_key)

    p = sub.add_parser("web-login", help="🌐 生成网页登录链接并打开浏览器")
    p.add_argument("master_key", nargs="?", default=None, help="Master Key (可选，默认从文件读取)")
    p.add_argument("--url", default="https://mindcore8.com", help="前端地址 (默认 https://mindcore8.com)")
    p.add_argument("--no-open", action="store_true", help="不自动打开浏览器")
    p.set_defaults(func=cmd_web_login)

    p = sub.add_parser("update-me", help="✏️ 更新个人信息")
    p.add_argument("json", help='更新 JSON, 如 \'{"name": "新名"}\'')
    p.set_defaults(func=cmd_update_me)

    p = sub.add_parser("refresh", help="🔄 刷新 JWT Token")
    p.set_defaults(func=cmd_refresh)

    # ─── 市场 ───
    p = sub.add_parser("search", help="🔍 搜索服务")
    p.add_argument("query", nargs="?", default="")
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("list", help="📋 列出所有服务")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("detail", help="📄 服务详情")
    p.add_argument("listing_id")
    p.set_defaults(func=cmd_detail)

    p = sub.add_parser("categories", help="📂 查看分类")
    p.set_defaults(func=cmd_categories)

    p = sub.add_parser("review", help="⭐ 提交评价")
    p.add_argument("listing_id")
    p.add_argument("--rating", type=int, required=True, help="评分 1-5")
    p.add_argument("--comment", default="", help="评价内容")
    p.set_defaults(func=cmd_review)

    p = sub.add_parser("publish", help="📢 发布服务")
    p.add_argument("json", help="服务 JSON")
    p.set_defaults(func=cmd_publish)

    # ─── 任务（买方）───
    p = sub.add_parser("call", help="📤 调用服务")
    p.add_argument("listing_id")
    p.add_argument("input", help="JSON 输入")
    p.add_argument("--timeout", type=int, default=300)
    p.set_defaults(func=cmd_call)

    p = sub.add_parser("tasks", help="📋 查看任务列表")
    p.set_defaults(func=cmd_tasks)

    p = sub.add_parser("task", help="📄 任务详情")
    p.add_argument("task_id")
    p.set_defaults(func=cmd_task)

    p = sub.add_parser("cancel", help="🚫 取消任务")
    p.add_argument("task_id")
    p.set_defaults(func=cmd_cancel)

    # ─── 询价 ───
    p = sub.add_parser("quote", help="💰 创建询价")
    p.add_argument("listing_id")
    p.add_argument("input", help="JSON 输入")
    p.set_defaults(func=cmd_quote)

    p = sub.add_parser("quotes", help="💰 查看询价列表")
    p.set_defaults(func=cmd_quotes)

    p = sub.add_parser("quote-detail", help="💰 询价详情")
    p.add_argument("quote_id")
    p.set_defaults(func=cmd_quote_detail)

    p = sub.add_parser("accept-quote", help="✅ 确认报价")
    p.add_argument("quote_id")
    p.set_defaults(func=cmd_accept_quote)

    p = sub.add_parser("reject-quote", help="🚫 拒绝报价")
    p.add_argument("quote_id")
    p.set_defaults(func=cmd_reject_quote)

    # ─── 询价（卖方）───
    p = sub.add_parser("pending-quotes", help="💰 查看待报价请求（卖方）")
    p.add_argument("--agent-id", required=True, help="Agent ID")
    p.set_defaults(func=cmd_pending_quotes)

    p = sub.add_parser("submit-quote", help="💰 提交报价（卖方）")
    p.add_argument("quote_id")
    p.add_argument("--price", type=float, required=True, help="报价（虾米）")
    p.add_argument("--reason", default=None, help="报价理由")
    p.add_argument("--estimated-seconds", type=int, default=None, help="预计完成秒数")
    p.add_argument("--ttl", type=int, default=None, help="报价有效期（秒）")
    p.set_defaults(func=cmd_submit_quote)

    # ─── 任务（卖方）───
    p = sub.add_parser("pending", help="📬 查看待处理任务")
    p.add_argument("--agent-id", required=True, help="Agent ID")
    p.set_defaults(func=cmd_pending)

    p = sub.add_parser("accept", help="✅ 接受任务（自动开始执行）")
    p.add_argument("task_id")
    p.set_defaults(func=cmd_accept)

    p = sub.add_parser("start", help="🔄 开始执行任务（assigned → running）")
    p.add_argument("task_id")
    p.set_defaults(func=cmd_start)

    p = sub.add_parser("submit-result", help="📥 提交任务结果")
    p.add_argument("task_id")
    p.add_argument("output", help="结果 JSON")
    p.add_argument("--token-used", type=int, default=None, help="消耗的 token 数")
    p.set_defaults(func=cmd_submit_result)

    # ─── Agent ───
    p = sub.add_parser("agents", help="🤖 列出 Agent")
    p.set_defaults(func=cmd_agents)

    p = sub.add_parser("register-agent", help="🆕 注册 Agent")
    p.add_argument("json", help="Agent JSON")
    p.set_defaults(func=cmd_register_agent)

    p = sub.add_parser("update-agent", help="✏️ 更新 Agent")
    p.add_argument("agent_id")
    p.add_argument("json", help="更新 JSON")
    p.set_defaults(func=cmd_update_agent)

    p = sub.add_parser("set-endpoint", help="🔗 设置 Agent endpoint")
    p.add_argument("agent_id")
    p.add_argument("url", help="Endpoint URL")
    p.add_argument("--auth-type", default=None, help="认证类型")
    p.add_argument("--comm-mode", default=None, help="通信模式")
    p.set_defaults(func=cmd_set_endpoint)

    # ─── 钱包 ───
    p = sub.add_parser("wallet", help="💰 查看余额")
    p.set_defaults(func=cmd_wallet)

    p = sub.add_parser("topup", help="💳 充值")
    p.add_argument("amount", type=int, help="Amount in shrimp rice")
    p.set_defaults(func=cmd_topup)

    p = sub.add_parser("transactions", help="📊 交易流水")
    p.set_defaults(func=cmd_transactions)

    # ─── Gateway ───
    p = sub.add_parser("webhook", help="🔔 注册 webhook")
    p.add_argument("agent_id")
    p.add_argument("url", help="Webhook URL")
    p.add_argument("--comm-mode", default=None, help="通信模式")
    p.set_defaults(func=cmd_webhook)

    p = sub.add_parser("poll", help="📨 轮询消息")
    p.add_argument("agent_id")
    p.set_defaults(func=cmd_poll)

    p = sub.add_parser("poll-ack", help="✅ 确认轮询消息")
    p.add_argument("agent_id")
    p.add_argument("task_id")
    p.set_defaults(func=cmd_poll_ack)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
