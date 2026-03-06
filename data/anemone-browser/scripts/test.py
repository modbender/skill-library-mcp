#!/usr/bin/env python3
"""Test Chrome CDP connectivity and Google access."""
import asyncio
import json
import sys
import urllib.request

CDP_PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9222
NORMAL_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.7632.116 Safari/537.36"

async def test():
    try:
        import websockets
    except ImportError:
        print("ERROR: pip install websockets")
        return

    # Get tab info
    tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json/list").read())
    print(f"Tabs: {len(tabs)}")
    ws_url = tabs[0]["webSocketDebuggerUrl"]

    async with websockets.connect(ws_url) as ws:
        # Override UA
        await ws.send(json.dumps({
            "id": 1, "method": "Network.setUserAgentOverride",
            "params": {"userAgent": NORMAL_UA}
        }))
        await ws.recv()
        print("UA override: OK")

        # Test Google Search
        await ws.send(json.dumps({
            "id": 2, "method": "Page.navigate",
            "params": {"url": "https://www.google.com/search?q=test"}
        }))
        await ws.recv()
        await asyncio.sleep(5)

        await ws.send(json.dumps({
            "id": 3, "method": "Runtime.evaluate",
            "params": {"expression": "document.title"}
        }))
        r = json.loads(await ws.recv())
        title = r.get("result", {}).get("result", {}).get("value", "?")
        print(f"Google Search title: {title}")

        await ws.send(json.dumps({
            "id": 4, "method": "Runtime.evaluate",
            "params": {"expression": "document.body.innerText.substring(0,300)"}
        }))
        r = json.loads(await ws.recv())
        text = r.get("result", {}).get("result", {}).get("value", "")

        if "sorry" in text.lower() or "captcha" in text.lower() or "unusual traffic" in text.lower():
            print("Google: BLOCKED")
        else:
            print("Google: OK")

        # Test Google Scholar
        await ws.send(json.dumps({
            "id": 5, "method": "Page.navigate",
            "params": {"url": "https://scholar.google.com/scholar?q=test"}
        }))
        await ws.recv()
        await asyncio.sleep(5)

        await ws.send(json.dumps({
            "id": 6, "method": "Runtime.evaluate",
            "params": {"expression": "document.title"}
        }))
        r = json.loads(await ws.recv())
        title = r.get("result", {}).get("result", {}).get("value", "?")
        print(f"Scholar title: {title}")

        await ws.send(json.dumps({
            "id": 7, "method": "Runtime.evaluate",
            "params": {"expression": "document.body.innerText.substring(0,300)"}
        }))
        r = json.loads(await ws.recv())
        text = r.get("result", {}).get("result", {}).get("value", "")

        if "sorry" in text.lower() or "captcha" in text.lower() or "unusual traffic" in text.lower():
            print("Scholar: BLOCKED")
        else:
            print("Scholar: OK")

asyncio.run(test())
