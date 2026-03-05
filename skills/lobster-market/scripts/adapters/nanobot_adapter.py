#!/usr/bin/env python3
"""Nanobot 适配器 — 将任务转发到 nanobot 实例。

用法:
  python3 nanobot_adapter.py --port 8901 --nanobot-dir ~/.nanobot --agent-name product

标准接口:
  POST /execute  — 执行任务（调用 nanobot CLI）
  GET  /health   — 健康检查
"""

import argparse
import asyncio
import json
import logging
import os
import subprocess
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
log = logging.getLogger("nanobot-adapter")

NANOBOT_DIR = ""
AGENT_NAME = ""


async def _run_nanobot(message_text: str) -> str:
    """Run nanobot CLI and return output."""
    cmd = ["nanobot", "run"]
    if AGENT_NAME:
        cmd += ["--agent", AGENT_NAME]
    if NANOBOT_DIR:
        cmd += ["--dir", NANOBOT_DIR]
    cmd += ["--message", message_text]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=300)

    if proc.returncode != 0:
        err = stderr.decode().strip() or f"nanobot exit code {proc.returncode}"
        raise RuntimeError(err)

    return stdout.decode().strip()


def _extract_text(message) -> str:
    if isinstance(message, dict):
        parts = message.get("parts", [])
        texts = [p.get("text", "") for p in parts if isinstance(p, dict) and p.get("type") == "text"]
        return "\n".join(texts) if texts else json.dumps(message, ensure_ascii=False)
    return str(message)


async def handle_execute(request):
    try:
        body = await request.json()
    except Exception:
        return web.json_response({"status": "failed", "error": "Invalid JSON"}, status=400)

    task_id = body.get("task_id", "")
    message = body.get("message", {})
    user_text = _extract_text(message)
    log.info("📥 Execute task: %s", task_id)

    try:
        result_text = await _run_nanobot(user_text)
    except Exception as e:
        log.error("❌ Nanobot failed: %s", e)
        return web.json_response({"status": "failed", "error": str(e)})

    log.info("✅ Task completed: %s", task_id)
    return web.json_response({
        "status": "completed",
        "artifacts": [{
            "name": "任务结果",
            "parts": [{"type": "text", "text": result_text}],
            "metadata": {"mime_type": "text/markdown"},
        }],
    })


async def handle_health(request):
    return web.json_response({
        "status": "ok",
        "adapter": "nanobot",
        "agent": AGENT_NAME,
    })


def main():
    global NANOBOT_DIR, AGENT_NAME

    parser = argparse.ArgumentParser(description="Nanobot 适配器")
    parser.add_argument("--port", type=int, default=8901)
    parser.add_argument("--nanobot-dir", default="", help="Nanobot working directory")
    parser.add_argument("--agent-name", default="", help="Nanobot agent name")
    args = parser.parse_args()

    NANOBOT_DIR = args.nanobot_dir
    AGENT_NAME = args.agent_name

    if not HAS_AIOHTTP:
        print("❌ aiohttp required. Run: pip3 install aiohttp", file=sys.stderr)
        sys.exit(1)

    app = web.Application()
    app.router.add_post("/execute", handle_execute)
    app.router.add_get("/health", handle_health)
    log.info("🚀 Nanobot Adapter on port %d (agent=%s)", args.port, AGENT_NAME or "(default)")
    web.run_app(app, host="0.0.0.0", port=args.port, print=None)


if __name__ == "__main__":
    main()
