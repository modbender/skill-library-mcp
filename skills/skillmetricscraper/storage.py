"""
storage.py — SQLite Time-Series Database (v3 — ClawHub Edition)

Schema matches real ClawHub API response fields:
  skills           — canonical skill registry (one row per slug)
  metrics_history  — daily snapshots of downloads, stars, installs

DB file: data/metrics.db
"""

import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path


DB_PATH = Path(__file__).parent / "data" / "metrics.db"


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    """Create tables if they don't exist. Drops old v2 schema if detected."""
    with _connect() as conn:
        # Detect old v2 schema and migrate
        cols = [r[1] for r in conn.execute("PRAGMA table_info(skills)").fetchall()]
        if cols and "slug" not in cols:
            print("[STORAGE] Detected v2 schema — migrating to v3...")
            conn.executescript("DROP TABLE IF EXISTS metrics_history; DROP TABLE IF EXISTS skills;")

        conn.executescript("""
            CREATE TABLE IF NOT EXISTS skills (
                slug         TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                summary      TEXT DEFAULT '',
                author       TEXT DEFAULT '',
                source_url   TEXT DEFAULT '',
                clawhub_url  TEXT DEFAULT '',
                created_at   INTEGER DEFAULT 0,
                updated_at   INTEGER DEFAULT 0,
                latest_version TEXT DEFAULT '',
                os_support   TEXT DEFAULT '',
                systems      TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS metrics_history (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                slug             TEXT NOT NULL REFERENCES skills(slug),
                timestamp        TEXT NOT NULL,
                downloads        INTEGER NOT NULL DEFAULT 0,
                stars            INTEGER NOT NULL DEFAULT 0,
                installs_current INTEGER NOT NULL DEFAULT 0,
                installs_all_time INTEGER NOT NULL DEFAULT 0,
                versions         INTEGER NOT NULL DEFAULT 0,
                comments         INTEGER NOT NULL DEFAULT 0
            );

            CREATE INDEX IF NOT EXISTS idx_metrics_slug_ts
                ON metrics_history (slug, timestamp);
        """)
    print(f"[STORAGE] DB ready: {DB_PATH}")


def upsert_skills(skills: list[dict]) -> None:
    """Insert or update skill metadata (does not touch metrics_history)."""
    with _connect() as conn:
        conn.executemany(
            """
            INSERT INTO skills (slug, display_name, summary, author, clawhub_url,
                                created_at, updated_at, latest_version, os_support, systems)
            VALUES (:slug, :display_name, :summary, :author, :clawhub_url,
                    :created_at, :updated_at, :latest_version, :os_support, :systems)
            ON CONFLICT(slug) DO UPDATE SET
                display_name   = excluded.display_name,
                summary        = excluded.summary,
                author         = excluded.author,
                clawhub_url    = excluded.clawhub_url,
                updated_at     = excluded.updated_at,
                latest_version = excluded.latest_version,
                os_support     = excluded.os_support,
                systems        = excluded.systems
            """,
            skills,
        )


def record_snapshot(skills: list[dict]) -> int:
    """
    Insert a metrics_history row for each skill with the current timestamp.
    Deduplicates per-slug: only replaces today's rows for slugs in this batch,
    preserving rows from other runs (e.g. a full 13K-skill snapshot is safe
    even if a partial --max-pages test runs later the same day).
    Returns number of rows inserted.
    """
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    today = now.strftime("%Y-%m-%d")

    with _connect() as conn:
        # Slug-scoped dedup: only delete today's rows for slugs we're about to insert
        conn.execute("CREATE TEMP TABLE IF NOT EXISTS _snap_slugs (slug TEXT)")
        conn.execute("DELETE FROM _snap_slugs")
        conn.executemany("INSERT INTO _snap_slugs VALUES (?)", [(s["slug"],) for s in skills])

        replaced = conn.execute(
            "SELECT COUNT(*) FROM metrics_history WHERE DATE(timestamp) = ? AND slug IN (SELECT slug FROM _snap_slugs)",
            (today,),
        ).fetchone()[0]
        if replaced > 0:
            conn.execute(
                "DELETE FROM metrics_history WHERE DATE(timestamp) = ? AND slug IN (SELECT slug FROM _snap_slugs)",
                (today,),
            )
            print(f"[STORAGE] Replacing {replaced} rows for {len(skills)} slugs on {today}")

        conn.execute("DROP TABLE IF EXISTS _snap_slugs")

        rows = [
            {
                "slug": s["slug"],
                "timestamp": now_iso,
                "downloads": s.get("downloads", 0),
                "stars": s.get("stars", 0),
                "installs_current": s.get("installs_current", 0),
                "installs_all_time": s.get("installs_all_time", 0),
                "versions": s.get("versions", 0),
                "comments": s.get("comments", 0),
            }
            for s in skills
        ]
        conn.executemany(
            """
            INSERT INTO metrics_history
                (slug, timestamp, downloads, stars, installs_current, installs_all_time, versions, comments)
            VALUES
                (:slug, :timestamp, :downloads, :stars, :installs_current, :installs_all_time, :versions, :comments)
            """,
            rows,
        )
    print(f"[STORAGE] Snapshot recorded: {len(rows)} skills at {now_iso[:19]}")
    return len(rows)


