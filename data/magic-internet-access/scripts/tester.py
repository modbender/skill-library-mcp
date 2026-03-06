#!/usr/bin/env python3
import json, socket, time, os, sys, concurrent.futures
from datetime import datetime

def test_tcp(server, port, timeout=5):
    try:
        start = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((server, port))
        latency = round((time.time() - start) * 1000)
        sock.close()
        if result == 0: return True, latency
        return False, -1
    except: return False, -1

def test_node(node):
    server = node.get("server", "")
    port = node.get("port", 0)
    if not server or not port:
        node["alive"] = False; node["latency"] = -1; node["speed_rating"] = "Dead"; return node
    alive, latency = test_tcp(server, port)
    node["alive"] = alive; node["latency"] = latency
    if not alive: node["speed_rating"] = "Dead"
    elif latency < 100: node["speed_rating"] = "Fast"
    elif latency < 300: node["speed_rating"] = "OK"
    elif latency < 800: node["speed_rating"] = "Slow"
    else: node["speed_rating"] = "Very Slow"
    return node

def main():
    workspace = os.environ.get("OPENCLAW_WORKSPACE", os.path.expanduser("~/.openclaw/workspace"))
    input_path = os.path.join(workspace, "nodes_raw.json")
    output_path = os.path.join(workspace, "nodes_tested.json")
    if not os.path.exists(input_path):
        print("No nodes_raw.json found. Run scraper.py first."); sys.exit(1)
    with open(input_path, 'r', encoding='utf-8') as f: data = json.load(f)
    nodes = data.get("nodes", [])
    if not nodes: print("No nodes."); sys.exit(1)
    max_test = int(os.environ.get("MAX_TEST_NODES", 50))
    test_nodes = nodes[:max_test]
    print(f"Testing {len(test_nodes)} of {len(nodes)} nodes...")
    tested = []; alive_count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(test_node, n): n for n in test_nodes}
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            n = future.result(); tested.append(n)
            if n['alive']: alive_count += 1
            print(f"  [{i+1}/{len(test_nodes)}] {n['server']}:{n['port']} -> {n['latency']}ms" if n['alive'] else f"  [{i+1}/{len(test_nodes)}] {n['server']}:{n['port']} -> dead")
    tested.sort(key=lambda x: (not x['alive'], x['latency'] if x['latency'] > 0 else 99999))
    print(f"Alive: {alive_count}, Dead: {len(tested) - alive_count}")
    result = {"tested_at": datetime.now().isoformat(), "total_tested": len(tested), "alive": alive_count, "dead": len(tested) - alive_count, "nodes": tested}
    with open(output_path, 'w', encoding='utf-8') as f: json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    main()
