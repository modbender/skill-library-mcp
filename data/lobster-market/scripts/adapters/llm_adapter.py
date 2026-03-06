#!/usr/bin/env python3
"""LLM 直调适配器 — 接收任务请求，调用 LLM API 执行，返回结果。

用法:
  python3 llm_adapter.py --port 8900 --system-prompt /path/to/prompt.md

支持的 LLM:
  - DashScope (DASHSCOPE_API_KEY) — 默认 qwen-plus
  - OpenAI 兼容 (OPENAI_API_KEY + OPENAI_BASE_URL)

标准接口:
  POST /execute  — 执行任务
  GET  /health   — 健康检查
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

try:
    from aiohttp import web
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("llm-adapter")

# ---------------------------------------------------------------------------
# LLM calling
# ---------------------------------------------------------------------------

def _get_llm_config(model_override: str = ""):
    """Detect available LLM provider and return (base_url, api_key, model)."""
    # DashScope
    ds_key = os.environ.get("DASHSCOPE_API_KEY", "")
    if ds_key:
        return (
            "https://dashscope.aliyuncs.com/compatible-mode/v1",
            ds_key,
            model_override or "qwen-plus",
        )
    # OpenAI compatible
    oai_key = os.environ.get("OPENAI_API_KEY", "")
    if oai_key:
        return (
            os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            oai_key,
            model_override or "gpt-4o-mini",
        )
    return None, None, None


def _call_llm_sync(base_url: str, api_key: str, model: str, messages: list) -> str:
    """Synchronous LLM call via urllib (no extra deps)."""
    import urllib.request

    url = f"{base_url}/chat/completions"
    body = json.dumps({"model": model, "messages": messages}).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    })
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read().decode())
    return data["choices"][0]["message"]["content"]


# ---------------------------------------------------------------------------
# HTTP handlers
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = ""
MODEL = ""
BASE_URL = ""
API_KEY = ""


async def handle_execute(request):
    """POST /execute — 执行 LLM 任务"""
    try:
        body = await request.json()
    except Exception:
        return web.json_response({"status": "failed", "error": "Invalid JSON"}, status=400)

    task_id = body.get("task_id", "")
    message = body.get("message", {})
    log.info("📥 Execute task: %s", task_id)

    # Extract text from message.parts
    if isinstance(message, dict):
        parts = message.get("parts", [])
        texts = [p.get("text", "") for p in parts if isinstance(p, dict) and p.get("type") == "text"]
        user_text = "\n".join(texts) if texts else json.dumps(message, ensure_ascii=False)
    elif isinstance(message, str):
        user_text = message
    else:
        user_text = str(message)

    if not BASE_URL or not API_KEY:
        return web.json_response({
            "status": "failed",
            "error": "No LLM API key configured (set DASHSCOPE_API_KEY or OPENAI_API_KEY)",
        })

    # Build messages
    messages = []
    if SYSTEM_PROMPT:
        messages.append({"role": "system", "content": SYSTEM_PROMPT})
    messages.append({"role": "user", "content": user_text})

    try:
        import asyncio
        loop = asyncio.get_event_loop()
        result_text = await loop.run_in_executor(
            None, _call_llm_sync, BASE_URL, API_KEY, MODEL, messages
        )
    except Exception as e:
        log.error("❌ LLM call failed: %s", e)
        return web.json_response({"status": "failed", "error": str(e)})

    log.info("✅ Task completed: %s (%d chars)", task_id, len(result_text))
    return web.json_response({
        "status": "completed",
        "artifacts": [{
            "name": "任务结果",
            "parts": [{"type": "text", "text": result_text}],
            "metadata": {"mime_type": "text/markdown"},
        }],
    })


async def handle_health(request):
    """GET /health"""
    return web.json_response({
        "status": "ok",
        "adapter": "llm",
        "model": MODEL,
    })


# ---------------------------------------------------------------------------
# Fallback: stdlib http.server when aiohttp is unavailable
# ---------------------------------------------------------------------------

def _run_stdlib_server(port: int):
    """Minimal HTTP server using only stdlib."""
    import http.server
    import asyncio

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/health":
                self._respond(200, {"status": "ok", "adapter": "llm", "model": MODEL})
            else:
                self._respond(404, {"error": "not found"})

        def do_POST(self):
            if self.path != "/execute":
                self._respond(404, {"error": "not found"})
                return
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length)) if length else {}

            task_id = body.get("task_id", "")
            message = body.get("message", {})
            log.info("📥 Execute task: %s", task_id)

            if isinstance(message, dict):
                parts = message.get("parts", [])
                texts = [p.get("text", "") for p in parts if isinstance(p, dict) and p.get("type") == "text"]
                user_text = "\n".join(texts) if texts else json.dumps(message, ensure_ascii=False)
            elif isinstance(message, str):
                user_text = message
            else:
                user_text = str(message)

            if not BASE_URL or not API_KEY:
                self._respond(200, {"status": "failed", "error": "No LLM API key configured"})
                return

            msgs = []
            if SYSTEM_PROMPT:
                msgs.append({"role": "system", "content": SYSTEM_PROMPT})
            msgs.append({"role": "user", "content": user_text})

            try:
                result_text = _call_llm_sync(BASE_URL, API_KEY, MODEL, msgs)
            except Exception as e:
                self._respond(200, {"status": "failed", "error": str(e)})
                return

            self._respond(200, {
                "status": "completed",
                "artifacts": [{
                    "name": "任务结果",
                    "parts": [{"type": "text", "text": result_text}],
                    "metadata": {"mime_type": "text/markdown"},
                }],
            })

        def _respond(self, code, obj):
            data = json.dumps(obj, ensure_ascii=False).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, fmt, *a):
            log.info(fmt, *a)

    server = http.server.HTTPServer(("0.0.0.0", port), Handler)
    log.info("🚀 LLM Adapter (stdlib) listening on port %d", port)
    server.serve_forever()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    global SYSTEM_PROMPT, MODEL, BASE_URL, API_KEY

    parser = argparse.ArgumentParser(description="LLM 直调适配器")
    parser.add_argument("--port", type=int, default=8900)
    parser.add_argument("--system-prompt", help="System prompt file path (.md / .txt)")
    parser.add_argument("--model", default="", help="Override default model name")
    args = parser.parse_args()

    # Load system prompt
    if args.system_prompt:
        p = Path(args.system_prompt)
        if p.exists():
            SYSTEM_PROMPT = p.read_text().strip()
            log.info("📄 System prompt loaded: %s (%d chars)", p, len(SYSTEM_PROMPT))
        else:
            log.warning("⚠️  System prompt file not found: %s", p)

    # Detect LLM provider
    BASE_URL, API_KEY, MODEL = _get_llm_config(args.model)
    if not BASE_URL:
        log.warning("⚠️  No LLM API key found. Set DASHSCOPE_API_KEY or OPENAI_API_KEY.")
    else:
        log.info("🤖 LLM: %s @ %s", MODEL, BASE_URL[:50])

    if HAS_AIOHTTP:
        app = web.Application()
        app.router.add_post("/execute", handle_execute)
        app.router.add_get("/health", handle_health)
        log.info("🚀 LLM Adapter (aiohttp) starting on port %d", args.port)
        web.run_app(app, host="0.0.0.0", port=args.port, print=None)
    else:
        _run_stdlib_server(args.port)


if __name__ == "__main__":
    main()
