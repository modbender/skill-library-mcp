#!/usr/bin/env python3
import os, argparse, sqlite3, json, datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB = os.path.join(BASE_DIR, "data", "spotify-intelligence.sqlite")

def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def ensure(conn):
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS recommend_runs (
          run_id TEXT PRIMARY KEY,
          generated_at TEXT NOT NULL,
          mode TEXT NOT NULL,
          top_n INTEGER NOT NULL,
          context_json TEXT
        );
        CREATE TABLE IF NOT EXISTS recommend_items (
          run_id TEXT NOT NULL,
          rank_no INTEGER NOT NULL,
          track_id TEXT NOT NULL,
          track_name TEXT,
          artists TEXT,
          score REAL NOT NULL,
          reason TEXT,
          queued INTEGER NOT NULL DEFAULT 0,
          PRIMARY KEY(run_id, rank_no)
        );
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
        CREATE TABLE IF NOT EXISTS tracks (
          track_id TEXT PRIMARY KEY,
          name TEXT,
          artists TEXT,
          uri TEXT,
          updated_at TEXT
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
        CREATE TABLE IF NOT EXISTS track_feedback_profile (
          track_id TEXT PRIMARY KEY,
          like_count INTEGER NOT NULL DEFAULT 0,
          dislike_count INTEGER NOT NULL DEFAULT 0,
          skip_count INTEGER NOT NULL DEFAULT 0,
          keep_count INTEGER NOT NULL DEFAULT 0,
          dont_ask_again INTEGER NOT NULL DEFAULT 0,
          updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS device_context_profiles (
          device_name TEXT PRIMARY KEY,
          context_tag TEXT,
          bass_preference REAL NOT NULL DEFAULT 0.5,
          focus_preference REAL NOT NULL DEFAULT 0.5,
          energy_preference REAL NOT NULL DEFAULT 0.5,
          auto_volume_enabled INTEGER NOT NULL DEFAULT 1,
          updated_at TEXT NOT NULL
        );
        """
    )

def score_row(mode, speed, energy, focus, stability, novelty, confidence, tags, likes, dislikes, skips, keeps, d_focus, d_energy):
    score = 0.0
    reason = []
    if mode == "passend":
        score = (0.25 * focus) + (0.25 * energy) + (0.20 * stability) + (0.20 * confidence) + (0.10 * (1 - novelty))
        reason.append("balanced-fit")
    elif mode == "mood-shift":
        score = (0.45 * stability) + (0.30 * energy) + (0.15 * confidence) + (0.10 * (1 - novelty))
        if "heartbreak" in tags:
            score -= 0.15
            reason.append("heartbreak-penalty")
        reason.append("stability-shift")
    else:
        score = (0.50 * novelty) + (0.20 * confidence) + (0.15 * speed) + (0.15 * energy)
        reason.append("novelty-priority")

    # device-aware weighting
    score += 0.15 * d_focus * focus
    score += 0.15 * d_energy * energy
    if d_focus > 0.6:
        reason.append("device-focus-boost")
    if d_energy > 0.6:
        reason.append("device-energy-boost")

    if likes > 0 or keeps > 0:
        score += min(0.25, 0.05 * likes + 0.04 * keeps)
        reason.append("positive-feedback")
    if dislikes > 0 or skips > 0:
        score -= min(0.35, 0.07 * dislikes + 0.04 * skips)
        reason.append("negative-feedback")

    return score, ",".join(reason)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["passend", "mood-shift", "explore"], default="passend")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--device-name", default="")
    args = ap.parse_args()

    conn = sqlite3.connect(DB)
    try:
        ensure(conn)
        d_focus = d_energy = 0.5
        ctx = {"source": "derived_features"}
        if args.device_name:
            row = conn.execute("SELECT context_tag,focus_preference,energy_preference FROM device_context_profiles WHERE device_name=?", (args.device_name,)).fetchone()
            if row:
                ctx["device_name"] = args.device_name
                ctx["context_tag"] = row[0]
                d_focus = float(row[1] or 0.5)
                d_energy = float(row[2] or 0.5)

        rows = conn.execute(
            """
            SELECT t.track_id, t.name, t.artists,
                   COALESCE(df.speed_proxy,0), COALESCE(df.energy_proxy,0), COALESCE(df.focus_proxy,0),
                   COALESCE(df.mood_stability_proxy,0), COALESCE(df.novelty_proxy,0), COALESCE(df.confidence,0),
                   COALESCE(fp.like_count,0), COALESCE(fp.dislike_count,0), COALESCE(fp.skip_count,0), COALESCE(fp.keep_count,0)
            FROM tracks t
            LEFT JOIN track_derived_features df ON df.track_id = t.track_id
            LEFT JOIN track_feedback_profile fp ON fp.track_id = t.track_id
            """
        ).fetchall()

        scored = []
        for r in rows:
            track_id, name, artists, speed, energy, focus, stability, novelty, confidence, likes, dislikes, skips, keeps = r
            tags = set(x[0] for x in conn.execute("SELECT tag FROM track_tags WHERE track_id=?", (track_id,)).fetchall())

            # hard negative guardrail: if strongly negative and not positively reinforced, skip
            if (dislikes >= 2 or skips >= 5) and (likes + keeps) == 0:
                continue

            score, reason = score_row(args.mode, speed, energy, focus, stability, novelty, confidence, tags, likes, dislikes, skips, keeps, d_focus, d_energy)
            scored.append((track_id, name, artists, float(score), reason))

        scored.sort(key=lambda x: x[3], reverse=True)

        # diversity pass: avoid same lead artist dominating top list
        top = []
        artist_seen = {}
        for item in scored:
            if len(top) >= max(1, args.top):
                break
            artists = item[2] or ""
            lead = artists.split(',')[0].strip().lower() if artists else "unknown"
            cnt = artist_seen.get(lead, 0)
            if cnt >= 2:
                continue
            artist_seen[lead] = cnt + 1
            top.append(item)

        if len(top) < max(1, args.top):
            for item in scored:
                if len(top) >= max(1, args.top):
                    break
                if item in top:
                    continue
                top.append(item)
        run_id = datetime.datetime.now(datetime.timezone.utc).strftime("rec_%Y%m%dT%H%M%SZ")

        conn.execute("INSERT INTO recommend_runs(run_id,generated_at,mode,top_n,context_json) VALUES (?,?,?,?,?)", (run_id, now_iso(), args.mode, args.top, json.dumps(ctx)))
        for idx, (tid, n, a, s, reason) in enumerate(top, start=1):
            conn.execute("INSERT INTO recommend_items(run_id,rank_no,track_id,track_name,artists,score,reason,queued) VALUES (?,?,?,?,?,?,?,0)", (run_id, idx, tid, n, a, s, reason))
        conn.commit()
        print(json.dumps({"ok": True, "runId": run_id, "mode": args.mode, "count": len(top), "device": args.device_name or None}))
    finally:
        conn.close()

if __name__ == "__main__":
    main()



