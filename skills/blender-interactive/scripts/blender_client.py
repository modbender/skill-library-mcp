#!/usr/bin/env python3
"""
Blender Socket Client — 소켓 서버에 명령 전송.

사용법:
  # 단일 명령
  python3 blender_client.py ping
  python3 blender_client.py get_scene_info
  python3 blender_client.py create_object --params '{"type":"SPHERE","name":"MySphere","location":[0,0,2]}'
  python3 blender_client.py execute_code --params '{"code":"import bpy; print(len(bpy.data.objects))"}'

  # 파이프라인 (stdin에서 JSON 명령 읽기)
  echo '{"type":"ping"}' | python3 blender_client.py --stdin

  # 서버 주소 변경
  python3 blender_client.py ping --host 127.0.0.1 --port 9876
"""

import socket
import json
import sys
import argparse
import time


def send_command(host, port, command, timeout=300):
    """소켓 서버에 명령 전송 후 결과 수신"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)

    try:
        sock.connect((host, port))
        payload = json.dumps(command, ensure_ascii=False).encode("utf-8")
        sock.sendall(payload)

        # 응답 수신 — JSON 완성까지 누적
        buf = b""
        while True:
            chunk = sock.recv(16384)
            if not chunk:
                break
            buf += chunk

            try:
                result = json.loads(buf.decode("utf-8"))
                return result
            except json.JSONDecodeError:
                continue

        # 연결 닫힘
        if buf:
            return json.loads(buf.decode("utf-8"))
        return {"status": "error", "message": "No response received"}

    except socket.timeout:
        return {"status": "error", "message": "Connection timeout"}
    except ConnectionRefusedError:
        return {"status": "error", "message": f"Connection refused at {host}:{port}. Is the Blender server running?"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
    finally:
        sock.close()


def main():
    parser = argparse.ArgumentParser(description="Blender Socket Client")
    parser.add_argument("command", nargs="?", help="Command type (e.g. ping, get_scene_info)")
    parser.add_argument("--params", default="{}", help="JSON params string")
    parser.add_argument("--host", default="127.0.0.1", help="Server host")
    parser.add_argument("--port", type=int, default=9876, help="Server port")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout seconds")
    parser.add_argument("--stdin", action="store_true", help="Read JSON command from stdin")
    parser.add_argument("--pretty", action="store_true", help="Pretty print output")

    args = parser.parse_args()

    if args.stdin:
        # stdin에서 JSON 명령 읽기
        raw = sys.stdin.read().strip()
        command = json.loads(raw)
    elif args.command:
        params = json.loads(args.params)
        command = {"type": args.command, "params": params}
    else:
        parser.print_help()
        sys.exit(1)

    result = send_command(args.host, args.port, command, args.timeout)

    if args.pretty:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(result, ensure_ascii=False))

    # 에러면 exit code 1
    if result.get("status") == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
