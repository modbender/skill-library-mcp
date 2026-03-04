#!/usr/bin/env python3
import json, base64, os, sys, argparse
from datetime import datetime

def load_nodes(workspace):
    tested = os.path.join(workspace, "nodes_tested.json")
    raw = os.path.join(workspace, "nodes_raw.json")
    if os.path.exists(tested):
        with open(tested, 'r', encoding='utf-8') as f: data = json.load(f)
        return [n for n in data.get("nodes", []) if n.get("alive", True)]
    elif os.path.exists(raw):
        with open(raw, 'r', encoding='utf-8') as f: data = json.load(f)
        return data.get("nodes", [])
    else: print("No nodes found."); sys.exit(1)

def format_text(nodes, top=5):
    lines = ["Scientific Internet Access", datetime.now().strftime('%Y-%m-%d %H:%M'), ""]
    for i, n in enumerate(nodes[:top]):
        flag = n.get("flag", ""); name = n.get("name", n.get("country", "Unknown"))
        if len(name) > 30: name = name[:27] + "..."
        lat = f"{n['latency']}ms" if isinstance(n.get('latency'), int) and n['latency'] > 0 else "N/A"
        lines.append(f"{i+1}. {flag} {name} | {n.get('protocol','')} | {lat} | {n.get('speed_rating','')}")
        lines.append(f"   {n.get('raw','')}")
        lines.append("")
    lines.append("Free nodes are unstable, refresh regularly")
    lines.append("Powered by Scientific Internet Access | shadowrocket.ai")
    return "\n".join(lines)

def format_base64(nodes, top=50):
    lines = [n.get("raw", "") for n in nodes[:top] if n.get("raw")]
    return base64.b64encode("\n".join(lines).encode('utf-8')).decode('utf-8')

def format_clash(nodes, top=20):
    proxies = []; names = []
    for n in nodes[:top]:
        name = n.get("name", f"{n['server']}:{n['port']}")
        if name in names: name = f"{name}_{len(names)}"
        names.append(name)
        p = n.get("protocol", "")
        if p == "vmess": proxies.append({"name": name, "type": "vmess", "server": n["server"], "port": n["port"], "uuid": n.get("uuid",""), "alterId": n.get("aid",0), "cipher": "auto"})
        elif p == "trojan": proxies.append({"name": name, "type": "trojan", "server": n["server"], "port": n["port"], "password": n.get("password","")})
        elif p == "ss": proxies.append({"name": name, "type": "ss", "server": n["server"], "port": n["port"], "cipher": n.get("method","aes-256-gcm"), "password": n.get("password","")})
    config = {"port": 7890, "socks-port": 7891, "allow-lan": False, "mode": "rule", "proxies": proxies, "proxy-groups": [{"name": "Scientific", "type": "select", "proxies": names + ["DIRECT"]}], "rules": ["GEOIP,CN,DIRECT", "MATCH,Scientific"]}
    return json.dumps(config, ensure_ascii=False, indent=2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", "-f", default="text", choices=["text","clash","v2ray","base64"])
    parser.add_argument("--top", "-t", type=int, default=5)
    args = parser.parse_args()
    workspace = os.environ.get("OPENCLAW_WORKSPACE", os.path.expanduser("~/.openclaw/workspace"))
    nodes = load_nodes(workspace)
    formatters = {"text": format_text, "clash": format_clash, "base64": format_base64, "v2ray": lambda n,t: json.dumps([x.get("raw","") for x in n[:t]])}
    print(formatters[args.format](nodes, args.top))

if __name__ == "__main__":
    main()
