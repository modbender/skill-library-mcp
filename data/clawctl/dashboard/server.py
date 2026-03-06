#!/usr/bin/env python3
"""clawctl dashboard server — Token auth + SSE"""

import json
import os
import secrets
import time
from pathlib import Path

from flask import Flask, jsonify, request, Response, send_from_directory

from clawctl import db

app = Flask(__name__)

# Persistent token — saved between restarts
TOKEN_PATH = Path(os.path.expanduser("~/.openclaw/.clawctl-token"))


def load_or_create_token():
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    if TOKEN_PATH.exists():
        token = TOKEN_PATH.read_text().strip()
        if token:
            return token
    token = secrets.token_urlsafe(16)
    TOKEN_PATH.write_text(token)
    return token


TOKEN = load_or_create_token()

# ═══════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════


@app.before_request
def check_token():
    if request.path == "/" or request.path.endswith(".html"):
        return
    if request.path.startswith("/api"):
        if request.args.get("token") != TOKEN:
            return jsonify({"error": "unauthorized"}), 401


def row_to_dict(row):
    return dict(row) if row else None


# ═══════════════════════════════════════════
# STATIC FILES
# ═══════════════════════════════════════════


@app.route("/")
def index():
    return send_from_directory(Path(__file__).parent, "index.html")


# ═══════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════


@app.route("/api/board")
def board():
    with db.get_db() as conn:
        tasks, agents = db.get_board_api(conn)
    return jsonify(
        {
            "tasks": [row_to_dict(t) for t in tasks],
            "agents": [row_to_dict(a) for a in agents],
            "timestamp": int(time.time() * 1000),
        }
    )


@app.route("/api/task/<int:task_id>")
def task_detail(task_id):
    with db.get_db() as conn:
        task, messages = db.get_task_detail(conn, task_id)
    return jsonify(
        {
            "task": row_to_dict(task),
            "messages": [row_to_dict(m) for m in messages],
        }
    )


@app.route("/api/task/<int:task_id>/delete", methods=["POST"])
def delete_task(task_id):
    data = request.get_json() or {}
    agent = data.get("agent", "dashboard")
    with db.get_db() as conn:
        ok, err = db.cancel_task(conn, task_id, agent)
    if not ok:
        return jsonify({"success": False, "error": err}), 409
    return jsonify({"success": True})


@app.route("/api/task/<int:task_id>/complete", methods=["POST"])
def complete_task(task_id):
    data = request.get_json() or {}
    note = data.get("note", "")
    agent = data.get("agent", "dashboard")
    with db.get_db() as conn:
        db.complete_task(conn, task_id, agent, note, force=True)
    return jsonify({"success": True})


@app.route("/api/heartbeat")
def heartbeat():
    def stream():
        last_check = None
        while True:
            try:
                with db.get_db() as conn:
                    result = conn.execute(
                        "SELECT MAX(updated_at) as latest FROM tasks"
                    ).fetchone()
                latest = result["latest"] if result else None
                if latest != last_check:
                    last_check = latest
                    yield f"data: {json.dumps({'refresh': True, 'ts': int(time.time())})}\n\n"
                time.sleep(2)
            except GeneratorExit:
                break
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                time.sleep(5)

    return Response(
        stream(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ═══════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=3737)
    args = parser.parse_args()

    print(f"\n{'=' * 50}")
    print(f"  clawctl dashboard")
    print(f"{'=' * 50}")
    print(f"\n  Local URL:")
    print(f"  http://localhost:{args.port}/?token={TOKEN}")
    print(f"\n  For Tailscale/LAN access, use your IP:")
    print(f"  http://<your-ip>:{args.port}/?token={TOKEN}")
    print(f"\n  Token: {TOKEN}")
    print(f"\n{'=' * 50}\n")

    app.run(host="0.0.0.0", port=args.port, threaded=True)


if __name__ == "__main__":
    main()
