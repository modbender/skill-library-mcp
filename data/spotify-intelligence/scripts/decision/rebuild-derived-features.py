#!/usr/bin/env python3
import os, sqlite3, datetime, math

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB = os.path.join(BASE_DIR, "data", "spotify-intelligence.sqlite")


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))


def main():
    conn = sqlite3.connect(DB)
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS track_derived_features (
              track_id TEXT PRIMARY KEY,
              speed_proxy REAL NOT NULL DEFAULT 0,
              energy_proxy REAL NOT NULL DEFAULT 0,
              focus_proxy REAL NOT NULL DEFAULT 0,
              mood_stability_proxy REAL NOT NULL DEFAULT 0,
              novelty_proxy REAL NOT NULL DEFAULT 0,
              confidence REAL NOT NULL DEFAULT 0,
              signals_json TEXT,
              updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS track_tags (
              track_id TEXT NOT NULL,
              tag TEXT NOT NULL,
              weight REAL NOT NULL DEFAULT 1,
              source TEXT,
              first_set_at TEXT,
              last_set_at TEXT,
              set_count INTEGER NOT NULL DEFAULT 1,
              PRIMARY KEY(track_id, tag)
            );

            CREATE TABLE IF NOT EXISTS track_play_stats (
              track_id TEXT PRIMARY KEY,
              observed_switches INTEGER NOT NULL DEFAULT 0,
              observed_skips INTEGER NOT NULL DEFAULT 0,
              observed_completions INTEGER NOT NULL DEFAULT 0,
              observed_uncertain INTEGER NOT NULL DEFAULT 0,
              total_played_ms_before_switch INTEGER NOT NULL DEFAULT 0,
              avg_played_ms_before_switch REAL NOT NULL DEFAULT 0,
              updated_at TEXT
            );

            CREATE TABLE IF NOT EXISTS read_counters (
              source TEXT NOT NULL,
              entity_type TEXT NOT NULL,
              entity_id TEXT NOT NULL,
              seen_total INTEGER NOT NULL DEFAULT 0,
              first_seen_at TEXT NOT NULL,
              last_seen_at TEXT NOT NULL,
              PRIMARY KEY(source, entity_type, entity_id)
            );

            CREATE TABLE IF NOT EXISTS track_device_volume_stats (
              track_id TEXT NOT NULL,
              device_id TEXT NOT NULL,
              device_name TEXT,
              avg_volume REAL NOT NULL DEFAULT 0,
              min_volume INTEGER,
              max_volume INTEGER,
              samples INTEGER NOT NULL DEFAULT 0,
              updated_at TEXT NOT NULL,
              PRIMARY KEY(track_id, device_id)
            );
            """
        )

        rows = conn.execute(
            """
            SELECT t.track_id,
                   COALESCE(ps.observed_switches,0),
                   COALESCE(ps.observed_skips,0),
                   COALESCE(ps.observed_completions,0),
                   COALESCE(ps.observed_uncertain,0),
                   COALESCE(ps.avg_played_ms_before_switch,0),
                   COALESCE(rc.seen_total,0),
                   COALESCE(v.avg_volume,0),
                   COALESCE(v.samples,0)
            FROM tracks t
            LEFT JOIN track_play_stats ps ON ps.track_id = t.track_id
            LEFT JOIN read_counters rc ON rc.entity_type='track' AND rc.entity_id=t.track_id AND rc.source='recently-played'
            LEFT JOIN (
              SELECT track_id, AVG(avg_volume) AS avg_volume, SUM(samples) AS samples
              FROM track_device_volume_stats
              GROUP BY track_id
            ) v ON v.track_id = t.track_id
            """
        ).fetchall()

        for (track_id, switches, skips, completions, uncertain, avg_played_ms, seen_recent, avg_volume, vol_samples) in rows:
            switches = int(switches or 0)
            skips = int(skips or 0)
            completions = int(completions or 0)
            uncertain = int(uncertain or 0)
            avg_played_ms = float(avg_played_ms or 0)
            seen_recent = int(seen_recent or 0)

            tags = [r[0] for r in conn.execute("SELECT tag FROM track_tags WHERE track_id=?", (track_id,)).fetchall()]
            tagset = set(t.lower() for t in tags)

            skip_rate = (skips / switches) if switches > 0 else 0.0
            comp_rate = (completions / switches) if switches > 0 else 0.0
            uncertain_rate = (uncertain / switches) if switches > 0 else 1.0

            # speed proxy: shorter average listened duration + hype tags + higher skip dynamics
            speed_proxy = 0.0
            if avg_played_ms > 0:
                # faster tracks are often skipped/changed earlier in energetic sessions (heuristic)
                speed_proxy += clamp((180000 - min(avg_played_ms, 180000)) / 180000)
            speed_proxy += 0.2 if ("gym" in tagset or "push" in tagset or "energie" in tagset) else 0.0
            speed_proxy += 0.1 if skip_rate > 0.6 else 0.0
            speed_proxy = clamp(speed_proxy)

            energy_proxy = 0.0
            energy_proxy += 0.35 if ("gym" in tagset or "workout" in tagset or "energie" in tagset) else 0.0
            energy_proxy += 0.2 if ("party" in tagset or "drive" in tagset) else 0.0
            energy_proxy += 0.15 if skip_rate > 0.5 else 0.0
            energy_proxy += clamp(seen_recent / 50.0) * 0.3
            energy_proxy = clamp(energy_proxy)

            focus_proxy = 0.0
            focus_proxy += 0.5 if ("focus" in tagset or "deep-work" in tagset or "konzentration" in tagset) else 0.0
            focus_proxy += 0.2 if comp_rate > 0.6 else 0.0
            focus_proxy += 0.2 if avg_played_ms > 160000 else 0.0
            focus_proxy = clamp(focus_proxy)

            mood_stability_proxy = clamp((comp_rate * 0.7) + ((1 - uncertain_rate) * 0.3))
            novelty_proxy = clamp(1.0 - min(seen_recent, 100) / 100.0)

            # volume affinity proxy (higher avg volume + enough samples => likely stronger affinity)
            volume_affinity = 0.0
            if vol_samples > 0:
                volume_affinity = clamp((float(avg_volume) / 100.0)) * clamp(vol_samples / 10.0)

            energy_proxy = clamp(energy_proxy + 0.2 * volume_affinity)
            confidence = clamp((min(switches, 30) / 30.0) * (1 - uncertain_rate) + 0.2 * clamp(vol_samples / 10.0))

            sig = {
                "switches": switches,
                "skips": skips,
                "completions": completions,
                "uncertain": uncertain,
                "avg_played_ms": avg_played_ms,
                "seen_recent": seen_recent,
                "avg_volume": float(avg_volume),
                "volume_samples": int(vol_samples),
                "volume_affinity": float(volume_affinity),
                "tags": sorted(tagset),
            }

            conn.execute(
                """
                INSERT INTO track_derived_features(track_id,speed_proxy,energy_proxy,focus_proxy,mood_stability_proxy,novelty_proxy,confidence,signals_json,updated_at)
                VALUES (?,?,?,?,?,?,?,?,?)
                ON CONFLICT(track_id) DO UPDATE SET
                  speed_proxy=excluded.speed_proxy,
                  energy_proxy=excluded.energy_proxy,
                  focus_proxy=excluded.focus_proxy,
                  mood_stability_proxy=excluded.mood_stability_proxy,
                  novelty_proxy=excluded.novelty_proxy,
                  confidence=excluded.confidence,
                  signals_json=excluded.signals_json,
                  updated_at=excluded.updated_at
                """,
                (
                    track_id,
                    speed_proxy,
                    energy_proxy,
                    focus_proxy,
                    mood_stability_proxy,
                    novelty_proxy,
                    confidence,
                    str(sig),
                    now_iso(),
                ),
            )

        conn.commit()
        print(f"ok rebuilt derived features for {len(rows)} tracks")
    finally:
        conn.close()


if __name__ == "__main__":
    main()



