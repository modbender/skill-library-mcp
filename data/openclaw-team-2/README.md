# OpenClaw Team - 零知识团队协作服务器

[English version below]

## 背景

适用于部署一个 OpenClaw 实例，但可以多人共同使用——每个用户拥有独立的加密存储空间，实现真正的数据隔离。

## 特性

- 🔐 **零知识架构**：服务器不存储任何密码数据，用户数据只能用正确密码解密
- 👥 **多用户数据隔离**：每个用户独立文件夹，AES-256 加密，密码即密钥
- 📱 **跨设备访问**：支持电脑和手机通过局域网 IP 访问
- 🛡️ **端到端加密**：所有用户数据（历史、记忆、灵魂）在传输和存储全程加密
- 🔑 **设备绑定登录**：无需会话 Token，登录状态保存在浏览器 localStorage
- ⚡ **轻量部署**：无需数据库，一个 Python 脚本即可运行

## 适用场景

- **家庭共享**：一家人共用一个 OpenClaw 实例，各自拥有独立对话历史
- **团队协作**：小团队共享 AI 助手，每个人的数据和配置完全隔离
- **隐私敏感**：对数据安全有要求，不想让管理员或服务器运营方看到任何用户数据

## 技术亮点

### 1. 零知识认证（Zero-Knowledge）

传统方案：服务器存储密码 hash，登录时比对。

**本方案**：
- 服务器**不存储**任何密码相关数据
- 注册时：用密码加密生成 `credential.enc`（包含用户身份证明）
- 登录时：服务器尝试用提交的密码解密 `credential.enc`
- 解开 → 证明密码正确；解不开 → 登录失败

即使服务器被攻破、数据库被拖走，攻击者也无法恢复任何用户密码或解密数据。

### 2. 密码即密钥

用户的密码同时用于：
- 身份验证（解密 credential.enc）
- 数据加密（加密 history.enc、memory.enc、soul.enc）

密码丢失 = 数据永久丢失。这是特性，不是 bug——确保了**只有用户自己**能访问自己的数据。

### 3. 数据隔离

```
~/Desktop/alldata/
├── .protected          # 保护标记，防止误删
├── alice/             # Alice 的数据
│   ├── credential.enc
│   ├── config.json
│   ├── soul.enc
│   ├── memory.enc
│   └── history.enc
└── bob/               # Bob 的数据
    ├── credential.enc
    ├── config.json
    ├── soul.enc
    ├── memory.enc
    └── history.enc
```

每个文件夹只能被对应密码解密，Bob 无法读取 Alice 的任何文件。

### 4. 第一原则约束

代码中内置安全注释：
```python
# ⚠️ 安全原则：禁止删除 alldata 目录下任何非用户自己的文件夹
```

AI 助手不会执行任何删除他人数据的指令。

## 快速开始

### 方式 1: 使用启动脚本（推荐）

```bash
# 一键启动（自动创建虚拟环境、安装依赖、启动服务）
./start.sh
```

### 方式 2: 手动启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动服务器（使用 main.py）
cd scripts
python3 main.py

# 或使用 gunicorn（推荐生产环境）
gunicorn -w 4 -b 0.0.0.0:8888 main:app
```

访问: `http://<你的IP>:8888`

默认邀请码: `OPENCLAW2026`  
默认品牌名: `OPENCLAW-TEAM`

## 自定义配置

### 方式 1: 环境变量

```bash
# 自定义邀请码和品牌名称
INVITE_CODE=你的邀请码 BRAND_NAME=你的品牌名 python3 main.py

# 使用 gunicorn
INVITE_CODE=你的邀请码 BRAND_NAME=你的品牌名 gunicorn -w 4 -b 0.0.0.0:8888 main:app
```

### 方式 2: 修改代码

直接编辑 `scripts/main.py` 中的配置常量：
- `INVITE_CODE`: 注册邀请码
- `BRAND_NAME`: 品牌名称（显示在界面上）
- `PORT`: 服务器端口
- `DATA_DIR`: 数据存储目录
- `GATEWAY_URL`: OpenClaw Gateway API 地址
- `GATEWAY_TOKEN`: Gateway 认证令牌

## 配置

| 变量 | 默认值 | 说明 |
|------|--------|------|
| PORT | 8888 | 服务器端口 |
| INVITE_CODE | OPENCLAW2026 | 注册邀请码（环境变量可自定义） |
| BRAND_NAME | OPENCLAW-TEAM | 品牌名称（环境变量可自定义） |
| DATA_DIR | ~/Desktop/alldata | 数据存储目录 |
| GATEWAY_URL | http://127.0.0.1:18789 | OpenClaw Gateway API |
| GATEWAY_TOKEN | (配置中获取) | Gateway 认证令牌 |

## 与传统方案对比

