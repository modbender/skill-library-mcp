#!/usr/bin/env python3
"""
Moltbook posting tool with LLM-powered verification solver.
Handles the obfuscated lobster math challenges reliably.

Usage:
  # Post:
  python3 moltbook-post.py post --title "My Title" --content "Post body"
  python3 moltbook-post.py post --file /path/to/post.json
  
  # Comment:
  python3 moltbook-post.py comment --post-id <id> --content "Comment text"
  
  # Upvote:
  python3 moltbook-post.py upvote --post-id <id>
  python3 moltbook-post.py upvote --comment-id <id>

Requires: MOLTBOOK_TOKEN and OPENAI_API_KEY env vars (or reads from OpenClaw config)
"""

import json, urllib.request, os, sys, argparse, time, re, socket
from pathlib import Path

# --- Config ---
API = "https://www.moltbook.com/api/v1"
# Paths - resolve relative to workspace root or script directory
def _detect_workspace():
    """Detect workspace root. Handles running from tools/ or clawhub-skills/*/scripts/."""
    env_ws = os.environ.get("OPENCLAW_WORKSPACE")
    if env_ws:
        return env_ws
    # Walk up from script location looking for .secrets-cache.json or AGENTS.md
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(6):
        if os.path.exists(os.path.join(d, ".secrets-cache.json")) or os.path.exists(os.path.join(d, "AGENTS.md")):
            return d
        d = os.path.dirname(d)
    # Fallback: grandparent of script
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_WORKSPACE = _detect_workspace()
DEDUP_LOG_PATH = os.path.join(_WORKSPACE, "memory", "moltbook-dedup.json")
PERMANENT_DEDUP_PATH = os.path.join(_WORKSPACE, "memory", "moltbook-permanent-dedup.json")
DEDUP_TTL_DAYS = 7

# --- Identity Config ---
# Set MOLTBOOK_USERNAME env var or add identifiers to moltbook-identity.json
# Default: detected from API or hardcoded fallback
_IDENTITY_CACHE = None
def _load_my_identifiers():
    """Load the set of usernames/display names that identify this agent on Moltbook."""
    global _IDENTITY_CACHE
    if _IDENTITY_CACHE is not None:
        return _IDENTITY_CACHE
    
    identifiers = set()
    
    # 1. Environment variable
    env_user = os.environ.get("MOLTBOOK_USERNAME")
    if env_user:
        identifiers.add(env_user)
    
    # 2. Identity config file (skill directory or workspace)
    for path in [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "moltbook-identity.json"),
        os.path.join(_WORKSPACE, "moltbook-identity.json"),
    ]:
        if os.path.exists(path):
            try:
                with open(path) as f:
                    data = json.load(f)
                    for name in data.get("identifiers", []):
                        identifiers.add(name)
            except: pass
    
    # 3. Fallback defaults
    if not identifiers:
        identifiers = {"real-yoder-og-bot", "Yoder", "yoder"}
    
    _IDENTITY_CACHE = identifiers
    return identifiers

# --- Post Auto-Registration ---
def _auto_register_post(post_id, title, submolt="general"):
    """Auto-register a new post in the post-tracker.json if it exists."""
    tracker_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "post-tracker.json")
    if not os.path.exists(tracker_path):
        return
    try:
        with open(tracker_path) as f:
            tracker = json.load(f)
        # Check if already tracked
        for p in tracker.get("posts", []):
            if p.get("id") == post_id:
                return  # Already tracked
        tracker.setdefault("posts", []).append({
            "id": post_id,
            "title": title,
            "format": "unknown",
            "submolt": submolt,
            "posted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "upvotes": 0,
            "comments": 0,
            "our_replies": 0,
            "notes": "Auto-registered on creation"
        })
        with open(tracker_path, 'w') as f:
            json.dump(tracker, f, indent=2)
        print(f"  📊 Auto-registered in post-tracker.json")
    except Exception as e:
        print(f"  ⚠️  Auto-register failed: {e}", file=sys.stderr)

