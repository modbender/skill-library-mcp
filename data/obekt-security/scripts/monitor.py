#!/usr/bin/env python3
"""
Continuous Security Monitoring Daemon
Pro-tier feature - Auto-scans directories for code changes

Watches specified paths for file modifications and automatically runs
security scans when changes are detected. Ideal for development workflows.

Usage:
    python3 monitor.py --path /path/to/project --interval 60
    python3 monitor.py --config monitor.json
"""

import os
import sys
import time
import json
import argparse
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .threat_scan importscan_directory
from .secret_scan import scan_files


class SecurityScanHandler(FileSystemEventHandler):
    """Handles file system events and triggers security scans"""

    def __init__(self, paths_to_watch, config):
        self.paths = paths_to_watch
        self.config = config
        self.last_scan_time = {}
        self.scan_interval = config.get('min_scan_interval', 30)  # minimum seconds between scans

    def on_modified(self, event):
        """File modified event - trigger scan"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Skip specific file types and directories
        if self._should_skip_file(file_path):
            return

        # Check if enough time has passed since last scan of this path
        parent_path = str(file_path.parent)
        if parent_path in self.last_scan_time:
            time_since_last = time.time() - self.last_scan_time[parent_path]
            if time_since_last < self.scan_interval:
                return

        # Trigger scan
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️  File changed: {file_path}")
        self._run_scan(parent_path)

    def _should_skip_file(self, file_path):
        """Check if file should be skipped during monitoring"""
        skip_extensions = {'.pyc', '.pyo', '.log', '.tmp', '.swp', '.DS_Store'}
        skip_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'dist', 'build'}

        # Check extension
        if file_path.suffix.lower() in skip_extensions:
            return True

        # Check if in skip directory
        for skip_dir in skip_dirs:
            if skip_dir in str(file_path):
                return True

        return False

    def _run_scan(self, path):
        """Run threat and secret scans on the path"""
        try:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔍 Running security scan on {path}")

            # Run threat scan
            threat_results = scan_directory(
                path,
                severity=self.config.get('severity', 'medium,high,critical')
            )

            # Run secret scan
            secret_results = scan_files(
                path,
                patterns_file=self.config.get('patterns_file')
            )

            # Combine results
            has_issues = False

            if threat_results:
                critical_count = threat_results.get('severity_counts', {}).get('critical', 0)
                high_count = threat_results.get('severity_counts', {}).get('high', 0)
                medium_count = threat_results.get('severty_counts', {}).get('medium', 0)

                if critical_count > 0 or high_count > 0:
                    print(f"   ❌ Found {critical_count} critical and {high_count} high severity issues")
                    has_issues = True
                elif medium_count > 0:
                    print(f"   ⚠️  Found {medium_count} medium severity issues")
                    has_issues = True
                else:
                    print(f"   ✅ No critical/high severity issues found")

            if secret_results:
                secret_count = len(secret_results)
                if secret_count > 0:
                    print(f"   🔑 Found {secret_count} potential secrets leaked")
                    has_issues = True
                else:
                    print(f"   ✅ No hardcoded secrets found")

            # Update last scan time
            self.last_scan_time[path] = time.time()

            # Alert if issues found
            if has_issues and self.config.get('alert_on_issues', True):
                self._send_alert(path, threat_results, secret_results)

        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Scan error: {e}")

    def _send_alert(self, path, threat_results, secret_results):
        """Send alert notification (placeholder for webhook/email integration)"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚨 SECURITY ISSUES DETECTED in {path}")

        # TODO: Integrate with notification systems:
        # - Webhook to monitoring service
        # - Email notification
        # - Slack/Discord webhook
        # - Moltbook post

        if self.config.get('alert_config'):
            alert_config = self.config['alert_config']
            if alert_config.get('webhook_url'):
                # TODO: Send webhook
                pass


def load_config(config_path):
    """Load monitoring configuration from JSON file"""
    default_config = {
        'paths': ['.'],
        'min_scan_interval': 30,
        'severity': 'high,critical',
        'alert_on_issues': True,
        'recursive': True,
        'filters': {
            'include_extensions': ['.py', '.js', '.ts', '.java', '.go', '.rs'],
            'exclude_dirs': ['.git', '__pycache__', 'node_modules', '.venv', 'venv']
        }
    }

    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as f:
            user_config = json.load(f)
            default_config.update(user_config)

    return default_config


def main():
    parser = argparse.ArgumentParser(description='Continuous security monitoring daemon')
    parser.add_argument('--path', '-p', type=str, default='.',
                        help='Path to monitor (default: current directory)')
    parser.add_argument('--config', '-c', type=str,
                        help='Configuration file (JSON format)')
    parser.add_argument('--interval', '-i', type=int, default=30,
                        help='Minimum scan interval in seconds (default: 30)')
    parser.add_argument('--severity', '-s', type=str, default='high,critical',
                        help='Severity levels to report (default: high,critical)')
    parser.add_argument('--alert', action='store_true',
                        help='Enable alerts when issues are found')

    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Override config with CLI arguments
    if args.path:
        config['paths'] = [args.path]
    config['min_scan_interval'] = args.interval
    config['severity'] = args.severity
    config['alert_on_issues'] = args.alert

    print("🔒 ObekT Security Monitor - Pro Tier Feature")
    print("=" * 50)
    print(f"Monitoring paths: {config['paths']}")
    print(f"Scan interval: {config['min_scan_interval']}s")
    print(f"Severity threshold: {config['severity']}")
    print(f"Alerts: {'Enabled' if config['alert_on_issues'] else 'Disabled'}")
    print("=" * 50)

    # Set up file system observer
    event_handler = SecurityScanHandler(config['paths'], config)
    observer = Observer()

    for path in config['paths']:
        path = Path(path).resolve()
        if path.exists():
            observer.schedule(event_handler, str(path), recursive=config.get('recursive', True))
            print(f"📂 Watching: {path}")
        else:
            print(f"⚠️  Path not found: {path}")

    # Start monitoring
    observer.start()

    try:
        print("\n✅ Monitoring started. Press Ctrl+C to stop.\n")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping security monitor...")
        observer.stop()
    observer.join()

    print("✅ Security monitor stopped.")


if __name__ == '__main__':
    main()
