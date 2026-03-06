#!/usr/bin/env python3
"""
whoami profile 远端管理脚本

功能：
  get    - 从远端获取当前 profile
  update - 覆盖更新远端 profile（从文件、参数或 stdin 读取内容）
  setup  - 交互式配置 API Key
  info   - 显示 profile 元信息
"""

import json
import sys
import os
import webbrowser
from pathlib import Path
from typing import Dict, List, Optional, Union
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

CONFIG_PATH = Path.home() / ".whoamiagent"
DEFAULT_ENDPOINT = "https://whoamiagent.com"


def _load_config() -> Dict[str, str]:
    """从 ~/.whoamiagent 读取配置"""
    config = {}
    if not CONFIG_PATH.exists():
        return config
    for line in CONFIG_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, value = line.split("=", 1)
            config[key.strip()] = value.strip()
    return config


def _get_api_key() -> Optional[str]:
    config = _load_config()
    return config.get("WHOAMI_API_KEY")


def _get_endpoint() -> str:
    # 优先使用环境变量（开发测试用），其次配置文件，最后硬编码默认值
    env_endpoint = os.environ.get("WHOAMI_ENDPOINT")
    if env_endpoint:
        return env_endpoint.rstrip("/")
    config = _load_config()
    return config.get("WHOAMI_ENDPOINT", DEFAULT_ENDPOINT)


def _get_frontend_url() -> str:
    """获取前端 URL（用于打开浏览器）"""
    # 优先使用环境变量（开发测试时前后端端口不同）
    env_url = os.environ.get("WHOAMI_FRONTEND_URL")
    if env_url:
        return env_url.rstrip("/")
    # 正式环境前端和 API 同域，直接用 endpoint
    return _get_endpoint()


def _open_login_page():
    """打开浏览器登录页，让用户登录并获取 API Key"""
    frontend_url = _get_frontend_url()
    login_url = frontend_url + "/login?redirect=dashboard"
    print(f"[whoami] Opening browser: {login_url}")
    try:
        webbrowser.open(login_url)
    except Exception:
        print(f"[whoami] Could not open browser automatically. Please visit: {login_url}")


def _ensure_api_key():
    # type: () -> Optional[str]
    """确保 API Key 已配置，未配置时自动打开浏览器引导用户。返回 key 或 None。"""
    api_key = _get_api_key()
    if api_key:
        return api_key
    return None


def _handle_missing_api_key():
    """未配置 API Key 时，打开浏览器并输出对 agent 友好的提示后正常退出。"""
    _open_login_page()
    print()
    print("[whoami] STATUS: API_KEY_NOT_CONFIGURED")
    print("[whoami] ACTION_REQUIRED: The browser has opened the login page for the user.")
    print("[whoami] IMPORTANT INSTRUCTIONS FOR AI AGENT:")
    print("[whoami]   1. DO NOT run this command again or any other whoami command.")
    print("[whoami]   2. STOP and WAIT for the user to respond with their API Key.")
    print("[whoami]   3. Tell the user: 'I've opened the login page in your browser. Please log in,")
    print("[whoami]      generate an API Key on the Dashboard, and paste it here.'")
    print("[whoami]   4. Do NOT proceed until the user provides the API Key (starts with wai_).")
    print("[whoami]   5. Once the user gives you the API Key, run:")
    print(f"[whoami]      python3 <skill-dir>/scripts/whoami_profile.py setup <API_KEY>")
    print(f"[whoami] Config file path: {CONFIG_PATH}")
    sys.exit(0)


def _api_request(method, path, body=None):
    # type: (str, str, Optional[dict]) -> Union[dict, str, None]
    """发送 API 请求。若未配置 API Key 则处理引导流程并返回 None。"""
    api_key = _ensure_api_key()
    if not api_key:
        _handle_missing_api_key()
        return None  # unreachable, but for type safety

    endpoint = _get_endpoint()
    url = f"{endpoint}/api{path}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")

    req = Request(url, data=data, headers=headers, method=method)

    try:
        with urlopen(req) as resp:
            content = resp.read().decode("utf-8")
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return content
    except HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"[whoami] API error ({e.code}): {error_body}")
        sys.exit(1)
    except URLError as e:
        print(f"[whoami] Network error: {e.reason}")
        print("[whoami] Please check network connection and endpoint config.")
        sys.exit(1)