# Secret loading - tries multiple sources
def get_secret(name, required=True):
    """Load secret from env, .secrets-cache.json, or OpenClaw auth profiles."""
    val = os.environ.get(name)
    if val:
        return val
    cache_path = os.path.join(_WORKSPACE, ".secrets-cache.json")
    if os.path.exists(cache_path):
        try:
            with open(cache_path) as f:
                cache = json.load(f)
                if name in cache:
                    return cache[name]
        except: pass
    auth_path = os.path.expanduser("~/.openclaw/agents/main/agent/auth-profiles.json")
    if os.path.exists(auth_path) and name == "OPENAI_API_KEY":
        try:
            with open(auth_path) as f:
                profiles = json.load(f)
                key = profiles.get("profiles", {}).get("openai:default", {}).get("key")
                if key: return key
        except: pass
    if required:
        print(f"Error: {name} not found in env, .secrets-cache.json, or auth profiles", file=sys.stderr)
        sys.exit(1)
    return None

# Lazy-loaded secrets (only fetched when first used)
_secrets_cache = {}
def _get(name, required=True):
    if name not in _secrets_cache:
        _secrets_cache[name] = get_secret(name, required=required)
    return _secrets_cache[name]

def MOLTBOOK_TOKEN(): return _get("MOLTBOOK_TOKEN")
def OPENAI_KEY(): return _get("OPENAI_API_KEY", required=False)

# --- Redis Rate Limiting ---
REDIS_HOST = "10.0.0.120"
REDIS_PORT = 6379
def REDIS_PASSWORD(): return _get("REDIS_PASSWORD", required=False) or ""

# --- Permanent Dedup Layer (never expires) ---
def _load_permanent_dedup():
    """Load permanent dedup set from disk."""
    if os.path.exists(PERMANENT_DEDUP_PATH):
        try:
            with open(PERMANENT_DEDUP_PATH, 'r') as f:
                data = json.load(f)
                return set(data.get("commented_posts", []))
        except:
            return set()
    return set()

