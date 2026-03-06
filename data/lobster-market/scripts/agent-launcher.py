#!/usr/bin/env python3
"""🦞 Agent Launcher — 从 API 自动读取 agent 配置并启动 adapter + connector

用法:
  python3 agent-launcher.py start    # 启动所有 agent
  python3 agent-launcher.py stop     # 停止所有
  python3 agent-launcher.py status   # 查看状态
  python3 agent-launcher.py restart  # 重启

环境变量:
  LOBSTER_API       API 地址 (默认 https://mindcore8.com/api/v1)
  DASHSCOPE_API_KEY DashScope API Key (llm adapter 需要)
  AGENT_PROMPT_DIR  System prompt 目录 (默认 /root/agent-prompts)
"""

import argparse
import json
import os
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PID_DIR = Path("/tmp/lobster-agents")
PROMPT_DIR = Path(os.environ.get("AGENT_PROMPT_DIR", "/root/agent-prompts"))
LOBSTER_API = os.environ.get("LOBSTER_API", "https://mindcore8.com/api/v1")
TOKEN_FILE = Path.home() / ".lobster-market" / "token.json"
BASE_PORT = 8900  # auto-assign ports starting from here


def load_token() -> str:
    if TOKEN_FILE.exists():
        data = json.loads(TOKEN_FILE.read_text())
        return data.get("access_token", "")
    return ""


def api_get(path: str) -> dict | list | None:
    """GET request to Lobster API."""
    token = load_token()
    url = f"{LOBSTER_API}{path}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}" if token else "",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"⚠️  API request failed: {e}")
        return None


def fetch_agents() -> list[dict]:
    """Fetch all agents with execution_config from API."""
    # Try agents list API (supports pagination)
    for path in ["/agents?page_size=100", "/agents/discover?page=1&page_size=100"]:
        data = api_get(path)
        if data:
            agents = data if isinstance(data, list) else data.get("items", data.get("agents", []))
            configured = [a for a in agents if a.get("execution_config") and a["execution_config"].get("adapter")]
            if configured:
                return configured

    # Fallback: try cached config
    cache_file = PID_DIR / "agents.cache.json"
    if cache_file.exists():
        print("⚠️  API 不可用，使用缓存")
        return json.loads(cache_file.read_text())

    print("❌ 无法获取 Agent 列表")
    return []


def save_cache(agents: list[dict]):
    PID_DIR.mkdir(parents=True, exist_ok=True)
    (PID_DIR / "agents.cache.json").write_text(json.dumps(agents, indent=2))


def start_adapter(agent: dict, port: int) -> subprocess.Popen | None:
    """Start the appropriate adapter based on execution_config."""
    config = agent.get("execution_config", {})
    adapter_type = config.get("adapter", "llm")
    role = config.get("role", "agent")
    agent_id = agent["id"]

    log_file = PID_DIR / f"{role}-adapter.log"
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    if adapter_type == "llm":
        # LLM adapter
        prompt_file = PROMPT_DIR / f"{role}.md"
        cmd = [
            sys.executable, "-u",
            str(SCRIPT_DIR / "adapters" / "llm_adapter.py"),
            "--port", str(port),
        ]
        if prompt_file.exists():
            cmd.extend(["--system-prompt", str(prompt_file)])
        model = config.get("model")
        if model:
            cmd.extend(["--model", model])

    elif adapter_type == "nanobot":
        # Nanobot adapter
        cmd = [
            sys.executable, "-u",
            str(SCRIPT_DIR / "adapters" / "nanobot_adapter.py"),
            "--port", str(port),
        ]
        if config.get("nanobot_bin"):
            cmd.extend(["--nanobot-bin", config["nanobot_bin"]])
        if config.get("nanobot_dir"):
            cmd.extend(["--nanobot-dir", config["nanobot_dir"]])
        if config.get("agent_name"):
            cmd.extend(["--agent-name", config["agent_name"]])

    elif adapter_type == "openclaw":
        cmd = [
            sys.executable, "-u",
            str(SCRIPT_DIR / "adapters" / "openclaw_adapter.py"),
            "--port", str(port),
        ]
        if config.get("agent_name"):
            cmd.extend(["--agent-name", config["agent_name"]])

    elif adapter_type == "external":
        # No adapter to start — external endpoint is used directly
        return None

    else:
        print(f"  ⚠️  Unknown adapter type: {adapter_type}")
        return None

    with open(log_file, "w") as lf:
        proc = subprocess.Popen(cmd, stdout=lf, stderr=subprocess.STDOUT, env=env)
    (PID_DIR / f"{role}-adapter.pid").write_text(str(proc.pid))
    return proc


