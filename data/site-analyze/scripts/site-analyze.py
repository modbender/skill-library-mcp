#!/usr/bin/env python3
"""
site-analyze.py - Website Infrastructure & Datacenter Tracer
Usage: python3 site-analyze.py <domain>
       python3 site-analyze.py --setup        # re-run env probe
       python3 site-analyze.py --show-env     # print cached env

On first run, automatically calls setup.py to probe the local network
environment and caches results to ~/.site-analyze/env.json.
Subsequent runs load the cache instantly — no re-probing needed.
"""

import sys
import json
import subprocess
import re
import socket
import time
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

ENV_FILE = Path.home() / ".site-analyze" / "env.json"

# ─────────────────────────────────────────
# DoH candidates (fallback if env not cached)
# ─────────────────────────────────────────
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

COMMON_SUBDOMAINS = [
    "", "www", "m", "api", "mail", "smtp", "ftp",
    "admin", "blog", "cdn", "static", "img", "origin",
    "direct", "src", "upload", "manage", "css", "js", "dev", "staging",
]

KNOWN_CDN = {
    "13335":  "Cloudflare",  "209242": "Cloudflare",
    "20940":  "Akamai",      "54113":  "Fastly",
    "16509":  "AWS CloudFront", "14618": "AWS CloudFront",
    "8075":   "Microsoft Azure",
    "45102":  "Aliyun",      "37963":  "Aliyun",
    "45090":  "Tencent Cloud", "132203": "Tencent Cloud", "134238": "Tencent Cloud",
    "15169":  "Google Cloud CDN", "396982": "Google Cloud CDN",
    "714":    "Apple",       "19551":  "Incapsula",
    "60068":  "CDN77",       "60626":  "Limelight", "22822": "Limelight",
    "397273": "Render",
}

CF_DATACENTER = {
    "AMS": "Netherlands·Amsterdam", "SIN": "Singapore",
    "NRT": "Japan·Tokyo",           "KIX": "Japan·Osaka",
    "LAX": "US·Los Angeles",        "SJC": "US·San Jose",
    "ORD": "US·Chicago",            "EWR": "US·New York",
    "IAD": "US·Washington DC",      "ATL": "US·Atlanta",
    "MIA": "US·Miami",              "SEA": "US·Seattle",
    "DFW": "US·Dallas",             "DEN": "US·Denver",
    "LHR": "UK·London",             "CDG": "France·Paris",
    "FRA": "Germany·Frankfurt",     "HKG": "China·Hong Kong",
    "TPE": "China·Taipei",          "ICN": "South Korea·Seoul",
    "SYD": "Australia·Sydney",      "MEL": "Australia·Melbourne",
    "BOM": "India·Mumbai",          "GRU": "Brazil·São Paulo",
    "DXB": "UAE·Dubai",             "JNB": "South Africa·Johannesburg",
    "YYZ": "Canada·Toronto",        "YVR": "Canada·Vancouver",
    "MAD": "Spain·Madrid",          "MXP": "Italy·Milan",
    "ARN": "Sweden·Stockholm",      "WAW": "Poland·Warsaw",
    "BKK": "Thailand·Bangkok",      "KUL": "Malaysia·Kuala Lumpur",
    "CGK": "Indonesia·Jakarta",     "MNL": "Philippines·Manila",
}

# ─────────────────────────────────────────
# Core HTTP helper
# ─────────────────────────────────────────

def http_get(url, timeout=6):
    try:
        req = Request(url, headers={"User-Agent": "site-analyze/1.0",
                                    "accept": "application/dns-json"})
        with urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace"), dict(resp.headers)
    except HTTPError as e:
        return e.code, "", {}
    except Exception:
        return 0, "", {}


def separator(title=""):
    width = 62
    if title:
        pad = (width - len(title) - 2) // 2
        print(f"\n{'─'*pad} {title} {'─'*(width - pad - len(title) - 2)}")
    else:
        print("─" * width)