| 特性 | 传统方案 | OpenClaw Team |
|------|----------|---------------|
| 密码存储 | 服务器存 hash | 服务器不存任何密码数据 |
| 数据隔离 | 管理员可查看 | 只有用户自己能解密 |
| 会话管理 | Token 有过期时间 | 设备绑定，永不过期 |
| 数据恢复 | 管理员可重置 | 密码丢失 = 数据丢失 |

## 技术栈

- Flask + Gunicorn
- Cryptography (Fernet/AES-256)
- 零知识认证架构
- PBKDF2 密钥派生

## 项目结构

```
openclaw-team/
├── scripts/
│   ├── main.py              # 主服务器文件（推荐使用）
│   ├── index.html           # 前端界面
│   ├── upload.py            # 文件上传模块
│   └── team_chat_server.py  # 独立完整版（备用）
├── requirements.txt         # Python 依赖
├── start.sh                # 一键启动脚本
├── .env.example            # 环境变量示例
├── .gitignore              # Git 忽略配置
├── README.md               # 项目文档
├── SKILL.md                # Skill 描述
└── license.txt             # 许可证
```

## 文件说明

- **main.py**: 模块化主服务器，使用独立的 HTML 文件和 upload 模块
- **index.html**: 白色极简风格前端界面
- **upload.py**: 文件上传功能模块
- **team_chat_server.py**: 独立完整版服务器（所有代码在一个文件，备用）

## 许可证

Apache License 2.0

---

# OpenClaw Team - Zero-Knowledge Team Collaboration Server

## Background

Designed for deploying a single OpenClaw instance that multiple users can share—each user gets isolated encrypted storage, achieving true data separation.

## Features

- 🔐 **Zero-knowledge**: Server never stores any password data; user data can only be decrypted with correct password
- 👥 **Data isolation**: Each user has independent folder with AES-256 encryption, password is the key
- 📱 **Cross-device**: Access via LAN IP from desktop or mobile
- 🛡️ **End-to-end encrypted**: All user data (history, memory, soul) encrypted in transit and at rest
- 🔑 **Device-based login**: No session tokens; login state stored in browser localStorage
- ⚡ **Lightweight**: No database needed; runs with a single Python script

## Use Cases

- **Family sharing**: Family shares one OpenClaw instance, each with independent conversation history
- **Team collaboration**: Small teams share AI assistant with complete data isolation per user
- **Privacy-sensitive**: High security requirements—neither admins nor server operators can see any user data

## Technical Highlights

### 1. Zero-Knowledge Architecture

Traditional approach: Server stores password hash, compares on login.

**This solution**:
- Server stores **nothing** password-related
- Registration: Encrypt `credential.enc` (contains user identity proof) using password
- Login: Server attempts to decrypt `credential.enc` with provided password
- Decrypt success → password verified; decrypt fail → login failed

Even if server is compromised and database stolen, attackers cannot recover any passwords or decrypt user data.

### 2. Password is the Key

User's password is used for:
- Authentication (decrypt credential.enc)
- Data encryption (encrypt history.enc, memory.enc, soul.enc)

Password lost = data permanently lost. This is a feature, not a bug—ensures **only the user** can access their own data.

### 3. Data Isolation

Each folder can only be decrypted with corresponding password—users cannot read each other's files.

### 4. First Principle Restriction

Security comment embedded in code:
```python
# Security principle: Never delete any folder in alldata except user's own folder
```

AI assistant will not execute any command to delete other users' data.

## Quick Start

```bash
# 1. Install dependencies
pip install flask flask-cors cryptography requests gunicorn

# 2. Start server
gunicorn -w 4 -b 0.0.0.0:8888 team_chat_server:app
```

Access at: `http://<your-ip>:8888`

Default invite code: `OPENCLAW2026`

## Custom Invite Code

```bash
# Option 1: Environment variable
INVITE_CODE=your_code gunicorn -w 4 -b 0.0.0.0:8888 team_chat_server:app

# Option 2: Edit INVITE_CODE constant in the script
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| PORT | 8888 | Server port |
| INVITE_CODE | OPENCLAW2026 | Invite code for registration |
| DATA_DIR | ~/Desktop/alldata | Data storage directory |
| GATEWAY_URL | http://127.0.0.1:18789 | OpenClaw Gateway API |
| GATEWAY_TOKEN | (from config) | Gateway auth token |

## Comparison with Traditional Solutions

| Feature | Traditional | OpenClaw Team |
|---------|-------------|---------------|
| Password storage | Server stores hash | Server stores nothing password-related |
| Data isolation | Admins can view | Only user can decrypt |
| Session management | Token expires | Device-based, never expires |
| Data recovery | Admin can reset | Password lost = data lost |

## Tech Stack

- Flask + Gunicorn
- Cryptography (Fernet/AES-256)
- Zero-knowledge architecture
- PBKDF2 key derivation

## License

Apache License 2.0
