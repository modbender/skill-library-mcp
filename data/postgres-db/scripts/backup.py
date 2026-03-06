#!/usr/bin/env python3
"""
PostgreSQL Backup Script
Backup and restore PostgreSQL databases
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime


def get_env(dbname=None):
    """Get environment for pg_dump"""
    env = os.environ.copy()
    env['PGHOST'] = os.environ.get('PGHOST', 'localhost')
    env['PGPORT'] = os.environ.get('PGPORT', '5432')
    env['PGDATABASE'] = dbname or os.environ.get('PGDATABASE', 'postgres')
    env['PGUSER'] = os.environ.get('PGUSER', 'postgres')
    if 'PGPASSWORD' in os.environ:
        env['PGPASSWORD'] = os.environ['PGPASSWORD']
    return env


def backup_database(dbname, backup_dir, backup_name=None, format='custom'):
    """Create full database backup"""
    os.makedirs(backup_dir, exist_ok=True)
    
    if backup_name is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{dbname}_{timestamp}.backup"
    
    backup_path = os.path.join(backup_dir, backup_name)
    
    # Format flags
    format_flag = {
        'custom': 'c',      # Custom format (compressed)
        'plain': 'p',       # Plain SQL
        'directory': 'd',   # Directory format
        'tar': 't'          # Tar format
    }.get(format, 'c')
    
    cmd = [
        'pg_dump',
        '-Fc' if format == 'custom' else '-Fp' if format == 'plain' else '-Ft' if format == 'tar' else '-Fd',
        '-f', backup_path,
        '-h', os.environ.get('PGHOST', 'localhost'),
        '-p', os.environ.get('PGPORT', '5432'),
        '-U', os.environ.get('PGUSER', 'postgres'),
        dbname
    ]
    
    env = get_env(dbname)
    
    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        if result.returncode == 0:
            size = os.path.getsize(backup_path)
            print(f"Backup created: {backup_path} ({size:,} bytes)")
            return backup_path
        else:
            print(f"Backup failed: {result.stderr}", file=sys.stderr)
            sys.exit(1)
    except FileNotFoundError:
        print("Error: pg_dump not found. Ensure PostgreSQL client tools are installed.", file=sys.stderr)
        sys.exit(1)


def backup_table(dbname, table, backup_dir):
    """Backup single table"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"{table}_{timestamp}.sql"
    backup_path = os.path.join(backup_dir, backup_name)
    
    cmd = [
        'pg_dump',
        '-t', table,
        '-Fp',  # Plain SQL format
        '-f', backup_path,
        '-h', os.environ.get('PGHOST', 'localhost'),
        '-p', os.environ.get('PGPORT', '5432'),
        '-U', os.environ.get('PGUSER', 'postgres'),
        dbname
    ]
    
    env = get_env(dbname)
    
    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        if result.returncode == 0:
            size = os.path.getsize(backup_path)
            print(f"Table backup created: {backup_path} ({size:,} bytes)")
            return backup_path
        else:
            print(f"Backup failed: {result.stderr}", file=sys.stderr)
            sys.exit(1)
    except FileNotFoundError:
        print("Error: pg_dump not found.", file=sys.stderr)
        sys.exit(1)


def restore_database(backup_file, dbname, target_db=None):
    """Restore database from backup"""
    target = target_db or dbname
    
    cmd = [
        'pg_restore',
        '-d', target,
        '-h', os.environ.get('PGHOST', 'localhost'),
        '-p', os.environ.get('PGPORT', '5432'),
        '-U', os.environ.get('PGUSER', 'postgres'),
        '--clean',  # Drop existing objects
        '--create' if target_db else '',  # Create database first
        backup_file
    ]
    
    # Remove empty strings
    cmd = [c for c in cmd if c]
    
    env = get_env(dbname)
    
    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Database restored successfully to {target}")
        else:
            print(f"Restore failed: {result.stderr}", file=sys.stderr)
            sys.exit(1)
    except FileNotFoundError:
        print("Error: pg_restore not found.", file=sys.stderr)
        sys.exit(1)


def list_backups(backup_dir):
    """List backup files in directory"""
    if not os.path.exists(backup_dir):
        print(f"Directory not found: {backup_dir}")
        return
    
    backups = [f for f in os.listdir(backup_dir) if f.endswith(('.backup', '.sql', '.dump'))]
    
    if not backups:
        print("No backups found")
        return
    
    print(f"Backups in {backup_dir}:")
    for backup in sorted(backups):
        path = os.path.join(backup_dir, backup)
        size = os.path.getsize(path)
        mtime = datetime.fromtimestamp(os.path.getmtime(path))
        print(f"  {backup} ({size:,} bytes) - {mtime.strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    parser = argparse.ArgumentParser(description='PostgreSQL backup and restore')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create database backup')
    backup_parser.add_argument('--dbname', '-d', required=True, help='Database name')
    backup_parser.add_argument('--backup-dir', '-o', default='./backups', help='Backup directory')
    backup_parser.add_argument('--name', '-n', help='Backup file name')
    backup_parser.add_argument('--format', '-f', choices=['custom', 'plain', 'tar', 'directory'],
                                default='custom', help='Backup format')
    backup_parser.add_argument('--table', '-t', help='Backup single table only')
    
    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore database from backup')
    restore_parser.add_argument('--backup', '-i', required=True, help='Backup file to restore')
    restore_parser.add_argument('--dbname', '-d', required=True, help='Target database name')
    restore_parser.add_argument('--create', action='store_true', help='Create database if not exists')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available backups')
    list_parser.add_argument('--backup-dir', '-o', default='./backups', help='Backup directory')
    
    args = parser.parse_args()
    
    if args.command == 'backup':
        if args.table:
            backup_table(args.dbname, args.table, args.backup_dir)
        else:
            backup_database(args.dbname, args.backup_dir, args.name, args.format)
    elif args.command == 'restore':
        restore_database(args.backup, args.dbname)
    elif args.command == 'list':
        list_backups(args.backup_dir)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
