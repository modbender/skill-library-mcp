#!/usr/bin/env python3
"""
Codex Auth File Cleaner — 监控、检查、禁用、删除无效的 codex 认证文件。

支持从 config.json 读取配置，执行完输出结构化报告。

用法:
  python3 codex_cleaner.py status          # 查看状态
  python3 codex_cleaner.py check           # 检查并禁用 401
  python3 codex_cleaner.py delete          # 双重验证后删除
  python3 codex_cleaner.py clean           # 一键清理 (check + delete)
  python3 codex_cleaner.py clean --report  # 清理并输出 Telegram 报告格式

配置优先级: 命令行参数 > 环境变量 > config.json
"""

import argparse
import json
import logging
import os
import signal
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent.resolve()
CONFIG_PATH = SCRIPT_DIR.parent / "config.json"

API_URL = ""
HEADERS = {}
CONFIG = {}


def load_config() -> dict:
    """Load config from config.json."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {}


def save_config(config: dict):
    """Save config to config.json."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    log.info("✅ 配置已保存到 %s", CONFIG_PATH)


def setup_wizard() -> dict:
    """Interactive setup wizard when config is missing."""
    print()
    print("=" * 50)
    print("🔧 Codex Cleaner 首次配置向导")
    print("=" * 50)
    print()

    # Load existing config or create default
    config = load_config()
    default_url = config.get("cpa_url", "")

    # CPA URL
    print(f"📡 CPA 管理 API 地址")
    if default_url:
        print(f"   当前: {default_url}")
        url_input = input(f"   输入 URL (回车保留当前): ").strip()
    else:
        print(f"   示例: http://your-host:8318")
        url_input = input(f"   输入 URL: ").strip()
    cpa_url = url_input if url_input else default_url
    if not cpa_url:
        print("❌ URL 不能为空！")
        sys.exit(1)

    # CPA Key
    default_key = config.get("cpa_key", "")
    print()
    print(f"🔑 CPA Admin Key")
    if default_key:
        masked = default_key[:4] + "****" + default_key[-4:] if len(default_key) > 8 else "****"
        print(f"   当前: {masked}")
        key_input = input(f"   输入 Key (回车保留当前): ").strip()
        cpa_key = key_input if key_input else default_key
    else:
        cpa_key = input(f"   输入 Key: ").strip()
    if not cpa_key:
        print("❌ Key 不能为空！")
        sys.exit(1)

    # Concurrency
    print()
    default_conc = config.get("concurrency", 20)
    print(f"⚡ 并发数 (默认: {default_conc})")
    conc_input = input(f"   输入并发数 (回车使用默认): ").strip()
    concurrency = int(conc_input) if conc_input.isdigit() else default_conc

    # Monitor interval
    print()
    default_interval = config.get("monitor_interval", 300)
    print(f"⏱️ 监控间隔秒数 (默认: {default_interval})")
    interval_input = input(f"   输入间隔 (回车使用默认): ").strip()
    interval = int(interval_input) if interval_input.isdigit() else default_interval

    # Notification settings
    print()
    notify_config = config.get("notify", {"enabled": True, "channel": "telegram", "chat_id": ""})
    default_channel = notify_config.get("channel", "telegram")
    default_chat_id = notify_config.get("chat_id", "")

    print(f"📢 通知设置 (清理完成后推送结果)")
    print(f"   支持的频道: telegram, discord")
    if default_channel:
        print(f"   当前频道: {default_channel}")
        channel_input = input(f"   输入频道 (回车保留当前): ").strip()
    else:
        channel_input = input(f"   输入频道 (默认 telegram): ").strip()
    notify_channel = channel_input if channel_input else default_channel or "telegram"

    print()
    print(f"💬 Chat ID (你的聊天 ID，用于接收通知)")
    print(f"   Telegram: 发送 /start 给 @userinfobot 获取")
    if default_chat_id:
        print(f"   当前: {default_chat_id}")
        chat_id_input = input(f"   输入 Chat ID (回车保留当前): ").strip()
    else:
        chat_id_input = input(f"   输入 Chat ID: ").strip()
    notify_chat_id = chat_id_input if chat_id_input else default_chat_id

    print()
    enable_notify = True
    if not notify_chat_id:
        print("   ⚠️ 未填写 Chat ID，通知功能将关闭")
        enable_notify = False

    config.update({
        "cpa_url": cpa_url,
        "cpa_key": cpa_key,
        "concurrency": concurrency,
        "monitor_interval": interval,
        "notify": {
            "enabled": enable_notify,
            "channel": notify_channel,
            "chat_id": notify_chat_id,
        },
    })

    save_config(config)

    # Test connection
    print()
    print("🔗 测试连接...")
    init_config(cpa_url, cpa_key)
    resp = api_get("/v0/management/auth-files")
    if resp["status_code"] == 200:
        files = resp["json"].get("files", [])
        print(f"✅ 连接成功！当前共 {len(files)} 个认证文件")
    else:
        print(f"⚠️ 连接失败 (status={resp['status_code']}): {resp['body'][:200]}")
        print("   配置已保存，你可以稍后修改 config.json 重试")

    print()
    print("=" * 50)
    print("✅ 配置完成！现在可以使用以下命令：")
    print("   python3 codex_cleaner.py status")
    print("   python3 codex_cleaner.py clean --report")
    print("=" * 50)
    print()

    return config


