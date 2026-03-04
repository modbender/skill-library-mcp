"""
notify.py — Shared multi-channel notification for restart-guard.
"""

import json
import os
import subprocess


def dotenv_get(key):
    env_path = os.path.expanduser("~/.openclaw/.env")
    if not os.path.isfile(env_path):
        return ""
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() == key:
                    return v.strip().strip('"').strip("'")
    except Exception:
        pass
    return ""


def _resolve_env(env_name):
    return os.environ.get(env_name, "") or dotenv_get(env_name)


def notify(notif_config, full_config, oc_bin, message):
    result = notify_with_result(notif_config, full_config, oc_bin, message)
    return bool(result.get("ok", False))


def notify_with_result(notif_config, full_config, oc_bin, message):
    """
    Send notification and return detailed delivery result.
    """
    notif_config = notif_config if isinstance(notif_config, dict) else {}
    primary = str(notif_config.get("primary", "openclaw")).strip().lower()
    attempted = []
    succeeded = []

    if primary == "openclaw":
        attempted.append("openclaw")
        if _notify_openclaw(notif_config, full_config, oc_bin, message):
            succeeded.append("openclaw")

    channels = _normalize_channels(notif_config.get("channels", []))
    if not channels:
        fallback = str(notif_config.get("fallback", "")).strip()
        if fallback:
            channels = [fallback]

    for ch in channels:
        ch = ch.strip().lower()
        if not ch or ch in {"none", "off", "disabled", "webui"}:
            continue
        attempted.append(ch)
        try:
            if ch == "telegram":
                ok = _notify_telegram(notif_config, message)
            elif ch == "discord":
                ok = _notify_discord(notif_config, message)
            elif ch == "slack":
                ok = _notify_slack(notif_config, message)
            elif ch == "webhook":
                ok = _notify_webhook(notif_config, message)
            else:
                # Generic passthrough for channels like feishu, teams, etc.
                ok = _notify_openclaw(
                    notif_config, full_config, oc_bin, message, force_channel=ch
                )
            if ok:
                succeeded.append(ch)
        except Exception:
            continue
    return {
        "ok": bool(succeeded),
        "attempted": attempted,
        "succeeded": succeeded,
    }


def _normalize_channels(raw):
    if isinstance(raw, list):
        return [str(x) for x in raw if str(x).strip()]
    if isinstance(raw, str):
        text = raw.strip()
        if not text:
            return []
        if text.startswith("[") and text.endswith("]"):
            try:
                parsed = json.loads(text)
                if isinstance(parsed, list):
                    return [str(x) for x in parsed if str(x).strip()]
            except Exception:
                pass
        return [x.strip() for x in text.split(",") if x.strip()]
    return []


