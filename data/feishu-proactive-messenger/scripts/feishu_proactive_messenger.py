#!/usr/bin/env python3
"""
feishu-proactive-messenger
Send a text message to Feishu proactively using the current agent's credentials.
"""

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import requests


FEISHU_TOKEN_URL = (
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
)
FEISHU_SEND_MSG_URL = "https://open.feishu.cn/open-apis/im/v1/messages"
FEISHU_BOT_INFO_URL = "https://open.feishu.cn/open-apis/bot/v3/info"
OPENCLAW_CONFIG = Path.home() / ".openclaw" / "openclaw.json"


def load_openclaw_config() -> Dict[str, Any]:
    if not OPENCLAW_CONFIG.exists():
        raise FileNotFoundError(f"OpenClaw config not found: {OPENCLAW_CONFIG}")
    return json.loads(OPENCLAW_CONFIG.read_text(encoding="utf-8"))


def resolve_agent_id(config: Dict[str, Any]) -> str:
    cwd = Path.cwd().resolve()
    default_workspace = (
        config.get("agents", {}).get("defaults", {}).get("workspace")
    )
    best_match = (0, None)
    for agent in config.get("agents", {}).get("list", []):
        workspace = agent.get("workspace") or default_workspace
        agent_id = agent.get("id")
        if not workspace or not agent_id:
            continue
        workspace_path = Path(workspace).resolve()
        if str(cwd).startswith(str(workspace_path)):
            match_len = len(str(workspace_path))
            if match_len > best_match[0]:
                best_match = (match_len, agent_id)
    if best_match[1]:
        return best_match[1]
    raise RuntimeError("Unable to resolve agent id from workspace path")


def resolve_feishu_account(
    config: Dict[str, Any], agent_id: str
) -> Tuple[str, str, Optional[str]]:
    """Returns (app_id, app_secret, default_to)."""
    bindings = config.get("bindings", [])
    account_id = None
    for binding in bindings:
        if binding.get("agentId") == agent_id:
            account_id = binding.get("match", {}).get("accountId")
            if account_id:
                break
    if not account_id:
        raise RuntimeError(f"No Feishu account binding for agent: {agent_id}")

    accounts = (
        config.get("channels", {})
        .get("feishu", {})
        .get("accounts", {})
    )
    account = accounts.get(account_id)
    if not account:
        raise RuntimeError(f"Feishu account not found: {account_id}")
    app_id = account.get("appId")
    app_secret = account.get("appSecret")
    if not app_id or not app_secret:
        raise RuntimeError(f"Missing appId/appSecret for account: {account_id}")
    default_to = account.get("defaultTo")
    return app_id, app_secret, default_to


def get_tenant_access_token(app_id: str, app_secret: str) -> str:
    resp = requests.post(
        FEISHU_TOKEN_URL,
        json={"app_id": app_id, "app_secret": app_secret},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"Get token failed: {data}")
    return data["tenant_access_token"]


def get_bot_name(token: str) -> str:
    """Get the bot's display name from Feishu. Returns empty string on failure."""
    try:
        resp = requests.get(
            FEISHU_BOT_INFO_URL,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") == 0:
            return data.get("bot", {}).get("app_name", "")
    except Exception:
        pass
    return ""


def send_text_message(
    token: str,
    receive_id: str,
    receive_id_type: str,
    text: str,
) -> Dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    params = {"receive_id_type": receive_id_type}
    payload = {
        "receive_id": receive_id,
        "msg_type": "text",
        "content": json.dumps({"text": text}),
    }
    resp = requests.post(
        FEISHU_SEND_MSG_URL,
        headers=headers,
        params=params,
        json=payload,
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"Send message failed: {data}")
    return data


def infer_receive_id_type(receive_id: str, explicit: Optional[str]) -> str:
    if explicit:
        return explicit
    if receive_id.startswith("oc_"):
        return "chat_id"
    if receive_id.startswith("ou_"):
        return "open_id"
    if receive_id.startswith("on_"):
        return "user_id"
    return "open_id"


def resolve_receive_id(cli_value: Optional[str], default_to: Optional[str]) -> str:
    """Resolve receive_id from CLI arg, env, or defaultTo config."""
    if cli_value:
        return cli_value

    env_value = (
        os.getenv("OPENCLAW_CHAT_ID")
        or os.getenv("OPENCLAW_RECEIVE_ID")
        or os.getenv("FEISHU_CHAT_ID")
    )
    if env_value:
        return env_value

    if default_to:
        # Strip "user:" prefix if present (OpenClaw internal format)
        if default_to.startswith("user:"):
            return default_to[5:]
        return default_to

    raise RuntimeError(
        "Missing receive_id. Provide --receive-id, set OPENCLAW_CHAT_ID, "
        "or configure defaultTo in the Feishu account."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send a text message to Feishu proactively"
    )
    parser.add_argument("--text", required=True, help="Message text to send")
    parser.add_argument("--agent", default=None, help="Agent id (e.g. coder, data). Auto-detect from cwd if omitted")
    parser.add_argument("--receive-id", default=None, help="chat_id or open_id")
    parser.add_argument(
        "--receive-id-type",
        default=None,
        help="chat_id / open_id / user_id (auto-detect if omitted)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    config = load_openclaw_config()
    agent_id = args.agent or resolve_agent_id(config)
    app_id, app_secret, default_to = resolve_feishu_account(config, agent_id)

    receive_id = resolve_receive_id(args.receive_id, default_to)
    receive_id_type = infer_receive_id_type(receive_id, args.receive_id_type)

    token = get_tenant_access_token(app_id, app_secret)
    bot_name = get_bot_name(token)
    result = send_text_message(token, receive_id, receive_id_type, args.text)
    label = bot_name if bot_name else agent_id
    print(f"✅ [{label}] 消息已发送")


if __name__ == "__main__":
    main()