def init_config(url: str, key: str):
    global API_URL, HEADERS
    API_URL = url.rstrip("/")
    HEADERS = {
        "Accept": "application/json, text/plain, */*",
        "Authorization": f"Bearer {key}",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }


# ---------------------------------------------------------------------------
# HTTP helpers (stdlib only, no requests dependency)
# ---------------------------------------------------------------------------
def _request(method: str, url: str, headers: dict = None, data: bytes = None, timeout: int = 30) -> dict:
    hdrs = {**(headers or HEADERS)}
    req = Request(url, data=data, headers=hdrs, method=method)
    try:
        with urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return {"status_code": resp.status, "body": body, "json": json.loads(body) if body else {}}
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"status_code": e.code, "body": body, "json": {}}
    except URLError as e:
        return {"status_code": -1, "body": str(e.reason), "json": {}}
    except Exception as e:
        return {"status_code": -1, "body": str(e), "json": {}}


def api_get(path: str) -> dict:
    return _request("GET", f"{API_URL}{path}")


def api_post(path: str, payload: dict) -> dict:
    hdrs = {**HEADERS, "Content-Type": "application/json"}
    return _request("POST", f"{API_URL}{path}", headers=hdrs, data=json.dumps(payload).encode())


def api_patch(path: str, payload: dict) -> dict:
    hdrs = {**HEADERS, "Content-Type": "application/json"}
    return _request("PATCH", f"{API_URL}{path}", headers=hdrs, data=json.dumps(payload).encode())


def api_delete(path: str, params: dict = None) -> dict:
    url = f"{API_URL}{path}"
    if params:
        url += "?" + urlencode(params)
    return _request("DELETE", url)


# ---------------------------------------------------------------------------
# Core operations
# ---------------------------------------------------------------------------
def get_auth_files() -> list:
    resp = api_get("/v0/management/auth-files")
    if resp["status_code"] != 200:
        log.error("Failed to fetch auth files: %s", resp["body"])
        return []
    files = resp["json"].get("files", [])
    log.info("Fetched %d auth files", len(files))
    return files


def check_quota(file_info: dict) -> dict:
    auth_index = file_info["auth_index"]
    account_id = file_info.get("id_token", {}).get("chatgpt_account_id", "")
    file_id = file_info["id"]

    payload = {
        "authIndex": auth_index,
        "method": "GET",
        "url": "https://chatgpt.com/backend-api/wham/usage",
        "header": {
            "Authorization": "Bearer $TOKEN$",
            "Content-Type": "application/json",
            "User-Agent": "codex_cli_rs/0.76.0 (Debian 13.0.0; x86_64) WindowsTerminal",
            "Chatgpt-Account-Id": account_id,
        },
    }
    resp = api_post("/v0/management/api-call", payload)
    if resp["status_code"] == 200:
        data = resp["json"]
        sc = data.get("status_code", -1)
        body = data.get("body", "")
        return {"id": file_id, "status_code": sc, "body": body}
    else:
        return {"id": file_id, "status_code": -1, "body": resp["body"]}


