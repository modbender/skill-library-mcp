#!/usr/bin/env python3
"""
scrask_bot.py
Scrask Bot — Screenshot to Task/Calendar Parser

Parses screenshots sent via Telegram using Claude or Gemini vision (user's choice),
then creates items in Google Calendar or Google Tasks.

Usage:
  python scrask_bot.py --image-path <path> [--provider claude|gemini] [--timezone <tz>]
  python scrask_bot.py --image-base64 <base64> [--provider claude|gemini]

Env vars:
  ANTHROPIC_API_KEY   — required if provider is 'claude'
  GEMINI_API_KEY      — required if provider is 'gemini'
  GOOGLE_CREDENTIALS  — path to Google service account JSON
  VISION_PROVIDER     — 'claude' or 'gemini' (overridden by --provider flag)

Requirements:
  pip install -r requirements.txt
"""

import argparse
import base64
import json
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# ── Google imports ─────────────────────────────────────────────────────────────
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

# ── Anthropic (Claude) ─────────────────────────────────────────────────────────
try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False

# ── Google Generative AI (Gemini) ──────────────────────────────────────────────
try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


# ─── Constants ─────────────────────────────────────────────────────────────────

MIME_TYPES = {
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png":  "image/png",
    ".gif":  "image/gif",
    ".webp": "image/webp",
}

CONFIDENCE_THRESHOLD  = 0.75
DEFAULT_EVENT_DURATION = 60   # minutes
DEFAULT_REMINDER_LEAD  = 30   # minutes

GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/tasks",
]

# Model names
CLAUDE_MODEL = "claude-opus-4-6"
GEMINI_MODEL = "gemini-2.0-flash"


# ─── Shared prompt ─────────────────────────────────────────────────────────────
# Both providers get the same instruction — only the API call differs.

SYSTEM_PROMPT = (
    "You are a structured data extraction assistant. "
    "Your only job is to analyze screenshots and return valid JSON — nothing else. "
    "No preamble, no explanation, no markdown fences. Only raw JSON."
)

USER_PROMPT_TEMPLATE = """Analyze this screenshot carefully. It may be a WhatsApp forward,
email screenshot, social media post, or chat message received via Telegram.

Extract ALL actionable information and return a single JSON object:

{{
  "items": [
    {{
      "type": "event" | "reminder" | "task",
      "confidence": 0.0-1.0,
      "title": "concise title (max 60 chars)",
      "date": "YYYY-MM-DD or null",
      "time": "HH:MM (24h) or null",
      "end_time": "HH:MM (24h) or null",
      "timezone_hint": "detected timezone string or null",
      "location": "physical address or venue name or null",
      "online_link": "Zoom/Meet/Teams URL or null",
      "recurrence": "none | daily | weekly | monthly | yearly",
      "recurrence_day": "e.g. Tuesday or null",
      "description": "1-2 sentence context summary or null",
      "priority": "high | medium | low",
      "source_type": "whatsapp | email | social_media | chat | flyer | other",
      "language": "ISO 639-1 code of the screenshot text",
      "already_in_calendar_hint": true | false
    }}
  ],
  "screenshot_summary": "one sentence describing what this screenshot shows",
  "no_actionable_content": true | false,
  "parse_notes": "edge cases, ambiguities, or things to flag to the user"
}}

Classification rules:
- "event"    → specific date+time OR a venue/link; social or external gathering
- "reminder" → deadline/due date; personal action item; no specific gathering
- "task"     → no date at all; pure to-do or action item

Confidence scoring:
- 0.9–1.0  All key fields present, no ambiguity
- 0.75–0.9 Most fields present, minor inference needed
- 0.5–0.75 Date or type is uncertain
- < 0.5    Very little usable info

Current date: {today}
User timezone: {timezone}

Return only JSON. No markdown. No explanation."""


# ─── Provider: Claude ──────────────────────────────────────────────────────────

def parse_with_claude(
    image_base64: str,
    media_type: str,
    api_key: str,
    timezone: str = "UTC",
) -> dict:
    """Call Claude vision API and return structured parsed data."""
    if not CLAUDE_AVAILABLE:
        raise RuntimeError("anthropic package not installed. Run: pip install anthropic")

    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": image_base64,
                    },
                },
                {
                    "type": "text",
                    "text": USER_PROMPT_TEMPLATE.format(
                        today=date.today().isoformat(),
                        timezone=timezone,
                    ),
                },
            ],
        }],
    )

    raw = message.content[0].text if message.content else ""
    return _clean_and_parse_json(raw)


# ─── Provider: Gemini ──────────────────────────────────────────────────────────

