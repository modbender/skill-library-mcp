#!/usr/bin/env python3
"""
Rent-A-Human-Agent Bounty Scanner

Pulls open bounties, scores for feasibility, filters scams,
sends top picks to Telegram. Run via cron or /rent scan.

============HOT KEYS================
python bounty_hunter.py --jobs        # List all open job postings (raw, no scoring)
python bounty_hunter.py --humans      # List available humans for hire
python bounty_hunter.py --force       # Bypass cache, fresh Grok scoring
python bounty_hunter.py --no-telegram # Skip sending to Telegram
===================================

Project: Rent-A-Human-Agent
Repo: github.com/shane9coy/Rent-A-Human-Agent
Built by: x.com/@shaneswrld_ | github.com/shane9coy
"""

import os
import sys
import json
import threading
import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dotenv import load_dotenv

# Project root is 4 levels up from this script
# .claude/skills/rent/scripts/bounty_hunter.py -> project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
SCRIPT_DIR = Path(__file__).parent

# Skill directory is 2 levels up from this script
# .claude/skills/rent/scripts/bounty_hunter.py -> .claude/skills/rent/
PROJECT_DIR = Path(__file__).parent.parent

# Load .env from project root
load_dotenv(PROJECT_ROOT / ".env")

RENTAHUMAN_API_KEY = os.getenv("RENTAHUMAN_API_KEY", "")
XAI_API_KEY = os.getenv("XAI_API_KEY", "")
RENTAHUMAN_BASE = "https://rentahuman.ai/api"
RENTAHUMAN_WEB = "https://rentahuman.ai"
CACHE_DIR = PROJECT_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)
CACHE_FILE = CACHE_DIR / "bounties_cache.json"
CACHE_TXT_FILE = CACHE_DIR / "bounties_ranked.txt"
CACHE_TTL_HOURS = 12
CACHE_VERSION = 2  # Bump to invalidate old caches (v1 had unfiltered for-hire ads)

# Skills you can actually do — bounties matching these score higher
MY_SKILLS = [
    "web development", "python", "javascript", "react", "node",
    "automation", "ai", "swe", "full stack", "marketing",
    "research", "writing", "data entry", "design",
]

SCAM_SIGNALS = [
    "send money", "send eth", "send btc", "send crypto",
    "wallet:", "0x", "deposit first", "return to your",
    "get paid to register", "sign up and get", "2.5x",
    "dm me", "whatsapp", "join our telegram",
]

# "For hire" self-promotions — these are people advertising themselves, not posting jobs
FOR_HIRE_SIGNALS = [
    "my name is", "i am a ", "i'm a ", "hire me", "available for",
    "looking for work", "looking for opportunities", "my portfolio",
    "my experience", "years of experience", "i specialize in",
    "i offer", "my services", "freelancer with", "developer with",
    "i can help", "reach out to me", "contact me for",
]


# ── API ──────────────────────────────────────────────────

def _headers():
    return {"X-API-Key": RENTAHUMAN_API_KEY, "Content-Type": "application/json"}


def fetch_bounties():
    """Pull all open bounties."""
    r = requests.get(f"{RENTAHUMAN_BASE}/bounties", headers=_headers(), timeout=15)
    r.raise_for_status()
    return r.json().get("bounties", [])


# ── Filtering ────────────────────────────────────────────

