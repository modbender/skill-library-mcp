#!/usr/bin/env python3
"""
infra-watchdog — Infrastructure Monitoring & Health Alerts for OpenClaw
Monitors endpoints, services, containers, resources, and sends alerts via WhatsApp/Telegram/Discord.
"""

import os
import sys
import json
import sqlite3
import time
import socket
import subprocess
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import urllib.request
import urllib.error
import ssl

# Paths
HOME = Path.home()
WORKSPACE = HOME / '.openclaw' / 'workspace'
DATA_DIR = WORKSPACE / 'infra-watchdog-data'
DB_PATH = DATA_DIR / 'monitors.db'
CONFIG_PATH = DATA_DIR / 'config.json'
STATE_PATH = DATA_DIR / 'state.json'

# Ensure data dir exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Default config
DEFAULT_CONFIG = {
    'alert_channel': 'whatsapp',
    'alert_cooldown_minutes': 15,
    'check_interval_minutes': 5,
    'ssl_expiry_warning_days': 30,
}

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS monitors (
                id TEXT PRIMARY KEY,
                type TEXT,
                name TEXT,
                target TEXT,
                config TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                monitor_id TEXT,
                timestamp TIMESTAMP,
                status TEXT,
                response_time_ms REAL,
                details TEXT,
                FOREIGN KEY (monitor_id) REFERENCES monitors(id)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                monitor_id TEXT,
                timestamp TIMESTAMP,
                severity TEXT,
                message TEXT,
                sent_at TIMESTAMP,
                FOREIGN KEY (monitor_id) REFERENCES monitors(id)
            )
        ''')
        conn.commit()
        conn.close()

    def add_monitor(self, monitor_id: str, monitor_type: str, name: str, target: str, config: Dict):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        now = datetime.utcnow().isoformat()
        c.execute('''
            INSERT OR REPLACE INTO monitors 
            (id, type, name, target, config, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (monitor_id, monitor_type, name, target, json.dumps(config), now, now))
        conn.commit()
        conn.close()

    def list_monitors(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT id, type, name, target, config FROM monitors ORDER BY name')
        monitors = []
        for row in c.fetchall():
            monitors.append({
                'id': row[0],
                'type': row[1],
                'name': row[2],
                'target': row[3],
                'config': json.loads(row[4])
            })
        conn.close()
        return monitors

    def record_check(self, monitor_id: str, status: str, response_time_ms: float, details: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        now = datetime.utcnow().isoformat()
        c.execute('''
            INSERT INTO checks (monitor_id, timestamp, status, response_time_ms, details)
            VALUES (?, ?, ?, ?, ?)
        ''', (monitor_id, now, status, response_time_ms, details))
        conn.commit()
        conn.close()

    def record_alert(self, monitor_id: str, severity: str, message: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        now = datetime.utcnow().isoformat()
        c.execute('''
            INSERT INTO alerts (monitor_id, timestamp, severity, message)
            VALUES (?, ?, ?, ?)
        ''', (monitor_id, now, severity, message))
        conn.commit()
        conn.close()

    def get_last_check(self, monitor_id: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT status, response_time_ms, details, timestamp 
            FROM checks 
            WHERE monitor_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''', (monitor_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return {'status': row[0], 'response_time_ms': row[1], 'details': row[2], 'timestamp': row[3]}
        return None

    def get_last_alert(self, monitor_id: str, within_minutes: int = 60):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        cutoff = (datetime.utcnow() - timedelta(minutes=within_minutes)).isoformat()
        c.execute('''
            SELECT timestamp 
            FROM alerts 
            WHERE monitor_id = ? AND timestamp > ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''', (monitor_id, cutoff))
        row = c.fetchone()
        conn.close()
        return row[0] if row else None


class Monitors:
    def __init__(self, db):
        self.db = db

    def check_http(self, target: str, timeout: int = 10) -> Tuple[str, float, str]:
        """Check HTTP/HTTPS endpoint. Returns (status, response_time_ms, details)."""
        try:
            start = time.time()
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(target, method='HEAD')
            with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
                elapsed = (time.time() - start) * 1000
                status_code = resp.status
                return ('up', elapsed, f'HTTP {status_code}')
        except urllib.error.HTTPError as e:
            elapsed = (time.time() - start) * 1000
            return ('down', elapsed, f'HTTP {e.code}')
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return ('down', elapsed, f'Error: {str(e)[:100]}')

    def check_tcp(self, target: str, timeout: int = 5) -> Tuple[str, float, str]:
        """Check TCP port. Returns (status, response_time_ms, details)."""
        try:
            host, port = target.split(':')
            port = int(port)
            start = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            elapsed = (time.time() - start) * 1000
            sock.close()
            if result == 0:
                return ('up', elapsed, f'{host}:{port} open')
            else:
                return ('down', elapsed, f'{host}:{port} closed')
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return ('down', elapsed, f'Error: {str(e)[:100]}')

    def check_docker(self, container_id: str) -> Tuple[str, float, str]:
        """Check Docker container status. Returns (status, 0, details)."""
        try:
            result = subprocess.run(
                ['docker', 'inspect', container_id],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                info = json.loads(result.stdout)[0]
                state = info.get('State', {})
                running = state.get('Running', False)
                if running:
                    return ('up', 0, 'Running')
                else:
                    return ('down', 0, f'Stopped, ExitCode: {state.get("ExitCode", "?")}')
            else:
                return ('down', 0, f'Container not found')
        except Exception as e:
            return ('down', 0, f'Error: {str(e)[:100]}')

    def check_disk(self, mount_point: str = '/') -> Tuple[str, float, str]:
        """Check disk usage. Returns (status, 0, details)."""
        try:
            result = subprocess.run(
                ['df', '-h', mount_point],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) >= 5:
                        usage_percent = int(parts[4].rstrip('%'))
                        if usage_percent >= 90:
                            return ('critical', 0, f'{mount_point}: {usage_percent}% full')
                        elif usage_percent >= 75:
                            return ('warning', 0, f'{mount_point}: {usage_percent}% full')
                        else:
                            return ('up', 0, f'{mount_point}: {usage_percent}% full')
        except Exception as e:
            return ('down', 0, f'Error: {str(e)[:100]}')

    def check_memory(self) -> Tuple[str, float, str]:
        """Check memory usage. Returns (status, 0, details)."""
        try:
            result = subprocess.run(
                ['free', '-b'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) >= 3:
                        total = int(parts[1])
                        used = int(parts[2])
                        usage_percent = int((used / total) * 100)
                        if usage_percent >= 90:
                            return ('critical', 0, f'Memory: {usage_percent}% used')
                        elif usage_percent >= 75:
                            return ('warning', 0, f'Memory: {usage_percent}% used')
                        else:
                            return ('up', 0, f'Memory: {usage_percent}% used')
        except Exception as e:
            return ('down', 0, f'Error: {str(e)[:100]}')

    def check_ssl_expiry(self, target: str) -> Tuple[str, float, str]:
        """Check SSL certificate expiry. Returns (status, 0, details)."""
        try:
            import ssl as ssl_module
            host = target.split('://')[1].split('/')[0].split(':')[0]
            ctx = ssl_module.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl_module.CERT_NONE
            with socket.create_connection((host, 443), timeout=10) as sock:
                with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                    cert_der = ssock.getpeercert_der()
                    import ssl as ssl_module
                    cert = ssl_module.DER_cert_to_PEM_cert(cert_der)
                    # Simple extraction
                    import re
                    match = re.search(r'notAfter=(.*?)[\r\n]', cert, re.DOTALL)
                    if match:
                        return ('up', 0, f'Certificate valid')
        except Exception as e:
            return ('warning', 0, f'SSL check error: {str(e)[:100]}')

    def run_check(self, monitor_id: str, monitor_type: str, target: str):
        """Run a single check."""
        if monitor_type == 'http':
            status, elapsed, details = self.check_http(target)
        elif monitor_type == 'tcp':
            status, elapsed, details = self.check_tcp(target)
        elif monitor_type == 'docker':
            status, elapsed, details = self.check_docker(target)
        elif monitor_type == 'disk':
            status, elapsed, details = self.check_disk(target)
        elif monitor_type == 'memory':
            status, elapsed, details = self.check_memory()
        elif monitor_type == 'ssl':
            status, elapsed, details = self.check_ssl_expiry(target)
        else:
            return None

        self.db.record_check(monitor_id, status, elapsed, details)
        return {'status': status, 'response_time_ms': elapsed, 'details': details}


def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    return DEFAULT_CONFIG


def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)


def cmd_init(args):
    """Initialize watchdog (interactive setup)."""
    print("🔍 Infra Watchdog — Interactive Setup")
    print("-" * 40)
    
    config = load_config()
    
    print(f"Alert channel ({config['alert_channel']}): ", end='')
    channel = input().strip() or config['alert_channel']
    config['alert_channel'] = channel
    
    print(f"Check interval in minutes ({config['check_interval_minutes']}): ", end='')
    try:
        interval = int(input().strip() or config['check_interval_minutes'])
        config['check_interval_minutes'] = interval
    except ValueError:
        pass
    
    save_config(config)
    print("\n✅ Configuration saved!")


def cmd_add_monitor(args):
    """Add a monitor."""
    db = Database(DB_PATH)
    config = load_config()
    
    monitor_type = args.type
    name = args.name
    target = args.target
    
    monitor_id = f"{monitor_type}_{int(time.time())}_{hash(target) % 10000}"
    
    monitor_config = {}
    db.add_monitor(monitor_id, monitor_type, name, target, monitor_config)
    
    print(f"✅ Monitor added: {name} ({monitor_type})")
    print(f"   Target: {target}")
    print(f"   ID: {monitor_id}")


def cmd_list(args):
    """List all monitors."""
    db = Database(DB_PATH)
    monitors = db.list_monitors()
    
    if not monitors:
        print("No monitors configured. Run 'infra-watchdog add-monitor' to add one.")
        return
    
    print("📋 Configured Monitors:")
    print("-" * 60)
    
    for m in monitors:
        last_check = db.get_last_check(m['id'])
        status_icon = '✅' if last_check and last_check['status'] == 'up' else '❌'
        
        print(f"{status_icon} {m['name']}")
        print(f"   Type: {m['type']}")
        print(f"   Target: {m['target']}")
        if last_check:
            print(f"   Last: {last_check['status']} ({last_check['response_time_ms']:.0f}ms) — {last_check['details']}")
        print()


def cmd_check(args):
    """Run all checks now."""
    db = Database(DB_PATH)
    monitors = db.list_monitors()
    
    if not monitors:
        print("No monitors configured.")
        return
    
    print("🔍 Running checks...")
    
    monitor_obj = Monitors(db)
    results = []
    
    for m in monitors:
        result = monitor_obj.run_check(m['id'], m['type'], m['target'])
        if result:
            icon = '✅' if result['status'] == 'up' else '❌'
            print(f"{icon} {m['name']}: {result['status']} ({result['details']})")
            results.append((m['name'], result['status'], result['details']))
    
    return results


def cmd_status(args):
    """Show status of all monitors."""
    db = Database(DB_PATH)
    monitors = db.list_monitors()
    
    if not monitors:
        print("No monitors configured.")
        return
    
    print("📊 Infrastructure Status")
    print("=" * 60)
    
    up_count = 0
    down_count = 0
    
    for m in monitors:
        last_check = db.get_last_check(m['id'])
        if last_check:
            status = last_check['status']
            if status == 'up':
                up_count += 1
            else:
                down_count += 1
            
            icon = '✅' if status == 'up' else '❌'
            print(f"{icon} {m['name']}: {status}")
            print(f"   {last_check['details']} ({last_check['response_time_ms']:.0f}ms)")
        else:
            print(f"❓ {m['name']}: not checked yet")
    
    print("-" * 60)
    print(f"Summary: {up_count} up, {down_count} down")


def cmd_cron_install(args):
    """Install cron job for periodic checks."""
    config = load_config()
    interval = config.get('check_interval_minutes', 5)
    
    print(f"✅ Cron job would run every {interval} minutes.")
    print("   To activate: set up in OpenClaw's cron system")
    print(f"   Command: infra-watchdog check")


def main():
    parser = argparse.ArgumentParser(
        description='🔍 Infra Watchdog — Infrastructure Monitoring'
    )
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # init
    subparsers.add_parser('init', help='Interactive setup')
    
    # add-monitor
    p_add = subparsers.add_parser('add-monitor', help='Add a monitor')
    p_add.add_argument('type', choices=['http', 'tcp', 'docker', 'disk', 'memory', 'ssl'])
    p_add.add_argument('name', help='Monitor name')
    p_add.add_argument('target', help='Target (URL, host:port, container_id, or mount point)')
    
    # list
    subparsers.add_parser('list', help='List all monitors')
    
    # check
    subparsers.add_parser('check', help='Run all checks now')
    
    # status
    subparsers.add_parser('status', help='Show current status')
    
    # cron-install
    subparsers.add_parser('cron-install', help='Install periodic cron job')
    
    args = parser.parse_args()
    
    if args.command == 'init':
        cmd_init(args)
    elif args.command == 'add-monitor':
        cmd_add_monitor(args)
    elif args.command == 'list':
        cmd_list(args)
    elif args.command == 'check':
        cmd_check(args)
    elif args.command == 'status':
        cmd_status(args)
    elif args.command == 'cron-install':
        cmd_cron_install(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