def parse_with_gemini(
    image_base64: str,
    media_type: str,
    api_key: str,
    timezone: str = "UTC",
) -> dict:
    """Call Gemini vision API and return structured parsed data."""
    if not GEMINI_AVAILABLE:
        raise RuntimeError(
            "google-generativeai package not installed. "
            "Run: pip install google-generativeai"
        )

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=SYSTEM_PROMPT,
    )

    # Gemini takes image as inline bytes
    image_bytes = base64.standard_b64decode(image_base64)
    image_part = {"mime_type": media_type, "data": image_bytes}

    prompt = USER_PROMPT_TEMPLATE.format(
        today=date.today().isoformat(),
        timezone=timezone,
    )

    # Relax safety settings so event descriptions don't get blocked
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT:        HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH:       HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }

    response = model.generate_content(
        [image_part, prompt],
        safety_settings=safety_settings,
        generation_config=genai.GenerationConfig(
            max_output_tokens=1500,
            temperature=0.1,   # low temp for consistent structured output
        ),
    )

    raw = response.text if response.text else ""
    return _clean_and_parse_json(raw)


# ─── Provider router ───────────────────────────────────────────────────────────

FALLBACK_THRESHOLD = 0.60   # If Gemini returns any item below this, retry with Claude
FALLBACK_IMPROVEMENT_MIN = 0.05  # Only switch if Claude meaningfully improves confidence


def parse_screenshot(
    image_base64: str,
    media_type: str,
    provider: str,
    api_key: str,
    timezone: str = "UTC",
    claude_api_key: str | None = None,
    gemini_api_key: str | None = None,
) -> dict:
    """
    Route to the correct vision provider based on user preference.

    If provider is 'auto' (default):
      1. Try Gemini first (fast, cheap)
      2. If any item confidence < FALLBACK_THRESHOLD, retry with Claude
      3. Return whichever result has higher average confidence
      4. Attach '_provider_used' and '_fallback_triggered' metadata to result

    If provider is 'claude' or 'gemini': use that provider directly.
    """
    provider = provider.lower().strip()

    if provider == "claude":
        result = parse_with_claude(image_base64, media_type, api_key or claude_api_key, timezone)
        result["_provider_used"]       = "claude"
        result["_fallback_triggered"]  = False
        return result

    elif provider == "gemini":
        result = parse_with_gemini(image_base64, media_type, api_key or gemini_api_key, timezone)
        result["_provider_used"]       = "gemini"
        result["_fallback_triggered"]  = False
        return result

    elif provider == "auto":
        return _parse_with_auto_fallback(
            image_base64, media_type, timezone,
            gemini_api_key=gemini_api_key or api_key,
            claude_api_key=claude_api_key,
        )

    else:
        raise ValueError(f"Unknown provider '{provider}'. Choose 'auto', 'claude', or 'gemini'.")


def _parse_with_auto_fallback(
    image_base64: str,
    media_type: str,
    timezone: str,
    gemini_api_key: str,
    claude_api_key: str | None,
) -> dict:
    """
    Auto mode:
    - Run Gemini first
    - If any item is below FALLBACK_THRESHOLD, run Claude too
    - Return whichever parse has better average confidence
    """
    # Step 1: Gemini
    gemini_result = parse_with_gemini(image_base64, media_type, gemini_api_key, timezone)
    gemini_items  = gemini_result.get("items", [])
    gemini_min    = min((i.get("confidence", 0) for i in gemini_items), default=1.0)
    gemini_avg    = _avg_confidence(gemini_items)

    # Step 2: Decide if fallback is worth it
    fallback_triggered = gemini_min < FALLBACK_THRESHOLD and bool(claude_api_key)

    if not fallback_triggered:
        gemini_result["_provider_used"]      = "gemini"
        gemini_result["_fallback_triggered"] = False
        gemini_result["_gemini_avg_conf"]    = round(gemini_avg, 3)
        return gemini_result

    # Step 3: Retry with Claude
    try:
        claude_result = parse_with_claude(image_base64, media_type, claude_api_key, timezone)
        claude_avg    = _avg_confidence(claude_result.get("items", []))
    except Exception as e:
        # Claude failed — return Gemini result with a note
        gemini_result["_provider_used"]      = "gemini"
        gemini_result["_fallback_triggered"] = True
        gemini_result["_fallback_error"]     = f"Claude fallback failed: {e}"
        gemini_result["_gemini_avg_conf"]    = round(gemini_avg, 3)
        return gemini_result

    # Step 4: Pick the better result
    improvement = claude_avg - gemini_avg

    if improvement >= FALLBACK_IMPROVEMENT_MIN:
        claude_result["_provider_used"]      = "claude"
        claude_result["_fallback_triggered"] = True
        claude_result["_gemini_avg_conf"]    = round(gemini_avg, 3)
        claude_result["_claude_avg_conf"]    = round(claude_avg, 3)
        claude_result["_confidence_gain"]    = round(improvement, 3)
        return claude_result
    else:
        # Claude didn't improve enough — stick with Gemini
        gemini_result["_provider_used"]      = "gemini"
        gemini_result["_fallback_triggered"] = True
        gemini_result["_fallback_outcome"]   = "gemini_retained"
        gemini_result["_gemini_avg_conf"]    = round(gemini_avg, 3)
        gemini_result["_claude_avg_conf"]    = round(claude_avg, 3)
        return gemini_result


