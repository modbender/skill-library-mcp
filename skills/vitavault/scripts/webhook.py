#!/usr/bin/env python3
"""VitaVault webhook receiver.

Receives health snapshots via HTTP POST, stores timestamped JSON in ~/vitavault/data/.
Auth is optional via VITAVAULT_SYNC_TOKEN env var.
"""

import argparse, json, os, re, shutil
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from socketserver import ThreadingMixIn

DATA_DIR = Path.home() / "vitavault" / "data"
LATEST = DATA_DIR / "latest.json"


def save_snapshot(payload: dict) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    date = payload.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    name = f"{date}_{ts}.json"
    dest = DATA_DIR / name
    with open(dest, "w") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    if LATEST.exists() or LATEST.is_symlink():
        LATEST.unlink()
    try:
        LATEST.symlink_to(dest.name)
    except OSError:
        shutil.copy2(dest, LATEST)
    return dest


class Handler(BaseHTTPRequestHandler):
    server_version = "VitaVaultWebhook/1.1"

    def do_POST(self):
        token = getattr(self.server, "sync_token", "")
        if token:
            auth = self.headers.get("Authorization", "")
            if auth != f"Bearer {token}":
                self._respond(401, {"success": False, "error": "unauthorized"})
                return

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._respond(400, {"success": False, "error": "bad-length"})
            return

        try:
            payload = json.loads(self.rfile.read(length).decode())
        except Exception:
            self._respond(400, {"success": False, "error": "invalid-json"})
            return

        if not isinstance(payload, dict):
            self._respond(400, {"success": False, "error": "must-be-object"})
            return

        dest = save_snapshot(payload)
        m = payload.get("metrics", {})
        print(f"✅ Saved: {dest.name} | steps={m.get('steps','n/a')} sleep={m.get('sleepHours','n/a')}")
        self._respond(200, {"success": True, "saved": str(dest)})

    def do_GET(self):
        if self.path.rstrip("/").endswith("/health"):
            self._respond(200, {"ok": True})
        else:
            self._respond(405, {"error": "method-not-allowed"})

    def log_message(self, *a):
        pass

    def _respond(self, status, body):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class ThreadedServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--port", type=int, default=8787)
    args = p.parse_args()

    token = os.environ.get("VITAVAULT_SYNC_TOKEN", "").strip()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    srv = ThreadedServer((args.host, args.port), Handler)
    srv.sync_token = token

    auth_status = "AUTH ENABLED" if token else "NO AUTH (open)"
    print(f"VitaVault webhook on http://{args.host}:{args.port} [{auth_status}]")
    print(f"Data dir: {DATA_DIR}")

    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()


if __name__ == "__main__":
    main()
