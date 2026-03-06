#!/usr/bin/env python3
"""
Memory Pruner — Generic Version for nima-core
Episodic distillation → file-based suppression registry → zero SIGSEGV risk.

Architecture:
1. Score memories in Python (read-only queries = safe)
2. Distill sessions to semantic gists via LLM
3. Write pruned IDs to suppression_registry.json
4. Caller filters suppressed IDs at read time (no DB writes)

Environment Variables:
- NIMA_DB_PATH: Path to LadybugDB (default: ~/.nima/memory/ladybug.lbug)
- NIMA_DATA_DIR: Base data directory (default: ~/.nima/memory)
- ANTHROPIC_API_KEY: Anthropic API key for LLM distillation (optional, falls back to extractive)
"""
import os
import sys
import json
import math
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# ── Configuration via Environment ───────────────────────────────────────────────

DATA_DIR = Path(os.environ.get('NIMA_DATA_DIR', str(Path.home() / '.nima' / 'memory')))
DB_PATH = os.environ.get('NIMA_DB_PATH', str(DATA_DIR / 'ladybug.lbug'))
REGISTRY_PATH = DATA_DIR / 'suppression_registry.json'
LOG_PATH = DATA_DIR / 'pruner_log.json'

# Configurable defaults
DEFAULT_MIN_AGE_DAYS = 7
DEFAULT_MAX_SESSIONS = None
DEFAULT_LIMBO_DAYS = 30
DEFAULT_GAP_HOURS = 4


# ── Suppression Registry ───────────────────────────────────────────────────────

def load_registry():
    """Load suppression registry (IDs to filter from recall)."""
    if not REGISTRY_PATH.exists():
        return {}
    try:
        return json.loads(REGISTRY_PATH.read_text())
    except Exception:
        return {}


def save_registry(registry):
    """Save suppression registry to disk."""
    REGISTRY_PATH.parent.mkdir(exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2))


def add_to_registry(memory_ids, reason='low_value', distillate=None, limbo_days=None):
    """Add IDs to suppression registry with metadata."""
    if limbo_days is None:
        limbo_days = DEFAULT_LIMBO_DAYS

    registry = load_registry()
    now = datetime.now()
    expires = now + timedelta(days=limbo_days)

    for mid in memory_ids:
        registry[str(mid)] = {
            'suppressed_at': now.isoformat(),
            'reason': reason,
            'distillate': distillate,
            'expires': expires.isoformat()
        }
    save_registry(registry)
    return len(registry)


def get_suppressed_ids():
    """Return set of currently suppressed memory IDs."""
    registry = load_registry()
    return set(int(k) for k in registry.keys())


def restore_memory(memory_id):
    """Restore a suppressed memory (remove from registry)."""
    registry = load_registry()
    if str(memory_id) in registry:
        del registry[str(memory_id)]
        save_registry(registry)
        return True
    return False


def list_suppressed(show_expired=False):
    """List suppressed memories for review."""
    registry = load_registry()
    now = datetime.now()
    results = []

    for mid, entry in registry.items():
        try:
            expires = datetime.fromisoformat(entry.get('expires', now.isoformat()))
        except ValueError:
            expires = now + timedelta(days=DEFAULT_LIMBO_DAYS)

        is_expired = now > expires
        if show_expired or not is_expired:
            results.append({
                'id': int(mid),
                'reason': entry.get('reason'),
                'suppressed_at': entry.get('suppressed_at'),
                'distillate': entry.get('distillate', '')[:100],
                'days_remaining': max(0, (expires - now).days),
                'status': 'limbo' if not is_expired else 'expired'
            })

    return sorted(results, key=lambda x: x['suppressed_at'])


# ── DB Access ──────────────────────────────────────────────────────────────────

def get_conn():
    """
    Get database connection.
    Tries real_ladybug first, falls back to ladybug.
    """
    # Try real_ladybug first (preferred)
    try:
        from real_ladybug import Database, Connection
        db = Database(DB_PATH)
        conn = Connection(db)
        try:
            conn.execute("LOAD VECTOR")
        except Exception:
            pass
        return conn
    except ImportError:
        pass

    # Fallback to ladybug
    try:
        from ladybug import Database, Connection
        db = Database(DB_PATH)
        conn = Connection(db)
        try:
            conn.execute("LOAD VECTOR")
        except Exception:
            pass
        return conn
    except ImportError:
        pass

    raise ImportError("Neither real_ladybug nor ladybug package available")