def _save_permanent_dedup(post_ids):
    """Save permanent dedup set to disk."""
    try:
        with open(PERMANENT_DEDUP_PATH, 'w') as f:
            json.dump({"commented_posts": sorted(list(post_ids)), "updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, f, indent=2)
    except Exception as e:
        print(f"  ⚠️  Permanent dedup save failed: {e}", file=sys.stderr)

def permanent_check(post_id):
    """Check if we've ever commented on this post. Never expires."""
    known = _load_permanent_dedup()
    return post_id in known

def permanent_mark(post_id):
    """Mark a post as commented on permanently."""
    known = _load_permanent_dedup()
    known.add(post_id)
    _save_permanent_dedup(known)

# --- Deduplication ---
def redis_check_posted(post_id, target_type="post"):
    """
    Check if we already replied/posted to this target using Redis.
    Returns True if already posted (should skip), False otherwise.
    Checks both exact key and prefix match (for threaded replies).
    """
    key = f"moltbook:posted:{target_type}:{post_id}"
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((REDIS_HOST, REDIS_PORT))
        
        def send_cmd(parts):
            data = f"*{len(parts)}\r\n".encode('utf-8')
            for p in parts:
                encoded = str(p).encode('utf-8')
                data += f"${len(encoded)}\r\n".encode('utf-8') + encoded + b"\r\n"
            sock.sendall(data)
        
        def read_line():
            line = b""
            while True:
                byte = sock.recv(1)
                if not byte:
                    break
                if byte == b'\r':
                    next_byte = sock.recv(1)
                    if next_byte == b'\n':
                        break
                    line += byte + next_byte
                else:
                    line += byte
            return line
        
        def read_resp():
            first = sock.recv(1)
            if first == b'+':
                return read_line().decode('utf-8')
            elif first == b':':
                return int(read_line())
            elif first == b'$':
                length = int(read_line())
                if length == -1:
                    return None
                data = sock.recv(length)
                sock.recv(2)  # \r\n
                return data.decode('utf-8')
            elif first == b'-':
                error = read_line().decode('utf-8')
                raise Exception(f"Redis error: {error}")
            return None
        
        # Authenticate
        send_cmd(["AUTH", REDIS_PASSWORD()])
        auth_resp = read_resp()
        if auth_resp != "OK":
            sock.close()
            return False  # Fail open if auth fails
        
        # Check if exact key exists
        send_cmd(["GET", key])
        result = read_resp()
        
        if result is not None:
            sock.close()
            return True
        
        # Also check for prefix matches (catches threaded replies like post_id:comment_id)
        # Use SCAN-like approach: send KEYS and parse the raw response
        prefix_key = f"moltbook:posted:{target_type}:{post_id}:*"
        send_cmd(["KEYS", prefix_key])
        # Read raw response - KEYS returns array (*N\r\n$len\r\nkey\r\n...)
        raw = b""
        try:
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                raw += chunk
                if len(chunk) < 4096:
                    break
        except socket.timeout:
            pass
        sock.close()
        
        # Parse: if response starts with *0, no matches. If *N where N>0, we have matches.
        raw_str = raw.decode('utf-8', errors='ignore')
        if raw_str.startswith('*0'):
            return False
        if raw_str.startswith('*') and not raw_str.startswith('*-1'):
            return True
        
        return False
        
    except Exception as e:
        print(f"  ⚠️  Redis dedup check failed: {e}", file=sys.stderr)
        return False  # Fail open on Redis errors


def redis_mark_posted(post_id, target_type="post", content_preview=""):
    """
    Mark a post as posted in Redis with TTL, and update local dedup log.
    """
    key = f"moltbook:posted:{target_type}:{post_id}"
    ttl_seconds = DEDUP_TTL_DAYS * 24 * 60 * 60  # 7 days
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((REDIS_HOST, REDIS_PORT))
        
        def send_cmd(parts):
            data = f"*{len(parts)}\r\n".encode('utf-8')
            for p in parts:
                encoded = str(p).encode('utf-8')
                data += f"${len(encoded)}\r\n".encode('utf-8') + encoded + b"\r\n"
            sock.sendall(data)
        
        def read_line():
            line = b""
            while True:
                byte = sock.recv(1)
                if not byte:
                    break
                if byte == b'\r':
                    next_byte = sock.recv(1)
                    if next_byte == b'\n':
                        break
                    line += byte + next_byte
                else:
                    line += byte
            return line
        
        def read_resp():
            first = sock.recv(1)
            if first == b'+':
                return read_line().decode('utf-8')
            elif first == b':':
                return int(read_line())
            elif first == b'$':
                length = int(read_line())
                if length == -1:
                    return None
                data = sock.recv(length)
                sock.recv(2)  # \r\n
                return data.decode('utf-8')
            elif first == b'-':
                error = read_line().decode('utf-8')
                raise Exception(f"Redis error: {error}")
            return None
        
        # Authenticate
        send_cmd(["AUTH", REDIS_PASSWORD()])
        auth_resp = read_resp()
        if auth_resp != "OK":
            sock.close()
            return
        
        # Set key with TTL
        send_cmd(["SET", key, "posted", "EX", ttl_seconds])
        read_resp()
        sock.close()
        
    except Exception as e:
        print(f"  ⚠️  Redis mark posted failed: {e}", file=sys.stderr)
    
    # Update local dedup log
    try:
        log_entry = {
            "post_id": post_id,
            "target_type": target_type,
            "timestamp": time.time(),
            "content_preview": content_preview[:100] if content_preview else ""
        }
        
        # Read existing log
        existing = []
        if os.path.exists(DEDUP_LOG_PATH):
            try:
                with open(DEDUP_LOG_PATH, 'r') as f:
                    existing = json.load(f)
            except:
                existing = []
        
        # Append and save
        existing.append(log_entry)
        
        # Keep only last 1000 entries to prevent file bloat
        if len(existing) > 1000:
            existing = existing[-1000:]
        
        with open(DEDUP_LOG_PATH, 'w') as f:
            json.dump(existing, f, indent=2)
            
    except Exception as e:
        print(f"  ⚠️  Dedup log update failed: {e}", file=sys.stderr)


def redis_check_ratelimit(service, action, window=1800, max_requests=1):
    """
    Check if action is allowed under rate limit using Redis.
    Returns (allowed: bool, remaining: int, reset_in: int)
    """
    key = f"ratelimit:{service}:{action}"
    
    try:
        # Connect to Redis
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((REDIS_HOST, REDIS_PORT))
        
        def send_cmd(parts):
            # RESP array encoding
            data = f"*{len(parts)}\r\n".encode('utf-8')
            for p in parts:
                encoded = str(p).encode('utf-8')
                data += f"${len(encoded)}\r\n".encode('utf-8') + encoded + b"\r\n"
            sock.sendall(data)
        
        def read_line():
            line = b""
            while True:
                byte = sock.recv(1)
                if not byte:
                    break
                if byte == b'\r':
                    next_byte = sock.recv(1)
                    if next_byte == b'\n':
                        break
                    line += byte + next_byte
                else:
                    line += byte
            return line
        
        def read_resp():
            first = sock.recv(1)
            if first == b'+':
                return read_line().decode('utf-8')
            elif first == b':':
                return int(read_line())
            elif first == b'$':
                length = int(read_line())
                if length == -1:
                    return None
                data = sock.recv(length)
                sock.recv(2)  # \r\n
                return data.decode('utf-8')
            elif first == b'-':
                error = read_line().decode('utf-8')
                raise Exception(f"Redis error: {error}")
            return None
        
        # Authenticate
        send_cmd(["AUTH", REDIS_PASSWORD()])
        auth_resp = read_resp()
        if auth_resp != "OK":
            sock.close()
            return (True, max_requests, 0)  # Fail open if auth fails
        
        # Check current count
        send_cmd(["GET", key])
        current = read_resp()
        
        if current is None:
            # First request - set counter and expiry
            send_cmd(["SET", key, "1", "EX", window])
            read_resp()
            sock.close()
            return (True, max_requests - 1, window)
        
        count = int(current)
        if count >= max_requests:
            # Rate limited - get remaining TTL
            send_cmd(["TTL", key])
            ttl = int(read_resp())
            sock.close()
            return (False, 0, max(0, ttl))
        
        # Increment counter
        send_cmd(["INCR", key])
        new_count = int(read_resp())
        remaining = max(0, max_requests - new_count)
        
        # Get TTL
        send_cmd(["TTL", key])
        ttl = int(read_resp())
        sock.close()
        
        return (True, remaining, max(0, ttl))
        
    except Exception as e:
        print(f"  ⚠️  Redis rate limit check failed: {e}", file=sys.stderr)
        return (True, max_requests, 0)  # Fail open on Redis errors

# --- HTTP helpers ---
def molt_api(method, path, data=None):
    """Call Moltbook API"""
    url = f"{API}{path}"
    payload = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=payload, method=method,
        headers={"Authorization": f"Bearer {MOLTBOOK_TOKEN()}", "Content-Type": "application/json"})
    try:
        resp = urllib.request.urlopen(req, timeout=20)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        try:
            return json.loads(body)
        except:
            return {"error": f"HTTP {e.code}", "body": body}

def openai_chat(prompt, model="gpt-4o-mini"):
    """Quick OpenAI chat completion"""
    url = "https://api.openai.com/v1/chat/completions"
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": 50
    }).encode()
    req = urllib.request.Request(url, data=payload,
        headers={"Authorization": f"Bearer {OPENAI_KEY()}", "Content-Type": "application/json"})
    resp = urllib.request.urlopen(req, timeout=15)
    result = json.loads(resp.read())
    return result["choices"][0]["message"]["content"].strip()

