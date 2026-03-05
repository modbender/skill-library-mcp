#!/usr/bin/env python3
"""Wrapper for tentactl. Pass tool name and JSON args as argv."""

import subprocess, json, sys, os, time, select

tool = sys.argv[1]
args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
binary = os.environ.get("KRAKEN_MCP_BINARY") or "tentactl"
if not os.path.isabs(binary):
    import shutil
    if not shutil.which(binary):
        cargo_bin = os.path.expanduser("~/.cargo/bin/tentactl")
        if os.path.isfile(cargo_bin) and os.access(cargo_bin, os.X_OK):
            binary = cargo_bin

init = json.dumps({"jsonrpc":"2.0","id":0,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"openclaw","version":"0.1"}}})
notif = json.dumps({"jsonrpc":"2.0","method":"notifications/initialized"})
call = json.dumps({"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":tool,"arguments":args}})

proc = subprocess.Popen([binary], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
proc.stdin.write(init + "\n" + notif + "\n" + call + "\n")
proc.stdin.flush()

deadline = time.time() + 10
while time.time() < deadline:
    ready, _, _ = select.select([proc.stdout], [], [], 1.0)
    if ready:
        line = proc.stdout.readline()
        if not line:
            break
        try:
            r = json.loads(line.strip())
            if r.get("id") == 1:
                if "error" in r:
                    print("Error:", r["error"].get("message", str(r["error"])))
                    proc.terminate()
                    sys.exit(1)
                content = r.get("result", {}).get("content", [])
                is_error = r.get("result", {}).get("isError", False)
                for c in content:
                    print(c.get("text", ""))
                proc.terminate()
                sys.exit(1 if is_error else 0)
        except json.JSONDecodeError:
            continue

proc.terminate()
print("Error: no response from server")
sys.exit(1)
