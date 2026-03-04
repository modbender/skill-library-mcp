#!/usr/bin/env python3
"""
WaniKani Query Tool - Common reports and insights from synced data.
"""

import sqlite3
import json
import argparse
from pathlib import Path
from datetime import datetime

DB_FILENAME = "wanikani.db"


class WaniKaniQueries:
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

    def show_leeches(self, limit=15, min_fails=5):
        """Show kanji/vocab that keep falling back (reading/meaning streak <= 2)."""
        rows = self._query('''
            SELECT 
                s.characters,
                s.object as subject_type,
                s.level,
                json_extract(s.meanings, '$[0]') as meaning,
                json_extract(s.readings, '$[0]') as reading,
                a.srs_stage,
                rs.meaning_incorrect + rs.reading_incorrect as total_fails,
                rs.percentage_correct as accuracy,
                rs.meaning_current_streak,
                rs.reading_current_streak,
                rs.meaning_max_streak,
                rs.reading_max_streak
            FROM review_statistics rs
            JOIN assignments a ON rs.subject_id = a.subject_id
            JOIN subjects s ON rs.subject_id = s.id
            WHERE (rs.reading_current_streak <= 2 OR rs.meaning_current_streak <= 2)
              AND (rs.meaning_incorrect + rs.reading_incorrect) >= ?
            ORDER BY total_fails DESC, accuracy ASC
            LIMIT ?
        ''', (min_fails, limit))

        if not rows:
            print("No leeches found matching criteria.")
            return

        print(f"=== TOP {limit} LEACHES (weak streaks, {min_fails}+ fails) ===")
        print()

        srs_names = ['Locked', 'App I', 'App II', 'App III', 'App IV', 
                     'Guru I', 'Guru II', 'Master', 'Enlightened', 'Burned']

        for i, row in enumerate(rows, 1):
            r = dict(row)
            srs_name = srs_names[r['srs_stage']] if r['srs_stage'] is not None else '?'
            
            print(f"{i}. {r['characters']} ({r['meaning']})")
            print(f"   Type: {r['subject_type']} | Level: {r['level']} | SRS: {srs_name}")
            if r['reading']:
                print(f"   Reading: {r['reading']}")
            print(f"   Accuracy: {r['accuracy']:.0f}% | Fails: {r['total_fails']}")
            
            issues = []
            if r['reading_current_streak'] <= 2 and r['subject_type'] in ('kanji', 'vocabulary'):
                issues.append(f"reading streak {r['reading_current_streak']}")
            if r['meaning_current_streak'] <= 2:
                issues.append(f"meaning streak {r['meaning_current_streak']}")
            if issues:
                print(f"   🔴 Weak: {', '.join(issues)}")
            print()

    def show_srs_distribution(self):
        """Show items per SRS stage."""
        rows = self._query('''
            SELECT 
                a.srs_stage,
                COUNT(*) as count,
                s.object as subject_type
            FROM assignments a
            LEFT JOIN subjects s ON a.subject_id = s.id
            GROUP BY a.srs_stage, s.object
            ORDER BY a.srs_stage, s.object
        ''')

        print("=== SRS STAGE DISTRIBUTION ===")
        print()
        
        srs_names = ['Locked', 'App I', 'App II', 'App III', 'App IV', 
                     'Guru I', 'Guru II', 'Master', 'Enlightened', 'Burned']
        
        # Aggregate by stage
        stage_counts = {i: {'total': 0, 'kanji': 0, 'vocabulary': 0, 'radical': 0, 'kana_vocabulary': 0} 
                       for i in range(10)}
        
        for row in rows:
            stage = row['srs_stage'] if row['srs_stage'] is not None else 0
            obj = row['subject_type'] or 'unknown'
            count = row['count']
            stage_counts[stage]['total'] += count
            if obj in stage_counts[stage]:
                stage_counts[stage][obj] += count

        # Print table
        print(f"{'Stage':<12} {'Total':>6} {'Kanji':>6} {'Vocab':>6} {'Radical':>8}")
        print("-" * 44)
        for stage in range(10):
            data = stage_counts[stage]
            if data['total'] > 0:
                print(f"{srs_names[stage]:<12} {data['total']:>6} {data['kanji']:>6} "
                      f"{data['vocabulary']:>6} {data['radical']:>8}")
        
        # Summary
        total = sum(s['total'] for s in stage_counts.values())
        apprentice = sum(stage_counts[i]['total'] for i in range(1, 5))
        guru = sum(stage_counts[i]['total'] for i in range(5, 7))
        master = stage_counts[7]['total']
        enlightened = stage_counts[8]['total']
        burned = stage_counts[9]['total']
        locked = stage_counts[0]['total']
        
        print()
        print(f"Summary: {total} total items")
        print(f"  Apprentice (1-4): {apprentice} items in active review")
        print(f"  Guru (5-6): {guru} items (passed, unlocking new content)")
        print(f"  Master (7): {master} items")
        print(f"  Enlightened (8): {enlightened} items")
        print(f"  Burned (9): {burned} items (complete)")
        print(f"  Locked (0): {locked} items not yet available")
        print()

    def show_level_progress(self):
        """Show progress through each level."""
        rows = self._query('''
            SELECT 
                level,
                unlocked_at,
                started_at,
                passed_at,
                completed_at,
                abandoned_at,
                CASE 
                    WHEN abandoned_at IS NOT NULL THEN 'abandoned'
                    WHEN completed_at IS NOT NULL THEN 'completed'
                    WHEN passed_at IS NOT NULL THEN 'passed'
                    WHEN started_at IS NOT NULL THEN 'in_progress'
                    WHEN unlocked_at IS NOT NULL THEN 'unlocked'
                    ELSE 'locked'
                END as status
            FROM level_progressions
            ORDER BY level
        ''')

        if not rows:
            print("No level progression data found.")
            return

        print("=== LEVEL PROGRESSION ===")
        print()
        print(f"{'Lvl':>3} {'Status':<12} {'Unlocked':<12} {'Started':<12} {'Passed':<12} {'Days to Pass':>12}")
        print("-" * 70)

        for row in rows:
            r = dict(row)
            status = r['status']
            unlocked = r['unlocked_at'][:10] if r['unlocked_at'] else '-'
            started = r['started_at'][:10] if r['started_at'] else '-'
            passed = r['passed_at'][:10] if r['passed_at'] else '-'
            
            days = '-'
            if r['started_at'] and r['passed_at']:
                start = datetime.fromisoformat(r['started_at'].replace('Z', '+00:00'))
                end = datetime.fromisoformat(r['passed_at'].replace('Z', '+00:00'))
                days = str((end - start).days)
            elif r['abandoned_at']:
                days = 'abandoned'
            
            print(f"{r['level']:>3} {status:<12} {unlocked:<12} {started:<12} {passed:<12} {days:>12}")
        print()

    def show_critical_items(self, limit=10):
        """Show items close to dropping in SRS ( Guru with weak streaks)."""
        rows = self._query('''
            SELECT 
                s.characters,
                s.object as subject_type,
                s.level,
                json_extract(s.meanings, '$[0]') as meaning,
                json_extract(s.readings, '$[0]') as reading,
                a.srs_stage,
                a.available_at,
                rs.percentage_correct as accuracy,
                rs.reading_current_streak,
                rs.meaning_current_streak,
                rs.meaning_incorrect + rs.reading_incorrect as total_fails
            FROM assignments a
            JOIN subjects s ON a.subject_id = s.id
            JOIN review_statistics rs ON a.subject_id = rs.subject_id
            WHERE a.srs_stage IN (5, 6, 7, 8)  -- Guru, Master, Enlightened
              AND (rs.reading_current_streak <= 2 OR rs.meaning_current_streak <= 2)
            ORDER BY a.srs_stage DESC, rs.percentage_correct ASC
            LIMIT ?
        ''', (limit,))

        if not rows:
            print("No critical items found.")
            return

        print(f"=== CRITICAL ITEMS (High SRS + Weak Streak = Risk of Falling Back) ===")
        print()
        
        srs_names = ['Locked', 'App I', 'App II', 'App III', 'App IV', 
                     'Guru I', 'Guru II', 'Master', 'Enlightened', 'Burned']

        for i, row in enumerate(rows, 1):
            r = dict(row)
            srs_name = srs_names[r['srs_stage']] if r['srs_stage'] is not None else '?'
            next_review = r['available_at'][:10] if r['available_at'] else 'available'
            
            print(f"{i}. {r['characters']} ({r['meaning']}) - Level {r['level']}")
            print(f"   SRS: {srs_name} | Accuracy: {r['accuracy']:.0f}% | Fails: {r['total_fails']}")
            print(f"   Next review: {next_review}")
            
            warnings = []
            if r['reading_current_streak'] and r['reading_current_streak'] <= 1:
                warnings.append("⚠️ reading streak critical")
            if r['meaning_current_streak'] and r['meaning_current_streak'] <= 1:
                warnings.append("⚠️ meaning streak critical")
            if warnings:
                print(f"   {' | '.join(warnings)}")
            print()

    def show_accuracy_by_type(self):
        """Show accuracy statistics by subject type."""
        rows = self._query('''
            SELECT 
                subject_type,
                COUNT(*) as count,
                ROUND(AVG(percentage_correct), 1) as avg_accuracy,
                ROUND(MIN(percentage_correct), 1) as min_accuracy,
                ROUND(MAX(percentage_correct), 1) as max_accuracy
            FROM review_statistics
            GROUP BY subject_type
        ''')

        print("=== ACCURACY BY SUBJECT TYPE ===")
        print()
        print(f"{'Type':<15} {'Count':>6} {'Avg Acc':>10} {'Min':>8} {'Max':>8}")
        print("-" * 51)
        
        for row in rows:
            print(f"{row['subject_type']:<15} {row['count']:>6} {row['avg_accuracy']:>9}% "
                  f"{row['min_accuracy']:>7}% {row['max_accuracy']:>7}%")
        print()

    def show_recent_mistakes(self, days=7, limit=10):
        """Show items with recent incorrect answers (requires reviews table)."""
        # Check if reviews table has data
        count = self._query("SELECT COUNT(*) as c FROM reviews")[0]['c']
        if count == 0:
            print("No review history available. Reviews table is empty (may need pagination fix in sync).")
            print("Showing items with highest total incorrect answers instead:")
            print()
            
            rows = self._query('''
                SELECT 
                    s.characters,
                    s.object as subject_type,
                    s.level,
                    json_extract(s.meanings, '$[0]') as meaning,
                    rs.meaning_incorrect + rs.reading_incorrect as total_fails,
                    rs.percentage_correct as accuracy
                FROM review_statistics rs
                JOIN subjects s ON rs.subject_id = s.id
                ORDER BY total_fails DESC
                LIMIT ?
            ''', (limit,))
            
            for i, row in enumerate(rows, 1):
                print(f"{i}. {row['characters']} ({row['meaning']}) - {row['total_fails']} fails, {row['accuracy']:.0f}%")
            print()
            return

        rows = self._query('''
            SELECT 
                s.characters,
                s.object as subject_type,
                json_extract(s.meanings, '$[0]') as meaning,
                r.incorrect_meaning_answers + r.incorrect_reading_answers as wrong,
                r.created_at
            FROM reviews r
            JOIN subjects s ON r.subject_id = s.id
            WHERE r.created_at > datetime('now', '-{} days')
              AND (r.incorrect_meaning_answers > 0 OR r.incorrect_reading_answers > 0)
            ORDER BY wrong DESC, r.created_at DESC
            LIMIT ?
        '''.format(days), (limit,))

        if rows:
            print(f"=== RECENT MISTAKES (last {days} days) ===")
            for row in rows:
                print(f"  {row['characters']} ({row['meaning']}): {row['wrong']} wrong on {row['created_at'][:10]}")
        else:
            print(f"No mistakes found in last {days} days.")
        print()


