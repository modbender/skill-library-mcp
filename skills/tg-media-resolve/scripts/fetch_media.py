#!/usr/bin/env python3
"""
Fetch media (photo/document/video) from a Telegram message via Bot API.
Downloads the largest available photo or the document/video file.

Usage:
    python3 fetch_media.py --bot-token TOKEN --chat-id CHAT_ID --message-id MSG_ID [--out DIR]

Outputs the local file path on success.
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error

API = "https://api.telegram.org"


def api_call(token: str, method: str, params: dict | None = None):
    url = f"{API}/bot{token}/{method}"
    if params:
        data = json.dumps(params).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    else:
        req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def download_file(token: str, file_path: str, out_path: str):
    url = f"{API}/file/bot{token}/{file_path}"
    urllib.request.urlretrieve(url, out_path)


def get_file_ext(file_path: str) -> str:
    _, ext = os.path.splitext(file_path)
    return ext if ext else ".bin"


def main():
    parser = argparse.ArgumentParser(description="Fetch media from a Telegram message")
    parser.add_argument("--bot-token", required=True, help="Telegram Bot API token")
    parser.add_argument("--chat-id", required=True, help="Chat ID")
    parser.add_argument("--message-id", required=True, help="Message ID to fetch media from")
    parser.add_argument("--out", default="/tmp", help="Output directory (default: /tmp)")
    parser.add_argument("--forward-to", default=None,
                        help="Chat ID to temporarily forward to (for fetching file_id). "
                             "Forwards are deleted after download. Defaults to --chat-id.")
    args = parser.parse_args()

    token = args.bot_token
    chat_id = args.chat_id
    msg_id = args.message_id
    out_dir = args.out
    forward_to = args.forward_to or chat_id

    os.makedirs(out_dir, exist_ok=True)

    # Forward the message to get full message object with file info
    try:
        result = api_call(token, "forwardMessage", {
            "chat_id": forward_to,
            "from_chat_id": chat_id,
            "message_id": int(msg_id),
        })
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"Error forwarding message: {e.code} {body}", file=sys.stderr)
        sys.exit(1)

    msg = result.get("result", {})
    fwd_msg_id = msg.get("message_id")

    # Find file_id from the forwarded message
    file_id = None
    file_name = None

    if "photo" in msg:
        # Get largest photo (last in array)
        photo = msg["photo"][-1]
        file_id = photo["file_id"]
        file_name = f"tg_{chat_id}_{msg_id}.jpg"
    elif "document" in msg:
        doc = msg["document"]
        file_id = doc["file_id"]
        file_name = doc.get("file_name", f"tg_{chat_id}_{msg_id}.bin")
    elif "video" in msg:
        vid = msg["video"]
        file_id = vid["file_id"]
        file_name = vid.get("file_name", f"tg_{chat_id}_{msg_id}.mp4")
    elif "animation" in msg:
        anim = msg["animation"]
        file_id = anim["file_id"]
        file_name = anim.get("file_name", f"tg_{chat_id}_{msg_id}.gif")
    elif "sticker" in msg:
        stk = msg["sticker"]
        file_id = stk["file_id"]
        file_name = f"tg_{chat_id}_{msg_id}.webp"
    elif "voice" in msg:
        file_id = msg["voice"]["file_id"]
        file_name = f"tg_{chat_id}_{msg_id}.ogg"
    elif "video_note" in msg:
        file_id = msg["video_note"]["file_id"]
        file_name = f"tg_{chat_id}_{msg_id}.mp4"
    elif "audio" in msg:
        aud = msg["audio"]
        file_id = aud["file_id"]
        file_name = aud.get("file_name", f"tg_{chat_id}_{msg_id}.mp3")

    # Clean up: delete the forwarded message
    if fwd_msg_id:
        try:
            api_call(token, "deleteMessage", {
                "chat_id": forward_to,
                "message_id": fwd_msg_id,
            })
        except Exception:
            pass  # best effort

    if not file_id:
        print("No media found in message", file=sys.stderr)
        sys.exit(1)

    # Get file path from Telegram servers
    file_info = api_call(token, "getFile", {"file_id": file_id})
    tg_file_path = file_info["result"]["file_path"]

    # Use proper extension from Telegram's file path if available
    tg_ext = get_file_ext(tg_file_path)
    name_base, name_ext = os.path.splitext(file_name)
    if not name_ext or name_ext == ".bin":
        file_name = name_base + tg_ext

    out_path = os.path.join(out_dir, file_name)
    download_file(token, tg_file_path, out_path)

    print(out_path)


if __name__ == "__main__":
    main()
