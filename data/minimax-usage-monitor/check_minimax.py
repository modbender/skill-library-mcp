#!/usr/bin/env python3
"""
MiniMax Coding Plan 用量监控脚本
用法: python check_minimax.py [--notify]
"""
import os
import sys
import json
import argparse
from datetime import datetime

# Windows 注册表读取
try:
    import winreg
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_READ)
    value, _ = winreg.QueryValueEx(key, "MINIMAX_CODING_KEY")
    winreg.CloseKey(key)
    os.environ["MINIMAX_CODING_KEY"] = value
except:
    pass

API_KEY = os.environ.get("MINIMAX_CODING_KEY")
if not API_KEY:
    print("[ERROR] MINIMAX_CODING_KEY not found in environment")
    print("[ERROR] Please set your API key first. See: MINIMAX_SETUP.md")
    sys.exit(1)


# 配置参数
WINDOWS_COUNT = 15  # 15个5小时窗口 = 1500/100 (Plus套餐)
PROMPTS_PER_WINDOW = 100  # Plus套餐


def check_usage():
    """查询 Coding Plan 用量"""
    import requests
    
    url = "https://www.minimaxi.com/v1/api/openplatform/coding_plan/remains"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    r = requests.get(url, headers=headers)
    
    if r.status_code != 200:
        return {"error": f"API error: {r.status_code}", "detail": r.text}
    
    data = r.json()
    model_data = data.get("model_remains", [{}])[0]
    
    total_count = model_data.get("current_interval_total_count", 0)
    usage_count = model_data.get("current_interval_usage_count", 0)
    remains_time_ms = model_data.get("remains_time", 0)
    
    # 计算实际用量
    # usage_count 是当前剩余可用prompts (不是已用!)
    # total_count 是总窗口量 (1500 = 15窗口 × 100)
    remaining_in_all_windows = usage_count  # 剩余总量
    used_in_all_windows = total_count - usage_count  # 已用总量
    
    # 当前窗口的用量
    current_window_used = PROMPTS_PER_WINDOW - (usage_count % PROMPTS_PER_WINDOW)  # 当前窗口已用
    current_window_remaining = usage_count % PROMPTS_PER_WINDOW  # 当前窗口剩余
    
    # 转换时间
    remains_minutes = remains_time_ms // 60000
    remains_hours = remains_minutes // 60
    remains_mins = remains_minutes % 60
    
    return {
        "api_total": total_count,
        "api_remaining": usage_count,
        "total_prompts": total_count,
        "used": used_in_all_windows,
        "remaining": remaining_in_all_windows,
        "percentage": round(used_in_all_windows / total_count * 100, 1) if total_count > 0 else 0,
        "current_window_used": current_window_used,
        "current_window_remaining": current_window_remaining,
        "reset_in": f"{remains_hours}h {remains_mins}m" if remains_hours > 0 else f"{remains_mins}m",
        "reset_timestamp": datetime.now().timestamp() + remains_time_ms/1000,
        "model": model_data.get("model_name", "Unknown")
    }


def format_message(usage: dict, notify: bool = False) -> str:
    """格式化输出消息"""
    if "error" in usage:
        return f"[ERROR] Query failed: {usage['error']}"
    
    pct = usage["percentage"]
    remaining = usage["remaining"]
    total = usage["total_prompts"]
    window_rem = usage["current_window_remaining"]
    window_used = usage["current_window_used"]
    
    # 警告阈值 (剩余20%)
    warning = remaining < total * 0.2
    critical = remaining < total * 0.1
    
    status = "[CRITICAL]" if critical else ("[WARNING]" if warning else "[OK]")
    
    msg = f"""=== MiniMax Coding Plan Usage ===
Model: {usage['model']}
Total: {total:,} prompts
Used: {usage['used']:,} ({pct}%)
Remaining: {remaining:,} ({100-pct}%)

Current Window (5h):
  Used: {window_used} / {PROMPTS_PER_WINDOW}
  Remaining: {window_rem} / {PROMPTS_PER_WINDOW}

Reset in: {usage['reset_in']}
Status: {status}
"""
    if notify and warning:
        msg += "\n[WARNING] Less than 20% remaining in total!"
    if notify and critical:
        msg += "\n[CRITICAL] Less than 10% remaining!"
    
    return msg


def main():
    parser = argparse.ArgumentParser(description="MiniMax Coding Plan Usage Monitor")
    parser.add_argument("--notify", action="store_true", help="Show notification messages")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()
    
    usage = check_usage()
    
    if args.json:
        print(json.dumps(usage, indent=2, ensure_ascii=False))
    else:
        print(format_message(usage, args.notify))


if __name__ == "__main__":
    main()