def filter_recent(bounties, hours=48):
    """Keep only bounties created in the last N hours."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    recent = []
    for b in bounties:
        created = b.get("createdAt", "")
        if not created:
            recent.append(b)
            continue
        try:
            dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            if dt >= cutoff:
                recent.append(b)
        except (ValueError, TypeError):
            recent.append(b)
    return recent


def filter_jobs_only(bounties):
    """Remove 'for hire' self-promotions — keep only actual job postings."""
    jobs = []
    for b in bounties:
        text = f"{b.get('title', '')} {b.get('description', '')}".lower()
        hits = sum(1 for s in FOR_HIRE_SIGNALS if s in text)
        if hits >= 2:
            continue  # Almost certainly a self-promo
        # Title pattern: "Job Title – Person Name" where desc starts with "I am"
        if hits >= 1 and ("–" in b.get("title", "") or "—" in b.get("title", "")):
            continue
        jobs.append(b)
    return jobs


# ── Scoring ──────────────────────────────────────────────

def score_bounty(bounty):
    """Score a bounty 0-100 for feasibility and value."""
    score = 50
    price = bounty.get("price", 0) or 0
    hours = bounty.get("estimatedHours", 1) or 1
    hourly = price / hours

    # Pay rate
    if hourly >= 50:
        score += 20
    elif hourly >= 25:
        score += 10
    elif hourly < 10:
        score -= 15

    # Remote
    if bounty.get("location", {}).get("isRemoteAllowed"):
        score += 10

    # Scam detection
    text = f"{bounty.get('title', '')} {bounty.get('description', '')}".lower()
    scam_hits = sum(1 for s in SCAM_SIGNALS if s in text)
    if scam_hits >= 2:
        score -= 40
    elif scam_hits == 1:
        score -= 15

    # Skill match
    needed = [s.lower() for s in bounty.get("skillsNeeded", [])]
    if needed:
        matches = sum(1 for s in needed if any(ms in s or s in ms for ms in MY_SKILLS))
        score += 15 if matches > 0 else -10

    # Description quality
    desc_len = len(bounty.get("description", ""))
    if desc_len > 200:
        score += 5
    elif desc_len < 50:
        score -= 10

    # Competition
    spots = bounty.get("spotsAvailable", 1) or 1
    filled = bounty.get("spotsFilled", 0) or 0
    if spots > 1 and filled == 0:
        score += 5
    if spots - filled <= 0:
        score -= 50

    # Easy categories
    if bounty.get("category", "") in ("research", "physical-tasks", "errands"):
        score += 5

    return max(0, min(100, score))


# ── Cache ───────────────────────────────────────────

def load_cache():
    """Load cached scan results. Returns (data, is_fresh) tuple."""
    try:
        cache = json.loads(CACHE_FILE.read_text())
        # Invalidate if wrong version (old caches had unfiltered for-hire ads)
        if cache.get("version") != CACHE_VERSION:
            _log(f"Cache version mismatch (found {cache.get('version')}, need {CACHE_VERSION}) — invalidating")
            return None, False
        last_call = datetime.fromisoformat(cache.get("last_call", "2000-01-01"))
        age = datetime.now() - last_call
        is_fresh = age.total_seconds() < CACHE_TTL_HOURS * 3600
        return cache, is_fresh
    except Exception:
        return None, False


def save_cache(scored_bounties):
    """Save scored bounties to cache with timestamp."""
    CACHE_DIR.mkdir(exist_ok=True)
    cache = {
        "version": CACHE_VERSION,
        "last_call": datetime.now().isoformat(),
        "model": "grok-4-1-fast-reasoning",
        "bounties": [
            {"id": b.get("id"), "title": b.get("title"), "score": s, "reason": b.get("_grok_reason", "")}
            for b, s in scored_bounties
        ],
    }
    CACHE_FILE.write_text(json.dumps(cache, indent=2))
    generate_cache_txt(cache)


def generate_cache_txt(cache):
    """Generate human-readable TXT file from cache."""
    cached = cache.get("bounties", [])
    if not cached:
        return
    last_call = datetime.fromisoformat(cache.get("last_call", datetime.now().isoformat()))
    model = cache.get("model", "heuristic")
    
    lines = [
        f"BOUNTY SCAN RESULTS — {datetime.now().strftime('%b %d %Y %I:%M %p')}",
        f"Scored via: {model}",
        f"Total: {len(cached)} bounties",
        "=" * 60,
        "",
    ]
    for i, entry in enumerate(cached, 1):
        reason = entry.get("reason", "")
        bid = entry.get("id", "")
        title = entry.get("title", "Untitled")
        score = entry.get("score", "?")
        link = f"{RENTAHUMAN_WEB}/bounties/{bid}" if bid else ""
        lines.append(f"#{i}. [{score}/100] {title}")
        if reason:
            lines.append(f"    Reason: {reason}")
        if link:
            lines.append(f"    Link: {link}")
        if bid:
            lines.append(f"    ID: {bid[:8]}")
        lines.append("")
    
    CACHE_TXT_FILE.write_text("\n".join(lines))


# ── Grok Scoring ────────────────────────────────────

def _log(msg):
    """Print timestamped status to terminal."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[scanner {ts}] {msg}")


