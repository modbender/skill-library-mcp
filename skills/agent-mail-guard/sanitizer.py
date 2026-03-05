#!/usr/bin/env python3
"""
Email Sanitization Middleware for OpenClaw AI Agent.

Pure Python (stdlib only) — strips HTML, invisible unicode, injection patterns,
markdown image exfiltration vectors, and base64 blobs from email content before
it reaches the LLM context.

Usage:
    # As CLI — pipe JSON email(s) via stdin
    echo '{"sender":"a@b.com","subject":"Hi","body":"Hello"}' | python3 sanitizer.py

    # As module
    from sanitizer import sanitize_email
    result = sanitize_email({"sender": "a@b.com", "subject": "Hi", "body": "Hello"})
"""

import json
import sys
from typing import Any

# Import all sanitization primitives from shared core
from sanitize_core import (
    MAX_BODY_LENGTH,
    classify_sender,
    detect_cross_field_injection,
    normalize_unicode,
    remove_invisible_unicode,
    strip_invisible_unicode,
    sanitize_text,
    strip_base64_blobs,
    strip_html,
    strip_markdown_images,
)

# Re-export for backward compatibility (tests import from sanitizer)
__all__ = [
    "sanitize_email",
    "sanitize_emails",
    "sanitize_text",
    "classify_sender",
    "strip_html",
    "remove_invisible_unicode",
    "normalize_unicode",
    "strip_base64_blobs",
    "strip_markdown_images",
]


# ---------------------------------------------------------------------------
# Main sanitize_email function
# ---------------------------------------------------------------------------

def sanitize_email(email_data: dict[str, Any]) -> dict[str, Any]:
    """
    Sanitize a single email dict.

    Expected input keys: sender, subject, body, date (all optional strings).
    Returns structured output dict.
    """
    sender_raw = str(email_data.get("sender", ""))
    subject_raw = str(email_data.get("subject", ""))
    date_raw = str(email_data.get("date", ""))
    body_raw = str(email_data.get("body", ""))

    # Sanitize subject (full pipeline, capped at 500 chars)
    subject_clean, subject_flags, _ = sanitize_text(subject_raw, max_len=500)

    # Sanitize date (strip HTML for consistency)
    date_clean = strip_html(date_raw)

    # Sanitize sender (light)
    sender_clean = strip_html(sender_raw)
    sender_clean = remove_invisible_unicode(sender_clean)
    sender_clean = normalize_unicode(sender_clean)

    # Sanitize body (full pipeline)
    body_clean, body_flags, original_length = sanitize_text(body_raw)

    # Cross-field injection detection
    cross_flags = detect_cross_field_injection([subject_clean, body_clean])

    # Merge flags (deduplicate, preserving order)
    all_flags = list(dict.fromkeys(subject_flags + body_flags + cross_flags))

    # Classify sender
    sender_tier = classify_sender(sender_clean)
    summary_level = "full" if sender_tier == "known" else "minimal"

    # For unknown senders, provide a 3-line triage summary
    # Line 1: sender email + name if available
    # Line 2: subject + first sentence of body
    # Line 3: flag count + action hint
    if summary_level == "minimal":
        first_sentence = ""
        if body_clean:
            # Grab first sentence (up to period, question mark, or 150 chars)
            for i, ch in enumerate(body_clean[:150]):
                if ch in ".?!" and i > 10:
                    first_sentence = body_clean[: i + 1].replace("\n", " ").strip()
                    break
            if not first_sentence:
                first_sentence = body_clean[:150].replace("\n", " ").strip()
                if len(body_clean) > 150:
                    first_sentence += "..."

        flag_count = len(all_flags)
        if flag_count > 0:
            action_hint = f"{flag_count} flag(s) detected, review with caution"
        else:
            action_hint = "0 flags, may be legit"

        body_output = (
            f"From: {sender_clean}\n"
            f"Re: \"{subject_clean}\" — {first_sentence}\n"
            f"{action_hint}"
        )
    else:
        body_output = body_clean

    return {
        "sender": sender_clean,
        "subject": subject_clean,
        "date": date_clean,
        "body_clean": body_output,
        "body_length_original": original_length,
        "truncated": original_length > MAX_BODY_LENGTH,
        "suspicious": len(all_flags) > 0,
        "flags": all_flags,
        "sender_tier": sender_tier,
        "summary_level": summary_level,
    }


def sanitize_emails(emails: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sanitize a list of email dicts."""
    return [sanitize_email(e) for e in emails]


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

def main():
    """Read JSON from stdin, sanitize, print JSON to stdout."""
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid JSON input"}), file=sys.stderr)
        sys.exit(1)

    if isinstance(data, list):
        result = sanitize_emails(data)
    elif isinstance(data, dict):
        result = sanitize_email(data)
    else:
        print(json.dumps({"error": "Expected JSON object or array"}), file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