def start_connector(agent: dict, port: int) -> subprocess.Popen:
    """Start market-connect.py for an agent."""
    config = agent.get("execution_config", {})
    adapter_type = config.get("adapter", "llm")
    role = config.get("role", "agent")
    agent_id = agent["id"]

    # Determine local endpoint
    if adapter_type == "external":
        endpoint = config.get("endpoint", f"http://localhost:{port}/execute")
    else:
        endpoint = f"http://localhost:{port}/execute"

    log_file = PID_DIR / f"{role}-connect.log"
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    cmd = [
        sys.executable, "-u",
        str(SCRIPT_DIR / "market-connect.py"),
        "--agent-id", agent_id,
        "--local-endpoint", endpoint,
        "--max-concurrent", "1",
    ]

    with open(log_file, "w") as lf:
        proc = subprocess.Popen(cmd, stdout=lf, stderr=subprocess.STDOUT, env=env)
    (PID_DIR / f"{role}-connect.pid").write_text(str(proc.pid))
    return proc


def cmd_start():
    PID_DIR.mkdir(parents=True, exist_ok=True)
    print("🦞 Agent Launcher — Starting...")

    agents = fetch_agents()
    if not agents:
        # Fallback: try internal API
        print("🔄 Trying internal agent API...")
        data = api_get("/agents?page_size=50")
        if data:
            items = data if isinstance(data, list) else data.get("items", data.get("agents", []))
            agents = [a for a in items if a.get("execution_config") and a["execution_config"].get("adapter")]

    if not agents:
        print("❌ No agents found with execution_config. Set configs first.")
        sys.exit(1)

    save_cache(agents)
    print(f"📋 Found {len(agents)} agents with execution_config\n")

    for i, agent in enumerate(agents):
        config = agent.get("execution_config", {})
        adapter_type = config.get("adapter", "?")
        role = config.get("role", f"agent{i}")
        port = BASE_PORT + i
        agent_id = agent["id"]

        print(f"  ▸ {role} ({adapter_type}) — port {port}, agent {agent_id[:8]}...")

        # Start adapter (unless external)
        if adapter_type != "external":
            adapter_proc = start_adapter(agent, port)
            if adapter_proc:
                time.sleep(1)
                if adapter_proc.poll() is not None:
                    print(f"    ❌ Adapter crashed. Check {PID_DIR}/{role}-adapter.log")
                    continue
                # Health check
                try:
                    with urllib.request.urlopen(f"http://localhost:{port}/health", timeout=3) as r:
                        health = json.loads(r.read().decode())
                        print(f"    ✅ Adapter healthy: {health.get('adapter', '?')}")
                except Exception:
                    print(f"    ⚠️  Adapter not responding on port {port}")

        # Start connector
        start_connector(agent, port)
        print(f"    ✅ Connector started")

    print(f"\n✅ All agents started. Logs in {PID_DIR}/")


def cmd_stop():
    print("🛑 Stopping all agents...")
    for pidfile in PID_DIR.glob("*.pid"):
        try:
            pid = int(pidfile.read_text().strip())
            os.kill(pid, signal.SIGTERM)
            print(f"  ▸ Killed {pidfile.stem} (PID {pid})")
        except (ProcessLookupError, ValueError):
            pass
        pidfile.unlink(missing_ok=True)
    print("✅ All agents stopped.")


def cmd_status():
    print("📊 Agent Status:\n")
    agents_cache = PID_DIR / "agents.cache.json"
    if not agents_cache.exists():
        print("  No cached agent info. Run 'start' first.")
        return

    agents = json.loads(agents_cache.read_text())
    for i, agent in enumerate(agents):
        config = agent.get("execution_config", {})
        role = config.get("role", f"agent{i}")
        port = BASE_PORT + i

        # Check PIDs
        def check_pid(name):
            pf = PID_DIR / f"{role}-{name}.pid"
            if pf.exists():
                try:
                    pid = int(pf.read_text().strip())
                    os.kill(pid, 0)
                    return f"▶ running ({pid})"
                except (ProcessLookupError, ValueError):
                    return "⏹ dead"
            return "⏹ stopped"

        adapter_s = check_pid("adapter")
        connect_s = check_pid("connect")

        # Health check
        health = ""
        if "running" in adapter_s:
            try:
                with urllib.request.urlopen(f"http://localhost:{port}/health", timeout=2) as r:
                    h = json.loads(r.read().decode())
                    health = f"✅ {h.get('adapter', '?')}"
            except Exception:
                health = "❌ unhealthy"

        print(f"  {role} ({config.get('adapter', '?')}): adapter={adapter_s}  connector={connect_s}  port={port}  {health}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🦞 Agent Launcher")
    parser.add_argument("action", choices=["start", "stop", "status", "restart"], default="start", nargs="?")
    args = parser.parse_args()

    if args.action == "start":
        cmd_start()
    elif args.action == "stop":
        cmd_stop()
    elif args.action == "status":
        cmd_status()
    elif args.action == "restart":
        cmd_stop()
        time.sleep(2)
        cmd_start()
