#!/usr/bin/env python3
import os, argparse, sqlite3, datetime, json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB = os.path.join(BASE_DIR, "data", "spotify-intelligence.sqlite")


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc)


def now_iso():
    return now_utc().isoformat()


def parse_iso(s):
    if not s:
        return None
    s = str(s).strip()
    if s.endswith('Z'):
        s = s[:-1] + '+00:00'
    try:
        dt = datetime.datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt
    except Exception:
        return None


def get_policy(conn, key, default):
    r = conn.execute("SELECT value FROM governance_policy WHERE key=?", (key,)).fetchone()
    return r[0] if r and r[0] is not None else default


def in_quiet_hours(local_hour, policy):
    try:
        a, b = policy.split('-')
        start = int(a)
        end = int(b)
    except Exception:
        return False
    if start < end:
        return start <= local_hour < end
    return local_hour >= start or local_hour < end


def log_event(conn, trigger_type, action_type, decision, note):
    conn.execute(
        "INSERT INTO trigger_events(happened_at,trigger_type,action_type,decision,note) VALUES (?,?,?,?,?)",
        (now_iso(), trigger_type, action_type, decision, note),
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--action-type", required=True)
    ap.add_argument("--require-human-confirm", action="store_true")
    ap.add_argument("--human-confirm", default="false")
    args = ap.parse_args()

    conn = sqlite3.connect(DB)
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS governance_policy (
              key TEXT PRIMARY KEY,
              value TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS action_budget (
              period_key TEXT NOT NULL,
              action_type TEXT NOT NULL,
              max_actions INTEGER NOT NULL,
              used_actions INTEGER NOT NULL DEFAULT 0,
              updated_at TEXT NOT NULL,
              PRIMARY KEY(period_key, action_type)
            );
            CREATE TABLE IF NOT EXISTS trigger_events (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              happened_at TEXT NOT NULL,
              trigger_type TEXT NOT NULL,
              action_type TEXT,
              decision TEXT,
              note TEXT
            );
            """
        )

        quiet = get_policy(conn, "cleanup_prompt_quiet_hours", "23-08")
        cost_mode = get_policy(conn, "cost_mode", "lean")
        now = now_utc()
        local_hour = int((now + datetime.timedelta(hours=1)).hour)  # Berlin approx

        # human confirm gate
        hc = str(args.human_confirm).lower() == 'true'
        if args.require_human_confirm and not hc:
            log_event(conn, "preflight", args.action_type, "blocked", "human_confirm_required")
            conn.commit()
            print(json.dumps({"ok": True, "allow": False, "reason": "human_confirm_required"}))
            return

        # quiet hours block only destructive actions
        destructive = args.action_type in {"confirm_delete", "reorg_apply"}
        if destructive and in_quiet_hours(local_hour, quiet):
            log_event(conn, "preflight", args.action_type, "blocked", "quiet_hours")
            conn.commit()
            print(json.dumps({"ok": True, "allow": False, "reason": "quiet_hours"}))
            return

        period_key = conn.execute("SELECT COALESCE(MAX(period_key), strftime('%Y-W%W','now')) FROM action_budget").fetchone()[0]
        b = conn.execute(
            "SELECT max_actions, used_actions FROM action_budget WHERE period_key=? AND action_type=?",
            (period_key, args.action_type),
        ).fetchone()

        if b:
            mx, used = int(b[0]), int(b[1])
            if used >= mx:
                log_event(conn, "preflight", args.action_type, "blocked", "budget_exhausted")
                conn.commit()
                print(json.dumps({"ok": True, "allow": False, "reason": "budget_exhausted", "remaining": 0}))
                return
            remaining = mx - used
        else:
            # unknown action type in lean mode -> block by default
            if cost_mode == 'lean':
                log_event(conn, "preflight", args.action_type, "blocked", "unknown_action_type")
                conn.commit()
                print(json.dumps({"ok": True, "allow": False, "reason": "unknown_action_type"}))
                return
            remaining = None

        log_event(conn, "preflight", args.action_type, "allowed", "ok")
        conn.commit()
        print(json.dumps({"ok": True, "allow": True, "reason": "ok", "remaining": remaining}))
    finally:
        conn.close()


if __name__ == '__main__':
    main()