# ─────────────────────────────────────────
# Environment cache (setup + load)
# ─────────────────────────────────────────

def load_env():
    try:
        if ENV_FILE.exists():
            return json.loads(ENV_FILE.read_text())
    except Exception:
        pass
    return None


def ensure_env(force=False):
    """Return cached env dict, running setup.py on first use."""
    env = load_env()
    if env and not force:
        return env
    setup_script = Path(__file__).parent / "setup.py"
    if setup_script.exists():
        print("📡 First run — probing local network environment...")
        print("   (results cached at ~/.site-analyze/env.json for future runs)\n")
        try:
            subprocess.run([sys.executable, str(setup_script)], check=True)
        except Exception as e:
            print(f"  ⚠️  setup.py failed: {e} — falling back to live probe\n")
    else:
        print("  ⚠️  setup.py not found — using live DoH probe\n")
    return load_env()


def doh_servers_from_env(env):
    """Extract ordered [(name, url)] from cached env."""
    if env and env.get("doh_servers"):
        return [(s["name"], s["url"]) for s in env["doh_servers"]]
    return []


def live_probe_doh():
    """Concurrent DoH probe (used only when no env cache)."""
    import threading
    results, lock = {}, threading.Lock()

    def probe(name, base):
        url = f"{base}?name=example.com&type=A"
        try:
            req = Request(url, headers={"User-Agent": "site-analyze/1.0",
                                        "accept": "application/dns-json"})
            with urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read())
                if data.get("Answer") or data.get("Status") == 0:
                    with lock:
                        results[name] = base
        except Exception:
            pass

    threads = [threading.Thread(target=probe, args=(n, b), daemon=True)
               for n, b in DOH_CANDIDATES.items()]
    for t in threads:
        t.start()
    deadline = time.time() + 4
    for t in threads:
        t.join(timeout=max(0, deadline - time.time()))

    order = list(DOH_CANDIDATES.keys())
    return sorted(results.items(), key=lambda x: order.index(x[0]) if x[0] in order else 99)


# ─────────────────────────────────────────
# DNS helpers
# ─────────────────────────────────────────

IPV4_RE = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")

def is_ipv4(s):
    return bool(IPV4_RE.match(s.strip()))


def doh_query_all(domain, qtype, servers):
    """Query all working DoH servers; for A records returns only IPv4 addresses."""
    results = {}
    for name, base in servers:
        url = f"{base}?name={domain}&type={qtype}"
        status, body, _ = http_get(url, timeout=6)
        if status == 200 and body:
            try:
                answers = [a["data"] for a in json.loads(body).get("Answer", [])]
                if qtype == "A":
                    answers = [a for a in answers if is_ipv4(a)]
                results[name] = answers
            except Exception:
                results[name] = []
    return results


def doh_query_best(domain, qtype, servers):
    """Return answers from the first responding DoH server.
    For A records, follows CNAME chain and returns only IPv4 addresses."""
    for _, base in servers:
        url = f"{base}?name={domain}&type={qtype}"
        status, body, _ = http_get(url, timeout=6)
        if status == 200 and body:
            try:
                data = json.loads(body)
                answers = data.get("Answer", [])
                if qtype == "A":
                    # Collect only type=1 (A) records — skip CNAME (type=5)
                    ips = [a["data"] for a in answers if a.get("type") == 1 and is_ipv4(a["data"])]
                    if ips:
                        return ips
                    # If only CNAMEs returned, follow the chain
                    cnames = [a["data"].rstrip(".") for a in answers if a.get("type") == 5]
                    if cnames:
                        # Resolve the final CNAME target
                        return doh_query_best(cnames[-1], "A", servers)
                    return []
                else:
                    return [a["data"] for a in answers]
            except Exception:
                continue
    try:
        return list({r[4][0] for r in socket.getaddrinfo(domain, None)})
    except Exception:
        return []


