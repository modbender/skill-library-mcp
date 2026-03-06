#!/usr/bin/env python3
"""
Shared utilities for youtube-archiver.

Python compatibility: 3.7+
Dependencies: stdlib only
"""

from __future__ import annotations

import datetime
import errno
import html
import json
import os
import random
import re
import shutil
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


DEFAULT_PLAYLISTS = [
    {"id": "LL", "name": "Liked Videos"},
    {"id": "WL", "name": "Watch Later"},
]

DEFAULT_TAGS = [
    "tutorial",
    "programming",
    "devops",
    "ai",
    "productivity",
    "design",
    "hardware",
    "open-source",
    "career",
    "self-hosted",
    "gaming",
    "science",
    "music",
    "finance",
    "health",
]

DEFAULT_CONFIG = {
    "playlists": DEFAULT_PLAYLISTS,
    "browser": "chrome",
    "cookies_file": "",
    "summary": {
        "provider": "openai",
        "model": "gpt-5-mini",
        "api_key_env": "OPENAI_API_KEY",
        "base_url": "",
        "api_mode": "auto",
        "prompt_file": "",
    },
    "tagging": {
        "provider": "gemini",
        "model": "gemini-3-flash",
        "api_key_env": "GEMINI_API_KEY",
        "base_url": "",
        "api_mode": "auto",
    },
    "tags": DEFAULT_TAGS,
}

DEFAULT_SUMMARY_PROMPT = """Summarize this YouTube transcript into a compact reference note.

Use this exact structure:

## Key Takeaways
- 3 to 5 bullets with the most important points.

## Details
- Explain tools, commands, tactics, and notable examples.
- Keep it factual and specific.
- Distinguish objective facts from opinions when possible.

## Notable Quotes
- 1 to 3 direct quotes only if they are meaningful.
- If no quote stands out, write: None.

Transcript:
{transcript}
"""

ALLOWED_PROVIDERS = {
    "openai",
    "gemini",
    "anthropic",
    "openrouter",
    "ollama",
    "none",
}

LOCKFILE_NAME = ".yt-archiver.lock"
SYNC_STATE_NAME = ".sync-state.json"

INLINE_TS_RE = re.compile(r"<\d{2}:\d{2}:\d{2}\.\d{3}>")
TAG_RE = re.compile(r"<[^>]+>")
PUNCT_RE = re.compile(r"[^\w\s]", re.UNICODE)


class ConfigError(Exception):
    pass


class LockError(Exception):
    pass


def _deep_copy(obj):
    return json.loads(json.dumps(obj))


def utc_now_iso():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def today_iso():
    return datetime.date.today().isoformat()


def ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)


def command_exists(cmd):
    return shutil.which(cmd) is not None


# ---------------------------------------------------------------------------
# Config and init
# ---------------------------------------------------------------------------


def _merge_defaults(defaults, value):
    if isinstance(defaults, dict):
        merged = {}
        value = value if isinstance(value, dict) else {}
        for key in defaults:
            merged[key] = _merge_defaults(defaults[key], value.get(key))
        for key in value:
            if key not in merged:
                merged[key] = value[key]
        return merged
    if isinstance(defaults, list):
        if isinstance(value, list):
            return value
        return _deep_copy(defaults)
    if value is None:
        return defaults
    return value


def load_config(config_path, create_if_missing=False):
    config_path = Path(config_path)
    if not config_path.exists():
        config = _deep_copy(DEFAULT_CONFIG)
        if create_if_missing:
            ensure_dir(config_path.parent)
            config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
        return config

    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ConfigError("Invalid JSON in config: {0}".format(exc))

    return _merge_defaults(DEFAULT_CONFIG, data)


def _validate_provider_block(name, block, strict=False):
    errors = []
    warnings = []
    block_keys = {"provider", "model", "api_key_env", "base_url", "api_mode", "prompt_file"}

    if not isinstance(block, dict):
        errors.append("{0} must be an object".format(name))
        return errors, warnings

    provider = str(block.get("provider", "none")).lower().strip()
    if provider not in ALLOWED_PROVIDERS:
        errors.append("{0}.provider must be one of: {1}".format(name, ", ".join(sorted(ALLOWED_PROVIDERS))))

    model = str(block.get("model", "")).strip()
    if provider != "none" and not model:
        errors.append("{0}.model is required when provider != none".format(name))

    api_mode = str(block.get("api_mode", "auto")).lower().strip()
    if provider == "ollama" and api_mode not in ("auto", "native", "openai"):
        errors.append("{0}.api_mode for ollama must be auto|native|openai".format(name))

    if strict:
        for key in block.keys():
            if key not in block_keys:
                errors.append("Unknown key in {0}: {1}".format(name, key))
    else:
        for key in block.keys():
            if key not in block_keys:
                warnings.append("Unknown key in {0}: {1}".format(name, key))

    return errors, warnings


def validate_config(config, strict=False):
    errors = []
    warnings = []

    allowed_top = {"playlists", "browser", "cookies_file", "summary", "tagging", "tags"}
    if not isinstance(config, dict):
        raise ConfigError("Config must be a JSON object")

    playlists = config.get("playlists", [])
    if not isinstance(playlists, list):
        errors.append("playlists must be a list")
    else:
        for idx, item in enumerate(playlists):
            if not isinstance(item, dict):
                errors.append("playlists[{0}] must be an object".format(idx))
                continue
            pid = str(item.get("id", "")).strip()
            name = str(item.get("name", "")).strip()
            if not pid:
                errors.append("playlists[{0}].id is required".format(idx))
            if not name:
                errors.append("playlists[{0}].name is required".format(idx))

    browser = str(config.get("browser", "")).strip()
    if browser and browser.lower() not in (
        "chrome",
        "firefox",
        "edge",
        "safari",
        "brave",
        "chromium",
        "opera",
        "vivaldi",
    ):
        warnings.append("browser '{0}' may not be supported by yt-dlp".format(browser))

    tags = config.get("tags", [])
    if not isinstance(tags, list):
        errors.append("tags must be a list")
    else:
        for idx, tag in enumerate(tags):
            if not isinstance(tag, str) or not tag.strip():
                errors.append("tags[{0}] must be a non-empty string".format(idx))

    sub_errors, sub_warnings = _validate_provider_block("summary", config.get("summary", {}), strict=strict)
    errors.extend(sub_errors)
    warnings.extend(sub_warnings)

    tag_errors, tag_warnings = _validate_provider_block("tagging", config.get("tagging", {}), strict=strict)
    errors.extend(tag_errors)
    warnings.extend(tag_warnings)

    if strict:
        for key in config.keys():
            if key not in allowed_top:
                errors.append("Unknown top-level key: {0}".format(key))
    else:
        for key in config.keys():
            if key not in allowed_top:
                warnings.append("Unknown top-level key: {0}".format(key))

    if errors:
        raise ConfigError("; ".join(errors))

    return warnings


