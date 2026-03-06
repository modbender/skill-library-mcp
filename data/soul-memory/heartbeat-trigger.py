#!/usr/bin/env python3
"""
Soul Memory Heartbeat Auto-Save Trigger
v3.2.4 - 寬鬆識別模式（降低閾值 + 擴展關鍵詞 + 減少排除規則）
"""

import sys
import os
import json
import re
import hashlib
from pathlib import Path
from datetime import datetime, timedelta

SOUL_MEMORY_PATH = os.environ.get('SOUL_MEMORY_PATH', os.path.dirname(__file__))
sys.path.insert(0, SOUL_MEMORY_PATH)

from core import SoulMemorySystem

# OpenClaw session 路徑
SESSIONS_DIR = Path.home() / ".openclaw" / "agents" / "main" / "sessions"
SESSIONS_JSON = SESSIONS_DIR / "sessions.json"

# 去重記錄文件
DEDUP_FILE = Path.home() / ".openclaw" / "workspace" / "soul-memory" / "dedup_hashes.json"

def get_active_session_id():
    """獲取當前 active session 的 ID"""
    try:
        with open(SESSIONS_JSON, 'r', encoding='utf-8') as f:
            sessions = json.load(f)
        
        # 找到最近更新的 session
        best_session = None
        best_time = 0
        
        for key, data in sessions.items():
            if isinstance(data, dict) and 'updatedAt' in data:
                if data['updatedAt'] > best_time:
                    best_time = data['updatedAt']
                    best_session = data.get('sessionId', key)
        
        return best_session
    except Exception as e:
        print(f"⚠️ 無法讀取 sessions.json: {e}")
        return None

