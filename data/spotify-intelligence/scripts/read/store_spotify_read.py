#!/usr/bin/env python3
import os, argparse, json, sqlite3, hashlib, datetime
from pathlib import Path


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def canonical_hash(obj):
    s = json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def init_db(conn):
    conn.executescript(
        """
        PRAGMA journal_mode=WAL;

        CREATE TABLE IF NOT EXISTS endpoint_stats (
          source TEXT PRIMARY KEY,
          pull_count INTEGER NOT NULL DEFAULT 0,
          unique_payload_count INTEGER NOT NULL DEFAULT 0,
          duplicate_payload_count INTEGER NOT NULL DEFAULT 0,
          last_pull_at TEXT,
          last_status TEXT
        );

        CREATE TABLE IF NOT EXISTS payload_fingerprints (
          source TEXT NOT NULL,
          payload_hash TEXT NOT NULL,
          first_seen_at TEXT NOT NULL,
          last_seen_at TEXT NOT NULL,
          seen_count INTEGER NOT NULL DEFAULT 1,
          PRIMARY KEY(source, payload_hash)
        );

        CREATE TABLE IF NOT EXISTS users (
          user_id TEXT PRIMARY KEY,
          display_name TEXT,
          country TEXT,
          product TEXT,
          email TEXT,
          uri TEXT,
          href TEXT,
          updated_at TEXT
        );

        CREATE TABLE IF NOT EXISTS artists (
          artist_id TEXT PRIMARY KEY,
          name TEXT,
          uri TEXT,
          href TEXT,
          popularity INTEGER,
          followers_total INTEGER,
          genres_json TEXT,
          updated_at TEXT
        );

        CREATE TABLE IF NOT EXISTS albums (
          album_id TEXT PRIMARY KEY,
          name TEXT,
          uri TEXT,
          href TEXT,
          album_type TEXT,
          release_date TEXT,
          total_tracks INTEGER,
          updated_at TEXT
        );

        CREATE TABLE IF NOT EXISTS tracks (
          track_id TEXT PRIMARY KEY,
          name TEXT,
          uri TEXT,
          href TEXT,
          duration_ms INTEGER,
          explicit INTEGER,
          popularity INTEGER,
          disc_number INTEGER,
          track_number INTEGER,
          is_local INTEGER,
          album_id TEXT,
          updated_at TEXT,
          FOREIGN KEY(album_id) REFERENCES albums(album_id)
        );

        CREATE TABLE IF NOT EXISTS track_artists (
          track_id TEXT NOT NULL,
          artist_id TEXT NOT NULL,
          position INTEGER NOT NULL,
          PRIMARY KEY(track_id, artist_id),
          FOREIGN KEY(track_id) REFERENCES tracks(track_id),
          FOREIGN KEY(artist_id) REFERENCES artists(artist_id)
        );

        CREATE TABLE IF NOT EXISTS playlists (
          playlist_id TEXT PRIMARY KEY,
          name TEXT,
          description TEXT,
          owner_id TEXT,
          owner_name TEXT,
          public INTEGER,
          collaborative INTEGER,
          tracks_total INTEGER,
          snapshot_id TEXT,
          uri TEXT,
          href TEXT,
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
        """
    )


def upsert_endpoint_stats(conn, source, status, unique_payload=False, duplicate_payload=False):
    conn.execute(
        """
        INSERT INTO endpoint_stats(source, pull_count, unique_payload_count, duplicate_payload_count, last_pull_at, last_status)
        VALUES (?,1,?,?,?,?)
        ON CONFLICT(source) DO UPDATE SET
          pull_count = pull_count + 1,
          unique_payload_count = unique_payload_count + excluded.unique_payload_count,
          duplicate_payload_count = duplicate_payload_count + excluded.duplicate_payload_count,
          last_pull_at = excluded.last_pull_at,
          last_status = excluded.last_status
        """,
        (source, 1 if unique_payload else 0, 1 if duplicate_payload else 0, now_iso(), status),
    )


def register_payload_fingerprint(conn, source, payload):
    h = canonical_hash(payload)
    row = conn.execute(
        "SELECT seen_count FROM payload_fingerprints WHERE source=? AND payload_hash=?", (source, h)
    ).fetchone()
    t = now_iso()
    if row:
        conn.execute(
            "UPDATE payload_fingerprints SET seen_count = seen_count + 1, last_seen_at=? WHERE source=? AND payload_hash=?",
            (t, source, h),
        )
        upsert_endpoint_stats(conn, source, status="ok", duplicate_payload=True)
        return False, h

    conn.execute(
        "INSERT INTO payload_fingerprints(source,payload_hash,first_seen_at,last_seen_at,seen_count) VALUES (?,?,?,?,1)",
        (source, h, t, t),
    )
    upsert_endpoint_stats(conn, source, status="ok", unique_payload=True)
    return True, h


def increment_counter(conn, source, entity_type, entity_id):
    if not entity_id:
        return
    t = now_iso()
    conn.execute(
        """
        INSERT INTO read_counters(source, entity_type, entity_id, seen_total, first_seen_at, last_seen_at)
        VALUES (?,?,?,?,?,?)
        ON CONFLICT(source, entity_type, entity_id) DO UPDATE SET
          seen_total = read_counters.seen_total + 1,
          last_seen_at = excluded.last_seen_at
        """,
        (source, entity_type, entity_id, 1, t, t),
    )