def load_and_validate_config(config_path, strict=False, create_if_missing=False):
    config = load_config(config_path, create_if_missing=create_if_missing)
    warnings = validate_config(config, strict=strict)
    return config, warnings


def save_config(config_path, config):
    config_path = Path(config_path)
    ensure_dir(config_path.parent)
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")


def _build_output_readme(import_script_path, enrich_script_path, output_dir):
    return """# YouTube Archive

This folder is managed by the `youtube-archiver` OpenClaw skill. It contains archived YouTube videos as markdown notes with summaries, transcripts, and tags.

## Quick Reference

The easiest way to use this is to ask your OpenClaw agent:

- \"Sync my YouTube bookmarks\"
- \"Import my Watch Later playlist\"
- \"Enrich my YouTube notes\"
- \"Set up daily YouTube sync\"

### Manual commands (if needed)

```bash
# Import new videos (fast, metadata only)
python3 {import_script} --output {output_dir}

# Enrich with AI summaries + transcripts (slower, batched)
python3 {enrich_script} --output {output_dir} --limit 10

# Dry run (preview without writing)
python3 {import_script} --output {output_dir} --dry-run
```

## Configuration (`.config.json`)

All settings live in `.config.json` in this folder.

### `playlists`

```json
{{
  "playlists": [
    {{"id": "LL", "name": "Liked Videos"}},
    {{"id": "WL", "name": "Watch Later"}},
    {{"id": "PLxxxxxxxxxxxxxx", "name": "My Playlist"}}
  ]
}}
```

### `browser`

```json
{{
  "browser": "chrome"
}}
```

Options: `chrome`, `firefox`, `edge`, `safari`, `brave`, `chromium`, `opera`, `vivaldi`

### `summary`

```json
{{
  "summary": {{
    "provider": "openai",
    "model": "gpt-5-mini",
    "api_key_env": "OPENAI_API_KEY"
  }}
}}
```

Providers: `openai`, `gemini`, `anthropic`, `openrouter`, `ollama`, `none`

### `tagging`

```json
{{
  "tagging": {{
    "provider": "gemini",
    "model": "gemini-3-flash",
    "api_key_env": "GEMINI_API_KEY"
  }}
}}
```

### `tags`

```json
{{
  "tags": [
    "tutorial", "programming", "devops", "ai", "productivity",
    "design", "hardware", "open-source", "career", "self-hosted",
    "gaming", "science", "music", "finance", "health"
  ]
}}
```

### `cookies_file` (optional)

```json
{{
  "cookies_file": "/path/to/cookies.txt"
}}
```

Use this when browser cookie extraction fails.

## How It Works

1. Import pulls playlist metadata via `yt-dlp`
2. Each video becomes a markdown file in a playlist subfolder
3. Enrichment adds transcript, summary, and tags
4. Existing videos are skipped by `video_id`
5. `.sync-state.json` tracks the last run

## Troubleshooting

- Cookie auth fails: try another browser or set `cookies_file`
- Rate limiting: run enrichment with `--limit`
- Missing summaries: check API key env vars and model names
- Missing transcripts: some videos do not expose subtitles

## Automation

Ask your agent:

> Set up a daily YouTube sync at 11 AM — import new videos then enrich up to 10
""".format(
        import_script=str(import_script_path),
        enrich_script=str(enrich_script_path),
        output_dir=str(output_dir),
    )


def initialize_output(output_dir, config_path, import_script_path, enrich_script_path):
    output_dir = Path(output_dir)
    config_path = Path(config_path)
    ensure_dir(output_dir)

    if not config_path.exists():
        save_config(config_path, _deep_copy(DEFAULT_CONFIG))

    readme_path = output_dir / "README.md"
    readme_text = _build_output_readme(import_script_path, enrich_script_path, output_dir)
    readme_path.write_text(readme_text, encoding="utf-8")

    return {
        "config_path": str(config_path),
        "readme_path": str(readme_path),
    }


# ---------------------------------------------------------------------------
# Lock management
# ---------------------------------------------------------------------------


def _is_pid_running(pid):
    if not isinstance(pid, int) or pid <= 0:
        return False
    if os.name == "nt":
        # Windows: os.kill(pid, 0) actually terminates the process.
        # Use ctypes to call OpenProcess instead.
        try:
            import ctypes
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            handle = ctypes.windll.kernel32.OpenProcess(
                PROCESS_QUERY_LIMITED_INFORMATION, False, pid
            )
            if handle:
                ctypes.windll.kernel32.CloseHandle(handle)
                return True
            return False
        except Exception:
            return False
    try:
        os.kill(pid, 0)
        return True
    except OSError as exc:
        if exc.errno in (errno.ESRCH,):
            return False
        return True


def acquire_lock(output_dir, force=False):
    output_dir = Path(output_dir)
    ensure_dir(output_dir)
    lock_path = output_dir / LOCKFILE_NAME
    current_pid = os.getpid()

    if lock_path.exists():
        stale = True
        info = {}
        try:
            info = json.loads(lock_path.read_text(encoding="utf-8"))
            pid = int(info.get("pid", 0))
            stale = not _is_pid_running(pid)
        except Exception:
            stale = True

        if not stale and not force:
            raise LockError("Another youtube-archiver process is running (pid={0})".format(info.get("pid", "?")))

        if stale or force:
            try:
                lock_path.unlink()
            except Exception:
                pass

    payload = {
        "pid": current_pid,
        "created_at": utc_now_iso(),
    }
    lock_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return lock_path