def main():
    parser = argparse.ArgumentParser(description="Query WaniKani synced data")
    parser.add_argument("--data-dir", "-d", default=".", help="Directory with wanikani.db")
    
    subparsers = parser.add_subparsers(dest="command", help="Available queries")
    
    # leeches
    leeches_parser = subparsers.add_parser("leeches", help="Show items with weak streaks")
    leeches_parser.add_argument("--limit", "-n", type=int, default=15)
    leeches_parser.add_argument("--min-fails", type=int, default=5)
    
    # srs
    subparsers.add_parser("srs", help="Show SRS stage distribution")
    
    # levels
    subparsers.add_parser("levels", help="Show level progression")
    
    # critical
    critical_parser = subparsers.add_parser("critical", help="Show high-SRS items at risk")
    critical_parser.add_argument("--limit", "-n", type=int, default=10)
    
    # accuracy
    subparsers.add_parser("accuracy", help="Show accuracy by subject type")
    
    # recent
    recent_parser = subparsers.add_parser("recent", help="Show recent mistakes")
    recent_parser.add_argument("--days", type=int, default=7)
    recent_parser.add_argument("--limit", "-n", type=int, default=10)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    queries = WaniKaniQueries(Path(args.data_dir))
    
    if args.command == "leeches":
        queries.show_leeches(args.limit, args.min_fails)
    elif args.command == "srs":
        queries.show_srs_distribution()
    elif args.command == "levels":
        queries.show_level_progress()
    elif args.command == "critical":
        queries.show_critical_items(args.limit)
    elif args.command == "accuracy":
        queries.show_accuracy_by_type()
    elif args.command == "recent":
        queries.show_recent_mistakes(args.days, args.limit)


if __name__ == "__main__":
    main()
