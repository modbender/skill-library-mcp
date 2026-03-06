#!/usr/bin/env python3
"""
Snapmaker 2.0 API CLI
Provides safe control of Snapmaker 2.0 3D printers
"""

import argparse
import json
import os
import socket
import sys
import time
from pathlib import Path
import requests
from typing import Optional, Dict, Any, List, Tuple

def _find_workspace_root():
    """Walk up from script location to find workspace root (parent of 'skills/')."""
    env = os.environ.get("SNAPMAKER_WORKSPACE")
    if env:
        return Path(env)
    
    # Prefer CWD if it looks like a workspace (handles symlinks correctly)
    cwd = Path.cwd()
    if (cwd / "skills").is_dir():
        return cwd

    d = Path(__file__).resolve().parent
    for _ in range(6):
        if (d / "skills").is_dir() and d != d.parent:
            return d
        d = d.parent
    return Path.cwd()


def _skill_root() -> Path:
    """Find the skill folder containing SKILL.md."""
    cwd = Path.cwd()
    if (cwd / "SKILL.md").exists():
        return cwd

    d = Path(__file__).resolve().parent
    for _ in range(5):
        if (d / "SKILL.md").exists():
            return d
        if d == d.parent:
            break
        d = d.parent
    return Path(__file__).resolve().parents[1]


def _default_config_path() -> Path:
    """Resolve config from workspace only.

    Priority:
      1) <workspace>/snapmaker/config.json
      2) <skill>/config.json (fallback)
    """
    ws_cfg = _find_workspace_root() / "snapmaker" / "config.json"
    if ws_cfg.exists():
        return ws_cfg

    skill_cfg = _skill_root() / "config.json"
    if skill_cfg.exists():
        return skill_cfg

    return ws_cfg


class SnapmakerAPI:
    def __init__(self, config_path: str = None):
        cfg_path = Path(config_path).expanduser() if config_path else _default_config_path()

        if not cfg_path.exists():
            raise SystemExit(
                "Missing config.json. Create one in workspace/snapmaker/ (start from config.json.example)."
            )

        with open(cfg_path, 'r') as f:
            config = json.load(f)
        
        self.ip = config['ip']
        self.token = config['token']
        self.port = config.get('port', 8080)
        self.base_url = f"http://{self.ip}:{self.port}/api/v1"
        self._connected = False
    
    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make API request with token"""
        # Auto-connect on first request (except connect itself)
        if not self._connected and endpoint != 'connect':
            try:
                self.connect()
            except Exception:
                # If connect fails, still try the request (might be already connected)
                pass
        
        url = f"{self.base_url}/{endpoint}"
        # Note: Snapmaker firmware API requires token as query parameter.
        # The device does not support Authorization headers.
        # This is a LAN-only API (no internet exposure).
        params = kwargs.get('params', {})
        params['token'] = self.token
        kwargs['params'] = params
        
        try:
            response = requests.request(method, url, timeout=10, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    def connect(self) -> Dict[str, Any]:
        """Establish connection to printer"""
        response = self._request('POST', 'connect')
        self._connected = True
        return response.json()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current printer status"""
        response = self._request('GET', 'status')
        return response.json()
    
    def is_printing(self) -> bool:
        """Check if printer is currently printing"""
        status = self.get_status()
        return status.get('status') in ['RUNNING', 'PAUSED']
    
    # Allowed file extensions for 3D printing
    ALLOWED_EXTENSIONS = {'.gcode', '.nc', '.cnc', '.stl', '.snap3dp', '.snapcnc', '.snaplaser'}

    def send_file(self, file_path: str, print_type: str = '3dp') -> Dict[str, Any]:
        """Send a 3D printing file to the printer (but don't start printing).

        Only allows known 3D printing file types. File must be under the
        workspace directory or /tmp.
        """
        p = Path(file_path).expanduser().resolve()

        if not p.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Validate file extension
        if p.suffix.lower() not in self.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"File type '{p.suffix}' not allowed. "
                f"Supported: {', '.join(sorted(self.ALLOWED_EXTENSIONS))}"
            )

        # Sandbox: only allow files from workspace or /tmp
        allowed_roots = [
            _find_workspace_root().resolve(),
            Path("/tmp").resolve(),
            Path(os.environ.get("TMPDIR", "/tmp")).resolve(),
        ]
        if not any(p == root or str(p).startswith(str(root) + "/") for root in allowed_roots):
            raise ValueError(
                f"File '{file_path}' is outside allowed directories. "
                f"Only files under workspace or /tmp can be sent."
            )

        # Safety check: don't interfere with active print
        if self.is_printing():
            raise RuntimeError("Printer is currently printing. Cannot send file.")

        with open(p, 'rb') as f:
            files = {'file': f}
            params = {'type': print_type}
            response = self._request('POST', 'prepare_print', params=params, files=files)
            return response.json()
    
    def start_print(self) -> Dict[str, Any]:
        """Start printing the prepared file"""
        # Safety check
        if self.is_printing():
            raise RuntimeError("Printer is already printing!")
        
        response = self._request('POST', 'start_print')
        return response.json()
    
    def pause_print(self) -> Dict[str, Any]:
        """Pause current print job"""
        if not self.is_printing():
            raise RuntimeError("No active print job to pause")
        
        response = self._request('POST', 'pause')
        return response.json()
    
    def resume_print(self) -> Dict[str, Any]:
        """Resume paused print job"""
        status = self.get_status()
        if status.get('status') != 'PAUSED':
            raise RuntimeError("Print is not paused")
        
        response = self._request('POST', 'resume')
        return response.json()
    
    def stop_print(self) -> Dict[str, Any]:
        """Stop/cancel current print job"""
        if not self.is_printing():
            raise RuntimeError("No active print job to stop")
        
        response = self._request('POST', 'stop')
        return response.json()
    
    def get_print_file(self) -> bytes:
        """Get the last uploaded file"""
        response = self._request('GET', 'print_file')
        return response.content