def release_lock(lock_path):
    lock_path = Path(lock_path)
    if lock_path.exists():
        try:
            lock_path.unlink()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Frontmatter helpers and note IO
# ---------------------------------------------------------------------------


def yaml_escape(value):
    if value is None:
        return ""
    text = str(value)
    if text == "":
        return '""'
    if any(ch in text for ch in ':{}[]&*?|->!%@`#,\'"\n'):
        return '"{0}"'.format(text.replace("\\", "\\\\").replace('"', '\\"'))
    return text


def _serialize_yaml_value(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return json.dumps(value, ensure_ascii=False)
    return yaml_escape(value)


def dump_frontmatter(frontmatter):
    order = [
        "title",
        "channel",
        "url",
        "video_id",
        "published",
        "duration",
        "view_count",
        "source_playlist",
        "created",
        "enriched",
        "enriched_at",
        "enrichment_version",
        "tags",
        "transcript_status",
        "summary_status",
        "tags_status",
    ]
    lines = ["---"]
    seen = set()
    for key in order:
        if key in frontmatter:
            lines.append("{0}: {1}".format(key, _serialize_yaml_value(frontmatter.get(key))))
            seen.add(key)

    for key in sorted(frontmatter.keys()):
        if key in seen:
            continue
        lines.append("{0}: {1}".format(key, _serialize_yaml_value(frontmatter.get(key))))

    lines.append("---")
    return "\n".join(lines)


def _parse_scalar(value):
    value = value.strip()
    if value == "":
        return ""
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False

    if value.startswith("[") and value.endswith("]"):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            return value

    if value.startswith('"') and value.endswith('"') and len(value) >= 2:
        raw = value[1:-1]
        raw = raw.replace('\\"', '"').replace("\\\\", "\\")
        return raw

    if re.match(r"^-?\d+$", value):
        try:
            return int(value)
        except Exception:
            return value

    if re.match(r"^-?\d+\.\d+$", value):
        try:
            return float(value)
        except Exception:
            return value

    return value


def parse_frontmatter(markdown_text):
    text = markdown_text
    if not text.startswith("---\n") and text.strip() != "---":
        return {}, text

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text

    end_index = -1
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_index = idx
            break

    if end_index == -1:
        return {}, text

    fm_lines = lines[1:end_index]
    body_lines = lines[end_index + 1 :]

    fm = {}
    for line in fm_lines:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        fm[key] = _parse_scalar(value)

    body = "\n".join(body_lines).lstrip("\n")
    return fm, body


def _build_body(title, channel, duration, url, summary_text, transcript_text):
    lines = [
        "# {0}".format(title),
        "",
        "**Channel:** {0}  ".format(channel or "Unknown"),
        "**Duration:** {0}  ".format(duration or ""),
        "**URL:** {0}".format(url),
        "",
    ]

    if summary_text:
        lines.extend(["## Summary", "", summary_text.strip(), ""])

    if transcript_text:
        lines.extend(["## Transcript", "", "> [!note]- Full Transcript"])
        for row in transcript_text.splitlines():
            lines.append("> {0}".format(row))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_note(path, frontmatter, summary_text="", transcript_text=""):
    path = Path(path)
    ensure_dir(path.parent)

    title = str(frontmatter.get("title", "Untitled"))
    channel = str(frontmatter.get("channel", "Unknown"))
    duration = str(frontmatter.get("duration", ""))
    url = str(frontmatter.get("url", ""))

    content = dump_frontmatter(frontmatter)
    content += "\n\n"
    content += _build_body(title, channel, duration, url, summary_text, transcript_text)
    path.write_text(content, encoding="utf-8")


def read_note(path):
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    return {
        "frontmatter": fm,
        "body": body,
        "text": text,
    }


def sanitize_filename(title, max_len=120):
    safe = re.sub(r"[\\/:*?\"<>|]", "-", str(title or "Untitled"))
    safe = re.sub(r"\s+", " ", safe).strip()
    safe = safe.strip(".")
    if not safe:
        safe = "Untitled"
    if len(safe) > max_len:
        safe = safe[:max_len].rsplit(" ", 1)[0]
    return safe or "Untitled"


def note_filename(title, video_id):
    return "{0} [{1}].md".format(sanitize_filename(title), video_id)


def load_existing_video_ids(output_dir):
    output_dir = Path(output_dir)
    mapping = {}
    if not output_dir.exists():
        return mapping

    for path in output_dir.rglob("*.md"):
        if any(part.startswith(".") for part in path.parts):
            continue
        try:
            note = read_note(path)
        except Exception:
            continue
        video_id = str(note["frontmatter"].get("video_id", "")).strip()
        if video_id:
            mapping[video_id] = path
    return mapping


# ---------------------------------------------------------------------------
# Subprocess and retries
# ---------------------------------------------------------------------------


def run_command(cmd, timeout=120):
    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "returncode": 124,
            "stdout": exc.stdout or "",
            "stderr": (exc.stderr or "") + "\nTIMEOUT",
        }
    except FileNotFoundError:
        return {
            "returncode": 127,
            "stdout": "",
            "stderr": "COMMAND_NOT_FOUND",
        }


def is_transient_command_error(result):
    code = int(result.get("returncode", 1))
    stderr = (result.get("stderr") or "").lower()

    if code == 0:
        return False

    transient_terms = [
        "429",
        "too many requests",
        "timed out",
        "timeout",
        "temporarily unavailable",
        "connection reset",
        "network is unreachable",
        "service unavailable",
        "http error 500",
        "http error 502",
        "http error 503",
        "http error 504",
    ]
    for term in transient_terms:
        if term in stderr:
            return True

    if code in (124,):
        return True

    return False


