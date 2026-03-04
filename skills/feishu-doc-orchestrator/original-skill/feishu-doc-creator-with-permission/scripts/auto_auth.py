#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书自动化授权脚本
自动启动本地服务器接收 OAuth 回调，无需手动复制授权码
"""

import requests
import json
import time
import webbrowser
import secrets
import urllib.parse
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from pathlib import Path

# 全局变量存储授权码
auth_code = None
server_running = True

class CallbackHandler(BaseHTTPRequestHandler):
    """处理 OAuth 回调"""

    def do_GET(self):
        global auth_code, server_running

        # 解析查询参数
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)

        # 检查错误
        if 'error' in query_params:
            error = query_params['error'][0]
            self.send_response(400)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(f"""
            <html><head><title>授权失败</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: red;">授权失败</h1>
                <p>错误: {error}</p>
                <p>请检查授权 URL 中的权限范围是否正确</p>
            </body></html>
            """.encode('utf-8'))
            auth_code = f"ERROR: {error}"
            server_running = False
            return

        # 获取授权码
        if 'code' in query_params:
            auth_code = query_params['code'][0]
            print(f"[OK] 收到授权码: {auth_code[:20]}...")

            # 返回成功页面
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write("""
            <html><head><title>授权成功</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: green;">授权成功！</h1>
                <p>您可以关闭此页面并返回终端查看结果。</p>
                <script>window.close();</script>
            </body></html>
            """.encode('utf-8'))
            server_running = False
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write("""
            <html><head><title>错误</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1>错误</h1>
                <p>未收到授权码</p>
            </body></html>
            """.encode('utf-8'))

    def log_message(self, format, *args):
        """禁用日志输出"""
        pass


def start_oauth_server(port=8080):
    """启动本地 HTTP 服务器接收回调"""
    global server_running
    server_running = True
    server = HTTPServer(('localhost', port), CallbackHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def load_config():
    """加载配置文件"""
    # 获取项目根目录 - 从脚本位置向上找到项目根目录
    project_root = Path(__file__).parent.parent.parent.parent.parent
    config_path = project_root / ".claude" / "feishu-config.env"

    if not config_path.exists():
        config_path = Path(".claude/feishu-config.env")

    config = {}
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip().strip('"\'')
    return config


def get_token_with_code(code, config):
    """使用授权码获取 token"""
    redirect_uri = config.get('FEISHU_OAUTH_REDIRECT_URI', 'http://localhost:8080/callback')

    url = f"{config['FEISHU_API_DOMAIN']}/open-apis/authen/v2/oauth/token"
    payload = {
        'grant_type': 'authorization_code',
        'client_id': config['FEISHU_APP_ID'],
        'client_secret': config['FEISHU_APP_SECRET'],
        'code': code,
        'redirect_uri': redirect_uri
    }

    print(f"[INFO] 正在获取 user_access_token...")
    response = requests.post(url, json=payload, timeout=30)
    result = response.json()

    if result.get('code') != 0:
        raise Exception(f"获取 token 失败: {result}")

    return result


def save_token(token_data):
    """保存 token 到文件"""
    # 获取项目根目录 - 从脚本位置向上找到项目根目录
    # 脚本位置: .claude/skills/feishu-doc-creator-with-permission/scripts/auto_auth.py
    # 项目根目录需要向上 5 级
    project_root = Path(__file__).parent.parent.parent.parent.parent
    token_path = project_root / ".claude" / "feishu-token.json"

    expires_in = token_data.get('expires_in', 7200)
    refresh_expires_in = token_data.get('refresh_token_expires_in', 604800)

    data = {
        'access_token': token_data.get('access_token'),
        'user_access_token': token_data.get('access_token'),
        'refresh_token': token_data.get('refresh_token'),
        'expires_at': int(time.time()) + expires_in,
        'refresh_expires_at': int(time.time()) + refresh_expires_in,
        'scope': token_data.get('scope', ''),
        'token_type': token_data.get('token_type', 'Bearer')
    }

    with open(token_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] Token 已保存到: {token_path}")
    return data


def auto_authorize():
    """自动完成 OAuth 授权流程"""
    global auth_code, server_running

    print("=" * 70)
    print("飞书自动化授权")
    print("=" * 70)
    print()

    # 加载配置
    config = load_config()
    if not config:
        print("[FAIL] 无法加载配置文件")
        return None

    # 生成授权 URL
    # 正确的权限范围 - 不包含 drive:drive.permission（会报错 20043）
    scope = 'drive:drive docs:doc docx:document docs:permission.member:create offline_access'
    state = secrets.token_urlsafe(16)
    redirect_uri = config.get('FEISHU_OAUTH_REDIRECT_URI', 'http://localhost:8080/callback')
    port = int(redirect_uri.split(':')[-1].split('/')[0])

    auth_url = (
        f"https://accounts.feishu.cn/open-apis/authen/v1/authorize?"
        f"client_id={config['FEISHU_APP_ID']}"
        f"&redirect_uri={urllib.parse.quote(redirect_uri)}"
        f"&scope={urllib.parse.quote(scope)}"
        f"&response_type=code"
        f"&state={state}"
    )

    # 启动本地服务器
    print(f"[INFO] 启动本地回调服务器: {redirect_uri}")
    server = start_oauth_server(port)

    # 打开浏览器
    print("[INFO] 正在打开浏览器...")
    print()
    try:
        webbrowser.open(auth_url)
        print("[OK] 浏览器已打开授权页面")
    except Exception as e:
        print(f"[WARN] 无法自动打开浏览器: {e}")
        print()
        print("请手动复制以下 URL 到浏览器:")
        print()
        print(auth_url)
        print()

    print()
    print("=" * 70)
    print("等待用户授权...")
    print("=" * 70)
    print("请在浏览器中完成授权（点击同意按钮）")
    print("完成后将自动接收授权码...")
    print()

    # 等待授权码（最多 5 分钟）
    max_wait = 300
    start_time = time.time()
    while server_running and (time.time() - start_time) < max_wait:
        time.sleep(1)

    # 关闭服务器
    server.shutdown()

    if not auth_code or auth_code.startswith("ERROR"):
        print()
        print("[FAIL] 授权失败或超时")
        return None

    print()
    print("[OK] 授权码接收成功")

    # 获取 token
    try:
        token_result = get_token_with_code(auth_code, config)
        token_data = save_token(token_result)

        print()
        print("=" * 70)
        print("授权成功！")
        print("=" * 70)
        print(f"Access Token: {token_data['access_token'][:30]}...")
        print(f"有效期: {token_data['expires_at'] - int(time.time())} 秒")
        print(f"权限范围: {token_data['scope']}")
        print()

        return token_data

    except Exception as e:
        print()
        print(f"[FAIL] 获取 token 失败: {e}")
        return None


if __name__ == "__main__":
    result = auto_authorize()
    if result:
        print("[SUCCESS] 授权完成，现在可以使用 user_access_token 了")
        sys.exit(0)
    else:
        print("[FAIL] 授权失败")
        sys.exit(1)
