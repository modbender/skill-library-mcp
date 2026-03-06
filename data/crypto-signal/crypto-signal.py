#!/usr/bin/env python3
"""CryptoSignal CLI — lightweight API client for OpenClaw agents."""
import os, sys, json, urllib.request, urllib.error

API_BASE = os.environ.get("CRYPTOSIGNAL_API_URL", "https://api.qtxh.top/v1")
API_KEY = os.environ.get("CRYPTOSIGNAL_API_KEY", "")

def request(path: str, params: dict = None) -> dict:
    if not API_KEY:
        print("Error: Set CRYPTOSIGNAL_API_KEY environment variable.")
        print("Get your free key at https://cryptosignal.pro")
        sys.exit(1)
    url = f"{API_BASE}{path}"
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
        if qs:
            url += f"?{qs}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {API_KEY}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            err = json.loads(body)
            print(f"Error ({e.code}): {err.get('detail', body)}")
        except:
            print(f"Error ({e.code}): {body}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def cmd_status():
    data = request("/status")
    print(json.dumps(data, indent=2))

def cmd_trending(hours=24):
    data = request("/trending", {"hours": hours})
    print(f"📊 Trending ({data['period']}) — {data['groups_analyzed']} groups, {data['messages_processed']} messages\n")
    for t in data.get("trending", []):
        sources = ", ".join(t["sources"][:3])
        print(f"  {t['rank']}. **{t['topic']}** ({t['mentions']} mentions) — {sources}")
        if t.get("summary"):
            summary = t["summary"][:150]
            print(f"     {summary}")
        print()

def cmd_signals(sig_type=None, hours=24, limit=20):
    params = {"hours": hours, "limit": limit}
    if sig_type:
        params["type"] = sig_type
    data = request("/signals", params)
    print(f"🚨 Signals ({data['plan']} plan)\n")
    for s in data.get("signals", []):
        severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(s["severity"], "⚪")
        tokens = ", ".join(s.get("related_tokens", []))
        print(f"  {severity_icon} [{s['type']}] {s['title']}")
        if tokens:
            print(f"     Tokens: {tokens}")
        print(f"     {s['timestamp']}")
        print()

def cmd_groups():
    data = request("/groups")
    print(f"📡 Monitored Groups ({data['plan']} plan)\n")
    for g in data.get("groups", []):
        print(f"  • {g['title']} ({g['link']}) — {g['message_count_24h']} msgs/24h")

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print("Usage: crypto-signal <command> [options]")
        print()
        print("Commands:")
        print("  status                    Service status")
        print("  trending [--hours N]      Trending topics (default 24h)")
        print("  signals [--type T] [--hours N] [--limit N]  Alpha signals")
        print("  groups                    List monitored groups")
        print()
        print("Signal types: whale_transfer, price_move, liquidation, regulatory, security, listing, airdrop, partnership")
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "status":
        cmd_status()
    elif cmd == "trending":
        hours = 24
        if "--hours" in sys.argv:
            hours = int(sys.argv[sys.argv.index("--hours") + 1])
        cmd_trending(hours)
    elif cmd == "signals":
        sig_type = None
        hours = 24
        limit = 20
        if "--type" in sys.argv:
            sig_type = sys.argv[sys.argv.index("--type") + 1]
        if "--hours" in sys.argv:
            hours = int(sys.argv[sys.argv.index("--hours") + 1])
        if "--limit" in sys.argv:
            limit = int(sys.argv[sys.argv.index("--limit") + 1])
        cmd_signals(sig_type, hours, limit)
    elif cmd == "groups":
        cmd_groups()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
