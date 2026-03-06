#!/usr/bin/env python3
"""
setup.py - One-time network environment probe for site-analyze.
Saves results to ~/.site-analyze/env.json for use by site-analyze.py.

Run once after installation:
    python3 scripts/setup.py
"""

import json
import os
import re
import socket
import subprocess
import sys
import time
import threading
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

ENV_DIR  = Path.home() / ".site-analyze"
ENV_FILE = ENV_DIR / "env.json"

DOH_CANDIDATES = {
    "Google":     "https://dns.google/resolve",
    "Cloudflare": "https://cloudflare-dns.com/dns-query",
    "Quad9":      "https://dns.quad9.net/dns-query",
    "AliDNS":     "https://dns.alidns.com/resolve",
    "DNSPod":     "https://doh.pub/dns-query",
    "360DNS":     "https://doh.360.cn/resolve",
    "AdGuard":    "https://dns.adguard-dns.com/dns-query",
    "OpenDNS":    "https://doh.opendns.com/dns-query",
}

WELL_KNOWN = {
    "8.8.8.8":   ("Google DNS",       53),
    "1.1.1.1":   ("Cloudflare DNS",   53),
    "223.5.5.5": ("AliDNS",           53),
    "114.114.114.114": ("114DNS",      53),
}

def http_get(url, timeout=4):
    try:
        req = Request(url, headers={"User-Agent": "site-analyze-setup/1.0",
                                    "accept": "application/dns-json"})
        with urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except Exception:
        return 0, ""

def probe_exit_ip():
    """Detect public exit IP via multiple services."""
    services = [
        "https://api.ipify.org",
        "https://ipv4.icanhazip.com",
        "https://checkip.amazonaws.com",
    ]
    for svc in services:
        status, body = http_get(svc, timeout=5)
        if status == 200 and body.strip():
            ip = body.strip()
            if re.match(r"^\d+\.\d+\.\d+\.\d+$", ip):
                return ip
    return None

def probe_exit_ip_info(ip):
    """Get ASN/geo for the exit IP."""
    if not ip:
        return {}
    status, body = http_get(f"https://ipinfo.io/{ip}/json", timeout=6)
    if status == 200 and body:
        try:
            d = json.loads(body)
            return {
                "ip":      d.get("ip", ip),
                "city":    d.get("city", "?"),
                "region":  d.get("region", "?"),
                "country": d.get("country", "?"),
                "org":     d.get("org", "?"),
                "loc":     d.get("loc", ""),
                "timezone":d.get("timezone", "?"),
            }
        except Exception:
            pass
    return {"ip": ip}

def probe_udp_dns():
    """Check if well-known UDP DNS servers are reachable."""
    results = {}
    for ip, (name, port) in WELL_KNOWN.items():
        try:
            t0 = time.time()
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(2)
            # Send a minimal DNS query for "." type NS
            query = b"\x00\x01\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x01"
            s.sendto(query, (ip, port))
            s.recv(512)
            s.close()
            rtt = round((time.time() - t0) * 1000, 1)
            results[ip] = {"name": name, "reachable": True, "rtt_ms": rtt}
        except Exception:
            results[ip] = {"name": name, "reachable": False, "rtt_ms": None}
    return results

def probe_doh_servers():
    """Concurrently probe all DoH candidates; return ordered working list."""
    results = {}
    lock = threading.Lock()

    def probe_one(name, base):
        url = f"{base}?name=example.com&type=A"
        t0 = time.time()
        try:
            req = Request(url, headers={"User-Agent": "site-analyze-setup/1.0",
                                        "accept": "application/dns-json"})
            with urlopen(req, timeout=3) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                data = json.loads(body)
                if data.get("Answer") or data.get("Status") == 0:
                    rtt = round((time.time() - t0) * 1000, 1)
                    with lock:
                        results[name] = {"url": base, "rtt_ms": rtt}
        except Exception:
            pass

    threads = [threading.Thread(target=probe_one, args=(n, b), daemon=True)
               for n, b in DOH_CANDIDATES.items()]
    for t in threads:
        t.start()
    deadline = time.time() + 4
    for t in threads:
        t.join(timeout=max(0, deadline - time.time()))

    order = list(DOH_CANDIDATES.keys())
    return sorted(results.items(), key=lambda x: order.index(x[0]) if x[0] in order else 99)

def probe_tcp_latency(host, port, tries=3):
    """TCP latency in ms."""
    lats = []
    for _ in range(tries):
        try:
            t0 = time.time()
            s = socket.create_connection((host, port), timeout=4)
            lats.append(round((time.time() - t0) * 1000, 1))
            s.close()
        except Exception:
            pass
    return lats

