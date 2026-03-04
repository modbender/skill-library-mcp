#!/usr/bin/env python3
"""
clawhub-login - ClawHub OAuth 登录助手（无头服务器专用）

用法:
    python3 clawhub_login.py              # 交互式登录
    python3 clawhub_login.py --get-url    # 仅获取授权 URL
    python3 clawhub_login.py --check      # 检查登录状态
    python3 clawhub_login.py --logout     # 退出登录
"""

import os
import sys
import subprocess
import json
import re
from pathlib import Path

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def log(msg, level='info'):
    colors = {
        'info': Colors.BLUE,
        'success': Colors.GREEN,
        'warn': Colors.YELLOW,
        'error': Colors.RED
    }
    prefix = {'info': 'ℹ', 'success': '✓', 'warn': '⚠', 'error': '✗'}
    print(f"{colors.get(level, '')}{prefix.get(level, 'ℹ')} {msg}{Colors.END}")

def check_login_status():
    """检查登录状态"""
    try:
        result = subprocess.run(['clawhub', 'whoami'], capture_output=True, text=True)
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, result.stderr.strip()
    except Exception as e:
        return False, str(e)

def get_auth_url():
    """获取授权 URL"""
    try:
        # 运行 clawhub login，捕获输出
        result = subprocess.run(['clawhub', 'login'], capture_output=True, text=True)
        
        # 从错误输出中提取 URL
        output = result.stderr
        url_match = re.search(r'https://clawhub\.ai/cli/auth\?[^\s]+', output)
        
        if url_match:
            return url_match.group(0)
        
        return None
    except Exception as e:
        return None

def verify_callback_url(callback_url):
    """验证回调 URL 并完成登录"""
    # 实际上 clawhub CLI 会自动处理回调
    # 这里我们只需要重新运行 clawhub login 并让它检测 token
    log("验证授权...", 'info')
    
    # 等待用户完成授权后，检查 token 文件
    token_path = Path.home() / '.clawhub' / 'token'
    
    if token_path.exists():
        log("检测到 Token 文件", 'success')
        return True
    
    return False

def interactive_login():
    """交互式登录"""
    print(f"\n{Colors.BOLD}🔐 ClawHub OAuth 登录助手{Colors.END}\n")
    
    # 检查是否已登录
    logged_in, status = check_login_status()
    if logged_in:
        log(f"已登录：{status}", 'success')
        print(f"\n{Colors.YELLOW}提示：如需重新登录，先运行 --logout{Colors.END}\n")
        return
    
    # 检测环境
    is_headless = os.environ.get('DISPLAY') is None
    if is_headless:
        log("检测到无头环境，使用手动授权模式", 'info')
    else:
        log("检测到图形环境，但仍可使用手动模式", 'info')
    
    print()
    
    # 获取授权 URL
    log("正在获取授权 URL...", 'info')
    auth_url = get_auth_url()
    
    if not auth_url:
        log("无法获取授权 URL，请手动运行 clawhub login", 'error')
        print(f"\n{Colors.YELLOW}建议：{Colors.END}")
        print("  1. 运行：clawhub login")
        print("  2. 复制输出的 URL")
        print("  3. 在浏览器打开并授权")
        print("  4. 授权后重新检查登录状态\n")
        return
    
    # 显示授权 URL
    print(f"\n{Colors.BOLD}1. 打开以下 URL（复制到本地浏览器）：{Colors.END}")
    print(f"{Colors.BLUE}{auth_url}{Colors.END}")
    print()
    
    # 提示用户操作
    print(f"{Colors.BOLD}2. 在浏览器中：{Colors.END}")
    print("   - 打开上面的 URL")
    print("   - 点击授权按钮")
    print("   - 等待页面跳转")
    print()
    
    # 等待用户完成授权
    input(f"{Colors.BOLD}3. 完成后按回车键继续...{Colors.END}")
    
    # 验证登录
    log("验证登录状态...", 'info')
    logged_in, status = check_login_status()
    
    if logged_in:
        log(f"登录成功！{status}", 'success')
        print()
        print(f"{Colors.GREEN}✅ 现在可以使用 clawhub 命令了！{Colors.END}")
        print()
        print(f"{Colors.YELLOW}下一步：{Colors.END}")
        print("  - 发布 skill: clawhub publish <path>")
        print("  - 查看技能：  clawhub search <query>")
        print()
    else:
        log("登录验证失败", 'error')
        print()
        print(f"{Colors.YELLOW}可能原因：{Colors.END}")
        print("  1. 尚未完成授权")
        print("  2. 授权已过期")
        print("  3. 网络问题")
        print()
        print(f"{Colors.YELLOW}建议：{Colors.END}")
        print("  1. 重新运行本脚本")
        print("  2. 或直接在网页上获取 API Token")
        print("  3. 使用：clawhub login --token <token>")
        print()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='ClawHub OAuth 登录助手')
    parser.add_argument('--get-url', action='store_true', help='仅获取授权 URL')
    parser.add_argument('--check', action='store_true', help='检查登录状态')
    parser.add_argument('--logout', action='store_true', help='退出登录')
    parser.add_argument('--callback', help='回调 URL（用于自动完成登录）')
    
    args = parser.parse_args()
    
    # 检查登录状态
    if args.check:
        logged_in, status = check_login_status()
        if logged_in:
            log(f"已登录：{status}", 'success')
            sys.exit(0)
        else:
            log(f"未登录：{status}", 'error')
            sys.exit(1)
    
    # 退出登录
    if args.logout:
        token_path = Path.home() / '.clawhub' / 'token'
        if token_path.exists():
            token_path.unlink()
            log("已退出登录", 'success')
        else:
            log("未找到 Token 文件", 'warn')
        sys.exit(0)
    
    # 仅获取 URL
    if args.get_url:
        auth_url = get_auth_url()
        if auth_url:
            print(auth_url)
            sys.exit(0)
        else:
            log("无法获取授权 URL", 'error')
            sys.exit(1)
    
    # 交互式登录（默认）
    interactive_login()

if __name__ == '__main__':
    main()