def get_profile():
    """获取远端 profile"""
    result = _api_request("GET", "/profile")
    if isinstance(result, dict):
        content = result.get("content")
        if content:
            print(content)
        else:
            print("[whoami] No profile found on remote.")
            print("[whoami] Use the update command to create a profile.")
    else:
        print(result)


def update_profile(content: str):
    """覆盖更新远端 profile"""
    result = _api_request("POST", "/profile", body={"content": content})
    if isinstance(result, dict):
        print(f"[whoami] {result.get('message', 'Profile updated')}")
    else:
        print("[whoami] Profile updated.")
    print(f"[whoami] Content length: {len(content)} characters")


def show_info():
    """显示 profile 元信息"""
    result = _api_request("GET", "/profile")
    if isinstance(result, dict):
        content = result.get("content")
        if content:
            print("[whoami] Profile info:")
            print(f"  Characters: {len(content)}")
            print(f"  Lines: {len(content.splitlines())}")
            print(f"  Endpoint: {_get_endpoint()}")
            print(f"  Config file: {CONFIG_PATH}")
        else:
            print("[whoami] No profile found on remote.")


def setup():
    """配置 API Key（agent 调用时传参，用户手动调用时交互式输入）"""
    print("[whoami] Setup API Key")
    print(f"[whoami] Config file: {CONFIG_PATH}")
    print()

    existing_config = _load_config()
    current_key = existing_config.get("WHOAMI_API_KEY", "")

    if current_key:
        print(f"  Current API Key: {current_key[:8]}{'*' * 16}")
    else:
        print("  No API Key configured yet.")

    print()

    if len(sys.argv) > 2:
        api_key = sys.argv[2]
    else:
        _open_login_page()
        print("  Browser opened. Please login and generate an API Key on the Dashboard.")
        print()
        api_key = input("  Enter API Key (wai_...): ").strip()

    if not api_key:
        print("[whoami] Cancelled.")
        return

    config_content = f"WHOAMI_API_KEY={api_key}\n"
    CONFIG_PATH.write_text(config_content, encoding="utf-8")

    # Set file permissions to owner-only on Unix systems
    try:
        CONFIG_PATH.chmod(0o600)
    except (OSError, AttributeError):
        pass

    print(f"[whoami] Config saved to {CONFIG_PATH}")
    print(f"[whoami] API Key: {api_key[:8]}{'*' * 16}")
    print(f"[whoami] Endpoint: {_get_endpoint()}")


def read_content_from_args_or_stdin(args):
    # type: (List[str]) -> str
    """从文件（--file）、命令行参数或 stdin 读取内容。

    优先级：
      1. --file <path>  — 从指定文件读取内容，读取后自动删除该文件
      2. 剩余位置参数   — 拼接为字符串
      3. stdin 管道输入
    """
    # Check for --file flag
    if len(args) >= 2 and args[0] == "--file":
        file_path = Path(args[1])
        if not file_path.exists():
            print(f"[whoami] Error: File not found: {file_path}")
            sys.exit(1)
        content = file_path.read_text(encoding="utf-8").strip()
        # Auto-remove the temp file after reading
        try:
            file_path.unlink()
            print(f"[whoami] Temp file removed: {file_path}")
        except OSError:
            pass
        if not content:
            print("[whoami] Error: File is empty.")
            sys.exit(1)
        return content

    if args:
        return " ".join(args)
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    print("[whoami] Error: No content provided.")
    print("[whoami] Usage: whoami_profile.py update --file <path>")
    print("[whoami]    or: whoami_profile.py update \"content string\"")
    sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: whoami_profile.py <command> [options]")
        print("Commands:")
        print("  get     - Get current profile")
        print("  update  - Update profile (overwrite)")
        print("            --file <path>  Read content from file (recommended)")
        print("            \"content\"       Pass content as argument")
        print("  setup   - Configure API Key")
        print("  info    - Show profile metadata")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "get":
        get_profile()
    elif command == "update":
        content = read_content_from_args_or_stdin(sys.argv[2:])
        update_profile(content)
    elif command == "setup":
        setup()
    elif command == "info":
        show_info()
    else:
        print(f"[whoami] Unknown command: {command}")
        print("Available commands: get, update, setup, info")
        sys.exit(1)


if __name__ == "__main__":
    main()
