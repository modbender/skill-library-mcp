#!/usr/bin/env python3
"""
WaniKani Progress Sync Tool
Fetches user progress data from WaniKani API and stores locally for analysis.
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import argparse

import requests

API_BASE = "https://api.wanikani.com/v2"
REVISION = "20170710"
DB_FILENAME = "wanikani.db"

class WaniKaniSync:
    def __init__(self, api_token: str, data_dir: Optional[Path] = None):
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Wanikani-Revision": REVISION,
            "Content-Type": "application/json"
        }
        self.data_dir = data_dir or Path.cwd()
        self.db_path = self.data_dir / DB_FILENAME
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database with required tables."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # User info (id is UUID string)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id TEXT PRIMARY KEY,
                username TEXT,
                level INTEGER,
                max_level_granted INTEGER,
                started_at TEXT,
                subscribed INTEGER,
                subscription_type TEXT,
                period_ends_at TEXT,
                updated_at TEXT
            )
        """)

        # Assignments (user progress on subjects)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY,
                subject_id INTEGER,
                subject_type TEXT,
                srs_stage INTEGER,
                level INTEGER,
                unlocked_at TEXT,
                started_at TEXT,
                passed_at TEXT,
                burned_at TEXT,
                available_at TEXT,
                resurrected_at TEXT,
                hidden INTEGER,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # Level progressions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS level_progressions (
                id INTEGER PRIMARY KEY,
                level INTEGER,
                unlocked_at TEXT,
                started_at TEXT,
                passed_at TEXT,
                completed_at TEXT,
                abandoned_at TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # Reviews
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                assignment_id INTEGER,
                subject_id INTEGER,
                spaced_repetition_system_id INTEGER,
                starting_srs_stage INTEGER,
                ending_srs_stage INTEGER,
                incorrect_meaning_answers INTEGER,
                incorrect_reading_answers INTEGER,
                created_at TEXT
            )
        """)

        # Review statistics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS review_statistics (
                id INTEGER PRIMARY KEY,
                subject_id INTEGER,
                subject_type TEXT,
                meaning_correct INTEGER,
                meaning_current_streak INTEGER,
                meaning_incorrect INTEGER,
                meaning_max_streak INTEGER,
                reading_correct INTEGER,
                reading_current_streak INTEGER,
                reading_incorrect INTEGER,
                reading_max_streak INTEGER,
                percentage_correct REAL,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # Resets
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resets (
                id INTEGER PRIMARY KEY,
                original_level INTEGER,
                target_level INTEGER,
                confirmed_at TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # Subjects (kanji, vocabulary, radicals - the actual learning content)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY,
                object TEXT,
                characters TEXT,
                level INTEGER,
                document_url TEXT,
                meaning_mnemonic TEXT,
                reading_mnemonic TEXT,
                meanings TEXT,
                readings TEXT,
                component_subject_ids TEXT,
                amalgamation_subject_ids TEXT,
                vocabulary_ids TEXT,
                parts_of_speech TEXT,
                pronunciation_audios TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # Sync metadata
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_meta (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TEXT
            )
        """)

        conn.commit()
        conn.close()

    def _get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Make GET request to WaniKani API."""
        url = f"{API_BASE}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params or {})
        response.raise_for_status()
        return response.json()

    def _fetch_collection(self, endpoint: str, updated_after: Optional[str] = None, **filters) -> list:
        """Fetch all pages of a collection endpoint."""
        all_data = []
        params = dict(filters)
        if updated_after:
            params["updated_after"] = updated_after

        while True:
            response = self._get(endpoint, params)
            all_data.extend(response.get("data", []))

            next_url = response.get("pages", {}).get("next_url")
            if not next_url:
                break

            # Extract page_after_id from next_url
            import urllib.parse
            parsed = urllib.parse.urlparse(next_url)
            query = urllib.parse.parse_qs(parsed.query)
            if "page_after_id" in query:
                params["page_after_id"] = query["page_after_id"][0]
            else:
                break

        return all_data

    def sync_user(self) -> dict:
        """Sync user data."""
        data = self._get("user")
        user = data.get("data", {})

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user")
        cursor.execute("""
            INSERT INTO user (id, username, level, max_level_granted, started_at,
                            subscribed, subscription_type, period_ends_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user.get("id"),
            user.get("username"),
            user.get("level"),
            user.get("subscription", {}).get("max_level_granted"),
            user.get("started_at"),
            int(user.get("subscription", {}).get("active", False)),
            user.get("subscription", {}).get("type"),
            user.get("subscription", {}).get("period_ends_at"),
            data.get("data_updated_at")
        ))
        conn.commit()
        conn.close()

        return data

    def sync_assignments(self, full_sync: bool = False) -> int:
        """Sync assignments (user progress on subjects)."""
        updated_after = None if full_sync else self._get_last_sync("assignments")
        assignments = self._fetch_collection("assignments", updated_after=updated_after)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for item in assignments:
            data = item.get("data", {})
            cursor.execute("""
                INSERT OR REPLACE INTO assignments
                (id, subject_id, subject_type, srs_stage, level, unlocked_at, started_at,
                 passed_at, burned_at, available_at, resurrected_at, hidden, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.get("id"),
                data.get("subject_id"),
                data.get("subject_type"),
                data.get("srs_stage"),
                data.get("level"),
                data.get("unlocked_at"),
                data.get("started_at"),
                data.get("passed_at"),
                data.get("burned_at"),
                data.get("available_at"),
                data.get("resurrected_at"),
                int(data.get("hidden", False)),
                data.get("created_at"),
                item.get("data_updated_at")
            ))

        conn.commit()
        conn.close()

        self._set_last_sync("assignments")
        return len(assignments)

    def sync_level_progressions(self, full_sync: bool = False) -> int:
        """Sync level progression data."""
        updated_after = None if full_sync else self._get_last_sync("level_progressions")
        progressions = self._fetch_collection("level_progressions", updated_after=updated_after)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for item in progressions:
            data = item.get("data", {})
            cursor.execute("""
                INSERT OR REPLACE INTO level_progressions
                (id, level, unlocked_at, started_at, passed_at, completed_at, abandoned_at,
                 created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.get("id"),
                data.get("level"),
                data.get("unlocked_at"),
                data.get("started_at"),
                data.get("passed_at"),
                data.get("completed_at"),
                data.get("abandoned_at"),
                data.get("created_at"),
                item.get("data_updated_at")
            ))

        conn.commit()
        conn.close()

        self._set_last_sync("level_progressions")
        return len(progressions)

    def sync_reviews(self, full_sync: bool = False) -> int:
        """Sync review history."""
        updated_after = None if full_sync else self._get_last_sync("reviews")
        reviews = self._fetch_collection("reviews", updated_after=updated_after)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for item in reviews:
            data = item.get("data", {})
            cursor.execute("""
                INSERT OR REPLACE INTO reviews
                (id, assignment_id, subject_id, spaced_repetition_system_id,
                 starting_srs_stage, ending_srs_stage, incorrect_meaning_answers,
                 incorrect_reading_answers, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.get("id"),
                data.get("assignment_id"),
                data.get("subject_id"),
                data.get("spaced_repetition_system_id"),
                data.get("starting_srs_stage"),
                data.get("ending_srs_stage"),
                data.get("incorrect_meaning_answers"),
                data.get("incorrect_reading_answers"),
                data.get("created_at")
            ))

        conn.commit()
        conn.close()

        self._set_last_sync("reviews")
        return len(reviews)

    def sync_review_statistics(self, full_sync: bool = False) -> int:
        """Sync review statistics."""
        updated_after = None if full_sync else self._get_last_sync("review_statistics")
        stats = self._fetch_collection("review_statistics", updated_after=updated_after)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for item in stats:
            data = item.get("data", {})
            cursor.execute("""
                INSERT OR REPLACE INTO review_statistics
                (id, subject_id, subject_type, meaning_correct, meaning_current_streak,
                 meaning_incorrect, meaning_max_streak, reading_correct, reading_current_streak,
                 reading_incorrect, reading_max_streak, percentage_correct, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.get("id"),
                data.get("subject_id"),
                data.get("subject_type"),
                data.get("meaning_correct"),
                data.get("meaning_current_streak"),
                data.get("meaning_incorrect"),
                data.get("meaning_max_streak"),
                data.get("reading_correct"),
                data.get("reading_current_streak"),
                data.get("reading_incorrect"),
                data.get("reading_max_streak"),
                data.get("percentage_correct"),
                data.get("created_at"),
                item.get("data_updated_at")
            ))

        conn.commit()
        conn.close()

        self._set_last_sync("review_statistics")
        return len(stats)

    def sync_resets(self, full_sync: bool = False) -> int:
        """Sync reset history."""
        updated_after = None if full_sync else self._get_last_sync("resets")
        resets = self._fetch_collection("resets", updated_after=updated_after)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for item in resets:
            data = item.get("data", {})
            cursor.execute("""
                INSERT OR REPLACE INTO resets
                (id, original_level, target_level, confirmed_at, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                item.get("id"),
                data.get("original_level"),
                data.get("target_level"),
                data.get("confirmed_at"),
                data.get("created_at"),
                item.get("data_updated_at")
            ))

        conn.commit()
        conn.close()

        self._set_last_sync("resets")
        return len(resets)

    def sync_subjects(self, full_sync: bool = False, levels: Optional[list] = None) -> int:
        """Sync subject data (kanji, vocabulary, radicals).
        
        Subjects contain the actual characters, meanings, readings, and mnemonics.
        Optionally filter by levels to reduce API calls.
        """
        params = {}
        if levels:
            params["levels"] = ",".join(str(l) for l in levels)
        
        updated_after = None if full_sync else self._get_last_sync("subjects")
        subjects = self._fetch_collection("subjects", updated_after=updated_after, **params)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for item in subjects:
            data = item.get("data", {})
            
            # Extract meanings as JSON
            meanings = [m.get("meaning") for m in data.get("meanings", [])]
            
            # Extract readings as JSON (for kanji/vocab)
            readings = []
            if "readings" in data:
                readings = [r.get("reading") for r in data.get("readings", [])]
            
            # Extract component/amalgamation IDs
            component_ids = data.get("component_subject_ids", [])
            amalgamation_ids = data.get("amalgamation_subject_ids", [])
            vocab_ids = data.get("vocabulary_ids", [])
            
            cursor.execute("""
                INSERT OR REPLACE INTO subjects
                (id, object, characters, level, document_url, meaning_mnemonic,
                 reading_mnemonic, meanings, readings, component_subject_ids,
                 amalgamation_subject_ids, vocabulary_ids, parts_of_speech,
                 pronunciation_audios, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.get("id"),
                item.get("object"),
                data.get("characters"),
                data.get("level"),
                data.get("document_url"),
                data.get("meaning_mnemonic"),
                data.get("reading_mnemonic"),
                json.dumps(meanings),
                json.dumps(readings),
                json.dumps(component_ids),
                json.dumps(amalgamation_ids),
                json.dumps(vocab_ids),
                json.dumps(data.get("parts_of_speech", [])),
                json.dumps(data.get("pronunciation_audios", [])),
                data.get("created_at"),
                item.get("data_updated_at")
            ))

        conn.commit()
        conn.close()

        self._set_last_sync("subjects")
        return len(subjects)

    def _get_last_sync(self, table: str) -> Optional[str]:
        """Get timestamp of last sync for a table."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM sync_meta WHERE key = ?", (f"last_sync_{table}",))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    def _set_last_sync(self, table: str):
        """Update timestamp of last sync for a table."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        cursor.execute("""
            INSERT OR REPLACE INTO sync_meta (key, value, updated_at)
            VALUES (?, ?, ?)
        """, (f"last_sync_{table}", now, now))
        conn.commit()
        conn.close()

    def sync_all(self, full_sync: bool = False, include_subjects: bool = False, subject_levels: Optional[list] = None) -> dict:
        """Sync all WaniKani data."""
        results = {}

        print("Syncing user data...")
        results["user"] = self.sync_user()

        print("Syncing assignments...")
        results["assignments"] = self.sync_assignments(full_sync)

        print("Syncing level progressions...")
        results["level_progressions"] = self.sync_level_progressions(full_sync)

        print("Syncing reviews...")
        results["reviews"] = self.sync_reviews(full_sync)

        print("Syncing review statistics...")
        results["review_statistics"] = self.sync_review_statistics(full_sync)

        print("Syncing resets...")
        results["resets"] = self.sync_resets(full_sync)

        if include_subjects:
            print("Syncing subjects...")
            results["subjects"] = self.sync_subjects(full_sync, subject_levels)

        return results


def main():
    parser = argparse.ArgumentParser(description="Sync WaniKani progress data")
    parser.add_argument("--token", "-t", help="WaniKani API token (or set WANIKANI_API_TOKEN env var)")
    parser.add_argument("--data-dir", "-d", help="Directory to store data (default: current directory)")
    parser.add_argument("--full", "-f", action="store_true", help="Force full sync (ignore last sync time)")
    parser.add_argument("--user-only", action="store_true", help="Sync only user data")
    parser.add_argument("--assignments-only", action="store_true", help="Sync only assignments")
    parser.add_argument("--reviews-only", action="store_true", help="Sync only reviews")
    parser.add_argument("--subjects-only", action="store_true", help="Sync only subjects")
    parser.add_argument("--with-subjects", action="store_true", help="Include subjects in full sync")
    parser.add_argument("--subject-levels", help="Comma-separated levels to sync subjects (e.g., 1,2,3)")
    parser.add_argument("--stats", "-s", action="store_true", help="Show stats after sync")

    args = parser.parse_args()

    token = args.token or os.environ.get("WANIKANI_API_TOKEN")
    if not token:
        print("Error: WaniKani API token required. Provide via --token or WANIKANI_API_TOKEN env var.")
        sys.exit(1)

    data_dir = Path(args.data_dir) if args.data_dir else None

    sync = WaniKaniSync(token, data_dir)
    
    # Parse subject levels if provided
    subject_levels = None
    if args.subject_levels:
        subject_levels = [int(l.strip()) for l in args.subject_levels.split(",")]

    if args.user_only:
        result = sync.sync_user()
        print(f"User synced: {result.get('data', {}).get('username', 'unknown')} (Level {result.get('data', {}).get('level', '?')})")
    elif args.assignments_only:
        count = sync.sync_assignments(args.full)
        print(f"Synced {count} assignments")
    elif args.reviews_only:
        count = sync.sync_reviews(args.full)
        print(f"Synced {count} reviews")
    elif args.subjects_only:
        count = sync.sync_subjects(args.full, subject_levels)
        print(f"Synced {count} subjects")
    else:
        results = sync.sync_all(args.full, include_subjects=args.with_subjects, subject_levels=subject_levels)
        print("\nSync complete:")
        user = results.get("user", {}).get("data", {})
        print(f"  User: {user.get('username', 'unknown')} (Level {user.get('level', '?')})")
        print(f"  Assignments: {results.get('assignments', 0)} records")
        print(f"  Level progressions: {results.get('level_progressions', 0)} records")
        print(f"  Reviews: {results.get('reviews', 0)} records")
        print(f"  Review statistics: {results.get('review_statistics', 0)} records")
        print(f"  Resets: {results.get('resets', 0)} records")
        if args.with_subjects:
            print(f"  Subjects: {results.get('subjects', 0)} records")

    if args.stats:
        print("\nDatabase stats:")
        conn = sqlite3.connect(sync.db_path)
        cursor = conn.cursor()
        tables = ["assignments", "level_progressions", "reviews", "review_statistics", "resets", "subjects"]
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {table}: {count} rows")
            except sqlite3.OperationalError:
                print(f"  {table}: table not found")
        conn.close()


if __name__ == "__main__":
    main()
