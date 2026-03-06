#!/usr/bin/env python3
"""
Chat History - 直接从JSONL文件归档（v3.0）
优化设计：
- 自动支持多个channel（webui/imessage/telegram等）
- 只归档上次归档后的新消息（增量归档）
- 统一查询接口，跨端搜索
"""

import os
import sys
import json
import re
from datetime import datetime

# 配置（自动检测路径）
OPENCLAW_DIR = os.path.expanduser(os.environ.get("OPENCLAW_DIR", "~/.openclaw"))
WORKSPACE_DIR = os.path.expanduser(os.environ.get("OPENCLAW_WORKSPACE", os.path.join(OPENCLAW_DIR, "workspace")))

SESSIONS_DIR = os.path.join(OPENCLAW_DIR, "agents/main/sessions")
ARCHIVE_DIR = os.path.join(WORKSPACE_DIR, "conversation-archives")
LOG_FILE = os.path.join(ARCHIVE_DIR, "chat-archive.log")
STATUS_FILE = os.path.join(ARCHIVE_DIR, "status.json")


def ensure_directories():
    """确保归档目录存在"""
    os.makedirs(ARCHIVE_DIR, exist_ok=True)


def load_status():
    """加载状态"""
    if not os.path.exists(STATUS_FILE):
        return {
            "last_archive": None,
            "archive_time": "23:59",
            "total_messages": 0,
            "total_files": 0,
            "channels": []
        }
    with open(STATUS_FILE, "r") as f:
        return json.load(f)


def save_status(status):
    """保存状态"""
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)


def parse_jsonl_datetime(timestamp_str):
    """解析JSONL时间戳"""
    try:
        if '.' in timestamp_str:
            timestamp_str = timestamp_str.split('.')[0] + "Z"
        return datetime.strptime(timestamp_str[:19], "%Y-%m-%dT%H:%M:%S")
    except:
        return None


def extract_channel_from_message(data):
    """从消息中提取channel"""
    try:
        # 方法1：从message字段中提取
        message_data = data.get('message', {})
        if 'channel' in message_data:
            return message_data['channel']

        # 方法2：从自定义字段中提取
        for field in ['inbound_meta', 'metadata', 'meta']:
            if field in data:
                meta = data[field]
                if isinstance(meta, dict) and 'channel' in meta:
                    return meta['channel']

        # 方法3：默认值
        return 'webui'  # 默认是webui
    except:
        return 'webui'


