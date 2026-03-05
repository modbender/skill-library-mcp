#!/usr/bin/env python3
import os, sqlite3, datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB = os.path.join(BASE_DIR, "data", "spotify-intelligence.sqlite")


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


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

        ts = now_iso()
        defaults = {
            "cleanup_prompt_cooldown_hours": "72",
            "cleanup_prompt_max_per_week": "2",
            "cleanup_prompt_quiet_hours": "23-08",
            "auto_cleanup_enabled": "false",
            "cost_mode": "lean",
        }
        for k, v in defaults.items():
            conn.execute(
                "INSERT INTO governance_policy(key,value,updated_at) VALUES (?,?,?) ON CONFLICT(key) DO NOTHING",
                (k, v, ts),
            )

        # Initialize current ISO week budgets
        week = datetime.datetime.now().strftime("%Y-W%W")
        budgets = {
            "reorg_apply": 8,
            "confirm_delete": 5,
            "feature_sync": 4,
            "deep_analysis": 3,
        }
        for action, mx in budgets.items():
            conn.execute(
                """
                INSERT INTO action_budget(period_key,action_type,max_actions,used_actions,updated_at)
                VALUES (?,?,?,?,?)
                ON CONFLICT(period_key,action_type) DO NOTHING
                """,
                (week, action, mx, 0, ts),
            )

        conn.commit()
        print("ok governance initialized")
    finally:
        conn.close()


if __name__ == "__main__":
    main()



