"""
Browser tab audio capture via Chrome CDP.

Strategy: Use CDP to inject JavaScript that captures tab audio via
the Web Audio API + MediaRecorder, then streams PCM16 chunks back
to the Percept receiver via WebSocket or HTTP POST.

Key insight: We can't use tabCapture (extension-only), but we CAN use
getDisplayMedia({ audio: true, video: false }) which Chrome supports
for tab audio capture. The user sees a picker — we auto-select the
correct tab via CDP.

Alternative for meetings: Many meeting platforms expose audio via
Web Audio API's AudioContext destination. We tap into that directly.
"""

import asyncio
import json
import time
import struct
import base64
from typing import Optional
import aiohttp

from .cdp_client import (
    get_tabs, find_meeting_tabs, connect_tab, 
    send_cdp, evaluate_js, CDP_URL
)

PERCEPT_RECEIVER = "http://127.0.0.1:8900"
SAMPLE_RATE = 16000
CHUNK_DURATION_MS = 3000  # Send audio every 3 seconds


# JavaScript injected into the meeting tab to capture audio
CAPTURE_JS = """
(async () => {
    // Check if already capturing
    if (window.__perceptCapture) {
        return { status: 'already_capturing', sessionId: window.__perceptSessionId };
    }
    
    // Generate session ID
    const sessionId = 'browser_' + Date.now();
    window.__perceptSessionId = sessionId;
    
    // Try getDisplayMedia for tab audio (Chrome shows a picker)
    let stream;
    try {
        stream = await navigator.mediaDevices.getDisplayMedia({
            audio: {
                echoCancellation: false,
                noiseSuppression: false,
                autoGainControl: false,
                sampleRate: 16000,
            },
            video: false,  // Audio only
        });
    } catch (e) {
        // Fallback: try to capture from AudioContext destination
        // This works on some meeting platforms
        try {
            const ctx = new AudioContext({ sampleRate: 16000 });
            const dest = ctx.createMediaStreamDestination();
            
            // Try to find existing audio elements
            const audioElements = document.querySelectorAll('audio, video');
            if (audioElements.length === 0) {
                return { status: 'error', error: 'No audio sources found. Join a meeting first.' };
            }
            
            for (const el of audioElements) {
                try {
                    const source = ctx.createMediaElementSource(el);
                    source.connect(dest);
                    source.connect(ctx.destination); // Keep playing
                } catch (err) {
                    // Element might already be connected
                }
            }
            stream = dest.stream;
        } catch (e2) {
            return { status: 'error', error: e2.message };
        }
    }
    
    if (!stream || stream.getAudioTracks().length === 0) {
        return { status: 'error', error: 'No audio track in stream' };
    }
    
    // Set up AudioContext for PCM conversion
    const audioCtx = new AudioContext({ sampleRate: 16000 });
    const source = audioCtx.createMediaStreamSource(stream);
    const processor = audioCtx.createScriptProcessor(4096, 1, 1);
    
    let audioBuffer = [];
    let chunkStartTime = Date.now();
    const CHUNK_MS = CHUNK_DURATION_MS;
    
    processor.onaudioprocess = (e) => {
        const input = e.inputBuffer.getChannelData(0);
        // Convert float32 to int16
        const pcm16 = new Int16Array(input.length);
        for (let i = 0; i < input.length; i++) {
            pcm16[i] = Math.max(-32768, Math.min(32767, Math.round(input[i] * 32768)));
        }
        audioBuffer.push(pcm16);
        
        // Send chunk every CHUNK_MS
        if (Date.now() - chunkStartTime >= CHUNK_MS) {
            const totalLength = audioBuffer.reduce((acc, arr) => acc + arr.length, 0);
            const merged = new Int16Array(totalLength);
            let offset = 0;
            for (const arr of audioBuffer) {
                merged.set(arr, offset);
                offset += arr.length;
            }
            
            // Convert to base64 for transport
            const bytes = new Uint8Array(merged.buffer);
            let binary = '';
            for (let i = 0; i < bytes.length; i++) {
                binary += String.fromCharCode(bytes[i]);
            }
            const b64 = btoa(binary);
            
            // Post to Percept receiver
            fetch('PERCEPT_URL/audio/browser', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sessionId: sessionId,
                    audio: b64,
                    sampleRate: 16000,
                    format: 'pcm16',
                    source: 'browser_cdp',
                    tabUrl: window.location.href,
                    tabTitle: document.title,
                }),
            }).catch(err => console.error('Percept send error:', err));
            
            audioBuffer = [];
            chunkStartTime = Date.now();
        }
    };
    
    source.connect(processor);
    processor.connect(audioCtx.destination);
    
    // Store for cleanup
    window.__perceptCapture = {
        stream, audioCtx, source, processor,
        stop: () => {
            processor.disconnect();
            source.disconnect();
            audioCtx.close();
            stream.getTracks().forEach(t => t.stop());
            delete window.__perceptCapture;
            delete window.__perceptSessionId;
        }
    };
    
    return { status: 'capturing', sessionId: sessionId, tracks: stream.getAudioTracks().length };
})()
""".replace("CHUNK_DURATION_MS", str(CHUNK_DURATION_MS)).replace("PERCEPT_URL", PERCEPT_RECEIVER)


