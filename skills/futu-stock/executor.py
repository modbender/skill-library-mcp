#!/usr/bin/env python3
"""
MCP Skill Executor
==================
Handles dynamic communication with the futu-stock MCP server.
Supports: --check-env, --install-deps, --call, --describe, --list
"""

import json
import sys
import asyncio
import argparse
import socket
import shutil
import subprocess
import os
import platform
from pathlib import Path

# Check if mcp package is available
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    HAS_MCP = True
except ImportError:
    HAS_MCP = False
    print("Warning: mcp package not installed. Install with: pip install mcp", file=sys.stderr)


def _get_env() -> dict:
    """Load env from mcp-config.json and override with os.environ."""
    config_path = Path(__file__).parent / "mcp-config.json"
    env = {}
    if config_path.exists():
        with open(config_path) as f:
            cfg = json.load(f)
            env = dict(cfg.get("env", {}))
    env.update(os.environ)
    return env


def _check_futu_port(env: dict, timeout: float = 3.0) -> bool:
    """Best-effort runtime check: ensure FutuOpenD TCP 端口真的在监听.

    直接用 socket 建立一次 TCP 连接，而不是只看日志，避免“日志说监听了但进程已经挂了”的情况。
    """
    host = (env or {}).get("FUTU_HOST") or "127.0.0.1"
    port_str = (env or {}).get("FUTU_PORT") or "11111"
    try:
        port = int(port_str)
    except ValueError:
        return False

    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _try_start_opend(env: dict) -> bool:
    """Try to start FutuOpenD if OPEND_PATH is set. Returns True if started or already running."""
    opend_path = env.get("OPEND_PATH")
    if not opend_path or not Path(opend_path).is_dir():
        return False

    if _check_futu_port(env):
        return True

    sys_name = platform.system()
    if sys_name == "Windows":
        exe = Path(opend_path) / "FutuOpenD.exe"
    elif sys_name == "Darwin":
        app = Path(opend_path) / "FutuOpenD.app"
        exe = app / "Contents" / "MacOS" / "FutuOpenD" if app.is_dir() else Path(opend_path) / "FutuOpenD"
    else:
        exe = Path(opend_path) / "FutuOpenD"

    if not exe.exists():
        return False

    try:
        import time
        subprocess.Popen(
            [str(exe)],
            cwd=str(Path(opend_path)),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        for _ in range(10):
            time.sleep(1)
            if _check_futu_port(env):
                return True
    except Exception:
        pass
    return False


def _ensure_futu_ready(env: dict) -> None:
    """Ensure OpenD is listening. Try auto-start if OPEND_PATH set. Exit on failure."""
    if _check_futu_port(env):
        return
    if _try_start_opend(env):
        return
    host = env.get("FUTU_HOST") or "127.0.0.1"
    port = env.get("FUTU_PORT") or "11111"
    print(f"Error: FutuOpenD not listening on {host}:{port}", file=sys.stderr)
    print("Start OpenD manually or set OPEND_PATH for auto-start.", file=sys.stderr)
    sys.exit(1)


def run_check_env() -> None:
    """Run environment check and print results."""
    env = _get_env()
    results = []

    # python3
    py_ok = shutil.which("python3") is not None
    results.append(("python3", "OK" if py_ok else "缺失", "pip install / brew install python3" if not py_ok else ""))

    # futu-mcp-server
    futu_ok = shutil.which("futu-mcp-server") is not None
    results.append(("futu-mcp-server", "OK" if futu_ok else "缺失", "pipx install futu-stock-mcp-server" if not futu_ok else ""))

    # mcp package
    mcp_ok = HAS_MCP
    results.append(("mcp 包", "OK" if mcp_ok else "缺失", "pip install mcp" if not mcp_ok else ""))

    # OpenD
    opend_ok = _check_futu_port(env)
    opend_msg = "监听中" if opend_ok else "未监听"
    opend_fix = "" if opend_ok else "启动 OpenD 或设置 OPEND_PATH"
    results.append(("OpenD (FUTU_HOST:FUTU_PORT)", opend_msg, opend_fix))

    for name, status, fix in results:
        fix_str = f" -> {fix}" if fix else ""
        print(f"  {name}: {status}{fix_str}")
    print()


async def list_tools_from_server(server_config):
    """Get list of available tools from MCP server."""
    env = {**server_config.get("env", {}), **os.environ}
    _ensure_futu_ready(env)

    server_params = StdioServerParameters(
        command=server_config["command"],
        args=server_config.get("args", []),
        env=env
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            response = await session.list_tools()
            return [
                {
                    "name": tool.name,
                    "description": tool.description
                }
                for tool in response.tools
            ]


async def describe_tool_from_server(server_config, tool_name: str):
    """Get detailed schema for a specific tool from MCP server."""
    env = {**server_config.get("env", {}), **os.environ}
    _ensure_futu_ready(env)

    server_params = StdioServerParameters(
        command=server_config["command"],
        args=server_config.get("args", []),
        env=env
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            response = await session.list_tools()

            for tool in response.tools:
                if tool.name == tool_name:
                    return {
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema
                    }
            return None


async def call_tool_on_server(server_config, tool_name: str, arguments: dict):
    """Execute a tool call on MCP server."""
    env = {**server_config.get("env", {}), **os.environ}
    _ensure_futu_ready(env)

    server_params = StdioServerParameters(
        command=server_config["command"],
        args=server_config.get("args", []),
        env=env
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            response = await session.call_tool(tool_name, arguments)
            return response.content


def run_install_deps() -> None:
    """Install missing dependencies (mcp, futu-stock-mcp-server)."""
    installed = []
    # mcp package
    if not HAS_MCP:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "mcp"], check=True, capture_output=True)
            installed.append("mcp")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install mcp: {e}", file=sys.stderr)
            sys.exit(1)

    # futu-mcp-server
    if shutil.which("futu-mcp-server") is None:
        ok = False
        if shutil.which("pipx"):
            try:
                subprocess.run(["pipx", "install", "futu-stock-mcp-server"], check=True, capture_output=True)
                installed.append("futu-stock-mcp-server")
                ok = True
            except subprocess.CalledProcessError as e:
                print(f"pipx install failed: {e}", file=sys.stderr)
        if not ok and shutil.which("pip"):
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "futu-stock-mcp-server"], check=True, capture_output=True)
                installed.append("futu-stock-mcp-server")
                ok = True
            except subprocess.CalledProcessError as e:
                print(f"pip install failed: {e}", file=sys.stderr)
        if not ok:
            print("Install futu-stock-mcp-server manually: pipx install futu-stock-mcp-server", file=sys.stderr)
            sys.exit(1)

    if installed:
        print(f"Installed: {', '.join(installed)}")
    else:
        print("All dependencies already installed.")


