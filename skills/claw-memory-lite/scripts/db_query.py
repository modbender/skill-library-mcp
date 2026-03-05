#!/usr/bin/env python3
"""
db_query.py - Query long-term memory database for claw-memory-lite

Usage:
    python3 db_query.py [SEARCH_TERM] [--category CATEGORY]

Arguments:
    SEARCH_TERM          Keyword to search in content and keywords (optional)
    -c, --category CAT   Filter by category (System/Environment/Skill/Project/Comm/Security)

Examples:
    python3 db_query.py backup
    python3 db_query.py --category Skill
    python3 db_query.py uv --category Environment
"""

import sqlite3
import sys
import os
import argparse

# Database path (default: OpenClaw database location)
DB_PATH = os.environ.get(
    "CLAW_MEMORY_DB_PATH",
    "/home/node/.openclaw/database/insight.db"
)


def query(search_term=None, category=None):
    """
    Query the long-term memory database.
    
    Args:
        search_term: Keyword to search in content and keywords fields
        category: Filter by category (optional)
    """
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        print("Run 'python3 extract_memory.py' first to initialize the database.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Build query
    query_str = "SELECT category, content, created_at FROM long_term_memory WHERE 1=1"
    params = []
    
    if category:
        query_str += " AND category = ?"
        params.append(category)
    
    if search_term:
        query_str += " AND (content LIKE ? OR keywords LIKE ?)"
        params.extend([f'%{search_term}%', f'%{search_term}%'])
    
    query_str += " ORDER BY created_at DESC"
    
    cursor.execute(query_str, params)
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("No matching memories found.")
        return

    # Print results
    for row in rows:
        print(f"[{row[2]}] {row[0]}: {row[1]}")


def list_categories():
    """List all available categories in the database."""
    if not os.path.exists(DB_PATH):
        print("Database not found.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT category, COUNT(*) as count 
        FROM long_term_memory 
        GROUP BY category 
        ORDER BY count DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("No categories found (database is empty).")
        return
    
    print("Available categories:")
    for row in rows:
        print(f"  {row[0]}: {row[1]} records")


def stats():
    """Show database statistics."""
    if not os.path.exists(DB_PATH):
        print("Database not found.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total records
    cursor.execute("SELECT COUNT(*) FROM long_term_memory")
    total = cursor.fetchone()[0]
    
    # Records by category
    cursor.execute("""
        SELECT category, COUNT(*) as count 
        FROM long_term_memory 
        GROUP BY category 
        ORDER BY count DESC
    """)
    by_category = cursor.fetchall()
    
    # Oldest and newest records
    cursor.execute("SELECT MIN(created_at), MAX(created_at) FROM long_term_memory")
    date_range = cursor.fetchone()
    
    conn.close()
    
    print(f"📊 Database Statistics")
    print(f"   Total records: {total}")
    print(f"   Date range: {date_range[0]} to {date_range[1]}")
    print(f"\n   Records by category:")
    for cat, count in by_category:
        print(f"      {cat}: {count}")


def main():
    parser = argparse.ArgumentParser(
        description="Query long-term memory database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 db_query.py backup              Search for 'backup' keyword
  python3 db_query.py --category Skill    List all Skill records
  python3 db_query.py uv --category Env   Search 'uv' in Environment category
  python3 db_query.py --stats             Show database statistics
  python3 db_query.py --categories        List available categories
        """
    )
    
    parser.add_argument(
        "search_term",
        nargs="?",
        help="Keyword to search in content and keywords"
    )
    parser.add_argument(
        "-c", "--category",
        help="Filter by category (System/Environment/Skill/Project/Comm/Security)"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show database statistics"
    )
    parser.add_argument(
        "--categories",
        action="store_true",
        help="List available categories"
    )
    
    args = parser.parse_args()
    
    # Handle special modes
    if args.stats:
        stats()
        return
    
    if args.categories:
        list_categories()
        return
    
    # Normal query
    query(search_term=args.search_term, category=args.category)


if __name__ == "__main__":
    main()