def read_session_messages(session_id, hours=1):
    """讀取 session 對話內容（最近 N 小時）"""
    session_file = SESSIONS_DIR / f"{session_id}.jsonl"
    
    if not session_file.exists():
        print(f"⚠️ Session 檔案不存在: {session_file}")
        return []
    
    messages = []
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    try:
        with open(session_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                
                try:
                    entry = json.loads(line)
                    
                    # 只處理消息類型
                    if entry.get('type') != 'message':
                        continue
                    
                    # 解析時間戳
                    timestamp_str = entry.get('timestamp', '')
                    if not timestamp_str:
                        continue
                    
                    try:
                        msg_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        msg_time = msg_time.replace(tzinfo=None)
                    except:
                        continue
                    
                    # 只處理最近的消息
                    if msg_time < cutoff_time:
                        continue
                    
                    # 提取消息內容
                    message = entry.get('message', {})
                    role = message.get('role', '')
                    content = message.get('content', [])
                    
                    # 提取文本內容
                    text_content = ''
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and item.get('type') == 'text':
                                text_content += item.get('text', '')
                    
                    if text_content.strip():
                        messages.append({
                            'time': msg_time,
                            'role': role,
                            'content': text_content.strip()
                        })
                        
                except json.JSONDecodeError:
                    continue
                    
    except Exception as e:
        print(f"⚠️ 讀取 session 檔案錯誤: {e}")
    
    return messages

def identify_important_content(messages):
    """識別重要內容（寬鬆模式 v3.2.4）"""
    important = []
    
    for msg in messages:
        content = msg['content']
        
        # 排除內容（寬鬆版本）
        # 1. 太短（降低閾值）
        if len(content) < 30:
            continue
        
        # 2. 系統指令（僅排除 HEARTBEAT.md）
        if 'HEARTBEAT.md' in content or 'Read HEARTBEAT.md' in content:
            continue
        
        # 識別重要內容（寬鬆啟發式規則）
        importance_score = 0
        priority = 'N'  # 默認 Normal
        
        # 長文本內容（降低閾值 > 100 字）
        if len(content) > 100:
            importance_score += 2
            if len(content) > 200:
                priority = 'I'
        
        # 包含專有名詞或主題詞（擴展列表）
        topic_keywords = [
            '劇情', '故事', '設定', '歷史', 'QST', '物理', '公式',
            '配置', '安裝', 'API', 'Token', '密鑰', 'SSH', 'VPS',
            '秦王', '陛下', '臣', '記住', '重要', '備份', '連接',
            '問題', '解決', '完成', '成功', '失敗', '錯誤',
            '網絡', '防火牆', '封禁', '登錄', '密碼',
            'GitHub', '倉庫', '推送到', '提交', '版本',
            'OpenClaw', 'Heartbeat', '記憶', '系統',
            '任務', '命令', '執行', '重啟', '配置'
        ]
        
        for keyword in topic_keywords:
            if keyword in content:
                importance_score += 1
                if keyword in ['重要', 'QST', '物理', '公式', '配置', '安裝', 'Token', '密鑰', '備份', 'GitHub', 'SSH', 'VPS']:
                    priority = 'C' if importance_score < 3 else priority
                break
        
        # 定義、說明模式（擴展）
        if re.search(r'是.*的|定義|屬於|包括|原理|方式|方法|步驟|設置', content):
            importance_score += 1
        
        # 劇情/故事模式
        if re.search(r'第.\集|情節|角色|劇中|主角|劇情', content):
            importance_score += 1
            priority = 'I'
        
        # AI 回應內容（降低閾值 >= 1）
        if msg['role'] == 'assistant' and importance_score >= 1:
            important.append({
                'time': msg['time'],
                'content': content,
                'priority': priority
            })
    
    return important

def save_to_daily_file(content, priority):
    """保存到 daily file"""
    today = datetime.now().strftime('%Y-%m-%d')
    daily_dir = Path.home() / ".openclaw" / "workspace" / "memory"
    daily_file = daily_dir / f"{today}.md"
    
    # 確保目錄存在
    daily_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成內容
    timestamp = datetime.now().strftime('%H:%M')
    header = "\n\n" + "-" * 50 + "\n"
    header += f"## [{priority}] {timestamp} - Heartbeat 自動提取\n"
    header += f"**來源**：Session 對話回顧\n"
    header += f"**時區**：UTC\n\n"
    
    # 追加到檔案
    with open(daily_file, 'a', encoding='utf-8') as f:
        f.write(header)
        f.write(content)
        f.write('\n')
    
    return str(daily_file)

def get_content_hash(content):
    """計算內容哈希（用於去重）"""
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def get_saved_hashes(today_date=None):
    """獲取已保存的內容哈希"""
    if today_date is None:
        today_date = datetime.now().strftime('%Y-%m-%d')

    if not DEDUP_FILE.exists():
        return {}

    try:
        with open(DEDUP_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 返回今天的哈希集合
        return data.get(today_date, set())
    except Exception as e:
        print(f"⚠️ 讀取去重記錄失敗: {e}")
        return set()

def save_hash(today_date, content_hash):
    """記錄新的內容哈希"""
    try:
        # 讀取現有記錄
        if DEDUP_FILE.exists():
            with open(DEDUP_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {}

        # 更新今天的哈希集合
        if today_date not in data:
            data[today_date] = []

        if content_hash not in data[today_date]:
            data[today_date].append(content_hash)

        # 保存
        with open(DEDUP_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"⚠️ 保存去重記錄失敗: {e}")

def check_daily_memory():
    """檢查今日記憶檔案"""
    today = datetime.now().strftime('%Y-%m-%d')
    daily_file = Path.home() / ".openclaw" / "workspace" / "memory" / f"{today}.md"
    
    if daily_file.exists():
        with open(daily_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 計算各類標記數量
        auto_save_count = content.count('[Auto-Save]')
        heartbeat_extract_count = content.count('## [I]') + content.count('## [C]') - content.count('[Auto-Save]')
        
        return auto_save_count, heartbeat_extract_count
    
    return 0, 0

def main():
    """Heartbeat 檢查點"""
    print(f"🧠 初始化 Soul Memory System v3.2.2...")
    system = SoulMemorySystem()
    system.initialize()
    print(f"✅ 記憶系統就緒")

    # 步驟 1：檢查現有記憶
    auto_save_count, heartbeat_extract_count = check_daily_memory()

    print(f"\n🩺 Heartbeat 記憶檢查 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC)")
    print(f"- [Auto-Save] 條目：{auto_save_count} 條")
    print(f"- [Heartbeat 提取] 條目：{heartbeat_extract_count} 條")

    # 步驟 2：主動提取對話（新功能 v3.2.0）
    print(f"\n🔍 開始主動提取對話...")

    session_id = get_active_session_id()
    if not session_id:
        print("⚠️ 無法獲取 session ID，跳過對話提取")
    else:
        print(f"📋 當前 Session: {session_id[:8]}...")

        # 讀取最近 1 小時的對話
        messages = read_session_messages(session_id, hours=1)
        print(f"📝 找到 {len(messages)} 條 recent 消息")

        # 識別重要內容
        important = identify_important_content(messages)
        print(f"⭐ 識別出 {len(important)} 條重要內容")

        # 去重：獲取已保存的哈希
        today = datetime.now().strftime('%Y-%m-%d')
        saved_hashes = get_saved_hashes(today)
        print(f"🔒 已有 {len(saved_hashes)} 條今日記憶")

        # 保存重要內容（跳過重複）
        saved_count = 0
        skipped_count = 0

        for item in important:
            content_hash = get_content_hash(item['content'])

            # 檢查是否已經保存過
            if content_hash in saved_hashes:
                skipped_count += 1
                print(f"  ⏭️  跳過重複 [{item['priority']}] - {len(item['content'])} 字")
                continue

            # 保存新內容
            daily_file = save_to_daily_file(item['content'], item['priority'])
            save_hash(today, content_hash)  # 記錄哈希
            saved_count += 1
            print(f"  ✅ 保存 [{item['priority']}] {saved_count}/{len(important)} - {len(item['content'])} 字")

        if saved_count > 0:
            print(f"💾 已保存 {saved_count} 條新記憶至 {daily_file}")
        if skipped_count > 0:
            print(f"🔄 跳過 {skipped_count} 條重複記憶")

    # 最終報告
    print(f"\n📊 最終狀態:")
    new_auto_save, new_heartbeat = check_daily_memory()

    if new_auto_save > auto_save_count or new_heartbeat > heartbeat_extract_count:
        print(f"✅ 新增記憶已保存")
        print(f"   - Auto-Save: {new_auto_save - auto_save_count} 條")
        print(f"   - Heartbeat 提取: {new_heartbeat - heartbeat_extract_count} 條")
        print(f"   ↳ 保存至 memory/{datetime.now().strftime('%Y-%m-%d')}.md")
    else:
        print("❌ 無新記憶需要保存")

if __name__ == '__main__':
    main()
