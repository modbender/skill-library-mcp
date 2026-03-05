"""
MCP Tool Server: Session Management

Exposes tools for the Agent to be aware of its own session context
and query existing sessions:
  - get_current_session: Returns the current session_id the agent is running in
  - list_sessions: Lists all sessions for the current user with summaries

Runs as a stdio MCP server, just like the other mcp_*.py tools.
"""

import os
import json
import aiosqlite
from mcp.server.fastmcp import FastMCP
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

mcp = FastMCP("Session Management")

# Checkpoint DB path — same as agent.py uses
_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "agent_memory.db",
)

# LangGraph checkpoint serde (msgpack-based, not plain JSON)
_serde = JsonPlusSerializer()


@mcp.tool()
async def get_current_session(
    username: str = "",
    current_session_id: str = "default",
) -> str:
    """
    Get the session ID that the agent is currently running in.

    This is useful for:
      - Knowing which session to specify as callback target (notify_session)
        when dispatching sub-agents
      - Building workflows like "agent A does work, reports back to session C"

    Args:
        username: (auto-injected) current user identity; do NOT set manually
        current_session_id: (auto-injected) current session ID; do NOT set manually

    Returns:
        Current session context info as a formatted string
    """
    return (
        f"📍 当前会话信息:\n"
        f"  用户: {username}\n"
        f"  Session ID: {current_session_id}\n\n"
        f"💡 如需将讨论完成通知发送到当前会话，"
        f"请在 post_to_oasis 中设置 notify_session=\"{current_session_id}\""
    )


@mcp.tool()
async def list_sessions(
    username: str = "",
) -> str:
    """
    List all conversation sessions for the current user, with title and summary.

    Returns each session's ID, title (first user message), last message preview,
    and message count. Useful for knowing which sessions exist and choosing
    a target session for callbacks or cross-session workflows.

    Args:
        username: (auto-injected) current user identity; do NOT set manually

    Returns:
        Formatted list of all sessions with summaries
    """
    if not username:
        return "❌ 无法获取用户信息"

    if not os.path.exists(_DB_PATH):
        return "❌ 对话记录数据库不存在"

    prefix = f"{username}#"
    sessions = []

    try:
        async with aiosqlite.connect(_DB_PATH) as db:
            cursor = await db.execute(
                "SELECT DISTINCT thread_id FROM checkpoints "
                "WHERE thread_id LIKE ? ORDER BY thread_id",
                (f"{prefix}%",),
            )
            rows = await cursor.fetchall()

            for (thread_id,) in rows:
                sid = thread_id[len(prefix):]

                # Get latest checkpoint data to extract summary
                ckpt_cursor = await db.execute(
                    "SELECT type, checkpoint FROM checkpoints "
                    "WHERE thread_id = ? ORDER BY ROWID DESC LIMIT 1",
                    (thread_id,),
                )
                ckpt_row = await ckpt_cursor.fetchone()
                if not ckpt_row:
                    continue

                # Parse checkpoint using LangGraph serde (msgpack format)
                try:
                    ckpt_data = _serde.loads_typed((ckpt_row[0], ckpt_row[1]))
                except Exception:
                    continue

                # Extract channel_values -> messages from checkpoint
                channel_values = ckpt_data.get("channel_values", {})
                messages = channel_values.get("messages", [])

                first_human = ""
                last_human = ""
                msg_count = 0

                for m in messages:
                    # After proper deserialization, messages are LangChain objects
                    # Check type by class name (HumanMessage, AIMessage, etc.)
                    type_name = type(m).__name__

                    if type_name != "HumanMessage":
                        continue

                    content = getattr(m, "content", "")
                    if not content:
                        continue

                    # Handle multimodal content (list of parts)
                    if isinstance(content, list):
                        text_parts = []
                        for p in content:
                            if isinstance(p, dict) and p.get("type") == "text":
                                text_parts.append(p.get("text", ""))
                        content = " ".join(text_parts) or "(多媒体消息)"
                    elif not isinstance(content, str):
                        content = str(content)

                    # Skip system trigger messages
                    if content.startswith("[系统触发]"):
                        continue

                    msg_count += 1
                    if not first_human:
                        first_human = content[:80]
                    last_human = content[:80]

                if not first_human:
                    continue  # Skip empty or system-only sessions

                sessions.append({
                    "session_id": sid,
                    "title": first_human,
                    "last_message": last_human,
                    "message_count": msg_count,
                })

    except Exception as e:
        return f"❌ 查询会话列表失败: {str(e)}"

    if not sessions:
        return "📭 当前没有任何对话记录。"

    lines = [f"📋 用户 {username} 的会话列表（共 {len(sessions)} 个）:\n"]
    for s in sessions:
        lines.append(
            f"  🔹 session_id: \"{s['session_id']}\"\n"
            f"     标题: {s['title']}\n"
            f"     最新消息: {s['last_message']}\n"
            f"     消息数: {s['message_count']}\n"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run(transport="stdio")
