#!/usr/bin/env python3
import argparse
import base64
import hashlib
import ipaddress
import json
import math
import os
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from typing import Any, Dict, List, Optional, Tuple

def _is_disallowed_host(host: str) -> bool:
    """Check if host is internal/private (SSRF protection)."""
    if not host:
        return True

    lowered = host.lower().rstrip(".")
    if lowered in ("localhost", "localhost.localdomain"):
        return True
    if lowered.endswith(".local") or lowered.endswith(".internal"):
        return True
    if lowered in ("metadata.google.internal", "169.254.169.254"):
        return True

    try:
        ip = ipaddress.ip_address(lowered)
        return not ip.is_global
    except ValueError:
        return False


def _resolve_and_validate_host(hostname: str) -> None:
    """Resolve hostname and validate IP to prevent DNS rebinding attacks."""
    import socket

    try:
        addr_info = socket.getaddrinfo(hostname, None)
    except socket.gaierror as exc:
        raise ValueError(f"Cannot resolve hostname: {hostname}") from exc

    for _, _, _, _, sockaddr in addr_info:
        ip = sockaddr[0]
        if _is_disallowed_host(ip):
            raise ValueError(f"Resolved IP {ip} for {hostname} is disallowed")


def _sanitize_api_url(url: str) -> str:
    """Sanitize API URL to prevent SSRF attacks."""
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme.lower() not in ("http", "https"):
        raise ValueError(f"API URL must use HTTP or HTTPS scheme: {url}")

    host = (parsed.hostname or "").lower().rstrip(".")
    if not host:
        raise ValueError("API URL must have a valid hostname")

    # First check: hostname string validation
    if _is_disallowed_host(host):
        raise ValueError(f"API URL points to disallowed host: {host}")

    # Second check: DNS rebinding protection - resolve and validate IP
    _resolve_and_validate_host(host)

    # Third check: path traversal prevention
    path = urllib.parse.unquote(parsed.path or "/")
    if ".." in path or "//" in path.replace("//", "/"):
        raise ValueError(f"API URL contains suspicious path traversal: {path}")

    # Check against allowlist if configured
    allow_hosts = os.getenv("QUOTLY_API_ALLOW_HOSTS", "")
    if allow_hosts:
        allowed = {h.strip().lower().rstrip(".") for h in allow_hosts.split(",") if h.strip()}
        if host not in allowed:
            raise ValueError(f"API URL host not in allowlist: {host}")

    return parsed._replace(fragment="", username=None, password=None).geturl()


def _first_non_empty(*values: Any) -> Any:
    for value in values:
        if isinstance(value, str):
            text = value.strip()
            if text:
                return text
            continue
        if value not in (None, {}, [], ()):
            return value
    return None


def _audit_log(action: str, details: Dict[str, Any]) -> None:
    """Write audit log for security events."""
    import datetime

    audit_enabled = os.getenv("QUOTLY_AUDIT_LOG", "").lower() in ("1", "true", "yes")
    if not audit_enabled:
        return

    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    log_entry = {"timestamp": timestamp, "action": action, **details}
    # Log to stderr for capture by logging infrastructure
    print(f"AUDIT: {json.dumps(log_entry, ensure_ascii=False)}", file=sys.stderr)


def _parse_env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw.strip())
    except ValueError:
        print(
            f"WARN: Invalid integer env {name}={raw!r}, using default {default}.",
            file=sys.stderr,
        )
    return default


def _as_int(value: Any, default: int) -> int:
    try:
        return int(str(value).strip())
    except Exception:
        return default


def _clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, value))


def _estimate_canvas_height(messages: List[Dict[str, Any]]) -> int:
    # Keep short quotes compact while giving multi-line batches room.
    total_chars = 0
    for message in messages:
        text = str(message.get("text") or "")
        total_chars += len(text.strip())
    text_lines = max(1, math.ceil(total_chars / 18))
    estimated = 180 + text_lines * 44 + max(0, len(messages) - 1) * 52
    return _clamp(estimated, 320, 1024)


