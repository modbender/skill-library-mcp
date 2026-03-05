"""
MCP Tool Server: LLM API Access

Provides two tools for the Agent:

1. call_llm_api — Call any external OpenAI-compatible LLM API.
   Agent provides url, api_key, model, messages content, and gets back the response.
   Useful for consulting powerful/expensive models (GPT-5, Claude, etc.)

2. send_internal_message — Send a message to another internal session (or user)
   via the local /v1/chat/completions endpoint using INTERNAL_TOKEN auth.
   Two modes:
     - wait=True  (default): synchronously wait for the reply (up to timeout)
     - wait=False: fire-and-forget, returns immediately with "已送达"

Runs as a stdio MCP server.
"""

import os
import json
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# 加载 .env
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(dotenv_path=os.path.join(root_dir, "config", ".env"))

mcp = FastMCP("LLM API Access")

# Internal Agent endpoint
_AGENT_PORT = os.getenv("PORT_AGENT", "51200")
_AGENT_URL = f"http://127.0.0.1:{_AGENT_PORT}/v1/chat/completions"
_INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN", "")

# Default timeout for external API calls (seconds)
_DEFAULT_TIMEOUT = 120
# Default timeout for internal sync calls
_INTERNAL_SYNC_TIMEOUT = 180


@mcp.tool()
async def call_llm_api(
    username: str,
    api_url: str,
    api_key: str,
    model: str,
    content: str,
    system_prompt: str = "",
    temperature: float = 0.7,
    max_tokens: int = 4096,
    timeout: int = _DEFAULT_TIMEOUT,
) -> str:
    """
    Call an external OpenAI-compatible LLM API and return the response.

    Use this to consult powerful/expensive external models (e.g. GPT-5, Claude, o3)
    for complex reasoning, second opinions, or tasks that exceed the current model's
    capabilities. The request is wrapped in standard OpenAI chat completions format.

    Args:
        username: (auto-injected) current user identity; do NOT set manually
        api_url: Full API endpoint URL, e.g. "https://api.openai.com/v1/chat/completions"
        api_key: API key / Bearer token for authentication
        model: Model name, e.g. "gpt-5", "claude-sonnet-4-20250514"
        content: The user message content to send to the model
        system_prompt: Optional system prompt to prepend
        temperature: Sampling temperature (0-2), default 0.7
        max_tokens: Maximum response tokens, default 4096
        timeout: Request timeout in seconds, default 120

    Returns:
        The model's response text, or an error message
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": content})

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                api_url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

            if response.status_code != 200:
                return (
                    f"❌ API 请求失败 (HTTP {response.status_code}):\n"
                    f"{response.text[:2000]}"
                )

            res_data = response.json()

            # Standard OpenAI format
            if "choices" in res_data and res_data["choices"]:
                reply = res_data["choices"][0].get("message", {}).get("content", "")
                usage = res_data.get("usage", {})
                usage_info = ""
                if usage:
                    usage_info = (
                        f"\n\n📊 Token 用量: "
                        f"prompt={usage.get('prompt_tokens', '?')}, "
                        f"completion={usage.get('completion_tokens', '?')}, "
                        f"total={usage.get('total_tokens', '?')}"
                    )
                return f"✅ [{model}] 回复:\n\n{reply}{usage_info}"

            # Fallback: return raw response
            return f"⚠️ 非标准响应格式:\n{json.dumps(res_data, ensure_ascii=False, indent=2)[:3000]}"

    except httpx.TimeoutException:
        return f"❌ 请求超时 ({timeout}s)。可以增大 timeout 参数重试。"
    except Exception as e:
        return f"❌ 请求异常: {type(e).__name__}: {str(e)}"


@mcp.tool()
async def send_internal_message(
    username: str,
    target_user: str,
    content: str,
    target_session: str = "default",
    wait: bool = True,
    system_prompt: str = "",
    timeout: int = _INTERNAL_SYNC_TIMEOUT,
    source_session: str = "",
) -> str:
    """
    Send a message to another internal Agent session via the local OpenAI-compatible API.

    Two modes:
    - wait=True (default): Send and wait for the target session's Agent to respond.
      Like a synchronous "internal consultation" — useful for asking another session's
      Agent for help and getting the answer back.
    - wait=False: Fire-and-forget. The message is delivered and the target session's
      Agent will process it asynchronously (via system_trigger). You'll get "已送达"
      immediately. The target Agent's response will appear in that session's chat history.

    IMPORTANT: Do NOT use wait=True to send to your own current session — this will
    cause a deadlock. Use wait=False for same-session messaging, or target a different session.

    Typical use cases:
    - Cross-session coordination: "Hey session-B, please run this analysis"
    - Consulting a specialized session that has different context/tools
    - Leaving a message for a session to process later

    Args:
        username: (auto-injected) current user identity; do NOT set manually
        target_user: Target user's username. Use same username for cross-session within
                     same user, or a different username for cross-user messaging.
        content: The message content to send
        target_session: Target session ID (default: "default")
        wait: If True, wait for response synchronously; if False, fire-and-forget
        system_prompt: Optional system context to include (sent as system message)
        timeout: Response timeout in seconds (only for wait=True), default 180
        source_session: (auto-injected) current session ID; do NOT set manually

    Returns:
        The target Agent's response (wait=True), or delivery confirmation (wait=False)
    """
    if not _INTERNAL_TOKEN:
        return "❌ 系统未配置 INTERNAL_TOKEN，无法进行内部通信。"

    # 死锁保护：wait=True 且目标是自己当前 session → 强制降级为 wait=False
    if wait and target_user == username and target_session == source_session:
        return (
            "❌ 不能以 wait=True 模式向自己当前 session 发送消息（会导致死锁）。\n"
            "请改用 wait=False（异步投递），或发送到不同的 session。"
        )

    # Build API key: INTERNAL_TOKEN:target_user:target_session
    api_key = f"{_INTERNAL_TOKEN}:{target_user}:{target_session}"

    if wait:
        # Synchronous mode: call /v1/chat/completions and wait for response
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": content})

        payload = {
            "model": "internal",
            "messages": messages,
            "stream": False,
        }

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    _AGENT_URL,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )

                if response.status_code != 200:
                    return (
                        f"❌ 内部请求失败 (HTTP {response.status_code}):\n"
                        f"{response.text[:2000]}"
                    )

                res_data = response.json()
                if "choices" in res_data and res_data["choices"]:
                    reply = res_data["choices"][0].get("message", {}).get("content", "")
                    return (
                        f"✅ [{target_user}#{target_session}] 回复:\n\n{reply}"
                    )

                return f"⚠️ 非标准响应:\n{json.dumps(res_data, ensure_ascii=False, indent=2)[:2000]}"

        except httpx.TimeoutException:
            return (
                f"⏰ 等待 [{target_user}#{target_session}] 回复超时 ({timeout}s)。\n"
                f"消息已送达，对方 Agent 可能仍在处理中。"
            )
        except Exception as e:
            return f"❌ 内部通信异常: {type(e).__name__}: {str(e)}"

    else:
        # Fire-and-forget mode: use /system_trigger endpoint
        trigger_url = f"http://127.0.0.1:{_AGENT_PORT}/system_trigger"

        # Prepend system_prompt to content if provided
        full_content = content
        if system_prompt:
            full_content = f"[来自 {username} 的消息，附带说明]\n{system_prompt}\n\n---\n{content}"
        else:
            full_content = f"[来自 {username} 的消息]\n{content}"

        payload = {
            "user_id": target_user,
            "session_id": target_session,
            "text": full_content,
        }

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    trigger_url,
                    headers={
                        "X-Internal-Token": _INTERNAL_TOKEN,
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )

                if response.status_code != 200:
                    return (
                        f"❌ 消息投递失败 (HTTP {response.status_code}):\n"
                        f"{response.text[:1000]}"
                    )

                return (
                    f"✅ 消息已送达 [{target_user}#{target_session}]。\n"
                    f"对方 Agent 将异步处理，回复会出现在目标会话中。"
                )

        except Exception as e:
            return f"❌ 消息投递异常: {type(e).__name__}: {str(e)}"


@mcp.tool()
async def send_to_group(
    username: str,
    group_id: str,
    content: str,
    source_session: str = "",
) -> str:
    """
    Send a message to a group chat. Use this when you receive a message
    from a group chat (indicated by "[群聊 xxx]" prefix) and want to reply,
    or when you proactively want to say something in a group.

    The message will be broadcast to all agent members in the group (except yourself).
    Human members will see it when they next poll/refresh the group chat UI.

    Args:
        username: (auto-injected) current user identity; do NOT set manually
        group_id: The group chat ID (e.g. "g_1234567890_abcd1234")
        content: The message content to send to the group
        source_session: (auto-injected) current session ID; do NOT set manually

    Returns:
        Confirmation of message delivery
    """
    if not _INTERNAL_TOKEN:
        return "❌ 系统未配置 INTERNAL_TOKEN，无法发送群聊消息。"

    url = f"http://127.0.0.1:{_AGENT_PORT}/groups/{group_id}/messages"
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                url,
                headers={
                    "X-Internal-Token": _INTERNAL_TOKEN,
                    "Content-Type": "application/json",
                },
                json={
                    "content": content,
                    "sender": f"{username}#{source_session}" if source_session else username,
                    "sender_session": source_session,
                },
            )
            if response.status_code != 200:
                return f"❌ 发送失败 (HTTP {response.status_code}): {response.text[:500]}"
            return f"✅ 消息已发送到群聊 [{group_id}]"
    except Exception as e:
        return f"❌ 发送群聊消息失败: {type(e).__name__}: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
