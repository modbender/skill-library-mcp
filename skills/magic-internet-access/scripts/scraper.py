#!/usr/bin/env python3
import json, base64, re, urllib.request, urllib.error, os, sys, time
from datetime import datetime

SOURCES = [
    {"name": "freefq/free", "urls": ["https://raw.githubusercontent.com/freefq/free/master/v2"]},
    {"name": "Pawdroid/Free-servers", "urls": ["https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub"]},
    {"name": "aiboboxx/v2rayfree", "urls": ["https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2"]},
    {"name": "mfuu/v2ray", "urls": ["https://raw.githubusercontent.com/mfuu/v2ray/master/v2ray"]},
    {"name": "ermaozi/get_subscribe", "urls": ["https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/v2ray.txt"]},
    {"name": "peasoft/NoMoreWalls", "urls": ["https://raw.githubusercontent.com/peasoft/NoMoreWalls/master/list_raw.txt"]},
    {"name": "mahdibland/V2RayAggregator", "urls": ["https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge_base64.txt"]},
    {"name": "barry-far/V2ray-Configs", "urls": ["https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub1.txt", "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub2.txt"]},
    {"name": "Leon406/SubCrawler", "urls": ["https://raw.githubusercontent.com/Leon406/SubCrawler/main/sub/share/v2"]},
    {"name": "vveg26/chromego_merge", "urls": ["https://raw.githubusercontent.com/vveg26/chromego_merge/main/sub/merged_proxies_new"]},
]

COUNTRY_MAP = {
    "JP": "\U0001f1ef\U0001f1f5", "Japan": "\U0001f1ef\U0001f1f5", "Tokyo": "\U0001f1ef\U0001f1f5",
    "SG": "\U0001f1f8\U0001f1ec", "Singapore": "\U0001f1f8\U0001f1ec",
    "US": "\U0001f1fa\U0001f1f8", "USA": "\U0001f1fa\U0001f1f8", "Los Angeles": "\U0001f1fa\U0001f1f8",
    "HK": "\U0001f1ed\U0001f1f0", "Hong Kong": "\U0001f1ed\U0001f1f0",
    "TW": "\U0001f1f9\U0001f1fc", "Taiwan": "\U0001f1f9\U0001f1fc",
    "KR": "\U0001f1f0\U0001f1f7", "Korea": "\U0001f1f0\U0001f1f7",
    "DE": "\U0001f1e9\U0001f1ea", "Germany": "\U0001f1e9\U0001f1ea", "Frankfurt": "\U0001f1e9\U0001f1ea",
    "UK": "\U0001f1ec\U0001f1e7", "England": "\U0001f1ec\U0001f1e7",
    "CA": "\U0001f1e8\U0001f1e6", "Canada": "\U0001f1e8\U0001f1e6",
}

def detect_country(s):
    if not s: return "\U0001f30d", "Unknown"
    for k, v in COUNTRY_MAP.items():
        if k.lower() in s.lower(): return v, k
    return "\U0001f30d", "Unknown"

def decode_base64(data):
    data = data.strip()
    m = len(data) % 4
    if m: data += '=' * (4 - m)
    try: return base64.b64decode(data).decode('utf-8', errors='ignore')
    except:
        try: return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        except: return ""

def parse_vmess(uri):
    try:
        raw = uri.replace("vmess://", "")
        decoded = decode_base64(raw)
        if not decoded: return None
        c = json.loads(decoded)
        name = c.get("ps", c.get("remarks", ""))
        flag, country = detect_country(name)
        return {"protocol": "vmess", "name": name, "server": c.get("add", ""), "port": int(c.get("port", 0)), "uuid": c.get("id", ""), "aid": int(c.get("aid", 0)), "network": c.get("net", "tcp"), "tls": c.get("tls", ""), "country": country, "flag": flag, "raw": uri.strip()}
    except: return None

def parse_vless(uri):
    try:
        raw = uri.replace("vless://", "")
        m = re.match(r'^([^@]+)@([^:]+):(\d+)(?:\?([^#]*))?(?:#(.*))?$', raw)
        if not m: return None
        uuid, server, port, params, name = m.groups()
        name = urllib.request.unquote(name or "")
        flag, country = detect_country(name)
        return {"protocol": "vless", "name": name, "server": server, "port": int(port), "uuid": uuid, "params": params or "", "country": country, "flag": flag, "raw": uri.strip()}
    except: return None

def parse_trojan(uri):
    try:
        raw = uri.replace("trojan://", "")
        m = re.match(r'^([^@]+)@([^:]+):(\d+)(?:\?([^#]*))?(?:#(.*))?$', raw)
        if not m: return None
        pw, server, port, params, name = m.groups()
        name = urllib.request.unquote(name or "")
        flag, country = detect_country(name)
        return {"protocol": "trojan", "name": name, "server": server, "port": int(port), "password": pw, "params": params or "", "country": country, "flag": flag, "raw": uri.strip()}
    except: return None

def parse_ss(uri):
    try:
        raw = uri.replace("ss://", "")
        parts = raw.split("#", 1)
        name = urllib.request.unquote(parts[1]) if len(parts) > 1 else ""
        decoded = decode_base64(parts[0])
        if not decoded: decoded = parts[0]
        m = re.match(r'^([^:]+):([^@]+)@([^:]+):(\d+)$', decoded)
        if not m: return None
        method, pw, server, port = m.groups()
        flag, country = detect_country(name)
        return {"protocol": "ss", "name": name, "server": server, "port": int(port), "method": method, "password": pw, "country": country, "flag": flag, "raw": uri.strip()}
    except: return None

def parse_node(line):
    line = line.strip()
    if line.startswith("vmess://"): return parse_vmess(line)
    elif line.startswith("vless://"): return parse_vless(line)
    elif line.startswith("trojan://"): return parse_trojan(line)
    elif line.startswith("ss://"): return parse_ss(line)
    return None

def fetch_source(source):
    nodes = []
    for url in source["urls"]:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode('utf-8', errors='ignore').strip()
            decoded = decode_base64(content)
            if decoded and any(p in decoded for p in ["vmess://", "vless://", "trojan://", "ss://"]): content = decoded
            for line in content.split('\n'):
                line = line.strip()
                if not line: continue
                node = parse_node(line)
                if node and node.get("server"):
                    node["source"] = source["name"]
                    nodes.append(node)
            print(f"  OK {source['name']} -> {len(nodes)} nodes")
        except Exception as e:
            print(f"  FAIL {source['name']}: {e}")
    return nodes

def deduplicate(nodes):
    seen = set()
    unique = []
    for n in nodes:
        key = f"{n['server']}:{n['port']}:{n['protocol']}"
        if key not in seen:
            seen.add(key)
            unique.append(n)
    return unique

def main():
    workspace = os.environ.get("OPENCLAW_WORKSPACE", os.path.expanduser("~/.openclaw/workspace"))
    output_path = os.path.join(workspace, "nodes_raw.json")
    print(f"Scraping {len(SOURCES)} sources...")
    all_nodes = []
    for source in SOURCES:
        all_nodes.extend(fetch_source(source))
    unique = deduplicate(all_nodes)
    protocols = {}
    for n in unique: protocols[n["protocol"]] = protocols.get(n["protocol"], 0) + 1
    print(f"Total: {len(all_nodes)}, Unique: {len(unique)}, Protocols: {protocols}")
    result = {"scraped_at": datetime.now().isoformat(), "total": len(unique), "protocols": protocols, "nodes": unique}
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(unique)} nodes to {output_path}")

if __name__ == "__main__":
    main()
