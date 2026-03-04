#!/usr/bin/env python3
"""Agent Brain v4 — Memory engine with pluggable storage.

Usage: python3 brain.py <command> [args...]
Env:   MEMORY_DIR       — path to memory directory (default: ../memory relative to script)
       AGENT_BRAIN_BACKEND — 'sqlite' (default) or 'json'
       AGENT_BRAIN_SUPERMEMORY_SYNC — auto | on | off
       AGENT_BRAIN_PII_MODE — strict (default) | off
"""

import json
import math
import os
import re
import sys
import urllib.error
import urllib.request
import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone

# --- Text Processing ---

STOPWORDS = frozenset({
    "i", "a", "an", "the", "is", "are", "was", "were", "be", "been",
    "do", "does", "did", "have", "has", "had", "will", "would", "could",
    "should", "may", "might", "can", "shall", "to", "of", "in", "for",
    "on", "with", "at", "by", "from", "it", "its", "this", "that",
    "and", "or", "but", "not", "no", "so", "if", "then", "than",
    "my", "me", "you", "your", "he", "she", "we", "they", "them",
    "very", "just", "also", "like", "about", "up", "out", "all",
    "over", "use", "using", "used", "every", "always", "never"
})


def normalize(word: str) -> str:
    if len(word) > 3 and word.endswith('s') and not word.endswith('ss'):
        word = word[:-1]
    if len(word) > 5 and word.endswith('ment'):
        return word[:-4]
    if len(word) > 5 and word.endswith('tion'):
        return word[:-4]
    if len(word) > 5 and word.endswith('sion'):
        return word[:-4]
    if len(word) > 4 and word.endswith('ing'):
        return word[:-3]
    if len(word) > 3 and word.endswith('ed') and not word.endswith('eed'):
        return word[:-2]
    if len(word) > 4 and word.endswith('ly'):
        return word[:-2]
    return word


def tokenize(text: str) -> list:
    return [normalize(w) for w in re.findall(r'\b[a-z]+\b', text.lower())
            if w not in STOPWORDS]


def tokenize_set(text: str) -> set:
    return set(tokenize(text))


def now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def now_dt() -> datetime:
    return datetime.now(timezone.utc)


