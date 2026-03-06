#!/usr/bin/env python3
"""Telegram Bot API helper for MISO — pin/unpin/sendAnimation/editMessageMedia"""

import json
import sys
import os
from urllib.request import urlopen, Request
from urllib.parse import urlencode
import mimetypes

CONFIG_PATH = "/Users/shunsukehayashi/.openclaw/openclaw.json"
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")

PHASE_GIFS = {
    "init": "miso-init.gif",
    "running": "miso-running.gif",
    "partial": "miso-partial.gif",
    "approval": "miso-approval.gif",
    "complete": "miso-complete.gif",
    "error": "miso-error.gif",
}

# Agent-specific GIFs: agent-{name}-{phase}.gif
AGENT_PHASES = ["init", "running", "complete"]


def _get_token() -> str:
    with open(CONFIG_PATH) as f:
        return json.load(f)["channels"]["telegram"]["botToken"]


def _api_call(method: str, chat_id: int, message_id: int) -> dict:
    token = _get_token()
    url = f"https://api.telegram.org/bot{token}/{method}"
    payload = json.dumps({"chat_id": chat_id, "message_id": message_id,
                          "disable_notification": True}).encode("utf-8")
    req = Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urlopen(req) as res:
            return json.loads(res.read())
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _multipart_post(url: str, fields: dict, files: dict) -> dict:
    """Multipart form-data POST for file uploads."""
    import uuid
    boundary = uuid.uuid4().hex
    body = b""
    for key, val in fields.items():
        body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"{key}\"\r\n\r\n{val}\r\n".encode()
    for key, (filename, data, content_type) in files.items():
        body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"{key}\"; filename=\"{filename}\"\r\nContent-Type: {content_type}\r\n\r\n".encode()
        body += data + b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    req = Request(url, data=body,
                  headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    try:
        with urlopen(req) as res:
            return json.loads(res.read())
    except Exception as e:
        return {"ok": False, "error": str(e)}


def pin_message(chat_id: int, message_id: int) -> dict:
    return _api_call("pinChatMessage", chat_id, message_id)


def unpin_message(chat_id: int, message_id: int) -> dict:
    return _api_call("unpinChatMessage", chat_id, message_id)


def _resolve_gif(phase: str, agent: str = None) -> str:
    """Resolve GIF filename. If agent specified, try agent-specific first."""
    if agent and phase in AGENT_PHASES:
        agent_gif = f"agent-{agent}-{phase}.gif"
        if os.path.exists(os.path.join(ASSETS_DIR, agent_gif)):
            return agent_gif
    return PHASE_GIFS.get(phase)


def send_animation(chat_id: int, phase: str, caption: str = "",
                   reply_markup: dict = None, agent: str = None) -> dict:
    """Send animated GIF for a MISO phase. Returns message with messageId."""
    token = _get_token()
    gif_file = _resolve_gif(phase, agent)
    if not gif_file:
        return {"ok": False, "error": f"Unknown phase: {phase}"}
    gif_path = os.path.join(ASSETS_DIR, gif_file)
    if not os.path.exists(gif_path):
        return {"ok": False, "error": f"GIF not found: {gif_path}"}

    url = f"https://api.telegram.org/bot{token}/sendAnimation"
    with open(gif_path, "rb") as f:
        gif_data = f.read()

    fields = {"chat_id": str(chat_id), "caption": caption, "parse_mode": "HTML"}
    if reply_markup:
        fields["reply_markup"] = json.dumps(reply_markup)
    files = {"animation": (gif_file, gif_data, "image/gif")}
    return _multipart_post(url, fields, files)


def edit_message_media(chat_id: int, message_id: int, phase: str,
                       caption: str = "", reply_markup: dict = None,
                       agent: str = None) -> dict:
    """Edit existing animation message with new phase GIF + caption."""
    token = _get_token()
    gif_file = _resolve_gif(phase, agent)
    if not gif_file:
        return {"ok": False, "error": f"Unknown phase: {phase}"}
    gif_path = os.path.join(ASSETS_DIR, gif_file)
    if not os.path.exists(gif_path):
        return {"ok": False, "error": f"GIF not found: {gif_path}"}

    url = f"https://api.telegram.org/bot{token}/editMessageMedia"
    with open(gif_path, "rb") as f:
        gif_data = f.read()

    media = {
        "type": "animation",
        "media": "attach://animation",
        "caption": caption,
        "parse_mode": "HTML",
    }
    fields = {
        "chat_id": str(chat_id),
        "message_id": str(message_id),
        "media": json.dumps(media),
    }
    if reply_markup:
        fields["reply_markup"] = json.dumps(reply_markup)
    files = {"animation": (gif_file, gif_data, "image/gif")}
    return _multipart_post(url, fields, files)


if __name__ == "__main__":
    usage = """Usage:
  python3 miso_telegram.py pin <chat_id> <message_id>
  python3 miso_telegram.py unpin <chat_id> <message_id>
  python3 miso_telegram.py send <chat_id> <phase> [caption] [--agent <name>]
  python3 miso_telegram.py edit <chat_id> <message_id> <phase> [caption] [--agent <name>]

Phases: init, running, partial, approval, complete, error
Agents: researcher, writer, reviewer, security (uses agent-specific GIF)"""

    if len(sys.argv) < 3:
        print(usage)
        sys.exit(1)

    action = sys.argv[1]

    if action == "pin":
        result = pin_message(int(sys.argv[2]), int(sys.argv[3]))
    elif action == "unpin":
        result = unpin_message(int(sys.argv[2]), int(sys.argv[3]))
    elif action == "send":
        chat_id = int(sys.argv[2])
        phase = sys.argv[3]
        agent = None
        caption_parts = []
        i = 4
        while i < len(sys.argv):
            if sys.argv[i] == "--agent" and i + 1 < len(sys.argv):
                agent = sys.argv[i + 1]
                i += 2
            else:
                caption_parts.append(sys.argv[i])
                i += 1
        caption = " ".join(caption_parts)
        result = send_animation(chat_id, phase, caption, agent=agent)
    elif action == "edit":
        chat_id = int(sys.argv[2])
        message_id = int(sys.argv[3])
        phase = sys.argv[4]
        agent = None
        caption_parts = []
        i = 5
        while i < len(sys.argv):
            if sys.argv[i] == "--agent" and i + 1 < len(sys.argv):
                agent = sys.argv[i + 1]
                i += 2
            else:
                caption_parts.append(sys.argv[i])
                i += 1
        caption = " ".join(caption_parts)
        result = edit_message_media(chat_id, message_id, phase, caption, agent=agent)
    else:
        print(usage)
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))