def disable_file(file_id: str) -> bool:
    payload = {"name": file_id, "disabled": True}
    resp = api_patch("/v0/management/auth-files/status", payload)
    if resp["status_code"] == 200 and resp["json"].get("status") == "ok":
        log.info("✅ Disabled: %s", file_id)
        return True
    log.warning("❌ Disable failed: %s — %s", file_id, resp["body"])
    return False


def delete_file(file_id: str) -> bool:
    resp = api_delete("/v0/management/auth-files", params={"name": file_id})
    if resp["status_code"] == 200 and resp["json"].get("status") == "ok":
        log.info("🗑️ Deleted: %s", file_id)
        return True
    log.warning("❌ Delete failed: %s — %s", file_id, resp["body"])
    return False


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------
def cmd_status(args) -> dict:
    files = get_auth_files()
    codex_files = [f for f in files if f.get("provider") == "codex"]
    active = [f for f in codex_files if not f.get("disabled")]
    disabled = [f for f in codex_files if f.get("disabled")]
    non_codex = [f for f in files if f.get("provider") != "codex"]

    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_files": len(files),
        "codex_total": len(codex_files),
        "codex_active": len(active),
        "codex_disabled": len(disabled),
        "non_codex": len(non_codex),
    }

    if getattr(args, "output_json", False):
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        log.info("=" * 50)
        log.info("📊 CPA Auth Files Status")
        log.info("=" * 50)
        log.info("Total files:      %d", summary["total_files"])
        log.info("Codex total:      %d", summary["codex_total"])
        log.info("  ├─ Active:      %d", summary["codex_active"])
        log.info("  └─ Disabled:    %d", summary["codex_disabled"])
        log.info("Non-codex:        %d", summary["non_codex"])
        log.info("=" * 50)

    return summary


def cmd_check(args) -> dict:
    concurrency = getattr(args, "concurrency", 20)
    log.info("🔍 [check] Start. concurrency=%d", concurrency)
    files = get_auth_files()
    codex_files = [f for f in files if f.get("provider") == "codex" and not f.get("disabled")]
    log.info("Found %d active codex auth files", len(codex_files))

    if not codex_files:
        log.info("No active codex files to check.")
        return {"checked": 0, "found_401": 0, "disabled": 0}

    results = []
    total = len(codex_files)
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = {pool.submit(check_quota, f): f for f in codex_files}
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            results.append(result)
            status_emoji = "❌" if result["status_code"] == 401 else "✅"
            log.info("[check] %d/%d %s id=%s status=%s", i, total, status_emoji, result["id"], result["status_code"])

    invalid = [r for r in results if r["status_code"] == 401]
    log.info("Found %d files with 401, disabling...", len(invalid))

    disabled_count = 0
    for r in invalid:
        if disable_file(r["id"]):
            disabled_count += 1

    summary = {"checked": len(results), "found_401": len(invalid), "disabled": disabled_count}
    log.info("✅ [check] Done. checked=%d, found_401=%d, disabled=%d",
             summary["checked"], summary["found_401"], summary["disabled"])
    return summary


def cmd_delete(args) -> dict:
    concurrency = getattr(args, "concurrency", 20)
    log.info("🗑️ [delete] Start. concurrency=%d", concurrency)
    files = get_auth_files()
    targets = [f for f in files if f.get("provider") == "codex" and f.get("disabled") is True]
    log.info("Found %d disabled codex files", len(targets))

    if not targets:
        log.info("No disabled codex files to delete.")
        return {"found": 0, "verified": 0, "deleted": 0, "skipped": 0}

    # --- Round 1 ---
    log.info("🔄 Round 1 verification...")
    first_results = []
    total = len(targets)
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = {pool.submit(check_quota, f): f for f in targets}
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            first_results.append(result)
            log.info("[delete] Verify#1 %d/%d id=%s status=%s", i, total, result["id"], result["status_code"])

    first_401_ids = {r["id"] for r in first_results if r["status_code"] == 401}
    first_401_targets = [f for f in targets if f["id"] in first_401_ids]
    first_skipped = len(first_results) - len(first_401_ids)

    if not first_401_targets:
        log.info("No files confirmed 401 in round 1.")
        return {"found": len(targets), "verified": 0, "deleted": 0, "skipped": len(targets)}

    # --- Round 2 ---
    log.info("⏳ Sleeping 2s before round 2...")
    time.sleep(2)
    log.info("🔄 Round 2 verification...")
    second_results = []
    total2 = len(first_401_targets)
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = {pool.submit(check_quota, f): f for f in first_401_targets}
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            second_results.append(result)
            log.info("[delete] Verify#2 %d/%d id=%s status=%s", i, total2, result["id"], result["status_code"])

    deletable = [r for r in second_results if r["status_code"] == 401]
    second_skipped = len(second_results) - len(deletable)

    # --- Delete ---
    deleted_count = 0
    for r in deletable:
        if delete_file(r["id"]):
            deleted_count += 1

    total_skipped = first_skipped + second_skipped
    summary = {"found": len(targets), "verified": len(deletable), "deleted": deleted_count, "skipped": total_skipped}
    log.info("✅ [delete] Done. found=%d, verified=%d, deleted=%d, skipped=%d",
             summary["found"], summary["verified"], summary["deleted"], summary["skipped"])
    return summary