def _avg_confidence(items: list[dict]) -> float:
    if not items:
        return 0.0
    return sum(i.get("confidence", 0) for i in items) / len(items)


def _clean_and_parse_json(raw: str) -> dict:
    """Strip accidental markdown fences and parse JSON."""
    cleaned = (
        raw.removeprefix("```json").removeprefix("```")
           .removesuffix("```").strip()
    )
    return json.loads(cleaned)


# ─── Google helpers ────────────────────────────────────────────────────────────

def get_google_services(credentials_path: str):
    if not GOOGLE_AVAILABLE:
        raise RuntimeError(
            "Google client libraries not installed. "
            "Run: pip install google-auth google-auth-httplib2 google-api-python-client"
        )
    creds = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=GOOGLE_SCOPES
    )
    calendar = build("calendar", "v3", credentials=creds)
    tasks    = build("tasks",    "v1", credentials=creds)
    return calendar, tasks


def build_datetime(date_str: str, time_str: str | None, tz: str) -> str:
    try:
        tzinfo = ZoneInfo(tz)
    except ZoneInfoNotFoundError:
        tzinfo = ZoneInfo("UTC")

    if time_str:
        dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        return dt.replace(tzinfo=tzinfo).isoformat()
    return date_str


def create_calendar_event(service, item: dict, timezone: str, reminder_minutes: int) -> str:
    tz_hint  = item.get("timezone_hint") or timezone
    start_dt = build_datetime(item["date"], item.get("time"), tz_hint)

    if item.get("end_time"):
        end_dt = build_datetime(item["date"], item["end_time"], tz_hint)
    elif item.get("time"):
        start = datetime.fromisoformat(start_dt)
        end_dt = (start + timedelta(minutes=DEFAULT_EVENT_DURATION)).isoformat()
    else:
        end_dt = start_dt

    body = {
        "summary":     item["title"],
        "description": (item.get("description") or "") + "\n\n[Added by Scrask]",
        "start": {"dateTime": start_dt, "timeZone": tz_hint}
                 if item.get("time") else {"date": start_dt},
        "end":   {"dateTime": end_dt,   "timeZone": tz_hint}
                 if item.get("time") else {"date": end_dt},
        "reminders": {
            "useDefault": False,
            "overrides":  [{"method": "popup", "minutes": reminder_minutes}],
        },
    }

    if item.get("location"):
        body["location"] = item["location"]

    if item.get("online_link"):
        body["description"] += f"\n\nJoin: {item['online_link']}"
        body["location"] = item["online_link"]

    if item.get("recurrence") and item["recurrence"] != "none":
        freq_map = {
            "daily": "DAILY", "weekly": "WEEKLY",
            "monthly": "MONTHLY", "yearly": "YEARLY",
        }
        rrule = f"RRULE:FREQ={freq_map[item['recurrence']]}"
        if item.get("recurrence_day") and item["recurrence"] == "weekly":
            day_map = {
                "monday": "MO", "tuesday": "TU", "wednesday": "WE",
                "thursday": "TH", "friday": "FR", "saturday": "SA", "sunday": "SU",
            }
            day_code = day_map.get(item["recurrence_day"].lower())
            if day_code:
                rrule += f";BYDAY={day_code}"
        body["recurrence"] = [rrule]

    result = service.events().insert(calendarId="primary", body=body).execute()
    return result.get("htmlLink", "")


def create_task(service, item: dict) -> str:
    body = {
        "title": item["title"],
        "notes": (item.get("description") or "") + "\n[Added by Scrask]",
    }
    if item.get("date"):
        body["due"] = f"{item['date']}T00:00:00.000Z"

    result = service.tasks().insert(tasklist="@default", body=body).execute()
    return result.get("id", "")