def _clean_name(*parts: Any) -> Optional[str]:
    items = []
    for part in parts:
        if isinstance(part, str) and part.strip():
            items.append(part.strip())
    if not items:
        return None
    return " ".join(items)


def _extract_message_items(input_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract message items from selected_messages.

    Each item should have:
    - message: { message_id, text, forward_from }
    - overwrite_message (optional): { text, forward_from }
    """
    selected_messages = input_payload.get("selected_messages")
    if not isinstance(selected_messages, list):
        return []

    items: List[Dict[str, Any]] = []

    for item in selected_messages:
        if not isinstance(item, dict):
            continue

        message = item.get("message")
        if not isinstance(message, dict):
            continue

        items.append({
            "payload": item,
            "message": message,
        })

    return items


def _extract_forward_from_message(message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract forward source info from message.

    Forward source format:
    {
        "type": "hidden_user",  # optional, indicates hidden user
        "id": 123456789,        # optional, user id
        "first_name": "张",     # required, first name or nickname
        "last_name": "三",      # optional, last name
        "avatar_url": "",       # optional, avatar url or base64 data
        "status_url": ""        # optional, status url or base64 data
    }
    """
    forward_from = message.get("forward_from")
    if isinstance(forward_from, dict):
        # New simplified format
        first_name = _first_non_empty(forward_from.get("first_name"))
        last_name = _first_non_empty(forward_from.get("last_name"))
        name = _first_non_empty(
            forward_from.get("name"),
            _clean_name(first_name, last_name),
        )
        return {
            "id": forward_from.get("id"),
            "first_name": first_name,
            "last_name": last_name,
            "name": name,
            "avatar": _first_non_empty(
                forward_from.get("avatar_url"),
                forward_from.get("avatar"),
            ),
            "status_url": _first_non_empty(
                forward_from.get("status_url"),
                forward_from.get("status"),
            ),
        }

    return {}


def _extract_entities(
    item_payload: Dict[str, Any],
    message: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Extract message entities (formatting) from message or overwrite_message."""
    # First check overwrite_message
    overwrite = item_payload.get("overwrite_message")
    if isinstance(overwrite, dict):
        entities = overwrite.get("entities")
        if isinstance(entities, list):
            return _sanitize_entities(entities)

    # Then check message
    entities = message.get("entities")
    if isinstance(entities, list):
        return _sanitize_entities(entities)

    # Also check caption_entities for media messages
    caption_entities = message.get("caption_entities")
    if isinstance(caption_entities, list):
        return _sanitize_entities(caption_entities)

    return []


def _apply_default_entities(text: str) -> List[Dict[str, Any]]:
    """Apply default entity styling to text.

    Default styles:
    - URLs -> text_link
    - @mentions -> mention
    - #hashtags -> hashtag
    - **bold** -> bold (markdown style)
    - *italic* or _italic_ -> italic
    - `code` -> code
    """
    import re

    entities: List[Dict[str, Any]] = []

    # URL pattern
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    for match in re.finditer(url_pattern, text):
        entities.append({
            "type": "text_link",
            "offset": match.start(),
            "length": match.end() - match.start(),
            "url": match.group()
        })

    # @mention pattern
    mention_pattern = r'@[\w\d_]+'
    for match in re.finditer(mention_pattern, text):
        entities.append({
            "type": "mention",
            "offset": match.start(),
            "length": match.end() - match.start()
        })

    # #hashtag pattern
    hashtag_pattern = r'#[\w\d_]+'
    for match in re.finditer(hashtag_pattern, text):
        entities.append({
            "type": "hashtag",
            "offset": match.start(),
            "length": match.end() - match.start()
        })

    # **bold** markdown
    bold_pattern = r'\*\*(.+?)\*\*'
    for match in re.finditer(bold_pattern, text):
        entities.append({
            "type": "bold",
            "offset": match.start(),
            "length": match.end() - match.start()
        })

    # *italic* or _italic_ markdown
    italic_pattern = r'\*(.+?)\*|_(.+?)_'
    for match in re.finditer(italic_pattern, text):
        entities.append({
            "type": "italic",
            "offset": match.start(),
            "length": match.end() - match.start()
        })

    # `code` inline code
    code_pattern = r'`([^`]+)`'
    for match in re.finditer(code_pattern, text):
        entities.append({
            "type": "code",
            "offset": match.start(),
            "length": match.end() - match.start()
        })

    # Sort by offset to maintain order
    entities.sort(key=lambda e: e["offset"])

    # Remove overlapping entities (keep first one)
    filtered: List[Dict[str, Any]] = []
    last_end = 0
    for entity in entities:
        if entity["offset"] >= last_end:
            filtered.append(entity)
            last_end = entity["offset"] + entity["length"]

    return filtered


def _sanitize_entities(entities: List[Any]) -> List[Dict[str, Any]]:
    """Sanitize and validate entity list for QuotLy API."""
    valid_types = {
        "mention", "hashtag", "cashtag", "bot_command", "url", "email",
        "phone_number", "bold", "italic", "underline", "strikethrough",
        "spoiler", "code", "pre", "text_link", "text_mention", "custom_emoji",
    }
    sanitized: List[Dict[str, Any]] = []

    for entity in entities:
        if not isinstance(entity, dict):
            continue
        entity_type = entity.get("type")
        if entity_type not in valid_types:
            continue
        offset = entity.get("offset")
        length = entity.get("length")
        if not isinstance(offset, int) or not isinstance(length, int):
            continue
        if offset < 0 or length <= 0:
            continue

        clean_entity: Dict[str, Any] = {
            "type": entity_type,
            "offset": offset,
            "length": length,
        }
        # Optional fields
        if "url" in entity and isinstance(entity["url"], str):
            clean_entity["url"] = entity["url"]
        if "user" in entity and isinstance(entity["user"], dict):
            clean_entity["user"] = entity["user"]
        if "language" in entity and isinstance(entity["language"], str):
            clean_entity["language"] = entity["language"]
        if "custom_emoji_id" in entity and isinstance(entity["custom_emoji_id"], str):
            clean_entity["custom_emoji_id"] = entity["custom_emoji_id"]

        sanitized.append(clean_entity)

    return sanitized


def _extract_text(
    item_payload: Dict[str, Any],
    message: Dict[str, Any],
) -> str:
    """Extract quote text from overwrite_message or message."""
    overwrite = item_payload.get("overwrite_message")
    if isinstance(overwrite, dict):
        text = _first_non_empty(overwrite.get("text"))
        if text:
            return str(text)
    return str(_first_non_empty(message.get("text"), message.get("caption"), ""))


def _decode_image_base64(image_data: str) -> bytes:
    payload = image_data.strip()
    if payload.startswith("data:image") and "," in payload:
        payload = payload.split(",", 1)[1]
    payload = payload.replace("\n", "").replace("\r", "")
    missing_padding = len(payload) % 4
    if missing_padding:
        payload += "=" * (4 - missing_padding)
    return base64.b64decode(payload)


def _looks_like_webp(data: bytes) -> bool:
    return len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP"


def _request_quote_api_bytes(
    api_url: str, payload: Dict[str, Any], timeout_seconds: float
) -> bytes:
    # Enforce max payload size (1MB)
    payload_bytes = json.dumps(payload).encode("utf-8")
    max_payload_size = 1024 * 1024
    if len(payload_bytes) > max_payload_size:
        raise ValueError(f"Payload exceeds maximum size of {max_payload_size} bytes")

    request = urllib.request.Request(
        api_url,
        data=payload_bytes,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "openclaw-quotly-skill/1.0",
            "Accept": "application/json,image/webp,*/*",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        # Enforce max response size (10MB)
        max_response_size = 10 * 1024 * 1024
        content_length = response.headers.get("Content-Length")
        if content_length and int(content_length) > max_response_size:
            raise ValueError(f"Response exceeds maximum size of {max_response_size} bytes")
        data = response.read(max_response_size + 1)
        if len(data) > max_response_size:
            raise ValueError(f"Response exceeds maximum size of {max_response_size} bytes")
        return data


def _generate_quote_image(
    payload: Dict[str, Any], api_url: str, timeout_seconds: float
) -> bytes:
    urls = [api_url]
    if not api_url.lower().endswith(".webp"):
        urls.append(f"{api_url}.webp")

    last_error: Optional[Exception] = None
    for url in urls:
        try:
            body = _request_quote_api_bytes(url, payload, timeout_seconds)
            if _looks_like_webp(body):
                return body
            result = json.loads(body.decode("utf-8"))
            # Try to extract image from result
            image_data = result.get("image")
            if isinstance(image_data, str) and image_data.strip():
                return _decode_image_base64(image_data)
            # Try nested result.image
            nested_result = result.get("result")
            if isinstance(nested_result, dict):
                image_data = nested_result.get("image")
                if isinstance(image_data, str) and image_data.strip():
                    return _decode_image_base64(image_data)
            raise RuntimeError(f"Invalid QuotLy response: {result}")
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            json.JSONDecodeError,
            RuntimeError,
        ) as exc:
            last_error = exc

    if last_error is not None:
        raise last_error
    raise RuntimeError("Failed to generate quote image.")


def _is_secure_posix_tmp_dir(path_value: str) -> bool:
    if not os.path.isdir(path_value) or os.path.islink(path_value):
        return False
    if not hasattr(os, "getuid"):
        return True
    try:
        st = os.stat(path_value, follow_symlinks=False)
    except OSError:
        return False
    if st.st_uid != os.getuid():
        return False
    return (st.st_mode & 0o022) == 0


def _resolve_openclaw_tmp_dir() -> str:
    base_tmp = os.path.abspath(tempfile.gettempdir())
    uid = os.getuid() if hasattr(os, "getuid") else None
    fallback_name = "openclaw" if uid is None else f"openclaw-{uid}"
    fallback_dir = os.path.join(base_tmp, fallback_name)

    if os.name != "posix":
        return fallback_dir

    preferred_dir = "/tmp/openclaw"
    if _is_secure_posix_tmp_dir(preferred_dir) and os.access(
        preferred_dir, os.W_OK | os.X_OK
    ):
        return preferred_dir

    if not os.path.exists(preferred_dir):
        try:
            if os.path.isdir("/tmp") and os.access("/tmp", os.W_OK | os.X_OK):
                os.makedirs(preferred_dir, mode=0o700, exist_ok=True)
        except OSError:
            pass
        if _is_secure_posix_tmp_dir(preferred_dir) and os.access(
            preferred_dir, os.W_OK | os.X_OK
        ):
            return preferred_dir

    return fallback_dir


def _resolve_output_dir() -> str:
    """Resolve a safe output directory for stickers."""
    candidates = [
        # Prefer OpenClaw's temp root so local-media allowlists accept MEDIA paths.
        _resolve_openclaw_tmp_dir(),
        # Keep workspace-local output as a fallback for local/dev runs.
        os.path.join(os.getcwd(), ".openclaw-media"),
        tempfile.gettempdir(),
    ]

    seen: set[str] = set()
    for candidate in candidates:
        normalized = os.path.abspath(candidate)
        if normalized in seen:
            continue
        seen.add(normalized)
        try:
            os.makedirs(normalized, exist_ok=True)
        except OSError:
            continue
        if os.path.isdir(normalized) and os.access(normalized, os.W_OK):
            return normalized

    raise RuntimeError("No writable directory available for sticker output.")


def _save_temp_webp(image_bytes: bytes) -> str:
    output_dir = _resolve_output_dir()
    path = os.path.join(output_dir, f"quotly-{uuid.uuid4().hex}.webp")
    with open(path, "wb") as handle:
        handle.write(image_bytes)
    return os.path.abspath(path)


def _stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _resolve_context_event(input_payload: Dict[str, Any]) -> Dict[str, Any]:
    context = input_payload.get("context")
    if isinstance(context, dict):
        event = context.get("event")
        if isinstance(event, dict):
            return event
    event = input_payload.get("event")
    if isinstance(event, dict):
        return event
    return {}


def _payload_hash_dedupe_key(input_payload: Dict[str, Any]) -> Optional[str]:
    selected_messages = input_payload.get("selected_messages")
    if not isinstance(selected_messages, list) or not selected_messages:
        return None
    digest = hashlib.sha256(_stable_json(selected_messages).encode("utf-8")).hexdigest()
    return f"payload:{digest[:32]}"


def _build_dedupe_key(input_payload: Dict[str, Any]) -> Optional[str]:
    event = _resolve_context_event(input_payload)
    channel = str(_first_non_empty(event.get("channel"), "unknown")).strip().lower()

    for key in ("update_id", "event_id", "delivery_id", "id"):
        value = event.get(key)
        if value is None:
            continue
        value_text = str(value).strip()
        if value_text:
            return f"{channel}:{key}:{value_text}"

    nested_update = event.get("update")
    if isinstance(nested_update, dict):
        value = nested_update.get("update_id")
        if value is not None:
            value_text = str(value).strip()
            if value_text:
                return f"{channel}:update_id:{value_text}"

    return _payload_hash_dedupe_key(input_payload)


def _dedupe_cache_path() -> str:
    base_dir = _resolve_openclaw_tmp_dir()
    os.makedirs(base_dir, exist_ok=True)
    return os.path.join(base_dir, "quotly-dedup-cache.json")


def _load_dedupe_cache(path: str) -> Dict[str, float]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except FileNotFoundError:
        return {}
    except (OSError, json.JSONDecodeError):
        return {}

    if not isinstance(payload, dict):
        return {}

    cleaned: Dict[str, float] = {}
    for key, value in payload.items():
        if not isinstance(key, str):
            continue
        if isinstance(value, (int, float)):
            cleaned[key] = float(value)
    return cleaned


def _save_dedupe_cache(path: str, cache: Dict[str, float]) -> None:
    temp_path = f"{path}.{uuid.uuid4().hex}.tmp"
    with open(temp_path, "w", encoding="utf-8") as handle:
        json.dump(cache, handle, ensure_ascii=False, separators=(",", ":"))
    os.replace(temp_path, path)


def _acquire_lock(lock_path: str, timeout_seconds: float = 2.0) -> bool:
    deadline = time.time() + max(0.1, timeout_seconds)
    while time.time() < deadline:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            return True
        except FileExistsError:
            time.sleep(0.05)
        except OSError:
            return False
    return False


def _release_lock(lock_path: str) -> None:
    try:
        os.unlink(lock_path)
    except OSError:
        pass


def _is_duplicate_recent(dedupe_key: str, dedupe_window_seconds: int) -> bool:
    if dedupe_window_seconds <= 0:
        return False

    cache_path = _dedupe_cache_path()
    lock_path = f"{cache_path}.lock"
    if not _acquire_lock(lock_path):
        # Fail open: if lock can't be acquired, proceed with generation.
        return False

    now = time.time()
    retention_seconds = max(dedupe_window_seconds * 4, 900)
    try:
        cache = _load_dedupe_cache(cache_path)
        fresh_cache: Dict[str, float] = {}
        for key, timestamp in cache.items():
            if now - timestamp < retention_seconds:
                fresh_cache[key] = timestamp

        last_seen = fresh_cache.get(dedupe_key)
        is_duplicate = isinstance(last_seen, float) and (now - last_seen) < dedupe_window_seconds
        if not is_duplicate:
            fresh_cache[dedupe_key] = now

        _save_dedupe_cache(cache_path, fresh_cache)
        return is_duplicate
    finally:
        _release_lock(lock_path)


def _sanitize_avatar_for_renderer(avatar_value: Any) -> Optional[str]:
    """Sanitize avatar URL for QuotLy renderer. Only accepts data URLs and simple HTTPS URLs."""
    if not isinstance(avatar_value, str):
        return None

    avatar = avatar_value.strip()
    if not avatar:
        return None

    # Accept data URLs (base64 encoded images)
    if avatar.lower().startswith("data:image/"):
        return avatar

    # Accept simple HTTPS URLs without credentials
    parsed = urllib.parse.urlparse(avatar)
    if parsed.scheme.lower() != "https":
        return None
    if parsed.username or parsed.password:
        return None

    # Remove fragment and return clean URL
    return parsed._replace(fragment="").geturl()


def _split_display_name(name: str) -> Tuple[str, Optional[str]]:
    text = name.strip()
    if not text:
        return "Unknown", None
    parts = text.split(" ", 1)
    first_name = parts[0]
    last_name = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
    return first_name, last_name


def _resolve_source_profile(
    item_payload: Dict[str, Any],
    message: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Resolve source profile from forward_from or overwrite_message.forward_from.

    Priority:
    1. overwrite_message.forward_from (user override)
    2. message.forward_from (original forward source)
    """
    # Check for overwrite in payload
    overwrite = item_payload.get("overwrite_message")
    if isinstance(overwrite, dict):
        overwrite_forward = overwrite.get("forward_from")
        if isinstance(overwrite_forward, dict):
            # Build profile from overwrite
            first_name = _first_non_empty(overwrite_forward.get("first_name"))
            last_name = _first_non_empty(overwrite_forward.get("last_name"))
            name = _first_non_empty(
                overwrite_forward.get("name"),
                _clean_name(first_name, last_name),
            )
            return {
                "id": overwrite_forward.get("id"),
                "first_name": first_name,
                "last_name": last_name,
                "name": name,
                "avatar": _first_non_empty(
                    overwrite_forward.get("avatar_url"),
                    overwrite_forward.get("avatar"),
                ),
                "status_url": _first_non_empty(
                    overwrite_forward.get("status_url"),
                    overwrite_forward.get("status"),
                ),
            }

    # Use message forward_from
    return _extract_forward_from_message(message)


def _build_quote_message(
    item_payload: Dict[str, Any],
    message: Dict[str, Any],
    args: argparse.Namespace,
) -> Optional[Dict[str, Any]]:
    """
    Build a quote message for the QuotLy API.

    Uses forward_from for source info and supports overwrite_message for overrides.
    """
    source_profile = _resolve_source_profile(item_payload, message)

    # Extract source info from profile
    source_id = source_profile.get("id")
    source_first_name = _first_non_empty(source_profile.get("first_name"))
    source_last_name = _first_non_empty(source_profile.get("last_name"))
    source_name = str(
        _first_non_empty(
            _clean_name(source_first_name, source_last_name),
            source_profile.get("name"),
            "Unknown",
        )
    )
    source_avatar = source_profile.get("avatar")

    # Get quote text and entities
    quote_text = _extract_text(item_payload, message)
    if not quote_text.strip():
        return None

    # Extract entities from message or overwrite_message
    entities = _extract_entities(item_payload, message)

    # Build message_from for QuotLy API
    first_name, last_name = _split_display_name(source_name)
    if source_first_name:
        first_name = str(source_first_name)
    if source_last_name:
        last_name = str(source_last_name)

    message_from: Dict[str, Any] = {"id": source_id if source_id is not None else 0}
    message_from["first_name"] = first_name
    if last_name:
        message_from["last_name"] = last_name
    message_from["name"] = source_name

    # Handle avatar
    if source_avatar:
        sanitized_avatar = _sanitize_avatar_for_renderer(source_avatar)
        if sanitized_avatar:
            message_from["photo"] = {"url": str(sanitized_avatar)}

    # Apply default entity styling if no entities provided
    if not entities:
        entities = _apply_default_entities(quote_text)

    return {
        "entities": entities,
        "avatar": True,
        "from": message_from,
        "text": quote_text,
    }


def _load_input_payload(input_arg: str) -> Dict[str, Any]:
    if input_arg == "-":
        raw = sys.stdin.read()
        if not raw.strip():
            raise RuntimeError(
                "Stdin is empty. Provide JSON via stdin when using --input -."
            )
        payload = json.loads(raw)
    else:
        with open(input_arg, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    if not isinstance(payload, dict):
        raise RuntimeError("Input payload must be a JSON object.")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate QuotLy-style sticker and output MEDIA path for OpenClaw.",
        epilog=(
            "Environment variables:\n"
            "  QUOTLY_API_URL - QuotLy API endpoint (default: https://bot.lyo.su/quote/generate).\n"
            "  QUOTLY_API_ALLOW_HOSTS - Comma-separated list of allowed API hosts.\n"
            "  QUOTLY_DEDUP_WINDOW_SECONDS - Suppress duplicate requests within N seconds (default: 180)."
        ),
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input JSON file, or '-' to read JSON from stdin.",
    )
    parser.add_argument(
        "--timeout", type=float, default=20.0, help="Network timeout seconds."
    )
    args = parser.parse_args()

    try:
        input_payload = _load_input_payload(args.input)
        dedupe_window_seconds = _parse_env_int("QUOTLY_DEDUP_WINDOW_SECONDS", 180)
        dedupe_key = _build_dedupe_key(input_payload)
        if dedupe_key and _is_duplicate_recent(dedupe_key, dedupe_window_seconds):
            _audit_log(
                "generation_duplicate_skipped",
                {"dedupe_key": dedupe_key, "window_seconds": dedupe_window_seconds},
            )
            print(
                f"WARN: Duplicate request skipped for dedupe key: {dedupe_key}",
                file=sys.stderr,
            )
            return 0

        message_items = _extract_message_items(input_payload)
        if not message_items:
            raise RuntimeError(
                "selected_messages is required and must contain at least one message item."
            )

        quote_messages: List[Dict[str, Any]] = []
        for idx, item in enumerate(message_items, start=1):
            quote_message = _build_quote_message(
                item["payload"],
                item["message"],
                args,
            )
            if quote_message is None:
                print(
                    f"WARN: Skipping message #{idx} because no renderable text was found.",
                    file=sys.stderr,
                )
                continue
            quote_messages.append(quote_message)

        if not quote_messages:
            raise RuntimeError(
                "No quote text available. Provide overwrite_message.text or message.text."
            )

        width = _as_int(input_payload.get("width", 512), 512)
        height = _as_int(
            input_payload.get("height", _estimate_canvas_height(quote_messages)),
            _estimate_canvas_height(quote_messages),
        )

        quotly_payload = {
            "type": "quote",
            "format": "webp",
            "backgroundColor": str(input_payload.get("background_color", "#1b1429")),
            "width": _clamp(width, 256, 1024),
            "height": _clamp(height, 320, 1024),
            "scale": _as_int(input_payload.get("scale", 2), 2),
            "maxWidth": _as_int(input_payload.get("max_width", 300), 300),
            "borderRadius": _as_int(input_payload.get("border_radius", 28), 28),
            "pictureRadius": _as_int(input_payload.get("picture_radius", 512), 512),
            "messages": quote_messages,
        }

        # Get and sanitize API URL to prevent SSRF
        api_url = os.getenv("QUOTLY_API_URL", "https://bot.lyo.su/quote/generate")
        _audit_log("api_request", {"url": api_url, "message_count": len(quote_messages)})
        api_url = _sanitize_api_url(api_url)
        image_bytes = _generate_quote_image(quotly_payload, api_url, args.timeout)
        media_path = _save_temp_webp(image_bytes)

        _audit_log("generation_success", {"media_path": media_path, "size_bytes": len(image_bytes)})
        print("Quote sticker generated.")
        print(f"MEDIA:{media_path}")
        return 0
    except Exception as exc:
        _audit_log("generation_failed", {"error": str(exc), "error_type": type(exc).__name__})
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
