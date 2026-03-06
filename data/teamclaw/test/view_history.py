"""
查看 agent_memory.db 中的历史聊天记录
用法: python test/view_history.py [--user USER_ID] [--limit N]
"""

import os
import sys
import asyncio
import argparse
import sqlite3

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "agent_memory.db")


def get_all_threads() -> list[str]:
    """获取所有 thread_id"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("SELECT DISTINCT thread_id FROM checkpoints ORDER BY thread_id")
    threads = [row[0] for row in cursor.fetchall()]
    conn.close()
    return threads


async def get_chat_history(thread_id: str, limit: int = 50) -> list[dict]:
    """通过 LangGraph 的 checkpoint saver 正确反序列化消息"""
    async with AsyncSqliteSaver.from_conn_string(DB_PATH) as memory:
        config = {"configurable": {"thread_id": thread_id}}
        checkpoint = await memory.aget(config)

        if not checkpoint:
            return []

        channel_values = checkpoint.get("channel_values", {})
        messages = channel_values.get("messages", [])

        result = []
        for msg in messages:
            role = getattr(msg, "type", "unknown")
            content = getattr(msg, "content", "")
            name = getattr(msg, "name", "")

            # content 可能是 list（如 ToolMessage）
            if isinstance(content, list):
                parts = []
                for item in content:
                    if isinstance(item, dict):
                        parts.append(item.get("text", str(item)))
                    else:
                        parts.append(str(item))
                content = "\n".join(parts)

            if not content:
                continue

            result.append({
                "role": role,
                "content": content,
                "name": name,
            })

        return result[-limit:]


def print_messages(messages: list[dict]):
    """格式化打印消息"""
    role_map = {
        "human": "👤 用户",
        "ai": "🤖 助手",
        "tool": "🔧 工具",
        "system": "⚙️ 系统",
    }
    for msg in messages:
        role = role_map.get(msg["role"], msg["role"])
        name_suffix = f" [{msg['name']}]" if msg["name"] else ""
        print(f"\n{role}{name_suffix}:")
        print(f"  {msg['content']}")


async def async_main(args):
    threads = get_all_threads()
    if not threads:
        print("数据库中没有任何聊天记录。")
        return

    if args.user:
        if args.user not in threads:
            print(f"未找到用户 '{args.user}'，已有用户: {', '.join(threads)}")
            return
        target_threads = [args.user]
    else:
        target_threads = threads

    for tid in target_threads:
        print(f"\n{'='*60}")
        print(f"  用户: {tid}")
        print(f"{'='*60}")

        messages = await get_chat_history(tid, args.limit)
        if messages:
            print_messages(messages)
        else:
            print("  （无消息记录）")

        print()


def main():
    parser = argparse.ArgumentParser(description="查看 agent_memory.db 中的历史聊天记录")
    parser.add_argument("--user", type=str, default=None, help="指定用户 ID，不指定则显示所有用户")
    parser.add_argument("--limit", type=int, default=50, help="每个用户最多显示的消息条数（默认 50）")
    args = parser.parse_args()

    if not os.path.exists(DB_PATH):
        print(f"数据库文件不存在: {os.path.abspath(DB_PATH)}")
        print("请先运行 Agent 并进行对话后再查看。")
        sys.exit(1)

    asyncio.run(async_main(args))


if __name__ == "__main__":
    main()
