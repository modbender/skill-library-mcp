#!/usr/bin/env python3
"""
Embedding Server — keeps the model warm for instant embeddings.
Listens on a Unix socket for embed requests.

Usage:
    python3 embed_server.py              # Start server
    python3 embed_server.py --status     # Check if running
    python3 embed_server.py --stop       # Stop server

Protocol (over Unix socket):
    Send: JSON line {"action": "embed", "text": "..."}\n
    Recv: JSON line {"embedding": [...], "ms": 5}\n

    Send: {"action": "embed_batch", "texts": ["...", "..."]}\n
    Recv: {"embeddings": [[...], [...]], "ms": 12}\n

    Send: {"action": "ping"}\n
    Recv: {"status": "ok", "model": "all-MiniLM-L6-v2", "uptime": 123}\n
"""
import json
import os
import sys
import time
import signal
import socket
import threading
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("embed_server")

SOCKET_PATH = "/tmp/openclaw-embed.sock"
PID_FILE = "/tmp/openclaw-embed.pid"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Global model reference
model = None
start_time = None


def load_model():
    global model, start_time
    log.info(f"Loading model {MODEL_NAME}...")
    t0 = time.time()
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(MODEL_NAME)
    elapsed = (time.time() - t0) * 1000
    start_time = time.time()
    log.info(f"Model loaded in {elapsed:.0f}ms")


def embed(text: str) -> list:
    vec = model.encode(text, normalize_embeddings=True)
    return vec.tolist()


def embed_batch(texts: list) -> list:
    vecs = model.encode(texts, normalize_embeddings=True, batch_size=32)
    return vecs.tolist()


def handle_client(conn):
    try:
        data = b""
        while True:
            chunk = conn.recv(65536)
            if not chunk:
                break
            data += chunk
            if b"\n" in data:
                break

        if not data:
            return

        request = json.loads(data.decode().strip())
        action = request.get("action", "")

        if action == "ping":
            uptime = round(time.time() - start_time) if start_time else 0
            response = {"status": "ok", "model": MODEL_NAME, "uptime": uptime}

        elif action == "embed":
            t0 = time.time()
            vec = embed(request["text"])
            ms = round((time.time() - t0) * 1000)
            response = {"embedding": vec, "ms": ms}

        elif action == "embed_batch":
            t0 = time.time()
            vecs = embed_batch(request["texts"])
            ms = round((time.time() - t0) * 1000)
            response = {"embeddings": vecs, "ms": ms}

        else:
            response = {"error": f"Unknown action: {action}"}

        conn.sendall((json.dumps(response) + "\n").encode())
    except Exception as e:
        try:
            conn.sendall((json.dumps({"error": str(e)}) + "\n").encode())
        except:
            pass
    finally:
        conn.close()


def run_server():
    # Clean up old socket
    if os.path.exists(SOCKET_PATH):
        os.unlink(SOCKET_PATH)

    load_model()

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    server.listen(5)
    os.chmod(SOCKET_PATH, 0o666)

    # Write PID file
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

    def shutdown(sig, frame):
        log.info("Shutting down...")
        server.close()
        if os.path.exists(SOCKET_PATH):
            os.unlink(SOCKET_PATH)
        if os.path.exists(PID_FILE):
            os.unlink(PID_FILE)
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    log.info(f"Embedding server listening on {SOCKET_PATH}")

    while True:
        try:
            conn, _ = server.accept()
            threading.Thread(target=handle_client, args=(conn,), daemon=True).start()
        except OSError:
            break


def check_status():
    if not os.path.exists(SOCKET_PATH):
        print("Embedding server: NOT RUNNING")
        return False
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(SOCKET_PATH)
        s.sendall(b'{"action":"ping"}\n')
        data = s.recv(4096)
        s.close()
        resp = json.loads(data.decode().strip())
        print(f"Embedding server: RUNNING (uptime={resp.get('uptime', '?')}s, model={resp.get('model', '?')})")
        return True
    except:
        print("Embedding server: STALE SOCKET (not responding)")
        return False


def stop_server():
    if os.path.exists(PID_FILE):
        with open(PID_FILE) as f:
            pid = int(f.read().strip())
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"Sent SIGTERM to pid {pid}")
        except ProcessLookupError:
            print(f"Process {pid} not found")
        os.unlink(PID_FILE)
    if os.path.exists(SOCKET_PATH):
        os.unlink(SOCKET_PATH)


if __name__ == "__main__":
    if "--status" in sys.argv:
        check_status()
    elif "--stop" in sys.argv:
        stop_server()
    else:
        run_server()