def get_all_velocities(days: int = 7, slug_filter: str | None = None) -> list[dict]:
    """
    Return velocity stats for all skills (or one skill) in a single SQL query.
    Uses installs_all_time (cumulative counter) as primary trending signal.
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    slug_clause = "AND m.slug = :slug_filter" if slug_filter else ""
    skills_clause = "WHERE slug = :slug_filter" if slug_filter else ""

    query = f"""
    WITH windowed AS (
        SELECT slug, timestamp, installs_current, installs_all_time, downloads, stars
        FROM metrics_history m
        WHERE timestamp >= :cutoff {slug_clause}
        GROUP BY slug, DATE(timestamp)
        HAVING timestamp = MAX(timestamp)
    ),
    bounds AS (
        SELECT slug, MIN(timestamp) AS earliest_ts, MAX(timestamp) AS latest_ts,
               COUNT(*) AS snapshots_used
        FROM windowed GROUP BY slug
    )
    SELECT
        s.slug,
        COALESCE(lw.installs_current,  0) AS latest_installs,
        COALESCE(lw.installs_all_time, 0) AS latest_installs_all_time,
        COALESCE(lw.downloads,         0) AS latest_downloads,
        COALESCE(lw.stars,             0) AS latest_stars,
        COALESCE(ew.installs_current,  COALESCE(lw.installs_current,  0)) AS earliest_installs,
        COALESCE(ew.installs_all_time, COALESCE(lw.installs_all_time, 0)) AS earliest_installs_all_time,
        COALESCE(ew.downloads,         COALESCE(lw.downloads,         0)) AS earliest_downloads,
        COALESCE(ew.stars,             COALESCE(lw.stars,             0)) AS earliest_stars,
        COALESCE(b.snapshots_used, 0) AS snapshots_used
    FROM (SELECT slug FROM skills {skills_clause}) s
    LEFT JOIN bounds   b  ON b.slug  = s.slug
    LEFT JOIN windowed lw ON lw.slug = s.slug AND lw.timestamp = b.latest_ts
    LEFT JOIN windowed ew ON ew.slug = s.slug AND ew.timestamp = b.earliest_ts
    """

    params: dict = {"cutoff": cutoff}
    if slug_filter:
        params["slug_filter"] = slug_filter

    with _connect() as conn:
        rows = conn.execute(query, params).fetchall()

    results = []
    for r in rows:
        n = r["snapshots_used"]
        zero = {
            "slug": r["slug"],
            "latest_installs": 0, "earliest_installs": 0, "installs_delta": 0,
            "latest_installs_all_time": 0, "installs_all_time_delta": 0,
            "latest_downloads": 0, "earliest_downloads": 0, "downloads_delta": 0,
            "latest_stars": 0, "earliest_stars": 0, "stars_delta": 0,
            "pct_increase": 0.0, "snapshots_used": 0,
        }

        if n == 0:
            results.append(zero)
            continue

        if n == 1:
            results.append({
                **zero,
                "latest_installs": r["latest_installs"],
                "earliest_installs": r["latest_installs"],
                "latest_installs_all_time": r["latest_installs_all_time"],
                "latest_downloads": r["latest_downloads"],
                "earliest_downloads": r["latest_downloads"],
                "latest_stars": r["latest_stars"],
                "earliest_stars": r["latest_stars"],
                "snapshots_used": 1,
            })
            continue

        iat_delta = r["latest_installs_all_time"] - r["earliest_installs_all_time"]
        dl_delta = r["latest_downloads"] - r["earliest_downloads"]
        stars_delta = r["latest_stars"] - r["earliest_stars"]
        inst_delta = r["latest_installs"] - r["earliest_installs"]

        base = r["earliest_installs_all_time"]
        pct = (iat_delta / base * 100) if base > 0 else (100.0 if iat_delta > 0 else 0.0)

        results.append({
            "slug": r["slug"],
            "latest_installs": r["latest_installs"],
            "earliest_installs": r["earliest_installs"],
            "installs_delta": inst_delta,
            "latest_installs_all_time": r["latest_installs_all_time"],
            "installs_all_time_delta": iat_delta,
            "latest_downloads": r["latest_downloads"],
            "earliest_downloads": r["earliest_downloads"],
            "downloads_delta": dl_delta,
            "latest_stars": r["latest_stars"],
            "earliest_stars": r["earliest_stars"],
            "stars_delta": stars_delta,
            "pct_increase": round(pct, 2),
            "snapshots_used": n,
        })

    return results


def get_velocity(slug: str, days: int = 7) -> dict:
    """Calculate install velocity for one skill. Thin wrapper around get_all_velocities."""
    results = get_all_velocities(days=days, slug_filter=slug)
    if results:
        return results[0]
    return {
        "slug": slug,
        "latest_installs": 0, "earliest_installs": 0, "installs_delta": 0,
        "latest_installs_all_time": 0, "installs_all_time_delta": 0,
        "latest_downloads": 0, "earliest_downloads": 0, "downloads_delta": 0,
        "latest_stars": 0, "earliest_stars": 0, "stars_delta": 0,
        "pct_increase": 0.0, "snapshots_used": 0,
    }


def get_skill(slug: str) -> dict | None:
    """Fetch skill metadata row."""
    with _connect() as conn:
        row = conn.execute("SELECT * FROM skills WHERE slug = ?", (slug,)).fetchone()
    return dict(row) if row else None


def get_latest_snapshot() -> list[dict]:
    """Return the most recent metrics_history row for each skill."""
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT m.slug, m.downloads, m.stars, m.installs_current,
                   m.installs_all_time, m.versions, m.comments, m.timestamp,
                   s.display_name, s.summary, s.author, s.clawhub_url
            FROM metrics_history m
            JOIN skills s ON s.slug = m.slug
            WHERE m.timestamp = (
                SELECT MAX(timestamp) FROM metrics_history WHERE slug = m.slug
            )
            ORDER BY m.installs_current DESC
            """
        ).fetchall()
    return [dict(r) for r in rows]


