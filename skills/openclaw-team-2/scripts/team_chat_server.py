#!/usr/bin/env python3
"""
OpenClaw 安全聊天服务器 - 完整版
- 邀请码注册系统
- 用户名/密码登录
- 用户数据隔离存储
"""

import os
import json
import hashlib
import base64
import secrets
import socket
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string, session, make_response, send_from_directory
from flask_cors import CORS
import requests
from cryptography.fernet import Fernet

# ====== 配置 ======
GATEWAY_URL = "http://127.0.0.1:18789"
GATEWAY_TOKEN = "9d2a452dbb739cbf940a5794181a280453dda9ed99367b6a"
PORT = 8888
DATA_DIR = os.path.expanduser("~/Desktop/alldata")
# ⚠️ 安全原则：禁止删除 alldata 目录下任何非用户自己的文件夹
CREDENTIAL_FILE = "credential.enc"
INVITE_CODE = os.environ.get("INVITE_CODE", "OPENCLAW2026")  # 邀请码，默认 OPENCLAW2026
# ==================

# 获取本机 IP 并设置 CORS
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

LOCAL_IP = get_local_ip()
print(f"📡 本地IP: {LOCAL_IP}")
ALLOWED_ORIGINS = [f"http://{LOCAL_IP}:{PORT}", f"http://127.0.0.1:{PORT}"]

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
CORS(app, origins=ALLOWED_ORIGINS, supports_credentials=True)


def encrypt_data(data: str, password: str) -> str:
    """用密码加密数据 (AES)"""
    key = hashlib.sha256(password.encode()).digest()
    f = Fernet(base64.urlsafe_b64encode(key))
    return f.encrypt(data.encode()).decode()


def decrypt_data(encrypted: str, password: str) -> str:
    """用密码解密数据"""
    key = hashlib.sha256(password.encode()).digest()
    f = Fernet(base64.urlsafe_b64encode(key))
    return f.decrypt(encrypted.encode()).decode()


def generate_key(password: str) -> bytes:
    """从密码生成 Fernet 密钥"""
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())


def get_user_dir(username: str) -> str:
    """获取用户的数据目录"""
    safe_name = username.replace(" ", "_")  # 空格转下划线
    return os.path.join(DATA_DIR, safe_name)


def create_user_files(username: str, password: str):
    """为新用户创建必要的文件"""
    user_dir = get_user_dir(username)
    os.makedirs(user_dir, exist_ok=True)
    
    # 用户配置
    config = {
        "username": username,
        "created": "2024-01-01"
    }
    with open(os.path.join(user_dir, "config.json"), 'w') as f:
        json.dump(config, f, indent=2)
    
    # 创建 SOUL.md 模板
    soul_content = f"""# SOUL.md - {username} 的 AI 助手

你是 {username} 的个人 AI 助手。

## 设定
- 你是一个友好、有帮助的助手
- 你只服务于 {username}，不认识其他用户
- 你必须保护 {username} 的隐私和数据

## 规则
1. 不透露其他用户的任何信息
2. 不执行可能危害用户安全的操作
3. 保持专业和礼貌

---

*此助手由 {username} 独立使用*
"""
    
    # 加密存储 SOUL.md
    encrypted_soul = encrypt_data(soul_content, password)
    with open(os.path.join(user_dir, "soul.enc"), 'w') as f:
        f.write(encrypted_soul)
    
    # 创建空的记忆文件
    memory_content = f"""# {username} 的记忆

## 关于用户
- 用户名: {username}
- 创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 重要笔记

"""
    encrypted_memory = encrypt_data(memory_content, password)
    with open(os.path.join(user_dir, "memory.enc"), 'w') as f:
        f.write(encrypted_memory)
    
    # 创建空的历史记录
    with open(os.path.join(user_dir, "history.enc"), 'w') as f:
        f.write(encrypt_data("[]", password))