# ─── Decision engine ───────────────────────────────────────────────────────────

def process_item(item: dict) -> dict:
    confidence    = item.get("confidence", 0.0)
    item_type     = item.get("type", "task")
    destination   = "google_calendar" if item_type == "event" else "google_tasks"

    return {
        "item":                 item,
        "confidence":           confidence,
        "needs_confirmation":   confidence < CONFIDENCE_THRESHOLD,
        "destination":          destination,
        "action_taken":         None,
        "link":                 None,
        "error":                None,
    }


def execute_item(result: dict, args: argparse.Namespace) -> dict:
    item             = result["item"]
    credentials_path = os.environ.get("GOOGLE_CREDENTIALS", args.google_credentials)

    try:
        cal_service, tasks_service = get_google_services(credentials_path)
    except Exception as e:
        result["error"] = f"Google auth failed: {e}"
        return result

    try:
        if result["destination"] == "google_calendar":
            link = create_calendar_event(
                cal_service, item, args.timezone, DEFAULT_REMINDER_LEAD
            )
            result["action_taken"] = "created_calendar_event"
            result["link"]         = link
        else:
            task_id = create_task(tasks_service, item)
            result["action_taken"] = "created_google_task"
            result["link"]         = f"https://tasks.google.com/tasks/search?q={task_id}"
    except Exception as e:
        result["error"] = str(e)

    return result


# ─── Telegram reply formatter ──────────────────────────────────────────────────

def format_telegram_reply(results: list[dict], parse_data: dict, provider: str) -> str:
    lines = []
    silent_items  = [r for r in results if not r["needs_confirmation"]]
    confirm_items = [r for r in results if r["needs_confirmation"]]

    for r in silent_items:
        item = r["item"]
        if r.get("error"):
            lines.append(f"⚠️ Failed to save **{item['title']}**: {r['error']}")
            continue
        if r["destination"] == "google_calendar":
            when = f"{item.get('date', '')} at {item['time']}" if item.get("time") else item.get("date", "")
            lines.append(f"📅 Added to Calendar: **{item['title']}** — {when}")
        else:
            due  = f" (due {item['date']})" if item.get("date") else ""
            icon = "🔔" if item.get("date") else "✅"
            lines.append(f"{icon} Added to Tasks: **{item['title']}**{due}")

    for r in confirm_items:
        item = r["item"]
        lines.append(f"\n🤔 Not sure about this one (confidence: {int(r['confidence']*100)}%)")
        if r["destination"] == "google_calendar":
            lines.append(f"📅 **Event detected**")
            lines.append(f"  Title: {item['title']}")
            lines.append(f"  Date:  {item.get('date') or '?'}")
            lines.append(f"  Time:  {item.get('time') or '?'}")
            if item.get("location"):
                lines.append(f"  Where: {item['location']}")
            if item.get("online_link"):
                lines.append(f"  Link:  {item['online_link']}")
        else:
            icon  = "🔔" if item.get("date") else "✅"
            label = "Reminder" if item.get("date") else "Task"
            lines.append(f"{icon} **{label} detected**")
            lines.append(f"  Title: {item['title']}")
            if item.get("date"):
                lines.append(f"  Due:   {item['date']}")
        if item.get("description"):
            lines.append(f"  Note:  {item['description']}")
        lines.append("\nSave it? Reply **yes**, **edit**, or **skip**.")

    if parse_data.get("parse_notes"):
        lines.append(f"\n_ℹ️ {parse_data['parse_notes']}_")

    # Subtle provider attribution (useful for debugging)
    lines.append(f"\n_Parsed by Scrask using {provider.capitalize()}_")

    return "\n".join(lines).strip()