def append_snapshot(skills: list[dict]) -> int:
    """
    Append-only snapshot insert for hourly heartbeat.
    No DATE-scoped dedup — each hourly run creates distinct rows.
    Uses INSERT OR IGNORE with hour-level granularity to prevent
    accidental duplicate runs within the same hour.
    """
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()

    with _connect() as conn:
        rows = [
            (
                s["slug"], now_iso,
                s.get("downloads", 0), s.get("stars", 0),
                s.get("installs_current", 0), s.get("installs_all_time", 0),
                s.get("versions", 0), s.get("comments", 0),
            )
            for s in skills
        ]
        conn.executemany(
            """INSERT INTO metrics_history
                (slug, timestamp, downloads, stars, installs_current,
                 installs_all_time, versions, comments)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            rows,
        )
    print(f"[STORAGE] Heartbeat appended: {len(rows)} rows at {now_iso[:19]}")
    return len(rows)


def rollup_hourly(retention_days: int = 30) -> int:
    """
    Compact hourly data older than retention_days.
    Keeps only the last row per slug per day for old data.
    Returns number of rows deleted.
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(days=retention_days)).strftime("%Y-%m-%d")

    with _connect() as conn:
        # Count before
        before = conn.execute("SELECT COUNT(*) FROM metrics_history").fetchone()[0]

        # Keep only the max(id) per slug per date for rows older than cutoff
        conn.execute("""
            DELETE FROM metrics_history
            WHERE DATE(timestamp) < :cutoff
              AND id NOT IN (
                  SELECT MAX(id) FROM metrics_history
                  WHERE DATE(timestamp) < :cutoff
                  GROUP BY slug, DATE(timestamp)
              )
        """, {"cutoff": cutoff})

        after = conn.execute("SELECT COUNT(*) FROM metrics_history").fetchone()[0]
        deleted = before - after

    if deleted > 0:
        print(f"[STORAGE] Rollup: deleted {deleted} hourly rows older than {cutoff}")
    return deleted


