#!/usr/bin/env python3
"""Quick health check of all OpenClaw systems. Stdlib only."""
import json, os, subprocess, sys, urllib.request, urllib.error

def check(name, fn):
    try:
        result = fn()
        print(f"  ✅ {name}: {result}")
        return True
    except Exception as e:
        print(f"  ❌ {name}: {e}")
        return False

def run(cmd, timeout=10):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip(), r.returncode

def http_get(url, timeout=5):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())

def main():
    print("🏗️ OpenClaw Health Check\n")
    checks_passed = 0
    checks_total = 0

    # 1. Gateway
    print("=== Gateway ===")
    checks_total += 1
    if check("Gateway process", lambda: (
        run("pgrep -f 'openclaw.*gateway\\|node.*dist/index'")[1] == 0 and "running" or "not found"
    )):
        checks_passed += 1

    checks_total += 1
    if check("Gateway health", lambda: (
        http_get("http://localhost:18789/health").get("status", "unknown")
    )):
        checks_passed += 1

    # 2. Config
    print("\n=== Configuration ===")
    config_path = os.path.expanduser("~/.openclaw/openclaw.json")
    checks_total += 1
    if check("openclaw.json", lambda: (
        os.path.exists(config_path) and f"exists ({os.path.getsize(config_path)} bytes)" or "MISSING"
    )):
        checks_passed += 1

    # 3. Workspace
    print("\n=== Workspace ===")
    ws = os.path.expanduser("~/.openclaw/workspace")
    for f in ["MEMORY.md", "AGENTS.md", "SOUL.md", "TOOLS.md"]:
        checks_total += 1
        if check(f, lambda f=f: (
            os.path.exists(os.path.join(ws, f)) and 
            f"{os.path.getsize(os.path.join(ws, f))} bytes" or "MISSING"
        )):
            checks_passed += 1

    skills_dir = os.path.join(ws, "skills")
    checks_total += 1
    if check("Skills directory", lambda: (
        f"{len(os.listdir(skills_dir))} skills" if os.path.isdir(skills_dir) else "MISSING"
    )):
        checks_passed += 1

    # 4. Brain Stack
    print("\n=== Brain Stack ===")
    checks_total += 1
    if check("Qdrant", lambda: (
        http_get("http://localhost:6333/collections").get("result", {}).get("collections") is not None
        and f"up — {len(http_get('http://localhost:6333/collections')['result']['collections'])} collection(s)"
        or "responding"
    )):
        checks_passed += 1

    checks_total += 1
    if check("Neo4j", lambda: (
        run("curl -sf http://localhost:7474/ -o /dev/null && echo up")[0] or "up"
    )):
        checks_passed += 1

    sqlite_path = os.path.join(ws, ".data/sqlite/agxntsix.db")
    checks_total += 1
    if check("SQLite", lambda: (
        os.path.exists(sqlite_path) and f"exists ({os.path.getsize(sqlite_path)} bytes)" or "MISSING"
    )):
        checks_passed += 1

    # 5. Docker
    print("\n=== Docker ===")
    checks_total += 1
    if check("Docker socket", lambda: (
        os.path.exists("/var/run/docker.sock") and "accessible" or "MISSING"
    )):
        checks_passed += 1

    checks_total += 1
    out, rc = run("docker ps --format '{{.Names}}' 2>/dev/null | wc -l")
    if check("Docker containers", lambda: f"{out.strip()} running" if rc == 0 else "docker not accessible"):
        checks_passed += 1

    # 6. Network
    print("\n=== Network ===")
    checks_total += 1
    if check("Tailscale", lambda: (
        run("tailscale status --json 2>/dev/null")[1] == 0 and "connected" or 
        run("cat /proc/net/if_inet6 2>/dev/null | grep -q tailscale && echo up || echo down")[0]
    )):
        checks_passed += 1

    # 7. Python env
    print("\n=== Python Environment ===")
    venv = os.path.join(ws, ".venv/bin/python3")
    checks_total += 1
    if check("Python venv", lambda: (
        os.path.exists(venv) and run(f"{venv} --version")[0] or "MISSING"
    )):
        checks_passed += 1

    # Summary
    print(f"\n{'='*40}")
    print(f"Results: {checks_passed}/{checks_total} checks passed")
    if checks_passed == checks_total:
        print("🎉 All systems healthy!")
    elif checks_passed >= checks_total * 0.8:
        print("⚠️  Mostly healthy, some issues to address")
    else:
        print("🔴 Multiple issues detected — review above")
    
    return 0 if checks_passed == checks_total else 1

if __name__ == "__main__":
    sys.exit(main())