def _notify_openclaw(notif_config, full_config, oc_bin, message, force_channel=""):
    if not oc_bin:
        return False
    oc_notif = notif_config.get("openclaw", {})
    if not isinstance(oc_notif, dict):
        oc_notif = {}

    gateway_cfg = full_config.get("gateway", {}) if isinstance(full_config, dict) else {}
    host = str(gateway_cfg.get("host", "127.0.0.1"))
    port = str(gateway_cfg.get("port", "18789"))
    try:
        from write_context import validate_host_port
        host, port = validate_host_port(host, port)
    except ValueError:
        # Skip HTTP path on validation failure - fall through to CLI fallback below
        host = None
    auth_env = str(gateway_cfg.get("auth_token_env", "GATEWAY_AUTH_TOKEN"))
    auth_token = _resolve_env(auth_env)

    channel = str(force_channel or oc_notif.get("channel", "")).strip()
    target = str(oc_notif.get("target", "") or oc_notif.get("to", "")).strip()

    # Derive target for known channels when possible.
    if not target and channel == "telegram":
        target = str((notif_config.get("telegram", {}) or {}).get("chat_id", "")).strip()
    if not target and channel and isinstance(notif_config.get(channel), dict):
        target = str((notif_config.get(channel, {}) or {}).get("target", "")).strip()

    args_obj = {"action": "send", "message": message}
    if channel:
        args_obj["channel"] = channel
    if target:
        args_obj["target"] = target
        args_obj["to"] = target

    # Skip HTTP if validation failed (host is None) - will fall through to CLI
    if host is not None:
        url = f"http://{host}:{port}/tools/invoke"
        payload = json.dumps({"tool": "message", "args": args_obj, "sessionKey": "main"})

    if auth_token and host is not None:
        try:
            result = subprocess.run(
                [
                    "curl",
                    "-sS",
                    "-o",
                    "/dev/null",
                    "-w",
                    "%{http_code}",
                    "-H",
                    f"Authorization: Bearer {auth_token}",
                    "-H",
                    "Content-Type: application/json",
                    "-d",
                    payload,
                    url,
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.stdout.strip() == "200":
                return True
        except Exception:
            pass

    try:
        cmd = [oc_bin, "message", "send", "--message", message]
        if channel:
            cmd.extend(["--channel", channel])
        if target:
            cmd.extend(["--target", target])
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return result.returncode == 0
    except Exception:
        return False


def _notify_telegram(notif_config, message):
    tg = notif_config.get("telegram", {})
    if not isinstance(tg, dict):
        return False
    token_env = tg.get("bot_token_env", "TELEGRAM_BOT_TOKEN")
    token = _resolve_env(str(token_env))
    chat_id = str(tg.get("chat_id", "")).strip()
    if not token or not chat_id:
        return False
    result = subprocess.run(
        [
            "curl",
            "-sS",
            "-X",
            "POST",
            f"https://api.telegram.org/bot{token}/sendMessage",
            "-d",
            f"chat_id={chat_id}",
            "--data-urlencode",
            f"text={message}",
        ],
        capture_output=True,
        timeout=10,
    )
    return result.returncode == 0


def _notify_discord(notif_config, message):
    dc = notif_config.get("discord", {})
    if not isinstance(dc, dict):
        return False
    url_env = dc.get("webhook_url_env", "DISCORD_WEBHOOK_URL")
    url = _resolve_env(str(url_env))
    if not url:
        return False
    result = subprocess.run(
        [
            "curl",
            "-sS",
            "-X",
            "POST",
            "-H",
            "Content-Type: application/json",
            "-d",
            json.dumps({"content": message}),
            url,
        ],
        capture_output=True,
        timeout=10,
    )
    return result.returncode == 0


def _notify_slack(notif_config, message):
    sl = notif_config.get("slack", {})
    if not isinstance(sl, dict):
        return False
    url_env = sl.get("webhook_url_env", "SLACK_WEBHOOK_URL")
    url = _resolve_env(str(url_env))
    if not url:
        return False
    result = subprocess.run(
        [
            "curl",
            "-sS",
            "-X",
            "POST",
            "-H",
            "Content-Type: application/json",
            "-d",
            json.dumps({"text": message}),
            url,
        ],
        capture_output=True,
        timeout=10,
    )
    return result.returncode == 0


def _notify_webhook(notif_config, message):
    wh = notif_config.get("webhook", {})
    if not isinstance(wh, dict):
        return False
    url_env = wh.get("url_env", "RESTART_GUARD_WEBHOOK_URL")
    url = _resolve_env(str(url_env))
    if not url:
        return False
    method = str(wh.get("method", "POST")).upper()
    headers = wh.get("headers", {"Content-Type": "application/json"})
    if not isinstance(headers, dict):
        headers = {"Content-Type": "application/json"}
    body_template = str(wh.get("body_template", '{"text": "{{message}}"}'))
    # Security: use proper JSON encoding instead of string replacement to prevent injection
    body = _render_webhook_body(body_template, message)
    if body is None:
        return False

    cmd = ["curl", "-sS", "-X", method]
    for k, v in headers.items():
        cmd.extend(["-H", f"{k}: {v}"])
    cmd.extend(["-d", body, url])
    result = subprocess.run(cmd, capture_output=True, timeout=10)
    return result.returncode == 0


def _render_webhook_body(template, message):
    """
    Safely render webhook body template with message substitution.
    Uses JSON-aware encoding to prevent injection attacks.
    Returns None if template is invalid.
    """
    try:
        # Validate that the template is valid JSON
        parsed = json.loads(template)
        # Recursively substitute {{message}} placeholders with proper JSON encoding
        substituted = _substitute_message_placeholder(parsed, message)
        return json.dumps(substituted, ensure_ascii=False)
    except (json.JSONDecodeError, ValueError):
        # Template is not valid JSON, fall back to safe string replacement.
        # This is intentional: webhook endpoints may accept plain text, form-encoded,
        # or other non-JSON bodies (configured via Content-Type header).
        # Only allow simple string templates with exactly one placeholder.
        if template.count("{{message}}") != 1:
            return None
        # Encode message as JSON string to safely escape all special characters
        encoded = json.dumps(message, ensure_ascii=False)
        # Remove surrounding quotes since we're inserting into a string context
        if encoded.startswith('"') and encoded.endswith('"'):
            encoded = encoded[1:-1]
        return template.replace("{{message}}", encoded)


def _substitute_message_placeholder(obj, message):
    """Recursively substitute {{message}} placeholders in JSON structure."""
    if isinstance(obj, str):
        if "{{message}}" in obj:
            # If the entire string is the placeholder, use the message as-is
            if obj == "{{message}}":
                return message
            # Otherwise, do string replacement with JSON-encoded message
            encoded = json.dumps(message, ensure_ascii=False)
            if encoded.startswith('"') and encoded.endswith('"'):
                encoded = encoded[1:-1]
            return obj.replace("{{message}}", encoded)
        return obj
    if isinstance(obj, dict):
        return {k: _substitute_message_placeholder(v, message) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_substitute_message_placeholder(item, message) for item in obj]
    return obj
