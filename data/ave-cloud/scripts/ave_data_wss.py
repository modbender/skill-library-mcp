#!/usr/bin/env python3
"""AVE Cloud Data WebSocket API client CLI.

Usage: python ave_data_wss.py <command> [options]
Requires: AVE_API_KEY and API_PLAN=pro environment variables
"""

import argparse
import json
import os
import shlex
import subprocess
import sys
import threading

_dir = os.path.dirname(os.path.abspath(__file__))
if _dir not in sys.path:
    sys.path.insert(0, _dir)

from ave_data_rest import (
    get_api_key, get_api_plan, USE_DOCKER, IN_SERVER, SERVER_CONTAINER,
    SERVER_FIFO, WSS_BASE, VALID_WSS_INTERVALS, _server_is_running,
)


def _require_pro():
    if get_api_plan() != "pro":
        print("Error: WebSocket subscriptions require API_PLAN=pro.", file=sys.stderr)
        sys.exit(1)


def _require_docker():
    if not USE_DOCKER:
        print("Error: API_PLAN=pro requires AVE_USE_DOCKER=true.", file=sys.stderr)
        sys.exit(1)


def _send_to_server(line):
    result = subprocess.run(
        ["docker", "exec", SERVER_CONTAINER, "sh", "-c",
         f"echo {shlex.quote(line)} > {SERVER_FIFO}"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"Error sending to server: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    print(f"Sent. Watch events: docker logs -f {SERVER_CONTAINER}", file=sys.stderr)


def _wss_on_message(ws, message):
    try:
        print(json.dumps(json.loads(message), indent=2), flush=True)
        print("---", flush=True)
    except json.JSONDecodeError:
        print(message, flush=True)


def _wss_connect(on_open):
    _require_pro()
    try:
        import websocket
    except ImportError:
        print(
            "Error: websocket-client is not installed.\n"
            "Run: pip install -r scripts/requirements.txt",
            file=sys.stderr,
        )
        sys.exit(1)

    def on_error(ws, error):
        print(f"WebSocket error: {error}", file=sys.stderr)

    def on_close(ws, close_status_code, close_msg):
        print("\nConnection closed.", file=sys.stderr)

    ws = websocket.WebSocketApp(
        WSS_BASE,
        header={"X-API-KEY": get_api_key()},
        on_open=on_open,
        on_message=_wss_on_message,
        on_error=on_error,
        on_close=on_close,
    )
    try:
        ws.run_forever(ping_interval=30, ping_timeout=10)
    except KeyboardInterrupt:
        ws.close()


def cmd_watch_tx(args):
    def on_open(ws):
        ws.send(json.dumps({
            "jsonrpc": "2.0", "method": "subscribe",
            "params": [args.topic, args.address, args.chain], "id": 1,
        }))
    _wss_connect(on_open)


def cmd_watch_kline(args):
    def on_open(ws):
        ws.send(json.dumps({
            "jsonrpc": "2.0", "method": "subscribe",
            "params": ["kline", args.address, args.interval, args.chain], "id": 1,
        }))
    _wss_connect(on_open)


def cmd_watch_price(args):
    def on_open(ws):
        ws.send(json.dumps({
            "jsonrpc": "2.0", "method": "subscribe",
            "params": ["price", args.tokens], "id": 1,
        }))
    _wss_connect(on_open)


def cmd_wss_repl(args):
    _require_pro()
    try:
        import websocket
    except ImportError:
        print(
            "Error: websocket-client is not installed.\n"
            "Run: pip install -r scripts/requirements.txt",
            file=sys.stderr,
        )
        sys.exit(1)

    ws_ref = [None]
    connected = threading.Event()
    msg_id = [0]

    def next_id():
        msg_id[0] += 1
        return msg_id[0]

    def on_open(ws):
        ws_ref[0] = ws
        connected.set()

    def on_error(ws, error):
        print(f"\nWebSocket error: {error}", file=sys.stderr)

    def on_close(ws, close_status_code, close_msg):
        print("\nConnection closed.", file=sys.stderr)
        connected.clear()

    ws = websocket.WebSocketApp(
        WSS_BASE,
        header={"X-API-KEY": get_api_key()},
        on_open=on_open,
        on_message=_wss_on_message,
        on_error=on_error,
        on_close=on_close,
    )
    t = threading.Thread(
        target=ws.run_forever,
        kwargs={"ping_interval": 30, "ping_timeout": 10},
        daemon=True,
    )
    t.start()

    if not connected.wait(timeout=10):
        print("Error: failed to connect within 10s.", file=sys.stderr)
        sys.exit(1)

    print("Connected. Type 'help' for commands.", file=sys.stderr)

    try:
        while True:
            try:
                line = input("\n> ").strip()
            except EOFError:
                break
            if not line:
                continue
            parts = line.split()
            cmd = parts[0].lower()

            if cmd in ("quit", "exit", "q"):
                break
            elif cmd == "help":
                print(
                    "Commands:\n"
                    "  subscribe price <addr-chain> [<addr-chain> ...]\n"
                    "  subscribe tx <pair_address> <chain> [tx|multi_tx|liq]\n"
                    "  subscribe kline <pair_address> <chain> [interval]\n"
                    "  unsubscribe\n"
                    "  quit",
                    file=sys.stderr,
                )
            elif cmd == "subscribe":
                if len(parts) < 2:
                    print("Usage: subscribe <topic> [args...]", file=sys.stderr)
                    continue
                topic = parts[1]
                if topic == "price":
                    tokens = parts[2:]
                    if not tokens:
                        print("Usage: subscribe price <addr-chain> [...]", file=sys.stderr)
                        continue
                    ws_ref[0].send(json.dumps({
                        "jsonrpc": "2.0", "method": "subscribe",
                        "params": ["price", tokens], "id": next_id(),
                    }))
                elif topic in ("tx", "multi_tx", "liq"):
                    if len(parts) < 4:
                        print("Usage: subscribe tx|multi_tx|liq <pair_address> <chain>", file=sys.stderr)
                        continue
                    address, chain = parts[2], parts[3]
                    ws_ref[0].send(json.dumps({
                        "jsonrpc": "2.0", "method": "subscribe",
                        "params": [topic, address, chain], "id": next_id(),
                    }))
                elif topic == "kline":
                    if len(parts) < 4:
                        print("Usage: subscribe kline <pair_address> <chain> [interval]", file=sys.stderr)
                        continue
                    address, chain = parts[2], parts[3]
                    interval = parts[4] if len(parts) > 4 else "k60"
                    ws_ref[0].send(json.dumps({
                        "jsonrpc": "2.0", "method": "subscribe",
                        "params": ["kline", address, interval, chain], "id": next_id(),
                    }))
                else:
                    print(f"Unknown topic: {topic!r}. Topics: price, tx, multi_tx, liq, kline", file=sys.stderr)
            elif cmd == "unsubscribe":
                ws_ref[0].send(json.dumps({
                    "jsonrpc": "2.0", "method": "unsubscribe",
                    "params": [], "id": next_id(),
                }))
            else:
                print(f"Unknown command: {cmd!r}. Type 'help'.", file=sys.stderr)
    except KeyboardInterrupt:
        pass
    finally:
        ws.close()


def cmd_serve(args):
    _require_pro()
    try:
        import websocket
    except ImportError:
        print("Error: websocket-client is not installed.", file=sys.stderr)
        sys.exit(1)

    if os.path.exists(SERVER_FIFO):
        os.remove(SERVER_FIFO)
    os.mkfifo(SERVER_FIFO)

    ws_ref = [None]
    connected = threading.Event()
    msg_id = [0]

    def next_id():
        msg_id[0] += 1
        return msg_id[0]

    def on_open(ws):
        ws_ref[0] = ws
        connected.set()

    def on_error(ws, error):
        print(f"WebSocket error: {error}", file=sys.stderr, flush=True)

    def on_close(ws, code, msg):
        print("WebSocket closed.", file=sys.stderr, flush=True)
        connected.clear()

    ws = websocket.WebSocketApp(
        WSS_BASE,
        header={"X-API-KEY": get_api_key()},
        on_open=on_open,
        on_message=_wss_on_message,
        on_error=on_error,
        on_close=on_close,
    )
    t = threading.Thread(
        target=ws.run_forever,
        kwargs={"ping_interval": 30, "ping_timeout": 10},
        daemon=True,
    )
    t.start()

    if not connected.wait(timeout=10):
        print("Error: WebSocket connection timeout.", file=sys.stderr)
        sys.exit(1)

    print("Server ready.", file=sys.stderr, flush=True)

    def _process_cmd(line):
        parts = line.split()
        if not parts:
            return
        cmd = parts[0].lower()
        if cmd == "subscribe" and len(parts) >= 2:
            topic = parts[1]
            if topic == "price" and len(parts) >= 3:
                ws_ref[0].send(json.dumps({
                    "jsonrpc": "2.0", "method": "subscribe",
                    "params": ["price", parts[2:]], "id": next_id(),
                }))
            elif topic in ("tx", "multi_tx", "liq") and len(parts) >= 4:
                ws_ref[0].send(json.dumps({
                    "jsonrpc": "2.0", "method": "subscribe",
                    "params": [topic, parts[2], parts[3]], "id": next_id(),
                }))
            elif topic == "kline" and len(parts) >= 4:
                interval = parts[4] if len(parts) > 4 else "k60"
                ws_ref[0].send(json.dumps({
                    "jsonrpc": "2.0", "method": "subscribe",
                    "params": ["kline", parts[2], interval, parts[3]], "id": next_id(),
                }))
            print(f"Subscribed: {' '.join(parts[1:])}", file=sys.stderr, flush=True)
        elif cmd == "unsubscribe":
            ws_ref[0].send(json.dumps({
                "jsonrpc": "2.0", "method": "unsubscribe",
                "params": [], "id": next_id(),
            }))
            print("Unsubscribed.", file=sys.stderr, flush=True)

    try:
        while True:
            with open(SERVER_FIFO, "r") as pipe:
                for raw in pipe:
                    _process_cmd(raw.strip())
    except KeyboardInterrupt:
        ws.close()


def cmd_start_server(args):
    _require_pro()
    _require_docker()
    if _server_is_running():
        print(f"Server already running: {SERVER_CONTAINER}", file=sys.stderr)
        return
    subprocess.run(["docker", "rm", "-f", SERVER_CONTAINER], capture_output=True)
    key = get_api_key()
    result = subprocess.run([
        "docker", "run", "-d", "--name", SERVER_CONTAINER,
        "-e", f"AVE_API_KEY={key}",
        "-e", "API_PLAN=pro",
        "-e", "AVE_USE_DOCKER=true",
        "-e", "AVE_IN_SERVER=true",
        "ave-cloud", "serve",
    ], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    print(f"Started ({result.stdout.strip()[:12]}). Logs: docker logs -f {SERVER_CONTAINER}",
          file=sys.stderr)


def cmd_stop_server(args):
    result = subprocess.run(
        ["docker", "rm", "-f", SERVER_CONTAINER], capture_output=True, text=True,
    )
    if result.returncode == 0:
        print(f"Server stopped: {SERVER_CONTAINER}", file=sys.stderr)
    else:
        print(f"Error: {result.stderr}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="AVE Cloud Data WebSocket API client")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("watch-tx", help="Stream live swap/liquidity events (pro plan)")
    p.add_argument("--address", required=True)
    p.add_argument("--chain", required=True)
    p.add_argument("--topic", default="tx", choices=["tx", "multi_tx", "liq"])

    p = sub.add_parser("watch-kline", help="Stream live kline updates for a pair (pro plan)")
    p.add_argument("--address", required=True)
    p.add_argument("--chain", required=True)
    p.add_argument("--interval", default="k60", choices=list(VALID_WSS_INTERVALS))

    p = sub.add_parser("watch-price", help="Stream live price changes for tokens (pro plan)")
    p.add_argument("--tokens", required=True, nargs="+", metavar="ADDRESS-CHAIN")

    sub.add_parser("wss-repl", help="Interactive WebSocket REPL (pro plan)")
    sub.add_parser("serve", help="Run persistent WebSocket server daemon inside container (pro plan)")
    sub.add_parser("start-server", help="Start persistent server container (pro plan)")
    sub.add_parser("stop-server", help="Stop persistent server container")

    args = parser.parse_args()

    _DIRECT = {"start-server", "stop-server", "serve"}

    if get_api_plan() == "pro" and not IN_SERVER:
        _require_docker()
        if args.command not in _DIRECT:
            if not _server_is_running():
                print(
                    "Error: server not running.\n"
                    "Run: AVE_USE_DOCKER=true API_PLAN=pro AVE_API_KEY=... "
                    "python scripts/ave_data_wss.py start-server",
                    file=sys.stderr,
                )
                sys.exit(1)
            if args.command == "watch-tx":
                _send_to_server(f"subscribe {args.topic} {args.address} {args.chain}")
                return
            if args.command == "watch-kline":
                _send_to_server(f"subscribe kline {args.address} {args.chain} {args.interval}")
                return
            if args.command == "watch-price":
                _send_to_server("subscribe price " + " ".join(args.tokens))
                return
            if args.command == "wss-repl":
                r = subprocess.run(
                    ["docker", "exec", "-it", SERVER_CONTAINER,
                     "python", "scripts/ave_data_wss.py", "wss-repl"],
                )
                sys.exit(r.returncode)

    commands = {
        "watch-tx": cmd_watch_tx,
        "watch-kline": cmd_watch_kline,
        "watch-price": cmd_watch_price,
        "wss-repl": cmd_wss_repl,
        "serve": cmd_serve,
        "start-server": cmd_start_server,
        "stop-server": cmd_stop_server,
    }

    try:
        commands[args.command](args)
    except (EnvironmentError, ValueError, ImportError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