def get_candidates(min_age_days=7, layers=None, db_path=None):
    """Fetch old input/output memories as candidates for pruning."""
    if layers is None:
        layers = ['input', 'output']

    try:
        conn = get_conn()
    except Exception as e:
        print(f"Warning: Could not connect to database: {e}")
        return []

    cutoff_ms = (datetime.now() - timedelta(days=min_age_days)).timestamp() * 1000
    suppressed = get_suppressed_ids()

    # Whitelist valid layer names to prevent injection
    VALID_LAYERS = {'input', 'output', 'contemplation', 'insight', 'dream'}

    all_candidates = []
    for layer in layers:
        if layer not in VALID_LAYERS:
            print("  Warning: Skipping invalid layer name: {l}".format(l=layer))
            continue
        try:
            df = conn.execute('''
                MATCH (n:MemoryNode)
                WHERE n.is_ghost = false AND n.layer = "{layer}"
                RETURN n.id, n.text, n.timestamp, n.dismissal_count, n.layer, n.themes
                LIMIT 2000
            '''.format(layer=layer)).get_as_df()

            for _, row in df.iterrows():
                mid = int(row['n.id'])
                if mid in suppressed:
                    continue
                ts = float(row.get('n.timestamp', 0) or 0)
                if ts < cutoff_ms:
                    all_candidates.append({
                        'id': mid,
                        'text': str(row['n.text'] or ''),
                        'timestamp': ts,
                        'layer': str(row['n.layer'] or ''),
                        'dismissal_count': int(row.get('n.dismissal_count', 0) or 0),
                        'themes': str(row.get('n.themes', '') or ''),
                    })
        except Exception as e:
            print(f"Warning: Query failed for layer {layer}: {e}")
            continue

    return sorted(all_candidates, key=lambda x: x['timestamp'])


# ── Session Grouping ───────────────────────────────────────────────────────────

def group_by_session(memories, gap_hours=4):
    """Group memories into conversation sessions by timestamp proximity."""
    if not memories:
        return []

    sessions = []
    current = [memories[0]]

    for mem in memories[1:]:
        gap = (mem['timestamp'] - current[-1]['timestamp']) / 3600000
        if gap < gap_hours:
            current.append(mem)
        else:
            sessions.append(current)
            current = [mem]

    if current:
        sessions.append(current)

    return sessions


# ── Semantic Distillation ──────────────────────────────────────────────────────

def _get_anthropic_key():
    """Get Anthropic API key from environment variable."""
    return os.environ.get("ANTHROPIC_API_KEY", "")


def distill_session_llm(session, dry_run=False):
    """
    Distill a session to a semantic gist via Claude Haiku.
    Falls back to extractive distillation if no API key available.
    """
    if len(session) < 2:
        return None

    transcript = []
    for m in sorted(session, key=lambda x: x['timestamp'])[:20]:
        text = m['text'].replace('\n', ' ')[:250]
        prefix = '→ Agent:' if m['layer'] == 'output' else 'User:'
        transcript.append("{prefix} {text}".format(prefix=prefix, text=text))

    date_str = datetime.fromtimestamp(session[0]['timestamp'] / 1000).strftime('%B %d, %Y')
    full_text = '\n'.join(transcript)

    if dry_run:
        return "[DRY RUN session from {date_str}, {len} turns]".format(
            date_str=date_str, len=len(session)
        )

    prompt = """Distill this conversation from {date_str} into a compact memory summary (2-4 sentences).

Include: decisions made, things built, important context.
Exclude: routine greetings, trivial exchanges, repetitive content.

Conversation:
{full_text}

Summary:""".format(date_str=date_str, full_text=full_text)

    # Try LLM distillation first
    api_key = _get_anthropic_key()
    if not api_key:
        print("  Warning: No ANTHROPIC_API_KEY found — using extractive fallback")
        return _extractive_distill(session, date_str)

    try:
        import urllib.request
        import urllib.error

        distill_model = os.environ.get('NIMA_DISTILL_MODEL', 'claude-haiku-4-5')
        payload = json.dumps({
            "model": distill_model,
            "max_tokens": 200,
            "messages": [{"role": "user", "content": prompt}]
        }).encode('utf-8')

        http_req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }
        )
        with urllib.request.urlopen(http_req, timeout=30) as r:
            data = json.loads(r.read())
            gist = data["content"][0]["text"].strip()
            return gist if gist and len(gist) > 15 else _extractive_distill(session, date_str)

    except urllib.error.HTTPError as e:
        print("  Warning: HTTP error from Anthropic API ({code}) — using extractive fallback".format(code=e.code))
        return _extractive_distill(session, date_str)
    except Exception as e:
        err_name = e.__class__.__name__
        print("  Warning: LLM distill error ({err}) — using extractive fallback".format(err=err_name))
        return _extractive_distill(session, date_str)


