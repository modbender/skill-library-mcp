from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_schema(conn: sqlite3.Connection, *, schema_sql: str) -> None:
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(schema_sql)


def get_schema_sql() -> str:
    here = Path(__file__).resolve().parent
    return (here / "schema.sql").read_text(encoding="utf-8")


def apply_migrations(conn: sqlite3.Connection) -> None:
    """Apply schema and incremental migrations in order."""

    ensure_schema(conn, schema_sql=get_schema_sql())

    current = conn.execute("SELECT COALESCE(MAX(version), 0) FROM schema_migrations").fetchone()[0]

    # If this is a brand-new DB, schema.sql just created it. We can mark all known migrations
    # as applied and skip executing them, to avoid duplicate-column errors.
    is_fresh = current == 0

    here = Path(__file__).resolve().parent
    mig_dir = here / "migrations"
    migrations: list[tuple[int, Path]] = []
    for p in mig_dir.glob("*.sql"):
        if not p.name[:4].isdigit():
            continue
        migrations.append((int(p.name[:4]), p))
    migrations.sort(key=lambda x: x[0])

    for version, path in migrations:
        if version <= current:
            continue
        if version == 1:
            # 0001_init.sql uses sqlite3-shell `.read` directive; schema.sql is already applied.
            conn.execute(
                "INSERT OR IGNORE INTO schema_migrations(version, applied_at) VALUES (?, ?)",
                (version, _utc_now()),
            )
            current = version
            continue
        if not is_fresh:
            sql = path.read_text(encoding="utf-8")
            try:
                conn.executescript(sql)
            except sqlite3.DatabaseError as e:
                raise RuntimeError(f"migration failed: {path.name}: {e}")

        conn.execute(
            "INSERT OR IGNORE INTO schema_migrations(version, applied_at) VALUES (?, ?)",
            (version, _utc_now()),
        )
        current = version

    conn.commit()