def grok_score_bounties(bounties):
    """Send bounties to Grok for AI scoring. Returns [(bounty, score), ...] sorted."""
    if not XAI_API_KEY or not bounties:
        if not XAI_API_KEY:
            _log("XAI_API_KEY not set — skipping Grok")
        return None

    _log(f"Sending {len(bounties)} bounties to Grok (grok-4-1-fast-reasoning)...")

    # Build compact bounty summaries for the prompt
    summaries = []
    for i, b in enumerate(bounties):
        summaries.append({
            "idx": i,
            "title": b.get("title", ""),
            "price": b.get("price", 0),
            "hours": b.get("estimatedHours", 0),
            "category": b.get("category", ""),
            "skills": b.get("skillsNeeded", []),
            "remote": b.get("location", {}).get("isRemoteAllowed", False),
            "spots": b.get("spotsAvailable", 1),
            "desc": (b.get("description", "") or "")[:300],
        })

    prompt = (
        "You are a bounty evaluator for a freelance platform. Score each bounty 0-100 "
        "based on: pay rate, feasibility, location requirements (I'm in northern Ohio, USA) skill match (python, web dev, "
        "AI, automation, marketing, writing, research, vibe coach, photographer, telegram, psychologist, life coach, mcp, design), remote availability, and description quality.\n\n"
        "IMPORTANT: These should be REAL JOB POSTINGS where someone pays for work to be done. "
        "Score < 10 for 'for hire' self-promotions (people advertising their own skills/services, "
        "résumés, 'hire me' posts). Only score high for actual tasks/gigs with clear deliverables.\n\n"
        "Flag scams (crypto deposits, upfront payments, suspicious links) with score < 20.\n\n"
        f"Bounties:\n{json.dumps(summaries)}\n\n"
        "Respond with ONLY a JSON array, no markdown, no explanation:\n"
        '[{"idx": 0, "score": 90, "reason": "Good pay, skill match"}, ...]'
    )

    try:
        r = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {XAI_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "grok-4-1-fast-reasoning",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
            },
        )
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"].strip()
        # Strip markdown fences if present
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        scores = json.loads(content)

        scored = []
        for item in scores:
            idx = item.get("idx", -1)
            if 0 <= idx < len(bounties):
                bounties[idx]["_grok_reason"] = item.get("reason", "")
                scored.append((bounties[idx], item.get("score", 50)))
        scored.sort(key=lambda x: x[1], reverse=True)
        _log(f"Grok scored {len(scored)} bounties")
        return scored

    except requests.exceptions.HTTPError as e:
        _log(f"Grok API HTTP error: {e.response.status_code} — falling back to heuristic")
        return None
    except json.JSONDecodeError as e:
        _log(f"Grok returned invalid JSON: {e} — falling back to heuristic")
        return None
    except Exception as e:
        _log(f"Grok scoring failed: {type(e).__name__}: {e} — falling back to heuristic")
        return None


# ── Formatting ───────────────────────────────────────────

def format_bounty(b, score=None):
    """Format a single bounty for Telegram."""
    bid = b.get("id", "")
    title = b.get("title", "Untitled")
    price = b.get("price", 0) or 0
    hours = b.get("estimatedHours", 0) or 0
    category = b.get("category", "")
    remote = b.get("location", {}).get("isRemoteAllowed", False)
    spots = b.get("spotsAvailable", "?")
    agent = b.get("agentName", "")
    link = f"{RENTAHUMAN_WEB}/bounties/{bid}"

    hourly_str = f" (${price/hours:.0f}/hr)" if price and hours else ""
    flags = []
    if remote:
        flags.append("Remote")
    if category:
        flags.append(category)
    flag_str = " | ".join(flags)

    reason = b.get("_grok_reason", "")
    lines = [f"[{title}]({link})"]
    lines.append(f"  ${price} / {hours}hrs{hourly_str} | {flag_str}")
    if agent:
        lines.append(f"  Posted by: {agent}")
    lines.append(f"  Spots: {spots} | ID: `{bid[:8]}`")
    if score is not None:
        lines.append(f"  Score: {score}/100{' — ' + reason if reason else ''}")
    return "\n".join(lines)