def run_command_with_retry(cmd, timeout=120, attempts=4, base_delays=None, max_delay=45):
    if base_delays is None:
        base_delays = [2, 6, 18]

    last = None
    for attempt in range(1, attempts + 1):
        last = run_command(cmd, timeout=timeout)
        if int(last.get("returncode", 1)) == 0:
            return last

        if attempt >= attempts:
            return last

        if not is_transient_command_error(last):
            return last

        base = base_delays[min(attempt - 1, len(base_delays) - 1)]
        wait_s = min(max_delay, random.uniform(0.0, float(base)))
        time.sleep(wait_s)

    return last


# ---------------------------------------------------------------------------
# yt-dlp helpers
# ---------------------------------------------------------------------------


def build_ytdlp_auth_args(browser=None, cookies_file=None):
    args = []
    cookies_file = str(cookies_file or "").strip()
    browser = str(browser or "").strip()

    if cookies_file:
        args.extend(["--cookies", cookies_file])
    elif browser:
        args.extend(["--cookies-from-browser", browser])

    return args


def _duration_from_entry(entry):
    if isinstance(entry.get("duration_string"), str) and entry.get("duration_string"):
        return entry.get("duration_string")

    sec = entry.get("duration")
    if isinstance(sec, (int, float)) and sec >= 0:
        sec = int(sec)
        hrs = sec // 3600
        mins = (sec % 3600) // 60
        secs = sec % 60
        if hrs > 0:
            return "{0:02d}:{1:02d}:{2:02d}".format(hrs, mins, secs)
        return "{0:02d}:{1:02d}".format(mins, secs)

    return ""


def fetch_playlist_videos(playlist_id, browser=None, cookies_file=None):
    url = "https://www.youtube.com/playlist?list={0}".format(playlist_id)
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--dump-single-json",
        "--no-warnings",
    ]
    cmd.extend(build_ytdlp_auth_args(browser=browser, cookies_file=cookies_file))
    cmd.append(url)

    result = run_command_with_retry(cmd, timeout=120)
    if int(result.get("returncode", 1)) != 0:
        return "", [], result.get("stderr", "").strip()

    try:
        payload = json.loads(result.get("stdout", "") or "{}")
    except Exception:
        return "", [], "Invalid yt-dlp JSON output"

    entries = payload.get("entries") or []
    playlist_title = payload.get("title") or payload.get("playlist_title") or ""

    videos = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        video_id = str(entry.get("id") or "").strip()
        if not video_id:
            continue

        videos.append(
            {
                "id": video_id,
                "title": str(entry.get("title") or "Untitled").strip() or "Untitled",
                "channel": str(entry.get("channel") or entry.get("uploader") or "Unknown").strip() or "Unknown",
                "duration": _duration_from_entry(entry),
                "view_count": int(entry.get("view_count") or 0),
                "published": str(entry.get("upload_date") or "").strip(),
            }
        )

    return playlist_title, videos, ""


def normalize_upload_date(raw):
    raw = str(raw or "").strip()
    if len(raw) == 8 and raw.isdigit():
        return "{0}-{1}-{2}".format(raw[0:4], raw[4:6], raw[6:8])
    return raw


# ---------------------------------------------------------------------------
# Transcript extraction and VTT parsing
# ---------------------------------------------------------------------------


def _norm_caption_line(text):
    text = text.lower().strip()
    text = PUNCT_RE.sub("", text)
    text = re.sub(r"\s+", " ", text)
    return text


def parse_webvtt(vtt_text):
    text = (vtt_text or "").replace("\r\n", "\n").replace("\r", "\n")
    text = text.lstrip("\ufeff")
    blocks = re.split(r"\n\s*\n", text)

    out = []
    recent = []

    for block in blocks:
        lines = [line.strip() for line in block.split("\n") if line.strip()]
        if not lines:
            continue

        first = lines[0]
        if first.startswith(("WEBVTT", "NOTE", "STYLE", "REGION", "Kind:", "Language:")):
            continue

        if len(lines) > 1 and "-->" not in lines[0] and "-->" in lines[1]:
            lines = lines[1:]

        if not lines or "-->" not in lines[0]:
            continue

        text_lines = lines[1:]
        for line in text_lines:
            line = INLINE_TS_RE.sub("", line)
            line = TAG_RE.sub("", line)
            line = html.unescape(line)
            line = re.sub(r"\s+", " ", line).strip()
            if not line:
                continue

            normalized = _norm_caption_line(line)
            if normalized in recent:
                continue

            out.append(line)
            recent = (recent + [normalized])[-3:]

    return "\n".join(out).strip()


def _pick_best_vtt_file(vtt_paths):
    if not vtt_paths:
        return None
    # Prefer English-like captions, then longest file
    scored = []
    for p in vtt_paths:
        name = p.name.lower()
        score = 0
        if ".en" in name or "english" in name:
            score += 5
        try:
            score += int(p.stat().st_size / 1000)
        except Exception:
            pass
        scored.append((score, p))
    scored.sort(key=lambda item: item[0], reverse=True)
    return scored[0][1]


def extract_transcript_with_ytdlp(video_url, browser=None, cookies_file=None):
    temp_dir = Path(tempfile.mkdtemp(prefix="yt-archiver-"))
    try:
        output_tpl = str(temp_dir / "%(id)s.%(ext)s")
        cmd = [
            "yt-dlp",
            "--skip-download",
            "--write-auto-subs",
            "--write-subs",
            "--sub-format",
            "vtt",
            "--sub-langs",
            "all",
            "--output",
            output_tpl,
            "--no-warnings",
        ]
        cmd.extend(build_ytdlp_auth_args(browser=browser, cookies_file=cookies_file))
        cmd.append(video_url)

        result = run_command_with_retry(cmd, timeout=180)
        if int(result.get("returncode", 1)) != 0:
            return "", "failed"

        vtt_files = list(temp_dir.glob("*.vtt"))
        if not vtt_files:
            return "", "missing"

        best = _pick_best_vtt_file(vtt_files)
        if not best:
            return "", "missing"

        transcript = parse_webvtt(best.read_text(encoding="utf-8", errors="ignore"))
        if not transcript:
            return "", "missing"

        return transcript, "ok"
    finally:
        try:
            shutil.rmtree(str(temp_dir))
        except Exception:
            pass


