#!/usr/bin/env python3
"""
Bunpro Query Tool - Common reports and insights from synced data.
"""

import sqlite3
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

DB_FILENAME = "bunpro.db"


class BunproQueries:
    def __init__(self, data_dir: Path):
        self.db_path = data_dir / DB_FILENAME
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found at {self.db_path}. Run sync.py first.")

    def _query(self, sql, params=()):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql, params)
        results = cursor.fetchall()
        conn.close()
        return results

    def show_srs_overview(self):
        """Show SRS level distribution."""
        # Load from stats table
        rows = self._query('''
            SELECT data FROM user_stats WHERE stat_type = 'srs_overview'
        ''')
        
        if not rows:
            print("No SRS overview data found. Run sync with stats.")
            return
        
        data = json.loads(rows[0]['data'])
        stats_data = data.get('data', {}).get('attributes', {})
        
        print("=== SRS LEVEL DISTRIBUTION ===")
        print()
        
        srs_levels = stats_data.get('srs_levels', {})
        total = sum(srs_levels.values()) if srs_levels else 0
        
        if srs_levels:
            print(f"{'SRS Level':<15} {'Count':>8} {'Percentage':>12}")
            print("-" * 40)
            for level, count in sorted(srs_levels.items()):
                pct = (count / total * 100) if total else 0
                print(f"{level:<15} {count:>8} {pct:>11.1f}%")
        
        print()
        print(f"Total reviews: {total}")
        print(f"Burned items: {stats_data.get('burned_count', 0)}")
        print()

    def show_review_forecast(self):
        """Show upcoming review forecast."""
        rows = self._query('''
            SELECT data FROM user_stats WHERE stat_type = 'forecast_daily'
        ''')
        
        if not rows:
            # Fallback: calculate from reviews table
            rows = self._query('''
                SELECT DATE(next_review) as day, COUNT(*) as count
                FROM reviews
                WHERE next_review IS NOT NULL
                  AND next_review > datetime('now')
                GROUP BY DATE(next_review)
                ORDER BY day
                LIMIT 7
            ''')
            
            if rows:
                print("=== UPCOMING REVIEWS (from review data) ===")
                print()
                print(f"{'Date':<12} {'Reviews':>8}")
                print("-" * 25)
                for row in rows:
                    print(f"{row['day']:<12} {row['count']:>8}")
            else:
                print("No forecast data available.")
            return
        
        data = json.loads(rows[0]['data'])
        forecast = data.get('data', {}).get('attributes', {}).get('forecast', {})
        
        print("=== DAILY REVIEW FORECAST ===")
        print()
        print(f"{'Date':<12} {'Reviews':>8}")
        print("-" * 25)
        for date, count in sorted(forecast.items())[:7]:
            print(f"{date:<12} {count:>8}")
        print()

    def show_grammar_mastery(self, jlpt_level=None):
        """Show grammar mastery by JLPT level."""
        where_clause = ""
        params = ()
        if jlpt_level:
            where_clause = "WHERE g.jlpt_level = ?"
            params = (jlpt_level,)
        
        rows = self._query(f'''
            SELECT 
                g.jlpt_level,
                g.title,
                g.meaning,
                r.srs_stage_string,
                r.burned,
                r.next_review
            FROM grammar_points g
            LEFT JOIN reviews r ON g.id = r.grammar_point_id
            {where_clause}
            ORDER BY g.jlpt_level, r.srs_stage DESC
            LIMIT 20
        ''', params)
        
        if not rows:
            print("No grammar mastery data found. Sync reviews and grammar points.")
            return
        
        level_str = f" (JLPT N{jlpt_level})" if jlpt_level else ""
        print(f"=== GRAMMAR MASTERY{level_str} ===")
        print()
        
        for row in rows:
            burned_mark = "✓" if row['burned'] else ""
            next_review = row['next_review'][:10] if row['next_review'] else "N/A"
            print(f"{row['title']:<20} {row['meaning']:<30} {row['srs_stage_string'] or 'New':<10} {burned_mark}")
        
        print()

    def show_due_reviews(self):
        """Show currently due reviews."""
        rows = self._query('''
            SELECT 
                d.reviewable_id,
                d.reviewable_type,
                d.streak,
                d.is_leech,
                g.title,
                g.meaning
            FROM due_items d
            LEFT JOIN grammar_points g ON d.reviewable_id = g.id
            ORDER BY d.streak DESC
        ''')
        
        if not rows:
            print("No due items found. Either nothing is due or sync due_items.")
            return
        
        print(f"=== DUE REVIEWS ({len(rows)} items) ===")
        print()
        print(f"{'Grammar':<25} {'Type':<10} {'Streak':>8} {'Leech':<8}")
        print("-" * 60)
        
        for row in rows:
            title = row['title'] or f"ID:{row['reviewable_id']}"
            leech_mark = "🔴" if row['is_leech'] else ""
            print(f"{title:<25} {row['reviewable_type']:<10} {row['streak'] or 0:>8} {leech_mark:<8}")
        
        print()

    def show_leeches(self, limit=15):
        """Show grammar leeches (is_leech flag)."""
        rows = self._query('''
            SELECT 
                d.reviewable_id,
                d.reviewable_type,
                d.streak,
                g.title,
                g.meaning,
                g.jlpt_level,
                r.srs_stage_string
            FROM due_items d
            LEFT JOIN grammar_points g ON d.reviewable_id = g.id
            LEFT JOIN reviews r ON d.reviewable_id = r.reviewable_id
            WHERE d.is_leech = 1
            ORDER BY d.streak ASC
            LIMIT ?
        ''', (limit,))
        
        if not rows:
            print("No leeches found. Great job!")
            return
        
        print(f"=== TOP {limit} GRAMMAR LEECHES ===")
        print()
        print("These grammar points keep falling back - they need extra attention:")
        print()
        
        for i, row in enumerate(rows, 1):
            print(f"{i}. {row['title']} ({row['meaning']})")
            print(f"   Level: N{row['jlpt_level'] or '?'} | Streak: {row['streak'] or 0} | SRS: {row['srs_stage_string'] or 'New'}")
            print()

    def show_user_progress(self):
        """Show overall user progress."""
        user_rows = self._query('SELECT * FROM user LIMIT 1')
        if not user_rows:
            print("No user data found.")
            return
        
        user = dict(user_rows[0])
        
        # Get review counts
        review_counts = self._query('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN burned = 1 THEN 1 ELSE 0 END) as burned,
                SUM(CASE WHEN srs_stage >= 5 THEN 1 ELSE 0 END) as guru_plus
            FROM reviews
        ''')[0]
        
        # Get due count
        due_count = self._query('SELECT COUNT(*) as c FROM due_items')[0]['c']
        
        print("=== BUNPRO PROGRESS ===")
        print()
        print(f"User: {user['username']}")
        print(f"Level: {user['level']}")
        print(f"XP: {user['xp']:,}")
        print(f"Buncoin: {user['buncoin']:,}")
        print(f"Lifetime: {'Yes' if user['is_lifetime'] else 'No'}")
        print()
        print(f"Grammar Reviews: {review_counts['total']}")
        print(f"  • Burned: {review_counts['burned']}")
        print(f"  • Guru+: {review_counts['guru_plus']}")
        print(f"  • Due now: {due_count}")
        print()

    def show_review_activity(self):
        """Show recent review activity."""
        rows = self._query('''
            SELECT data FROM user_stats WHERE stat_type = 'review_activity'
        ''')
        
        if not rows:
            print("No review activity data found.")
            return
        
        data = json.loads(rows[0]['data'])
        activity = data.get('data', {}).get('attributes', {}).get('activity', {})
        
        print("=== RECENT REVIEW ACTIVITY ===")
        print()
        print(f"{'Date':<12} {'Reviews':>8} {'Correct':>8} {'Accuracy':>10}")
        print("-" * 45)
        
        for date, stats in sorted(activity.items(), reverse=True)[:14]:  # Last 14 days
            total = stats.get('total', 0)
            correct = stats.get('correct', 0)
            accuracy = (correct / total * 100) if total else 0
            print(f"{date:<12} {total:>8} {correct:>8} {accuracy:>9.1f}%")
        
        print()


def main():
    parser = argparse.ArgumentParser(description="Query Bunpro synced data")
    parser.add_argument("--data-dir", "-d", default=".", help="Directory with bunpro.db")
    
    subparsers = parser.add_subparsers(dest="command", help="Available queries")
    
    # srs
    subparsers.add_parser("srs", help="Show SRS level distribution")
    
    # forecast
    subparsers.add_parser("forecast", help="Show upcoming review forecast")
    
    # grammar
    grammar_parser = subparsers.add_parser("grammar", help="Show grammar mastery")
    grammar_parser.add_argument("--jlpt", type=int, choices=[5, 4, 3, 2, 1], help="Filter by JLPT level")
    
    # due
    subparsers.add_parser("due", help="Show currently due reviews")
    
    # leeches
    leeches_parser = subparsers.add_parser("leeches", help="Show grammar leeches")
    leeches_parser.add_argument("--limit", "-n", type=int, default=15)
    
    # progress
    subparsers.add_parser("progress", help="Show overall user progress")
    
    # activity
    subparsers.add_parser("activity", help="Show recent review activity")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    queries = BunproQueries(Path(args.data_dir))
    
    if args.command == "srs":
        queries.show_srs_overview()
    elif args.command == "forecast":
        queries.show_review_forecast()
    elif args.command == "grammar":
        queries.show_grammar_mastery(args.jlpt)
    elif args.command == "due":
        queries.show_due_reviews()
    elif args.command == "leeches":
        queries.show_leeches(args.limit)
    elif args.command == "progress":
        queries.show_user_progress()
    elif args.command == "activity":
        queries.show_review_activity()


if __name__ == "__main__":
    main()
