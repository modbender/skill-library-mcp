#!/usr/bin/env python3
import os, argparse
import os, json
import os, sqlite3
import os, datetime
from pathlib import Path


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def table_has_column(conn, table_name, column_name):
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return any(r[1] == column_name for r in rows)


def init_db(conn):
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS playlist_track_membership (
          playlist_id TEXT NOT NULL,
          track_id TEXT NOT NULL,
          added_at TEXT,
          added_by_user_id TEXT,
          first_added_at TEXT,
          last_added_at TEXT,
          first_seen_at TEXT NOT NULL,
          last_seen_at TEXT NOT NULL,
          times_seen INTEGER NOT NULL DEFAULT 1,
          currently_present INTEGER NOT NULL DEFAULT 1,
          PRIMARY KEY(playlist_id, track_id)
        );

        CREATE TABLE IF NOT EXISTS playlist_track_removals (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          removed_at TEXT NOT NULL,
          playlist_id TEXT NOT NULL,
          track_id TEXT NOT NULL,
          source TEXT NOT NULL DEFAULT 'sync_snapshot',
          removal_reason TEXT,
          previous_added_at TEXT,
          previous_first_added_at TEXT,
          previous_last_added_at TEXT,
          previous_last_seen_at TEXT,
          restore_status TEXT NOT NULL DEFAULT 'available',
          restored_at TEXT,
          UNIQUE(playlist_id, track_id, removed_at)
        );

        CREATE INDEX IF NOT EXISTS idx_ptm_track ON playlist_track_membership(track_id);
        CREATE INDEX IF NOT EXISTS idx_ptm_playlist ON playlist_track_membership(playlist_id);
        CREATE INDEX IF NOT EXISTS idx_ptr_playlist_track ON playlist_track_removals(playlist_id, track_id);
        """
    )

    # Forward migrations for older local DBs
    wanted = {
        "added_at": "TEXT",
        "added_by_user_id": "TEXT",
        "first_added_at": "TEXT",
        "last_added_at": "TEXT",
        "first_seen_at": "TEXT",
        "last_seen_at": "TEXT",
        "times_seen": "INTEGER NOT NULL DEFAULT 1",
        "currently_present": "INTEGER NOT NULL DEFAULT 1",
    }
    for col, typ in wanted.items():
        if not table_has_column(conn, "playlist_track_membership", col):
            conn.execute(f"ALTER TABLE playlist_track_membership ADD COLUMN {col} {typ}")


def upsert_artist(conn, artist):
    aid = (artist or {}).get("id")
    if not aid:
        return
    conn.execute(
        """
        INSERT INTO artists(artist_id, name, uri, href, popularity, followers_total, genres_json, updated_at)
        VALUES (?,?,?,?,?,?,?,?)
        ON CONFLICT(artist_id) DO UPDATE SET
          name=excluded.name,
          uri=excluded.uri,
          href=excluded.href,
          popularity=COALESCE(excluded.popularity, artists.popularity),
          followers_total=COALESCE(excluded.followers_total, artists.followers_total),
          genres_json=COALESCE(excluded.genres_json, artists.genres_json),
          updated_at=excluded.updated_at
        """,
        (aid, artist.get("name"), artist.get("uri"), artist.get("href"), artist.get("popularity"), None, None, now_iso()),
    )


def upsert_album(conn, album):
    alb_id = (album or {}).get("id")
    if not alb_id:
        return None
    conn.execute(
        """
        INSERT INTO albums(album_id, name, uri, href, album_type, release_date, total_tracks, updated_at)
        VALUES (?,?,?,?,?,?,?,?)
        ON CONFLICT(album_id) DO UPDATE SET
          name=excluded.name,
          uri=excluded.uri,
          href=excluded.href,
          album_type=COALESCE(excluded.album_type, albums.album_type),
          release_date=COALESCE(excluded.release_date, albums.release_date),
          total_tracks=COALESCE(excluded.total_tracks, albums.total_tracks),
          updated_at=excluded.updated_at
        """,
        (
            alb_id,
            album.get("name"),
            album.get("uri"),
            album.get("href"),
            album.get("album_type"),
            album.get("release_date"),
            album.get("total_tracks"),
            now_iso(),
        ),
    )
    return alb_id


def upsert_track(conn, track):
    tid = (track or {}).get("id")
    if not tid:
        return None

    album_id = upsert_album(conn, track.get("album") or {})
    conn.execute(
        """
        INSERT INTO tracks(track_id, name, uri, href, duration_ms, explicit, popularity, disc_number, track_number, is_local, album_id, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(track_id) DO UPDATE SET
          name=excluded.name,
          uri=excluded.uri,
          href=excluded.href,
          duration_ms=COALESCE(excluded.duration_ms, tracks.duration_ms),
          explicit=COALESCE(excluded.explicit, tracks.explicit),
          popularity=COALESCE(excluded.popularity, tracks.popularity),
          disc_number=COALESCE(excluded.disc_number, tracks.disc_number),
          track_number=COALESCE(excluded.track_number, tracks.track_number),
          is_local=COALESCE(excluded.is_local, tracks.is_local),
          album_id=COALESCE(excluded.album_id, tracks.album_id),
          updated_at=excluded.updated_at
        """,
        (
            tid,
            track.get("name"),
            track.get("uri"),
            track.get("href"),
            track.get("duration_ms"),
            1 if track.get("explicit") else 0,
            track.get("popularity"),
            track.get("disc_number"),
            track.get("track_number"),
            1 if track.get("is_local") else 0,
            album_id,
            now_iso(),
        ),
    )

    artists = track.get("artists") or []
    for pos, a in enumerate(artists, start=1):
        aid = a.get("id")
        if not aid:
            continue
        upsert_artist(conn, a)
        conn.execute(
            """
            INSERT INTO track_artists(track_id, artist_id, position)
            VALUES (?,?,?)
            ON CONFLICT(track_id, artist_id) DO UPDATE SET position=excluded.position
            """,
            (tid, aid, pos),
        )

    return tid


def upsert_membership(conn, playlist_id, track_id, added_at, added_by_user_id):
    t = now_iso()
    existing = conn.execute(
        "SELECT first_added_at, last_added_at FROM playlist_track_membership WHERE playlist_id=? AND track_id=?",
        (playlist_id, track_id),
    ).fetchone()

    if existing:
        first_added, last_added = existing
        new_first = first_added or added_at
        if added_at and first_added and added_at < first_added:
            new_first = added_at
        new_last = last_added or added_at
        if added_at and last_added and added_at > last_added:
            new_last = added_at

        conn.execute(
            """
            UPDATE playlist_track_membership
            SET added_at = COALESCE(?, added_at),
                added_by_user_id = COALESCE(?, added_by_user_id),
                first_added_at = ?,
                last_added_at = ?,
                last_seen_at = ?,
                times_seen = times_seen + 1,
                currently_present = 1
            WHERE playlist_id=? AND track_id=?
            """,
            (added_at, added_by_user_id, new_first, new_last, t, playlist_id, track_id),
        )
    else:
        conn.execute(
            """
            INSERT INTO playlist_track_membership(
              playlist_id, track_id, added_at, added_by_user_id,
              first_added_at, last_added_at,
              first_seen_at, last_seen_at, times_seen, currently_present
            ) VALUES (?,?,?,?,?,?,?,?,1,1)
            """,
            (playlist_id, track_id, added_at, added_by_user_id, added_at, added_at, t, t),
        )


def mark_removed_memberships(conn, playlist_id, present_track_ids):
    existing_rows = conn.execute(
        """
        SELECT track_id, added_at, first_added_at, last_added_at, last_seen_at
        FROM playlist_track_membership
        WHERE playlist_id=? AND currently_present=1
        """,
        (playlist_id,),
    ).fetchall()

    removed = 0
    t = now_iso()
    present = set(present_track_ids)

    for track_id, added_at, first_added_at, last_added_at, prev_last_seen in existing_rows:
        if track_id in present:
            continue

        conn.execute(
            """
            UPDATE playlist_track_membership
            SET currently_present=0,
                last_seen_at=?
            WHERE playlist_id=? AND track_id=?
            """,
            (t, playlist_id, track_id),
        )

        conn.execute(
            """
            INSERT INTO playlist_track_removals(
              removed_at, playlist_id, track_id, source, removal_reason,
              previous_added_at, previous_first_added_at, previous_last_added_at, previous_last_seen_at
            ) VALUES (?,?,?,?,?,?,?,?,?)
            """,
            (
                t,
                playlist_id,
                track_id,
                "sync_snapshot",
                "missing_in_latest_snapshot",
                added_at,
                first_added_at,
                last_added_at,
                prev_last_seen,
            ),
        )
        removed += 1

    return removed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--payload", required=True)
    args = ap.parse_args()

    payload = json.loads(Path(args.payload).read_text(encoding="utf-8-sig"))
    playlist_id = payload.get("playlist_id")
    items = payload.get("items") or []
    if not playlist_id:
        raise ValueError("payload.playlist_id required")

    conn = sqlite3.connect(args.db)
    try:
        init_db(conn)

        present_track_ids = []
        processed = 0
        for it in items:
            tr = (it or {}).get("track") or {}
            tid = upsert_track(conn, tr)
            if not tid:
                continue
            present_track_ids.append(tid)
            added_at = it.get("added_at")
            added_by = ((it.get("added_by") or {}).get("id"))
            upsert_membership(conn, playlist_id, tid, added_at, added_by)
            processed += 1

        removed = mark_removed_memberships(conn, playlist_id, present_track_ids)

        conn.commit()
        print(json.dumps({
            "ok": True,
            "playlistId": playlist_id,
            "tracksProcessed": processed,
            "tracksMarkedRemoved": removed
        }))
    finally:
        conn.close()


if __name__ == "__main__":
    main()


