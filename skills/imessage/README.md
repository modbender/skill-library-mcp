# iMessage Skill

让 OpenClaw 能够通过 macOS Messages 应用发送和接收 iMessage 消息。

## 功能

- 💬 发送文本消息
- 🖼️ 发送图片
- 📨 查看最近消息
- 👥 查看联系人列表

## 安装

```bash
npx clawhub install imessage
```

## 使用

```bash
# 发送消息
python3 scripts/main.py send phone=+8613800138000 message="Hello"

# 查看最近消息
python3 scripts/main.py recent limit=10

# 查看联系人
python3 scripts/main.py contacts
```

## 要求

- macOS 10.14+
- Messages 应用
- 辅助功能权限

## 许可证

MIT