async def main():
    parser = argparse.ArgumentParser(description="MCP Skill Executor")
    parser.add_argument("--check-env", action="store_true", help="Check environment (python3, futu-mcp-server, mcp, OpenD)")
    parser.add_argument("--install-deps", action="store_true", help="Install missing dependencies (mcp, futu-stock-mcp-server)")
    parser.add_argument("--call", help="JSON tool call to execute")
    parser.add_argument("--describe", help="Get tool schema")
    parser.add_argument("--list", action="store_true", help="List all tools")

    args = parser.parse_args()

    # --check-env: run before loading config, no MCP required
    if args.check_env:
        run_check_env()
        return

    # --install-deps
    if args.install_deps:
        run_install_deps()
        return

    # Load server config
    config_path = Path(__file__).parent / "mcp-config.json"
    if not config_path.exists():
        print(f"Error: Configuration file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    with open(config_path) as f:
        config = json.load(f)

    if not HAS_MCP:
        print("Error: mcp package not installed", file=sys.stderr)
        print("Install with: pip install mcp", file=sys.stderr)
        sys.exit(1)

    try:
        if args.list:
            tools = await list_tools_from_server(config)
            print(json.dumps(tools, indent=2))

        elif args.describe:
            schema = await describe_tool_from_server(config, args.describe)
            if schema:
                print(json.dumps(schema, indent=2))
            else:
                print(f"Tool not found: {args.describe}", file=sys.stderr)
                sys.exit(1)

        elif args.call:
            call_data = json.loads(args.call)
            result = await call_tool_on_server(
                config,
                call_data["tool"],
                call_data.get("arguments", {})
            )

            # Format result
            if isinstance(result, list):
                for item in result:
                    if hasattr(item, 'text'):
                        print(item.text)
                    else:
                        print(json.dumps(item.__dict__ if hasattr(item, '__dict__') else item, indent=2))
            else:
                print(json.dumps(result.__dict__ if hasattr(result, '__dict__') else result, indent=2))
        else:
            parser.print_help()

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
