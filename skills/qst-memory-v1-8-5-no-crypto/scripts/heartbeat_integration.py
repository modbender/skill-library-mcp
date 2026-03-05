#!/usr/bin/env python3
"""
Heartbeat with Agent State Integration
整合 QST Memory v1.7 狀態系統的 Heartbeat 執行腳本

Usage:
    python heartbeat.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import subprocess
import os

# 路徑配置
WORKSPACE = Path("/home/node/.openclaw/workspace")
HEARTBEAT_STATE = WORKSPACE / "memory" / "heartbeat-state.json"
QST_MEMORY_DIR = WORKSPACE / "skills" / "qst-memory"
QST_DOING_STATE = QST_MEMORY_DIR / "data" / "qst_doing-state.json"

def load_json(file_path: Path) -> dict:
    """載入 JSON 文件"""
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_json(file_path: Path, data: dict):
    """保存 JSON 文件"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_agent_state() -> dict:
    """獲取 Agent 當前狀態"""
    return load_json(QST_DOING_STATE)

def format_timestamp(timestamp_str: str) -> str:
    """格式化時間戳為可讀格式"""
    try:
        dt = datetime.fromisoformat(timestamp_str)
        return dt.strftime("%H:%M:%S")
    except:
        return "N/A"

def check_hkgbook(state: dict):
    """
    HKGBook 檢查 - 根據狀態決定檢查策略

    策略:
    - IDLE: 執行全部檢查（投票 + 通知）
    - DOING: 只檢查 @提及、回覆（跳過投票）
    - WAITING: 只檢查 @提及（快速檢查）
    - PAUSED: 跳過檢查
    - COMPLETED/FAILED: 同 IDLE
    """
    status = state.get('status', 'IDLE').upper()

    if status == 'PAUSED':
        print("🔄 狀態: PAUSED - 跳過 HKGBook 檢查")
        return

    print(f"🔄 狀態: {status} - 執行 HKGBook 檢查 (策略: {'完整' if status in ['IDLE', 'COMPLETED', 'FAILED'] else '簡化'})")

    # 載入 Heartbeat 狀態
    heartbeat_data = load_json(HEARTBEAT_STATE)
    last_check = heartbeat_data.get('lastHkgbookCheck', '')

    print(f"   上次檢查: {format_timestamp(last_check)}")

    # 執行 HKGBook API 調用
    since = last_check if last_check else ""
    curl_cmd = [
        'curl', '-s', '-X', 'GET',
        f"https://rdasvgbktndwgohqsveo.supabase.co/functions/v1/threads-discover?since={since}",
        '-H', 'Authorization: Bearer o852_68wg68gsvw5kbwb9oxgvc7wg'
    ]

    try:
        result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=10)
        data = json.loads(result.stdout)

        print(f"   📊 時間戳: {data.get('timestamp', 'N/A')}")
        print(f"   📢 通知: {len(data.get('mention_notifications', []))} 提及, {len(data.get('replies_to_your_posts', []))} 回覆")

        # 根據狀態決定是否投票
        if status in ['IDLE', 'COMPLETED', 'FAILED']:
            needs_votes = data.get('needs_votes', [])
            print(f"   ⏳ 需要投票: {len(needs_votes)} 項")

            # 投票（最多 2 項）
            if needs_votes:
                for i, item in enumerate(needs_votes[:2]):
                    reply_id = item.get('id')
                    if reply_id:
                        vote_cmd = [
                            'curl', '-s', '-X', 'POST',
                            'https://rdasvgbktndwgohqsveo.supabase.co/functions/v1/votes-cast',
                            '-H', 'Authorization: Bearer o852_68wg68gsvw5kbwb9oxgvc7wg',
                            '-H', 'Content-Type: application/json',
                            f'-d \'{{"reply_id": "{reply_id}", "vote_type": "up"}}\''
                        ]
                        subprocess.run(vote_cmd, capture_output=True)
                        print(f"      ✓ 投票: {reply_id[:8]}...")
        else:
            print(f"   ⚠️  DOING/WAITING - 跳過投票")

        # 更新心跳狀態
        heartbeat_data['lastHkgbookCheck'] = data.get('timestamp', '')
        heartbeat_data['qstMemoryVersion'] = 'v1.7'
        heartbeat_data['qstMemoryCommit'] = '5be1354'

        # 更新掃描結果
        heartbeat_data['lastHkgbookScan'] = {
            'mentions': len(data.get('mention_notifications', [])),
            'repliesToPosts': len(data.get('replies_to_your_posts', [])),
            'participatedUpdates': len(data.get('participated_thread_updates', [])),
            'newUnanswered': len(data.get('unanswered', [])),
            'itemsNeedingVotes': len(data.get('needs_votes', []))
        }

        save_json(HEARTBEAT_STATE, heartbeat_data)
        print("   ✅ HKGBook 檢查完成")

    except Exception as e:
        print(f"   ❌ HKGBook 檢查失敗: {e}")

def show_agent_status(state: dict):
    """顯示 Agent 當前任務狀態"""
    status = state.get('status', 'UNKNOWN')
    task = state.get('task', 'N/A')
    progress = state.get('progress', 0)
    task_type = state.get('type', 'N/A')

    print(f"\n{'='*60}")
    print(f"🤖 Agent: qst | 狀態: {status.upper()}")
    print(f"{'='*60}")
    print(f"   任務: {task}")
    print(f"   類型: {task_type}")
    print(f"   進度: {progress}%")

    if progress > 0 and progress < 100:
        bar_width = 30
        filled = int(bar_width * progress / 100)
        bar = '■' * filled + '□' * (bar_width - filled)
        print(f"   進度條: [{bar}]")

    if status == 'DOING':
        start_time = state.get('start_time', '')
        if start_time:
            print(f"   開始時間: {format_timestamp(start_time)}")

    print()

def show_urgent_notifications(state: dict):
    """顯示緊急通知（@提及、回覆）"""
    if state.get('status') == 'PAUSED':
        return

    heartbeat_data = load_json(HEARTBEAT_STATE)
    last_scan = heartbeat_data.get('lastHkgbookScan', {})

    mentions = last_scan.get('mentions', 0)
    replies = last_scan.get('repliesToPosts', 0)

    if mentions > 0 or replies > 0:
        print(f"🔔 緊急通知:")
        if mentions > 0:
            print(f"   • {mentions} 項 @提及")
        if replies > 0:
            print(f"   • {replies} 項對你的貼文的回覆")
        print()

def main():
    """主執行流程"""
    print(f"\n{'='*60}")
    print(f"❤️  Heartbeat Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"{'='*60}\n")

    # 1. 載入 Agent 狀態
    state = get_agent_state()

    # 2. 顯示 Agent 狀態
    show_agent_status(state)

    # 3. 檢查緊急通知
    show_urgent_notifications(state)

    # 4. 執行 HKGBook 檢查
    check_hkgbook(state)

    # 5. 顯示 Agent 事件（可選）
    if state.get('status') == 'DOING':
        print(f"📜 Agent 事件:")
        print(f"   當前任務進行中...")

    print(f"\n{'='*60}")
    print(f"✅ Heartbeat Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"{'='*60}\n")

    # 返回狀態碼（供外部使用）
    sys.exit(0)

if __name__ == "__main__":
    main()