def _extractive_distill(session, date_str):
    """Simple fallback: extract key phrases from session."""
    texts = [m['text'][:150] for m in session if len(m['text']) > 30]
    combined = ' '.join(texts[:5])
    return "Session {date_str} ({count} turns): {text}".format(
        date_str=date_str, count=len(session), text=combined[:200]
    )


# ── Capture Distillate ─────────────────────────────────────────────────────────

def capture_distillate(gist, session, dry_run=False, capture_cli_path=None):
    """
    Store distillate as a contemplation memory.
    Tries nima-core capture CLI first, then generic capture.
    """
    date_str = datetime.fromtimestamp(session[0]['timestamp'] / 1000).strftime('%Y-%m-%d')
    memory_text = "[Episodic distillation {date}] {gist}".format(date=date_str, gist=gist)

    if dry_run:
        print("  [DRY RUN] Would capture: {text}...".format(text=memory_text[:100]))
        return True

    # Try multiple capture methods
    capture_methods = []

    # Method 1: nima-core capture (if available)
    if capture_cli_path:
        capture_methods.append(('nima-core', [capture_cli_path, 'capture', 'nima', memory_text, '--importance', '0.75']))

    # Method 2: generic capture via NIMA_CAPTURE_CLI env var
    capture_env = os.environ.get('NIMA_CAPTURE_CLI', '')
    if capture_env and Path(capture_env).exists():
        capture_methods.append(('env', [capture_env, memory_text, '--importance', '0.75']))

    # Try each method
    for method_name, cmd in capture_methods:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(DATA_DIR)
            )
            if result.returncode == 0:
                return True
        except Exception:
            pass

    # If no capture method worked, just log it
    print("  Note: Could not capture distillate (no capture CLI available)")
    return False


# ── Main Pruner ────────────────────────────────────────────────────────────────

def run_pruner(min_age_days=7, dry_run=True, max_sessions=None, limbo_days=None,
               db_path=None, capture_cli_path=None):
    """
    Full pruning run:

    Args:
        min_age_days: Only consider memories older than this (default: 7)
        dry_run: If True, don't actually suppress (default: True)
        max_sessions: Limit sessions to process (default: None = all)
        limbo_days: Days before suppression becomes permanent (default: 30)
        db_path: Override database path (default: from env/NIMA_DB_PATH)
        capture_cli_path: Path to capture CLI (optional)

    Returns:
        dict with run statistics
    """
    print("\n=== Memory Pruner (nima-core) ===")
    print("Mode: {mode}".format(mode='DRY RUN' if dry_run else 'LIVE'))
    print("Config: min_age={min}d, max_sessions={max}, limbo={limbo}d\n".format(
        min=min_age_days,
        max=max_sessions if max_sessions else 'unlimited',
        limbo=limbo_days if limbo_days else DEFAULT_LIMBO_DAYS
    ))

    candidates = get_candidates(min_age_days=min_age_days, db_path=db_path)
    print("Candidates: {count} raw turns (>={min}d old)".format(
        count=len(candidates), min=min_age_days
    ))
    print("Already suppressed: {count}".format(count=len(get_suppressed_ids())))

    if not candidates:
        print("Nothing to prune.")
        return {'pruned': 0, 'sessions': 0, 'distilled': 0}

    sessions = group_by_session(candidates, gap_hours=DEFAULT_GAP_HOURS)
    if max_sessions:
        sessions = sessions[:max_sessions]
    print("Sessions to process: {count}\n".format(count=len(sessions)))

    suppressed_count = 0
    distilled_count = 0

    for i, session in enumerate(sessions):
        date_str = datetime.fromtimestamp(session[0]['timestamp'] / 1000).strftime('%Y-%m-%d')
        print("Session {idx}/{total}: {turns} turns from {date}".format(
            idx=i+1, total=len(sessions), turns=len(session), date=date_str
        ))

        # Distill
        gist = distill_session_llm(session, dry_run=dry_run)
        if not gist:
            print("  Skipped (too small)")
            continue

        print("  Gist: {gist}...".format(gist=gist[:100]))

        # Capture distillate
        captured = capture_distillate(gist, session, dry_run=dry_run, capture_cli_path=capture_cli_path)

        # Suppress in registry
        ids = [m['id'] for m in session]
        if not dry_run and captured:
            total = add_to_registry(ids, reason='distilled', distillate=gist[:200], limbo_days=limbo_days)
            print("  OK: Suppressed {count} turns (registry total: {total})".format(
                count=len(ids), total=total
            ))
            suppressed_count += len(ids)
            distilled_count += 1
        elif dry_run:
            print("  [DRY RUN] Would suppress {count} turns".format(count=len(ids)))
            suppressed_count += len(ids)
            distilled_count += 1

    summary = {
        'run_at': datetime.now().isoformat(),
        'dry_run': dry_run,
        'candidates': len(candidates),
        'sessions_processed': len(sessions),
        'distilled': distilled_count,
        'suppressed': suppressed_count,
    }

    # Log to file
    if not dry_run:
        history = []
        if LOG_PATH.exists():
            try:
                history = json.loads(LOG_PATH.read_text())
            except Exception:
                pass
        history.append(summary)
        LOG_PATH.parent.mkdir(exist_ok=True)
        LOG_PATH.write_text(json.dumps(history[-30:], indent=2))
        
        # Sync ghost marks to LadybugDB
        try:
            from nima_core.dream_db_sync import sync_pruner_to_ladybug, _get_ladybug_conn
            lb_conn = _get_ladybug_conn()
            if lb_conn:
                ghost_result = sync_pruner_to_ladybug(lb_conn)
                print("  LadybugDB ghost sync: {ghosted} marked".format(
                    ghosted=ghost_result.get('ghosted', 0)))
        except Exception as e:
            print("  LadybugDB ghost sync skipped: {err}".format(err=e))

    print("\nDone: {distilled} sessions distilled, {suppressed} turns suppressed".format(
        distilled=distilled_count, suppressed=suppressed_count
    ))
    return summary