STOP_JS = """
(() => {
    if (window.__perceptCapture) {
        window.__perceptCapture.stop();
        return { status: 'stopped' };
    }
    return { status: 'not_capturing' };
})()
"""

STATUS_JS = """
(() => {
    if (window.__perceptCapture) {
        return { 
            status: 'capturing', 
            sessionId: window.__perceptSessionId,
            url: window.location.href,
            title: document.title,
        };
    }
    return { status: 'idle' };
})()
"""


async def capture_tab(tab_id: Optional[str] = None, cdp_url: str = CDP_URL) -> dict:
    """Start capturing audio from a browser tab.
    
    If tab_id is None, auto-detects meeting tabs.
    """
    tabs = await get_tabs(cdp_url)
    
    if not tabs:
        return {"status": "error", "error": "No tabs open in CDP Chrome"}
    
    target_tab = None
    
    if tab_id:
        for tab in tabs:
            if tab["id"] == tab_id:
                target_tab = tab
                break
        if not target_tab:
            return {"status": "error", "error": f"Tab {tab_id} not found"}
    else:
        # Auto-detect meeting tab
        meetings = await find_meeting_tabs(cdp_url)
        if meetings:
            target_tab = meetings[0]
            print(f"🎯 Auto-detected meeting: {target_tab['title']}")
        else:
            # Default to active tab
            target_tab = tabs[0]
            print(f"📌 No meeting detected, using active tab: {target_tab['title']}")
    
    ws_url = target_tab["webSocketDebuggerUrl"]
    ws, session = await connect_tab(ws_url)
    
    try:
        # Enable Runtime domain
        await send_cdp(ws, "Runtime.enable", msg_id=1)
        
        # Inject capture script
        result = await evaluate_js(ws, CAPTURE_JS, msg_id=2)
        
        return {
            "status": "ok",
            "tab": {
                "id": target_tab["id"],
                "title": target_tab["title"],
                "url": target_tab["url"],
            },
            "capture": result,
        }
    finally:
        await ws.close()
        await session.close()


async def stop_capture(tab_id: Optional[str] = None, cdp_url: str = CDP_URL) -> dict:
    """Stop capturing audio from a browser tab."""
    tabs = await get_tabs(cdp_url)
    
    if tab_id:
        target_tabs = [t for t in tabs if t["id"] == tab_id]
    else:
        target_tabs = tabs  # Try all tabs
    
    results = []
    for tab in target_tabs:
        ws_url = tab["webSocketDebuggerUrl"]
        ws, session = await connect_tab(ws_url)
        try:
            await send_cdp(ws, "Runtime.enable", msg_id=1)
            result = await evaluate_js(ws, STOP_JS, msg_id=2)
            if result and result.get("status") == "stopped":
                results.append({"tab": tab["title"], "status": "stopped"})
        except Exception:
            pass
        finally:
            await ws.close()
            await session.close()
    
    return {"status": "ok", "stopped": results} if results else {"status": "none_capturing"}


async def capture_status(cdp_url: str = CDP_URL) -> dict:
    """Check capture status across all tabs."""
    tabs = await get_tabs(cdp_url)
    active = []
    
    for tab in tabs:
        ws_url = tab.get("webSocketDebuggerUrl")
        if not ws_url:
            continue
        ws, session = await connect_tab(ws_url)
        try:
            await send_cdp(ws, "Runtime.enable", msg_id=1)
            result = await evaluate_js(ws, STATUS_JS, msg_id=2)
            if result and result.get("status") == "capturing":
                active.append({
                    "tab_id": tab["id"],
                    "title": result.get("title", tab["title"]),
                    "url": result.get("url", tab["url"]),
                    "sessionId": result.get("sessionId"),
                })
        except Exception:
            pass
        finally:
            await ws.close()
            await session.close()
    
    return {"status": "ok", "active_captures": active, "total_tabs": len(tabs)}


async def watch_meetings(cdp_url: str = CDP_URL, check_interval: int = 15):
    """Auto-detect and capture meeting tabs. Runs continuously."""
    print("👀 Watching for meeting tabs...")
    capturing = set()
    
    while True:
        try:
            meetings = await find_meeting_tabs(cdp_url)
            
            for tab in meetings:
                tab_id = tab["id"]
                if tab_id not in capturing:
                    print(f"🎙️ Meeting detected: {tab['title']} ({tab['url'][:60]})")
                    result = await capture_tab(tab_id, cdp_url)
                    if result.get("capture", {}).get("status") == "capturing":
                        capturing.add(tab_id)
                        print(f"✅ Capture started: {result['capture'].get('sessionId')}")
                    else:
                        print(f"⚠️ Capture failed: {result}")
            
            # Check if captured tabs are still open
            open_ids = {t["id"] for t in await get_tabs(cdp_url)}
            closed = capturing - open_ids
            if closed:
                for tab_id in closed:
                    print(f"📴 Tab closed, capture ended: {tab_id}")
                capturing -= closed
            
        except Exception as e:
            print(f"❌ Watch error: {e}")
        
        await asyncio.sleep(check_interval)
