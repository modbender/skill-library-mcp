#!/usr/bin/env python3
"""
aria2-rpc: Remote control for aria2 download service via JSON-RPC 2.0

Usage:
    python3 aria2_rpc.py <command> [options] [arguments]

Commands:
    add-uri       Add HTTP/FTP/Magnet download
    tell-active   Get active downloads
    tell-waiting  Get waiting downloads
    tell-stopped  Get stopped downloads
    tell-status   Get task status by GID
    pause         Pause download
    unpause       Resume download
    remove        Remove download
    remove-force  Force remove download
    global-stat   Get global statistics

Environment Variables:
    ARIA2_RPC_URL     RPC endpoint URL (default: http://localhost:6800/jsonrpc)
    ARIA2_RPC_SECRET  RPC secret token (optional)
"""

import json
import sys
import os
import argparse
import base64
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests library not installed. Run: pip3 install requests", file=sys.stderr)
    sys.exit(1)


class Aria2RPC:
    """aria2 JSON-RPC 2.0 client"""
    
    def __init__(self, rpc_url=None, rpc_secret=None, timeout=30):
        self.rpc_url = rpc_url or os.environ.get(
            'ARIA2_RPC_URL', 
            'http://localhost:6800/jsonrpc'
        )
        self.rpc_secret = rpc_secret or os.environ.get('ARIA2_RPC_SECRET')
        self.timeout = timeout
        self.session = requests.Session()
    
    def _get_auth_token(self):
        """Get authentication token"""
        if self.rpc_secret:
            return f'token:{self.rpc_secret}'
        return None
    
    def _call(self, method, params=None):
        """Make JSON-RPC 2.0 call"""
        payload = {
            'jsonrpc': '2.0',
            'id': 'aria2-rpc',
            'method': f'aria2.{method}'
        }
        
        # Add auth token as first parameter if exists
        auth_token = self._get_auth_token()
        if params is None:
            params = []
        
        if auth_token:
            params = [auth_token] + list(params)
        
        payload['params'] = params
        
        try:
            response = self.session.post(
                self.rpc_url,
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            result = response.json()
            
            if 'error' in result:
                error = result['error']
                print(f"Error: {error.get('message', 'Unknown error')}", file=sys.stderr)
                if 'data' in error:
                    print(f"Details: {error['data']}", file=sys.stderr)
                return None
            
            return result.get('result')
        
        except requests.exceptions.ConnectionError as e:
            print(f"Error: Cannot connect to aria2 RPC at {self.rpc_url}", file=sys.stderr)
            print(f"Details: {e}", file=sys.stderr)
            return None
        except requests.exceptions.Timeout:
            print(f"Error: Connection timeout ({self.timeout}s)", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return None
    
    def add_uri(self, uris, options=None):
        """Add URI download(s)"""
        params = [uris]
        if options:
            params.append(options)
        return self._call('addUri', params)
    
    def add_torrent(self, torrent_path, uris=None, options=None):
        """Add torrent download"""
        try:
            with open(torrent_path, 'rb') as f:
                torrent_b64 = base64.b64encode(f.read()).decode('utf-8')
            
            params = [torrent_b64]
            if uris is None:
                uris = []
            params.append(uris)
            if options:
                params.append(options)
            else:
                params.append({})
            return self._call('addTorrent', params)
        except FileNotFoundError:
            print(f"Error: Torrent file not found: {torrent_path}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Error reading torrent file: {e}", file=sys.stderr)
            return None
    
    def add_metalink(self, metalink_path):
        """Add metalink download"""
        try:
            with open(metalink_path, 'rb') as f:
                metalink_b64 = base64.b64encode(f.read()).decode('utf-8')
            return self._call('addMetalink', [metalink_b64])
        except Exception as e:
            print(f"Error reading metalink file: {e}", file=sys.stderr)
            return None
    
    def tell_active(self):
        """Get active downloads"""
        return self._call('tellActive')
    
    def tell_waiting(self, offset=0, num=1000):
        """Get waiting downloads"""
        return self._call('tellWaiting', [offset, num])
    
    def tell_stopped(self, offset=0, num=1000):
        """Get stopped downloads"""
        return self._call('tellStopped', [offset, num])
    
    def tell_status(self, gid):
        """Get task status by GID"""
        return self._call('tellStatus', [gid])
    
    def pause(self, gid):
        """Pause download"""
        return self._call('pause', [gid])
    
    def force_pause(self, gid):
        """Force pause download"""
        return self._call('forcePause', [gid])
    
    def unpause(self, gid):
        """Resume download"""
        return self._call('unpause', [gid])
    
    def remove(self, gid):
        """Remove download"""
        return self._call('remove', [gid])
    
    def force_remove(self, gid):
        """Force remove download"""
        return self._call('forceRemove', [gid])
    
    def get_global_stat(self):
        """Get global statistics"""
        return self._call('getGlobalStat')
    
    def purge_download_result(self):
        """Purge completed/error/removed downloads"""
        return self._call('purgeDownloadResult')
    
    def get_version(self):
        """Get aria2 version"""
        return self._call('getVersion')
    
    def get_global_option(self):
        """Get global options"""
        return self._call('getGlobalOption')
    
    def change_global_option(self, options):
        """Change global options
        
        Args:
            options: dict of option name -> value
            
        Returns:
            'OK' on success
        """
        return self._call('changeGlobalOption', [options])
    
    def get_option(self, gid):
        """Get options for a specific download"""
        return self._call('getOption', [gid])
    
    def change_option(self, gid, options):
        """Change options for a specific download
        
        Args:
            gid: Task GID
            options: dict of option name -> value
            
        Returns:
            'OK' on success
        """
        return self._call('changeOption', [gid, options])


def format_size(size_bytes):
    """Format byte size to human readable"""
    if size_bytes is None:
        return "N/A"
    
    size_bytes = int(size_bytes)
    if size_bytes < 0:
        return "N/A"
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def format_speed(speed):
    """Format speed to human readable"""
    return format_size(speed) + "/s" if speed else "N/A"


def format_time(seconds):
    """Format seconds to human readable"""
    if seconds is None or seconds < 0:
        return "N/A"
    
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins}m {secs}s"
    else:
        hours = seconds // 3600
        mins = (seconds % 3600) // 60
        return f"{hours}h {mins}m"


def print_task(task, verbose=False):
    """Print task information"""
    gid = task.get('gid', 'N/A')[:8]
    status = task.get('status', 'unknown')
    files = task.get('files', [])
    filename = files[0].get('path', '') if files else 'N/A'
    if not filename or filename == 'N/A':
        filename = files[0].get('uris', [{}])[0].get('uri', 'N/A') if files else 'N/A'
    
    # Just show filename without path
    if '/' in filename:
        filename = filename.split('/')[-1]
    
    total_length = int(task.get('totalLength', 0))
    completed_length = int(task.get('completedLength', 0))
    download_speed = int(task.get('downloadSpeed', 0))
    upload_speed = int(task.get('uploadSpeed', 0))
    num_peers = task.get('numSeeders', task.get('connections', 'N/A'))
    
    # Progress
    if total_length > 0:
        progress = (completed_length / total_length) * 100
        progress_str = f"{progress:.1f}%"
    else:
        progress_str = "N/A"
    
    # ETA
    if download_speed > 0 and total_length > completed_length:
        eta = (total_length - completed_length) / download_speed
        eta_str = format_time(eta)
    else:
        eta_str = "N/A"
    
    print(f"\n[GID: {gid}] {filename}")
    print(f"  Status: {status} | Progress: {progress_str}")
    print(f"  Size: {format_size(completed_length)} / {format_size(total_length)}")
    print(f"  Speed: ↓ {format_speed(download_speed)} | ↑ {format_speed(upload_speed)}")
    print(f"  Connections/Peers: {num_peers} | ETA: {eta_str}")
    
    if verbose:
        if 'bittorrent' in task:
            bt = task['bittorrent']
            print(f"  Torrent: {bt.get('name', 'N/A')}")
            print(f"  Mode: {task.get('seeder', 'N/A')}")


def cmd_add_uri(args):
    """Handle add-uri command"""
    rpc = Aria2RPC(rpc_url=args.rpc_url, rpc_secret=args.rpc_secret)
    
    uris = args.uris
    options = {}
    
    if args.dir:
        options['dir'] = args.dir
    if args.out:
        options['out'] = args.out
    if args.split:
        options['split'] = str(args.split)
    if args.max_connections:
        options['max-connection-per-server'] = str(args.max_connections)
    
    result = rpc.add_uri(uris, options if options else None)
    
    if result:
        print(f"✓ Download added successfully")
        print(f"  GID: {result}")
        if len(uris) == 1:
            print(f"  URI: {uris[0]}")
        else:
            print(f"  URIs: {len(uris)} sources")
    else:
        sys.exit(1)


def cmd_tell_active(args):
    """Handle tell-active command"""
    rpc = Aria2RPC(rpc_url=args.rpc_url, rpc_secret=args.rpc_secret)
    
    result = rpc.tell_active()
    
    if result is None:
        sys.exit(1)
    
    tasks = result if isinstance(result, list) else []
    
    if not tasks:
        print("No active downloads")
    else:
        print(f"Active downloads: {len(tasks)}")
        print("=" * 60)
        for task in tasks:
            print_task(task, verbose=args.verbose)


def cmd_tell_waiting(args):
    """Handle tell-waiting command"""
    rpc = Aria2RPC(rpc_url=args.rpc_url, rpc_secret=args.rpc_secret)
    
    result = rpc.tell_waiting(offset=args.offset, num=args.num)
    
    if result is None:
        sys.exit(1)
    
    tasks = result if isinstance(result, list) else []
    
    if not tasks:
        print("No waiting downloads")
    else:
        print(f"Waiting downloads: {len(tasks)}")
        print("=" * 60)
        for task in tasks:
            print_task(task, verbose=args.verbose)


def cmd_tell_stopped(args):
    """Handle tell-stopped command"""
    rpc = Aria2RPC(rpc_url=args.rpc_url, rpc_secret=args.rpc_secret)
    
    result = rpc.tell_stopped(offset=args.offset, num=args.num)
    
    if result is None:
        sys.exit(1)
    
    tasks = result if isinstance(result, list) else []
    
    if not tasks:
        print("No stopped downloads")
    else:
        print(f"Stopped downloads: {len(tasks)}")
        print("=" * 60)
        for task in tasks:
            print_task(task, verbose=args.verbose)


def cmd_tell_status(args):
    """Handle tell-status command"""
    rpc = Aria2RPC(rpc_url=args.rpc_url, rpc_secret=args.rpc_secret)
    
    result = rpc.tell_status(args.gid)
    
    if result is None:
        sys.exit(1)
    
    print_task(result, verbose=True)
    
    # Show error message if present
    if result.get('errorMessage'):
        print(f"\n⚠ Error: {result['errorMessage']}")


def cmd_pause(args):
    """Handle pause command"""
    rpc = Aria2RPC(rpc_url=args.rpc_url, rpc_secret=args.rpc_secret)
    
    if args.force:
        result = rpc.force_pause(args.gid)
    else:
        result = rpc.pause(args.gid)
    
    if result:
        print(f"✓ Download paused: {args.gid}")
    else:
        sys.exit(1)


def cmd_unpause(args):
    """Handle unpause command"""
    rpc = Aria2RPC(rpc_url=args.rpc_url, rpc_secret=args.rpc_secret)
    
    result = rpc.unpause(args.gid)
    
    if result:
        print(f"✓ Download resumed: {args.gid}")
    else:
        sys.exit(1)


def cmd_remove(args):
    """Handle remove command"""
    rpc = Aria2RPC(rpc_url=args.rpc_url, rpc_secret=args.rpc_secret)
    
    if args.force:
        result = rpc.force_remove(args.gid)
    else:
        result = rpc.remove(args.gid)
    
    if result:
        print(f"✓ Download removed: {args.gid}")
    else:
        sys.exit(1)


def cmd_global_stat(args):
    """Handle global-stat command"""
    rpc = Aria2RPC(rpc_url=args.rpc_url, rpc_secret=args.rpc_secret)
    
    result = rpc.get_global_stat()
    
    if result is None:
        sys.exit(1)
    
    print("aria2 Global Statistics")
    print("=" * 60)
    print(f"Active downloads:      {result.get('numActive', 0)}")
    print(f"Waiting downloads:     {result.get('numWaiting', 0)}")
    print(f"Stopped downloads:     {result.get('numStopped', 0)}")
    print(f"Total speed:           ↓ {format_speed(int(result.get('downloadSpeed', 0)))}")
    print(f"                       ↑ {format_speed(int(result.get('uploadSpeed', 0)))}")
    print(f"Files downloaded:      {result.get('numFilesDownloaded', 0)}")
    print(f"Files removed:         {result.get('numFilesRemoved', 0)}")
    
    # Get version
    version_result = rpc.get_version()
    if version_result:
        version = version_result.get('version', 'N/A')
        enabled_features = version_result.get('enabledFeatures', [])
        print(f"\naria2 Version:       {version}")
        if enabled_features:
            print(f"Enabled Features:    {', '.join(enabled_features[:5])}...")


def cmd_get_global_option(args):
    """Handle get-global-option command"""
    rpc = Aria2RPC(rpc_url=args.rpc_url, rpc_secret=args.rpc_secret)
    
    result = rpc.get_global_option()
    
    if result is None:
        sys.exit(1)
    
    print("aria2 Global Options")
    print("=" * 60)
    
    # Filter and display options
    if args.key:
        # Show specific option
        if args.key in result:
            print(f"{args.key}: {result[args.key]}")
        else:
            print(f"Option '{args.key}' not found")
            print(f"\nAvailable options:")
            for key in sorted(result.keys()):
                print(f"  {key}")
            sys.exit(1)
    else:
        # Show all options
        if args.verbose:
            # Show all options
            for key in sorted(result.keys()):
                print(f"{key}: {result[key]}")
        else:
            # Show common options only
            common_options = [
                'max-concurrent-downloads',
                'max-overall-download-limit',
                'max-overall-upload-limit',
                'max-connection-per-server',
                'split',
                'min-split-size',
                'dir',
                'continue',
                'enable-rpc',
                'rpc-listen-port',
                'save-session',
                'user-agent',
                'all-proxy',
                'timeout',
                'connect-timeout',
                'max-tries',
                'retry-wait'
            ]
            
            print("Common Options:")
            print("-" * 60)
            for key in common_options:
                if key in result:
                    value = result[key]
                    # Truncate long values
                    if len(str(value)) > 50:
                        value = str(value)[:47] + "..."
                    print(f"{key}: {value}")
            
            print(f"\nTotal: {len(result)} options")
            print("\nUse --verbose to show all options")
            print("Use --key <option-name> to show specific option")


def cmd_set_global_option(args):
    """Handle set-global-option command"""
    rpc = Aria2RPC(rpc_url=args.rpc_url, rpc_secret=args.rpc_secret)
    
    # Parse options
    options = {}
    if args.options:
        for opt in args.options:
            if '=' in opt:
                key, value = opt.split('=', 1)
                options[key] = value
            else:
                print(f"Error: Invalid option format '{opt}'. Use KEY=VALUE", file=sys.stderr)
                sys.exit(1)
    
    if not options:
        print("Error: No options specified. Use KEY=VALUE format", file=sys.stderr)
        print("Example: --set max-overall-download-limit=10M", file=sys.stderr)
        sys.exit(1)
    
    result = rpc.change_global_option(options)
    
    if result:
        print("✓ Global options updated successfully")
        print("\nChanged options:")
        for key, value in options.items():
            print(f"  {key}: {value}")
    else:
        sys.exit(1)


def cmd_get_option(args):
    """Handle get-option command"""
    rpc = Aria2RPC(rpc_url=args.rpc_url, rpc_secret=args.rpc_secret)
    
    result = rpc.get_option(args.gid)
    
    if result is None:
        sys.exit(1)
    
    print(f"Options for Task: {args.gid}")
    print("=" * 60)
    
    if args.verbose:
        # Show all options
        for key in sorted(result.keys()):
            print(f"{key}: {result[key]}")
    else:
        # Show common options only
        common_options = [
            'dir',
            'out',
            'split',
            'min-split-size',
            'max-connection-per-server',
            'dry-run',
            'resume',
            'all-proxy',
            'user-agent',
            'timeout',
            'connect-timeout'
        ]
        
        print("Common Options:")
        print("-" * 60)
        for key in common_options:
            if key in result:
                value = result[key]
                if len(str(value)) > 60:
                    value = str(value)[:57] + "..."
                print(f"{key}: {value}")
        
        print(f"\nTotal: {len(result)} options")
        print("\nUse --verbose to show all options")


def cmd_set_option(args):
    """Handle set-option command"""
    rpc = Aria2RPC(rpc_url=args.rpc_url, rpc_secret=args.rpc_secret)
    
    # Parse options
    options = {}
    if args.options:
        for opt in args.options:
            if '=' in opt:
                key, value = opt.split('=', 1)
                options[key] = value
            else:
                print(f"Error: Invalid option format '{opt}'. Use KEY=VALUE", file=sys.stderr)
                sys.exit(1)
    
    if not options:
        print("Error: No options specified. Use KEY=VALUE format", file=sys.stderr)
        print("Example: --set split=16", file=sys.stderr)
        sys.exit(1)
    
    result = rpc.change_option(args.gid, options)
    
    if result:
        print(f"✓ Options updated for task: {args.gid}")
        print("\nChanged options:")
        for key, value in options.items():
            print(f"  {key}: {value}")
    else:
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='aria2-rpc: Remote control for aria2 download service',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  ARIA2_RPC_URL     RPC endpoint URL (default: http://localhost:6800/jsonrpc)
  ARIA2_RPC_SECRET  RPC secret token (optional)

Examples:
  %(prog)s add-uri http://example.com/file.zip
  %(prog)s add-uri http://mirror1/file.zip http://mirror2/file.zip --dir /downloads
  %(prog)s tell-active
  %(prog)s tell-status abc12345
  %(prog)s pause abc12345
  %(prog)s remove abc12345
  %(prog)s global-stat
        """
    )
    
    parser.add_argument('--rpc-url', help='RPC endpoint URL')
    parser.add_argument('--rpc-secret', help='RPC secret token')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # add-uri command
    add_uri_parser = subparsers.add_parser('add-uri', help='Add HTTP/FTP/Magnet download')
    add_uri_parser.add_argument('uris', nargs='+', help='URIs to download')
    add_uri_parser.add_argument('--dir', help='Download directory')
    add_uri_parser.add_argument('--out', help='Output filename')
    add_uri_parser.add_argument('-s', '--split', type=int, help='Number of connections')
    add_uri_parser.add_argument('-x', '--max-connections', type=int, help='Max connections per server')
    add_uri_parser.set_defaults(func=cmd_add_uri)
    
    # tell-active command
    tell_active_parser = subparsers.add_parser('tell-active', help='Get active downloads')
    tell_active_parser.set_defaults(func=cmd_tell_active)
    
    # tell-waiting command
    tell_waiting_parser = subparsers.add_parser('tell-waiting', help='Get waiting downloads')
    tell_waiting_parser.add_argument('--offset', type=int, default=0, help='Offset')
    tell_waiting_parser.add_argument('--num', type=int, default=1000, help='Number of results')
    tell_waiting_parser.set_defaults(func=cmd_tell_waiting)
    
    # tell-stopped command
    tell_stopped_parser = subparsers.add_parser('tell-stopped', help='Get stopped downloads')
    tell_stopped_parser.add_argument('--offset', type=int, default=0, help='Offset')
    tell_stopped_parser.add_argument('--num', type=int, default=1000, help='Number of results')
    tell_stopped_parser.set_defaults(func=cmd_tell_stopped)
    
    # tell-status command
    tell_status_parser = subparsers.add_parser('tell-status', help='Get task status by GID')
    tell_status_parser.add_argument('gid', help='Task GID')
    tell_status_parser.set_defaults(func=cmd_tell_status)
    
    # pause command
    pause_parser = subparsers.add_parser('pause', help='Pause download')
    pause_parser.add_argument('gid', help='Task GID')
    pause_parser.add_argument('-f', '--force', action='store_true', help='Force pause')
    pause_parser.set_defaults(func=cmd_pause)
    
    # unpause command
    unpause_parser = subparsers.add_parser('unpause', help='Resume download')
    unpause_parser.add_argument('gid', help='Task GID')
    unpause_parser.set_defaults(func=cmd_unpause)
    
    # remove command
    remove_parser = subparsers.add_parser('remove', help='Remove download')
    remove_parser.add_argument('gid', help='Task GID')
    remove_parser.add_argument('-f', '--force', action='store_true', help='Force remove')
    remove_parser.set_defaults(func=cmd_remove)
    
    # global-stat command
    global_stat_parser = subparsers.add_parser('global-stat', help='Get global statistics')
    global_stat_parser.set_defaults(func=cmd_global_stat)
    
    # get-global-option command
    get_global_opt_parser = subparsers.add_parser('get-global-option', help='Get global options')
    get_global_opt_parser.add_argument('--key', help='Show specific option key')
    get_global_opt_parser.set_defaults(func=cmd_get_global_option)
    
    # set-global-option command
    set_global_opt_parser = subparsers.add_parser('set-global-option', help='Set global options')
    set_global_opt_parser.add_argument('options', nargs='*', help='Options in KEY=VALUE format')
    set_global_opt_parser.set_defaults(func=cmd_set_global_option)
    
    # get-option command
    get_opt_parser = subparsers.add_parser('get-option', help='Get options for a task')
    get_opt_parser.add_argument('gid', help='Task GID')
    get_opt_parser.set_defaults(func=cmd_get_option)
    
    # set-option command
    set_opt_parser = subparsers.add_parser('set-option', help='Set options for a task')
    set_opt_parser.add_argument('gid', help='Task GID')
    set_opt_parser.add_argument('options', nargs='*', help='Options in KEY=VALUE format')
    set_opt_parser.set_defaults(func=cmd_set_option)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == '__main__':
    main()