def doh_resolve_ips(domain, servers):
    """Resolve domain to IPv4 list, following CNAME chain. Returns (ips, cname_chain)."""
    cname_chain = []
    current = domain
    for _ in range(10):  # max 10 hops
        for _, base in servers:
            url = f"{base}?name={current}&type=A"
            status, body, _ = http_get(url, timeout=6)
            if status == 200 and body:
                try:
                    data = json.loads(body)
                    answers = data.get("Answer", [])
                    ips = [a["data"] for a in answers if a.get("type") == 1 and is_ipv4(a["data"])]
                    if ips:
                        return ips, cname_chain
                    cnames = [a["data"].rstrip(".") for a in answers if a.get("type") == 5]
                    if cnames:
                        cname_chain.append(cnames[-1])
                        current = cnames[-1]
                        break
                    return [], cname_chain
                except Exception:
                    continue
        else:
            break
    return [], cname_chain


# ─────────────────────────────────────────
# Analysis helpers
# ─────────────────────────────────────────

def ip_info(ip):
    status, body, _ = http_get(f"https://ipinfo.io/{ip}/json", timeout=6)
    if status == 200 and body:
        try:
            d = json.loads(body)
            org = d.get("org", "")
            asn = org.split()[0].lstrip("AS") if org else ""
            return {
                "ip": ip, "city": d.get("city", "?"), "region": d.get("region", "?"),
                "country": d.get("country", "?"), "org": org, "asn": asn,
                "cdn": KNOWN_CDN.get(asn, ""), "anycast": d.get("anycast", False),
                "timezone": d.get("timezone", "?"), "loc": d.get("loc", ""),
            }
        except Exception:
            pass
    return {"ip": ip, "city": "?", "region": "?", "country": "?", "org": "?",
            "asn": "?", "cdn": "", "anycast": False, "timezone": "?", "loc": ""}


def tcp_latency(ip, port=80, tries=3):
    lats = []
    for _ in range(tries):
        try:
            t0 = time.time()
            s = socket.create_connection((ip, port), timeout=5)
            lats.append(round((time.time() - t0) * 1000, 2))
            s.close()
        except Exception:
            pass
    return lats


def curl_timing(domain):
    cmd = [
        "curl", "-s", "-o", "/dev/null", "--max-time", "12",
        "-w", "dns=%{time_namelookup}|tcp=%{time_connect}|tls=%{time_appconnect}"
              "|ttfb=%{time_starttransfer}|total=%{time_total}|ip=%{remote_ip}|code=%{http_code}",
        "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        f"https://{domain}",
    ]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=14).decode()
        return dict(item.split("=", 1) for item in out.split("|") if "=" in item)
    except Exception:
        return {}


def curl_headers(url):
    cmd = ["curl", "-sI", "--max-time", "10", "-A", "Mozilla/5.0", url]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=12).decode()
        headers = {}
        for line in out.splitlines():
            if ":" in line and not line.startswith("HTTP"):
                k, _, v = line.partition(":")
                headers[k.strip().lower()] = v.strip()
        status_lines = [l for l in out.splitlines() if l.startswith("HTTP/")]
        return (status_lines[-1] if status_lines else ""), headers
    except Exception:
        return "", {}


def ssl_info(domain):
    cmd = ["bash", "-c",
           f"echo | timeout 6 openssl s_client -connect {domain}:443 "
           f"-servername {domain} 2>/dev/null "
           f"| openssl x509 -noout -text 2>/dev/null "
           f"| grep -E '(Issuer:|Subject:|DNS:|Not After|Not Before)'"]
    try:
        return subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=10).decode().strip()
    except Exception:
        return ""


def traceroute_tcp(ip, port=443, max_hops=15):
    for cmd in (
        ["tcptraceroute", "-n", "-m", str(max_hops), "-w", "2", ip, str(port)],
        ["traceroute",    "-n", "-m", str(max_hops), "-w", "2", ip],
    ):
        try:
            return subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=40).decode().strip()
        except Exception:
            continue
    return "(traceroute unavailable)"


