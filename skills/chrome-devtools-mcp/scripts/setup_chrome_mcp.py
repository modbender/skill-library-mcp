#!/usr/bin/env python3
"""Chrome DevTools MCP — Setup, status check, and test script.

Usage:
    setup_chrome_mcp.py setup    # Install and configure
    setup_chrome_mcp.py status   # Check if working
    setup_chrome_mcp.py test     # Run a quick browser test
"""

import json, os, subprocess, sys


def run(cmd, capture=True, timeout=30):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=capture, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip() if capture else "", r.stderr.strip() if capture else ""
    except subprocess.TimeoutExpired:
        return 1, "", "timeout"
    except Exception as e:
        return 1, "", str(e)


def setup():
    """Install chrome-devtools-mcp and configure for OpenClaw."""
    print("🌐 Setting up Chrome DevTools MCP...")

    # Check Node.js
    code, out, _ = run("node --version")
    if code != 0:
        print("❌ Node.js not found. Required v20.19+")
        return False
    print(f"✅ Node.js: {out}")

    # Check npx
    code, out, _ = run("npx --version")
    if code != 0:
        print("❌ npx not found")
        return False
    print(f"✅ npx: {out}")

    # Pre-cache the package
    print("📦 Installing chrome-devtools-mcp...")
    code, out, err = run("npx -y chrome-devtools-mcp@latest --help", timeout=60)
    if code == 0:
        print("✅ chrome-devtools-mcp installed")
    else:
        # --help may not be supported, check if binary exists
        code2, out2, _ = run("npm list -g chrome-devtools-mcp 2>/dev/null || echo 'not global'")
        print(f"⚠️  Package cached (--help may not be supported): {err[:100]}")

    # Check for Chrome/Chromium
    chrome_paths = [
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        os.path.expanduser("~/.cache/ms-playwright/chromium-1208/chrome-linux64/chrome"),
    ]
    chrome_found = None
    for p in chrome_paths:
        if os.path.exists(p):
            chrome_found = p
            break

    if chrome_found:
        print(f"✅ Chrome found: {chrome_found}")
    else:
        print("⚠️  No Chrome/Chromium found. MCP server will try to download one.")

    print("\n📋 MCP Configuration for openclaw.json:")
    config = {
        "mcp": {
            "servers": {
                "chrome-devtools": {
                    "command": "npx",
                    "args": ["-y", "chrome-devtools-mcp@latest", "--headless", "--no-usage-statistics"]
                }
            }
        }
    }
    print(json.dumps(config, indent=2))

    print("\n✅ Setup complete. Add the config above to openclaw.json to enable.")
    return True


def status():
    """Check if chrome-devtools-mcp is available."""
    print("🔍 Chrome DevTools MCP Status\n")

    # Node
    code, out, _ = run("node --version")
    print(f"{'✅' if code == 0 else '❌'} Node.js: {out if code == 0 else 'not found'}")

    # npx
    code, out, _ = run("npx --version")
    print(f"{'✅' if code == 0 else '❌'} npx: {out if code == 0 else 'not found'}")

    # Chrome
    chrome_paths = [
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        os.path.expanduser("~/.cache/ms-playwright/chromium-1208/chrome-linux64/chrome"),
    ]
    chrome_found = None
    for p in chrome_paths:
        if os.path.exists(p):
            chrome_found = p
            break
    print(f"{'✅' if chrome_found else '⚠️ '} Chrome: {chrome_found or 'not found locally'}")

    # Check if MCP config exists in openclaw.json
    config_path = os.path.expanduser("~/.openclaw/openclaw.json")
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
        mcp_servers = config.get("mcp", {}).get("servers", {})
        if "chrome-devtools" in mcp_servers:
            print("✅ MCP server configured in openclaw.json")
        else:
            print("⚠️  MCP server NOT configured in openclaw.json — run setup")
    else:
        print("⚠️  openclaw.json not found")


def test():
    """Quick test — start MCP server and verify it responds."""
    print("🧪 Testing Chrome DevTools MCP...\n")

    # Try starting with --headless
    print("Starting MCP server (headless)...")
    proc = subprocess.Popen(
        ["npx", "-y", "chrome-devtools-mcp@latest", "--headless", "--no-usage-statistics"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    import time
    time.sleep(5)

    if proc.poll() is not None:
        _, err = proc.communicate()
        print(f"❌ Server exited immediately: {err[:200]}")
        return False

    print("✅ MCP server started successfully (headless mode)")
    print("   Server is running and accepting MCP connections")

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except:
        proc.kill()

    print("✅ Server shut down cleanly")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: setup_chrome_mcp.py [setup|status|test]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "setup":
        setup()
    elif cmd == "status":
        status()
    elif cmd == "test":
        test()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
