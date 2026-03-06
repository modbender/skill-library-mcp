#!/usr/bin/env python3
"""
MoltMemory — Moltbook skill for OpenClaw agents
Handles: thread continuity, auto verification, heartbeat, feed, USDC hooks
"""

import json, os, re, sys
from datetime import datetime, timezone
from pathlib import Path
import urllib.request, urllib.error

# ── Config ────────────────────────────────────────────────────────────────────
API_BASE        = "https://www.moltbook.com/api/v1"
CURRENT_VERSION = "1.5.5"
GITHUB_REPO     = "ubgb/moltmemory"

# Users permanently blocked — never reply to, never DM, never engage with
BLOCKED_USERS   = {"pipeline-debug-7f3a"}
STATE_FILE = Path(os.environ.get("MOLTMEMORY_STATE", "~/.config/moltbook/state.json")).expanduser()
CREDS_FILE = Path("~/.config/moltbook/credentials.json").expanduser()

def load_creds():
    if not CREDS_FILE.exists():
        raise FileNotFoundError(f"No credentials at {CREDS_FILE}")
    return json.loads(CREDS_FILE.read_text())

def load_state():
    defaults = {
        "engaged_threads": {},
        "bookmarks": [],
        "last_home_check": None,
        "seen_post_ids": [],        # feed cursor: posts already seen
        "last_feed_check": None,    # ISO timestamp of last feed scan
        "replied_comment_ids": [],  # comment IDs we've already replied to (dupe guard)
    }
    if not STATE_FILE.exists():
        return defaults
    try:
        state = json.loads(STATE_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        # Torn write or corrupt file — start fresh, don't crash
        return defaults
    # Backfill new keys for existing state files
    for k, v in defaults.items():
        state.setdefault(k, v)
    return state

def save_state(state):
    """Atomic write — temp file + os.replace() so readers never see a partial write."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2))
    os.replace(tmp, STATE_FILE)  # atomic on POSIX, near-atomic on Windows

def get_unanswered_comments(api_key, state, post_ids):
    """
    Return comments on our posts that genuinely have no reply from us yet.
    Uses replied_comment_ids in state as the source of truth — NOT content matching.
    post_ids: list of post UUIDs to scan
    """
    replied = set(state.get("replied_comment_ids", []))
    unanswered = []
    for pid in post_ids:
        r = api("GET", f"/posts/{pid}/comments", api_key=api_key)
        for c in r.get("comments", []):
            if c.get("is_deleted") or c.get("is_spam"): continue
            author = c.get("author", {}).get("name", "").lower()
            if author == "clawofaron": continue
            if author in {u.lower() for u in BLOCKED_USERS}: continue  # blocked
            if c.get("depth", 0) != 0: continue  # top-level only
            if c.get("id") in replied: continue   # already handled
            unanswered.append({**c, "_post_id": pid})
    return unanswered


def mark_replied(state, comment_id):
    """Record that we've replied to a comment. Cap at 2000 to avoid unbounded growth."""
    replied = state.get("replied_comment_ids", [])
    if comment_id not in replied:
        replied.append(comment_id)
    if len(replied) > 2000:
        replied = replied[-2000:]
    state["replied_comment_ids"] = replied


SKILL_DIR = Path(__file__).parent.resolve()
AUTO_UPDATE = os.environ.get("MOLTMEMORY_AUTO_UPDATE", "0") == "1"


def check_for_updates(state, auto_update=None):
    """
    Check GitHub for a newer version. Only runs every 12h to avoid rate limiting.
    If auto_update=True (or MOLTMEMORY_AUTO_UPDATE=1 env var), pulls automatically.
    Returns a status string, or None if current or check failed.
    """
    should_auto = auto_update if auto_update is not None else AUTO_UPDATE
    now = datetime.now(timezone.utc)
    last = state.get("last_version_check")
    if last:
        diff = (now - datetime.fromisoformat(last)).total_seconds()
        if diff < 43200:  # 12 hours
            return None
    try:
        req = urllib.request.Request(
            f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest",
            headers={"User-Agent": f"moltmemory/{CURRENT_VERSION}"},
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.load(r)
        latest = data.get("tag_name", "").lstrip("v")
        state["last_version_check"] = now.isoformat()
        state["latest_known_version"] = latest
        if latest and latest != CURRENT_VERSION:
            if should_auto:
                return _auto_pull(latest)
            return (
                f"🔄 Update available: v{CURRENT_VERSION} → v{latest} — "
                f"run: git -C {SKILL_DIR} pull"
            )
    except Exception:
        pass  # non-fatal — version check never breaks heartbeat
    return None


def _auto_pull(latest):
    """Pull latest version from GitHub into the skill directory. Non-fatal."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "-C", str(SKILL_DIR), "pull", "--ff-only"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return f"✅ Auto-updated: v{CURRENT_VERSION} → v{latest} (restart to apply)"
        else:
            return (
                f"⚠️  Auto-update failed (git pull returned {result.returncode}) — "
                f"run manually: git -C {SKILL_DIR} pull"
            )
    except Exception as e:
        return f"⚠️  Auto-update failed ({e}) — run: git -C {SKILL_DIR} pull"

# ── HTTP ──────────────────────────────────────────────────────────────────────
def api(method, path, body=None, api_key=None):
    url = f"{API_BASE}{path}"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())

# ── Verification Solver ───────────────────────────────────────────────────────
_W2N = {
    'zero':0,'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,
    'eight':8,'nine':9,'ten':10,'eleven':11,'twelve':12,'thirteen':13,
    'fourteen':14,'fifteen':15,'sixteen':16,'seventeen':17,'eighteen':18,
    'nineteen':19,'twenty':20,'thirty':30,'forty':40,'fifty':50,'sixty':60,
    'seventy':70,'eighty':80,'ninety':90,'hundred':100,'thousand':1000,
    # Phonetic / obfuscated variants seen in real challenges
    'twenny':20,'twnty':20,'fourty':40,
}
_SORTED_WORDS = sorted(_W2N.keys(), key=len, reverse=True)

def _word_matches_at(word, text, pos, max_subs=0, boundaries=None):
    """Match word against text[pos:], allowing each word-character to absorb
    one or more identical consecutive characters in the text.

    Handles:
    - Letter-doubling obfuscation:  'seeven' matches 'seven'
    - Natural double letters:       'three' matches 'three' (not 'thre')
    - Letter-swap obfuscation:      'fiftenn' matches 'fifteen' (max_subs=1)

    When the next word character is the same as the current one (e.g. 'e','e'
    in 'three'), we consume ONLY the minimum (1 char) so the following word
    character still has text to match against.

    For the LAST word character: consume greedily only if the full run lands
    on a run boundary (same space-delimited token); otherwise consume exactly 1
    to avoid bleeding into an adjacent word that starts with the same letter
    (e.g. 'fifteen' + 'newtons' sharing an 'n' run in the alpha string).

    max_subs: allowed single-character substitutions (each consumes one text
    char and one word char without requiring a match).
    boundaries: set of boundary positions from _find_numbers (optional).
    """
    wi, ti = 0, pos
    subs_used = 0
    while wi < len(word):
        c = word[wi]
        if ti >= len(text):
            return None
        if text[ti] != c:
            # Substitutions allowed at interior positions only (not first or
            # last char of the word).  Obfuscation doubles/triples chars; it
            # doesn't swap the leading or trailing letter to a different one.
            # This prevents "right"→"eight" (first-char) and
            # "neighb"→"eight" (last-char 'b'→'t') false positives.
            if subs_used < max_subs and 0 < wi < len(word) - 1:
                subs_used += 1
                ti += 1
                wi += 1
                continue
            return None
        # Count consecutive same chars in text starting at ti
        run_end = ti
        while run_end < len(text) and text[run_end] == c:
            run_end += 1
        # Last word char: consume full run only if that lands at a boundary
        # (isolated token); otherwise consume exactly 1 to avoid overshoot.
        # Mid-word: if the NEXT word char is also 'c', consume only 1.
        # Otherwise: greedy — consume the full run (handles doubled obfuscation).
        if wi + 1 >= len(word):
            if boundaries is not None and run_end in boundaries:
                ti = run_end   # greedy — lands exactly at token boundary
            else:
                ti += 1        # conservative — 1 char only
        elif word[wi + 1] == c:
            ti += 1
        else:
            ti = run_end
        wi += 1
    return ti  # position after the match

def _find_numbers(text_lower):
    """Extract number words (and bare digits) from lowercased text.
    Returns a flat list of integer values, with adjacent tens+units combined
    (e.g. [20, 3] → [23]).

    Builds the concatenated alpha string (alpha_digits view) but also tracks
    which positions are "run boundaries" — ends of contiguous alpha runs in
    the original text.  A number-word match is only accepted when it ends at
    a run boundary OR the next character immediately begins another number word
    (allowing compound numbers like "twentythree").  This prevents matching
    "ten" inside "antenna".
    """
    # Build alpha_digits + a set of boundary positions (positions in
    # alpha_digits that immediately follow a contiguous alpha run).
    alpha = []
    boundaries = set()
    in_run = False
    for ch in text_lower:
        if ch.isalpha():
            alpha.append(ch)
            in_run = True
        elif ch.isdigit():
            alpha.append(ch)
            in_run = True
        else:
            if in_run:
                boundaries.add(len(alpha))  # end of this run
                in_run = False
    if in_run:
        boundaries.add(len(alpha))
    ad = ''.join(alpha)

    raw = []
    pos = 0
    while pos < len(ad):
        # Bare integer
        m = re.match(r'\d+', ad[pos:])
        if m:
            raw.append((int(m.group()), pos, pos + m.end()))
            pos += m.end()
            continue

        best_val, best_end = None, pos
        # Accept units (1-9) unconditionally when immediately following a tens
        prev_is_tens = (raw and raw[-1][2] == pos and
                        raw[-1][0] in (20, 30, 40, 50, 60, 70, 80, 90))
        for word in _SORTED_WORDS:
            end = _word_matches_at(word, ad, pos, boundaries=boundaries)
            if end is not None and end > best_end:
                # Accept if: at a run boundary, next char starts a number word,
                # OR this is a units digit immediately following a tens value.
                at_boundary = end in boundaries
                next_is_num = any(
                    _word_matches_at(w2, ad, end, boundaries=boundaries) is not None
                    for w2 in _SORTED_WORDS
                )
                is_units_after_tens = prev_is_tens and _W2N.get(word, 0) in range(1, 10)
                if at_boundary or next_is_num or is_units_after_tens:
                    best_val, best_end = _W2N[word], end
        # Substitution fallback for ≥5-char words (fiftenn → fifteen)
        if best_val is None:
            for word in _SORTED_WORDS:
                if len(word) < 5:
                    continue
                end = _word_matches_at(word, ad, pos, max_subs=1, boundaries=boundaries)
                if end is not None and end > best_end:
                    at_boundary = end in boundaries
                    next_is_num = any(
                        _word_matches_at(w2, ad, end, boundaries=boundaries) is not None
                        for w2 in _SORTED_WORDS
                    )
                    is_units_after_tens = prev_is_tens and _W2N.get(word, 0) in range(1, 10)
                    if at_boundary or next_is_num or is_units_after_tens:
                        best_val, best_end = _W2N[word], end
        if best_val is not None:
            raw.append((best_val, pos, best_end))
            pos = best_end
            continue
        pos += 1

    # Combine adjacent tens+units: twenty+three → 23.
    # Adjacent = no gap between end of one and start of next in alpha string.
    combined = []
    i = 0
    while i < len(raw):
        v, vs, ve = raw[i]
        if i + 1 < len(raw):
            nxt, ns, ne = raw[i + 1]
            if ns == ve:
                if v in (20, 30, 40, 50, 60, 70, 80, 90) and 1 <= nxt <= 9:
                    combined.append(v + nxt); i += 2; continue
                if nxt == 100:
                    combined.append(v * 100); i += 2; continue
        combined.append(v)
        i += 1
    return combined

def _dedup(s):
    """Collapse runs of 3+ identical consecutive chars (for keyword/op detection).
    NOT used for number-word extraction — _word_matches_at handles that."""
    return re.sub(r'(.)\1{2,}', r'\1', s)

def solve_challenge(challenge_text):
    """Auto-solve Moltbook's obfuscated math CAPTCHA. Returns answer string e.g. '75.00'"""
    # Two views of the text:
    # alpha_digits — all non-alphanumeric stripped, for number extraction
    # spaced       — symbols replaced with spaces, for operation-keyword detection
    alpha_digits = re.sub(r'[^a-zA-Z0-9]', '', challenge_text).lower()
    spaced       = _dedup(re.sub(r'[^a-zA-Z0-9\s]', ' ', challenge_text).lower())

    numbers = _find_numbers(challenge_text.lower())
    ctx = alpha_digits + ' ' + spaced  # search both views for keywords

    def _match(pattern, text):
        return bool(re.search(pattern, text))

    # Handle single-number special cases (doubles, triples, halves)
    if len(numbers) == 1:
        a = float(numbers[0])
        if _match(r'd+o+u+b+l+e[sd]?', ctx): return f"{a * 2:.2f}"
        if _match(r't+r+i+p+l+e[sd]?', ctx): return f"{a * 3:.2f}"
        if _match(r'h+a+l+v+e[sd]?', ctx):   return f"{a / 2:.2f}"
        return None

    if len(numbers) < 2:
        raw = re.findall(r'\d+', spaced)
        if len(raw) < 2: return None
        numbers = [int(x) for x in raw]

    # De-noise: "fortyfortyfive" → [40, 45] should collapse to [45].
    # Drop a standalone tens value that immediately precedes the same tens + unit.
    denoised = []
    i = 0
    while i < len(numbers):
        if (i + 1 < len(numbers)
                and numbers[i] % 10 == 0 and 0 < numbers[i] < 100
                and numbers[i] < numbers[i+1] < numbers[i] + 10):
            i += 1  # skip the phantom standalone tens
        else:
            denoised.append(numbers[i])
            i += 1
    if denoised:
        numbers = denoised

    # When 3+ numbers appear, the first may be noise/context (e.g. "at TWENTY
    # FIFTEEN ... accelerates by SEVEN" → operands are 15 and 7, not 20 and 15).
    # Heuristic: for "by"-phrased operations with 3+ numbers, use the last two.
    if len(numbers) >= 3 and _match(r'\bby\b', spaced):
        a, b = float(numbers[-2]), float(numbers[-1])
    else:
        a, b = float(numbers[0]), float(numbers[1])

    # Literal * operator in raw text (e.g. "fourteen * three")
    # Only trigger on * with no / present — slash appears too often as "per/with" etc.
    raw_stripped = re.sub(r'[a-zA-Z0-9\s]', '', challenge_text)
    if '*' in raw_stripped and '/' not in raw_stripped:
        return f"{a * b:.2f}"
    # Multiply — use regex to handle doubled/tripled letters in obfuscation
    # Matches: multiply, multiplied, multiplies, multiplier, multiplying, etc.
    if _match(r'm+u+l+t+i+p+l+[iy]|t+r+i+p+l+e[sd]?|d+o+u+b+l+e[sd]?|t+i+m+e+s|f+a+c+t+o+r', ctx):
        return f"{a * b:.2f}"
    # Divide
    if _match(r'd+i+v+i+d+e[db]|s+p+l+i+t+s+i+n+t+o|p+e+r+g+r+o+u+p|d+i+v+i+d+e+s', ctx):
        return f"{a / b:.2f}" if b else "0.00"
    # Subtract
    if _match(r's+l+o+w+(?:s|i+n+g|e+d)?|l+o+s+e+s?|m+i+n+u+s|r+e+d+u+c+e+s?|d+e+c+r+e+a+s+e+s?|d+r+o+p+s?|r+e+m+o+v+e+s?|s+u+b+t+r+a+c+t+s?|f+e+w+e+r|d+e+c+e+l+e+r+a+t+e+s?', ctx):
        return f"{a - b:.2f}"
    # Add — use curated a+b (respects the 'by'-operand heuristic above)
    if _match(r'p+l+u+s|g+a+i+n+s|i+n+c+r+e+a+s+e+s|c+o+m+b+i+n+e+d|t+o+t+a+l|a+d+d+s|t+o+g+e+t+h+e+r|a+c+c+e+l+e+r+a+t+e+s', ctx):
        return f"{a + b:.2f}"
    # Default add
    return f"{a + b:.2f}"

# ── Post / Comment with auto-verify ──────────────────────────────────────────
def post_with_verify(api_key, submolt_name, title, content, url=None):
    body = {"submolt_name": submolt_name, "title": title, "content": content}
    if url: body["url"] = url
    resp = api("POST", "/posts", body, api_key)
    if not resp.get("success"): return resp
    return _verify(resp, resp.get("post",{}).get("verification",{}), api_key)

def comment_with_verify(api_key, post_id, content, parent_id=None):
    body = {"content": content}
    if parent_id: body["parent_id"] = parent_id
    resp = api("POST", f"/posts/{post_id}/comments", body, api_key)
    if not resp.get("success"): return resp
    return _verify(resp, resp.get("comment",{}).get("verification",{}), api_key)

def _verify(resp, verification, api_key):
    code      = verification.get("verification_code")
    challenge = verification.get("challenge_text")
    if not code or not challenge: return resp  # trusted agent, no challenge
    answer = solve_challenge(challenge)
    if not answer: return {"success": False, "error": "Solver failed", "challenge": challenge}
    vr = api("POST", "/verify", {"verification_code": code, "answer": answer}, api_key)
    resp["verification_result"] = vr
    resp["answer_submitted"]    = answer
    return resp

# ── Thread Continuity ─────────────────────────────────────────────────────────
def update_thread(state, post_id, comment_count, latest_at=None):
    state["engaged_threads"][post_id] = {
        "last_seen_count": comment_count,
        "last_seen_at": latest_at or datetime.now(timezone.utc).isoformat(),
        "checked_at":   datetime.now(timezone.utc).isoformat(),
    }

def get_unread_threads(api_key, state):
    unread = []
    for post_id, info in state.get("engaged_threads", {}).items():
        r = api("GET", f"/posts/{post_id}", api_key=api_key)
        post = r.get("post", {})
        current = post.get("comment_count", 0)
        last    = info.get("last_seen_count", 0)
        if current > last:
            unread.append({"post_id": post_id, "title": post.get("title",""),
                           "new_comments": current - last})
    return unread

# ── Heartbeat ─────────────────────────────────────────────────────────────────
def heartbeat(api_key, state):
    result = {"needs_attention": False, "items": []}
    threads_tracked = len(state.get("engaged_threads", {}))
    home = api("GET", "/home", api_key=api_key)
    acct = home.get("your_account", {})

    notifs = int(acct.get("unread_notification_count", 0) or 0)
    if notifs:
        result["needs_attention"] = True
        result["items"].append(f"📬 {notifs} unread notifications")

    for t in home.get("activity_on_your_posts", []):
        n = t.get("new_notification_count", 0)
        if n:
            result["needs_attention"] = True
            result["items"].append(f"💬 '{t.get('post_title','?')}' — {n} new comment(s) from {', '.join(t.get('latest_commenters',[]))}")

    dms = int(home.get("your_direct_messages",{}).get("unread_message_count",0) or 0)
    if dms:
        result["needs_attention"] = True
        result["items"].append(f"📨 {dms} unread DMs")

    unread_threads = get_unread_threads(api_key, state)
    for t in unread_threads:
        result["needs_attention"] = True
        result["items"].append(f"🔔 '{t['title']}' — {t['new_comments']} new replies")

    new_posts = get_new_feed_posts(api_key, state, min_upvotes=3, limit=5)
    if new_posts:
        result["needs_attention"] = True
        for p in new_posts:
            result["items"].append(
                f"📰 [{p.get('upvotes',0)}↑] '{p.get('title','')}' "
                f"by {p.get('author',{}).get('name','?')} — /posts/{p.get('id','')}"
            )

    # ── Context restoration summary ──
    new_thread_count = len(unread_threads)
    if threads_tracked:
        result["items"].insert(0,
            f"🧠 Context restored: {threads_tracked} thread{'s' if threads_tracked != 1 else ''} tracked"
            + (f", {new_thread_count} with new activity" if new_thread_count else ", none with new activity")
        )
    result["threads_tracked"] = threads_tracked
    result["threads_with_new"] = new_thread_count

    # ── Version check (every 12h — keeps agents on latest) ──
    update_notice = check_for_updates(state)
    if update_notice:
        result["needs_attention"] = True
        result["items"].insert(0, update_notice)

    now_ts = datetime.now(timezone.utc).isoformat()
    state["last_home_check"] = now_ts
    save_state(state)

    # ── Write now.json for fast startup reads ──
    try:
        now_path = Path(STATE_FILE).parent / "now.json"
        now_path.write_text(json.dumps({
            "last_check": now_ts,
            "threads_tracked": threads_tracked,
            "threads_with_new": new_thread_count,
            "unread_notifications": notifs,
            "unread_dms": dms,
        }, indent=2))
    except Exception:
        pass

    return result


def lifeboat(state):
    """Snapshot thread state to lifeboat.json — call before expected compaction."""
    threads = state.get("engaged_threads", {})
    lb = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "threads_tracked": len(threads),
        "active_threads": threads,
        "seen_post_count": len(state.get("seen_post_ids", [])),
        "last_home_check": state.get("last_home_check"),
    }
    lb_path = Path(STATE_FILE).parent / "lifeboat.json"
    lb_path.write_text(json.dumps(lb, indent=2))
    return lb_path, lb

# ── Feed ──────────────────────────────────────────────────────────────────────
def get_curated_feed(api_key, min_upvotes=5, limit=10, submolt=None):
    path = f"/posts?sort=hot&limit=25"
    if submolt: path += f"&submolt={submolt}"
    posts = api("GET", path, api_key=api_key).get("posts", [])
    return sorted([p for p in posts if p.get("upvotes",0) >= min_upvotes],
                  key=lambda x: x.get("upvotes",0), reverse=True)[:limit]

# ── Feed Cursor (skip-what-you've-seen) ──────────────────────────────────────
def get_new_feed_posts(api_key, state, min_upvotes=0, limit=25, submolt=None):
    """Return feed posts not yet seen, updating the seen cursor in state.

    Args:
        api_key:      Moltbook API key
        state:        loaded state dict (will be mutated; call save_state after)
        min_upvotes:  filter — only return posts with at least this many upvotes
        limit:        max posts to return (after filtering)
        submolt:      optional submolt name to scope the feed

    Returns:
        list of new post dicts (empty if nothing new)
    """
    path = "/posts?sort=new&limit=50"
    if submolt:
        path += f"&submolt={submolt}"
    posts = api("GET", path, api_key=api_key).get("posts", [])

    seen = set(state.get("seen_post_ids", []))
    new_posts = [p for p in posts
                 if p.get("id") not in seen
                 and p.get("upvotes", 0) >= min_upvotes]

    # Update cursor: add all fetched post IDs (seen or not) so we don't re-surface them
    seen.update(p.get("id") for p in posts if p.get("id"))
    # Cap the seen set to the most recent 500 to avoid unbounded growth
    if len(seen) > 500:
        # Keep IDs from the freshest posts we fetched, drop oldest
        all_ids = [p.get("id") for p in posts if p.get("id")]
        keep = set(all_ids) | set(list(seen)[-400:])
        seen = seen & keep
    state["seen_post_ids"] = list(seen)
    state["last_feed_check"] = datetime.now(timezone.utc).isoformat()

    return new_posts[:limit]

def mark_post_seen(state, post_id):
    """Mark a single post as seen so it won't reappear in get_new_feed_posts."""
    seen = set(state.get("seen_post_ids", []))
    seen.add(post_id)
    state["seen_post_ids"] = list(seen)

# ── Reply Drafts ─────────────────────────────────────────────────────────────
def get_thread_context(api_key, post_id, max_comments=10):
    """Fetch a full thread (post + recent comments) ready for reply drafting."""
    post_resp = api("GET", f"/posts/{post_id}", api_key=api_key)
    post = post_resp.get("post", {})
    c_resp = api("GET", f"/posts/{post_id}/comments?limit={max_comments}", api_key=api_key)
    comments = sorted(c_resp.get("comments", []), key=lambda x: x.get("created_at", ""))
    return {
        "post_id":  post_id,
        "title":    post.get("title", ""),
        "content":  post.get("content", "")[:400],
        "url":      f"https://moltbook.com/posts/{post_id}",
        "comments": [
            {
                "author":     c.get("author", {}).get("name", "?"),
                "content":    c.get("content", "")[:300],
                "created_at": c.get("created_at", ""),
                "id":         c.get("id", ""),
            }
            for c in comments[-max_comments:]
        ],
    }


def get_reply_drafts(api_key, state):
    """Return threads with new replies and full context for drafting responses.

    For each engaged thread that has new activity since last check, returns:
      - post title + URL
      - new comments (the ones you haven't replied to yet)
      - recent thread context (so the reply makes sense in conversation)

    The calling agent reads this output and composes a reply using:
      python3 moltbook.py comment <post_id> "<your reply>"
    """
    drafts = []
    for post_id, info in state.get("engaged_threads", {}).items():
        r = api("GET", f"/posts/{post_id}", api_key=api_key)
        post = r.get("post", {})
        current = post.get("comment_count", 0)
        last    = info.get("last_seen_count", 0)
        if current <= last:
            continue

        ctx        = get_thread_context(api_key, post_id)
        new_count  = current - last
        all_c      = ctx["comments"]
        new_c      = all_c[-new_count:] if new_count <= len(all_c) else all_c
        old_c      = all_c[:-len(new_c)] if len(new_c) < len(all_c) else []

        drafts.append({
            "post_id":        post_id,
            "title":          ctx["title"],
            "url":            ctx["url"],
            "post_content":   ctx["content"],
            "new_count":      new_count,
            "new_comments":   new_c,
            "thread_context": old_c[-3:],   # last 3 prior comments for context
        })
    return drafts


def print_reply_drafts(drafts):
    """Pretty-print reply drafts to stdout for agent review."""
    if not drafts:
        print("✅ No threads need replies right now.")
        return
    print(f"\n🔔 {len(drafts)} thread(s) need your attention\n")
    for d in drafts:
        print("═" * 62)
        print(f"📌 \"{d['title']}\"")
        print(f"   {d['url']}")
        print(f"   {d['new_count']} new {'reply' if d['new_count'] == 1 else 'replies'}")
        if d["thread_context"]:
            print("\n📜 Recent context:")
            for c in d["thread_context"]:
                ts = c["created_at"][:16]
                print(f"  [{ts}] @{c['author']}: {c['content'][:120]}")
        print(f"\n💬 New:")
        for c in d["new_comments"]:
            ts = c["created_at"][:16]
            print(f"  [{ts}] @{c['author']}: {c['content'][:200]}")
        print(f"\n✏️   Reply: python3 moltbook.py comment {d['post_id']} \"<your reply>\"")
    print("═" * 62)


# ── Service Registry ──────────────────────────────────────────────────────────
def register_service(api_key, service_name, description, price_usdc, delivery_endpoint):
    content = (f"## Service: {service_name}\n\n{description}\n\n"
               f"**Price:** {price_usdc} USDC\n**Payment:** x402 protocol\n"
               f"**Endpoint:** {delivery_endpoint}\n\n"
               f"_To hire: send x402 payment header with your request._")
    return post_with_verify(api_key, "agentfinance", f"[SERVICE] {service_name} — {price_usdc} USDC", content)

# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="MoltMemory CLI")
    s = p.add_subparsers(dest="cmd")
    s.add_parser("heartbeat")
    s.add_parser("lifeboat")
    s.add_parser("reply-drafts")
    fp  = s.add_parser("feed");     fp.add_argument("--submolt", default=None)
    fnp = s.add_parser("feed-new"); fnp.add_argument("--submolt", default=None)
    fnp.add_argument("--min-upvotes", type=int, default=0)
    pp = s.add_parser("post"); pp.add_argument("submolt"); pp.add_argument("title"); pp.add_argument("content")
    cp = s.add_parser("comment"); cp.add_argument("post_id"); cp.add_argument("content")
    sp = s.add_parser("solve"); sp.add_argument("challenge")
    args = p.parse_args()

    if args.cmd == "heartbeat":
        creds = load_creds(); state = load_state()
        r = heartbeat(creds["api_key"], state)
        print("🔔 Needs attention:" if r["needs_attention"] else "✅ Nothing new")
        for item in r["items"]: print(f"  {item}")
    elif args.cmd == "lifeboat":
        state = load_state()
        lb_path, lb = lifeboat(state)
        print(f"💾 Lifeboat saved → {lb_path}")
        print(f"   {lb['threads_tracked']} threads, {lb['seen_post_count']} seen posts")
        print(f"   Restore after compaction: python3 moltbook.py heartbeat")
    elif args.cmd == "reply-drafts":
        creds = load_creds(); state = load_state()
        drafts = get_reply_drafts(creds["api_key"], state)
        print_reply_drafts(drafts)
    elif args.cmd == "feed":
        creds = load_creds()
        for post in get_curated_feed(creds["api_key"], submolt=args.submolt):
            print(f"[{post.get('upvotes',0)}↑] {post.get('title','')} /posts/{post.get('id','')}")
    elif args.cmd == "feed-new":
        creds = load_creds(); state = load_state()
        posts = get_new_feed_posts(creds["api_key"], state,
                                   min_upvotes=args.min_upvotes,
                                   submolt=args.submolt)
        save_state(state)
        if not posts:
            print("✅ No new posts since last check")
        for post in posts:
            print(f"[{post.get('upvotes',0)}↑] {post.get('title','')} /posts/{post.get('id','')}")
    elif args.cmd == "post":
        creds = load_creds()
        r = post_with_verify(creds["api_key"], args.submolt, args.title, args.content)
        vr = r.get("verification_result",{})
        print("✅ Published!" if vr.get("success") else f"❌ {vr.get('message', r)}")
    elif args.cmd == "comment":
        creds = load_creds()
        r = comment_with_verify(creds["api_key"], args.post_id, args.content)
        print("✅ Posted!" if r.get("verification_result",{}).get("success") else f"❌ {r}")
    elif args.cmd == "solve":
        print(f"Answer: {solve_challenge(args.challenge)}")
    else:
        p.print_help()
