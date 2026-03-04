#!/usr/bin/env python3
"""
SQLite CLI - Command-line interface for Lite SQLite database operations.

Quick database management for OpenClaw agents.
"""

import sys
import argparse
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from sqlite_connector import SQLiteDB, json_loads, json_dumps


def main():
    parser = argparse.ArgumentParser(
        description="Lite SQLite CLI - Fast, lightweight local database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s init mydb.db                    # Create database
  %(prog)s create-table memos              # Show interactive table creation
  %(prog)s create-table memos -c id:INTEGER:P -c title:TEXT -c content:TEXT
  %(prog)s insert memos -d '{"title": "Test", "content": "Hello"}'
  %(prog)s query "SELECT * FROM memos" -d mydb.db
  %(prog)s optimize mydb.db                # Vacuum and analyze
  %(prog)s backup mydb.db backup/          # Create backup
  %(prog)s size mydb.db                    # Show database size
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Init command
    init_parser = subparsers.add_parser("init", help="Create new database")
    init_parser.add_argument("path", help="Database file path")

    # Create-table command
    table_parser = subparsers.add_parser("create-table", help="Create table")
    table_parser.add_argument("name", help="Table name")
    table_parser.add_argument("-c", "--column", action="append",
                            help="Column definition: name:TYPE[:PRIMARY|:AUTOINCREMENT]")
    table_parser.add_argument("-d", "--database", default="agent_data.db",
                            help="Database file")

    # Insert command
    insert_parser = subparsers.add_parser("insert", help="Insert row(s)")
    insert_parser.add_argument("table", help="Table name")
    insert_parser.add_argument("-d", "--database", default="agent_data.db",
                            help="Database file")
    insert_parser.add_argument("-f", "--file", help="Read JSON data from file")
    insert_parser.add_argument("data", nargs="?", help="JSON data as string")

    # Query command
    query_parser = subparsers.add_parser("query", help="Execute query")
    query_parser.add_argument("sql", help="SQL query")
    query_parser.add_argument("-d", "--database", default="agent_data.db",
                            help="Database file")
    query_parser.add_argument("-j", "--json", action="store_true",
                            help="Output as JSON")
    query_parser.add_argument("-p", "--params", help="Query parameters as JSON list")

    # Update command
    update_parser = subparsers.add_parser("update", help="Update rows")
    update_parser.add_argument("table", help="Table name")
    update_parser.add_argument("where", help="WHERE clause")
    update_parser.add_argument("-d", "--database", default="agent_data.db",
                            help="Database file")
    update_parser.add_argument("-f", "--file", help="Read JSON data from file")
    update_parser.add_argument("data", nargs="?", help="JSON data as string")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete rows")
    delete_parser.add_argument("table", help="Table name")
    delete_parser.add_argument("where", help="WHERE clause")
    delete_parser.add_argument("-d", "--database", default="agent_data.db",
                            help="Database file")
    delete_parser.add_argument("-p", "--params", help="WHERE parameters as JSON list")

    # Optimize command
    optimize_parser = subparsers.add_parser("optimize", help="Vacuum and analyze")
    optimize_parser.add_argument("path", nargs="?", default="agent_data.db",
                               help="Database file")

    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Create backup")
    backup_parser.add_argument("path", nargs="?", default="agent_data.db")
    backup_parser.add_argument("-o", "--output", help="Backup file/path")

    # Size command
    size_parser = subparsers.add_parser("size", help="Show database size")
    size_parser.add_argument("path", nargs="?", default="agent_data.db")

    # List tables command
    list_parser = subparsers.add_parser("list", help="List tables")
    list_parser.add_argument("-d", "--database", default="agent_data.db",
                           help="Database file")

    # Schema command
    schema_parser = subparsers.add_parser("schema", help="Show table schema")
    schema_parser.add_argument("table", help="Table name")
    schema_parser.add_argument("-d", "--database", default="agent_data.db",
                              help="Database file")

    # Index command
    index_parser = subparsers.add_parser("index", help="Create index")
    index_parser.add_argument("table", help="Table name")
    index_parser.add_argument("columns", help="Column name(s), comma-separated")
    index_parser.add_argument("-d", "--database", default="agent_data.db",
                             help="Database file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    try:
        if args.command == "init":
            db = SQLiteDB(args.path)
            print(f"✓ Database created: {args.path}")
            db.close()

        elif args.command == "create-table":
            if not args.column:
                # Interactive mode
                print(f"Creating table: {args.name}")
                print("Enter columns (name:type, e.g., id:INTEGER:P, title:TEXT)")
                print("Options: :P for PRIMARY KEY, :AUTOINCREMENT for autoincrement")
                print("Press Enter when done\n")

                columns = {}
                col_num = 1
                while True:
                    col_def = input(f"Column {col_num} (or Enter to finish): ").strip()
                    if not col_def:
                        break

                    parts = col_def.split(":")
                    if len(parts) < 2:
                        print("Error: Format should be name:type")
                        continue

                    name = parts[0]
                    type_def = parts[1].upper()
                    options = parts[2:] if len(parts) > 2 else []

                    definition = type_def
                    if "P" in options:
                        definition = f"{definition} PRIMARY KEY"
                    if "AUTOINCREMENT" in options:
                        definition = f"{definition} AUTOINCREMENT"

                    columns[name] = definition
                    col_num += 1

                if not columns:
                    print("Error: No columns defined")
                    return 1

            else:
                # Parse column definitions from CLI
                columns = {}
                for col_def in args.column:
                    parts = col_def.split(":")
                    name = parts[0]
                    type_def = parts[1].upper()
                    options = parts[2:] if len(parts) > 2 else []

                    definition = type_def
                    if "P" in options:
                        definition = f"{definition} PRIMARY KEY"
                    if "AUTOINCREMENT" in options:
                        definition = f"{definition} AUTOINCREMENT"

                    columns[name] = definition

            db = SQLiteDB(args.database)
            db.create_table(args.name, columns)
            print(f"✓ Table created: {args.name}")
            print(f"  Columns: {', '.join(columns.keys())}")
            db.close()

        elif args.command == "insert":
            # Read data from file or string
            if args.file:
                with open(args.file) as f:
                    data = json.load(f)
            elif args.data:
                data = json.loads(args.data)
            else:
                data_arg = input("Enter JSON data: ").strip()
                data = json.loads(data_arg)

            db = SQLiteDB(args.database)

            if isinstance(data, list):
                count = db.batch_insert(args.table, data)
                print(f"✓ Inserted {count} rows into {args.table}")
            else:
                row_id = db.insert(args.table, **data)
                print(f"✓ Inserted row {row_id} into {args.table}")

            db.close()

        elif args.command == "query":
            params = json.loads(args.params) if args.params else None
            if params and isinstance(params, list):
                params = tuple(params)

            db = SQLiteDB(args.database)
            results = db.query(args.sql, params)

            if args.json:
                print(json.dumps(results, indent=2, default=str))
            else:
                if results:
                    headers = results[0].keys()
                    col_widths = {col: min(max(len(col), max(len(str(row[col])) for row in results)), 50)
                                for col in headers}

                    # Print header
                    print("┌─" + "─┬─".join("─" * col_widths[h] for h in headers) + "─┐")
                    print("│ " + " │ ".join(h.ljust(col_widths[h]) for h in headers) + " │")
                    print("├─" + "─┼─".join("─" * col_widths[h] for h in headers) + "─┤")

                    # Print rows
                    for row in results:
                        print("│ " + " │ ".join(
                            str(row[h])[:col_widths[h]].ljust(col_widths[h]) for h in headers
                        ) + " │")

                    print("└─" + "─┴─".join("─" * col_widths[h] for h in headers) + "─┘")
                    print(f"\n{len(results)} row(s)")
                else:
                    print("No results")

            db.close()

        elif args.command == "update":
            if args.file:
                with open(args.file) as f:
                    data = json.load(f)
            elif args.data:
                data = json.loads(args.data)
            else:
                data_arg = input("Enter JSON data: ").strip()
                data = json.loads(data_arg)

            db = SQLiteDB(args.database)
            count = db.update(args.table, args.where, data)
            print(f"✓ Updated {count} row(s) in {args.table}")
            db.close()

        elif args.command == "delete":
            params = json.loads(args.params) if args.params else None
            if params and isinstance(params, list):
                params = tuple(params)

            db = SQLiteDB(args.database)
            count = db.delete(args.table, args.where, params)
            print(f"✓ Deleted {count} row(s) from {args.table}")
            db.close()

        elif args.command == "optimize":
            print(f"Optimizing: {args.path}")
            db = SQLiteDB(args.path)
            db.vacuum()
            db.analyze()
            size_info = db.size()
            db.close()
            print(f"✓ Database optimized")
            print(f"  Size: {size_info['size_mb']:.2f} MB")

        elif args.command == "backup":
            db = SQLiteDB(args.path)
            if args.output:
                backup_path = args.output
            else:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"{args.path.split('.')[0]}_{timestamp}.db"

            db.backup(backup_path)
            print(f"✓ Backup created: {backup_path}")
            db.close()

        elif args.command == "size":
            db = SQLiteDB(args.path)
            size_info = db.size()
            db.close()

            print(f"Database: {size_info['path']}")
            print(f"Size: {size_info['size_mb']:.2f} MB")
            print(f"Pages: {size_info['page_count']}")
            print(f"Page size: {size_info['page_size']} bytes")

        elif args.command == "list":
            db = SQLiteDB(args.database)
            tables = db.query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            db.close()

            if tables:
                print("Tables:")
                for row in tables:
                    count = db.count(row['name'])
                    print(f"  - {row['name']} ({count} rows)")
            else:
                print("No tables found")

        elif args.command == "schema":
            db = SQLiteDB(args.database)
            columns = db.query(f"PRAGMA table_info({args.table})")
            db.close()

            if columns:
                print(f"Schema for table: {args.table}")
                print()
                for col in columns:
                    pk = " (PK)" if col['pk'] else ""
                    notnull = " NOT NULL" if col['notnull'] else ""
                    print(f"  {col['name']}: {col['type']}{notnull}{pk}")
            else:
                print(f"Table not found: {args.table}")

        elif args.command == "index":
            db = SQLiteDB(args.database)
            db.create_index(args.table, args.columns)
            print(f"✓ Index created on {args.table}({args.columns})")
            db.close()

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