def extract_transcript_with_summarize(video_url):
    if not command_exists("summarize"):
        return "", "unavailable"

    cmd = ["summarize", video_url, "--youtube", "auto", "--extract-only"]
    result = run_command_with_retry(cmd, timeout=180)
    if int(result.get("returncode", 1)) != 0:
        return "", "failed"

    text = (result.get("stdout") or "").strip()
    if not text:
        return "", "missing"

    if text.lower().startswith("transcript:"):
        text = text[len("transcript:") :].strip()

    return text, "ok"


def extract_transcript(video_url, browser=None, cookies_file=None, allow_summarize_fallback=True):
    transcript, status = extract_transcript_with_ytdlp(
        video_url,
        browser=browser,
        cookies_file=cookies_file,
    )
    if transcript:
        return transcript, "ok"

    if allow_summarize_fallback:
        fallback, fb_status = extract_transcript_with_summarize(video_url)
        if fallback:
            return fallback, "fallback"
        if status == "failed" and fb_status == "failed":
            return "", "failed"

    return "", status


# ---------------------------------------------------------------------------
# HTTP + LLM providers (urllib only)
# ---------------------------------------------------------------------------


def _is_transient_http_error(exc):
    if isinstance(exc, urllib.error.HTTPError):
        if exc.code in (408, 409, 425, 429, 500, 502, 503, 504):
            return True
    if isinstance(exc, urllib.error.URLError):
        return True
    return False


def _http_post_json(url, payload, headers=None, timeout_s=60, attempts=4, base_delays=None):
    if headers is None:
        headers = {}
    if base_delays is None:
        base_delays = [2, 6, 18]

    data = json.dumps(payload).encode("utf-8")
    headers = dict(headers)
    headers.setdefault("Content-Type", "application/json")

    last_exc = None
    for attempt in range(1, attempts + 1):
        req = urllib.request.Request(url, data=data, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout_s) as response:
                raw = response.read().decode("utf-8", errors="replace")
                if not raw.strip():
                    return {}
                return json.loads(raw)
        except Exception as exc:
            last_exc = exc
            if attempt >= attempts:
                break
            if not _is_transient_http_error(exc):
                break
            base = base_delays[min(attempt - 1, len(base_delays) - 1)]
            wait_s = random.uniform(0.0, float(base))
            time.sleep(wait_s)

    raise last_exc


def _extract_json_fragment(text):
    if not text:
        return None

    # Try array first
    array_match = re.search(r"\[[\s\S]*\]", text)
    if array_match:
        raw = array_match.group(0)
        try:
            return json.loads(raw)
        except Exception:
            pass

    obj_match = re.search(r"\{[\s\S]*\}", text)
    if obj_match:
        raw = obj_match.group(0)
        try:
            return json.loads(raw)
        except Exception:
            pass

    return None


def _call_openai_compatible(prompt, provider_cfg, timeout_s, temperature, max_tokens, default_url, auth_header=True):
    model = str(provider_cfg.get("model", "")).strip()
    base_url = str(provider_cfg.get("base_url", "")).strip() or default_url
    api_key_env = str(provider_cfg.get("api_key_env", "")).strip()
    api_key = os.environ.get(api_key_env, "") if api_key_env else ""

    headers = {"Content-Type": "application/json"}
    if auth_header:
        if not api_key:
            return None
        headers["Authorization"] = "Bearer {0}".format(api_key)

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    try:
        data = _http_post_json(base_url, payload, headers=headers, timeout_s=timeout_s)
    except Exception:
        return None

    choices = data.get("choices") or []
    if not choices:
        return None
    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []
        for chunk in content:
            if isinstance(chunk, dict) and chunk.get("type") == "text":
                parts.append(str(chunk.get("text", "")))
        return "\n".join(parts).strip()

    return None


def _call_anthropic(prompt, provider_cfg, timeout_s, temperature, max_tokens):
    model = str(provider_cfg.get("model", "")).strip()
    base_url = str(provider_cfg.get("base_url", "")).strip() or "https://api.anthropic.com/v1/messages"
    api_key_env = str(provider_cfg.get("api_key_env", "")).strip()
    api_key = os.environ.get(api_key_env, "") if api_key_env else ""
    if not api_key:
        return None

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        data = _http_post_json(base_url, payload, headers=headers, timeout_s=timeout_s)
    except Exception:
        return None

    content = data.get("content") or []
    parts = []
    for item in content:
        if isinstance(item, dict) and item.get("type") == "text":
            parts.append(str(item.get("text", "")))
    text = "\n".join(parts).strip()
    return text or None


def _call_gemini(prompt, provider_cfg, timeout_s, temperature, max_tokens):
    model = str(provider_cfg.get("model", "")).strip()
    base_url = str(provider_cfg.get("base_url", "")).strip()
    api_key_env = str(provider_cfg.get("api_key_env", "")).strip()
    api_key = os.environ.get(api_key_env, "") if api_key_env else ""
    if not api_key:
        return None

    if base_url:
        if "{model}" in base_url:
            url = base_url.format(model=model)
        else:
            url = base_url
    else:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/{0}:generateContent?key={1}"
        ).format(model, api_key)

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        },
    }

    headers = {"Content-Type": "application/json"}
    if "key=" not in url:
        headers["x-goog-api-key"] = api_key

    try:
        data = _http_post_json(url, payload, headers=headers, timeout_s=timeout_s)
    except Exception:
        return None

    candidates = data.get("candidates") or []
    if not candidates:
        return None

    parts = ((candidates[0].get("content") or {}).get("parts") or [])
    text_parts = []
    for part in parts:
        if isinstance(part, dict) and "text" in part:
            text_parts.append(str(part.get("text", "")))

    text = "\n".join(text_parts).strip()
    return text or None