# --- Verification solver ---
def solve_challenge(challenge):
    """Parse obfuscated lobster math and solve it directly (no API call needed).
    These are always simple: two numbers + one operation (add/subtract/multiply/divide).
    Falls back to LLM only if regex solver returns 0.00."""
    answer = fallback_solve(challenge)
    if answer != "0.00":
        return answer
    # Only use LLM as last resort
    try:
        prompt = f"Obfuscated math challenge about lobsters. Parse the two numbers and operation, respond with ONLY the numeric answer with 2 decimal places.\n\nChallenge: {challenge}\n\nAnswer:"
        llm_answer = openai_chat(prompt)
        match = re.search(r'(\d+\.?\d*)', llm_answer)
        if match:
            return f"{float(match.group(1)):.2f}"
        return llm_answer
    except Exception as e:
        print(f"  LLM fallback also failed: {e}", file=sys.stderr)
        return answer

def fallback_solve(challenge):
    """Fast regex solver for lobster math challenges. No API calls needed.
    Handles: addition, subtraction, multiplication, division, repeats, net force.
    
    Strategy: strip non-alpha, collapse repeated chars, then scan the entire
    cleaned string for number words using a greedy left-to-right regex approach.
    This avoids fragile word-boundary tokenization that breaks on obfuscated text."""
    raw = re.sub(r'[^a-zA-Z\s]', '', challenge).lower()
    # Remove runs of 3+ same char down to 1, but keep doubles (e.g. "ee" in "three")
    clean = re.sub(r'(.)\1{2,}', r'\1', raw)
    # Collapse ALL whitespace so we can substring-match number words
    blob = re.sub(r'\s+', '', clean)
    # Also keep a spaced version for operation keyword detection
    spaced = ' '.join(clean.split())

    # Number words sorted longest first for greedy matching
    number_words = [
        ('seventeen',17),('thirteen',13),('fourteen',14),('fifteen',15),('sixteen',16),
        ('eighteen',18),('nineteen',19),('seventy',70),('twenty',20),('thirty',30),
        ('eighty',80),('twelve',12),('eleven',11),('ninety',90),('eighty',80),
        ('forty',40),('fifty',50),('sixty',60),('seven',7),('eight',8),
        ('three',3),('four',4),('five',5),('nine',9),('ten',10),('six',6),
        ('two',2),('one',1),('zero',0),('hundred',100),
    ]

    # Scan blob for number words left-to-right, recording position and value
    found = []  # list of (position_in_blob, value, matched_word)
    pos = 0
    while pos < len(blob):
        matched = False
        for word, val in number_words:
            if blob[pos:pos+len(word)] == word:
                found.append((pos, val, word))
                pos += len(word)
                matched = True
                break
        if not matched:
            pos += 1

    # Build final numbers: combine tens + ones (e.g. twenty + three = 23)
    numbers = []
    i = 0
    while i < len(found):
        _, val, word = found[i]
        # Compound: tens (20-90) followed immediately by ones (1-9)
        if val in (20,30,40,50,60,70,80,90) and i + 1 < len(found):
            _, next_val, _ = found[i+1]
            if 1 <= next_val <= 9:
                numbers.append(val + next_val)
                i += 2
                continue
        numbers.append(val)
        i += 1

    # Also find any bare digits in the original cleaned text
    for m in re.finditer(r'\b(\d+(?:\.\d+)?)\b', spaced):
        numbers.append(float(m.group(1)))

    # Strip unit phrases for operation detection
    ops_text = re.sub(r'per (second|minute|hour|meter|metre|day|year|cycle)', '', spaced)

    if len(numbers) >= 2:
        a, b = numbers[0], numbers[1]
        if any(w in ops_text for w in ['repeat', 'times', 'multipli', 'product']):
            return f"{a*b:.2f}"
        elif any(w in ops_text for w in ['net force', 'remain', 'reduc', 'left', 'minus', 'loses', 'subtract', 'decrease', 'less', 'decelerat']):
            return f"{a-b:.2f}"
        elif any(w in ops_text for w in ['divide', 'split', 'each get']):
            if b != 0:
                return f"{a/b:.2f}"
            return "0.00"
        else:
            return f"{a+b:.2f}"
    elif len(numbers) == 1:
        return f"{numbers[0]:.2f}"
    return "0.00"

