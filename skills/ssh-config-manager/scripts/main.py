#!/usr/bin/env python3
"""
SSH Config Manager - CLI tool to manage SSH configuration files
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

class SSHConfigManager:
    def __init__(self, config_path: str = None):
        """Initialize SSH config manager."""
        self.config_path = config_path or os.path.expanduser("~/.ssh/config")
        self.backup_dir = os.path.expanduser("~/.ssh/backups")
        
        # Create backup directory if it doesn't exist
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def backup_config(self) -> str:
        """Create a backup of the current config file."""
        if not os.path.exists(self.config_path):
            return ""
        
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.backup_dir, f"config_backup_{timestamp}")
        
        try:
            with open(self.config_path, 'r') as src:
                with open(backup_path, 'w') as dst:
                    dst.write(src.read())
            return backup_path
        except Exception as e:
            print(f"Warning: Failed to create backup: {e}")
            return ""
    
    def parse_config(self) -> List[Dict[str, Any]]:
        """Parse SSH config file and return list of hosts."""
        hosts = []
        current_host = {}
        
        if not os.path.exists(self.config_path):
            return hosts
        
        try:
            with open(self.config_path, 'r') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Check if this is a Host directive
                if line.lower().startswith('host '):
                    # Save previous host if exists
                    if current_host:
                        hosts.append(current_host)
                    
                    # Start new host
                    parts = line.split(maxsplit=1)
                    if len(parts) > 1:
                        host_pattern = parts[1]
                    else:
                        host_pattern = ""
                    
                    current_host = {
                        'host': host_pattern,
                        'options': {}
                    }
                elif current_host:
                    # Parse SSH config option (key value separated by space or tab)
                    # SSH config uses space-separated key-value pairs, not '='
                    # Some options may have '=' in the value (like IdentityFile with options)
                    # We'll split on first space or tab
                    if ' ' in line:
                        key, value = line.split(maxsplit=1)
                        current_host['options'][key.lower()] = value.strip()
                    elif '	' in line:
                        key, value = line.split('	', maxsplit=1)
                        current_host['options'][key.lower()] = value.strip()
                    # If no space or tab (shouldn't happen in valid config), ignore
            
            # Add the last host
            if current_host:
                hosts.append(current_host)
                
        except Exception as e:
            print(f"Error parsing config file: {e}")
        
        return hosts
        
        try:
            with open(self.config_path, 'r') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Check if this is a Host directive
                if line.lower().startswith('host '):
                    # Save previous host if exists
                    if current_host:
                        hosts.append(current_host)
                    
                    # Start new host
                    parts = line.split(maxsplit=1)
                    if len(parts) > 1:
                        host_pattern = parts[1]
                    else:
                        host_pattern = ""
                    
                    current_host = {
                        'host': host_pattern,
                        'options': {}
                    }
                elif current_host and '=' in line:
                    # Parse option (key=value or key value)
                    if ' ' in line:
                        key, value = line.split(maxsplit=1)
                        current_host['options'][key.lower()] = value.strip()
                    elif '\t' in line:
                        key, value = line.split('\t', maxsplit=1)
                        current_host['options'][key.lower()] = value.strip()
            
            # Add the last host
            if current_host:
                hosts.append(current_host)
                
        except Exception as e:
            print(f"Error parsing config file: {e}")
        
        return hosts
    
    def write_config(self, hosts: List[Dict[str, Any]]) -> bool:
        """Write hosts back to SSH config file."""
        try:
            with open(self.config_path, 'w') as f:
                for host in hosts:
                    f.write(f"Host {host['host']}\n")
                    for key, value in host['options'].items():
                        f.write(f"    {key} {value}\n")
                    f.write("\n")
            return True
        except Exception as e:
            print(f"Error writing config file: {e}")
            return False
    
    def add_host(self, host: str, hostname: str, user: str = None, 
                 port: int = None, identityfile: str = None, tags: str = None,
                 description: str = None, **kwargs) -> Dict[str, Any]:
        """Add a new host to SSH config."""
        options = {}
        
        # Required options
        options['hostname'] = hostname
        
        # Optional options
        if user:
            options['user'] = user
        if port:
            options['port'] = str(port)
        if identityfile:
            options['identityfile'] = identityfile
        
        # Additional options from kwargs
        for key, value in kwargs.items():
            if value:
                options[key.lower()] = str(value)
        
        # Create host entry
        host_entry = {
            'host': host,
            'options': options
        }
        
        # Parse existing config
        hosts = self.parse_config()
        
        # Check if host already exists
        for i, existing_host in enumerate(hosts):
            if existing_host['host'] == host:
                # Update existing host
                hosts[i] = host_entry
                break
        else:
            # Add new host
            hosts.append(host_entry)
        
        # Create backup
        backup_path = self.backup_config()
        
        # Write updated config
        if self.write_config(hosts):
            return {
                'status': 'success',
                'host': host,
                'backup': backup_path,
                'message': f'Host {host} added successfully'
            }
        else:
            return {
                'status': 'error',
                'host': host,
                'message': f'Failed to add host {host}'
            }
    
    def remove_host(self, host: str) -> Dict[str, Any]:
        """Remove a host from SSH config."""
        hosts = self.parse_config()
        original_count = len(hosts)
        
        # Filter out the host to remove
        hosts = [h for h in hosts if h['host'] != host]
        
        if len(hosts) == original_count:
            return {
                'status': 'error',
                'host': host,
                'message': f'Host {host} not found'
            }
        
        # Create backup
        backup_path = self.backup_config()
        
        # Write updated config
        if self.write_config(hosts):
            return {
                'status': 'success',
                'host': host,
                'backup': backup_path,
                'message': f'Host {host} removed successfully'
            }
        else:
            return {
                'status': 'error',
                'host': host,
                'message': f'Failed to remove host {host}'
            }
    
    def test_connection(self, host: str, timeout: int = 5) -> Dict[str, Any]:
        """Test SSH connection to a host."""
        # First, parse the config to get host details
        hosts = self.parse_config()
        target_host = None
        
        for h in hosts:
            if h['host'] == host:
                target_host = h
                break
        
        if not target_host:
            return {
                'status': 'error',
                'host': host,
                'message': f'Host {host} not found in config'
            }
        
        # Build SSH command
        options = target_host['options']
        ssh_command = ['ssh', '-o', 'ConnectTimeout=' + str(timeout), '-o', 'BatchMode=yes']
        
        if 'port' in options:
            ssh_command.extend(['-p', options['port']])
        
        if 'user' in options:
            sshname = f"{options['user']}@{options['hostname']}"
        else:
            sshname = options['hostname']
        
        ssh_command.extend([sshname, 'exit'])
        
        try:
            start_time = time.time()
            result = subprocess.run(
                ssh_command,
                capture_output=True,
                text=True,
                timeout=timeout + 2
            )
            elapsed = time.time() - start_time
            
            if result.returncode == 0:
                return {
                    'status': 'success',
                    'host': host,
                    'hostname': options['hostname'],
                    'time_ms': int(elapsed * 1000),
                    'message': 'Connection successful'
                }
            else:
                return {
                    'status': 'error',
                    'host': host,
                    'hostname': options['hostname'],
                    'exit_code': result.returncode,
                    'stderr': result.stderr.strip(),
                    'message': 'Connection failed'
                }
        except subprocess.TimeoutExpired:
            return {
                'status': 'error',
                'host': host,
                'hostname': options.get('hostname', 'unknown'),
                'message': f'Connection timeout after {timeout} seconds'
            }
        except Exception as e:
            return {
                'status': 'error',
                'host': host,
                'hostname': options.get('hostname', 'unknown'),
                'message': f'Error: {str(e)}'
            }
    
    def list_hosts(self, format: str = 'table', filter_tags: str = None) -> List[Dict[str, Any]]:
        """List all hosts in SSH config."""
        hosts = self.parse_config()
        
        if filter_tags:
            filter_tags_list = [tag.strip() for tag in filter_tags.split(',')]
            # Extract tags from host patterns or descriptions
            filtered_hosts = []
            for host in hosts:
                # Simple tag filtering based on host pattern
                host_lower = host['host'].lower()
                if any(tag.lower() in host_lower for tag in filter_tags_list):
                    filtered_hosts.append(host)
            hosts = filtered_hosts
        
        return hosts
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate SSH config syntax."""
        if not os.path.exists(self.config_path):
            return {
                'status': 'error',
                'message': f'Config file not found: {self.config_path}'
            }
        
        try:
            # Try to parse the config
            hosts = self.parse_config()
            
            # Check for common issues
            issues = []
            
            with open(self.config_path, 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    line = line.rstrip('\n')
                    stripped = line.strip()
                    
                    # Check for lines with Host directive but no pattern
                    if stripped.lower().startswith('host ') and len(stripped.split()) == 1:
                        issues.append(f'Line {i}: Host directive without pattern')
                    
                    # Check for lines with option but no value
                    if stripped and not stripped.startswith('#') and not stripped.lower().startswith('host'):
                        if ' ' in stripped:
                            key, value = stripped.split(maxsplit=1)
                            if not value.strip():
                                issues.append(f'Line {i}: Option "{key}" has no value')
                        elif '\t' in stripped:
                            key, value = stripped.split('\t', maxsplit=1)
                            if not value.strip():
                                issues.append(f'Line {i}: Option "{key}" has no value')
            
            if issues:
                return {
                    'status': 'warning',
                    'hosts_count': len(hosts),
                    'issues': issues,
                    'message': f'Found {len(issues)} issue(s) in config'
                }
            else:
                return {
                    'status': 'success',
                    'hosts_count': len(hosts),
                    'message': f'Config valid with {len(hosts)} hosts'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Validation error: {str(e)}'
            }

def format_table(hosts: List[Dict[str, Any]]) -> str:
    """Format hosts as a table."""
    if not hosts:
        return "No hosts found in SSH config."
    
    # Determine column widths
    max_host_len = max(len(h['host']) for h in hosts)
    max_hostname_len = max(len(h['options'].get('hostname', '')) for h in hosts)
    max_user_len = max(len(h['options'].get('user', '')) for h in hosts)
    
    # Ensure minimum widths
    max_host_len = max(max_host_len, 10)
    max_hostname_len = max(max_hostname_len, 15)
    max_user_len = max(max_user_len, 8)
    
    # Build table
    lines = []
    header = f"┌{'─' * (max_host_len + 2)}┬{'─' * (max_hostname_len + 2)}┬{'─' * (max_user_len + 2)}┐"
    lines.append(header)
    lines.append(f"│ {'Host'.ljust(max_host_len)} │ {'Hostname'.ljust(max_hostname_len)} │ {'User'.ljust(max_user_len)} │")
    lines.append(f"├{'─' * (max_host_len + 2)}┼{'─' * (max_hostname_len + 2)}┼{'─' * (max_user_len + 2)}┤")
    
    for host in hosts:
        host_str = host['host'][:max_host_len].ljust(max_host_len)
        hostname_str = host['options'].get('hostname', '')[:max_hostname_len].ljust(max_hostname_len)
        user_str = host['options'].get('user', '')[:max_user_len].ljust(max_user_len)
        lines.append(f"│ {host_str} │ {hostname_str} │ {user_str} │")
    
    lines.append(f"└{'─' * (max_host_len + 2)}┴{'─' * (max_hostname_len + 2)}┴{'─' * (max_user_len + 2)}┘")
    
    return '\n'.join(lines)

def main():
    parser = argparse.ArgumentParser(description="Manage SSH configuration files")
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all hosts in SSH config')
    list_parser.add_argument('--format', choices=['table', 'json', 'yaml'], default='table', help='Output format')
    list_parser.add_argument('--tags', help='Filter by tags (comma-separated)')
    list_parser.add_argument('--config', help='Path to SSH config file')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new host to SSH config')
    add_parser.add_argument('--host', required=True, help='Host alias/pattern')
    add_parser.add_argument('--hostname', required=True, help='Hostname or IP address')
    add_parser.add_argument('--user', help='Username')
    add_parser.add_argument('--port', type=int, help='Port number')
    add_parser.add_argument('--identityfile', help='Identity file path')
    add_parser.add_argument('--tag', help='Tags (comma-separated)')
    add_parser.add_argument('--description', help='Description')
    add_parser.add_argument('--config', help='Path to SSH config file')
    
    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove a host from SSH config')
    remove_parser.add_argument('--host', required=True, help='Host alias/pattern to remove')
    remove_parser.add_argument('--config', help='Path to SSH config file')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test SSH connection to a host')
    test_parser.add_argument('--host', required=True, help='Host alias/pattern to test')
    test_parser.add_argument('--timeout', type=int, default=5, help='Connection timeout in seconds')
    test_parser.add_argument('--config', help='Path to SSH config file')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate SSH config syntax')
    validate_parser.add_argument('--config', help='Path to SSH config file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = SSHConfigManager(args.config)
    
    if args.command == 'list':
        hosts = manager.list_hosts(filter_tags=args.tags)
        
        if args.format == 'json':
            import json
            print(json.dumps(hosts, indent=2))
        elif args.format == 'yaml':
            import yaml
            print(yaml.dump(hosts, default_flow_style=False))
        else:
            print(format_table(hosts))
            print(f"\nTotal hosts: {len(hosts)}")
    
    elif args.command == 'add':
        result = manager.add_host(
            host=args.host,
            hostname=args.hostname,
            user=args.user,
            port=args.port,
            identityfile=args.identityfile,
            tags=args.tag,
            description=args.description
        )
        
        if result['status'] == 'success':
            print(f"✅ {result['message']}")
            if result.get('backup'):
                print(f"   Backup created at: {result['backup']}")
        else:
            print(f"❌ {result['message']}")
    
    elif args.command == 'remove':
        result = manager.remove_host(host=args.host)
        
        if result['status'] == 'success':
            print(f"✅ {result['message']}")
            if result.get('backup'):
                print(f"   Backup created at: {result['backup']}")
        else:
            print(f"❌ {result['message']}")
    
    elif args.command == 'test':
        result = manager.test_connection(host=args.host, timeout=args.timeout)
        
        if result['status'] == 'success':
            print(f"✅ {result['message']}")
            print(f"   Host: {result['host']}")
            print(f"   Hostname: {result['hostname']}")
            print(f"   Time: {result['time_ms']}ms")
        else:
            print(f"❌ {result['message']}")
            if 'hostname' in result:
                print(f"   Hostname: {result['hostname']}")
            if 'stderr' in result:
                print(f"   Error: {result['stderr']}")
    
    elif args.command == 'validate':
        result = manager.validate_config()
        
        if result['status'] == 'success':
            print(f"✅ {result['message']}")
        elif result['status'] == 'warning':
            print(f"⚠️  {result['message']}")
            for issue in result.get('issues', []):
                print(f"   - {issue}")
        else:
            print(f"❌ {result['message']}")

if __name__ == "__main__":
    main()