def status():
    """Show current suppression registry status."""
    entries = list_suppressed()
    registry = load_registry()

    print("\n=== Suppression Registry Status ===")
    print("Total suppressed: {total}".format(total=len(registry)))
    print("In limbo (restorable): {limbo}".format(
        limbo=sum(1 for e in entries if e['status'] == 'limbo')
    ))

    if entries:
        print("\nMost recent suppressions:")
        for e in entries[-5:]:
            print("  ID {mid}: {reason} | {days}d remaining".format(
                mid=e['id'], reason=e['reason'], days=e['days_remaining']
            ))
            if e['distillate']:
                print("    -> {dist}".format(dist=e['distillate'][:80]))


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='NIMA Core Memory Pruner')
    parser.add_argument('--min-age', type=int, default=DEFAULT_MIN_AGE_DAYS,
                        help='Minimum age in days (default: {default})'.format(default=DEFAULT_MIN_AGE_DAYS))
    parser.add_argument('--live', action='store_true',
                        help='Actually run (default is dry-run)')
    parser.add_argument('--max-sessions', type=int, default=DEFAULT_MAX_SESSIONS,
                        help='Maximum sessions to process (default: unlimited)')
    parser.add_argument('--limbo-days', type=int, default=DEFAULT_LIMBO_DAYS,
                        help='Days in limbo before permanent (default: {default})'.format(default=DEFAULT_LIMBO_DAYS))
    parser.add_argument('--db-path', type=str, default=None,
                        help='Override database path')
    parser.add_argument('--status', action='store_true',
                        help='Show suppression registry status')
    parser.add_argument('--restore', type=int, metavar='ID',
                        help='Restore memory ID from suppression')
    parser.add_argument('--list', action='store_true',
                        help='List suppressed memories')
    parser.add_argument('--show-expired', action='store_true',
                        help='Show expired (permanently suppressed) entries')
    parser.add_argument('--version', action='store_true',
                        help='Show version')

    args = parser.parse_args()

    if args.version:
        print("NIMA Core Memory Pruner v2.3.0")
    elif args.status:
        status()
    elif args.list:
        entries = list_suppressed(show_expired=args.show_expired)
        if not entries:
            print("No suppressed memories.")
        else:
            for e in entries:
                print("[{status}] ID {mid}: {dist}".format(
                    status=e['status'], mid=e['id'], dist=e['distillate'][:60]
                ))
    elif args.restore:
        if restore_memory(args.restore):
            print("Memory {mid} restored".format(mid=args.restore))
        else:
            print("Memory {mid} not found in registry".format(mid=args.restore))
    else:
        run_pruner(
            min_age_days=args.min_age,
            dry_run=not args.live,
            max_sessions=args.max_sessions,
            limbo_days=args.limbo_days,
            db_path=args.db_path
        )
