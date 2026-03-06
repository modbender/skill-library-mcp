#!/usr/bin/env python3
"""
Bitaxe Gamma Monitor - Fetch status from Bitaxe API
Usage: python3 bitaxe_status.py [ip_address] [--format {json,text}] [--set-ip IP]

IP resolution order:
1. Command line argument
2. Config file (~/.config/bitaxe-monitor/config.json)
3. BITAXE_IP environment variable
4. Prompt for IP (if none of the above)

Use --set-ip to save IP to config file
"""

import sys
import json
import urllib.request
import urllib.error
import argparse
import os


def get_config_dir() -> str:
    """Get the config directory path."""
    config_dir = os.path.expanduser("~/.config/bitaxe-monitor")
    os.makedirs(config_dir, exist_ok=True)
    return config_dir


def get_config_file() -> str:
    """Get the config file path."""
    return os.path.join(get_config_dir(), "config.json")


def load_config() -> dict:
    """Load config from file."""
    config_file = get_config_file()
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_config(config: dict) -> None:
    """Save config to file."""
    config_file = get_config_file()
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)


def get_saved_ip() -> str | None:
    """Get IP from config file or environment variable."""
    # Priority 1: Config file
    config = load_config()
    if 'bitaxe_ip' in config:
        return config['bitaxe_ip']
    
    # Priority 2: Environment variable (for backwards compatibility)
    return os.environ.get('BITAXE_IP')


def set_ip_in_config(ip: str) -> None:
    """Save IP to config file."""
    config = load_config()
    config['bitaxe_ip'] = ip
    save_config(config)
    print(f"📝 Saved Bitaxe IP to {get_config_file()}")
    print(f"📡 IP: {ip}")


def fetch_bitaxe_status(ip: str) -> dict:
    """Fetch system info from Bitaxe Gamma API."""
    url = f"http://{ip}/api/system/info"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.URLError as e:
        raise ConnectionError(f"Failed to connect to Bitaxe at {ip}: {e}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON response: {e}")


def format_text(data: dict) -> str:
    """Format status data as human-readable text."""
    lines = [
        "═" * 40,
        "   📊 BITAXE GAMMA STATUS",
        "═" * 40,
        "",
        f"⚡ Power:       {data.get('power', 'N/A'):.2f} W",
        f"🌡️  Temperature:  {data.get('temp', 'N/A'):.1f}°C (ASIC)",
        f"🌡️  VR Temp:      {data.get('vrTemp', 'N/A'):.1f}°C" if data.get('vrTemp') != -1 else "",
        f"💨 Fan Speed:   {data.get('fanspeed', 'N/A'):.1f}% ({data.get('fanrpm', 'N/A')} RPM)",
        f"",
        f"⛏️  Hashrate:     {data.get('hashRate', 'N/A'):.2f} GH/s",
        f"⛏️  Hashrate 1m:  {data.get('hashRate_1m', 'N/A'):.2f} GH/s",
        f"⛏️  Hashrate 10m: {data.get('hashRate_10m', 'N/A'):.2f} GH/s",
        f"",
        f"🎯 Best Diff:    {data.get('bestDiff', 'N/A'):,}",
        f"🎯 Best Session: {data.get('bestSessionDiff', 'N/A'):,}",
        f"",
        f"✅ Shares Accepted:  {data.get('sharesAccepted', 'N/A')}",
        f"❌ Shares Rejected:  {data.get('sharesRejected', 'N/A')}",
        f"",
        f"🌐 WiFi: {data.get('wifiStatus', 'N/A')} (RSSI: {data.get('wifiRSSI', 'N/A')} dBm)",
        f"🔗 Pool: {data.get('stratumURL', 'N/A')}:{data.get('stratumPort', 'N/A')}",
        f"🔄 Uptime: {data.get('uptimeSeconds', 0) // 3600}h {(data.get('uptimeSeconds', 0) % 3600) // 60}m",
        f"",
        f"📋 Version: {data.get('version', 'N/A')} | Board: {data.get('boardVersion', 'N/A')}",
        f"🔧 ASIC: {data.get('ASICModel', 'N/A')} @ {data.get('frequency', 'N/A')} MHz",
        "═" * 40,
    ]
    return "\n".join(line for line in lines if line)


def main():
    parser = argparse.ArgumentParser(
        description="Bitaxe Gamma Status Monitor",
        epilog="IP resolution: 1) Command argument 2) Config file 3) BITAXE_IP env var"
    )
    parser.add_argument("ip", nargs="?", help="Bitaxe IP address (optional if configured)")
    parser.add_argument("--format", choices=["json", "text"], default="text",
                        help="Output format (default: text)")
    parser.add_argument("--set-ip", metavar="IP",
                        help="Save IP to config file (~/.config/bitaxe-monitor/config.json)")
    args = parser.parse_args()

    # Handle --set-ip first
    if args.set_ip:
        set_ip_in_config(args.set_ip)
        return

    # Determine which IP to use (priority: arg > config file > env var)
    ip = args.ip
    if not ip:
        ip = get_saved_ip()
        if not ip:
            parser.error(
                "No IP provided. Either:\n"
                "  - Pass IP as argument: bitaxe_status.py <IP>\n"
                "  - Save IP to config: bitaxe_status.py --set-ip <IP>\n"
                "  - Set BITAXE_IP environment variable"
            )
        source = "config file" if load_config().get('bitaxe_ip') else "environment variable"
        print(f"📡 Using Bitaxe IP from {source}: {ip}\n")

    # Fetch and display status
    try:
        data = fetch_bitaxe_status(ip)
        if args.format == "json":
            print(json.dumps(data, indent=2))
        else:
            print(format_text(data))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
