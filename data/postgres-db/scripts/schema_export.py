#!/usr/bin/env python3
"""
PostgreSQL Schema Export Script
Export database schema (tables, views, indexes, constraints)
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
    """Get database connection"""
    return psycopg2.connect(
        host=os.environ.get('PGHOST', 'localhost'),
        port=os.environ.get('PGPORT', '5432'),
        database=dbname or os.environ.get('PGDATABASE', 'postgres'),
        user=os.environ.get('PGUSER', 'postgres'),
        password=os.environ.get('PGPASSWORD', '')
    )


def get_tables(conn, schema='public'):
    """Get all tables in schema"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = %s AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """, (schema,))
        return [row['table_name'] for row in cur.fetchall()]


def get_columns(conn, table, schema='public'):
    """Get columns for a table"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT 
                column_name, data_type, is_nullable, column_default,
                character_maximum_length, numeric_precision, numeric_scale
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
        """, (schema, table))
        return [dict(row) for row in cur.fetchall()]


def get_indexes(conn, table, schema='public'):
    """Get indexes for a table"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE schemaname = %s AND tablename = %s
        """, (schema, table))
        return [dict(row) for row in cur.fetchall()]


def get_foreign_keys(conn, table, schema='public'):
    """Get foreign key constraints"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_schema = %s
                AND tc.table_name = %s
        """, (schema, table))
        return [dict(row) for row in cur.fetchall()]


def get_primary_key(conn, table, schema='public'):
    """Get primary key columns"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT kcu.column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.constraint_type = 'PRIMARY KEY'
                AND tc.table_schema = %s
                AND tc.table_name = %s
        """, (schema, table))
        return [row['column_name'] for row in cur.fetchall()]


def export_schema(dbname=None, schema='public', output_format='json'):
    """Export full schema"""
    conn = get_connection(dbname)
    schema_data = {'schema': schema, 'tables': {}}
    
    try:
        tables = get_tables(conn, schema)
        
        for table in tables:
            table_info = {
                'columns': get_columns(conn, table, schema),
                'primary_key': get_primary_key(conn, table, schema),
                'foreign_keys': get_foreign_keys(conn, table, schema),
                'indexes': get_indexes(conn, table, schema)
            }
            schema_data['tables'][table] = table_info
        
        if output_format == 'json':
            return json.dumps(schema_data, indent=2, default=str)
        elif output_format == 'markdown':
            return format_markdown(schema_data)
        else:
            return json.dumps(schema_data, indent=2, default=str)
    finally:
        conn.close()


def format_markdown(schema_data):
    """Format schema as Markdown"""
    lines = [f"# Schema: {schema_data['schema']}", ""]
    
    for table_name, table_info in schema_data['tables'].items():
        lines.append(f"## Table: {table_name}")
        
        if table_info['primary_key']:
            lines.append(f"**Primary Key:** {', '.join(table_info['primary_key'])}")
        
        lines.append("\n### Columns")
        lines.append("| Column | Type | Nullable | Default |")
        lines.append("|--------|------|----------|---------|")
        
        for col in table_info['columns']:
            col_type = col['data_type']
            if col['character_maximum_length']:
                col_type += f"({col['character_maximum_length']})"
            lines.append(f"| {col['column_name']} | {col_type} | {col['is_nullable']} | {col['column_default'] or ''} |")
        
        if table_info['foreign_keys']:
            lines.append("\n### Foreign Keys")
            for fk in table_info['foreign_keys']:
                lines.append(f"- {fk['column_name']} → {fk['foreign_table_name']}.{fk['foreign_column_name']}")
        
        if table_info['indexes']:
            lines.append("\n### Indexes")
            for idx in table_info['indexes']:
                lines.append(f"- `{idx['indexname']}`")
        
        lines.append("")
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Export PostgreSQL schema')
    parser.add_argument('--dbname', '-d', help='Database name')
    parser.add_argument('--schema', '-s', default='public', help='Schema name')
    parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    parser.add_argument('--format', '-f', choices=['json', 'markdown'], 
                        default='json', help='Output format')
    
    args = parser.parse_args()
    
    try:
        result = export_schema(args.dbname, args.schema, args.format)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(result)
            print(f"Schema exported to {args.output}")
        else:
            print(result)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
