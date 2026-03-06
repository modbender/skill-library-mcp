# openqq - QQ Bot for OpenClaw 🤖

[![ClawHub](https://img.shields.io/badge/ClawHub-openqq-blue)](https://clawhub.com/skills/openqq)
[![Version](https://img.shields.io/badge/version-0.0.3-green)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

让 OpenClaw 通过 QQ 与你互动 — 支持私聊和群聊@消息的 AI 自动回复。

---

## ✨ 特性

| 特性 | 说明 |
|------|------|
| 🚀 **快速集成** | 配置文件填写凭据即可启动 |
| 📁 **集中配置** | 所有配置在 `open-qq-config.json`，无需环境变量 |
| 💬 **双模式** | QQ 私聊 + 群聊@消息 |
| 🔐 **会话隔离** | 每个用户独立对话历史 |
| 📝 **完整日志** | 中国时区、自动轮转、敏感数据过滤 |
| 🔄 **自动重连** | WebSocket 断线自动重连 + 心跳保活 |
| 🛡️ **安全加固** | 命令注入防护、敏感数据过滤 |

---

## 🚀 快速开始

### 步骤 1: 获取 QQ 机器人凭据

访问 [QQ 开放平台](https://bot.q.qq.com/) 创建机器人，获取：
- **APP ID**
- **Token**
- **App Secret**

### 步骤 2: 安装并配置

```bash
# 进入 skill 目录
cd ~/.openclaw/workspace/skills/openqq

# 一键初始化配置
npm run setup

# 编辑配置文件
vim ~/.openclaw/workspace/open-qq-config.json
```

填写你的凭据（最小配置）：
```json
{
  "qq": {
    "appId": "你的实际 APP ID",
    "token": "你的实际 Token",
    "appSecret": "你的实际 App Secret"
  }
}
```

详细配置说明见 [CONFIG.md](skills/openqq/CONFIG.md)

### 步骤 3: 安装依赖并启动

```bash
# 安装依赖
npm install

# 启动机器人
npm start
```

看到以下输出表示成功：
```
🚀 正在启动 QQ Bot...
✅ QQ Bot 已就绪，可以接收消息了！
```

---

## 📖 使用示例

### 私聊消息

用户直接给机器人发消息：
```
用户：你好
机器人：哇啊啊～！你好呀！(≧∇≦)
```

### 群聊@消息

在群里@机器人：
```
@机器人 讲个笑话
机器人：有一天，0 遇到了 8...
```

### 会话隔离

每个用户/群组有独立会话：
- 私聊：`qq-private-{user_openid}`
- 群聊：`qq-group-{group_openid}`

---

## 🎯 常用命令

```bash
cd ~/.openclaw/workspace/skills/openqq

# 初始化配置（首次使用）
npm run setup

# 启动机器人
npm start

# 开发模式（热重载）
npm run dev

# 查看运行状态
npm run status

# 查看今日日志
npm run logs

# 健康检查
npm run health

# 测试消息（不通过 QQ）
npm run test-msg "你好"

# 查看版本
npm run version

# 清理依赖
npm run clean
```

---

## ⚙️ 配置说明

### 配置文件位置

`~/.openclaw/workspace/open-qq-config.json`

### 完整配置示例

```json
{
  "qq": {
    "appId": "YOUR_APP_ID",
    "token": "YOUR_TOKEN",
    "appSecret": "YOUR_APP_SECRET"
  },
  "logger": {
    "logLevel": "debug",
    "maxLogFiles": 7
  },
  "bot": {
    "heartbeatInterval": 30000,
    "reconnectDelay": 5000
  }
}
```

### 配置项说明

#### QQ 凭据（必需）

| 字段 | 说明 |
|------|------|
| `qq.appId` | QQ 机器人应用 ID |
| `qq.token` | QQ Bot Token |
| `qq.appSecret` | QQ 应用密钥 |

#### 日志配置（可选）

| 字段 | 默认值 | 说明 |
|------|--------|------|
| `logger.logLevel` | `debug` | `debug`/`info`/`error` |
| `logger.maxLogFiles` | `7` | 保留日志文件数 |

#### 机器人配置（可选）

| 字段 | 默认值 | 说明 |
|------|--------|------|
| `bot.heartbeatInterval` | `30000` | 心跳间隔（毫秒） |
| `bot.reconnectDelay` | `5000` | 重连延迟（毫秒） |

---

## 🔧 运维管理

### 查看日志

```bash
# 实时日志
tail -f ~/.openclaw/workspace/logs/qq-bot/qq-bot-$(date +%Y-%m-%d).log

# 调试日志
tail -f ~/.openclaw/workspace/logs/qq-bot/qq-bot-$(date +%Y-%m-%d)-debug.log

# 搜索错误
grep ERROR ~/.openclaw/workspace/logs/qq-bot/*.log
```

### 健康检查

```bash
# 使用脚本
bash scripts/health-check.sh

# 或使用命令
npm run health
```

输出示例：
```
🔍 QQ Bot 健康检查
==================
✅ 进程状态：运行中
✅ 日志文件：存在
✅ 日志更新：正常
✅ 最近错误：无
✅ 配置文件：存在
==================
✅ 健康检查完成
```

### 生产部署（systemd）

创建服务文件 `/etc/systemd/system/qq-bot.service`：

```ini
[Unit]
Description=OpenClaw QQ Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/.openclaw/workspace/skills/openqq
ExecStart=/usr/bin/node qq-bot.js
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable qq-bot
sudo systemctl start qq-bot
sudo systemctl status qq-bot
```

---

## ❓ FAQ

### Q: 机器人启动后立即断开？
**A:** 检查 Token 是否过期，每次启动会自动获取新 Token。如果持续失败，检查 QQ 开放平台的机器人配置。

### Q: 收不到消息回复？
**A:** 
1. 检查机器人是否有接收消息权限
2. 确认 QQ 开放平台的回调地址配置正确
3. 查看日志是否有错误信息

### Q: 如何查看机器人是否在运行？
**A:** 
```bash
npm run status
# 或
pgrep -f "node qq-bot.js"
```

### Q: 如何修改 AI 的人设？
**A:** 修改 OpenClaw 的 SOUL.md、IDENTITY.md 等文件，QQ 机器人会使用当前 OpenClaw 的人设。

### Q: 支持群聊非@消息吗？
**A:** 不支持。为了避免骚扰，机器人只响应私聊和群聊@消息。

### Q: 如何停止机器人？
**A:** 
```bash
# systemd 服务
sudo systemctl stop qq-bot

# 手动启动
pkill -f "node qq-bot.js"
```

### Q: 配置文件在哪里？
**A:** `~/.openclaw/workspace/open-qq-config.json`

### Q: 如何备份配置？
**A:** 备份 `open-qq-config.json` 文件即可，不要分享真实凭据。

---

## 🐛 故障排查

| 问题 | 解决方案 |
|------|----------|
| `配置文件不存在` | `npm run setup` |
| `缺少必需的 QQ 凭据` | 编辑配置文件填写凭据 |
| WebSocket 连接失败 | 检查 QQ 开放平台配置 |
| 消息无回复 | `openclaw agent --message "test"` 测试 |
| 日志不生成 | `chmod 755 ~/.openclaw/workspace/logs/qq-bot` |

---

## 🛡️ 安全

### 配置文件安全

```bash
# 设置权限
chmod 600 ~/.openclaw/workspace/open-qq-config.json

# 添加到 .gitignore
echo "open-qq-config.json" >> ~/.openclaw/workspace/.gitignore
```

### 防护机制

| 风险 | 防护措施 |
|------|----------|
| 命令注入 | 使用 `spawn` 而非 `exec` |
| 凭据泄露 | 配置文件 + 日志敏感数据过滤 |
| 路径遍历 | 会话 ID 白名单过滤 |

---

## 📦 文件结构

```
~/.openclaw/workspace/
├── open-qq-config.json         # 主配置文件
├── open-qq-config.json.example # 配置模板
└── skills/openqq/
    ├── .env.example            # 环境变量模板
    ├── .gitignore
    ├── CHANGELOG.md            # 版本历史
    ├── scripts/
    │   └── health-check.sh     # 健康检查
    ├── qq-bot.js               # 主程序
    ├── logger.js               # 日志系统
    ├── start-qq-bot.sh         # 启动脚本
    ├── package.json            # 依赖配置
    ├── README.md               # 本文档
    └── SKILL.md                # 技术文档
```

---

## 📝 更新日志

详见 [CHANGELOG.md](CHANGELOG.md)

### v0.0.3 (最新)
- ✨ 新增 7 个 npm 命令
- ✨ 添加 FAQ 章节
- ✨ Token 获取重试机制
- 🐛 修复健康检查脚本

### v0.0.2
- 代码精简 30%
- 添加健康检查脚本
- 优化文档结构

---

## 🤝 贡献

发现问题或有新功能建议？欢迎在 [ClawHub](https://clawhub.com/skills/openqq) 反馈！

---

## 🔗 相关链接

- [ClawHub 页面](https://clawhub.com/skills/openqq)
- [QQ 开放平台](https://bot.q.qq.com/)
- [OpenClaw 文档](https://docs.openclaw.ai/)
- [更新日志](CHANGELOG.md)

---

**版本：** 0.0.3 | **许可证：** MIT | **作者：** 番茄 🍅