def init_project_metadata() -> None:
    """Create project_metadata table for tracking OpenClaw ecosystem repos."""
    with _connect() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS project_metadata (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                repo                TEXT NOT NULL,
                timestamp           TEXT NOT NULL,
                stars               INTEGER DEFAULT 0,
                forks               INTEGER DEFAULT 0,
                open_issues         INTEGER DEFAULT 0,
                open_prs            INTEGER DEFAULT 0,
                watchers            INTEGER DEFAULT 0,
                latest_release      TEXT DEFAULT '',
                latest_release_date TEXT DEFAULT '',
                weekly_commits      INTEGER DEFAULT 0
            );
            CREATE INDEX IF NOT EXISTS idx_project_repo_ts
                ON project_metadata(repo, timestamp);
        """)


def record_project_metadata(entries: list[dict]) -> int:
    """Insert project metadata rows."""
    now_iso = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        rows = [
            (
                e["repo"], now_iso,
                e.get("stars", 0), e.get("forks", 0),
                e.get("open_issues", 0), e.get("open_prs", 0),
                e.get("watchers", 0), e.get("latest_release", ""),
                e.get("latest_release_date", ""), e.get("weekly_commits", 0),
            )
            for e in entries
        ]
        conn.executemany(
            """INSERT INTO project_metadata
                (repo, timestamp, stars, forks, open_issues, open_prs,
                 watchers, latest_release, latest_release_date, weekly_commits)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            rows,
        )
    print(f"[STORAGE] Project metadata: {len(rows)} repos at {now_iso[:19]}")
    return len(rows)


def get_skill_history(slug: str, days: int = 30) -> list[dict]:
    """Return daily time-series for a single skill (one row per day, last N days)."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    with _connect() as conn:
        rows = conn.execute("""
            SELECT DATE(timestamp) as date,
                   MAX(downloads) as downloads,
                   MAX(stars) as stars,
                   MAX(installs_all_time) as installs_all_time,
                   MAX(installs_current) as installs_current,
                   MAX(comments) as comments
            FROM metrics_history
            WHERE slug = :slug AND DATE(timestamp) >= :cutoff
            GROUP BY DATE(timestamp)
            ORDER BY date ASC
        """, {"slug": slug, "cutoff": cutoff}).fetchall()
    return [dict(r) for r in rows]


def get_catalog_history(days: int = 30) -> list[dict]:
    """Return daily catalog aggregates (total skills, downloads, installs, stars).
    Uses MAX per slug per day to avoid double-counting from multiple snapshots."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    with _connect() as conn:
        rows = conn.execute("""
            SELECT date,
                   COUNT(*) as total_skills,
                   SUM(max_dl) as total_downloads,
                   SUM(max_iat) as total_installs,
                   SUM(max_stars) as total_stars
            FROM (
                SELECT DATE(timestamp) as date, slug,
                       MAX(downloads) as max_dl,
                       MAX(installs_all_time) as max_iat,
                       MAX(stars) as max_stars
                FROM metrics_history
                WHERE DATE(timestamp) >= :cutoff
                GROUP BY DATE(timestamp), slug
            )
            GROUP BY date
            ORDER BY date ASC
        """, {"cutoff": cutoff}).fetchall()
    return [dict(r) for r in rows]


def get_project_history(days: int = 30) -> list[dict]:
    """Return project metadata time-series for all tracked repos."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    with _connect() as conn:
        rows = conn.execute("""
            SELECT repo, DATE(timestamp) as date,
                   MAX(stars) as stars, MAX(forks) as forks,
                   MAX(open_issues) as open_issues, MAX(open_prs) as open_prs,
                   MAX(watchers) as watchers, MAX(weekly_commits) as weekly_commits,
                   MAX(latest_release) as latest_release
            FROM project_metadata
            WHERE DATE(timestamp) >= :cutoff
            GROUP BY repo, DATE(timestamp)
            ORDER BY repo, date ASC
        """, {"cutoff": cutoff}).fetchall()
    return [dict(r) for r in rows]


def snapshot_count() -> int:
    """Return total number of snapshot rows."""
    with _connect() as conn:
        return conn.execute("SELECT COUNT(*) FROM metrics_history").fetchone()[0]


def distinct_snapshot_dates() -> list[str]:
    """Return distinct snapshot dates (YYYY-MM-DD) ordered ascending."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT DISTINCT DATE(timestamp) as d FROM metrics_history ORDER BY d ASC"
        ).fetchall()
    return [r["d"] for r in rows]
