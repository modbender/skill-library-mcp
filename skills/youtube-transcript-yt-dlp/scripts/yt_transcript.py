#!/usr/bin/env python3
"""Extract YouTube subtitles/captions (manual preferred, else auto) using yt-dlp.

Personal-scale oriented:
- No webserver
- SQLite cache (default: {baseDir}/cache/transcripts.sqlite)
- Output: json segments or plain text

Security:
- Validates input as YouTube URL or 11-char video id.
- Does not pass arbitrary user args to shell.

Requires:
- python3
- yt-dlp on PATH
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import time
import hashlib
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Literal

YOUTUBE_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{11}$")
# Accept common YouTube domains; keep conservative to avoid passing arbitrary URLs to yt-dlp.
YOUTUBE_URL_RE = re.compile(
    r"^https?://(www\.)?(youtube\.com|youtu\.be|m\.youtube\.com)/.+",
    re.IGNORECASE,
)

# Extract video id from common URL shapes (best-effort; still validate with YOUTUBE_ID_RE).
_YT_WATCH_ID_RE = re.compile(r"[?&]v=([a-zA-Z0-9_-]{11})")
_YT_SHORT_ID_RE = re.compile(r"youtu\.be/([a-zA-Z0-9_-]{11})")


class TranscriptError(RuntimeError):
    pass


@dataclasses.dataclass(frozen=True)
class Choice:
    kind: Literal["subtitles", "automatic_captions"]
    lang: str
    ext: str  # prefer vtt


def _run(cmd: list[str], timeout_s: int = 60) -> str:
    try:
        p = subprocess.run(
            cmd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_s,
        )
    except FileNotFoundError:
        raise TranscriptError(f"Missing required binary: {cmd[0]}")
    except subprocess.TimeoutExpired:
        raise TranscriptError(f"Command timed out after {timeout_s}s: {' '.join(cmd)}")

    if p.returncode != 0:
        # Keep stderr short; yt-dlp can be very verbose.
        err = (p.stderr or p.stdout or "").strip()
        err = "\n".join(err.splitlines()[-25:])
        raise TranscriptError(f"yt-dlp failed (code {p.returncode}).\n{err}")
    return p.stdout


def _normalize_input(s: str) -> str:
    s = s.strip()
    if YOUTUBE_ID_RE.match(s):
        # Let yt-dlp resolve by id. (It accepts bare IDs.)
        return s
    if YOUTUBE_URL_RE.match(s):
        return s
    raise TranscriptError("Input must be a YouTube URL or 11-character video id")


def _extract_video_id(video: str) -> str | None:
    """Best-effort extraction of 11-char YouTube id from a URL or id."""

    v = video.strip()
    if YOUTUBE_ID_RE.match(v):
        return v
    m = _YT_WATCH_ID_RE.search(v)
    if m:
        return m.group(1)
    m = _YT_SHORT_ID_RE.search(v)
    if m:
        return m.group(1)
    return None


def _yt_dlp_info(video: str, cookies: Path | None) -> dict[str, Any]:
    cmd = ["yt-dlp", "-J", "--skip-download", "--no-warnings", "--ignore-no-formats-error"]
    if cookies is not None:
        cmd += ["--cookies", str(cookies)]
    cmd += [video]
    out = _run(cmd, timeout_s=90)
    try:
        return json.loads(out)
    except json.JSONDecodeError as e:
        raise TranscriptError(f"Failed to parse yt-dlp JSON: {e}")


def _pick_lang(available: dict[str, Any], prefer: str | None) -> str | None:
    if not available:
        return None

    keys = list(available.keys())

    # Exact preferred match first
    if prefer and prefer in available:
        return prefer

    # If they asked for en-US, allow en
    if prefer and "-" in prefer:
        base = prefer.split("-", 1)[0]
        if base in available:
            return base

    # Prefer English, then first available
    for k in ("en", "en-US", "en-GB"):
        if k in available:
            return k

    return keys[0]


def _choose_caption(info: dict[str, Any], prefer_lang: str | None) -> Choice:
    subs = info.get("subtitles") or {}
    autos = info.get("automatic_captions") or {}

    # Manual captions preferred
    lang = _pick_lang(subs, prefer_lang)
    if lang:
        ext = _pick_ext(subs.get(lang, []))
        return Choice(kind="subtitles", lang=lang, ext=ext)

    # Auto captions fallback
    lang = _pick_lang(autos, prefer_lang)
    if lang:
        ext = _pick_ext(autos.get(lang, []))
        return Choice(kind="automatic_captions", lang=lang, ext=ext)

    raise TranscriptError("No captions/subtitles available for this video")


def _pick_ext(entries: list[dict[str, Any]]) -> str:
    # Prefer VTT, then anything
    exts = [e.get("ext") for e in entries if e.get("ext")]
    if "vtt" in exts:
        return "vtt"
    return exts[0] if exts else "vtt"


def _download_caption(video: str, choice: Choice, out_dir: Path, cookies: Path | None) -> Path:
    # Use a fixed out template so we can locate the file.
    tmpl = str(out_dir / "sub")

    common = [
        "yt-dlp",
        "--skip-download",
        "--no-warnings",
        "--ignore-no-formats-error",
    ]
    if cookies is not None:
        common += ["--cookies", str(cookies)]
    common += [
        "--sub-lang",
        choice.lang,
        "--sub-format",
        choice.ext,
        "-o",
        tmpl,
        video,
    ]

    if choice.kind == "subtitles":
        cmd = common[:]
        cmd.insert(1, "--write-subs")
    else:
        cmd = common[:]
        cmd.insert(1, "--write-auto-subs")

    _run(cmd, timeout_s=120)

    # yt-dlp outputs like sub.<lang>.<ext> or similar.
    # Find the first matching file in out_dir.
    candidates = sorted(out_dir.glob(f"sub*.{choice.lang}*.{choice.ext}"))
    if not candidates:
        # Fallback: any .vtt in dir
        candidates = sorted(out_dir.glob(f"*.{choice.ext}"))
    if not candidates:
        raise TranscriptError("Caption download succeeded but no subtitle file was found")
    return candidates[0]


def _parse_vtt(path: Path) -> list[dict[str, Any]]:
    # Minimal WebVTT parser good enough for YouTube VTT.
    text = path.read_text(errors="ignore")
    lines = [ln.rstrip("\n") for ln in text.splitlines()]

    segs: list[dict[str, Any]] = []
    i = 0

    def parse_ts(ts: str) -> float:
        # 00:01:02.345 or 01:02.345
        parts = ts.split(":")
        if len(parts) == 3:
            h, m, s = parts
        elif len(parts) == 2:
            h = "0"
            m, s = parts
        else:
            raise ValueError(ts)
        if "." in s:
            sec, ms = s.split(".", 1)
            ms = (ms + "000")[:3]
        else:
            sec, ms = s, "000"
        return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000.0

    # Skip header
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    if i < len(lines) and lines[i].startswith("WEBVTT"):
        i += 1

    cue_text: list[str] = []
    start = end = None

    while i < len(lines):
        ln = lines[i].strip()
        i += 1

        if not ln:
            if start is not None and end is not None and cue_text:
                seg_text = " ".join(_clean_caption_line(x) for x in cue_text if x.strip())
                seg_text = re.sub(r"\s+", " ", seg_text).strip()
                if seg_text:
                    segs.append(
                        {
                            "start": float(start),
                            "duration": float(max(0.0, end - start)),
                            "text": seg_text,
                        }
                    )
            cue_text = []
            start = end = None
            continue

        if "-->" in ln:
            # Timestamp line
            try:
                left, right = [x.strip() for x in ln.split("-->", 1)]
                right = right.split(" ", 1)[0].strip()  # strip settings
                start = parse_ts(left)
                end = parse_ts(right)
            except Exception:
                # Ignore malformed cue
                start = end = None
                cue_text = []
            continue

        # Optional cue id line: ignore if next line is timestamp
        if start is None and i < len(lines) and "-->" in lines[i]:
            continue

        cue_text.append(ln)

    # flush
    if start is not None and end is not None and cue_text:
        seg_text = " ".join(_clean_caption_line(x) for x in cue_text if x.strip())
        seg_text = re.sub(r"\s+", " ", seg_text).strip()
        if seg_text:
            segs.append({"start": float(start), "duration": float(max(0.0, end - start)), "text": seg_text})

    return segs


_TAG_RE = re.compile(r"<[^>]+>")


def _clean_caption_line(s: str) -> str:
    # Remove simple markup and speaker tags.
    s = _TAG_RE.sub("", s)
    # YouTube sometimes uses HTML entities already; keep simple.
    return s


def _segments_to_text(segs: list[dict[str, Any]], include_ts: bool) -> str:
    if include_ts:
        out_lines = []
        for s in segs:
            out_lines.append(f"[{s['start']:.2f}s] {s['text']}")
        return "\n".join(out_lines).strip() + "\n"
    return "\n".join(s["text"] for s in segs).strip() + "\n"


def _load_netscape_cookies_map(cookies_path: Path) -> dict[str, str]:
    """Parse Netscape cookies.txt into a name->value map (YouTube/Google only)."""

    mp: dict[str, str] = {}
    for ln in cookies_path.read_text(errors="ignore").splitlines():
        if not ln or ln.startswith("#"):
            continue
        fields = ln.split("\t")
        if len(fields) < 7:
            continue
        domain, _flag, _path, _secure, _exp, name, value = fields[:7]
        domain = domain.lstrip(".")
        if domain.endswith("youtube.com") or domain.endswith("google.com"):
            mp[name] = value
    return mp


def _load_netscape_cookies_for_youtube(cookies_path: Path) -> str:
    """Return a Cookie header value from a Netscape cookies.txt file."""

    mp = _load_netscape_cookies_map(cookies_path)
    return "; ".join(f"{k}={v}" for k, v in mp.items())


def _http_get(url: str, cookies: Path | None, timeout_s: int = 25) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    if cookies is not None:
        headers["Cookie"] = _load_netscape_cookies_for_youtube(cookies)
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def _extract_balanced_json(text: str, marker: str) -> dict[str, Any] | None:
    """Extract a *JSON* object following a marker like 'ytInitialData ='.

    Note: ytcfg.set(...) is often JS, not strict JSON; this may return None.
    """

    idx = text.find(marker)
    if idx < 0:
        return None
    i = text.find("{", idx)
    if i < 0:
        return None

    depth = 0
    in_str = False
    esc = False
    for j in range(i, len(text)):
        ch = text[j]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        else:
            if ch == '"':
                in_str = True
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    blob = text[i : j + 1]
                    try:
                        return json.loads(blob)
                    except Exception:
                        return None
    return None


def _extract_json_object_after(text: str, needle: str) -> dict[str, Any] | None:
    """Extract a JSON object that appears after a substring, e.g. '"INNERTUBE_CONTEXT":'."""

    idx = text.find(needle)
    if idx < 0:
        return None
    i = text.find("{", idx)
    if i < 0:
        return None

    depth = 0
    in_str = False
    esc = False
    for j in range(i, len(text)):
        ch = text[j]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        else:
            if ch == '"':
                in_str = True
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    blob = text[i : j + 1]
                    try:
                        return json.loads(blob)
                    except Exception:
                        return None
    return None


def _thirdparty_tubetranscript(video_id: str) -> tuple[str, str, list[dict[str, Any]]]:
    """Last-resort fallback via a third-party transcript provider.

    tubetranscript.com fetches transcripts from an API at:
      https://yt-to-text.com/api/v1/Subtitles

    We call that API directly (no YouTube cookies) as a last resort.

    This is *not* YouTube and may break / rate-limit / change at any time.
    Returns (lang, source, segments).

    NOTE: Despite the function name, this returns source="thirdparty:yt-to-text".
    """

    api = "https://yt-to-text.com/api/v1/Subtitles"
    body = json.dumps({"video_id": video_id}).encode("utf-8")
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "x-source": "tubetranscript",
        "x-app-version": "1.0",
    }

    req = urllib.request.Request(api, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", errors="ignore")
        raise TranscriptError(f"Third-party fallback (yt-to-text) HTTP {e.code}: {msg[:200]}")
    except urllib.error.URLError as e:
        raise TranscriptError(f"Third-party fallback (yt-to-text) failed: {e}")

    try:
        obj = json.loads(raw)
    except Exception as e:
        raise TranscriptError(f"Third-party fallback (yt-to-text) bad JSON: {e}")

    transcripts = (((obj.get("data") or {}).get("transcripts")) if isinstance(obj, dict) else None)
    if not transcripts or not isinstance(transcripts, list):
        raise TranscriptError("Third-party fallback (yt-to-text) returned no transcript")

    segs: list[dict[str, Any]] = []
    for it in transcripts:
        if not isinstance(it, dict):
            continue
        start = it.get("start")
        text = it.get("text")
        if start is None and it.get("s") is not None:
            start = it.get("s")
        if text is None and it.get("t") is not None:
            text = it.get("t")
        try:
            start_f = float(start) if start is not None else 0.0
        except Exception:
            start_f = 0.0
        text_s = re.sub(r"\s+", " ", str(text or "")).strip()
        if not text_s:
            continue
        segs.append({"start": start_f, "duration": 0.0, "text": text_s})

    if not segs:
        raise TranscriptError("Third-party fallback (yt-to-text) returned empty transcript")

    # De-dup consecutive duplicates
    deduped = []
    prev = None
    for s in segs:
        if s["text"] == prev:
            continue
        deduped.append(s)
        prev = s["text"]

    return "en", "thirdparty:yt-to-text", deduped


def _thirdparty_downsub(video_id: str) -> tuple[str, str, list[dict[str, Any]]]:
    """Third-party fallback using DownSub backends.

    Flow:
      1) Encrypt video id to an ENC_ID blob (same as DownSub client)
      2) GET https://get-info.downsub.com/<ENC_ID> to get subtitle tracks + urlSubtitle
      3) Pick a track and GET <urlSubtitle>/?title=...&url=<ENC_TRACK>

    Returns (lang, source, segments).
    """

    # Minimal AES-JSON format compatible with DownSub's CryptoJS formatter.
    # DownSub uses AES encrypt(JSON.stringify(value), key, {format: Mt}).toString(),
    # where Mt outputs {ct, iv, s} JSON and then base64-url encodes it.
    # We re-implement using CryptoJS-compatible AES via PyCryptodome would be heavy,
    # so instead we call their backend indirectly by using an already-generated ENC_ID.
    # Practically: we can generate ENC_ID by mimicking CryptoJS with openssl? Not reliable.
    #
    # Better approach: use the same scheme as their site: AES -> JSON -> base64url.
    # Implemented below using `Crypto.Cipher.AES` from PyCryptodome if available.

    try:
        from Crypto.Cipher import AES  # type: ignore
        from Crypto.Protocol.KDF import EVP_BytesToKey  # type: ignore
        from Crypto.Random import get_random_bytes  # type: ignore
    except Exception as e:
        raise TranscriptError(
            "DownSub fallback requires pycryptodome (Crypto). Install: pip install pycryptodome"
        )

    def _b64e(b: bytes) -> str:
        return base64.b64encode(b).decode("ascii")

    def _b64url(s: str) -> str:
        # their Pt: btoa -> base64url-like with -_ and strip '='
        return s.replace("+", "-").replace("/", "_").replace("=", "").strip()

    def _pad_pkcs7(data: bytes, bs: int = 16) -> bytes:
        pad = bs - (len(data) % bs)
        return data + bytes([pad]) * pad

    def _cryptojs_encrypt_json(value: str, key: str) -> str:
        # CryptoJS AES encrypt with passphrase uses OpenSSL EVP_BytesToKey with random salt.
        salt = get_random_bytes(8)
        k, iv = EVP_BytesToKey(key.encode("utf-8"), salt, 32, 16)
        cipher = AES.new(k, AES.MODE_CBC, iv)
        ct = cipher.encrypt(_pad_pkcs7(value.encode("utf-8")))
        obj = {"ct": _b64e(ct), "iv": iv.hex(), "s": salt.hex()}
        raw = json.dumps(obj, separators=(",", ":"))
        return _b64url(_b64e(raw.encode("utf-8")))

    # Key is embedded in DownSub JS.
    downsub_key = "zthxw34cdp6wfyxmpad38v52t3hsz6c5"

    enc_id = _cryptojs_encrypt_json(json.dumps(video_id), downsub_key)

    info_url = f"https://get-info.downsub.com/{enc_id}"
    info_raw = _http_get(info_url, cookies=None, timeout_s=30)
    try:
        info = json.loads(info_raw)
    except Exception:
        raise TranscriptError("DownSub fallback: get-info returned non-JSON")

    url_sub = info.get("urlSubtitle")
    subs = info.get("subtitles") or []
    if not url_sub or not isinstance(url_sub, str) or not subs:
        raise TranscriptError("DownSub fallback: no subtitles returned")

    # Pick first available track (usually auto-generated English); better selection later.
    track = subs[0]
    enc_track = track.get("url") if isinstance(track, dict) else None
    if not enc_track or not isinstance(enc_track, str):
        raise TranscriptError("DownSub fallback: subtitle track missing url")

    # Download SRT (default)
    title = info.get("title") or video_id
    q = urllib.parse.urlencode({"title": str(title)[:80], "url": enc_track})
    srt = _http_get(url_sub + "?" + q, cookies=None, timeout_s=30)

    # Parse SRT into segments
    segs: list[dict[str, Any]] = []
    cur_start = None
    cur_text = []
    for line in srt.splitlines():
        line = line.strip("\ufeff").rstrip()
        if re.match(r"^\d+$", line):
            continue
        m = re.match(r"^(\d{2}):(\d{2}):(\d{2}),(\d{3})\s+-->\s+(\d{2}):(\d{2}):(\d{2}),(\d{3})", line)
        if m:
            # flush
            if cur_start is not None and cur_text:
                segs.append({"start": cur_start, "duration": 0.0, "text": " ".join(cur_text).strip()})
            hh, mm, ss, ms = map(int, m.group(1, 2, 3, 4))
            cur_start = hh * 3600 + mm * 60 + ss + ms / 1000.0
            cur_text = []
            continue
        if not line:
            if cur_start is not None and cur_text:
                segs.append({"start": cur_start, "duration": 0.0, "text": " ".join(cur_text).strip()})
            cur_start = None
            cur_text = []
            continue
        cur_text.append(line)

    if cur_start is not None and cur_text:
        segs.append({"start": cur_start, "duration": 0.0, "text": " ".join(cur_text).strip()})

    if not segs:
        raise TranscriptError("DownSub fallback: empty transcript")

    # best-effort language
    lang = (track.get("code") if isinstance(track, dict) else None) or "en"
    return str(lang), "thirdparty:downsub", segs


def _thirdparty_noteey(video_id: str) -> tuple[str, str, list[dict[str, Any]]]:
    """Third-party fallback using Noteey subtitles API.

    Endpoint:
      GET https://api.noteey.com/api/v1/youtube/subtitles?url=<youtube-url>&language=<lang>

    Returns (lang, source, segments).
    """

    # Noteey expects full URL
    yt_url = f"https://youtu.be/{video_id}"
    api = "https://api.noteey.com/api/v1/youtube/subtitles"
    qs = urllib.parse.urlencode({"url": yt_url, "language": "en-US"})
    raw = _http_get(api + "?" + qs, cookies=None, timeout_s=30)

    try:
        items = json.loads(raw)
    except Exception:
        raise TranscriptError("Noteey fallback: non-JSON response")

    if not isinstance(items, list) or not items:
        raise TranscriptError("Noteey fallback: empty response")

    segs: list[dict[str, Any]] = []
    for it in items:
        if not isinstance(it, dict):
            continue
        try:
            start = float(it.get("from", 0.0))
        except Exception:
            start = 0.0
        try:
            dur = float(it.get("dur", 0.0))
        except Exception:
            dur = 0.0
        text = re.sub(r"\s+", " ", str(it.get("content") or "")).strip()
        if not text:
            continue
        segs.append({"start": start, "duration": dur, "text": text})

    if not segs:
        raise TranscriptError("Noteey fallback: no usable segments")

    return "en", "thirdparty:noteey", segs


def _youtubei_transcript(video_id: str, cookies: Path | None) -> tuple[str, str, list[dict[str, Any]]]:
    """Fallback transcript extraction using YouTube's engagement panel transcript endpoint.

    Returns (lang, source, segments).
    """

    watch_url = f"https://www.youtube.com/watch?v={video_id}&hl=en"
    html = _http_get(watch_url, cookies=cookies, timeout_s=30)

    # 1) Extract params for get_transcript from the watch page.
    m = re.search(r'"getTranscriptEndpoint"\s*:\s*\{\s*"params"\s*:\s*"([^"]+)"', html)
    if not m:
        raise TranscriptError("Transcript panel params not found on watch page")
    params = m.group(1)

    # 2) Extract youtubei config (API key + context + headers)
    # ytcfg.set(...) is often JS (not strict JSON), so prefer regex/JSON fragments.
    ytcfg = _extract_balanced_json(html, "ytcfg.set(") or {}

    api_key = ytcfg.get("INNERTUBE_API_KEY")
    context = ytcfg.get("INNERTUBE_CONTEXT")
    client_name = ytcfg.get("INNERTUBE_CONTEXT_CLIENT_NAME")
    client_version = ytcfg.get("INNERTUBE_CONTEXT_CLIENT_VERSION")
    visitor_data = ytcfg.get("VISITOR_DATA")
    page_cl = ytcfg.get("PAGE_CL")
    page_label = ytcfg.get("PAGE_BUILD_LABEL")

    if not context:
        context = _extract_json_object_after(html, '"INNERTUBE_CONTEXT":')

    if not api_key:
        m2 = re.search(r'"INNERTUBE_API_KEY"\s*:\s*"([^"]+)"', html)
        api_key = m2.group(1) if m2 else None

    if client_name is None:
        m = re.search(r'"INNERTUBE_CONTEXT_CLIENT_NAME"\s*:\s*(\d+)', html)
        client_name = m.group(1) if m else None
    if client_version is None:
        m = re.search(r'"INNERTUBE_CONTEXT_CLIENT_VERSION"\s*:\s*"([^"]+)"', html)
        client_version = m.group(1) if m else None
    if not visitor_data:
        m = re.search(r'"VISITOR_DATA"\s*:\s*"([^"]+)"', html)
        visitor_data = m.group(1) if m else None
    if page_cl is None:
        m = re.search(r'"PAGE_CL"\s*:\s*"?([^",}]+)', html)
        page_cl = m.group(1) if m else None
    if page_label is None:
        m = re.search(r'"PAGE_BUILD_LABEL"\s*:\s*"([^"]+)"', html)
        page_label = m.group(1) if m else None

    if not api_key:
        raise TranscriptError("INNERTUBE_API_KEY not found on watch page")
    if not context:
        # Last-resort context
        context = {"client": {"clientName": "WEB", "clientVersion": client_version or "2.20240201.01.00"}}

    # 3) Call youtubei get_transcript
    url = f"https://www.youtube.com/youtubei/v1/get_transcript?key={api_key}"

    body = json.dumps({"context": context, "params": params}).encode("utf-8")
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://www.youtube.com",
        "Referer": watch_url,
        "Accept-Language": "en-US,en;q=0.9",
    }
    # These headers materially affect youtubei responses.
    if client_name is not None:
        headers["X-Youtube-Client-Name"] = str(client_name)
    if client_version is not None:
        headers["X-Youtube-Client-Version"] = str(client_version)
    if visitor_data:
        headers["X-Goog-Visitor-Id"] = str(visitor_data)
    if page_cl:
        headers["X-Youtube-Page-CL"] = str(page_cl)
    if page_label:
        headers["X-Youtube-Page-Label"] = str(page_label)
    headers["X-Youtube-Bootstrap-Logged-In"] = "true"

    cookie_map = None
    if cookies is not None:
        cookie_map = _load_netscape_cookies_map(cookies)
        headers["Cookie"] = "; ".join(f"{k}={v}" for k, v in cookie_map.items())

    # Logged-in youtubei requests often require SAPISIDHASH auth.
    if cookie_map is not None:
        sapisid = cookie_map.get("SAPISID") or cookie_map.get("__Secure-3PAPISID")
        if sapisid:
            ts = str(int(time.time()))
            origin = "https://www.youtube.com"
            h = hashlib.sha1(f"{ts} {sapisid} {origin}".encode("utf-8")).hexdigest()
            headers["Authorization"] = f"SAPISIDHASH {ts}_{h}"
            headers["X-Origin"] = origin
            headers.setdefault("X-Goog-AuthUser", "0")

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as e:
        # youtubei errors are common under bot checks / gating
        msg = e.read().decode("utf-8", errors="ignore")
        raise TranscriptError(f"youtubei get_transcript HTTP {e.code}: {msg[:200]}")
    except urllib.error.URLError as e:
        raise TranscriptError(f"youtubei get_transcript failed: {e}")

    try:
        obj = json.loads(raw)
    except Exception as e:
        raise TranscriptError(f"Failed to parse youtubei transcript JSON: {e}")

    # 4) Traverse transcript structure
    def walk(o: Any):
        if isinstance(o, dict):
            for k, v in o.items():
                yield k, v
                yield from walk(v)
        elif isinstance(o, list):
            for it in o:
                yield from walk(it)

    cue_groups = None
    for k, v in walk(obj):
        if k == "cueGroups" and isinstance(v, list):
            cue_groups = v
            break

    if not cue_groups:
        raise TranscriptError("youtubei transcript response missing cueGroups")

    segs: list[dict[str, Any]] = []
    for g in cue_groups:
        r = (g or {}).get("transcriptCueGroupRenderer") or {}
        cues = r.get("cues") or []
        for c in cues:
            cr = (c or {}).get("transcriptCueRenderer") or {}
            start_ms = cr.get("startOffsetMs")
            dur_ms = cr.get("durationMs")
            cue = cr.get("cue") or {}
            txt = cue.get("simpleText") or ""
            txt = re.sub(r"\s+", " ", str(txt)).strip()
            if not txt:
                continue
            try:
                start = float(start_ms) / 1000.0 if start_ms is not None else 0.0
                dur = float(dur_ms) / 1000.0 if dur_ms is not None else 0.0
            except Exception:
                start, dur = 0.0, 0.0
            segs.append({"start": start, "duration": dur, "text": txt})

    if not segs:
        raise TranscriptError("youtubei transcript returned no cues")

    # Best-effort language detection
    lang = "en"
    # Some responses include language code in a top-level field; search for it.
    for k, v in walk(obj):
        if k in ("language", "languageCode") and isinstance(v, str) and len(v) <= 12:
            lang = v
            break

    # De-dup consecutive duplicate cue texts
    deduped = []
    prev = None
    for s in segs:
        if s["text"] == prev:
            continue
        deduped.append(s)
        prev = s["text"]

    return lang, "panel", deduped


def _db_connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(db_path))
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS transcripts (
          video_id TEXT NOT NULL,
          lang TEXT NOT NULL,
          source TEXT NOT NULL,  -- manual|auto
          include_timestamp INTEGER NOT NULL,
          format TEXT NOT NULL,  -- json|text
          payload TEXT NOT NULL,
          created_at TEXT NOT NULL,
          PRIMARY KEY (video_id, lang, source, include_timestamp, format)
        )
        """
    )
    return con