def format_time(seconds: int) -> str:
    """Format seconds into human-readable time"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def format_status(status: Dict[str, Any]) -> str:
    """Format status dict into readable output"""
    lines = []
    lines.append(f"Status: {status.get('status', 'UNKNOWN')}")
    
    if status.get('printStatus'):
        lines.append(f"Print Status: {status['printStatus']}")
    
    if status.get('fileName'):
        lines.append(f"File: {status['fileName']}")
    
    if status.get('progress') is not None:
        progress = status['progress'] * 100
        lines.append(f"Progress: {progress:.1f}%")
        
        if status.get('currentLine') and status.get('totalLines'):
            lines.append(f"Lines: {status['currentLine']:,} / {status['totalLines']:,}")
    
    if status.get('elapsedTime'):
        lines.append(f"Elapsed: {format_time(status['elapsedTime'])}")
    
    if status.get('remainingTime'):
        lines.append(f"Remaining: {format_time(status['remainingTime'])}")
    
    # Temperatures
    if status.get('nozzleTemperature1') is not None:
        temp = status['nozzleTemperature1']
        target = status.get('nozzleTargetTemperature1', 0)
        lines.append(f"Nozzle 1: {temp}°C / {target}°C")
    
    if status.get('heatedBedTemperature') is not None:
        temp = status['heatedBedTemperature']
        target = status.get('heatedBedTargetTemperature', 0)
        lines.append(f"Bed: {temp}°C / {target}°C")
    
    # Position
    if status.get('x') is not None:
        lines.append(f"Position: X={status['x']:.2f} Y={status['y']:.2f} Z={status['z']:.2f}")
    
    # Warnings
    if status.get('isFilamentOut'):
        lines.append("⚠️  FILAMENT OUT!")
    
    if status.get('isEnclosureDoorOpen'):
        lines.append("⚠️  Enclosure door open")
    
    return '\n'.join(lines)


def cmd_status(api: SnapmakerAPI, args):
    """Handle status command"""
    status = api.get_status()
    
    if args.json:
        print(json.dumps(status, indent=2))
    else:
        print(format_status(status))


def cmd_jobs(api: SnapmakerAPI, args):
    """Handle jobs command"""
    status = api.get_status()
    
    if args.json:
        print(json.dumps(status, indent=2))
    else:
        if status.get('printStatus') and status.get('fileName'):
            print(format_status(status))
        else:
            print("No active print job")


def cmd_send(api: SnapmakerAPI, args):
    """Handle send command"""
    file_path = args.file

    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    # Check if printer is busy (no override)
    if api.is_printing():
        print("Error: Printer is currently printing. Cannot send file.", file=sys.stderr)
        sys.exit(1)

    print(f"Sending file: {file_path}")
    try:
        result = api.send_file(file_path)
        print("✓ File sent successfully")

        if args.start:
            print("\nThis will start printing immediately!")
            response = input("Continue? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("Aborted")
                sys.exit(0)

            api.start_print()
            print("✓ Print started")
        else:
            print("File prepared. Use 'snapmaker.py start' to begin printing.")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_pause(api: SnapmakerAPI, args):
    """Handle pause command"""
    try:
        api.pause_print()
        print("✓ Print paused")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_resume(api: SnapmakerAPI, args):
    """Handle resume command"""
    try:
        api.resume_print()
        print("✓ Print resumed")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_stop(api: SnapmakerAPI, args):
    """Handle stop command"""
    try:
        api.stop_print()
        print("✓ Print stopped")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_watch(api: SnapmakerAPI, args):
    """Watch print progress"""
    print("Watching print progress (Ctrl+C to stop)...\n")
    
    try:
        while True:
            status = api.get_status()
            
            # Clear screen (ANSI escape code)
            print("\033[2J\033[H", end='')
            
            print(format_status(status))
            print(f"\nLast updated: {time.strftime('%H:%M:%S')}")
            
            # Check for completion or errors
            if status.get('printStatus') == 'Idle' and status.get('progress', 0) >= 0.99:
                print("\n🎉 Print completed!")
                break
            
            if status.get('isFilamentOut'):
                print("\n⚠️  Filament out detected!")
            
            time.sleep(args.interval)
    
    except KeyboardInterrupt:
        print("\n\nStopped watching")


def discover_printers(timeout: float = 3.0, retries: int = 3,
                      target: str = None) -> List[Dict[str, str]]:
    """Discover Snapmaker printers via UDP broadcast on port 20054.

    Sends the magic 'discover' packet and parses replies like:
      Snapmaker@192.168.0.32|model:Snapmaker 2 Model A350|status:RUNNING

    Args:
        timeout: seconds to wait for each attempt
        retries: number of broadcast attempts
        target: optional IP to probe directly (unicast) instead of broadcast

    Returns:
        list of dicts with keys: ip, model, status
    """
    DISCOVER_PORT = 20054
    found: Dict[str, Dict[str, str]] = {}  # keyed by IP to dedupe

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(timeout)

    try:
        for _ in range(retries):
            if target:
                sock.sendto(b'discover', (target, DISCOVER_PORT))
            else:
                sock.sendto(b'discover', ('255.255.255.255', DISCOVER_PORT))

            # Collect all replies until timeout
            while True:
                try:
                    data, addr = sock.recvfrom(1024)
                    reply = data.decode('utf-8', errors='replace').strip("'\"")
                    # Parse: Snapmaker@IP|model:...|status:...
                    parts = reply.split('|')
                    info: Dict[str, str] = {}
                    if '@' in parts[0]:
                        info['ip'] = parts[0].split('@', 1)[1]
                    else:
                        info['ip'] = addr[0]
                    for part in parts[1:]:
                        if ':' in part:
                            key, val = part.split(':', 1)
                            info[key.strip().lower()] = val.strip()
                    found[info['ip']] = info
                except socket.timeout:
                    break

            if found:
                break  # got results, stop retrying
    finally:
        sock.close()

    return list(found.values())


def cmd_discover(api_unused, args):
    """Discover Snapmaker printers on the network.

    Uses UDP broadcast (port 20054). No authentication required.
    Note: broadcast only works on the same subnet as the printer.
    Use --target IP to probe a specific address across subnets.
    """
    target = getattr(args, 'target', None)
    timeout = getattr(args, 'timeout', 3.0)
    retries = getattr(args, 'retries', 3)

    if target:
        print(f"Probing {target}:{20054} (UDP discover)...")
    else:
        print("Broadcasting UDP discover on port 20054...")
        print("(Only works on the same subnet as the printer)\n")

    printers = discover_printers(timeout=timeout, retries=retries, target=target)

    if not printers:
        # If no UDP reply and we have a config, try HTTP probe as fallback
        config_path = getattr(args, 'config', None)
        if config_path is None:
            config_path = str(_find_workspace_root() / "snapmaker" / "config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            ip = config.get('ip', '')
            port = config.get('port', 8080)
            probe_ip = target or ip
        if probe_ip:
                print(f"No UDP reply. Trying HTTP probe on {probe_ip}:{port}...")
                try:
                    r = requests.get(
                        f"http://{probe_ip}:{port}/api/v1/status",
                        params={'token': config.get('token', '')},
                        timeout=5,
                    )
                    if r.ok:
                        status = r.json()
                        printers = [{
                            'ip': probe_ip,
                            'model': 'Snapmaker 2.0 (HTTP)',
                            'status': status.get('status', 'UNKNOWN'),
                        }]
                except Exception:
                    pass

    if not printers:
        print("No Snapmaker printers found.")
        print("\nTips:")
        print("  • Make sure you're on the same subnet as the printer")
        print("  • Use --target IP to probe a known address directly")
        print("  • Check that the printer is powered on and connected to WiFi")
        sys.exit(1)

    if args.json:
        print(json.dumps(printers, indent=2))
    else:
        for p in printers:
            print(f"  📍 {p.get('ip', '?')}")
            if p.get('model'):
                print(f"     Model:  {p['model']}")
            if p.get('status'):
                print(f"     Status: {p['status']}")
            print()

    return printers


def main():
    parser = argparse.ArgumentParser(
        description='Snapmaker 2.0 API Control',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status              # Get current printer status
  %(prog)s watch               # Watch print progress
  %(prog)s send file.gcode     # Send file (don't start)
  %(prog)s send file.gcode --start  # Send and start (confirms interactively)
  %(prog)s pause               # Pause print
  %(prog)s resume              # Resume print
  %(prog)s stop                # Stop/cancel print
        """
    )
    
    parser.add_argument('--config', help='Path to config.json (default: workspace/snapmaker/config.json)')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    subparsers.required = True
    
    # Discover command
    discover_parser = subparsers.add_parser('discover', help='Find Snapmaker printers on the network')
    discover_parser.add_argument('--target', help='Probe a specific IP instead of broadcasting')
    discover_parser.add_argument('--timeout', type=float, default=3.0, help='Timeout per attempt (default: 3s)')
    discover_parser.add_argument('--retries', type=int, default=3, help='Number of attempts (default: 3)')
    discover_parser.add_argument('--json', action='store_true', help='Output as JSON')
    discover_parser.set_defaults(func=cmd_discover)

    # Status command
    status_parser = subparsers.add_parser('status', help='Get printer status')
    status_parser.add_argument('--json', action='store_true', help='Output as JSON')
    status_parser.set_defaults(func=cmd_status)
    
    # Jobs command
    jobs_parser = subparsers.add_parser('jobs', help='List/manage print jobs')
    jobs_parser.add_argument('--json', action='store_true', help='Output as JSON')
    jobs_parser.set_defaults(func=cmd_jobs)
    
    # Send command
    send_parser = subparsers.add_parser('send', help='Send file to printer')
    send_parser.add_argument('file', help='Path to 3D printing file (.gcode, .nc, .cnc, .stl)')
    send_parser.add_argument('--start', action='store_true', help='Start printing immediately (interactive confirmation)')
    send_parser.set_defaults(func=cmd_send)

    # Pause command
    pause_parser = subparsers.add_parser('pause', help='Pause current print')
    pause_parser.set_defaults(func=cmd_pause)

    # Resume command
    resume_parser = subparsers.add_parser('resume', help='Resume paused print')
    resume_parser.set_defaults(func=cmd_resume)

    # Stop command
    stop_parser = subparsers.add_parser('stop', help='Stop/cancel current print')
    stop_parser.set_defaults(func=cmd_stop)
    
    # Watch command
    watch_parser = subparsers.add_parser('watch', help='Watch print progress')
    watch_parser.add_argument('--interval', type=int, default=5, help='Update interval in seconds (default: 5)')
    watch_parser.set_defaults(func=cmd_watch)
    
    args = parser.parse_args()
    
    # Initialize API (discover doesn't require it)
    api = None
    if args.command != 'discover':
        try:
            api = SnapmakerAPI(args.config)
        except Exception as e:
            print(f"Error loading config: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Execute command
    args.func(api, args)


if __name__ == '__main__':
    main()