# --- Core actions ---
def verify_content(code, challenge, max_retries=2):
    """Solve challenge and verify, with retries"""
    for attempt in range(max_retries + 1):
        answer = solve_challenge(challenge)
        print(f"  Challenge: {challenge[:80]}...")
        print(f"  Answer: {answer}")
        
        result = molt_api("POST", "/verify", {"verification_code": code, "answer": answer})
        if result.get("success"):
            print(f"  ✅ Verified and published!")
            return True
        
        err = result.get("error", "")
        print(f"  ❌ {err}")
        
        if "expired" in err.lower() or "invalid verification" in err.lower():
            print("  Code expired, need fresh submission")
            return False
    
    return False

def post(title, content, submolt="general", max_attempts=1):
    """Create a post with verification.
    
    CRITICAL: max_attempts is ALWAYS 1 for posts. The Moltbook API creates the post
    on POST, BEFORE verification. If we retry the POST, we create a DUPLICATE post.
    Never retry the POST. One shot, one post.
    """
    print(f"Posting '{title[:50]}...'")
    result = molt_api("POST", "/posts", {"title": title, "content": content, "submolt": submolt})
    
    if not result.get("success"):
        print(f"  Error: {result}")
        return result
    
    post_id = result.get("post", {}).get("id", "")
    v = result.get("verification", {})
    
    if not v.get("code"):
        # No verification needed (trusted account)
        print(f"  ✅ Published directly! Post ID: {post_id}")
        _auto_register_post(post_id, title, submolt)
        return {"success": True, "post_id": post_id}
    
    if verify_content(v["code"], v["challenge"]):
        print(f"  ✅ Post verified and published! ID: {post_id}")
        _auto_register_post(post_id, title, submolt)
        return {"success": True, "post_id": post_id}
    
    # Verification failed, but the post IS on the server.
    # Do NOT retry - that would create a duplicate.
    print(f"  ⚠️  Verification failed but post {post_id} exists on server. NOT retrying to avoid duplicate.")
    _auto_register_post(post_id, title, submolt)
    return {"success": False, "error": "Verification failed (post exists, not retrying)", "post_id": post_id, "unverified": True}