def parse_ts(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


MEMORY_CLASSES = {"episodic", "semantic", "procedural", "preference", "policy"}
TYPE_TO_MEMORY_CLASS = {
    "fact": "semantic",
    "ingested": "semantic",
    "preference": "preference",
    "procedure": "procedural",
    "pattern": "procedural",
    "anti-pattern": "procedural",
    "correction": "episodic",
    "policy": "policy",
}

RETRIEVAL_POLICIES = {
    "fast": {"lexical_weight": 0.85, "semantic_weight": 0.15, "semantic_floor": 0.30, "top_k": 10},
    "balanced": {"lexical_weight": 0.65, "semantic_weight": 0.35, "semantic_floor": 0.24, "top_k": 12},
    "deep": {"lexical_weight": 0.45, "semantic_weight": 0.55, "semantic_floor": 0.20, "top_k": 20},
}


def infer_memory_class(entry_type: str) -> str:
    return TYPE_TO_MEMORY_CLASS.get(entry_type, "semantic")


def pii_mode() -> str:
    return os.environ.get("AGENT_BRAIN_PII_MODE", "strict").strip().lower()


def is_sensitive_content(text: str) -> bool:
    if pii_mode() in {"off", "false", "0"}:
        return False

    patterns = [
        r"-----BEGIN (RSA|EC|OPENSSH|PRIVATE) KEY-----",
        r"\bAKIA[0-9A-Z]{16}\b",
        r"\b(?:sk|rk|pk)_(?:live|test)?[A-Za-z0-9]{16,}\b",
        r"\bpassword\s*[:=]\s*\S+",
        r"\bapi[_-]?key\s*[:=]\s*\S+",
        r"\btoken\s*[:=]\s*\S+",
        r"\bsecret\s*[:=]\s*\S+",
        r"\bghp_[A-Za-z0-9]{20,}\b",
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def parse_common_flags(args: list[str]) -> dict:
    opts = {
        "query_parts": [],
        "policy": "balanced",
        "stores": None,
        "explain": False,
        "response": None,
        "user_feedback": None,
    }
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--":
            opts["query_parts"].extend(args[i + 1:])
            break
        if arg in {"--policy", "-p"}:
            if i + 1 >= len(args):
                raise ValueError("Missing value for --policy")
            opts["policy"] = args[i + 1].strip().lower()
            i += 2
            continue
        if arg.startswith("--policy="):
            opts["policy"] = arg.split("=", 1)[1].strip().lower()
            i += 1
            continue
        if arg in {"--stores", "-s"}:
            if i + 1 >= len(args):
                raise ValueError("Missing value for --stores")
            raw = args[i + 1]
            opts["stores"] = [s.strip().lower() for s in raw.split(",") if s.strip()]
            i += 2
            continue
        if arg.startswith("--stores="):
            raw = arg.split("=", 1)[1]
            opts["stores"] = [s.strip().lower() for s in raw.split(",") if s.strip()]
            i += 1
            continue
        if arg == "--explain":
            opts["explain"] = True
            i += 1
            continue
        if arg in {"--response", "-r"}:
            if i + 1 >= len(args):
                raise ValueError("Missing value for --response")
            opts["response"] = args[i + 1]
            i += 2
            continue
        if arg.startswith("--response="):
            opts["response"] = arg.split("=", 1)[1]
            i += 1
            continue
        if arg == "--user-feedback":
            if i + 1 >= len(args):
                raise ValueError("Missing value for --user-feedback")
            opts["user_feedback"] = args[i + 1]
            i += 2
            continue
        if arg.startswith("--user-feedback="):
            opts["user_feedback"] = arg.split("=", 1)[1]
            i += 1
            continue
        if arg.startswith("-"):
            raise ValueError(
                f"Unknown flag: {arg}. Use -- before query text that starts with '-'"
            )
        opts["query_parts"].append(arg)
        i += 1

    if opts["policy"] not in RETRIEVAL_POLICIES:
        raise ValueError("Policy must be one of: fast | balanced | deep")

    if opts["stores"]:
        bad = [s for s in opts["stores"] if s not in MEMORY_CLASSES]
        if bad:
            raise ValueError(
                "Invalid stores: " + ",".join(bad) +
                ". Allowed: " + ",".join(sorted(MEMORY_CLASSES))
            )
    return opts


def derive_query_terms(text: str, limit: int = 5) -> str:
    words = tokenize(text)
    if not words:
        words = [w.lower() for w in re.findall(r"\b[a-zA-Z0-9]{3,}\b", text)]
    return " ".join(words[:limit]).strip()


# --- Optional SuperMemory Sync ---

TRUTHY = {"1", "true", "yes", "on"}
FALSY = {"0", "false", "no", "off"}


def _is_truthy(value: str) -> bool:
    return value.strip().lower() in TRUTHY


def _is_falsy(value: str) -> bool:
    return value.strip().lower() in FALSY


def _supermemory_mode() -> str:
    return os.environ.get("AGENT_BRAIN_SUPERMEMORY_SYNC", "auto").strip().lower()


def _supermemory_api_key() -> str:
    return os.environ.get("SUPERMEMORY_API_KEY", "").strip()


def _sanitize_supermemory_tag(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9_-]+", "-", value.lower()).strip("-")
    return cleaned or "agent-brain"


def _maybe_sync_supermemory(entry: dict):
    mode = _supermemory_mode()
    if _is_falsy(mode):
        return

    api_key = _supermemory_api_key()
    if not api_key:
        if mode != "auto" and _is_truthy(os.environ.get("AGENT_BRAIN_SUPERMEMORY_DEBUG", "")):
            print("SuperMemory sync warning: SUPERMEMORY_API_KEY is not set", file=sys.stderr)
        return

    memory_payload = {
        "origin": "agent-brain",
        "entry_id": entry.get("id"),
        "type": entry.get("type"),
        "content": entry.get("content"),
        "source": entry.get("source"),
        "source_url": entry.get("source_url"),
        "tags": entry.get("tags", []),
        "context": entry.get("context"),
        "created": entry.get("created"),
        "confidence": entry.get("confidence"),
        "session_id": entry.get("session_id"),
        "correction_meta": entry.get("correction_meta"),
    }

    tags = [_sanitize_supermemory_tag("agent-brain"), _sanitize_supermemory_tag(entry.get("type", "entry"))]
    for tag in entry.get("tags", []):
        if len(tags) >= 8:
            break
        tags.append(_sanitize_supermemory_tag(tag))
    # Keep deterministic order and avoid duplicate container tags.
    tags = list(dict.fromkeys(tags))

    req_payload = {
        "content": json.dumps(memory_payload, ensure_ascii=False),
        "customId": f"agent_brain_{entry.get('id', uuid.uuid4())}",
        "containerTags": tags,
    }

    api_url = os.environ.get("SUPERMEMORY_API_URL", "https://api.supermemory.ai/v3/documents").strip()
    timeout = float(os.environ.get("AGENT_BRAIN_SUPERMEMORY_TIMEOUT", "8"))
    debug = _is_truthy(os.environ.get("AGENT_BRAIN_SUPERMEMORY_DEBUG", ""))

    try:
        data = json.dumps(req_payload).encode("utf-8")
        request = urllib.request.Request(
            api_url,
            data=data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if response.status >= 300 and debug:
                print(f"SuperMemory sync warning: HTTP {response.status}", file=sys.stderr)
    except urllib.error.HTTPError as exc:
        if debug:
            print(f"SuperMemory sync warning: HTTP {exc.code}", file=sys.stderr)
    except urllib.error.URLError as exc:
        if debug:
            print(f"SuperMemory sync warning: {exc.reason}", file=sys.stderr)
    except Exception as exc:
        if debug:
            print(f"SuperMemory sync warning: {exc}", file=sys.stderr)


# --- Scoring ---

CONF_WEIGHT = {"sure": 1.0, "likely": 0.7, "uncertain": 0.4}


def score_entry_components(entry: dict, query_words: list, now: datetime, max_access: int) -> dict:
    """Weighted lexical score: keyword 40% + tag 25% + confidence 15% + recency 10% + frequency 10%."""
    content_words = tokenize_set(entry["content"])
    tag_list = entry.get("tags", [])

    # 1. Keyword match (40%)
    keyword_matches = sum(1 for w in query_words if w in content_words)
    keyword_score = keyword_matches / len(query_words) if query_words else 0

    # 2. Tag overlap (25%) with prefix matching
    tag_matches = 0
    for qw in query_words:
        for tag in tag_list:
            tag_lower = tag.lower()
            if qw == tag_lower or tag_lower.startswith(qw + ".") or qw in tag_lower.split("."):
                tag_matches += 1
                break
    tag_score = tag_matches / len(query_words) if query_words else 0

    # 3. Confidence (15%)
    conf_score = CONF_WEIGHT.get(entry.get("confidence", "uncertain"), 0.4)

    # 4. Recency (10%)
    try:
        last = parse_ts(entry["last_accessed"])
        days_ago = (now - last).days
        recency_score = max(0.0, 1.0 - (days_ago / 365.0))
    except (ValueError, KeyError):
        recency_score = 0.5

    # 5. Access frequency (10%)
    access_count = entry.get("access_count", 0)
    freq_score = math.log(1 + access_count) / math.log(1 + max_access) if max_access > 0 else 0

    lexical = (keyword_score * 0.4 + tag_score * 0.25 + conf_score * 0.15 +
               recency_score * 0.1 + freq_score * 0.1)
    lexical = lexical if (keyword_matches > 0 or tag_matches > 0) else 0.0
    return {
        "keyword": keyword_score,
        "tag": tag_score,
        "confidence": conf_score,
        "recency": recency_score,
        "frequency": freq_score,
        "keyword_matches": keyword_matches,
        "tag_matches": tag_matches,
        "lexical": lexical,
    }


def score_entry(entry: dict, query_words: list, now: datetime, max_access: int) -> float:
    return score_entry_components(entry, query_words, now, max_access)["lexical"]


def cosine_sim(v1: dict, v2: dict) -> float:
    keys = set(v1) | set(v2)
    if not keys:
        return 0.0
    dot = sum(v1.get(k, 0) * v2.get(k, 0) for k in keys)
    mag1 = math.sqrt(sum(v ** 2 for v in v1.values())) or 1
    mag2 = math.sqrt(sum(v ** 2 for v in v2.values())) or 1
    return dot / (mag1 * mag2)


def jaccard(set1: set, set2: set) -> float:
    if not set1 and not set2:
        return 0.0
    union = set1 | set2
    return len(set1 & set2) / len(union) if union else 0.0


def local_semantic_vector(text: str) -> dict:
    tokens = tokenize(text)
    if not tokens:
        tokens = [w.lower() for w in re.findall(r"\b[a-zA-Z0-9]+\b", text)]
    feats = defaultdict(float)

    for t in tokens:
        feats[f"tok:{t}"] += 1.0
        for i in range(len(t) - 2):
            feats[f"tri:{t[i:i + 3]}"] += 0.25

    for i in range(len(tokens) - 1):
        feats[f"bi:{tokens[i]}_{tokens[i + 1]}"] += 0.75

    norm = math.sqrt(sum(v * v for v in feats.values())) or 1.0
    return {k: v / norm for k, v in feats.items()}


def remote_embeddings_enabled(entry_count: int) -> tuple[bool, str]:
    mode = os.environ.get("AGENT_BRAIN_REMOTE_EMBEDDINGS", "off").strip().lower()
    if mode not in TRUTHY:
        return False, "remote_disabled"

    url = os.environ.get("AGENT_BRAIN_EMBEDDING_URL", "").strip()
    if not url:
        return False, "missing_url"

    try:
        max_entries = int(os.environ.get("AGENT_BRAIN_REMOTE_EMBEDDING_MAX_ENTRIES", "120"))
    except ValueError:
        max_entries = 120

    if entry_count > max_entries:
        return False, "entry_limit"
    return True, "remote_enabled"


def remote_semantic_vector(text: str) -> dict | None:
    url = os.environ.get("AGENT_BRAIN_EMBEDDING_URL", "").strip()
    if not url:
        return None

    api_key = os.environ.get("AGENT_BRAIN_EMBEDDING_API_KEY", "").strip()
    payload = json.dumps({"input": text}).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    timeout = float(os.environ.get("AGENT_BRAIN_EMBEDDING_TIMEOUT", "6"))
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            if isinstance(body, dict) and isinstance(body.get("embedding"), list):
                vec = body["embedding"]
            elif isinstance(body, dict) and body.get("data") and isinstance(body["data"], list):
                vec = body["data"][0].get("embedding", [])
            else:
                vec = []
            if not vec:
                return None
            return {str(i): float(v) for i, v in enumerate(vec)}
    except Exception:
        return None


def semantic_vector(text: str, cache: dict | None = None) -> dict:
    if cache is not None and text in cache:
        return cache[text]
    vec = local_semantic_vector(text)
    if cache is not None:
        cache[text] = vec
    return vec


# --- Decay Logic ---

def decay_fn(entry: dict, now_str_val: str):
    """Returns new confidence if entry should decay, else None."""
    try:
        last = parse_ts(entry["last_accessed"])
        now = parse_ts(now_str_val)
        decay_days = 30 * (1 + entry.get("access_count", 0))
        if (now - last).days > decay_days:
            if entry["confidence"] == "sure":
                return "likely"
            elif entry["confidence"] == "likely":
                return "uncertain"
    except (ValueError, KeyError):
        pass
    return None


def should_auto_decay(store, now: datetime) -> bool:
    """Check if 24h have passed since last decay."""
    last_decay = store.get_meta("last_decay")
    if not last_decay:
        return True
    try:
        last_dt = parse_ts(last_decay)
        return (now - last_dt) > timedelta(hours=24)
    except (ValueError, TypeError):
        return True


# --- Store Factory ---

def get_store(memory_dir: str):
    backend = os.environ.get("AGENT_BRAIN_BACKEND", "sqlite").lower()
    if backend == "json":
        from json_store import JsonStore
        return JsonStore(os.path.join(memory_dir, "memory.json"))
    else:
        from sqlite_store import SQLiteStore
        return SQLiteStore(os.path.join(memory_dir, "memory.db"))


def build_entry(
    store,
    entry_type: str,
    content: str,
    source: str = "user",
    tags: list[str] | None = None,
    source_url: str | None = None,
    context: str | None = None,
    confidence: str | None = None,
    correction_meta: dict | None = None,
) -> dict:
    if is_sensitive_content(content):
        raise ValueError("Sensitive content detected; refusing to store.")

    ts = now_str()
    session = store.get_session()
    session_id = session["id"] if session else None
    entry_conf = confidence or ("sure" if source == "user" else "likely")
    return {
        "id": str(uuid.uuid4()),
        "type": entry_type,
        "memory_class": infer_memory_class(entry_type),
        "content": content,
        "source": source,
        "source_url": source_url if source_url else None,
        "tags": tags or [],
        "context": context if context else None,
        "session_id": session_id,
        "created": ts,
        "last_accessed": ts,
        "access_count": 1,
        "confidence": entry_conf,
        "superseded_by": None,
        "success_count": 0,
        "correction_meta": correction_meta,
    }


def find_conflicts_for_content(content: str, active_entries: list) -> list:
    content_words = tokenize_set(content)
    if not content_words:
        return []

    candidates = []
    for e in active_entries:
        entry_words = tokenize_set(e["content"])
        overlap = content_words & entry_words
        if len(overlap) >= 2:
            shorter = min(len(content_words), len(entry_words))
            if shorter > 0 and len(overlap) / shorter >= 0.3:
                score = len(overlap) / shorter
                candidates.append((score, e))
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates


def near_duplicate_exists(active_entries: list, entry_type: str, content: str) -> bool:
    target = set(tokenize(content))
    if not target:
        return False
    for e in active_entries:
        if e.get("type") != entry_type:
            continue
        overlap = jaccard(target, set(tokenize(e.get("content", ""))))
        if overlap >= 0.92:
            return True
    return False


def _print_get_result(result: dict, explain: bool = False):
    e = result["entry"]
    conf = e.get("confidence", "?")
    ctx = f"  context: {e['context']}" if e.get("context") else ""
    print(f"[{conf}] ({e['type']}/{e.get('memory_class', '?')}) {e['content']}")
    print(f"  id: {e['id']}  tags: {','.join(e.get('tags', []))}  score: {result['score']:.2f}{ctx}")
    if explain:
        c = result["components"]
        print(
            "  explain:"
            f" lexical={c['lexical']:.2f} semantic={c['semantic']:.2f}"
            f" keyword={c['keyword']:.2f} tag={c['tag']:.2f}"
            f" conf={c['confidence']:.2f} recency={c['recency']:.2f} freq={c['frequency']:.2f}"
            f" semantic_mode={c.get('semantic_mode', 'local')}"
            f" semantic_reason={c.get('semantic_reason', 'local_only')}"
        )
    print()


def retrieve_entries(
    store,
    query: str,
    policy: str = "balanced",
    stores: list[str] | None = None,
    explain: bool = False,
    touch_results: bool = True,
    log_action: str = "get",
) -> list:
    query = query.lower().strip()
    query_words = tokenize(query)
    if not query_words:
        query_words = list(set(query.split()))

    active = store.get_active_entries(memory_classes=stores)
    if not active:
        return []

    now = now_dt()
    max_access = max((e.get("access_count", 0) for e in active), default=1) or 1
    cfg = RETRIEVAL_POLICIES[policy]
    vector_cache = {}
    remote_ok, remote_reason = remote_embeddings_enabled(len(active))
    semantic_mode = "local"
    semantic_reason = remote_reason
    query_vec = None
    entry_vectors = {}

    if remote_ok:
        query_remote = remote_semantic_vector(query)
        if query_remote is not None:
            query_vec = query_remote
            remote_failed = False
            for e in active:
                rv = remote_semantic_vector(e["content"])
                if rv is None:
                    remote_failed = True
                    break
                entry_vectors[e["id"]] = rv
            if not remote_failed:
                semantic_mode = "remote"
                semantic_reason = "remote_enabled"
            else:
                semantic_reason = "remote_entry_error"
                query_vec = None
        else:
            semantic_reason = "remote_query_error"

    if query_vec is None:
        query_vec = semantic_vector(query, vector_cache)
        entry_vectors = {e["id"]: semantic_vector(e["content"], vector_cache) for e in active}
        semantic_mode = "local"

    results = []
    for e in active:
        components = score_entry_components(e, query_words, now, max_access)
        sem = cosine_sim(query_vec, entry_vectors[e["id"]])
        components["semantic"] = sem
        components["semantic_mode"] = semantic_mode
        components["semantic_reason"] = semantic_reason
        score = components["lexical"] * cfg["lexical_weight"] + sem * cfg["semantic_weight"]
        components["score"] = score

        is_match = components["lexical"] > 0 or sem >= cfg["semantic_floor"]
        if is_match:
            results.append({"score": score, "entry": e, "components": components})

    results.sort(key=lambda x: x["score"], reverse=True)
    if not results:
        return []

    top_results = results[:cfg["top_k"]]
    ts = now_str()
    if touch_results:
        returned_ids = {r["entry"]["id"] for r in top_results}
        store.bulk_touch(returned_ids, ts)

    store_list = ",".join(stores) if stores else "all"
    detail = (
        f"query='{query}' policy={policy} stores={store_list}"
        f" results={len(top_results)} explain={int(bool(explain))}"
        f" semantic_mode={semantic_mode} semantic_reason={semantic_reason}"
    )
    store.log_activity(ts, log_action, None, detail)

    if should_auto_decay(store, now):
        decayed = store.run_decay(ts, decay_fn)
        if decayed > 0:
            store.log_activity(ts, "decay", None, f"{decayed} entries decayed")
            print(f"Auto-decayed {decayed} entries")

    return top_results


def extract_candidates(message: str) -> list:
    text = message.strip()
    candidates = []

    def add_candidate(entry_type: str, content: str, tags: list[str], source: str = "inferred", confidence: str = "uncertain"):
        cleaned = re.sub(r"\s+", " ", content).strip()
        if not cleaned or len(cleaned) < 8 or len(cleaned) > 220:
            return
        candidates.append(
            {
                "type": entry_type,
                "content": cleaned,
                "source": source,
                "tags": tags,
                "confidence": confidence,
            }
        )

    m = re.search(r"\bmy name is\s+([A-Z][a-z]+)\b", text, re.IGNORECASE)
    if m:
        add_candidate("fact", f"The user's name is {m.group(1)}", ["identity", "personal"], source="user", confidence="sure")

    m = re.search(r"\b(i am|i'm)\s+a[n]?\s+([A-Za-z0-9 _-]{2,40})\s+at\s+([A-Za-z0-9 ._-]{2,40})", text, re.IGNORECASE)
    if m:
        role = re.sub(r"\s+", " ", m.group(2)).strip()
        company = re.sub(r"\s+", " ", m.group(3)).strip()
        add_candidate("fact", f"User is a {role} at {company}", ["identity", "work", "role"], source="user", confidence="sure")

    m = re.search(r"\bwe use\s+([A-Za-z0-9+.#/_ -]{2,60})", text, re.IGNORECASE)
    if m:
        tech = re.sub(r"[.?!].*$", "", m.group(1)).strip()
        add_candidate("fact", f"Team uses {tech}", ["project", "code.stack"], source="user", confidence="sure")

    m = re.search(r"\b(?:i\s+)?prefer\s+([^.!?]+)", text, re.IGNORECASE)
    if m:
        pref = m.group(1).strip(" \"'")
        add_candidate("preference", f"Prefers {pref}", ["style", "preferences"], source="user", confidence="sure")

    m = re.search(r"\bdon't use\s+([^.!?]+)", text, re.IGNORECASE)
    if m:
        pref = m.group(1).strip(" \"'")
        add_candidate("preference", f"Avoids using {pref}", ["style", "preferences"], source="user", confidence="sure")

    m = re.search(r"\b(i always|always)\s+([^.!?]+)", text, re.IGNORECASE)
    if m:
        proc = m.group(2).strip(" \"'")
        add_candidate("procedure", f"Workflow: {proc}", ["workflow", "process"], source="user", confidence="sure")

    # Deduplicate within extraction batch.
    seen = set()
    unique = []
    for c in candidates:
        key = (c["type"], c["content"].lower())
        if key not in seen:
            seen.add(key)
            unique.append(c)
    return unique


# --- Commands ---

def cmd_init(store):
    store.init()
    backend = os.environ.get("AGENT_BRAIN_BACKEND", "sqlite").lower()
    if backend == "json":
        path = os.path.join(os.path.dirname(store.path), "memory.json")
    else:
        path = store.db_path
    print(f"Initialized memory at {path}")


def cmd_add(store, args):
    if len(args) < 2:
        print("Usage: add <type> <content> [source] [tags] [source_url] [context]", file=sys.stderr)
        sys.exit(1)

    entry_type = args[0]
    content = args[1]
    source = args[2] if len(args) > 2 else "user"
    tags_str = args[3] if len(args) > 3 else ""
    source_url = args[4] if len(args) > 4 else ""
    context = args[5] if len(args) > 5 else ""

    tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []
    try:
        entry = build_entry(
            store=store,
            entry_type=entry_type,
            content=content,
            source=source,
            tags=tags,
            source_url=source_url if source_url else None,
            context=context if context else None,
        )
    except ValueError as exc:
        print(f"Refused to store entry: {exc}")
        sys.exit(1)

    ts = entry["created"]
    entry_id = entry["id"]
    store.add_entry(entry)
    _maybe_sync_supermemory(entry)
    tags_display = ",".join(tags) if tags else ""
    store.log_activity(ts, "add", entry_id,
                       f"{entry_type}/{entry['memory_class']}: {content[:60]}" + (f" [{tags_display}]" if tags_display else ""))

    # Auto-decay
    now = now_dt()
    if should_auto_decay(store, now):
        decayed = store.run_decay(ts, decay_fn)
        if decayed > 0:
            store.log_activity(ts, "decay", None, f"{decayed} entries decayed")
            print(f"Auto-decayed {decayed} entries")

    print(f"Added: {entry_id} ({entry_type})")


def cmd_get(store, args):
    if len(args) < 1:
        print(
            "Usage: get <query> [--policy fast|balanced|deep] [--stores semantic,procedural,...] [--explain]",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        opts = parse_common_flags(args)
    except ValueError as exc:
        print(f"Invalid arguments: {exc}", file=sys.stderr)
        sys.exit(1)

    if opts.get("response") is not None or opts.get("user_feedback") is not None:
        print("Invalid arguments: get does not accept --response or --user-feedback", file=sys.stderr)
        sys.exit(1)

    query = " ".join(opts["query_parts"]).strip()
    if not query:
        print("Usage: get <query> [--policy ...] [--stores ...] [--explain]", file=sys.stderr)
        sys.exit(1)

    results = retrieve_entries(
        store=store,
        query=query,
        policy=opts["policy"],
        stores=opts["stores"],
        explain=opts["explain"],
        touch_results=True,
        log_action="get",
    )
    if not results:
        print("No matching entries found.")
        return

    for result in results:
        _print_get_result(result, explain=opts["explain"])


def cmd_loop(store, args):
    if len(args) < 1:
        print(
            "Usage: loop <message> [--user-feedback <user_feedback>] [--response <assistant_response>] "
            "[--policy fast|balanced|deep] [--stores ...] [--explain]",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        opts = parse_common_flags(args)
    except ValueError as exc:
        print(f"Invalid arguments: {exc}", file=sys.stderr)
        sys.exit(1)

    message = " ".join(opts["query_parts"]).strip()
    if not message:
        print(
            "Usage: loop <message> [--user-feedback ...] [--response ...] [--policy ...] [--stores ...] [--explain]",
            file=sys.stderr,
        )
        sys.exit(1)

    query = derive_query_terms(message) or message
    retrieved = retrieve_entries(
        store=store,
        query=query,
        policy=opts["policy"],
        stores=opts["stores"],
        explain=opts["explain"],
        touch_results=True,
        log_action="loop_get",
    )

    print("LOOP_RETRIEVE")
    print(f"  query: {query}")
    print(f"  hits: {len(retrieved)}")
    if opts["explain"]:
        for r in retrieved[:5]:
            _print_get_result(r, explain=True)

    candidates = extract_candidates(message)
    active = store.get_active_entries()
    added = 0
    skipped_dup = 0
    skipped_conflict = 0
    skipped_sensitive = 0

    for c in candidates:
        if is_sensitive_content(c["content"]):
            skipped_sensitive += 1
            continue

        if near_duplicate_exists(active, c["type"], c["content"]):
            skipped_dup += 1
            continue

        conflicts = find_conflicts_for_content(c["content"], active)
        if conflicts:
            skipped_conflict += 1
            continue

        try:
            entry = build_entry(
                store=store,
                entry_type=c["type"],
                content=c["content"],
                source=c["source"],
                tags=c["tags"],
                confidence=c["confidence"],
            )
        except ValueError:
            skipped_sensitive += 1
            continue

        store.add_entry(entry)
        _maybe_sync_supermemory(entry)
        store.log_activity(
            entry["created"],
            "loop_add",
            entry["id"],
            f"{entry['type']}/{entry['memory_class']}: {entry['content'][:80]}",
        )
        active.append(entry)
        added += 1

    # Reinforcement only from explicit user feedback (not assistant response text).
    if opts.get("user_feedback") and retrieved:
        response = opts["user_feedback"].lower()
        if any(s in response for s in ["worked", "that helped", "helpful", "thanks", "great", "resolved"]):
            entry_id = retrieved[0]["entry"]["id"]
            updated = store.increment_success(entry_id, now_str())
            store.log_activity(now_str(), "loop_success", entry_id, f"total={updated.get('success_count', 0)}")
        else:
            store.log_activity(now_str(), "loop_feedback", None, "non-positive user feedback")

    print("LOOP_EXTRACT")
    print(f"  candidates: {len(candidates)}")
    print(f"  added: {added}")
    print(f"  skipped_duplicate: {skipped_dup}")
    print(f"  skipped_conflict: {skipped_conflict}")
    print(f"  skipped_sensitive: {skipped_sensitive}")
    if opts.get("response"):
        store.log_activity(now_str(), "loop_response", None, f"assistant_response_len={len(opts['response'])}")


def cmd_list(store, args):
    type_filter = args[0] if args else ""
    active = store.get_active_entries()

    for e in active:
        if type_filter and e["type"] != type_filter:
            continue
        conf = e.get("confidence", "?")
        src = e.get("source", "?")
        memory_class = e.get("memory_class", infer_memory_class(e.get("type", "")))
        ctx = f"  context: {e['context']}" if e.get("context") else ""
        sc = e.get("success_count", 0)
        sc_str = f"  success: {sc}x" if sc > 0 else ""
        print(f"[{conf}] ({e['type']}/{memory_class}) {e['content']}")
        print(f"  id: {e['id']}  source: {src}  accessed: {e.get('access_count', 0)}x{sc_str}{ctx}")
        print()

    total = len([e for e in active if not type_filter or e["type"] == type_filter])
    if type_filter:
        print(f"--- {total} {type_filter} entries ---")
    else:
        print(f"--- {len(active)} active entries ---")


def cmd_update(store, args):
    if len(args) < 3:
        print("Usage: update <id> <field> <value>", file=sys.stderr)
        sys.exit(1)

    entry_id, field, value = args[0], args[1], args[2]
    allowed = {"confidence", "tags", "content", "type", "context", "memory_class"}
    if field not in allowed:
        print(f"ERROR: Cannot update '{field}'. Allowed: {', '.join(sorted(allowed))}")
        sys.exit(1)
    if field == "memory_class" and value not in MEMORY_CLASSES:
        print(f"ERROR: memory_class must be one of {', '.join(sorted(MEMORY_CLASSES))}")
        sys.exit(1)

    try:
        store.update_entry(entry_id, field, value)
        store.log_activity(now_str(), "update", entry_id, f"{field}={value}")
        print(f"Updated {entry_id}: {field} = {value}")
    except KeyError:
        print(f"Entry not found: {entry_id}")
        sys.exit(1)


def cmd_touch(store, args):
    if len(args) < 1:
        print("Usage: touch <id>", file=sys.stderr)
        sys.exit(1)

    try:
        store.touch_entry(args[0], now_str())
        print(f"Touched: {args[0]}")
    except KeyError:
        print(f"Entry not found: {args[0]}")
        sys.exit(1)


def cmd_supersede(store, args):
    if len(args) < 2:
        print("Usage: supersede <old_id> <new_id>", file=sys.stderr)
        sys.exit(1)

    store.mark_superseded(args[0], args[1])
    store.log_activity(now_str(), "supersede", args[0], f"{args[0]} -> {args[1]}")
    print(f"Superseded {args[0]} -> {args[1]}")


def cmd_conflicts(store, args):
    if len(args) < 1:
        print("Usage: conflicts <content>", file=sys.stderr)
        sys.exit(1)

    candidates = find_conflicts_for_content(args[0], store.get_active_entries())

    if not candidates:
        print("NO_CONFLICTS")
    else:
        print("POTENTIAL_CONFLICTS")
        for score, e in candidates[:5]:
            print(f"  [{e.get('confidence', '?')}] {e['content']}")
            print(f"    id: {e['id']}  overlap: {score:.0%}")


def cmd_similar(store, args):
    if len(args) < 1:
        print("Usage: similar <content> [threshold]", file=sys.stderr)
        sys.exit(1)

    query = args[0]
    threshold = float(args[1]) if len(args) > 1 else 0.10

    active = store.get_active_entries()
    if not active:
        print("NO_SIMILAR")
        return

    query_tokens = tokenize(query)
    if not query_tokens:
        query_tokens = query.lower().split()

    query_token_set = set(query_tokens)
    all_docs = [query_tokens] + [tokenize(e["content"]) for e in active]

    # Compute IDF
    n = len(all_docs)
    df = {}
    for doc in all_docs:
        for word in set(doc):
            df[word] = df.get(word, 0) + 1

    # Build TF-IDF vectors
    vectors = []
    for doc in all_docs:
        tf = {}
        for w in doc:
            tf[w] = tf.get(w, 0) + 1
        vec = {}
        doc_len = len(doc) or 1
        for w, count in tf.items():
            vec[w] = (count / doc_len) * math.log((n + 1) / (df.get(w, 0) + 1))
        vectors.append(vec)

    query_vec = vectors[0]
    results = []
    for i, e in enumerate(active):
        content_sim = cosine_sim(query_vec, vectors[i + 1])
        entry_token_set = set(tokenize(e["content"]))
        token_overlap = jaccard(query_token_set, entry_token_set)
        sim = 0.6 * content_sim + 0.4 * token_overlap
        if sim >= threshold:
            results.append((sim, e))

    results.sort(key=lambda x: x[0], reverse=True)

    if not results:
        print("NO_SIMILAR")
    else:
        print(f"SIMILAR_ENTRIES ({len(results)} found)")
        for sim, e in results[:10]:
            print(f"  [{e.get('confidence', '?')}] ({e['type']}) {e['content']}")
            print(f"    id: {e['id']}  similarity: {sim:.2f}  tags: {','.join(e.get('tags', []))}")
            print()


def cmd_correct(store, args):
    if len(args) < 2:
        print("Usage: correct <wrong_id> <right_content> [reason] [tags]", file=sys.stderr)
        sys.exit(1)

    wrong_id = args[0]
    right_content = args[1]
    reason = args[2] if len(args) > 2 else ""
    tags_str = args[3] if len(args) > 3 else ""

    wrong_entry = store.get_entry(wrong_id)
    if not wrong_entry:
        print(f"Entry not found: {wrong_id}")
        sys.exit(1)

    tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else wrong_entry.get("tags", [])
    try:
        correction = build_entry(
            store=store,
            entry_type="correction",
            content=right_content,
            source="user",
            tags=tags,
            confidence="sure",
            correction_meta={
                "wrong_entry_id": wrong_id,
                "wrong_claim": wrong_entry["content"],
                "right_claim": right_content,
                "reason": reason if reason else None,
            },
        )
    except ValueError as exc:
        print(f"Refused to store correction: {exc}")
        sys.exit(1)

    new_id = correction["id"]
    ts = correction["created"]
    store.mark_superseded(wrong_id, new_id)
    store.add_entry(correction)
    _maybe_sync_supermemory(correction)

    store.log_activity(ts, "correct", new_id,
                       f"wrong={wrong_entry['content'][:40]} right={right_content[:40]}")

    print(f"Corrected: {wrong_id} -> {new_id}")
    print(f"  Wrong: {wrong_entry['content']}")
    print(f"  Right: {right_content}")
    if reason:
        print(f"  Reason: {reason}")

    # Anti-pattern detection
    active = store.get_active_entries()
    corrections = [e for e in active if e.get("type") == "correction"]
    tag_counts = {}
    for c in corrections:
        for t in c.get("tags", []):
            tag_counts.setdefault(t, []).append(c)

    for tag, group in tag_counts.items():
        if len(group) >= 3:
            existing_ap = [e for e in active
                          if e.get("type") == "anti-pattern"
                          and tag in e.get("tags", [])
                          and not e.get("superseded_by")]
            if not existing_ap:
                print(f"\nANTI_PATTERN_DETECTED: tag '{tag}' has {len(group)} corrections")
                print(f"  Consider: add anti-pattern 'Avoid inferring {tag} - ask explicitly' inferred '{tag},caution'")


def cmd_success(store, args):
    if len(args) < 1:
        print("Usage: success <id> [context]", file=sys.stderr)
        sys.exit(1)

    entry_id = args[0]
    ts = now_str()

    try:
        entry = store.increment_success(entry_id, ts)
    except KeyError:
        print(f"Entry not found: {entry_id}")
        sys.exit(1)

    sc = entry.get("success_count", 0)
    store.log_activity(ts, "success", entry_id, f"total={sc}")

    if sc >= 3 and entry.get("confidence") != "sure":
        old_conf = entry.get("confidence", "uncertain")
        store.update_entry(entry_id, "confidence", "sure")
        print(f"Auto-upgraded: {old_conf} -> sure ({sc} successes)")

    print(f"Success recorded: {entry_id} (total: {sc})")


def cmd_reflect(store):
    now = now_dt()
    active = store.get_active_entries()
    all_data = store.read_all()
    superseded = [e for e in all_data["entries"] if e.get("superseded_by")]

    # Stale entries
    stale = []
    for e in active:
        try:
            last = parse_ts(e["last_accessed"])
            days_old = (now - last).days
            if days_old > 30:
                stale.append((days_old, e))
        except (ValueError, KeyError):
            pass
    stale.sort(key=lambda x: x[0], reverse=True)

    # Upgrade candidates
    hot = [(e.get("access_count", 0), e) for e in active
           if e.get("access_count", 0) > 3 and e.get("confidence") != "sure"]
    hot.sort(key=lambda x: x[0], reverse=True)

    corrections = [e for e in active if e.get("type") == "correction"]
    uncertain = [e for e in active if e.get("confidence") == "uncertain"]

    successes = [(e.get("success_count", 0), e) for e in active if e.get("success_count", 0) > 0]
    successes.sort(key=lambda x: x[0], reverse=True)

    anti_patterns = [e for e in active if e.get("type") == "anti-pattern"]

    tag_counts = {}
    for e in active:
        for t in e.get("tags", []):
            tag_counts[t] = tag_counts.get(t, 0) + 1

    print("=== MEMORY REFLECTION ===\n")
    print(f"Total: {len(active)} active, {len(superseded)} superseded")
    session_counter = store.get_session_counter()
    if session_counter:
        print(f"Sessions: {session_counter}")
    print()

    if stale:
        print(f"STALE ({len(stale)} entries, 30+ days untouched):")
        for days, e in stale[:5]:
            print(f"  {days}d: [{e.get('confidence', '?')}] {e['content'][:60]}")
        if len(stale) > 5:
            print(f"  ... and {len(stale) - 5} more")
        print()

    if hot:
        print(f"UPGRADE CANDIDATES ({len(hot)} frequently accessed, not SURE):")
        for count, e in hot[:5]:
            print(f"  {count}x: [{e.get('confidence', '?')}] {e['content'][:60]}")
        print()

    if corrections:
        print(f"CORRECTIONS ({len(corrections)} learning events):")
        for e in corrections[:5]:
            meta = e.get("correction_meta") or {}
            print(f"  Wrong: {meta.get('wrong_claim', '?')[:50]}")
            print(f"  Right: {meta.get('right_claim', '?')[:50]}")
            if meta.get("reason"):
                print(f"  Why:   {meta['reason'][:50]}")
            print()

    if anti_patterns:
        print(f"ANTI-PATTERNS ({len(anti_patterns)} learned cautions):")
        for e in anti_patterns:
            print(f"  {e['content'][:70]}")
        print()

    if successes:
        print(f"TOP SUCCESSES ({len(successes)} entries with recorded wins):")
        for count, e in successes[:5]:
            print(f"  {count}x: {e['content'][:60]}")
        print()

    if uncertain:
        print(f"UNCERTAIN ({len(uncertain)} entries needing confirmation):")
        for e in uncertain[:5]:
            print(f"  {e['content'][:60]}")
            print(f"    id: {e['id']}")
        print()

    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    if sorted_tags:
        print(f"TOP TAGS: {', '.join(f'{t}({c})' for t, c in sorted_tags[:10])}")


def cmd_consolidate(store):
    active = store.get_active_entries()

    tag_groups = {}
    for e in active:
        for tag in e.get("tags", []):
            tag_groups.setdefault(tag, []).append(e)

    clusters = []
    seen = set()
    for tag, entries in sorted(tag_groups.items(), key=lambda x: len(x[1]), reverse=True):
        if len(entries) >= 3:
            ids = frozenset(e["id"] for e in entries)
            if ids not in seen:
                seen.add(ids)
                clusters.append({"tag": tag, "count": len(entries), "entries": entries})

    if not clusters:
        print("NO_CONSOLIDATION_CANDIDATES")
    else:
        print(f"CONSOLIDATION_CANDIDATES ({len(clusters)} clusters)\n")
        for c in clusters[:5]:
            print(f"Cluster: '{c['tag']}' ({c['count']} entries)")
            for e in c["entries"][:5]:
                print(f"  [{e.get('confidence', '?')}] {e['content'][:70]}")
            if c["count"] > 5:
                print(f"  ... and {c['count'] - 5} more")
            print()
        print("To consolidate: create a summary entry and supersede the originals.")


def cmd_session(store, args):
    context = args[0] if args else ""
    counter = store.get_session_counter() + 1
    store.set_session_counter(counter)
    ts = now_str()
    store.start_session(counter, context if context else None, ts)

    detail = f"Session {counter}"
    if context:
        detail += f": {context}"
    store.log_activity(ts, "session", None, detail)

    msg = f"Session {counter} started"
    if context:
        msg += f": {context}"
    print(msg)


def cmd_tags(store):
    active = store.get_active_entries()
    tree = defaultdict(lambda: {"count": 0, "children": defaultdict(int)})

    for e in active:
        for tag in e.get("tags", []):
            parts = tag.split(".", 1)
            root = parts[0]
            tree[root]["count"] += 1
            if len(parts) > 1:
                tree[root]["children"][parts[1]] += 1

    if not tree:
        print("No tags found.")
        return

    for root in sorted(tree, key=lambda r: tree[r]["count"], reverse=True):
        node = tree[root]
        print(f"{root} ({node['count']})")
        for child, count in sorted(node["children"].items(), key=lambda x: x[1], reverse=True):
            print(f"  .{child} ({count})")


def cmd_decay(store):
    ts = now_str()
    decayed = store.run_decay(ts, decay_fn)
    if decayed > 0:
        store.log_activity(ts, "decay", None, f"{decayed} entries decayed")
    print(f"Decayed {decayed} entries")


def cmd_export(store):
    print(store.export_json())


def cmd_log(store, args):
    limit = 50
    action_filter = None
    if args:
        try:
            limit = int(args[0])
        except ValueError:
            action_filter = args[0]
        if len(args) > 1:
            action_filter = args[1]

    entries = store.get_log(limit=limit, action=action_filter)
    if not entries:
        print("No activity logged yet.")
        return

    for e in entries:
        ts = e["timestamp"].replace("T", " ").replace("Z", "")
        action = e["action"]
        eid = e.get("entry_id") or ""
        detail = e.get("detail") or ""
        eid_str = f"  entry:{eid[:8]}" if eid else "             "
        print(f"[{ts}] {action:<10} {eid_str}  {detail}")


def cmd_stats(store):
    all_data = store.read_all()
    active = [e for e in all_data["entries"] if not e.get("superseded_by")]
    superseded = len(all_data["entries"]) - len(active)

    by_type = {}
    by_conf = {}
    by_source = {}
    by_memory_class = {}
    total_successes = 0
    for e in active:
        by_type[e["type"]] = by_type.get(e["type"], 0) + 1
        by_conf[e.get("confidence", "?")] = by_conf.get(e.get("confidence", "?"), 0) + 1
        by_source[e.get("source", "?")] = by_source.get(e.get("source", "?"), 0) + 1
        mclass = e.get("memory_class", infer_memory_class(e.get("type", "")))
        by_memory_class[mclass] = by_memory_class.get(mclass, 0) + 1
        total_successes += e.get("success_count", 0)

    print(f"Version: {all_data.get('version', '?')}")
    print(f"Sessions: {all_data.get('session_counter', 0)}")
    print(f"Total: {len(active)} active, {superseded} superseded")
    print(f"By type: {by_type}")
    print(f"By memory_class: {by_memory_class}")
    print(f"By confidence: {by_conf}")
    print(f"By source: {by_source}")
    print(f"Total success events: {total_successes}")
    if all_data.get("last_decay"):
        print(f"Last decay: {all_data['last_decay']}")


def cmd_help():
    print("Usage: memory.sh <command> [args]")
    print("")
    print("Core:")
    print("  init                                        Initialize memory")
    print("  add <type> <content> [src] [tags] [url] [ctx]  Add entry")
    print("  get <query> [--policy P] [--stores S] [--explain]  Hybrid retrieval")
    print("  loop <message> [--user-feedback F] [--response R] [--policy P] [--stores S] [--explain]")
    print("  list [type]                                 List entries")
    print("  update <id> <field> <value>                 Update entry field")
    print("  touch <id>                                  Mark as accessed")
    print("  supersede <old> <new>                       Replace entry")
    print("")
    print("Learning:")
    print("  conflicts <content>                         Find conflicts")
    print("  similar <content> [threshold]               Find related entries")
    print("  correct <wrong_id> <right> [reason] [tags]  Track correction")
    print("  success <id> [context]                      Record successful use")
    print("")
    print("Analysis:")
    print("  reflect                                     Memory health report")
    print("  consolidate                                 Find merge candidates")
    print("  tags                                        Tag hierarchy")
    print("  decay                                       Downgrade stale entries")
    print("  export                                      Dump full JSON")
    print("  stats                                       Show statistics")
    print("  log [count] [action]                        Activity log")
    print("")
    print("Session:")
    print("  session [context]                           Start new session")
    print("")
    print("Types: fact | preference | procedure | pattern | ingested | correction | anti-pattern | policy")
    print("Memory classes: episodic | semantic | procedural | preference | policy")


# --- Main Dispatch ---

def main():
    # Determine memory directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    memory_dir = os.environ.get("MEMORY_DIR", os.path.join(script_dir, "..", "memory"))
    memory_dir = os.path.abspath(memory_dir)

    # Add script dir to Python path so imports work
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    args = sys.argv[1:]
    cmd = args[0] if args else "help"
    cmd_args = args[1:]

    store = get_store(memory_dir)

    # Commands that need init first
    if cmd != "init":
        store.init()

    try:
        if cmd == "init":
            cmd_init(store)
        elif cmd == "add":
            cmd_add(store, cmd_args)
        elif cmd == "get":
            cmd_get(store, cmd_args)
        elif cmd == "loop":
            cmd_loop(store, cmd_args)
        elif cmd == "list":
            cmd_list(store, cmd_args)
        elif cmd == "update":
            cmd_update(store, cmd_args)
        elif cmd == "touch":
            cmd_touch(store, cmd_args)
        elif cmd == "supersede":
            cmd_supersede(store, cmd_args)
        elif cmd == "conflicts":
            cmd_conflicts(store, cmd_args)
        elif cmd == "similar":
            cmd_similar(store, cmd_args)
        elif cmd == "correct":
            cmd_correct(store, cmd_args)
        elif cmd == "success":
            cmd_success(store, cmd_args)
        elif cmd == "reflect":
            cmd_reflect(store)
        elif cmd == "consolidate":
            cmd_consolidate(store)
        elif cmd == "session":
            cmd_session(store, cmd_args)
        elif cmd == "tags":
            cmd_tags(store)
        elif cmd == "decay":
            cmd_decay(store)
        elif cmd == "export":
            cmd_export(store)
        elif cmd == "stats":
            cmd_stats(store)
        elif cmd == "log":
            cmd_log(store, cmd_args)
        else:
            cmd_help()
    finally:
        store.close()


if __name__ == "__main__":
    main()
