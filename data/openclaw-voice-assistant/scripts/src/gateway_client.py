"""WebSocket client for OpenClaw gateway."""

import asyncio
import json
import logging
import uuid
from typing import AsyncGenerator

import websockets

from config import GATEWAY_URL, GATEWAY_TOKEN

log = logging.getLogger(__name__)


class GatewayClient:
    """Connects to an OpenClaw gateway and sends/receives chat messages."""

    def __init__(self):
        self.ws = None
        self._connected = False
        self._chat_queues: dict[str, asyncio.Queue] = {}
        self._response_queues: dict[str, asyncio.Queue] = {}
        self._event_task = None

    async def connect(self):
        """Establish WebSocket connection and authenticate."""
        log.info("Connecting to gateway at %s", GATEWAY_URL)
        self.ws = await websockets.connect(GATEWAY_URL, max_size=2**24)

        # Step 1: Receive connect.challenge
        raw = await self.ws.recv()
        challenge = json.loads(raw)
        if challenge.get("event") != "connect.challenge":
            raise ConnectionError(f"Expected connect.challenge, got: {challenge}")
        log.debug("Received challenge: %s", challenge["payload"].get("nonce"))

        # Step 2: Send connect request
        connect_id = str(uuid.uuid4())
        await self.ws.send(json.dumps({
            "type": "req",
            "id": connect_id,
            "method": "connect",
            "params": {
                "minProtocol": 3,
                "maxProtocol": 3,
                "client": {
                    "id": "node-host",
                    "version": "1.0.0",
                    "platform": "windows",
                    "mode": "node"
                },
                "role": "operator",
                "scopes": ["operator.write"],
                "caps": [],
                "auth": {
                    "token": GATEWAY_TOKEN
                }
            }
        }))

        # Step 3: Receive hello-ok
        raw = await self.ws.recv()
        hello = json.loads(raw)
        if not hello.get("ok"):
            error = hello.get("error", {})
            raise ConnectionError(
                f"Gateway auth failed: {error.get('code')} - {error.get('message')}"
            )

        server = hello.get("payload", {}).get("server", {})
        log.info("Connected to gateway v%s (conn: %s)",
                 server.get("version"), server.get("connId"))
        self._connected = True

        # Start the SINGLE background reader — all reads go through here
        self._event_task = asyncio.create_task(self._handle_events())

    async def disconnect(self):
        """Close the WebSocket connection."""
        self._connected = False
        if self._event_task:
            self._event_task.cancel()
        if self.ws:
            await self.ws.close()
        log.info("Disconnected from gateway")

    async def send_message(self, text: str) -> AsyncGenerator[str, None]:
        """Send a chat message and yield response text as it streams in."""
        if not self._connected:
            raise RuntimeError("Not connected to gateway")

        run_id = str(uuid.uuid4())
        req_id = str(uuid.uuid4())

        # Register queues BEFORE sending so we don't miss the response
        chat_queue: asyncio.Queue = asyncio.Queue()
        response_queue: asyncio.Queue = asyncio.Queue()
        self._chat_queues[run_id] = chat_queue
        self._response_queues[req_id] = response_queue

        try:
            # Send the request (write-only, no recv here)
            await self.ws.send(json.dumps({
                "type": "req",
                "id": req_id,
                "method": "chat.send",
                "params": {
                    "sessionKey": "main",
                    "message": text,
                    "idempotencyKey": run_id
                }
            }))

            # Wait for ack — routed here by _handle_events
            ack = await asyncio.wait_for(response_queue.get(), timeout=10.0)
            if not ack.get("ok"):
                error = ack.get("error", {})
                raise RuntimeError(f"chat.send failed: {error.get('message')}")

            # Stream chat events — also routed by _handle_events
            while True:
                try:
                    event = await asyncio.wait_for(chat_queue.get(), timeout=120.0)
                except asyncio.TimeoutError:
                    log.warning("Timed out waiting for chat response")
                    break

                state = event.get("state")
                if state == "delta":
                    content = event.get("message", {}).get("content", [])
                    if content and content[0].get("type") == "text":
                        yield content[0]["text"]
                elif state == "final":
                    content = event.get("message", {}).get("content", [])
                    if content and content[0].get("type") == "text":
                        yield content[0]["text"]
                    break
                elif state == "error":
                    raise RuntimeError(
                        f"Agent error: {event.get('errorMessage', 'unknown')}"
                    )
                elif state == "aborted":
                    break
        finally:
            self._chat_queues.pop(run_id, None)
            self._response_queues.pop(req_id, None)

    async def _handle_events(self):
        """Single background reader — routes ALL incoming frames to queues."""
        try:
            async for raw in self.ws:
                try:
                    frame = json.loads(raw)
                except json.JSONDecodeError:
                    continue

                frame_type = frame.get("type")

                if frame_type == "event":
                    event_name = frame.get("event")
                    payload = frame.get("payload", {})

                    if event_name == "chat":
                        run_id = payload.get("runId")
                        queue = self._chat_queues.get(run_id)
                        if queue:
                            await queue.put(payload)

                    elif event_name == "tick":
                        pass  # keepalive

                elif frame_type == "res":
                    req_id = frame.get("id")
                    queue = self._response_queues.get(req_id)
                    if queue:
                        await queue.put(frame)

        except websockets.ConnectionClosed:
            log.warning("Gateway connection closed")
            self._connected = False
        except asyncio.CancelledError:
            pass

    @property
    def connected(self) -> bool:
        return self._connected