def check_already_commented_on_post(post_id):
    """
    Check ACTUAL Moltbook API to see if we already have comments on this post.
    This is the ground-truth dedup check - prevents duplicates even when Redis/local state is stale.
    Checks multiple user field formats since the API is inconsistent.
    """
    try:
        result = molt_api("GET", f"/posts/{post_id}/comments?limit=100")
        comments = []
        if isinstance(result, dict) and result.get("comments"):
            comments = result["comments"]
        elif isinstance(result, list):
            comments = result
        
        my_identifiers = _load_my_identifiers()
        for c in comments:
            # Check all possible user field locations
            user = c.get("user", c.get("author", {}))
            if isinstance(user, dict):
                username = user.get("username", user.get("name", ""))
                display = user.get("display_name", "")
                uid = user.get("id", "")
                if username in my_identifiers or display in my_identifiers:
                    print(f"  ⚠️  GROUND TRUTH: Already have comment(s) on this post (matched: {username or display}). Blocking duplicate.")
                    return True
            # Also check top-level author field
            author_str = c.get("author", "")
            if isinstance(author_str, str) and author_str in my_identifiers:
                print(f"  ⚠️  GROUND TRUTH: Already have comment(s) on this post (matched author: {author_str}). Blocking duplicate.")
                return True
    except Exception as e:
        print(f"  ⚠️  Ground truth check failed (proceeding cautiously): {e}", file=sys.stderr)
    return False