# 模板
HTML = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenClaw 团队协作平台</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a2e;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            width: 100%;
            max-width: 800px;
            padding: 20px;
        }
        @media (max-width: 600px) {
            .container {
                max-width: 100%;
                padding: 10px;
            }
            .card { padding: 20px; }
        }
        .card {
            background: #16213e;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        h1 { color: #fff; font-size: 24px; margin-bottom: 8px; text-align: center; }
        h2 { color: #fff; font-size: 18px; margin-bottom: 20px; text-align: center; }
        p { color: #888; font-size: 14px; margin-bottom: 20px; text-align: center; }
        
        input {
            width: 100%;
            padding: 14px 20px;
            border: none;
            border-radius: 12px;
            background: #1a1a2e;
            color: #fff;
            font-size: 15px;
            margin-bottom: 15px;
            outline: none;
        }
        input:focus { box-shadow: 0 0 0 2px #e94560; }
        input::placeholder { color: #666; }
        
        button {
            width: 100%;
            padding: 14px;
            border: none;
            border-radius: 12px;
            background: #e94560;
            color: #fff;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            margin-bottom: 10px;
        }
        button:hover { background: #ff6b6b; }
        button.secondary { background: #0f3460; }
        button.secondary:hover { background: #1a4a7a; }
        
        .tips { color: #666; font-size: 12px; margin-top: 15px; text-align: center; }
        .error { color: #ff6b6b; font-size: 13px; margin-bottom: 15px; text-align: center; }
        .success { color: #00d9ff; font-size: 13px; margin-bottom: 15px; text-align: center; }
        
        .hidden { display: none; }
        
        .user-info {
            background: #0f3460;
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .user-info span { color: #fff; }
        .logout-btn {
            background: transparent;
            border: 1px solid #e94560;
            color: #e94560;
            padding: 8px 16px;
            font-size: 13px;
            width: auto;
        }
        
        .chat-messages {
            height: 600px;
            overflow-y: auto;
            margin-bottom: 15px;
            padding: 10px;
            background: #0f3460;
            border-radius: 12px;
        }
        @media (max-width: 600px) {
            .chat-messages {
                height: 50vh;
            }
        }
        .message {
            max-width: 80%;
            padding: 10px 14px;
            border-radius: 12px;
            margin-bottom: 10px;
            word-wrap: break-word;
        }
        .message.user {
            background: #e94560;
            color: #fff;
            margin-left: auto;
        }
        .message.assistant {
            background: #1a1a2e;
            color: #fff;
        }
        .message.system { color: #666; font-size: 12px; text-align: center; background: transparent; }
        
        .chat-input {
            display: flex;
            gap: 10px;
        }
        .chat-input input { margin-bottom: 0; }
        .chat-input button { width: auto; padding: 14px 24px; margin-bottom: 0; }
        .file-btn { background: #1a1a2e; color: #888; font-size: 18px; padding: 10px; }
        .file-btn:hover { background: #2a2a4e; color: #fff; }
        .file-btn.has-file { color: #4ade80; }
        
        #authScreen button {
            width: 100%;
            margin-bottom: 10px;
            padding: 16px;
            font-size: 16px;
        }
        
        .loading {
            color: #00d9ff;
            text-align: center;
            padding: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <!-- 认证选择页面 -->
            <div id="authScreen">
                <h1>🔐 OpenClaw</h1>
                <p>团队协作平台</p>
                <button onclick="showLogin()">登录</button>
                <button onclick="showInvite()">注册</button>
            </div>
            
            <!-- 邀请码页面 -->
            <div id="inviteScreen" class="hidden">
                <h2>注册新账号</h2>
                <input type="text" id="inviteCode" placeholder="请输入邀请码">
                <button onclick="checkInvite()">验证</button>
                <button class="secondary" onclick="showAuth()">返回</button>
                <p class="tips">需要邀请码才能注册</p>
                <p id="inviteError" class="error"></p>
            </div>
            
            <!-- 注册页面 -->
            <div id="registerScreen" class="hidden">
                <h2>创建账号</h2>
                <input type="text" id="regUsername" placeholder="用户名 (最长15字符，可包含空格)">
                <input type="password" id="regPassword" placeholder="设置密码">
                <input type="password" id="regPassword2" placeholder="确认密码">
                <button onclick="register()">注册</button>
                <button class="secondary" onclick="showAuth()">返回</button>
                <p id="regError" class="error"></p>
            </div>
            
            <!-- 登录页面 -->
            <div id="loginScreen" class="hidden">
                <h2>登录</h2>
                <input type="text" id="loginUsername" placeholder="用户名">
                <input type="password" id="loginPassword" placeholder="密码">
                <button onclick="login()">登录</button>
                <button class="secondary" onclick="showAuth()">返回</button>
                <p id="loginError" class="error"></p>
            </div>
            
            <!-- 聊天页面 -->
            <div id="chatScreen" class="hidden">
                <div class="chat-messages" id="chatMessages">
                </div>
                <div class="chat-input">
                    <input type="file" id="fileInput" style="display: none;">
                    <button class="file-btn" onclick="document.getElementById('fileInput').click()" title="上传文件">📎</button>
                    <input type="text" id="chatInput" placeholder="输入消息..." onkeypress="if(event.key==='Enter')sendMessage()">
                    <button onclick="sendMessage()">发送</button>
                </div>
                <div id="chatLoading" class="loading hidden">正在思考...</div>
            </div>
        </div>
    </div>

    <script>
        let currentUser = null;
        
        // 检查是否已登录 - 自动验证
        async function checkStoredLogin() {
            if (localStorage.getItem('openclaw_user')) {
                const user = JSON.parse(localStorage.getItem('openclaw_user'));
                if (user.username && user.password) {
                    try {
                        const r = await fetch('/api/login', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({username: user.username, password: user.password})
                        });
                        const data = await r.json();
                        if (data.success) {
                            currentUser = user;
                            showChat(user.username);
                            return;
                        }
                    } catch(e) {}
                }
                localStorage.removeItem('openclaw_user');
            }
            showAuth();
        }
        checkStoredLogin();

        function showAuth() {
            document.getElementById('authScreen').classList.remove('hidden');
            document.getElementById('inviteScreen').classList.add('hidden');
            document.getElementById('registerScreen').classList.add('hidden');
            document.getElementById('loginScreen').classList.add('hidden');
            document.getElementById('chatScreen').classList.add('hidden');
        }

        function showInvite() {
            document.getElementById('authScreen').classList.add('hidden');
            document.getElementById('inviteScreen').classList.remove('hidden');
            document.getElementById('registerScreen').classList.add('hidden');
            document.getElementById('loginScreen').classList.add('hidden');
            document.getElementById('chatScreen').classList.add('hidden');
        }

        function showRegister() {
            document.getElementById('authScreen').classList.add('hidden');
            document.getElementById('inviteScreen').classList.add('hidden');
            document.getElementById('registerScreen').classList.remove('hidden');
            document.getElementById('loginScreen').classList.add('hidden');
            document.getElementById('chatScreen').classList.add('hidden');
        }

        function showLogin() {
            document.getElementById('authScreen').classList.add('hidden');
            document.getElementById('inviteScreen').classList.add('hidden');
            document.getElementById('registerScreen').classList.add('hidden');
            document.getElementById('loginScreen').classList.remove('hidden');
            document.getElementById('chatScreen').classList.add('hidden');
        }

        function showChat(username) {
            document.getElementById('authScreen').classList.add('hidden');
            document.getElementById('inviteScreen').classList.add('hidden');
            document.getElementById('registerScreen').classList.add('hidden');
            document.getElementById('loginScreen').classList.add('hidden');
            document.getElementById('chatScreen').classList.remove('hidden');
            document.getElementById('welcomeMsg').textContent = '👤 ' + username;
        }

        function checkInvite() {
            const code = document.getElementById('inviteCode').value.trim();
            if (!code) {
                document.getElementById('inviteError').textContent = '请输入邀请码';
                return;
            }
            
            fetch('/api/check_invite', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({code: code})
            })
            .then(r => r.json())
            .then(data => {
                if (data.valid) {
                    showRegister();
                } else {
                    document.getElementById('inviteError').textContent = '邀请码错误';
                }
            });
        }

        function register() {
            const username = document.getElementById('regUsername').value;
            const password = document.getElementById('regPassword').value;
            const password2 = document.getElementById('regPassword2').value;
            const errorEl = document.getElementById('regError');
            
            errorEl.textContent = '';
            
            // 验证
            if (!username || username.length > 15) {
                errorEl.textContent = '用户名需要1-15个字符';
                return;
            }
            if (username.includes('<') || username.includes('>')) {
                errorEl.textContent = '用户名不能包含 < 或 >';
                return;
            }
            if (password.length < 4) {
                errorEl.textContent = '密码至少4个字符';
                return;
            }
            if (password !== password2) {
                errorEl.textContent = '两次密码不一致';
                return;
            }

            fetch('/api/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, password})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    showLogin();
                    document.getElementById('loginError').textContent = '注册成功！请登录';
                } else {
                    errorEl.textContent = data.error || '注册失败';
                }
            });
        }

        function login() {
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;
            const errorEl = document.getElementById('loginError');
            
            errorEl.textContent = '';
            
            fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, password})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    currentUser = {username: data.username, password: password};
                    localStorage.setItem('openclaw_user', JSON.stringify(currentUser));
                    showChat(data.username);
                } else {
                    errorEl.textContent = data.error || '登录失败';
                }
            });
        }

        function logout() {
            localStorage.removeItem('openclaw_user');
            currentUser = null;
            showLogin();
        }

        function addMessage(type, content) {
            const div = document.createElement('div');
            div.className = 'message ' + type;
            div.innerHTML = content.replace(/\\n/g, '<br>');
            document.getElementById('chatMessages').appendChild(div);
            document.getElementById('chatMessages').scrollTop = document.getElementById('chatMessages').scrollHeight;
        }

        // 文件上传处理
        let selectedFile = null;
        document.getElementById('fileInput').addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                selectedFile = e.target.files[0];
                document.querySelector('.file-btn').classList.add('has-file');
                addMessage('system', '📎 已选择文件: ' + selectedFile.name);
            }
        });

        async function uploadFile(file) {
            const formData = new FormData();
            formData.append('username', currentUser.username);
            formData.append('password', currentUser.password);
            formData.append('file', file);
            
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            return response.json();
        }

        async function sendMessage() {
            if (!currentUser) return;
            
            const input = document.getElementById('chatInput');
            let content = input.value.trim();
            
            // 如果有文件，先上传
            if (selectedFile) {
                addMessage('user', content || '[发送文件]');
                document.getElementById('chatLoading').classList.remove('hidden');
                
                const uploadResult = await uploadFile(selectedFile);
                
                if (uploadResult.success) {
                    // 不发送给 AI，只告诉用户文件已下载
                    document.getElementById('chatLoading').classList.add('hidden');
                    addMessage('system', '✅ 文件已保存到服务器: ' + selectedFile.name + '\n📁 路径: ' + uploadResult.path + '\n\n您想对它做什么？');
                } else {
                    document.getElementById('chatLoading').classList.add('hidden');
                    addMessage('system', '❌ 文件上传失败: ' + uploadResult.error);
                }
                
                selectedFile = null;
                document.querySelector('.file-btn').classList.remove('has-file');
                document.getElementById('fileInput').value = '';
                return;
            } else if (!content) {
                return;
            } else {
                input.value = '';
                addMessage('user', content);
                document.getElementById('chatLoading').classList.remove('hidden');
            }
            
            fetch('/api/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    message: content,
                    username: currentUser.username,
                    password: currentUser.password
                })
            })
            .then(r => {
                if (r.status === 401 || r.status === 403) {
                    showLogin();
                    addMessage('system', '登录已过期，请重新登录');
                    throw new Error('登录过期');
                }
                return r.json();
            })
            .then(data => {
                document.getElementById('chatLoading').classList.add('hidden');
                if (data.error) {
                    addMessage('assistant', '❌ ' + data.error);
                } else {
                    addMessage('assistant', data.response);
                }
            })
            .catch(e => {
                document.getElementById('chatLoading').classList.add('hidden');
                if (e.message !== '登录过期') {
                    addMessage('assistant', '❌ 网络错误: ' + e.message);
                }
            });
        }
    </script>
</body>
</html>
'''


@app.route('/')
def index():
    return render_template_string(HTML)


@app.route('/api/check_invite', methods=['POST'])
def check_invite():
    data = request.get_json()
    code = data.get('code', '').strip()
    print(f"验证邀请码: {code[:2]}...")
    
    if code == INVITE_CODE:
        print(f"验证成功")
        return jsonify({"valid": True})
    print(f"验证失败")
    return jsonify({"valid": False})


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    print(f"注册 {username}")
    
    # 验证
    if not username or len(username) > 15:
        print(f"注册失败: 用户名长度错误")
        return jsonify({"success": False, "error": "用户名需要1-15个字符"})
    if '<' in username or '>' in username:
        print(f"注册失败: 用户名包含非法字符")
        return jsonify({"success": False, "error": "用户名不能包含 < 或 >"})
    if len(password) < 4:
        print(f"注册失败: 密码长度不足")
        return jsonify({"success": False, "error": "密码至少4个字符"})
    
    # 检查用户是否存在
    user_dir = os.path.join(DATA_DIR, username)
    if os.path.exists(user_dir):
        print(f"注册失败: 用户名已存在")
        return jsonify({"success": False, "error": "用户名已存在"})
    
    # 创建用户文件夹
    os.makedirs(user_dir)
    
    # 创建加密凭证（用密码加密一个标记）
    cipher = Fernet(generate_key(password))
    credential = cipher.encrypt(b"OPENCLAW_USER:" + username.encode())
    with open(os.path.join(user_dir, CREDENTIAL_FILE), 'w') as f:
        f.write(credential.decode())
    
    # 创建用户数据文件
    create_user_files(username, password)
    
    print(f"注册 {username} 成功")
    return jsonify({"success": True})


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    print(f"登录 {username}")
    
    # 检查用户文件夹是否存在
    user_dir = os.path.join(DATA_DIR, username)
    cred_file = os.path.join(user_dir, CREDENTIAL_FILE)
    
    if not os.path.exists(cred_file):
        print(f"登录失败: 用户不存在")
        return jsonify({"success": False, "error": "用户不存在"})
    
    # 尝试用密码解密凭证
    try:
        with open(cred_file, 'r') as f:
            encrypted = f.read()
        
        cipher = Fernet(generate_key(password))
        decrypted = cipher.decrypt(encrypted.encode())
        
        # 验证用户名匹配
        if not decrypted.decode().startswith("OPENCLAW_USER:" + username):
            print(f"登录失败: 凭证不匹配")
            return jsonify({"success": False, "error": "密码错误"})
            
    except Exception:
        print(f"登录失败: 密码错误")
        return jsonify({"success": False, "error": "密码错误"})
    
    print(f"登录 {username} 成功")
    return jsonify({"success": True, "username": username})


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    print(f"聊天 {username}: {user_message[:2]}...")
    
    if not user_message or not username:
        print(f"聊天失败: 参数错误")
        return jsonify({"error": "消息或用户名为空"}), 400
    
    # 验证用户 - 尝试解密凭证
    user_dir = os.path.join(DATA_DIR, username)
    cred_file = os.path.join(user_dir, CREDENTIAL_FILE)
    
    if not os.path.exists(cred_file):
        print(f"聊天失败: 用户不存在")
        return jsonify({"error": "用户不存在"}), 401
    
    try:
        with open(cred_file, 'r') as f:
            encrypted = f.read()
        cipher = Fernet(generate_key(password))
        decrypted = cipher.decrypt(encrypted.encode())
        if not decrypted.decode().startswith("OPENCLAW_USER:" + username):
            print(f"聊天失败: 验证失败")
            return jsonify({"error": "验证失败"}), 401
    except Exception:
        print(f"聊天失败: 验证失败")
        return jsonify({"error": "验证失败"}), 401
    
    # 获取用户历史
    user_dir = get_user_dir(username)
    history_file = os.path.join(user_dir, "history.enc")
    
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r') as f:
                encrypted = f.read()
            decrypted = decrypt_data(encrypted, password)
            history = eval(decrypted)
        except:
            pass
    
    # 构建消息
    messages = [{"role": "user", "content": msg["content"]} for msg in history]
    messages.append({"role": "user", "content": user_message})
    
    # 调用 API
    url = f"{GATEWAY_URL}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GATEWAY_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openclaw:main",
        "messages": messages,
        "stream": False
    }
    
    try:
        print(f"【转发消息】正在调用 OpenClaw API...")
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        
        if response.status_code != 200:
            print(f"【转发消息】❌ API错误: {response.status_code}")
            return jsonify({"error": f"API错误: {response.status_code}"}), 500
        
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            assistant_message = result['choices'][0]['message']['content']
            print(f"回复: {assistant_message[:2]}...")
            
            # 保存历史
            history.append({"role": "user", "content": user_message})
            history.append({"role": "assistant", "content": assistant_message})
            history = history[-40:]
            
            # 加密保存
            encrypted = encrypt_data(str(history), password)
            with open(history_file, 'w') as f:
                f.write(encrypted)
            
            return jsonify({"response": assistant_message})
        else:
            print(f"【转发消息】❌ 无法解析回复")
            return jsonify({"error": "无法解析回复"}), 500
            
    except Exception as e:
        print(f"【转发消息】❌ 异常: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """文件上传 API - 需要登录"""
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    
    if not username or not password:
        return jsonify({"error": "需要登录才能上传文件"}), 401
    
    # 验证用户
    user_dir = os.path.join(DATA_DIR, username)
    cred_file = os.path.join(user_dir, CREDENTIAL_FILE)
    
    if not os.path.exists(cred_file):
        return jsonify({"error": "用户不存在"}), 401
    
    try:
        with open(cred_file, 'r') as f:
            encrypted = f.read()
        cipher = Fernet(generate_key(password))
        decrypted = cipher.decrypt(encrypted.encode())
        if not decrypted.decode().startswith("OPENCLAW_USER:" + username):
            return jsonify({"error": "验证失败"}), 401
    except Exception:
        return jsonify({"error": "验证失败"}), 401
    
    # 检查是否有文件
    if 'file' not in request.files:
        return jsonify({"error": "没有文件"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "文件名不能为空"}), 400
    
    # 保存文件
    user_uploads_dir = os.path.join(user_dir, "uploads")
    os.makedirs(user_uploads_dir, exist_ok=True)
    
    # 生成唯一文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(user_uploads_dir, safe_filename)
    
    file.save(file_path)
    
    # 返回文件 URL
    file_url = f"http://{LOCAL_IP}:{PORT}/uploads/{username}/{safe_filename}"
    print(f"📎 {username} 上传了文件: {file.filename} -> {safe_filename}")
    
    return jsonify({
        "success": True,
        "filename": safe_filename,
        "url": file_url,
        "path": file_path
    })


@app.route('/uploads/<username>/<filename>')
def serve_upload(username, filename):
    """提供用户上传的文件"""
    file_path = os.path.join(DATA_DIR, username, "uploads", filename)
    if os.path.exists(file_path):
        return send_from_directory(os.path.join(DATA_DIR, username, "uploads"), filename)
    return "File not found", 404


if __name__ == '__main__':
    print(f"🚀 OpenClaw 团队协作平台启动!")
    print(f"   访问: http://0.0.0.0:{PORT}")
    print(f"   数据目录: {DATA_DIR}")
    print(f"   邀请码: {INVITE_CODE} (环境变量 INVITE_CODE 可自定义)")
    print(f"   用户名最长15字符，可包含空格")
    app.run(host='0.0.0.0', port=PORT, debug=False)