def _cache_get(
    con: sqlite3.Connection,
    video_id: str,
    lang: str,
    source: str,
    include_timestamp: bool,
    fmt: str,
) -> str | None:
    cur = con.execute(
        """
        SELECT payload FROM transcripts
        WHERE video_id=? AND lang=? AND source=? AND include_timestamp=? AND format=?
        """,
        (video_id, lang, source, 1 if include_timestamp else 0, fmt),
    )
    row = cur.fetchone()
    return row[0] if row else None


def _cache_put(
    con: sqlite3.Connection,
    video_id: str,
    lang: str,
    source: str,
    include_timestamp: bool,
    fmt: str,
    payload: str,
) -> None:
    con.execute(
        """
        INSERT OR REPLACE INTO transcripts
          (video_id, lang, source, include_timestamp, format, payload, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            video_id,
            lang,
            source,
            1 if include_timestamp else 0,
            fmt,
            payload,
            dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        ),
    )
    con.commit()


def _is_within(child: Path, parent: Path) -> bool:
    try:
        child_r = child.resolve()
        parent_r = parent.resolve()
    except Exception:
        return False
    return parent_r == child_r or parent_r in child_r.parents


def _validate_path_allowed(*, path: Path, allowed_dirs: list[Path], must_exist: bool, kind: str) -> Path:
    p = path.expanduser()

    if must_exist and not p.exists():
        raise TranscriptError(f"{kind} file not found: {p}")

    # If p doesn't exist yet (e.g., cache DB), validate against its parent dir.
    check_target = p if p.exists() else p.parent
    ok = any(_is_within(check_target, d.expanduser()) for d in allowed_dirs)
    if not ok:
        allowed = ", ".join(str(d.expanduser()) for d in allowed_dirs)
        raise TranscriptError(f"{kind} path not allowed: {p} (allowed under: {allowed})")

    return p


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract YouTube captions (manual preferred; else auto) via yt-dlp")
    ap.add_argument("video", help="YouTube URL or 11-char video id")
    ap.add_argument("--lang", default=None, help="Preferred language code (e.g., en, en-US)")
    ap.add_argument("--text", action="store_true", help="Output plain text (default: JSON)")
    ap.add_argument("--no-ts", action="store_true", help="Disable timestamps (default: enabled)")
    ap.add_argument("--cache", default=None, help="SQLite cache path (default: {baseDir}/cache/transcripts.sqlite)")
    ap.add_argument(
        "--cookies",
        default=None,
        help="Path to Netscape cookies.txt for YouTube (or set YT_TRANSCRIPT_COOKIES)",
    )
    args = ap.parse_args()

    video = _normalize_input(args.video)
    include_ts = not args.no_ts
    fmt = "text" if args.text else "json"

    base_dir = Path(__file__).resolve().parents[1]

    # Path allowlisting (defense-in-depth; prevents skill misuse even if caller is sloppy).
    allowed_cache_dirs = [base_dir / "cache", Path("~/.config/yt-transcript")]  # cache DB
    allowed_cookie_dirs = [Path("~/.config/yt-transcript")]  # cookies must live here

    db_path = Path(args.cache) if args.cache else (base_dir / "cache" / "transcripts.sqlite")
    db_path = _validate_path_allowed(path=db_path, allowed_dirs=allowed_cache_dirs, must_exist=False, kind="Cache")

    cookies_env = os.environ.get("YT_TRANSCRIPT_COOKIES")
    cookies_path = Path(args.cookies) if args.cookies else (Path(cookies_env) if cookies_env else None)

    # Public/publishable behavior: do NOT auto-load cookies from inside the skill directory.
    # Cookies must be explicitly provided via --cookies or YT_TRANSCRIPT_COOKIES.
    if cookies_path is not None:
        cookies_path = _validate_path_allowed(
            path=cookies_path,
            allowed_dirs=allowed_cookie_dirs,
            must_exist=True,
            kind="Cookies",
        )

    con = _db_connect(db_path)

    # Try yt-dlp info first; if yt-dlp is blocked, fall back to URL/id parsing.
    info = None
    try:
        info = _yt_dlp_info(video, cookies_path)
        video_id = info.get("id")
    except TranscriptError:
        video_id = None

    if not video_id or not isinstance(video_id, str):
        video_id = _extract_video_id(video)

    if not video_id or not isinstance(video_id, str):
        raise TranscriptError("Could not resolve video id")

    # Primary path: yt-dlp subtitles/auto-captions.
    # Fallback path: YouTube engagement panel transcript endpoint (youtubei/v1/get_transcript).

    try:
        if info is None:
            raise TranscriptError("yt-dlp metadata unavailable")
        choice = _choose_caption(info, args.lang)
        source = "manual" if choice.kind == "subtitles" else "auto"
        lang_for_cache = choice.lang

        cached = _cache_get(con, video_id, lang_for_cache, source, include_ts, fmt)
        if cached is not None:
            try:
                sys.stdout.write(cached)
            except BrokenPipeError:
                return 0
            return 0

        with tempfile.TemporaryDirectory(prefix="ytcap_") as td:
            out_dir = Path(td)
            cap_path = _download_caption(video, choice, out_dir, cookies_path)
            segs = _parse_vtt(cap_path)
            if not segs:
                raise TranscriptError("Transcript returned empty after parsing")

            # De-dup consecutive duplicate cue texts (common in some YouTube VTT variants)
            deduped = []
            prev = None
            for s in segs:
                t = s.get("text")
                if t and t == prev:
                    continue
                deduped.append(s)
                prev = t
            segs = deduped

    except TranscriptError as e:
        # Fallback order:
        # 1) YouTube transcript panel (youtubei/v1/get_transcript)
        # (No third-party fallbacks in the public/publishable version.)

        # (1) Fallback to transcript panel (often works when VTT tracks aren't exposed).
        cached = _cache_get(con, video_id, "en", "panel", include_ts, fmt)
        if cached is not None:
            try:
                sys.stdout.write(cached)
            except BrokenPipeError:
                return 0
            return 0

        try:
            lang_for_cache, source, segs = _youtubei_transcript(video_id, cookies_path)
        except TranscriptError:
            # No third-party fallbacks in this build.
            raise

    if fmt == "json":
        payload = json.dumps(
            {
                "video_id": video_id,
                "lang": lang_for_cache,
                "source": source,
                "segments": segs if include_ts else [{"text": s["text"]} for s in segs],
            },
            ensure_ascii=False,
        ) + "\n"
    else:
        payload = _segments_to_text(segs, include_ts)

    _cache_put(con, video_id, lang_for_cache, source, include_ts, fmt, payload)
    try:
        sys.stdout.write(payload)
    except BrokenPipeError:
        # Allow piping to head/sed without stack traces.
        return 0
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except TranscriptError as e:
        sys.stderr.write(f"ERROR: {e}\n")
        raise SystemExit(2)