def comment(post_id, content, parent_id=None, max_attempts=1, dry_run=False):
    """Post a comment with verification. Use parent_id to reply to a specific comment.
    
    CRITICAL: max_attempts is ALWAYS 1 for comments. The Moltbook API creates the comment
    on POST, BEFORE verification. If we retry the POST, we create a DUPLICATE comment.
    Verification failure means the comment exists but may be unverified - it still shows up.
    Never retry the POST. One shot, one comment.
    """
    # LAYER 0: Permanent dedup (never expires, survives Redis TTL)
    # For threaded replies (parent_id set), check post_id:parent_id combo
    # For top-level comments, check just post_id
    perm_key = f"{post_id}:{parent_id}" if parent_id else post_id
    if permanent_check(perm_key):
        print(f"  ⚠️  Already commented on this target (permanent record). Skipping.")
        return {"success": False, "error": "Already commented on this target (permanent)", "duplicate": True}
    
    # LAYER 1: Redis dedup (7-day TTL, fast check)
    target_id = f"{post_id}:{parent_id}" if parent_id else post_id
    if redis_check_posted(target_id, "comment"):
        print(f"  ⚠️  Already replied to this post/thread (Redis). Skipping.")
        permanent_mark(perm_key)  # Backfill permanent record
        return {"success": False, "error": "Already posted to this target", "duplicate": True}
    
    # LAYER 2: API ground truth (checks actual Moltbook for our comments)
    if check_already_commented_on_post(post_id):
        redis_mark_posted(target_id, "comment", "[retroactive dedup]")
        permanent_mark(perm_key)  # Backfill permanent record
        return {"success": False, "error": "Already have comments on this post (API check)", "duplicate": True}
    
    # Dry run mode - just log what would happen
    if dry_run:
        print(f"  🧪 DRY RUN: Would comment on post {post_id[:12]}...")
        print(f"     Content: {content[:60]}...")
        return {"success": True, "dry_run": True, "post_id": post_id}
    
    # === SINGLE ATTEMPT ONLY ===
    # The Moltbook API creates the comment on POST, before verification.
    # If we POST twice, we get TWO comments. NEVER retry the POST.
    # If verification fails, the comment still exists - we mark dedup and move on.
    
    target = f"comment {parent_id[:12]}" if parent_id else f"post {post_id[:12]}"
    print(f"Posting reply to {target}...")
    payload = {"content": content}
    if parent_id:
        payload["parent_id"] = parent_id
    result = molt_api("POST", f"/posts/{post_id}/comments", payload)
    
    if not result.get("success"):
        print(f"  Error: {result}")
        return result
    
    comment_id = result.get("comment", {}).get("id", "")
    v = result.get("verification", {})
    
    # IMMEDIATELY mark dedup BEFORE verification attempt.
    # The comment already exists on the server at this point.
    # Even if verification fails, the comment is visible.
    redis_mark_posted(target_id, "comment", content)
    permanent_mark(perm_key)
    
    if not v.get("code"):
        # No verification needed (trusted account)
        print(f"  ✅ Published directly! Comment ID: {comment_id}")
        return {"success": True, "comment_id": comment_id}
    
    if verify_content(v["code"], v["challenge"]):
        print(f"  ✅ Comment verified and published! ID: {comment_id}")
        return {"success": True, "comment_id": comment_id}
    
    # Verification failed, but the comment IS on the server (visible as unverified).
    # We already marked dedup. Do NOT retry - that would create a duplicate.
    print(f"  ⚠️  Verification failed but comment {comment_id} exists on server. NOT retrying to avoid duplicate.")
    print(f"  ⚠️  Dedup marked. Comment may be visible as unverified.")
    return {"success": False, "error": "Verification failed (comment exists, dedup marked)", "comment_id": comment_id, "unverified": True}

def upvote(post_id=None, comment_id=None):
    """Upvote a post or comment"""
    if post_id:
        result = molt_api("POST", f"/posts/{post_id}/upvote", {})
    elif comment_id:
        result = molt_api("POST", f"/comments/{comment_id}/upvote", {})
    else:
        return {"error": "Need post_id or comment_id"}
    print(f"  Upvote: {result}")
    return result