def _call_ollama_native(prompt, provider_cfg, timeout_s, temperature, max_tokens):
    model = str(provider_cfg.get("model", "")).strip()
    base_url = str(provider_cfg.get("base_url", "")).strip() or "http://localhost:11434/api/generate"

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        },
    }

    try:
        data = _http_post_json(base_url, payload, headers={"Content-Type": "application/json"}, timeout_s=timeout_s)
    except Exception:
        return None

    response = data.get("response")
    if isinstance(response, str):
        return response.strip() or None
    return None


def _call_ollama_openai(prompt, provider_cfg, timeout_s, temperature, max_tokens):
    cfg = dict(provider_cfg)
    if not str(cfg.get("base_url", "")).strip():
        cfg["base_url"] = "http://localhost:11434/v1/chat/completions"

    # Ollama OpenAI endpoint usually does not require auth
    api_key_env = str(cfg.get("api_key_env", "")).strip()
    has_key = bool(api_key_env and os.environ.get(api_key_env, ""))
    return _call_openai_compatible(
        prompt,
        cfg,
        timeout_s=timeout_s,
        temperature=temperature,
        max_tokens=max_tokens,
        default_url="http://localhost:11434/v1/chat/completions",
        auth_header=has_key,
    )


def call_llm(prompt, provider_cfg, task="summary", response_format="text", temperature=0.2, max_tokens=800, timeout_s=60):
    _ = task
    provider = str((provider_cfg or {}).get("provider", "none")).lower().strip()
    if provider == "none":
        return None

    text = None

    if provider == "openai":
        text = _call_openai_compatible(
            prompt,
            provider_cfg,
            timeout_s=timeout_s,
            temperature=temperature,
            max_tokens=max_tokens,
            default_url="https://api.openai.com/v1/chat/completions",
            auth_header=True,
        )
    elif provider == "openrouter":
        text = _call_openai_compatible(
            prompt,
            provider_cfg,
            timeout_s=timeout_s,
            temperature=temperature,
            max_tokens=max_tokens,
            default_url="https://openrouter.ai/api/v1/chat/completions",
            auth_header=True,
        )
    elif provider == "anthropic":
        text = _call_anthropic(
            prompt,
            provider_cfg,
            timeout_s=timeout_s,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    elif provider == "gemini":
        text = _call_gemini(
            prompt,
            provider_cfg,
            timeout_s=timeout_s,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    elif provider == "ollama":
        mode = str(provider_cfg.get("api_mode", "auto")).lower().strip() or "auto"
        if mode == "openai":
            text = _call_ollama_openai(prompt, provider_cfg, timeout_s, temperature, max_tokens)
        elif mode == "native":
            text = _call_ollama_native(prompt, provider_cfg, timeout_s, temperature, max_tokens)
        else:
            text = _call_ollama_openai(prompt, provider_cfg, timeout_s, temperature, max_tokens)
            if not text:
                text = _call_ollama_native(prompt, provider_cfg, timeout_s, temperature, max_tokens)

    if text is None:
        return None

    if response_format == "json":
        parsed = _extract_json_fragment(text)
        return parsed

    return text.strip()


# ---------------------------------------------------------------------------
# Summaries and tags
# ---------------------------------------------------------------------------


def load_summary_prompt(summary_cfg):
    summary_cfg = summary_cfg or {}
    prompt_file = str(summary_cfg.get("prompt_file", "")).strip()

    if prompt_file:
        path = Path(prompt_file).expanduser()
        if path.exists():
            try:
                return path.read_text(encoding="utf-8")
            except Exception:
                pass

    default_prompt_path = Path(__file__).resolve().parents[1] / "references" / "default-summary-prompt.md"
    if default_prompt_path.exists():
        try:
            return default_prompt_path.read_text(encoding="utf-8")
        except Exception:
            pass

    return DEFAULT_SUMMARY_PROMPT


def _render_prompt(template, transcript, chunk_number=None, chunk_total=None):
    values = {
        "transcript": transcript,
        "chunk_number": chunk_number if chunk_number is not None else "",
        "chunk_total": chunk_total if chunk_total is not None else "",
    }
    try:
        return template.format(**values)
    except Exception:
        return "{0}\n\nTranscript:\n{1}".format(template, transcript)


def chunk_transcript(text, max_chars=12000, overlap_chars=300):
    text = (text or "").strip()
    if not text:
        return []

    parts = [p.strip() for p in text.split("\n") if p.strip()]
    if not parts:
        return []

    chunks = []
    current = []
    current_len = 0

    for part in parts:
        part_len = len(part) + 1
        if current and current_len + part_len > max_chars:
            chunks.append("\n".join(current).strip())
            carry = ""
            if overlap_chars > 0 and chunks[-1]:
                carry = chunks[-1][-overlap_chars:]
            current = [carry, part] if carry else [part]
            current_len = len("\n".join(current))
        else:
            current.append(part)
            current_len += part_len

    if current:
        chunks.append("\n".join(current).strip())

    return [chunk for chunk in chunks if chunk]


def summarize_transcript(transcript, summary_cfg):
    transcript = (transcript or "").strip()
    if not transcript:
        return "", "missing_transcript"

    summary_cfg = summary_cfg or {}
    provider = str(summary_cfg.get("provider", "none")).lower().strip()
    if provider == "none":
        return "", "skipped"

    template = load_summary_prompt(summary_cfg)
    chunks = chunk_transcript(transcript, max_chars=12000, overlap_chars=300)

    if not chunks:
        return "", "missing_transcript"

    if len(chunks) == 1:
        prompt = _render_prompt(template, chunks[0], chunk_number=1, chunk_total=1)
        result = call_llm(
            prompt,
            summary_cfg,
            task="summary",
            response_format="text",
            temperature=0.2,
            max_tokens=1200,
            timeout_s=90,
        )
        if isinstance(result, str) and result.strip():
            return result.strip(), "ok"
        return "", "failed"

    chunk_summaries = []
    total = len(chunks)
    for idx, chunk in enumerate(chunks, 1):
        chunk_prompt = (
            "You are summarizing chunk {0}/{1} of a transcript. "
            "Focus on factual details and key points.\n\n{2}"
        ).format(idx, total, _render_prompt(template, chunk, chunk_number=idx, chunk_total=total))

        part_summary = call_llm(
            chunk_prompt,
            summary_cfg,
            task="summary",
            response_format="text",
            temperature=0.2,
            max_tokens=700,
            timeout_s=90,
        )

        if isinstance(part_summary, str) and part_summary.strip():
            chunk_summaries.append("Chunk {0}/{1}\n{2}".format(idx, total, part_summary.strip()))

    if not chunk_summaries:
        return "", "failed"

    meta_prompt = """Combine these chunk summaries into one final summary.
Use this structure exactly:

## Key Takeaways
- 3 to 5 bullets

## Details
- Explain concrete tools, methods, and examples

## Notable Quotes
- 1 to 3 quotes if meaningful, otherwise 'None'

Chunk summaries:
{summaries}
""".format(
        summaries="\n\n".join(chunk_summaries)
    )

    final_summary = call_llm(
        meta_prompt,
        summary_cfg,
        task="summary",
        response_format="text",
        temperature=0.2,
        max_tokens=1200,
        timeout_s=90,
    )

    if isinstance(final_summary, str) and final_summary.strip():
        return final_summary.strip(), "ok-chunked"

    return "\n\n".join(chunk_summaries), "partial-chunked"


KEYWORD_MAP = {
    "tutorial": ["tutorial", "guide", "how to", "walkthrough", "learn", "beginner", "course"],
    "programming": ["programming", "coding", "python", "javascript", "typescript", "java", "go", "rust", "c++", "software"],
    "devops": ["devops", "kubernetes", "docker", "ci/cd", "infrastructure", "terraform", "ansible", "monitoring"],
    "ai": ["ai", "machine learning", "llm", "neural", "gpt", "model", "inference", "prompt"],
    "productivity": ["productivity", "workflow", "time management", "focus", "notes", "organization"],
    "design": ["design", "ui", "ux", "figma", "typography", "layout", "branding"],
    "hardware": ["hardware", "cpu", "gpu", "motherboard", "ram", "electronics", "raspberry pi"],
    "open-source": ["open source", "open-source", "foss", "github", "community"],
    "career": ["career", "job", "interview", "resume", "hiring", "leadership", "management"],
    "self-hosted": ["self-hosted", "self hosted", "homelab", "nas", "server", "home server"],
    "gaming": ["gaming", "game", "steam", "esports", "gameplay"],
    "science": ["science", "physics", "biology", "chemistry", "research", "experiment"],
    "music": ["music", "song", "audio", "mixing", "production", "instrument", "guitar", "piano"],
    "finance": ["finance", "investing", "stocks", "budget", "money", "economy", "trading"],
    "health": ["health", "fitness", "nutrition", "wellness", "exercise", "sleep", "mental health"],
}


def keyword_fallback_tags(title, summary, transcript, tags_vocabulary, max_tags=4):
    text = " ".join([title or "", summary or "", transcript or ""]).lower()
    matches = []

    for tag in tags_vocabulary:
        normalized = str(tag).strip()
        if not normalized:
            continue

        keywords = KEYWORD_MAP.get(normalized, [normalized.replace("-", " "), normalized])
        if any(keyword.lower() in text for keyword in keywords):
            matches.append(normalized)

    return matches[:max_tags]


def tag_video(title, summary, transcript, tags_vocabulary, tagging_cfg, max_tags=4):
    vocab = [str(tag).strip() for tag in (tags_vocabulary or []) if str(tag).strip()]
    if not vocab:
        return [], "empty_vocabulary"

    provider = str((tagging_cfg or {}).get("provider", "none")).lower().strip()
    if provider == "none":
        return keyword_fallback_tags(title, summary, transcript, vocab, max_tags=max_tags), "keyword"

    prompt = """Pick the most relevant tags from this allowed list only:
{tags}

Video title: {title}
Summary: {summary}
Transcript excerpt: {transcript}

Rules:
- Return only a JSON array of tags.
- Use only allowed tags.
- Choose 1 to {max_tags} tags.
- Return [] if nothing fits.
""".format(
        tags=json.dumps(vocab, ensure_ascii=False),
        title=title or "",
        summary=(summary or "")[:1500],
        transcript=(transcript or "")[:1500],
        max_tags=max_tags,
    )

    response = call_llm(
        prompt,
        tagging_cfg,
        task="tagging",
        response_format="json",
        temperature=0.1,
        max_tokens=250,
        timeout_s=60,
    )

    if isinstance(response, list):
        cleaned = []
        allowed = set(vocab)
        for item in response:
            tag = str(item).strip()
            if tag in allowed and tag not in cleaned:
                cleaned.append(tag)
        if cleaned:
            return cleaned[:max_tags], "llm"

    fallback = keyword_fallback_tags(title, summary, transcript, vocab, max_tags=max_tags)
    return fallback, "keyword"


# ---------------------------------------------------------------------------
# Import + enrich workflows
# ---------------------------------------------------------------------------


def _playlist_map(config, filter_ids=None):
    playlists = config.get("playlists", [])
    out = []

    wanted = None
    if filter_ids:
        wanted = set(filter_ids)

    for item in playlists:
        if not isinstance(item, dict):
            continue
        pid = str(item.get("id", "")).strip()
        name = str(item.get("name", "")).strip() or pid
        if not pid:
            continue
        if wanted is not None and pid not in wanted:
            continue
        out.append({"id": pid, "name": name})

    return out


def _unique_tags(existing, new_tags):
    seen = set()
    merged = []
    for item in list(existing or []) + list(new_tags or []):
        tag = str(item).strip()
        if not tag:
            continue
        if tag in seen:
            continue
        seen.add(tag)
        merged.append(tag)
    return merged


def import_videos(
    output_dir,
    config,
    dry_run=False,
    no_summary=False,
    no_tags=False,
    playlist_ids=None,
    browser_override=None,
    cookies_override=None,
):
    output_dir = Path(output_dir)
    ensure_dir(output_dir)

    browser = browser_override if browser_override is not None else config.get("browser", "")
    cookies_file = cookies_override if cookies_override is not None else config.get("cookies_file", "")

    playlists = _playlist_map(config, filter_ids=playlist_ids)
    existing_ids = load_existing_video_ids(output_dir)

    stats = {
        "playlists": 0,
        "created": 0,
        "skipped": 0,
        "failed": 0,
        "would_create": 0,
        "errors": [],
    }

    for playlist in playlists:
        stats["playlists"] += 1
        pid = playlist["id"]
        configured_name = playlist["name"]

        detected_name, videos, err = fetch_playlist_videos(
            pid,
            browser=browser,
            cookies_file=cookies_file,
        )

        if err:
            stats["errors"].append("Playlist {0}: {1}".format(pid, err))

        folder_name = configured_name or detected_name or pid
        folder = output_dir / folder_name

        for video in videos:
            video_id = str(video.get("id", "")).strip()
            if not video_id:
                stats["failed"] += 1
                continue

            if video_id in existing_ids:
                stats["skipped"] += 1
                continue

            title = str(video.get("title", "Untitled"))
            channel = str(video.get("channel", "Unknown"))
            url = "https://www.youtube.com/watch?v={0}".format(video_id)
            duration = str(video.get("duration", ""))
            view_count = int(video.get("view_count", 0) or 0)
            published = normalize_upload_date(video.get("published", ""))

            note_path = folder / note_filename(title, video_id)

            if dry_run:
                stats["would_create"] += 1
                continue

            transcript_text = ""
            transcript_status = "skipped"
            summary_text = ""
            summary_status = "skipped"
            tags_status = "skipped"

            tags = ["youtube-archive"]

            if not no_summary:
                transcript_text, transcript_status = extract_transcript(
                    url,
                    browser=browser,
                    cookies_file=cookies_file,
                    allow_summarize_fallback=True,
                )
                summary_text, summary_status = summarize_transcript(
                    transcript_text,
                    config.get("summary", {}),
                )

            if not no_tags:
                tagged, tags_status = tag_video(
                    title,
                    summary_text,
                    transcript_text,
                    config.get("tags", []),
                    config.get("tagging", {}),
                    max_tags=4,
                )
                tags = _unique_tags(tags, tagged)

            enriched = bool(summary_text or transcript_text or (tags and len(tags) > 1))
            frontmatter = {
                "title": title,
                "channel": channel,
                "url": url,
                "video_id": video_id,
                "published": published,
                "duration": duration,
                "view_count": view_count,
                "source_playlist": folder_name,
                "created": today_iso(),
                "enriched": enriched,
                "enriched_at": utc_now_iso() if enriched else "",
                "enrichment_version": 1,
                "tags": tags,
                "transcript_status": transcript_status,
                "summary_status": summary_status,
                "tags_status": tags_status,
            }

            try:
                write_note(note_path, frontmatter, summary_text=summary_text, transcript_text=transcript_text)
                existing_ids[video_id] = note_path
                stats["created"] += 1
            except Exception as exc:
                stats["failed"] += 1
                stats["errors"].append("{0}: {1}".format(note_path.name, exc))

    return stats


def discover_notes(output_dir):
    output_dir = Path(output_dir)
    notes = []
    if not output_dir.exists():
        return notes

    for path in output_dir.rglob("*.md"):
        if any(part.startswith(".") for part in path.parts):
            continue
        notes.append(path)

    notes.sort()
    return notes


def enrich_notes(output_dir, config, dry_run=False, limit=None):
    output_dir = Path(output_dir)
    browser = config.get("browser", "")
    cookies_file = config.get("cookies_file", "")

    stats = {
        "processed": 0,
        "enriched": 0,
        "skipped": 0,
        "failed": 0,
        "errors": [],
    }

    notes = discover_notes(output_dir)

    for note_path in notes:
        if limit is not None and stats["enriched"] >= int(limit):
            break

        try:
            note = read_note(note_path)
        except Exception as exc:
            stats["failed"] += 1
            stats["errors"].append("{0}: {1}".format(note_path, exc))
            continue

        fm = dict(note.get("frontmatter", {}))
        if fm.get("enriched") is True:
            stats["skipped"] += 1
            continue

        video_id = str(fm.get("video_id", "")).strip()
        url = str(fm.get("url", "")).strip()
        title = str(fm.get("title", "Untitled"))

        if not video_id or not url:
            stats["skipped"] += 1
            continue

        stats["processed"] += 1

        transcript_text = ""
        transcript_status = "skipped"
        summary_text = ""
        summary_status = "skipped"

        if str(config.get("summary", {}).get("provider", "none")).lower().strip() != "none":
            transcript_text, transcript_status = extract_transcript(
                url,
                browser=browser,
                cookies_file=cookies_file,
                allow_summarize_fallback=True,
            )
            summary_text, summary_status = summarize_transcript(
                transcript_text,
                config.get("summary", {}),
            )

        tagged, tags_status = tag_video(
            title,
            summary_text,
            transcript_text,
            config.get("tags", []),
            config.get("tagging", {}),
            max_tags=4,
        )

        existing_tags = fm.get("tags", []) if isinstance(fm.get("tags"), list) else []
        merged_tags = _unique_tags(existing_tags, ["youtube-archive"] + tagged)

        fm["tags"] = merged_tags
        fm["enriched"] = True
        fm["enriched_at"] = utc_now_iso()
        fm["enrichment_version"] = 1
        fm["transcript_status"] = transcript_status
        fm["summary_status"] = summary_status
        fm["tags_status"] = tags_status

        if dry_run:
            stats["enriched"] += 1
            continue

        try:
            write_note(note_path, fm, summary_text=summary_text, transcript_text=transcript_text)
            stats["enriched"] += 1
        except Exception as exc:
            stats["failed"] += 1
            stats["errors"].append("{0}: {1}".format(note_path, exc))

    return stats


# ---------------------------------------------------------------------------
# Sync state
# ---------------------------------------------------------------------------


def update_sync_state(output_dir, mode, stats):
    output_dir = Path(output_dir)
    ensure_dir(output_dir)
    path = output_dir / SYNC_STATE_NAME

    state = {
        "last_run": utc_now_iso(),
        "mode": mode,
        "stats": stats,
    }

    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    return path