def cmd_clean(args) -> dict:
    """Full clean: check + disable, then delete. Optionally output report."""
    log.info("🧹 [clean] Full clean cycle start")

    # --- Before: get initial status ---
    files_before = get_auth_files()
    codex_before = [f for f in files_before if f.get("provider") == "codex"]
    active_before = len([f for f in codex_before if not f.get("disabled")])
    disabled_before = len([f for f in codex_before if f.get("disabled")])

    check_result = cmd_check(args)
    delete_result = cmd_delete(args)

    # --- After: get final status ---
    files_after = get_auth_files()
    codex_after = [f for f in files_after if f.get("provider") == "codex"]
    active_after = len([f for f in codex_after if not f.get("disabled")])
    disabled_after = len([f for f in codex_after if f.get("disabled")])

    now = datetime.now()
    summary = {
        "timestamp": now.isoformat(),
        "before": {
            "total": len(codex_before),
            "active": active_before,
            "disabled": disabled_before,
        },
        "check": check_result,
        "delete": delete_result,
        "after": {
            "total": len(codex_after),
            "active": active_after,
            "disabled": disabled_after,
        },
    }

    log.info("🧹 [clean] Full cycle done.")

    # --- Generate report ---
    if getattr(args, "report", False):
        report = format_report(summary, now)
        print(report)
    elif getattr(args, "output_json", False):
        print(json.dumps(summary, ensure_ascii=False, indent=2))

    return summary