def upsert_user(conn, user):
    uid = user.get("id")
    if not uid:
        return
    conn.execute(
        """
        INSERT INTO users(user_id, display_name, country, product, email, uri, href, updated_at)
        VALUES (?,?,?,?,?,?,?,?)
        ON CONFLICT(user_id) DO UPDATE SET
          display_name=excluded.display_name,
          country=excluded.country,
          product=excluded.product,
          email=excluded.email,
          uri=excluded.uri,
          href=excluded.href,
          updated_at=excluded.updated_at
        """,
        (
            uid,
            user.get("display_name"),
            user.get("country"),
            user.get("product"),
            user.get("email"),
            user.get("uri"),
            user.get("href"),
            now_iso(),
        ),
    )


def upsert_artist(conn, artist):
    aid = artist.get("id")
    if not aid:
        return
    followers = (artist.get("followers") or {}).get("total")
    genres = artist.get("genres")
    conn.execute(
        """
        INSERT INTO artists(artist_id, name, uri, href, popularity, followers_total, genres_json, updated_at)
        VALUES (?,?,?,?,?,?,?,?)
        ON CONFLICT(artist_id) DO UPDATE SET
          name=excluded.name,
          uri=excluded.uri,
          href=excluded.href,
          popularity=excluded.popularity,
          followers_total=excluded.followers_total,
          genres_json=excluded.genres_json,
          updated_at=excluded.updated_at
        """,
        (
            aid,
            artist.get("name"),
            artist.get("uri"),
            artist.get("href"),
            artist.get("popularity"),
            followers,
            json.dumps(genres, ensure_ascii=False) if genres is not None else None,
            now_iso(),
        ),
    )


def upsert_album(conn, album):
    alb_id = album.get("id")
    if not alb_id:
        return
    conn.execute(
        """
        INSERT INTO albums(album_id, name, uri, href, album_type, release_date, total_tracks, updated_at)
        VALUES (?,?,?,?,?,?,?,?)
        ON CONFLICT(album_id) DO UPDATE SET
          name=excluded.name,
          uri=excluded.uri,
          href=excluded.href,
          album_type=excluded.album_type,
          release_date=excluded.release_date,
          total_tracks=excluded.total_tracks,
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


def upsert_track(conn, track):
    tid = track.get("id")
    if not tid:
        return

    album = track.get("album") or {}
    upsert_album(conn, album)
    album_id = album.get("id")

    conn.execute(
        """
        INSERT INTO tracks(track_id, name, uri, href, duration_ms, explicit, popularity, disc_number, track_number, is_local, album_id, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(track_id) DO UPDATE SET
          name=excluded.name,
          uri=excluded.uri,
          href=excluded.href,
          duration_ms=excluded.duration_ms,
          explicit=excluded.explicit,
          popularity=excluded.popularity,
          disc_number=excluded.disc_number,
          track_number=excluded.track_number,
          is_local=excluded.is_local,
          album_id=excluded.album_id,
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
            ON CONFLICT(track_id, artist_id) DO UPDATE SET
              position=excluded.position
            """,
            (tid, aid, pos),
        )


def upsert_playlist(conn, pl):
    pid = pl.get("id")
    if not pid:
        return
    owner = pl.get("owner") or {}
    conn.execute(
        """
        INSERT INTO playlists(playlist_id, name, description, owner_id, owner_name, public, collaborative,
                              tracks_total, snapshot_id, uri, href, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(playlist_id) DO UPDATE SET
          name=excluded.name,
          description=excluded.description,
          owner_id=excluded.owner_id,
          owner_name=excluded.owner_name,
          public=excluded.public,
          collaborative=excluded.collaborative,
          tracks_total=excluded.tracks_total,
          snapshot_id=excluded.snapshot_id,
          uri=excluded.uri,
          href=excluded.href,
          updated_at=excluded.updated_at
        """,
        (
            pid,
            pl.get("name"),
            pl.get("description"),
            owner.get("id"),
            owner.get("display_name"),
            1 if pl.get("public") else 0 if pl.get("public") is not None else None,
            1 if pl.get("collaborative") else 0,
            (pl.get("tracks") or {}).get("total"),
            pl.get("snapshot_id"),
            pl.get("uri"),
            pl.get("href"),
            now_iso(),
        ),
    )


def ingest_source(conn, source, payload):
    if source == "profile":
        upsert_user(conn, payload)
        increment_counter(conn, source, "user", payload.get("id") or "unknown")
        return

    if source == "currently-playing":
        item = payload.get("item") or {}
        if item.get("id"):
            upsert_track(conn, item)
            increment_counter(conn, source, "track", item.get("id"))
        return

    if source == "recently-played":
        for it in payload.get("items", []):
            tr = (it or {}).get("track") or {}
            tid = tr.get("id")
            if not tid:
                continue
            upsert_track(conn, tr)
            increment_counter(conn, source, "track", tid)
        return

    if source in {"top-short", "top-medium", "top-long"}:
        for tr in payload.get("items", []):
            tid = (tr or {}).get("id")
            if not tid:
                continue
            upsert_track(conn, tr)
            increment_counter(conn, source, "track", tid)
        return

    if source == "playlists":
        for pl in payload.get("items", []):
            pid = (pl or {}).get("id")
            if not pid:
                continue
            upsert_playlist(conn, pl)
            increment_counter(conn, source, "playlist", pid)
        return


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--payload", required=True)
    args = ap.parse_args()

    payload = json.loads(Path(args.payload).read_text(encoding="utf-8-sig"))

    conn = sqlite3.connect(args.db)
    try:
      init_db(conn)
      is_new, h = register_payload_fingerprint(conn, args.source, payload)
      ingest_source(conn, args.source, payload)
      conn.commit()
      print(json.dumps({"ok": True, "source": args.source, "payloadHash": h, "isNewPayload": is_new}))
    finally:
      conn.close()


if __name__ == "__main__":
    main()