def format_digest(scored_bounties, limit=20):
    """Format top bounties as a Telegram digest."""
    top = scored_bounties[:limit]
    if not top:
        return None
    lines = ["**Bounty Scanner — Top Opportunities**", ""]
    for b, s in top:
        lines.append(format_bounty(b, s))
        lines.append("")
    lines.append(f"Scanned {datetime.now().strftime('%b %d %I:%M %p')} | {len(scored_bounties)} total scored")
    return "\n".join(lines)


# ── Scanner (cron entry point) ───────────────────────────

def _format_cache(cache, limit=20):
    """Format cached bounties for display."""
    cached = cache.get("bounties", [])
    if not cached:
        return None
    last_call = datetime.fromisoformat(cache["last_call"])
    age_mins = int((datetime.now() - last_call).total_seconds() / 60)
    model = cache.get("model", "heuristic")

    if age_mins < 60:
        age_str = f"{age_mins}min ago"
    else:
        age_str = f"{age_mins // 60}hr {age_mins % 60}min ago"

    lines = [f"**Bounty Scanner** — scored {age_str} via {model}", ""]
    for entry in cached[:limit]:
        reason = entry.get("reason", "")
        bid = entry.get("id", "")
        title = entry.get("title", "Untitled")
        link = f"{RENTAHUMAN_WEB}/bounties/{bid}" if bid else ""
        lines.append(f"[{title}]({link})" if link else f"**{title}**")
        lines.append(f"  Score: {entry.get('score', '?')}/100{' — ' + reason if reason else ''}")
        if bid:
            lines.append(f"  ID: `{bid[:8]}`")
        lines.append("")
    return "\n".join(lines)


def _background_rescore(hours, limit):
    """Background thread: fetch + Grok score + save to cache."""
    try:
        _log("Background rescore started...")
        bounties = fetch_bounties()
        bounties = filter_jobs_only(bounties)
        recent = filter_recent(bounties, hours=hours)

        if not recent:
            _log(f"No candidates to score ({len(bounties)} total)")
            return

        scored = grok_score_bounties(recent)
        if scored is None:
            _log("Grok failed in background — using heuristic")
            scored = [(b, score_bounty(b)) for b in recent]
            scored.sort(key=lambda x: x[1], reverse=True)
            # Mark as heuristic in cache
            for b, _ in scored:
                b["_grok_reason"] = ""

        scored = [(b, s) for b, s in scored if s >= 20]
        save_cache(scored)

        _log(f"Background rescore done — {len(scored)} bounties cached")
    except Exception as e:
        _log(f"Background rescore error: {e}")


def scan(hours=1000, limit=20, force=False):
    """Run a scan. Always returns cache first, refreshes in background when stale.

    Set force=True to block and re-score with Grok now (waits for result).
    """
    if not RENTAHUMAN_API_KEY:
        return "RENTAHUMAN_API_KEY not set."

    cache, is_fresh = load_cache()

    # Force mode: block, rescore ALL bounties now
    if force:
        _log("Force mode — blocking while Grok scores...")
        bounties = fetch_bounties()
        _log(f"Fetched {len(bounties)} total, filtering for-hire ads...")
        bounties = filter_jobs_only(bounties)
        _log(f"{len(bounties)} real job postings — scoring all")

        if not bounties:
            return "No bounties found."

        scored = grok_score_bounties(bounties)
        if scored is None:
            _log("Grok unavailable — heuristic scoring")
            scored = [(b, score_bounty(b)) for b in bounties]
            scored.sort(key=lambda x: x[1], reverse=True)
        scored = [(b, s) for b, s in scored if s >= 20]

        save_cache(scored)

        digest = format_digest(scored, limit=limit)
        return digest or "No opportunities scored above threshold."

    # Normal mode: always show cache, background refresh if stale
    if cache:
        result = _format_cache(cache, limit=limit)
        if is_fresh:
            _log("Loaded from cache (fresh)")
            return result
        else:
            _log("Cache is stale — returning cached + refreshing in background")
            thread = threading.Thread(
                target=_background_rescore, args=(hours, limit), daemon=True
            )
            thread.start()
            return (result or "") + "\nPulling new data in background. Refresh in a few minutes."

    # No cache at all: heuristic score immediately, Grok in background
    _log("No cache found — heuristic scoring now, Grok in background")
    bounties = fetch_bounties()
    bounties = filter_jobs_only(bounties)
    recent = filter_recent(bounties, hours=hours)

    if not recent:
        return f"No bounties in the last {hours}hrs ({len(bounties)} total checked)."

    # Quick heuristic scores for immediate display
    scored = [(b, score_bounty(b)) for b in recent]
    scored.sort(key=lambda x: x[1], reverse=True)
    scored = [(b, s) for b, s in scored if s >= 20]
    save_cache(scored)

    # Kick off Grok in background for next time
    thread = threading.Thread(
        target=_background_rescore, args=(hours, limit), daemon=True
    )
    thread.start()

    digest = format_digest(scored, limit=limit)
    suffix = "\nGrok scoring in background. Refresh in a few minutes for AI-ranked results."
    return (digest or "No opportunities scored above threshold.") + suffix