def format_messages(messages, date_str, channel):
    """格式化消息为可读文本"""
    output = []
    output.append(f"归档时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append(f"日期: {date_str}")
    output.append(f"Channel: {channel}")
    output.append("=" * 80 + "\n")

    for msg in messages:
        role_emoji = {"user": "👤", "assistant": "🤖", "system": "⚙️", "tool": "🔧"}.get(msg['role'], "❓")
        timestamp = msg['timestamp_str']
        content = msg['content']

        # 过滤System和heartbeat消息
        if 'System:' in content and ('scheduled reminder' in content.lower() or 'reminder has been triggered' in content.lower()):
            continue

        output.append(f"[{timestamp}] {role_emoji} {content}\n")

    output.append("=" * 80 + "\n")
    return "\n".join(output)


def archive_all_sessions(incremental=True):
    """
    归档所有会话

    Args:
        incremental: 是否增量归档（只归档上次归档后的消息）
                     False = 全量归档（归档所有消息）
    """
    ensure_directories()
    status = load_status()

    print("📦 开始归档...")
    print(f"会话目录: {SESSIONS_DIR}")
    print(f"归档模式: {'增量' if incremental else '全量'}\n")

    # 获取上次归档时间
    last_archive_time_str = status.get('last_archive')
    last_archive_time = None
    if incremental and last_archive_time_str:
        try:
            last_archive_time = datetime.strptime(last_archive_time_str, "%Y-%m-%d %H:%M:%S")
            print(f"上次归档: {last_archive_time_str}")
        except:
            print(f"⚠️  无法解析上次归档时间，执行全量归档")
            last_archive_time = None

    # 获取所有.jsonl文件
    jsonl_files = [f for f in os.listdir(SESSIONS_DIR) if f.endswith('.jsonl')]

    if not jsonl_files:
        print("❌ 未找到任何 .jsonl 会话文件\n")
        return 0

    print(f"✅ 找到 {len(jsonl_files)} 个会话文件\n")

    # 按channel和日期组织消息
    messages_by_date_and_channel = {}
    total_messages = 0

    # 遍历所有jsonl文件
    for jsonl_file in jsonl_files:
        file_path = os.path.join(SESSIONS_DIR, jsonl_file)
        print(f"📂 处理: {jsonl_file}")

        if not os.path.exists(file_path):
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if not line.strip():
                        continue

                    try:
                        data = json.loads(line)

                        # 只处理message类型的行
                        if data.get('type') != 'message':
                            continue

                        timestamp = parse_jsonl_datetime(data.get('timestamp', ''))
                        if not timestamp:
                            continue

                        # 增量归档：只归档上次归档后的消息
                        if incremental and last_archive_time and timestamp <= last_archive_time:
                            continue

                        date_str = timestamp.strftime("%Y-%m-%d")
                        channel = extract_channel_from_message(data)

                        # 提取消息内容
                        message_data = data.get('message', {})
                        role = message_data.get('role', '')
                        content = message_data.get('content', [])

                        # 解析content（可能text/media）
                        if not content:
                            continue

                        text_content = ""
                        for item in content:
                            if isinstance(item, dict):
                                if item.get('type') == 'text':
                                    text_content += item.get('text', '')
                                elif item.get('type') == 'media':
                                    text_content += f"[媒体: {item.get('url', '')}]"

                        if not text_content.strip():
                            continue

                        # 组织消息：按date+channel
                        key = (date_str, channel)
                        if key not in messages_by_date_and_channel:
                            messages_by_date_and_channel[key] = []

                        messages_by_date_and_channel[key].append({
                            'timestamp': timestamp,
                            'timestamp_str': timestamp.strftime("%H:%M:%S"),
                            'role': role,
                            'content': text_content
                        })

                        total_messages += 1

                    except json.JSONDecodeError as e:
                        print(f"  ⚠️  跳过第 {line_num} 行（解析错误）")
                        continue
                    except Exception as e:
                        continue

        except Exception as e:
            print(f"  ❌ 读取文件失败: {e}")
            continue

    print(f"\n✅ 提取了 {total_messages} 条消息\n")

    if total_messages == 0:
        print("⚠️  没有需要归档的消息（已经是最新状态）\n")
        return 0

    # 按日期和channel保存
    archived_files = 0
    archived_channels = set()

    for (date_str, channel), messages in sorted(messages_by_date_and_channel.items()):
        # 按timestamp排序
        messages.sort(key=lambda x: x['timestamp'])

        # 格式化
        formatted = format_messages(messages, date_str, channel)

        # 文件命名：YYYYMMDD-channel.txt
        filename = f"{date_str.replace('-', '')}-{channel}.txt"
        filepath = os.path.join(ARCHIVE_DIR, filename)

        # 保存
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(formatted)

        print(f"✅ 归档: {filename} ({len(messages)} 条消息)")

        archived_files += 1
        archived_channels.add(channel)

    # 更新状态
    status["last_archive"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status["total_messages"] += total_messages
    status["total_files"] += archived_files

    # 更新channels列表
    existing_channels = set(status.get("channels", []))
    status["channels"] = list(existing_channels.union(archived_channels))

    save_status(status)

    print(f"\n✅ 归档完成！")
    print(f"   归档文件: {archived_files} 个")
    print(f"   归档消息: {total_messages} 条")
    print(f"   涉及Channels: {', '.join(sorted(archived_channels))}")
    print(f"   归档目录: {ARCHIVE_DIR}\n")

    return total_messages


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='归档OpenClaw会话历史')
    parser.add_argument('--full', action='store_true', help='全量归档（不是增量）')
    args = parser.parse_args()

    try:
        count = archive_all_sessions(incremental=not args.full)

        if count > 0:
            print(f"🎉 成功归档 {count} 条对话记录\n")
            sys.exit(0)
        else:
            print("⚠️  没有归档任何消息\n")
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n\n❌ 用户取消\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 归档失败: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
