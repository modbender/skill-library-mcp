"""Browser Bridge — abstract interface for skill ↔ user's browser.

Current implementation: CDP (Chrome DevTools Protocol) via httpx + websockets.
Connects directly to the user's running browser — no Playwright, no agent-browser.
Future: IrisGo runtime replaces this with native browser API.
"""

import asyncio
import json
import time

import httpx


class BrowserBridge:
    """Connect to the user's running browser via CDP."""

    def __init__(self, cdp_port: int = 9222):
        self.cdp_port = cdp_port
        self.base_url = f"http://127.0.0.1:{cdp_port}"
        self._ws_connections: dict[str, object] = {}
        self._input_lock = asyncio.Lock()

    def verify_connection(self) -> bool:
        """Check if the user's browser is reachable."""
        try:
            resp = httpx.get(f"{self.base_url}/json/version", timeout=3)
            return resp.status_code == 200
        except Exception:
            return False

    def get_browser_info(self) -> dict:
        resp = httpx.get(f"{self.base_url}/json/version", timeout=3)
        return resp.json()

    def list_tabs(self) -> list[dict]:
        resp = httpx.get(f"{self.base_url}/json/list", timeout=5)
        return [t for t in resp.json() if t.get("type") == "page"]

    def new_tab(self, url: str = "") -> dict:
        """Open a new tab, return tab info with webSocketDebuggerUrl."""
        target = f"{self.base_url}/json/new?{url}" if url else f"{self.base_url}/json/new"
        # Try PUT first (Comet/newer Chrome), fall back to GET
        resp = httpx.put(target, timeout=10)
        if resp.status_code == 405:
            resp = httpx.get(target, timeout=10)
        return resp.json()

    def close_tab(self, tab_id: str) -> bool:
        try:
            resp = httpx.get(f"{self.base_url}/json/close/{tab_id}", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False

    async def connect_tab(self, ws_url: str):
        """Create a persistent WebSocket connection to a tab."""
        import websockets
        ws = await websockets.connect(ws_url, max_size=10 * 1024 * 1024)
        self._ws_connections[ws_url] = {"ws": ws, "msg_id": 1}
        return ws

    async def _send(self, ws_url: str, method: str, params: dict | None = None) -> dict:
        """Send CDP command on an existing connection."""
        conn = self._ws_connections.get(ws_url)
        if not conn:
            raise RuntimeError("Not connected. Call connect_tab first.")
        ws = conn["ws"]
        msg_id = conn["msg_id"]
        conn["msg_id"] += 1

        cmd = {"id": msg_id, "method": method}
        if params:
            cmd["params"] = params
        await ws.send(json.dumps(cmd))

        while True:
            resp = json.loads(await asyncio.wait_for(ws.recv(), timeout=30))
            if resp.get("id") == msg_id:
                return resp.get("result", {})

    async def eval_js(self, ws_url: str, expression: str) -> str:
        """Evaluate JavaScript and return string result."""
        result = await self._send(ws_url, "Runtime.evaluate",
                                  {"expression": expression, "returnByValue": True, "awaitPromise": True})
        val = result.get("result", {}).get("value", "")
        return str(val) if val is not None else ""

    async def insert_text(self, ws_url: str, text: str):
        """Type text using CDP Input.insertText (works with React/Vue)."""
        await self._send(ws_url, "Input.insertText", {"text": text})

    async def press_enter(self, ws_url: str):
        """Press Enter key via CDP."""
        await self._send(ws_url, "Input.dispatchKeyEvent", {
            "type": "keyDown", "key": "Enter", "code": "Enter",
            "windowsVirtualKeyCode": 13, "nativeVirtualKeyCode": 13,
        })
        await self._send(ws_url, "Input.dispatchKeyEvent", {
            "type": "keyUp", "key": "Enter", "code": "Enter",
            "windowsVirtualKeyCode": 13, "nativeVirtualKeyCode": 13,
        })

    async def close_ws(self, ws_url: str):
        """Close WebSocket connection."""
        conn = self._ws_connections.pop(ws_url, None)
        if conn:
            await conn["ws"].close()

    async def bring_to_front(self, ws_url: str):
        """Activate this tab (required before Input.insertText in multi-tab)."""
        await self._send(ws_url, "Page.bringToFront")

    async def submit_query(self, ws_url: str, focus_js: str, query: str):
        """Phase 1: Focus → type → Enter. Must hold _input_lock for multi-tab safety."""
        async with self._input_lock:
            await self.bring_to_front(ws_url)
            await asyncio.sleep(0.3)
            await self.eval_js(ws_url, focus_js)
            await asyncio.sleep(0.5)
            await self.insert_text(ws_url, query)
            await asyncio.sleep(0.8)
            await self.press_enter(ws_url)

    async def poll_response(self, ws_url: str, extract_js: str,
                            wait_after: float, poll_interval: float,
                            poll_max: int, min_length: int) -> str:
        """Phase 2: Wait → poll until stable. Safe to run in parallel."""
        await asyncio.sleep(wait_after)
        prev_text = ""
        stable_count = 0
        for _ in range(poll_max):
            await asyncio.sleep(poll_interval)
            text = await self.eval_js(ws_url, extract_js)
            if text == prev_text and len(text) > min_length:
                stable_count += 1
                if stable_count >= 2:
                    break
            else:
                stable_count = 0
            prev_text = text
        return prev_text

    async def query_in_tab(self, url: str, focus_js: str, query: str,
                           extract_js: str, wait_before: float = 8.0,
                           wait_after: float = 10.0, poll_interval: float = 3.0,
                           poll_max: int = 30, min_length: int = 200) -> str:
        """Full flow: open tab → submit query (serialized) → poll (parallel-safe) → close."""
        tab = self.new_tab(url)
        tab_id = tab.get("id", "")
        ws_url = tab.get("webSocketDebuggerUrl", "")

        if not ws_url:
            self.close_tab(tab_id)
            return "[Error] No WebSocket URL for tab"

        try:
            await self.connect_tab(ws_url)
            await asyncio.sleep(wait_before)

            # Phase 1: submit (serialized via _input_lock)
            await self.submit_query(ws_url, focus_js, query)

            # Phase 2: poll (parallel-safe, uses tab-specific WebSocket)
            text = await self.poll_response(
                ws_url, extract_js, wait_after, poll_interval, poll_max, min_length
            )
            return text or "[No response]"

        finally:
            await self.close_ws(ws_url)
            self.close_tab(tab_id)


def detect_cdp_port() -> int | None:
    for port in [9222, 9229, 9221, 18800]:
        try:
            resp = httpx.get(f"http://127.0.0.1:{port}/json/version", timeout=1)
            if resp.status_code == 200:
                return port
        except Exception:
            continue
    return None


def ensure_browser_bridge(config: dict | None = None) -> BrowserBridge:
    port = (config or {}).get("cdp_port")
    if port is None:
        port = detect_cdp_port()
    if port is None:
        raise RuntimeError(
            "Cannot connect to browser. Start your browser with CDP:\n"
            "  --remote-debugging-port=9222\n"
            "Or add this flag to your browser shortcut."
        )
    bridge = BrowserBridge(cdp_port=port)
    if not bridge.verify_connection():
        raise RuntimeError(f"CDP port {port} found but connection failed.")
    return bridge