# ─── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scrask Bot — parse screenshots and save to Google Calendar / Tasks."
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--image-path",   help="Path to the screenshot file")
    group.add_argument("--image-base64", help="Base64-encoded image data")

    parser.add_argument(
        "--provider",
        choices=["auto", "claude", "gemini"],
        default=os.environ.get("VISION_PROVIDER", "auto"),
        help=(
            "'auto' (default) = Gemini first, Claude fallback if confidence < 0.6. "
            "'claude' or 'gemini' = use that provider directly."
        ),
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help=(
            "API key for the chosen provider. "
            "Defaults to ANTHROPIC_API_KEY (claude) or GEMINI_API_KEY (gemini) env vars."
        ),
    )
    parser.add_argument(
        "--timezone",
        default=os.environ.get("USER_TIMEZONE", "UTC"),
        help="IANA timezone (e.g. Asia/Kolkata)",
    )
    parser.add_argument(
        "--google-credentials",
        default=os.environ.get("GOOGLE_CREDENTIALS", ""),
        help="Path to Google service account JSON",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and classify only — do not call Google APIs",
    )
    parser.add_argument(
        "--media-type",
        default=None,
        help="Override media type (auto-detected from file extension if omitted)",
    )

    args = parser.parse_args()

    # Resolve API keys from env
    claude_api_key = args.api_key or os.environ.get("ANTHROPIC_API_KEY")
    gemini_api_key = args.api_key or os.environ.get("GEMINI_API_KEY")

    # Validate: ensure required keys are present for chosen mode
    if args.provider == "claude" and not claude_api_key:
        exit_error("Missing ANTHROPIC_API_KEY for Claude provider.")
    if args.provider == "gemini" and not gemini_api_key:
        exit_error("Missing GEMINI_API_KEY for Gemini provider.")
    if args.provider == "auto" and not gemini_api_key:
        exit_error("Auto mode requires GEMINI_API_KEY at minimum. ANTHROPIC_API_KEY enables Claude fallback.")
    if args.provider == "auto" and not claude_api_key:
        # Warn but continue — fallback just won't trigger
        import sys
        print(
            "⚠️  ANTHROPIC_API_KEY not set. Auto mode will use Gemini only (no Claude fallback).",
            file=sys.stderr
        )

    # Load image
    try:
        if args.image_path:
            p = Path(args.image_path)
            if not p.exists():
                exit_error(f"Image not found: {args.image_path}")
            media_type   = args.media_type or MIME_TYPES.get(p.suffix.lower(), "image/png")
            image_base64 = base64.standard_b64encode(p.read_bytes()).decode()
        else:
            image_base64 = args.image_base64
            media_type   = args.media_type or "image/png"
    except Exception as e:
        exit_error(f"Failed to load image: {e}")

    # Parse with chosen provider
    try:
        parse_data = parse_screenshot(
            image_base64, media_type, args.provider, args.api_key,
            args.timezone,
            claude_api_key=claude_api_key,
            gemini_api_key=gemini_api_key,
        )
    except json.JSONDecodeError as e:
        exit_error(f"Provider returned invalid JSON: {e}")
    except Exception as e:
        exit_error(f"Error during parsing: {e}")

    provider_used = parse_data.get("_provider_used", args.provider)

    # No actionable content
    if parse_data.get("no_actionable_content") or not parse_data.get("items"):
        print(json.dumps({
            "success": False,
            "no_actionable_content": True,
            "provider": provider_used,
            "fallback_triggered": parse_data.get("_fallback_triggered", False),
            "screenshot_summary": parse_data.get("screenshot_summary", ""),
            "telegram_reply": (
                "🤷 I couldn't find any event, reminder, or task info in that screenshot.\n"
                "Could you describe what you'd like to add?"
            ),
        }, indent=2, ensure_ascii=False))
        return

    # Classify
    results = [process_item(item) for item in parse_data["items"]]

    # Execute high-confidence items
    if not args.dry_run:
        for r in results:
            if not r["needs_confirmation"]:
                execute_item(r, args)

    # Build output
    telegram_reply = format_telegram_reply(results, parse_data, provider_used)

    print(json.dumps({
        "success":                    True,
        "provider":                   provider_used,
        "fallback_triggered":         parse_data.get("_fallback_triggered", False),
        "gemini_avg_confidence":      parse_data.get("_gemini_avg_conf"),
        "claude_avg_confidence":      parse_data.get("_claude_avg_conf"),
        "confidence_gain":            parse_data.get("_confidence_gain"),
        "screenshot_summary":         parse_data.get("screenshot_summary", ""),
        "items_found":                len(results),
        "items_saved":                sum(1 for r in results if r.get("action_taken")),
        "items_pending_confirmation": sum(1 for r in results if r["needs_confirmation"]),
        "results": [
            {
                "title":              r["item"]["title"],
                "type":               r["item"]["type"],
                "confidence":         r["confidence"],
                "destination":        r["destination"],
                "needs_confirmation": r["needs_confirmation"],
                "action_taken":       r.get("action_taken"),
                "link":               r.get("link"),
                "error":              r.get("error"),
            }
            for r in results
        ],
        "telegram_reply": telegram_reply,
        "parse_notes":    parse_data.get("parse_notes"),
    }, indent=2, ensure_ascii=False))


def exit_error(message: str) -> None:
    sys.stderr.write(
        json.dumps({
            "error":          True,
            "message":        message,
            "success":        False,
            "telegram_reply": f"⚠️ Something went wrong: {message}",
        }) + "\n"
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
