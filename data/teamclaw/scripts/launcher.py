#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mini TimeBot 跨平台启动器
- 支持 Linux/macOS/Windows
- 精确管理子进程 PID
- 安全关闭：Ctrl+C、关窗口、kill 都能正常清理
"""

import subprocess
import sys
import os
import signal
import atexit
import time
import stat
import platform
import urllib.request
import webbrowser
from dotenv import load_dotenv

# 切换到项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)
ENV_PATH = os.path.join(PROJECT_ROOT, "config", ".env")

# 检查 .env 配置
if not os.path.exists("config/.env"):
    print("❌ 未找到 config/.env 文件，请先创建并填入 LLM_API_KEY")
    sys.exit(1)

# 加载 .env 配置
load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, "config", ".env"))

# 读取端口配置
PORT_SCHEDULER = os.getenv("PORT_SCHEDULER", "51201")
PORT_AGENT = os.getenv("PORT_AGENT", "51200")
PORT_FRONTEND = os.getenv("PORT_FRONTEND", "51209")
PORT_OASIS = os.getenv("PORT_OASIS", "51202")
PORT_BARK = os.getenv("PORT_BARK", "58010")

# 使用当前 Python 解释器（虚拟环境已由 run.sh/run.bat 激活）
venv_python = sys.executable

# Bark Server binary path
BARK_SERVER_PATH = os.path.join(PROJECT_ROOT, "bin", "bark-server")

# 子进程列表
procs = []
cleanup_done = False


def detect_bark_platform():
    """Detect platform for Bark Server binary download."""
    os_name = platform.system().lower()  # linux / darwin
    machine = platform.machine().lower()  # x86_64 / aarch64 / arm64

    if os_name not in ("linux", "darwin"):
        return None, None

    if machine in ("x86_64", "amd64"):
        arch = "amd64"
    elif machine in ("aarch64", "arm64"):
        arch = "arm64"
    else:
        return None, None

    return os_name, arch


def download_bark_server():
    """Download bark-server binary to bin/ directory."""
    os_name, arch = detect_bark_platform()
    if not os_name:
        print("⚠️  当前平台不支持自动下载 Bark Server，请手动安装")
        return False

    # Bark Server GitHub release URL (official repo: Finb/bark-server)
    url = f"https://github.com/Finb/bark-server/releases/latest/download/bark-server_{os_name}_{arch}"

    print(f"📥 正在下载 Bark Server ({os_name}/{arch})...")
    print(f"   来源: {url}")

    bin_dir = os.path.join(PROJECT_ROOT, "bin")
    os.makedirs(bin_dir, exist_ok=True)

    try:
        urllib.request.urlretrieve(url, BARK_SERVER_PATH)
        os.chmod(
            BARK_SERVER_PATH,
            os.stat(BARK_SERVER_PATH).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH,
        )
        print("✅ Bark Server 下载完成")
        return True
    except Exception as e:
        print(f"⚠️  Bark Server 下载失败: {e}")
        return False


def ensure_bark_server():
    """Ensure bark-server binary is available, download if needed."""
    if os.path.isfile(BARK_SERVER_PATH) and os.access(BARK_SERVER_PATH, os.X_OK):
        print(f"✅ 已找到 Bark Server: {BARK_SERVER_PATH}")
        return True
    print("⚠️  未找到 Bark Server，开始自动下载...")
    return download_bark_server()


PLACEHOLDER = "wait to set"


def _init_env_placeholder(key: str):
    """If the given key is missing or empty in config/.env, write 'wait to set' as placeholder."""
    current_value = os.getenv(key, "").strip()
    if current_value and current_value != PLACEHOLDER:
        # Already has a real value (e.g. set by tunnel.py), skip
        return

    # Write placeholder to .env so users know the field exists
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
    else:
        lines = []

    key_found = False
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(f"{key}=") or stripped.startswith(f"# {key}="):
            new_lines.append(f"{key}={PLACEHOLDER}\n")
            key_found = True
        else:
            new_lines.append(line)

    if not key_found:
        if new_lines and not new_lines[-1].endswith("\n"):
            new_lines.append("\n")
        new_lines.append(f"{key}={PLACEHOLDER}\n")

    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.writelines(new_lines)


def cleanup():
    """清理所有子进程"""
    global cleanup_done
    if cleanup_done:
        return
    cleanup_done = True

    print("\n🛑 正在关闭所有服务...")

    # 先发 SIGTERM（优雅关闭）
    for p in procs:
        if p.poll() is None:
            try:
                p.terminate()
            except Exception:
                pass

    # 等待进程退出（最多 5 秒）
    for _ in range(50):
        if all(p.poll() is not None for p in procs):
            break
        time.sleep(0.1)

    # 超时未退出的进程强制杀掉
    for p in procs:
        if p.poll() is None:
            try:
                print(f"⚠️  进程 {p.pid} 未响应，强制终止...")
                p.kill()
            except Exception:
                pass

    # 等待所有进程结束
    for p in procs:
        try:
            p.wait(timeout=2)
        except Exception:
            pass

    print("✅ 所有服务已关闭")


# 注册退出清理
atexit.register(cleanup)


# 信号处理
def signal_handler(signum, frame):
    sys.exit(0)  # 触发 atexit


signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # kill

# Windows 特殊处理：捕获关闭窗口事件
if sys.platform == "win32":
    try:
        import win32api
        win32api.SetConsoleCtrlHandler(lambda x: cleanup() or True, True)
    except ImportError:
        try:
            signal.signal(signal.SIGBREAK, signal_handler)
        except Exception:
            pass

print("🚀 启动 Mini TimeBot...")
print()

# --- Start Bark Server as a background process ---
bark_available = ensure_bark_server()
if bark_available:
    print(f"📱 [0/4] 启动 Bark 推送服务 (port {PORT_BARK})...")
    bark_data_dir = os.path.join(PROJECT_ROOT, "data", "bark")
    os.makedirs(bark_data_dir, exist_ok=True)
    bark_proc = subprocess.Popen(
        [BARK_SERVER_PATH, "-addr", f"127.0.0.1:{PORT_BARK}", "-data", bark_data_dir],
        cwd=PROJECT_ROOT,
        stdout=None,
        stderr=None,
    )
    procs.append(bark_proc)
    time.sleep(1)
    print(f"   ✅ Bark Server 已启动 (PID: {bark_proc.pid})")

    # If no public tunnel is configured, write placeholder to .env
    # so users know these fields exist and can set them later
    _init_env_placeholder("PUBLIC_DOMAIN")
    _init_env_placeholder("BARK_PUBLIC_URL")
else:
    print("⚠️  跳过 Bark Server 启动（二进制不可用），推送功能不可用")

# 确保 INTERNAL_TOKEN 在所有服务启动前已存在
# （mainagent 首次启动会自动生成，但 OASIS 比 mainagent 先启动，会读到空值）
if not os.getenv("INTERNAL_TOKEN"):
    import secrets, re
    _token = secrets.token_hex(32)
    with open(ENV_PATH, "r",encoding="utf-8") as f:
        content = f.read()
    if re.search(r"^INTERNAL_TOKEN=", content, re.MULTILINE):
        content = re.sub(r"^INTERNAL_TOKEN=.*$", f"INTERNAL_TOKEN={_token}", content, flags=re.MULTILINE)
    else:
        content += f"\nINTERNAL_TOKEN={_token}\n"
    with open(ENV_PATH, "w") as f:
        f.write(content)
    os.environ["INTERNAL_TOKEN"] = _token
    print(f"🔑 已自动生成 INTERNAL_TOKEN 并写入 .env")

# 服务配置：(提示信息, 脚本路径, 启动后等待秒数)
services = [
    (f"⏰ [1/5] 启动定时调度中心 (port {PORT_SCHEDULER})...", "src/time.py", 2),
    (f"🏛️ [2/5] 启动 OASIS 论坛服务 (port {PORT_OASIS})...", "oasis/server.py", 2),
    (f"🤖 [3/5] 启动 AI Agent (port {PORT_AGENT})...", "src/mainagent.py", 3),
]

# Chatbot 启动
chatbot_setup = os.path.join(PROJECT_ROOT, "chatbot", "setup.py")
if os.path.exists(chatbot_setup):
    print(f"💬 [4/5] 启动聊天机器人...")
    chatbot_dir = os.path.join(PROJECT_ROOT, "chatbot")
    subprocess.run([venv_python, "setup.py"], cwd=chatbot_dir)
    services.append((f"🌐 [5/5] 启动前端 Web UI (port {PORT_FRONTEND})...", "src/front.py", 1))
else:
    services.append((f"🌐 [4/4] 启动前端 Web UI (port {PORT_FRONTEND})...", "src/front.py", 1))

for msg, script, wait_time in services:
    print(msg)
    proc = subprocess.Popen(
        [venv_python, script],
        cwd=PROJECT_ROOT,
        stdout=None,  # 继承父进程的 stdout
        stderr=None,  # 继承父进程的 stderr
    )
    procs.append(proc)
    time.sleep(wait_time)

print()
print("============================================")
print("  ✅ Mini TimeBot 已全部启动！")
print(f"  🌐 访问: http://127.0.0.1:{PORT_FRONTEND}")
print("  按 Ctrl+C 停止所有服务")
print("============================================")
print()

# 自动打开浏览器（后台线程，避免无 GUI 环境阻塞主进程）
import threading

def _open_browser():
    url = f"http://127.0.0.1:{PORT_FRONTEND}"
    try:
        webbrowser.open(url)
        print(f"🌐 已自动打开浏览器: {url}")
    except Exception:
        print(f"⚠️  无法自动打开浏览器，请手动访问: {url}")

threading.Thread(target=_open_browser, daemon=True).start()

# 等待任意子进程退出
try:
    while True:
        for p in procs:
            if p.poll() is not None:
                print(f"⚠️ 服务 (PID {p.pid}) 异常退出，正在关闭其余服务...")
                sys.exit(1)
        time.sleep(0.5)
except KeyboardInterrupt:
    pass

sys.exit(0)