def crt_sh(domain):
    status, body, _ = http_get(f"https://crt.sh/?q=%.{domain}&output=json", timeout=10)
    if status == 200 and body:
        try:
            names = set()
            for cert in json.loads(body):
                for name in cert.get("name_value", "").split("\n"):
                    name = name.strip()
                    if domain in name and not name.startswith("*"):
                        names.add(name)
            return sorted(names)
        except Exception:
            pass
    return []


def hackertarget_hosts(domain):
    status, body, _ = http_get(f"https://api.hackertarget.com/hostsearch/?q={domain}", timeout=8)
    if status == 200 and body and "error" not in body.lower()[:50]:
        results = []
        for line in body.strip().splitlines():
            if "," in line:
                sub, ip = line.split(",", 1)
                results.append((sub.strip(), ip.strip()))
        return results
    return []


def parse_cf_ray(ray):
    m = re.search(r"-([A-Z]{2,4})$", ray or "")
    return m.group(1) if m else ""


# ─────────────────────────────────────────
# Main analysis
# ─────────────────────────────────────────

def main(domain):
    domain = re.sub(r"^https?://", "", domain).rstrip("/").split("/")[0]

    print(f"\n{'═'*62}")
    print(f"  🔍 Site Infrastructure Analysis: {domain}")
    print(f"{'═'*62}")

    # ── 0. Network environment (from cache or setup) ─────────
    separator("0. Network Environment")
    env = ensure_env()
    if env:
        exit_info = env.get("exit_ip") or {}
        print(f"  Exit IP:     {exit_info.get('ip','?')}  "
              f"({exit_info.get('city','?')}, {exit_info.get('country','?')} | {exit_info.get('org','?')})")
        udp_ok = not env.get("udp_dns_blocked", False)
        print(f"  UDP DNS:     {'available' if udp_ok else 'blocked — using DoH only'}")
        doh_servers = doh_servers_from_env(env)
        print(f"  DoH servers: {', '.join(n for n,_ in doh_servers) or 'none'}")
        tools = env.get("tools", {})
        print(f"  CLI tools:   {', '.join(t for t,ok in tools.items() if ok) or 'none'}")
        print(f"  Env cached:  {env.get('probed_at','?')}")
    else:
        print("  No env cache — running live DoH probe...")
        doh_servers = live_probe_doh()
        tools = {}
        if doh_servers:
            print(f"  Available: {', '.join(n for n,_ in doh_servers)}")
        else:
            print("  ⚠️  No DoH servers reachable — using system resolver")

    report = {"domain": domain, "ips": set(), "cdn": None, "cf_dc": None}

    # ── 1. DNS Resolution ────────────────────────────────────
    separator("1. DNS Resolution (multi-server DoH)")
    all_ips = set()
    a_results = doh_query_all(domain, "A", doh_servers)
    if a_results:
        for sname, ips in a_results.items():
            v4 = [ip for ip in ips if re.match(r"^\d+\.\d+\.\d+\.\d+$", ip)]
            print(f"  {sname:12s} [A]: {', '.join(v4) or '(none)'}")
            all_ips.update(v4)
    else:
        fallback = doh_query_best(domain, "A", [])
        all_ips.update(fallback)
        print(f"  System resolver [A]: {', '.join(fallback) or '(none)'}")

    for qtype in ("AAAA", "NS", "MX", "TXT", "SOA"):
        answers = doh_query_best(domain, qtype, doh_servers)
        if answers:
            print(f"  {'':12s} [{qtype}]: {' | '.join(answers[:4])}")

    report["ips"] = list(all_ips)

    # ── 2. IP Geolocation & CDN Detection ───────────────────
    separator("2. IP Geolocation & CDN Detection")
    ip_infos = {}
    for ip in sorted(all_ips):
        info = ip_info(ip)
        ip_infos[ip] = info
        tags = []
        if info["cdn"]:
            tags.append(f"🛡️ CDN={info['cdn']}")
        if info["anycast"]:
            tags.append("[anycast]")
        tag_str = "  " + "  ".join(tags) if tags else ""
        print(f"  {ip:20s}  {info['city']}, {info['region']}, {info['country']}"
              f"  |  {info['org']}{tag_str}")

    cdns = {i["cdn"] for i in ip_infos.values() if i["cdn"]}
    report["cdn"] = ", ".join(cdns) if cdns else None
    if report["cdn"]:
        print(f"\n  ⚠️  CDN detected: {report['cdn']} — real origin IP is hidden")

    # ── 3. Subdomain Enumeration ─────────────────────────────
    separator("3. Subdomain Enumeration")
    # found_subs: fqdn -> {"ips": [...], "cname": [...]}
    found_subs = {}

    def resolve_sub(fqdn):
        ips, cnames = doh_resolve_ips(fqdn, doh_servers)
        if ips:
            found_subs[fqdn] = {"ips": ips, "cname": cnames}

    for sub in COMMON_SUBDOMAINS:
        fqdn = f"{sub}.{domain}" if sub else domain
        resolve_sub(fqdn)
    for name in crt_sh(domain):
        if name not in found_subs:
            resolve_sub(name)
    for sub, raw_ip in hackertarget_hosts(domain):
        if sub not in found_subs:
            if is_ipv4(raw_ip):
                found_subs[sub] = {"ips": [raw_ip], "cname": []}
            else:
                resolve_sub(sub)

    non_cdn_found = []
    for fqdn, rec in sorted(found_subs.items()):
        ips = rec["ips"]
        cnames = rec["cname"]
        tags = []
        for ip in ips:
            info = ip_infos.get(ip) or ip_info(ip)
            ip_infos[ip] = info
            if info["cdn"]:
                tags.append(f"{ip} ({info['cdn']})")
            else:
                tags.append(f"⭐ {ip} (non-CDN!)")
                if (fqdn, ip) not in [(f, i) for f, i, _ in non_cdn_found]:
                    non_cdn_found.append((fqdn, ip, info))
        cname_str = f" → {' → '.join(cnames)}" if cnames else ""
        print(f"  {fqdn:38s} -> {', '.join(tags)}{cname_str}")

    if non_cdn_found:
        print("\n  🎯 Possible origin IPs (not behind CDN):")
        for fqdn, ip, info in non_cdn_found:
            print(f"     {ip:20s} {fqdn} — {info['city']}, {info['country']} | {info['org']}")

    # ── 4. TCP Latency ───────────────────────────────────────
    separator("4. TCP Latency")
    for ip in sorted(all_ips)[:4]:
        for port in (80, 443):
            lats = tcp_latency(ip, port, tries=3)
            if lats:
                avg = round(sum(lats) / len(lats), 2)
                flag = " ⚠️ anycast" if ip_infos.get(ip, {}).get("anycast") else ""
                print(f"  {ip}:{port:<5}  {lats} ms  (avg {avg}ms){flag}")
            else:
                print(f"  {ip}:{port:<5}  connection failed")

    # ── 5. HTTP/HTTPS Headers ────────────────────────────────
    separator("5. HTTP/HTTPS Response Headers")
    last_headers = {}
    for scheme in ("https", "http"):
        status_line, headers = curl_headers(f"{scheme}://{domain}")
        if status_line:
            print(f"\n  [{scheme.upper()}] {status_line}")
            for k in ["server", "x-powered-by", "cf-ray", "cf-cache-status",
                      "via", "x-cache", "x-cache-hits", "x-served-by",
                      "location", "x-generator", "proxy-agent",
                      "nel", "alt-svc", "x-backend", "x-host"]:
                if k in headers:
                    print(f"    {k}: {headers[k]}")
            last_headers = headers

    cf_ray = last_headers.get("cf-ray", "")
    if cf_ray:
        dc_code = parse_cf_ray(cf_ray)
        dc_name = CF_DATACENTER.get(dc_code, dc_code)
        report["cf_dc"] = dc_code
        print(f"\n  📍 Cloudflare Edge Node: {dc_code} = {dc_name}")

    # ── 6. HTTPS Timing ─────────────────────────────────────
    separator("6. HTTPS Timing Breakdown (curl)")
    timing = curl_timing(domain)
    if timing:
        dns_ms   = float(timing.get("dns",  0)) * 1000
        tcp_ms   = float(timing.get("tcp",  0)) * 1000
        tls_ms   = float(timing.get("tls",  0)) * 1000
        ttfb_ms  = float(timing.get("ttfb", 0)) * 1000
        total_ms = float(timing.get("total",0)) * 1000
        print(f"  DNS lookup:    {dns_ms:.1f} ms")
        print(f"  TCP connect:   {tcp_ms:.1f} ms")
        print(f"  TLS handshake: {tls_ms:.1f} ms  (÷2 ≈ one-way RTT to edge)")
        print(f"  TTFB:          {ttfb_ms:.1f} ms  (edge RTT + origin processing)")
        print(f"  Total:         {total_ms:.1f} ms")
        print(f"  HTTP code:     {timing.get('code','?')}")
        print(f"  Remote IP:     {timing.get('ip','?')}")
        if tls_ms > 0:
            print(f"\n  📐 Estimated RTT to edge: ~{tls_ms/2:.0f} ms")
    else:
        print("  (unavailable)")

    # ── 7. SSL Certificate ───────────────────────────────────
    separator("7. SSL Certificate")
    ssl = ssl_info(domain)
    if ssl:
        for line in ssl.splitlines():
            print(f"  {line.strip()}")
    else:
        print("  (unavailable)")

    # ── 8. Traceroute ────────────────────────────────────────
    separator("8. TCP Traceroute")
    if all_ips:
        target_ip = sorted(all_ips)[0]
        print(f"  Target: {target_ip}:443\n")
        for line in traceroute_tcp(target_ip, 443).splitlines():
            print(f"  {line}")
    else:
        print("  (no IPs available)")

    # ── 9. Summary ───────────────────────────────────────────
    separator("9. Summary")
    print(f"  Domain:       {domain}")
    print(f"  Resolved IPs: {', '.join(sorted(all_ips)) or 'unknown'}")
    print(f"  CDN:          {report['cdn'] or 'none detected'}")
    if report["cf_dc"]:
        print(f"  CF edge:      {report['cf_dc']} ({CF_DATACENTER.get(report['cf_dc'], report['cf_dc'])})")
    if non_cdn_found:
        print(f"\n  🎯 Likely origin server(s):")
        seen_ips = set()
        for fqdn, ip, info in non_cdn_found:
            if ip in seen_ips:
                continue
            seen_ips.add(ip)
            print(f"     {ip:18s} {info['city']}, {info['country']} | {info['org']}")
            if info["anycast"]:
                print(f"     {'':18s} ⚠️  Anycast — use TTFB to estimate real origin distance")
    elif report["cdn"]:
        print(f"\n  ⚠️  Origin IP hidden by {report['cdn']}")
        print(f"     Tip: check SecurityTrails/Shodan for historical IPs, or inspect mail headers")

    print(f"\n{'═'*62}\n")


# ─────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────

if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print("Usage: python3 site-analyze.py <domain>")
        print("       python3 site-analyze.py --setup       # re-run env probe")
        print("       python3 site-analyze.py --show-env    # print cached env")
        print("\nExamples:")
        print("  python3 site-analyze.py example.com")
        print("  python3 site-analyze.py https://example.com/path")
        sys.exit(0)

    if args[0] == "--setup":
        ensure_env(force=True)
        sys.exit(0)

    if args[0] == "--show-env":
        env = load_env()
        if env:
            print(json.dumps(env, indent=2, ensure_ascii=False))
        else:
            print("No env cached yet. Run: python3 site-analyze.py --setup")
        sys.exit(0)

    main(args[0])
