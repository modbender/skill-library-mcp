#!/usr/bin/env python3
"""
Tasmota Device Discovery
Scans network for Tasmota devices by:
1. HTTP-based detection (port 80)
2. Checking for Tasmota JSON API response
3. Looking for Tasmota user-agent in responses
"""

import socket
import subprocess
import concurrent.futures
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import json
import time

# Network configuration
SUBNET = "192.168.1.0/24"
TIMEOUT = 2  # seconds

def get_local_ip():
    """Get local IP to determine subnet"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "192.168.1.148"

def get_subnet_ips():
    """Generate list of IPs in subnet"""
    local_ip = get_local_ip()
    parts = local_ip.split('.')
    base = f"{parts[0]}.{parts[1]}.{parts[2]}"
    return [f"{base}.{i}" for i in range(1, 255)]

def check_http(ip):
    """Check if IP has HTTP service that might be Tasmota"""
    try:
        # Try basic HTTP request first
        req = Request(f"http://{ip}/", headers={'User-Agent': 'Tasmota-Scanner'})
        start = time.time()
        with urlopen(req, timeout=TIMEOUT) as response:
            elapsed = time.time() - start
            data = response.read(5000).decode('utf-8', errors='ignore')
            headers = dict(response.headers)

            # Check for Tasmota indicators
            is_tasmota = False
            evidence = []

            # Check for Tasmota-specific headers/content
            if 'tasmota' in headers.get('Server', '').lower():
                is_tasmota = True
                evidence.append(f"Server header: {headers.get('Server')}")

            # Check content for Tasmota patterns
            if 'tasmota' in data.lower():
                is_tasmota = True
                evidence.append("Tasmota keyword in content")

            # Check for known Tasmota page titles/elements
            if 'Status' in data and 'tasmota' in data.lower():
                is_tasmota = True
                evidence.append("Tasmota status page detected")

            # Try Tasmota JSON API
            try:
                req_api = Request(f"http://{ip}/cm?cmnd=status%200")
                with urlopen(req_api, timeout=1) as api_response:
                    api_data = api_response.read(1000).decode('utf-8', errors='ignore')
                    if 'tasmota' in api_data.lower() or 'StatusSNS' in api_data or 'StatusNET' in api_data:
                        is_tasmota = True
                        evidence.append("Tasmota JSON API response")
            except:
                pass

            if is_tasmota:
                try:
                    title = data.split('<title>')[1].split('</title>')[0].strip()
                except:
                    title = "N/A"

                return {
                    'ip': ip,
                    'port': 80,
                    'title': title,
                    'server': headers.get('Server', 'Unknown'),
                    'evidence': evidence,
                    'elapsed': elapsed
                }
            return None

    except (URLError, HTTPError, socket.timeout, ConnectionResetError):
        return None
    except Exception as e:
        return None

def ping_scan(ip):
    """Quick ping check to see if host is up"""
    try:
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '1', ip],
            capture_output=True,
            timeout=2
        )
        return result.returncode == 0
    except:
        return False

def discover_tasmota():
    """Main discovery function"""
    print(f"🔍 Scanning network for Tasmota devices...")
    print(f"📍 Local subnet: {SUBNET}")

    ips = get_subnet_ips()
    print(f"📡 Checking {len(ips)} IP addresses...")

    tasmota_devices = []

    # First, quick ping sweep to find live hosts
    print("\n1️⃣  Ping sweep (finding live hosts)...")
    live_hosts = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        future_to_ip = {executor.submit(ping_scan, ip): ip for ip in ips}
        for future in concurrent.futures.as_completed(future_to_ip):
            ip = future_to_ip[future]
            if future.result():
                live_hosts.append(ip)
                print(f"  ✅ {ip}")

    print(f"\n📍 Found {len(live_hosts)} live hosts")
    print(f"\n2️⃣  Scanning for Tasmota (HTTP) on live hosts...")

    # Then check HTTP on live hosts
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_ip = {executor.submit(check_http, ip): ip for ip in live_hosts}
        for future in concurrent.futures.as_completed(future_to_ip):
            result = future.result()
            if result:
                tasmota_devices.append(result)

    return tasmota_devices

if __name__ == "__main__":
    devices = discover_tasmota()

    print(f"\n{'='*60}")
    if devices:
        print(f"✅ Found {len(devices)} Tasmota device(s):\n")
        for i, device in enumerate(devices, 1):
            print(f"🔌 Device {i}:")
            print(f"   IP: {device['ip']}:{device['port']}")
            print(f"   Title: {device['title']}")
            print(f"   Server: {device['server']}")
            print(f"   Evidence:")
            for ev in device['evidence']:
                print(f"     • {ev}")
            print(f"   Response time: {device['elapsed']:.3f}s")
            print()
    else:
        print("❌ No Tasmota devices found")
    print(f"{'='*60}")