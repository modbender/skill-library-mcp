from __future__ import annotations

import asyncio
import json
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from maylo_assistant import MayloAssistant
from maylo_assistant.core import MAX_RECORD_SEC, say

ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = Path(__file__).resolve().parent / "static"
INDEX_HTML = STATIC_DIR / "index.html"

app = FastAPI(title="Maylo Voice Assistant UI")


class Hub:
    def __init__(self):
        self.clients: List[WebSocket] = []
        self.state: Dict[str, Any] = {
            "status": "idle",
            "last_wake_ts": None,
            "last_wake_score": None,
            "last_transcript": None,
            "last_reply": None,
        }
        self._lock = threading.Lock()
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def set_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    def update(self, **kwargs):
        with self._lock:
            self.state.update(kwargs)

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self.state)

    async def broadcast(self, msg: Dict[str, Any]):
        dead = []
        for ws in list(self.clients):
            try:
                await ws.send_text(json.dumps(msg, ensure_ascii=False))
            except Exception:
                dead.append(ws)
        for ws in dead:
            try:
                self.clients.remove(ws)
            except ValueError:
                pass

    def push_state(self) -> None:
        """Thread-safe: schedule a state broadcast to all connected /ws clients."""
        if not self._loop:
            return

        data = {"type": "state", "data": self.snapshot()}

        def _schedule() -> None:
            asyncio.create_task(self.broadcast(data))

        try:
            self._loop.call_soon_threadsafe(_schedule)
        except Exception:
            pass


hub = Hub()
assistant = MayloAssistant()


def _assistant_state_hook(state: str, payload: dict):
    # called from audio threads
    if state == "idle":
        hub.update(status="idle")
    elif state == "listening":
        hub.update(status="listening")
    elif state == "processing":
        hub.update(status="processing")
    elif state == "speaking":
        hub.update(status="speaking")
    elif state == "wake":
        hub.update(
            last_wake_ts=payload.get("ts"),
            last_wake_score=payload.get("score"),
        )
    elif state == "transcript":
        hub.update(last_transcript=payload.get("text"))
    elif state == "reply":
        hub.update(last_reply=payload.get("text"))

    hub.push_state()


assistant.on_state = _assistant_state_hook


@app.get("/")
def index():
    return FileResponse(INDEX_HTML)


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    hub.clients.append(ws)
    try:
        # initial snapshot
        await ws.send_text(json.dumps({"type": "state", "data": hub.snapshot()}, ensure_ascii=False))

        while True:
            msg = await ws.receive_text()
            try:
                data = json.loads(msg)
            except Exception:
                data = {"type": "unknown"}

            if data.get("type") == "ptt":
                # (legacy) server-microphone push-to-talk
                def _run():
                    try:
                        assistant.run_once_ptt()
                    except Exception:
                        pass

                threading.Thread(target=_run, daemon=True).start()
                await ws.send_text(json.dumps({"type": "ack", "msg": "ptt_started"}))

            elif data.get("type") == "ping":
                await ws.send_text(json.dumps({"type": "pong", "ts": time.time()}))

            else:
                await ws.send_text(json.dumps({"type": "error", "msg": "unknown_message"}))

    except WebSocketDisconnect:
        pass
    finally:
        try:
            hub.clients.remove(ws)
        except ValueError:
            pass


@app.websocket("/ws/audio")
async def ws_audio(ws: WebSocket):
    """Binary audio stream endpoint.

    Protocol (per utterance):
      - client sends JSON text: {type:"start", sample_rate:16000, format:"pcm_s16le"}
      - client streams binary: little-endian int16 mono PCM frames
      - client sends JSON text: {type:"stop"} and closes (optional)

    We enforce MAX_RECORD_SEC from the core assistant (default 15s).
    """

    await ws.accept()

    started = False
    sample_rate = 16000
    buf = bytearray()

    # 15s guardrail (16k * 2 bytes * MAX_RECORD_SEC)
    max_bytes = int(16000 * 2 * float(MAX_RECORD_SEC))

    try:
        while True:
            packet = await ws.receive()

            if packet.get("text") is not None:
                try:
                    data = json.loads(packet["text"])
                except Exception:
                    data = {}

                if data.get("type") == "start":
                    started = True
                    sample_rate = int(data.get("sample_rate") or 16000)
                    await ws.send_text(json.dumps({"type": "ack", "msg": "started"}))

                elif data.get("type") == "stop":
                    break

                else:
                    await ws.send_text(json.dumps({"type": "error", "msg": "unknown_control"}))

            elif packet.get("bytes") is not None:
                if not started:
                    # ignore unexpected binary before start
                    continue

                chunk = packet["bytes"]
                if chunk:
                    buf.extend(chunk)

                if len(buf) >= max_bytes:
                    # auto cut
                    break

            else:
                # ignore
                pass

    except WebSocketDisconnect:
        pass
    finally:
        if buf:
            # run pipeline in a worker thread
            pcm16 = np.frombuffer(bytes(buf), dtype=np.int16)

            def _run():
                try:
                    assistant._emit("listening")
                    assistant._emit("speaking")
                    # mirror local UX (optional)
                    say("Dinliyorum")
                    assistant.run_once_from_pcm16(pcm16, sample_rate=sample_rate, source="web")
                except Exception:
                    try:
                        assistant._emit("idle")
                    except Exception:
                        pass

            threading.Thread(target=_run, daemon=True).start()

        try:
            await ws.close()
        except Exception:
            pass


@app.on_event("startup")
async def startup():
    hub.set_loop(asyncio.get_running_loop())

    # Start wake-word listener in background thread (legacy behavior).
    # Set MAYLO_WEB_WAKE=0 to disable.
    import os

    if (str(os.getenv("MAYLO_WEB_WAKE", "1")).strip() not in {"0", "false", "False"}):
        def _loop():
            assistant.listen_forever(mode="full")

        threading.Thread(target=_loop, daemon=True).start()


# Run with:
#   uvicorn webapp.server:app --host 0.0.0.0 --port 8000
