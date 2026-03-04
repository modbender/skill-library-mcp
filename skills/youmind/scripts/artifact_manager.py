#!/usr/bin/env python3
"""Extract image/slides/doc artifacts from chat detail payloads."""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent))

from api_client import AuthError, YoumindApiClient


URL_RE = re.compile(r"https?://[^\"\s,]+")


def _dedup(items: List[str]) -> List[str]:
    out: List[str] = []
    seen = set()
    for item in items:
        if not item:
            continue
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def _extract_urls_from_obj(obj: Any) -> List[str]:
    text = json.dumps(obj, ensure_ascii=False)
    return _dedup(URL_RE.findall(text))


def _resolve_board_id(client: YoumindApiClient, board_id: Optional[str], board_url: Optional[str]) -> str:
    if board_id:
        return board_id
    if board_url:
        return client.board_id_from_url(board_url)
    raise ValueError("Provide --board-id or --board-url")


def _latest_chat_id(history_payload: Dict[str, Any]) -> Optional[str]:
    rows = history_payload.get("data", []) if isinstance(history_payload, dict) else []
    if not rows:
        return None
    return rows[0].get("id")


def _find_last_assistant_message(detail: Dict[str, Any]) -> Dict[str, Any]:
    messages = detail.get("messages", []) if isinstance(detail, dict) else []
    assistants = [m for m in messages if isinstance(m, dict) and m.get("role") == "assistant"]
    if not assistants:
        return {}
    return assistants[-1]


def _find_tool_block(message: Dict[str, Any]) -> Dict[str, Any]:
    blocks = message.get("blocks", []) if isinstance(message, dict) else []
    tool_blocks = [b for b in blocks if isinstance(b, dict) and b.get("type") == "tool"]
    if not tool_blocks:
        return {}
    # Usually there is only one tool block in generated artifact responses.
    return tool_blocks[-1]


def _artifact_from_tool(tool_block: Dict[str, Any], include_raw_content: bool = False) -> Dict[str, Any]:
    tool_name = tool_block.get("tool_name")
    tr = tool_block.get("tool_result") or {}

    result: Dict[str, Any] = {
        "tool_name": tool_name,
        "tool_status": tool_block.get("status"),
        "artifact_type": "unknown",
        "urls": [],
        "media_ids": [],
        "slides": [],
        "page_id": None,
        "content_preview": None,
        "raw_content": None,
        "tool_result": tr,
    }

    if tool_name == "image_generate":
        result["artifact_type"] = "image"
        image_urls = tr.get("image_urls") or []
        original_urls = tr.get("original_image_urls") or []
        media_ids = tr.get("mediaIds") or []
        result["urls"] = _dedup(list(original_urls) + list(image_urls))
        result["media_ids"] = list(media_ids)

    elif tool_name == "slides_generate":
        result["artifact_type"] = "slides"
        slides = tr.get("slides") or []
        result["slides"] = slides
        urls: List[str] = []
        media_ids: List[str] = []
        for slide in slides:
            if not isinstance(slide, dict):
                continue
            if slide.get("originalImageUrl"):
                urls.append(slide["originalImageUrl"])
            if slide.get("imageUrl"):
                urls.append(slide["imageUrl"])
            if slide.get("mediaId"):
                media_ids.append(slide["mediaId"])
        result["urls"] = _dedup(urls)
        result["media_ids"] = _dedup(media_ids)

    elif tool_name == "write":
        result["artifact_type"] = "doc"
        page = tr.get("page") or {}
        content = tr.get("content") or {}
        result["page_id"] = page.get("id")
        result["content_preview"] = content.get("contentPreview")
        if include_raw_content:
            result["raw_content"] = ((page.get("content") or {}).get("raw"))
        result["urls"] = _extract_urls_from_obj({"page": page, "content": content})

    else:
        # Generic fallback for unknown future tool types.
        result["artifact_type"] = "unknown"
        result["urls"] = _extract_urls_from_obj(tr)

    return result


def extract_from_chat_detail(detail: Dict[str, Any], include_raw_content: bool = False) -> Dict[str, Any]:
    assistant = _find_last_assistant_message(detail)
    tool_block = _find_tool_block(assistant)

    if not assistant:
        return {
            "ok": False,
            "error": "No assistant message found",
            "chat_id": detail.get("id"),
            "title": detail.get("title"),
        }

    if not tool_block:
        return {
            "ok": False,
            "error": "No tool block found in last assistant message",
            "chat_id": detail.get("id"),
            "title": detail.get("title"),
            "assistant_status": assistant.get("status"),
            "assistant_blocks": assistant.get("blocks", []),
        }

    artifact = _artifact_from_tool(tool_block, include_raw_content=include_raw_content)

    return {
        "ok": True,
        "chat_id": detail.get("id"),
        "title": detail.get("title"),
        "assistant_status": assistant.get("status"),
        "assistant_message_id": assistant.get("id"),
        "artifact": artifact,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract generated artifacts from Youmind chat messages")
    sub = parser.add_subparsers(dest="command", required=True)

    p_extract = sub.add_parser("extract", help="Extract artifact from a specific chat id")
    p_extract.add_argument("--chat-id", required=True)
    p_extract.add_argument("--include-raw-content", action="store_true", help="Include document raw content for write tool")

    p_latest = sub.add_parser("extract-latest", help="Extract artifact from latest chat in a board")
    p_latest.add_argument("--board-id")
    p_latest.add_argument("--board-url")
    p_latest.add_argument("--include-raw-content", action="store_true", help="Include document raw content for write tool")

    args = parser.parse_args()

    try:
        client = YoumindApiClient()

        if args.command == "extract":
            detail = client.get_chat_detail(args.chat_id)
            print(json.dumps(extract_from_chat_detail(detail, include_raw_content=args.include_raw_content), indent=2, ensure_ascii=False))
            return 0

        if args.command == "extract-latest":
            board_id = _resolve_board_id(client, args.board_id, args.board_url)
            history = client.list_chat_history(board_id)
            chat_id = _latest_chat_id(history)
            if not chat_id:
                print(json.dumps({"ok": False, "error": "No chats found", "board_id": board_id}, indent=2, ensure_ascii=False))
                return 1
            detail = client.get_chat_detail(chat_id)
            payload = extract_from_chat_detail(detail, include_raw_content=args.include_raw_content)
            payload["board_id"] = board_id
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return 0

        parser.print_help()
        return 1

    except AuthError as exc:
        print(f"❌ Auth error: {exc}")
        print("Run: python scripts/run.py auth_manager.py setup")
        return 1
    except Exception as exc:
        print(f"❌ Error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