def send_telegram(text):
    """Send via Telegram bot API (for cron use)."""
    from telegram_helpers import _load_profile
    profile = _load_profile()
    chat_id = profile.get("telegram", {}).get("chat_id")
    bot_token = os.getenv("KATANA_HTTP_TELEGRAM_BOT_TOKEN", "")
    if not chat_id or not bot_token:
        print(text)
        return
    requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        },
        timeout=10,
    )


def list_jobs():
    """List all open job postings (filtered, no scoring)."""
    _log("Fetching job postings...")
    bounties = fetch_bounties()
    total = len(bounties)
    bounties = filter_jobs_only(bounties)
    _log(f"{len(bounties)} jobs (filtered {total - len(bounties)} for-hire ads)")
    if not bounties:
        return "No open job postings found."
    lines = [f"**Open Job Postings** ({len(bounties)} found)", ""]
    for b in bounties:
        bid = b.get("id", "")
        title = b.get("title", "Untitled")
        price = b.get("price", 0) or 0
        hours = b.get("estimatedHours", 0) or 0
        category = b.get("category", "")
        spots = b.get("spotsRemaining", b.get("spotsAvailable", "?"))
        apps = b.get("applicationCount", 0)
        link = f"{RENTAHUMAN_WEB}/bounties/{bid}"
        hourly = f" (${price/hours:.0f}/hr)" if price and hours else ""
        lines.append(f"[{title}]({link})")
        lines.append(f"  ${price}{hourly} | {category} | Spots: {spots} | Apps: {apps}")
        lines.append("")
    return "\n".join(lines)


def list_humans():
    """List available humans for hire."""
    from telegram_helpers import rent_list_humans
    return rent_list_humans()


def main():
    """CLI entry point.

    Usage:
        python bounty_hunter.py              Scan + Grok score (cached)
        python bounty_hunter.py --jobs       List all open job postings
        python bounty_hunter.py --humans     List available humans for hire
        python bounty_hunter.py --force      Bypass cache, fresh Grok scoring
        python bounty_hunter.py --no-telegram  Skip sending to Telegram
    """
    if "--help" in sys.argv or "-h" in sys.argv:
        print(main.__doc__)
        return

    if "--jobs" in sys.argv:
        result = list_jobs()
        print(result)
        return

    if "--humans" in sys.argv or "--rent" in sys.argv:
        result = list_humans()
        print(result)
        return

    force = "--force" in sys.argv
    skip_tg = "--no-telegram" in sys.argv

    _log("Bounty scanner starting...")
    result = scan(hours=140, limit=20, force=force)

    print()
    print(result)
    print()

    if not skip_tg and "No bounties" not in result and "not set" not in result:
        send_telegram(result)
        _log("Sent digest to Telegram")
    else:
        _log("Done (not sent to Telegram)")

    # If background thread is running, wait for it
    for t in threading.enumerate():
        if t.name != "MainThread" and t.daemon:
            _log("Waiting for background Grok scoring to finish...")
            t.join()
            _log("Background scoring complete")


if __name__ == "__main__":
    main()
