#!/usr/bin/env python3
"""
PostgreSQL Query Execution Script
Execute SQL queries against PostgreSQL databases
"""

import argparse
import json
import os
import sys

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    print("Error: psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)


def get_connection(dbname=None):
    """Get database connection using environment variables or CLI args"""
    return psycopg2.connect(
        host=os.environ.get('PGHOST', 'localhost'),
        port=os.environ.get('PGPORT', '5432'),
        database=dbname or os.environ.get('PGDATABASE', 'postgres'),
        user=os.environ.get('PGUSER', 'postgres'),
        password=os.environ.get('PGPASSWORD', '')
    )


def execute_query(query, dbname=None, output_format='table'):
    """Execute SQL query and return results"""
    conn = get_connection(dbname)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            
            if cur.description:
                columns = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
                
                if output_format == 'json':
                    return json.dumps([dict(row) for row in rows], indent=2, default=str)
                elif output_format == 'csv':
                    import csv
                    import io
                    output = io.StringIO()
                    writer = csv.DictWriter(output, fieldnames=columns)
                    writer.writeheader()
                    for row in rows:
                        writer.writerow(dict(row))
                    return output.getvalue()
                else:  # table
                    return format_table(columns, rows)
            else:
                conn.commit()
                return f"Query executed successfully. Rows affected: {cur.rowcount}"
    finally:
        conn.close()


def format_table(columns, rows):
    """Format query results as ASCII table"""
    if not rows:
        return "No results found."
    
    # Calculate column widths
    widths = {col: len(col) for col in columns}
    for row in rows:
        for col in columns:
            val = str(row.get(col, ''))
            widths[col] = max(widths[col], len(val))
    
    # Build table
    separator = '+' + '+'.join('-' * (widths[col] + 2) for col in columns) + '+'
    header = '|' + '|'.join(f' {col:<{widths[col}]} ' for col in columns) + '|'
    
    result = [separator, header, separator]
    for row in rows:
        line = '|' + '|'.join(f' {str(row.get(col, "")):<{widths[col}]} ' for col in columns) + '|'
        result.append(line)
    result.append(separator)
    
    return '\n'.join(result)


def main():
    parser = argparse.ArgumentParser(description='Execute SQL queries on PostgreSQL')
    parser.add_argument('--dbname', '-d', help='Database name')
    parser.add_argument('--query', '-q', required=True, help='SQL query to execute')
    parser.add_argument('--format', '-f', choices=['table', 'json', 'csv'], 
                        default='table', help='Output format')
    
    args = parser.parse_args()
    
    try:
        result = execute_query(args.query, args.dbname, args.format)
        print(result)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
