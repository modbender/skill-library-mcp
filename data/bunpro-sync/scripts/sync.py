#!/usr/bin/env python3
"""
Bunpro Grammar Sync Tool
Fetches Japanese grammar progress from Bunpro API and stores locally for analysis.
Uses the community-documented API at api.bunpro.jp/api/frontend
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

API_BASE = "https://api.bunpro.jp/api/frontend"
DB_FILENAME = "bunpro.db"


class BunproSync:
    def __init__(self, api_token: str, data_dir: Optional[Path] = None):
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Accept": "application/json",
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

        # User info
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY,
                username TEXT,
                level INTEGER,
                xp INTEGER,
                is_lifetime INTEGER,
                buncoin INTEGER,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # Grammar points (the learning content)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grammar_points (
                id INTEGER PRIMARY KEY,
                title TEXT,
                meaning TEXT,
                structure TEXT,
                caution TEXT,
                level TEXT,
                jlpt_level TEXT,
                unit TEXT,
                lesson INTEGER,
                grammar TEXT,
                casual TEXT,
                spoken TEXT,
                nuance TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # Reviews (SRS progress on grammar)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                reviewable_id INTEGER,
                reviewable_type TEXT,
                grammar_point_id INTEGER,
                srs_stage INTEGER,
                srs_stage_string TEXT,
                next_review TEXT,
                last_review TEXT,
                burned INTEGER,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # Study queue (due items)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_queue (
                id INTEGER PRIMARY KEY,
                reviewable_id INTEGER,
                reviewable_type TEXT,
                available_at TEXT
            )
        """)

        # Due items (immediate reviews)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS due_items (
                id INTEGER PRIMARY KEY,
                reviewable_id INTEGER,
                reviewable_type TEXT,
                available_at TEXT,
                is_leech INTEGER,
                streak INTEGER
            )
        """)

        # User stats
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_stats (
                stat_type TEXT PRIMARY KEY,
                data TEXT,
                updated_at TEXT
            )
        """)

        # Review history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS review_histories (
                id INTEGER PRIMARY KEY,
                session_type TEXT,
                started_at TEXT,
                ended_at TEXT,
                total_reviews INTEGER,
                correct_reviews INTEGER,
                created_at TEXT
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
        """Make GET request to Bunpro API."""
        url = f"{API_BASE}{endpoint}"
        response = requests.get(url, headers=self.headers, params=params or {}, timeout=30)
        response.raise_for_status()
        return response.json()

    def sync_user(self) -> dict:
        """Sync user data."""
        data = self._get("/user")
        
        # Extract user from nested structure
        user_data = data.get("user", {}).get("data", {}).get("attributes", {})
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user")
        cursor.execute("""
            INSERT INTO user (id, username, level, xp, is_lifetime, buncoin, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_data.get("id"),
            user_data.get("username"),
            user_data.get("level"),
            user_data.get("xp"),
            int(user_data.get("is_lifetime", False)),
            user_data.get("buncoin"),
            user_data.get("created_at"),
            datetime.now(timezone.utc).isoformat()
        ))
        conn.commit()
        conn.close()
        
        return data

    def sync_queue(self) -> int:
        """Sync study queue (items due for review)."""
        data = self._get("/user/queue")
        queue_items = data.get("data", [])

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM study_queue")
        
        for item in queue_items:
            attrs = item.get("attributes", {})
            cursor.execute("""
                INSERT INTO study_queue (id, reviewable_id, reviewable_type, available_at)
                VALUES (?, ?, ?, ?)
            """, (
                item.get("id"),
                attrs.get("reviewable_id"),
                attrs.get("reviewable_type"),
                attrs.get("available_at")
            ))
        
        conn.commit()
        conn.close()
        return len(queue_items)

    def sync_due_items(self) -> int:
        """Sync due items (immediate reviews)."""
        data = self._get("/user/due")
        due_items = data.get("data", [])

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM due_items")
        
        for item in due_items:
            attrs = item.get("attributes", {})
            cursor.execute("""
                INSERT INTO due_items (id, reviewable_id, reviewable_type, available_at, is_leech, streak)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                item.get("id"),
                attrs.get("reviewable_id"),
                attrs.get("reviewable_type"),
                attrs.get("available_at"),
                int(attrs.get("is_leech", False)),
                attrs.get("streak")
            ))
        
        conn.commit()
        conn.close()
        return len(due_items)

    def sync_reviews(self, page: int = 1, per_page: int = 100) -> int:
        """Sync all grammar reviews with pagination."""
        all_reviews = []
        current_page = page
        
        while True:
            data = self._get("/reviews", {"page": current_page, "per_page": per_page})
            reviews = data.get("data", [])
            
            if not reviews:
                break
                
            all_reviews.extend(reviews)
            
            # Check if there are more pages
            total = data.get("meta", {}).get("total", 0)
            if len(all_reviews) >= total or len(reviews) < per_page:
                break
                
            current_page += 1

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reviews")
        
        for item in all_reviews:
            attrs = item.get("attributes", {})
            cursor.execute("""
                INSERT INTO reviews 
                (id, reviewable_id, reviewable_type, grammar_point_id, srs_stage, srs_stage_string,
                 next_review, last_review, burned, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.get("id"),
                attrs.get("reviewable_id"),
                attrs.get("reviewable_type"),
                attrs.get("grammar_point_id"),
                attrs.get("srs_stage"),
                attrs.get("srs_stage_string"),
                attrs.get("next_review"),
                attrs.get("last_review"),
                int(attrs.get("burned", False)),
                attrs.get("created_at"),
                attrs.get("updated_at")
            ))
        
        conn.commit()
        conn.close()
        return len(all_reviews)

    def sync_user_stats(self) -> dict:
        """Sync various user statistics."""
        stat_endpoints = {
            "base_stats": "/user_stats/base_stats",
            "jlpt_progress": "/user_stats/jlpt_progress_mixed",
            "forecast_daily": "/user_stats/forecast_daily",
            "forecast_hourly": "/user_stats/forecast_hourly",
            "srs_overview": "/user_stats/srs_level_overview",
            "review_activity": "/user_stats/review_activity"
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        results = {}
        for stat_name, endpoint in stat_endpoints.items():
            try:
                data = self._get(endpoint)
                cursor.execute("""
                    INSERT OR REPLACE INTO user_stats (stat_type, data, updated_at)
                    VALUES (?, ?, ?)
                """, (
                    stat_name,
                    json.dumps(data),
                    datetime.now(timezone.utc).isoformat()
                ))
                results[stat_name] = len(json.dumps(data))
            except Exception as e:
                print(f"Warning: Could not sync {stat_name}: {e}")
                results[stat_name] = 0
        
        conn.commit()
        conn.close()
        return results

    def sync_review_histories(self) -> dict:
        """Sync review session history."""
        results = {}
        
        try:
            # Last session
            data = self._get("/review_histories/last_session")
            results["last_session"] = data
        except Exception as e:
            print(f"Warning: Could not sync last session: {e}")
        
        try:
            # Last 24 hours
            data = self._get("/review_histories/last_24_hours")
            results["last_24h"] = data
        except Exception as e:
            print(f"Warning: Could not sync last 24h: {e}")
        
        return results

    def sync_all(self, full_sync: bool = False) -> dict:
        """Sync all Bunpro data."""
        results = {}

        print("Syncing user data...")
        try:
            results["user"] = self.sync_user()
        except Exception as e:
            print(f"Error syncing user: {e}")
            results["user"] = None

        print("Syncing study queue...")
        try:
            results["queue"] = self.sync_queue()
        except Exception as e:
            print(f"Error syncing queue: {e}")
            results["queue"] = 0

        print("Syncing due items...")
        try:
            results["due"] = self.sync_due_items()
        except Exception as e:
            print(f"Error syncing due: {e}")
            results["due"] = 0

        print("Syncing reviews...")
        try:
            results["reviews"] = self.sync_reviews()
        except Exception as e:
            print(f"Error syncing reviews: {e}")
            results["reviews"] = 0

        print("Syncing user stats...")
        try:
            results["stats"] = self.sync_user_stats()
        except Exception as e:
            print(f"Error syncing stats: {e}")
            results["stats"] = {}

        print("Syncing review histories...")
        try:
            results["histories"] = self.sync_review_histories()
        except Exception as e:
            print(f"Error syncing histories: {e}")
            results["histories"] = {}

        return results


def main():
    parser = argparse.ArgumentParser(description="Sync Bunpro grammar progress data")
    parser.add_argument("--token", "-t", help="Bunpro Frontend API token (or set BUNPRO_API_TOKEN env var)")
    parser.add_argument("--data-dir", "-d", help="Directory to store data (default: current directory)")
    parser.add_argument("--full", "-f", action="store_true", help="Force full sync")
    parser.add_argument("--user-only", action="store_true", help="Sync only user data")
    parser.add_argument("--queue-only", action="store_true", help="Sync only study queue")
    parser.add_argument("--reviews-only", action="store_true", help="Sync only reviews")
    parser.add_argument("--stats", "-s", action="store_true", help="Show stats after sync")

    args = parser.parse_args()

    token = args.token or os.environ.get("BUNPRO_API_TOKEN")
    if not token:
        print("Error: Bunpro API token required. Provide via --token or BUNPRO_API_TOKEN env var.")
        print("\nTo get your token:")
        print("1. Go to bunpro.jp and log in")
        print("2. Open browser DevTools (F12) → Console")
        print("3. Look for FRONTEND_API_TOKEN or check Application/Local Storage")
        print("4. The token is in the Authorization: Bearer header of API calls")
        sys.exit(1)

    data_dir = Path(args.data_dir) if args.data_dir else None

    sync = BunproSync(token, data_dir)

    if args.user_only:
        try:
            result = sync.sync_user()
            user = result.get("user", {}).get("data", {}).get("attributes", {})
            print(f"User synced: {user.get('username', 'unknown')} (Level {user.get('level', '?')})")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    elif args.queue_only:
        try:
            count = sync.sync_queue()
            print(f"Synced {count} queue items")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    elif args.reviews_only:
        try:
            count = sync.sync_reviews()
            print(f"Synced {count} reviews")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        try:
            results = sync.sync_all(args.full)
            print("\nSync complete:")
            
            if results.get("user"):
                user = results["user"].get("user", {}).get("data", {}).get("attributes", {})
                print(f"  User: {user.get('username', 'unknown')} (Level {user.get('level', '?')})")
            
            print(f"  Queue: {results.get('queue', 0)} items")
            print(f"  Due: {results.get('due', 0)} items")
            print(f"  Reviews: {results.get('reviews', 0)} records")
            
            if results.get("stats"):
                print(f"  Stats: {len(results['stats'])} categories")
        except Exception as e:
            print(f"Error during sync: {e}")
            sys.exit(1)

    if args.stats:
        print("\nDatabase stats:")
        conn = sqlite3.connect(sync.db_path)
        cursor = conn.cursor()
        tables = ["user", "grammar_points", "reviews", "study_queue", "due_items", "user_stats", "review_histories"]
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