def follow(agent_name):
    """Follow an agent on Moltbook."""
    result = molt_api("POST", f"/agents/{agent_name}/follow", {})
    print(f"  Follow {agent_name}: {result}")
    return result


def unfollow(agent_name):
    """Unfollow an agent on Moltbook."""
    result = molt_api("DELETE", f"/agents/{agent_name}/follow")
    print(f"  Unfollow {agent_name}: {result}")
    return result


def profile(agent_name=None):
    """Get agent profile. If no name given, gets own profile."""
    if agent_name:
        result = molt_api("GET", f"/agents/{agent_name}")
    else:
        result = molt_api("GET", "/agents/me")
    return result


# --- CLI ---
def main():
    parser = argparse.ArgumentParser(description="Moltbook posting tool")
    sub = parser.add_subparsers(dest="action")
    
    p_post = sub.add_parser("post", help="Create a post")
    p_post.add_argument("--title", required=False)
    p_post.add_argument("--content", required=False)
    p_post.add_argument("--file", help="JSON file with title/content/submolt")
    p_post.add_argument("--submolt", default="general")
    
    p_comment = sub.add_parser("comment", help="Post a comment")
    p_comment.add_argument("--post-id", required=True)
    p_comment.add_argument("--content", required=True)
    p_comment.add_argument("--parent-id", help="Reply to a specific comment (threaded reply)")
    p_comment.add_argument("--dry-run", action="store_true", help="Simulate without actually posting")
    
    p_check = sub.add_parser("check", help="Check if already commented on a post")
    p_check.add_argument("--post-id", required=True)
    
    p_upvote = sub.add_parser("upvote", help="Upvote content")
    p_upvote.add_argument("--post-id")
    p_upvote.add_argument("--comment-id")
    
    p_follow = sub.add_parser("follow", help="Follow an agent")
    p_follow.add_argument("--name", required=True, help="Agent name to follow")
    
    p_unfollow = sub.add_parser("unfollow", help="Unfollow an agent")
    p_unfollow.add_argument("--name", required=True, help="Agent name to unfollow")
    
    p_profile = sub.add_parser("profile", help="Get agent profile")
    p_profile.add_argument("--name", help="Agent name (omit for own profile)")
    
    args = parser.parse_args()
    
    if args.action == "post":
        if args.file:
            with open(args.file) as f:
                data = json.load(f)
            title = data["title"]
            content = data["content"]
            submolt = data.get("submolt", args.submolt)
        elif args.title and args.content:
            title = args.title
            content = args.content
            submolt = args.submolt
        else:
            print("Need --title and --content, or --file")
            sys.exit(1)
        
        result = post(title, content, submolt)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result.get("success") else 1)
    
    elif args.action == "comment":
        result = comment(args.post_id, args.content, parent_id=getattr(args, 'parent_id', None), dry_run=args.dry_run)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result.get("success") else 1)
    
    elif args.action == "check":
        perm = permanent_check(args.post_id)
        redis_already = redis_check_posted(args.post_id, "comment")
        api_check = check_already_commented_on_post(args.post_id)
        blocked = perm or redis_already or api_check
        result = {
            "already_commented": blocked,
            "post_id": args.post_id,
            "permanent": perm,
            "redis": redis_already,
            "api": api_check
        }
        # Backfill permanent record if found via other layers
        if (redis_already or api_check) and not perm:
            permanent_mark(args.post_id)
            result["backfilled_permanent"] = True
        print(json.dumps(result))
        sys.exit(1 if blocked else 0)
    
    elif args.action == "upvote":
        result = upvote(args.post_id, args.comment_id)
        sys.exit(0 if result.get("success") else 1)
    
    elif args.action == "follow":
        result = follow(args.name)
        sys.exit(0 if result.get("success") else 1)
    
    elif args.action == "unfollow":
        result = unfollow(args.name)
        sys.exit(0 if result.get("success") else 1)
    
    elif args.action == "profile":
        result = profile(args.name)
        print(json.dumps(result, indent=2))
        sys.exit(0)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
