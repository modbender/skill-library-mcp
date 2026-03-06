# 139mail Skill 快速入门

## 🚀 5分钟快速开始

### 第1步：环境检查
```bash
python scripts/check_env.py
```

### 第2步：安装依赖
```bash
pip install imapclient
```

### 第3步：获取授权码
1. 登录 https://mail.10086.cn/
2. 设置 → 账户 → IMAP/POP3服务 → 开启
3. 复制16位授权码（**不是登录密码！**）

### 第4步：配置账号
```bash
python scripts/config_manager.py save --username 136xxxxxxxxx@139.com --password 你的授权码
```

### 第5步：查看邮件
```bash
python scripts/check_mail.py --limit 5
```

---

## 📋 常用命令速查

| 功能 | 命令 |
|------|------|
| 查看最新邮件 | `python scripts/check_mail.py --limit 5` |
| 查看未读邮件 | `python scripts/check_mail.py --unread` |
| 查看邮件详情 | `python scripts/view_mail.py <邮件ID>` |
| 发送邮件 | `python scripts/send_mail.py "收件人@example.com" "主题" "正文"` |
| 搜索邮件 | `python scripts/search_mail.py "关键词"` |
| 列出邮件 | `python scripts/manage_mail.py --list` |
| 删除邮件 | `python scripts/manage_mail.py --delete <ID>` |
| 标记已读 | `python scripts/manage_mail.py --mark-read <ID>` |

---

## ⚠️ 常见问题

### SSL握手失败
**症状**：`[SSL: SSLV3_ALERT_HANDSHAKE_FAILURE]`

**原因**：139邮箱使用较旧TLS协议，Python 3.10+默认安全策略太严格

**解决**：本skill已自动处理，如仍失败运行 `python scripts/check_env.py` 诊断

### 登录失败
- 账号格式：`136xxxxxxxxx@139.com`（不是纯手机号）
- 必须使用**授权码**，不是登录密码
- 授权码可能过期，需要重新获取

### 中文乱码
Windows终端编码问题，建议使用 VS Code 终端

---

## 📖 详细文档

参见 [SKILL.md](SKILL.md)

## 🔒 安全提示

- 配置文件保存在本地 `config/139mail.conf`
- 使用兼容模式连接（降低SSL安全级别）
- 建议在受信任网络使用
- 用完可撤销邮箱授权码
