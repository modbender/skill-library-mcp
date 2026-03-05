"""Chrome DevTools Protocol client for audio capture."""

import json
import asyncio
import aiohttp
from typing import Optional, Dict, Any, Callable

CDP_URL = "http://127.0.0.1:9222"

# Meeting URL patterns
MEETING_PATTERNS = [
    "meet.google.com",
    "zoom.us/wc",
    "zoom.us/j",
    "app.zoom.us",
    "teams.microsoft.com",
    "teams.live.com",
    "webex.com/meet",
    "whereby.com",
    "around.co",
    "cal.com/video",
    "riverside.fm",
    "streamyard.com",
]


async def get_tabs(cdp_url: str = CDP_URL) -> list:
    """List all open Chrome tabs."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{cdp_url}/json") as resp:
            tabs = await resp.json()
            return [t for t in tabs if t.get("type") == "page"]


async def find_meeting_tabs(cdp_url: str = CDP_URL) -> list:
    """Find tabs running video meetings."""
    tabs = await get_tabs(cdp_url)
    meetings = []
    for tab in tabs:
        url = tab.get("url", "")
        for pattern in MEETING_PATTERNS:
            if pattern in url:
                meetings.append(tab)
                break
    return meetings


async def connect_tab(ws_url: str) -> aiohttp.ClientWebSocketResponse:
    """Connect to a tab's WebSocket debug URL."""
    session = aiohttp.ClientSession()
    ws = await session.ws_connect(ws_url)
    return ws, session


async def send_cdp(ws, method: str, params: dict = None, msg_id: int = 1) -> dict:
    """Send a CDP command and wait for response."""
    msg = {"id": msg_id, "method": method}
    if params:
        msg["params"] = params
    await ws.send_json(msg)
    
    while True:
        resp = await ws.receive_json()
        if resp.get("id") == msg_id:
            return resp
        # Skip events
        if "method" in resp:
            continue


async def evaluate_js(ws, expression: str, msg_id: int = 1) -> Any:
    """Evaluate JavaScript in the tab context."""
    resp = await send_cdp(ws, "Runtime.evaluate", {
        "expression": expression,
        "awaitPromise": True,
        "returnByValue": True,
    }, msg_id)
    
    result = resp.get("result", {}).get("result", {})
    if result.get("type") == "object" and result.get("subtype") == "error":
        raise Exception(f"JS Error: {result.get('description', 'unknown')}")
    return result.get("value")