def format_report(summary: dict, now: datetime) -> str:
    """Format a human-readable report for Telegram."""
    before = summary["before"]
    after = summary["after"]
    check = summary["check"]
    delete = summary["delete"]

    lines = [
        f"🧹 *Codex 认证清理报告*",
        f"⏰ {now.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"📊 *清理前*",
        f"  总计: {before['total']} | 可用: {before['active']} | 已禁用: {before['disabled']}",
        "",
        f"🔍 *检查阶段*",
        f"  检测: {check['checked']} | 失效(401): {check['found_401']} | 已禁用: {check['disabled']}",
        "",
        f"🗑️ *删除阶段*",
        f"  待删: {delete['found']} | 验证通过: {delete['verified']} | 已删除: {delete['deleted']} | 跳过: {delete['skipped']}",
        "",
        f"📊 *清理后*",
        f"  总计: {after['total']} | ✅可用: {after['active']} | ⛔已禁用: {after['disabled']}",
    ]

    # Highlight if something was cleaned
    cleaned = check["found_401"] + delete["deleted"]
    if cleaned > 0:
        lines.append("")
        lines.append(f"⚡ 本次清理: 禁用 {check['disabled']} + 删除 {delete['deleted']} = {check['disabled'] + delete['deleted']} 个无效文件")
    else:
        lines.append("")
        lines.append("✨ 全部正常，无需清理")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    # Load config.json first
    global CONFIG
    CONFIG = load_config()

    parser = argparse.ArgumentParser(
        description="Codex Auth File Cleaner — 监控、检查、禁用、删除无效认证文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Config priority: CLI args > env vars > config.json
    default_url = os.environ.get("CPA_URL", CONFIG.get("cpa_url", ""))
    default_key = os.environ.get("CPA_KEY", CONFIG.get("cpa_key", ""))
    default_concurrency = CONFIG.get("concurrency", 20)
    default_interval = CONFIG.get("monitor_interval", 300)

    parser.add_argument("--url", default=default_url, help="CPA API URL")
    parser.add_argument("--key", default=default_key, help="CPA admin key")
    parser.add_argument("--setup", action="store_true", help="Run setup wizard")

    sub = parser.add_subparsers(dest="command")

    # status
    status_p = sub.add_parser("status", help="Show auth files status summary")
    status_p.add_argument("--json", dest="output_json", action="store_true")

    # check
    check_p = sub.add_parser("check", help="Check quota and disable 401 files")
    check_p.add_argument("-c", "--concurrency", type=int, default=default_concurrency)

    # delete
    delete_p = sub.add_parser("delete", help="Double-verify then delete disabled 401 files")
    delete_p.add_argument("-c", "--concurrency", type=int, default=default_concurrency)

    # clean
    clean_p = sub.add_parser("clean", help="Full clean: check + disable + delete")
    clean_p.add_argument("-c", "--concurrency", type=int, default=default_concurrency)
    clean_p.add_argument("--report", action="store_true", help="Output Telegram-friendly report")
    clean_p.add_argument("--json", dest="output_json", action="store_true", help="Output JSON")

    # monitor (kept for standalone use)
    monitor_p = sub.add_parser("monitor", help="Monitor mode: run clean in a loop")
    monitor_p.add_argument("-c", "--concurrency", type=int, default=default_concurrency)
    monitor_p.add_argument("-i", "--interval", type=int, default=default_interval)

    # setup
    sub.add_parser("setup", help="Run interactive setup wizard")

    args = parser.parse_args()

    # --- Setup wizard trigger ---
    if args.command == "setup" or getattr(args, "setup", False):
        CONFIG = setup_wizard()
        if not args.command or args.command == "setup":
            return
        # Reload after setup
        default_url = CONFIG.get("cpa_url", "")
        default_key = CONFIG.get("cpa_key", "")
        args.url = default_url
        args.key = default_key

    # Auto-trigger setup if url or key is missing
    if not args.url or not args.key:
        print("⚠️ 未检测到 CPA 配置（url 或 key 缺失）")
        if sys.stdin.isatty():
            print("   正在启动配置向导...\n")
            CONFIG = setup_wizard()
            args.url = CONFIG.get("cpa_url", "")
            args.key = CONFIG.get("cpa_key", "")
        else:
            print("❌ 非交互模式，请先运行: python3 codex_cleaner.py setup")
            print("   或设置环境变量 CPA_URL / CPA_KEY")
            sys.exit(1)

    if not args.url or not args.key:
        print("❌ 配置不完整，请重新运行 setup")
        sys.exit(1)

    init_config(args.url, args.key)

    cmd_map = {
        "status": cmd_status,
        "check": cmd_check,
        "delete": cmd_delete,
        "clean": cmd_clean,
        "monitor": cmd_monitor,
    }

    handler = cmd_map.get(args.command)
    if handler:
        handler(args)
    else:
        cmd_status(args)


def cmd_monitor(args):
    """Monitor mode: run clean in a loop."""
    interval = args.interval
    log.info("👁️ [monitor] Starting monitor mode. interval=%ds", interval)

    running = True

    def _stop(sig, frame):
        nonlocal running
        log.info("Received signal %s, stopping...", sig)
        running = False

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    cycle = 0
    while running:
        cycle += 1
        log.info("=" * 50)
        log.info("👁️ [monitor] Cycle #%d at %s", cycle, datetime.now().isoformat())
        log.info("=" * 50)
        try:
            result = cmd_clean(args)
            log.info("👁️ [monitor] Cycle #%d result: %s", cycle, json.dumps(result, ensure_ascii=False))
        except Exception as e:
            log.error("👁️ [monitor] Cycle #%d error: %s", cycle, e)

        if not running:
            break
        log.info("👁️ [monitor] Next cycle in %ds...", interval)
        for _ in range(interval):
            if not running:
                break
            time.sleep(1)

    log.info("👁️ [monitor] Stopped after %d cycles.", cycle)


if __name__ == "__main__":
    main()
