#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import contextlib
import socket
import sys
import threading
import time
import traceback
import urllib.request
import uuid
from http.server import ThreadingHTTPServer
from pathlib import Path

import run_nonuse_webui as webui
from utils.logger import audit, set_run_context, setup_logger

LOGGER = setup_logger(__name__, log_dir=(Path(__file__).resolve().parent / "logs"))


def find_free_port(host: str, start: int = 18765, max_tries: int = 200) -> int:
    for port in range(start, start + max_tries):
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind((host, port))
                return port
            except OSError:
                continue
    raise RuntimeError("未找到可用端口，请稍后重试。")


def wait_ping(url: str, timeout: float = 15.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=0.8) as r:
                body = r.read().decode("utf-8", errors="ignore")
                if '"ok": true' in body:
                    return True
        except Exception as exc:
            LOGGER.exception("桌面版健康检查失败（继续重试）")
            audit({
                "type": "exception",
                "step": "wait_ping",
                "file": url,
                "error": str(exc),
                "traceback": traceback.format_exc(),
                "ok": False,
                "reason_code": "desktop_ping_retry",
            })
        time.sleep(0.2)
    return False


class ServerThread(threading.Thread):
    def __init__(self, host: str, port: int):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.server: ThreadingHTTPServer | None = None
        self.error: Exception | None = None

    def run(self) -> None:
        try:
            self.server = ThreadingHTTPServer((self.host, self.port), webui.Handler)
            self.server.serve_forever()
        except Exception as exc:  # pragma: no cover
            self.error = exc
            LOGGER.exception("桌面版服务线程异常")
            audit({
                "type": "exception",
                "step": "server_thread_run",
                "file": f"{self.host}:{self.port}",
                "error": str(exc),
                "traceback": traceback.format_exc(),
                "ok": False,
                "reason_code": "desktop_server_thread_failed",
            })

    def shutdown(self) -> None:
        if self.server is not None:
            self.server.shutdown()
            self.server.server_close()


def main() -> None:
    run_id = f"desktop_{uuid.uuid4().hex[:8]}"
    logs_dir = Path(getattr(webui, "BASE_DIR", Path(__file__).resolve().parent)) / "logs"
    set_run_context(logs_dir, run_id)
    global LOGGER
    LOGGER = setup_logger(__name__, log_dir=logs_dir)
    rc = 1
    audit({
        "type": "run_start",
        "step": "main",
        "ok": True,
        "run_mode": "desktop_app",
    })
    ap = argparse.ArgumentParser(description="撤三证据智审系统（独立窗口版）")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=0, help="0 表示自动分配可用端口")
    ap.add_argument("--title", default="撤三证据智审系统")
    ap.add_argument("--width", type=int, default=1320)
    ap.add_argument("--height", type=int, default=860)
    ap.add_argument("--self-test", action="store_true", help="仅测试服务启动与 ping，不打开窗口")
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()

    try:
        host = args.host
        port = args.port if args.port > 0 else find_free_port(host, start=webui.DEFAULT_PORT)
        base_url = f"http://{host}:{port}/"
        ping_url = f"http://{host}:{port}/api/ping"

        srv = ServerThread(host, port)
        srv.start()

        if not wait_ping(ping_url, timeout=18.0):
            srv.shutdown()
            if srv.error:
                raise RuntimeError(f"服务启动失败：{srv.error}") from srv.error
            raise RuntimeError("服务启动超时，请重试。")

        if args.self_test:
            print(f"SELF_TEST_OK {base_url}")
            srv.shutdown()
            rc = 0
            return

        try:
            import webview  # pywebview
        except Exception as exc:  # pragma: no cover
            srv.shutdown()
            LOGGER.exception("加载 pywebview 失败")
            audit({
                "type": "exception",
                "step": "import_pywebview",
                "file": "pywebview",
                "error": str(exc),
                "traceback": traceback.format_exc(),
                "ok": False,
                "reason_code": "desktop_pywebview_missing",
            })
            raise RuntimeError("缺少 pywebview 依赖，无法打开独立窗口。") from exc

        window = webview.create_window(
            args.title,
            base_url,
            width=args.width,
            height=args.height,
            min_size=(1120, 740),
            background_color="#F4F8FF",
        )
        try:
            webview.start(debug=args.debug, gui="cocoa", http_server=False)
        finally:
            srv.shutdown()
            _ = window
        rc = 0
    except Exception as exc:
        LOGGER.exception("桌面版主流程异常")
        audit({
            "type": "exception",
            "step": "main",
            "file": __file__,
            "error": str(exc),
            "traceback": traceback.format_exc(),
            "ok": False,
            "reason_code": "desktop_main_failed",
        })
        raise
    finally:
        audit({
            "type": "run_end",
            "step": "main",
            "ok": rc == 0,
            "exit_code": rc,
        })


if __name__ == "__main__":
    main()
