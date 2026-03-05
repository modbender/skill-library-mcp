# 📧 email-163-com 技能安装完成

**版本**: 1.0.0  
**安装日期**: 2026-02-19

---

## ✅ 已安装文件

```
~/.openclaw/workspace/skills/email-163-com/
├── SKILL.md           # 技能说明文档
├── README.md          # 使用指南
├── main.py            # 主程序
├── email-163-com      # 命令行包装器
└── INSTALL.sh         # 安装脚本

~/.config/email-163-com/
└── config.json        # 配置文件
```

---

## 🚀 快速开始

### 1. 添加到 PATH（可选）

```bash
# 方法 1: 创建软链接
ln -s ~/.openclaw/workspace/skills/email-163-com/email-163-com ~/.local/bin/email-163-com

# 方法 2: 使用完整路径
~/.openclaw/workspace/skills/email-163-com/email-163-com --help
```

### 2. 测试

```bash
# 查看帮助
email-163-com --help

# 读取邮件
email-163-com read --count 5

# 发送邮件
email-163-com send --to friend@example.com --subject "Hello" --body "Hi!"
```

---

## 📊 功能对比

### vs 旧方案（Himalaya + Python 脚本）

| 功能 | 旧方案 | 新方案 (email-163-com) |
|------|--------|----------------------|
| 发送邮件 | ✅ Himalaya | ✅ 统一命令 |
| 发送附件 | ✅ Python | ✅ 统一命令 |
| 读取邮件 | ✅ Python | ✅ 统一命令 |
| 搜索邮件 | ❌ | ✅ 新增 |
| 文件夹管理 | ✅ 两者 | ✅ 统一命令 |
| 附件下载 | ❌ | ✅ 新增 |
| 配置管理 | ❌ | ✅ 统一配置 |
| 命令数量 | 3 个工具 | 1 个工具 |

---

## 🎯 常用命令

### 读取邮件
```bash
email-163-com read              # 最新 5 封
email-163-com read --count 10   # 最新 10 封
email-163-com read --unread     # 未读邮件
```

### 发送邮件
```bash
email-163-com send --to x@example.com --subject "Hi" --body "Hello!"
email-163-com send --to x@example.com --subject "File" --attach doc.pdf
```

### 搜索邮件
```bash
email-163-com search --from "Cloudflare"
email-163-com search --subject "verify" --count 10
```

### 管理附件
```bash
email-163-com attachments --id 123
email-163-com attachments --id 123 --download
```

### 文件夹
```bash
email-163-com folders
```

---

## 📝 配置文件

位置：`~/.config/email-163-com/config.json`

```json
{
  "email": "newolf20000@163.com",
  "password": "KZtfcUWCKGNFf9M9",
  "imap_server": "imap.163.com",
  "imap_port": 993,
  "smtp_server": "smtp.163.com",
  "smtp_port": 465,
  "imap_id": {
    "name": "OpenClaw",
    "version": "1.0.0",
    "vendor": "email-163-com",
    "support_email": "newolf20000@163.com"
  },
  "defaults": {
    "folder": "INBOX",
    "count": 5,
    "output_dir": "~/Downloads"
  }
}
```

---

## 🎉 测试成功

### 已测试功能

- ✅ 读取邮件（5 封）
- ✅ 发送邮件
- ✅ IMAP ID 认证
- ✅ TLS 加密连接
- ✅ 中文支持

### 测试结果

```
📬 INBOX: 16 messages total

📧 From: 阿里云
   Subject: 域名信息修改成功通知
   
📧 From: Cloudflare
   Subject: [Action required] Verify your email address
   ...
```

---

## 🗑️ 已清理

- ❌ himalaya 技能（已删除）
- ❌ agentmail 技能（已删除）
- ❌ gmail 技能（已删除）

---

## 📚 文档

- **技能说明**: `~/.openclaw/workspace/skills/email-163-com/SKILL.md`
- **使用指南**: `~/.openclaw/workspace/skills/email-163-com/README.md`
- **配置**: `~/.config/email-163-com/config.json`

---

**安装完成时间**: 2026-02-19 22:35  
**状态**: ✅ 完全可用