def probe_traceroute_available():
    for cmd in ("tcptraceroute", "traceroute"):
        try:
            subprocess.run([cmd, "--version"], capture_output=True, timeout=3)
            return cmd
        except Exception:
            pass
    return None

def probe_tools():
    """Check availability of CLI tools."""
    tools = {}
    for tool in ("curl", "openssl", "tcptraceroute", "traceroute", "dig", "nslookup"):
        try:
            subprocess.run(["which", tool], capture_output=True, check=True, timeout=3)
            tools[tool] = True
        except Exception:
            tools[tool] = False
    return tools

def run():
    ENV_DIR.mkdir(parents=True, exist_ok=True)

    print("🔍 site-analyze — Network Environment Setup")
    print("=" * 50)

    env = {"probed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

    # 1. Exit IP
    print("\n[1/5] Detecting exit IP...", end=" ", flush=True)
    exit_ip = probe_exit_ip()
    if exit_ip:
        info = probe_exit_ip_info(exit_ip)
        env["exit_ip"] = info
        print(f"{exit_ip}  ({info.get('city','?')}, {info.get('country','?')} | {info.get('org','?')})")
    else:
        env["exit_ip"] = None
        print("(failed)")

    # 2. UDP DNS reachability
    print("\n[2/5] Probing UDP DNS (port 53)...", flush=True)
    udp_results = probe_udp_dns()
    env["udp_dns"] = udp_results
    for ip, r in udp_results.items():
        status = f"✓ {r['rtt_ms']}ms" if r["reachable"] else "✗ blocked"
        print(f"  {ip:18s} ({r['name']:16s}) {status}")

    udp_blocked = all(not r["reachable"] for r in udp_results.values())
    env["udp_dns_blocked"] = udp_blocked
    if udp_blocked:
        print("  ⚠️  All UDP DNS blocked — DoH will be used exclusively")
    else:
        print("  ✓ UDP DNS available")

    # 3. DoH servers
    print("\n[3/5] Probing DoH servers (parallel, 4s timeout)...", flush=True)
    doh_working = probe_doh_servers()
    env["doh_servers"] = [{"name": n, "url": v["url"], "rtt_ms": v["rtt_ms"]}
                          for n, v in doh_working]
    if doh_working:
        for name, v in doh_working:
            print(f"  ✓ {name:12s}  {v['rtt_ms']}ms  {v['url']}")
    else:
        print("  ✗ No DoH servers reachable!")

    # 4. TCP latency to well-known hosts
    print("\n[4/5] TCP latency to reference hosts...", flush=True)
    latency_probes = [
        ("8.8.8.8",     443, "Google"),
        ("1.1.1.1",     443, "Cloudflare"),
        ("223.5.5.5",   443, "AliDNS"),
        ("223.6.6.6",   443, "AliDNS-2"),
    ]
    env["tcp_latency"] = {}
    for host, port, label in latency_probes:
        lats = probe_tcp_latency(host, port)
        if lats:
            avg = round(sum(lats) / len(lats), 1)
            env["tcp_latency"][host] = {"label": label, "rtt_ms": lats, "avg_ms": avg}
            print(f"  {host:18s} ({label:12s}) {lats} avg={avg}ms")
        else:
            env["tcp_latency"][host] = {"label": label, "rtt_ms": [], "avg_ms": None}
            print(f"  {host:18s} ({label:12s}) unreachable")

    # 5. CLI tools
    print("\n[5/5] Checking CLI tools...", flush=True)
    tools = probe_tools()
    env["tools"] = tools
    for tool, ok in tools.items():
        print(f"  {'✓' if ok else '✗'} {tool}")

    # Save
    ENV_FILE.write_text(json.dumps(env, indent=2, ensure_ascii=False))
    print(f"\n✅ Environment saved to {ENV_FILE}")
    print("\nSummary:")
    print(f"  Exit IP:       {env['exit_ip']['ip'] if env['exit_ip'] else 'unknown'}")
    print(f"  UDP DNS:       {'blocked' if udp_blocked else 'available'}")
    print(f"  DoH servers:   {len(doh_working)} available ({', '.join(n for n,_ in doh_working)})")
    traceroute = env["tools"].get("tcptraceroute") or env["tools"].get("traceroute")
    print(f"  Traceroute:    {'available' if traceroute else 'unavailable'}")
    print()

if __name__ == "__main__":
    run()
