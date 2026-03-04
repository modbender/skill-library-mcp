"""
UnderSheet — Moltbook platform adapter.
Ports the MoltMemory skill into the UnderSheet adapter model.
Credentials: ~/.config/moltbook/credentials.json
  { "api_key": "...", "agent_name": "..." }
"""

import json
import os
import re
import time
import urllib.request
import urllib.parse
import urllib.error
from undersheet import PlatformAdapter

MOLTBOOK_API = "https://www.moltbook.com/api/v1"
CREDS_PATH = os.path.expanduser("~/.config/moltbook/credentials.json")


def _load_creds() -> dict:
    if not os.path.exists(CREDS_PATH):
        raise FileNotFoundError(f"Moltbook credentials not found at {CREDS_PATH}")
    with open(CREDS_PATH) as f:
        return json.load(f)


def _api(method: str, path: str, body: dict = None, api_key: str = None) -> dict:
    url = MOLTBOOK_API + path
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode())
    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------------------------------
# CAPTCHA solver (ported from MoltMemory v1.2)
# ---------------------------------------------------------------------------

def _word_matches_at(word: str, text: str, pos: int, max_subs: int = 0) -> int:
    """Match word chars against obfuscated text. Returns end pos or -1."""
    i, subs_used = pos, 0
    for wi, wc in enumerate(word):
        if i >= len(text):
            return -1
        if text[i] != wc:
            if max_subs > 0 and subs_used < max_subs:
                subs_used += 1
                # skip one char in text that doesn't match
                while i < len(text) and text[i] != (word[wi] if wi < len(word) else ''):
                    i += 1
                    if i < len(text) and text[i] == wc:
                        break
                if i >= len(text) or text[i] != wc:
                    return -1
            else:
                return -1
        # consume duplicates
        next_wc = word[wi + 1] if wi + 1 < len(word) else None
        i += 1
        while i < len(text) and text[i] == wc and (next_wc is None or wc != next_wc):
            i += 1
    return i


def _find_numbers(text_lower: str) -> list[str]:
    words = {
        "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
        "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
        "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
        "nineteen": 19, "twenty": 20, "twenny": 20,
        "thirty": 30, "forty": 40, "fourty": 40, "fifty": 50,
        "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
        "hundred": 100,
    }
    alpha = re.sub(r'[^a-z]', '', text_lower)
    results, i = [], 0
    while i < len(alpha):
        matched = False
        for word, val in sorted(words.items(), key=lambda x: -len(x[0])):
            end = _word_matches_at(word, alpha, i)
            if end == -1 and len(word) >= 5:
                end = _word_matches_at(word, alpha, i, max_subs=1)
            if end != -1:
                results.append((i, end, val))
                i = end
                matched = True
                break
        if not matched:
            i += 1

    if not results:
        return []

    # Compound tens+units
    combined, skip = [], set()
    for idx, (start, end, val) in enumerate(results):
        if idx in skip:
            continue
        if idx + 1 < len(results):
            nstart, nend, nval = results[idx + 1]
            if nstart == end and val in (20, 30, 40, 50, 60, 70, 80, 90) and 1 <= nval <= 9:
                combined.append(str(val + nval))
                skip.add(idx + 1)
                continue
        combined.append(str(val))
    return combined


def solve_challenge(challenge_text: str) -> str:
    text_lower = challenge_text.lower()
    spaced = re.sub(r'[^a-z0-9]', ' ', text_lower)

    def _match(pattern, t):
        return bool(re.search(pattern, t))

    numbers = _find_numbers(text_lower)
    if not numbers:
        return "0.00"

    if len(numbers) >= 3 and _match(r'\bby\b', spaced):
        a, b = float(numbers[-2]), float(numbers[-1])
    elif len(numbers) >= 2:
        a, b = float(numbers[0]), float(numbers[1])
    else:
        a, b = float(numbers[0]), 0.0

    if _match(r'm+u+l+t+i+p+l+[iy]|t+i+m+e+s|p+r+o+d+u+c+t', spaced):
        result = a * b
    elif _match(r'd+i+v+i+d+e+|p+e+r\b|r+a+t+i+o', spaced):
        result = a / b if b != 0 else 0.0
    elif _match(r's+u+b+t+r+a+c+t|m+i+n+u+s|d+i+f+f+e+r+e+n+c+e|l+e+s+s', spaced):
        result = a - b
    else:
        result = a + b

    return f"{result:.2f}"


def _verify_and_retry(api_key: str, post_id: str, content: str, parent_id: str = None) -> dict:
    body = {"content": content}
    if parent_id:
        body["parent_id"] = parent_id
    resp = _api("POST", f"/posts/{post_id}/comments", body, api_key)
    if resp.get("verification"):
        answer = solve_challenge(resp["verification"].get("challenge", ""))
        body["verification_answer"] = answer
        resp = _api("POST", f"/posts/{post_id}/comments", body, api_key)
    return resp


# ---------------------------------------------------------------------------
# Adapter
# ---------------------------------------------------------------------------

class Adapter(PlatformAdapter):
    name = "moltbook"

    def __init__(self):
        self._creds = _load_creds()
        self._api_key = self._creds["api_key"]

    def get_credentials(self) -> dict:
        return self._creds

    def get_threads(self, thread_ids: list) -> list:
        results = []
        for tid in thread_ids:
            r = _api("GET", f"/posts/{tid}", api_key=self._api_key)
            post = r.get("post", r)
            if post.get("id"):
                results.append({
                    "id": post["id"],
                    "title": post.get("title", ""),
                    "url": f"https://moltbook.com/posts/{post['id']}",
                    "comment_count": post.get("comment_count", 0),
                    "score": post.get("upvotes", 0),
                })
        return results

    def get_feed(self, limit: int = 25, submolt: str = None, **kwargs) -> list:
        path = "/posts?sort=hot&limit=25"
        if submolt:
            path += f"&submolt={urllib.parse.quote(submolt)}"
        r = _api("GET", path, api_key=self._api_key)
        posts = r.get("posts", [])
        result = []
        for p in posts[:limit]:
            result.append({
                "id": p.get("id", ""),
                "title": p.get("title", ""),
                "url": f"https://moltbook.com/posts/{p.get('id', '')}",
                "score": p.get("upvotes", 0),
                "created_at": p.get("created_at", ""),
            })
        return result

    def post_comment(self, thread_id: str, content: str, parent_id: str = None, **kwargs) -> dict:
        return _verify_and_retry(self._api_key, thread_id, content, parent_id)
