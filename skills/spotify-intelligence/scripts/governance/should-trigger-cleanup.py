#!/usr/bin/env python3
import os, sqlite3, datetime, json

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


def in_quiet_hours(now_local_h, policy):
    # format like "23-08"
    try:
        a, b = policy.split('-')
        start = int(a)
        end = int(b)
    except Exception:
        return False

    if start < end:
        return start <= now_local_h < end
    return now_local_h >= start or now_local_h < end


def main():
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

        cooldown_h = float(get_policy(conn, "cleanup_prompt_cooldown_hours", "72"))
        max_per_week = int(get_policy(conn, "cleanup_prompt_max_per_week", "2"))
        quiet = get_policy(conn, "cleanup_prompt_quiet_hours", "23-08")
        auto_enabled = get_policy(conn, "auto_cleanup_enabled", "false").lower() == 'true'

        now = now_utc()
        local_h = int((now + datetime.timedelta(hours=1)).hour)  # Europe/Berlin approx without DST handling

        if in_quiet_hours(local_h, quiet):
            result = {"ok": True, "shouldTrigger": False, "reason": "quiet_hours", "autoCleanupEnabled": auto_enabled}
            print(json.dumps(result))
            return

        last_prompt = conn.execute(
            "SELECT happened_at FROM trigger_events WHERE trigger_type='cleanup_prompt' ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if last_prompt:
            dt = parse_iso(last_prompt[0])
            if dt and (now - dt).total_seconds() < cooldown_h * 3600:
                result = {"ok": True, "shouldTrigger": False, "reason": "cooldown", "autoCleanupEnabled": auto_enabled}
                print(json.dumps(result))
                return

        # weekly cap
        week_start = (now - datetime.timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        week_count = conn.execute(
            "SELECT COUNT(*) FROM trigger_events WHERE trigger_type='cleanup_prompt' AND happened_at >= ?",
            (week_start.isoformat(),)
        ).fetchone()[0]
        if week_count >= max_per_week:
            result = {"ok": True, "shouldTrigger": False, "reason": "weekly_prompt_cap", "autoCleanupEnabled": auto_enabled}
            print(json.dumps(result))
            return

        # Budget check for deep analysis/reorg
        period_key = conn.execute("SELECT COALESCE(MAX(period_key), strftime('%Y-W%W','now')) FROM action_budget").fetchone()[0]
        budget_row = conn.execute(
            "SELECT max_actions, used_actions FROM action_budget WHERE period_key=? AND action_type='deep_analysis'",
            (period_key,),
        ).fetchone()
        if budget_row:
            mx, used = budget_row
            if used >= mx:
                result = {"ok": True, "shouldTrigger": False, "reason": "budget_exhausted", "autoCleanupEnabled": auto_enabled}
                print(json.dumps(result))
                return

        # If there are proposed/staged candidates, prompt is worthwhile
        cand = conn.execute(
            "SELECT COUNT(*) FROM playlist_reorg_candidates WHERE status IN ('proposed','staged')"
        ).fetchone()[0]

        if cand <= 0:
            result = {"ok": True, "shouldTrigger": False, "reason": "no_candidates", "autoCleanupEnabled": auto_enabled}
            print(json.dumps(result))
            return

        question = f"Soll ich mal aufrÃ¤umen? Ich hÃ¤tte aktuell {cand} VorschlÃ¤ge zur PrÃ¼fung."
        result = {
            "ok": True,
            "shouldTrigger": True,
            "reason": "candidates_available",
            "candidates": cand,
            "question": question,
            "autoCleanupEnabled": auto_enabled,
        }
        print(json.dumps(result))

    finally:
        conn.close()


if __name__ == '__main__':
    main()



