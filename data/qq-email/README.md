# QQ Email Skill for OpenClaw

通过 QQ 邮箱 SMTP/IMAP 发送和接收邮件的 OpenClaw 技能。

## 📦 安装

技能已位于：`~/.openclaw/workspace/skills/qq-email/`

包含文件：
- `SKILL.md` - 技能说明文档
- `qq_email.py` - Python 脚本工具（发送 + 接收）

## ⚙️ 配置

### 方法 1：环境变量（推荐）

```bash
export QQ_EMAIL_ADDRESS="123456@qq.com"
export QQ_EMAIL_AUTH="abcdefghijklmnop"  # 16 位授权码
export QQ_EMAIL_SENDER="Your Name"  # 可选
```

### 方法 2：TOOLS.md 配置

编辑 `~/.openclaw/workspace/TOOLS.md`，添加：

```markdown
## QQ Email

- Email: 123456@qq.com
- Auth Code: abcdefghijklmnop
- Sender Name: Your Name
```

### 获取 QQ 邮箱授权码

1. 登录 [QQ 邮箱网页版](https://mail.qq.com)
2. 点击 **设置** → **账户**
3. 找到 **POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV 服务**
4. 开启 **IMAP/SMTP 服务**
5. 点击 **生成授权码**
6. 按提示发送短信验证
7. 复制 16 位授权码（只显示一次，请保存好！）

## 🚀 使用方法

### 发送邮件

```bash
# 发送纯文本邮件
python3 ~/.openclaw/workspace/skills/qq-email/qq_email.py send \
  -t "recipient@example.com" \
  -s "测试邮件" \
  -c "这是邮件内容"

# 发送 HTML 邮件
python3 ~/.openclaw/workspace/skills/qq-email/qq_email.py send \
  -t "recipient@example.com" \
  -s "HTML 邮件" \
  -c "<h1>你好</h1>" \
  --html

# 发送带附件的邮件
python3 ~/.openclaw/workspace/skills/qq-email/qq_email.py send \
  -t "recipient@example.com" \
  -s "文件附件" \
  -c "请查收" \
  -a "/path/to/file.pdf"
```

### 接收邮件

```bash
# 查看最近 10 封邮件
python3 ~/.openclaw/workspace/skills/qq-email/qq_email.py receive

# 查看最近 20 封邮件
python3 ~/.openclaw/workspace/skills/qq-email/qq_email.py receive --count 20

# 只查看未读邮件
python3 ~/.openclaw/workspace/skills/qq-email/qq_email.py receive --unread
```

### 读取具体邮件

```bash
# 读取指定 UID 的邮件
python3 ~/.openclaw/workspace/skills/qq-email/qq_email.py read --uid 123

# 读取并保存附件
python3 ~/.openclaw/workspace/skills/qq-email/qq_email.py read --uid 123 --save

# 标记为已读
python3 ~/.openclaw/workspace/skills/qq-email/qq_email.py mark-read --uid 123
```

### 发送 HTML 邮件

```bash
python3 ~/.openclaw/workspace/skills/qq-email/qq_email.py \
  --to "recipient@example.com" \
  --subject "HTML 邮件" \
  --content "<h1>你好</h1><p>这是 <b>HTML</b> 内容</p>" \
  --html
```

### 发送附件

```bash
python3 ~/.openclaw/workspace/skills/qq-email/qq_email.py \
  --to "recipient@example.com" \
  --subject "文件附件" \
  --content "请查收附件" \
  --attachment "/path/to/file.pdf"
```

### 群发邮件

```bash
python3 ~/.openclaw/workspace/skills/qq-email/qq_email.py \
  --to "a@example.com,b@example.com,c@example.com" \
  --subject "群发邮件" \
  --content "大家好"
```

### JSON 输出（便于程序调用）

```bash
python3 ~/.openclaw/workspace/skills/qq-email/qq_email.py \
  --to "test@example.com" \
  --subject "Test" \
  --content "Content" \
  --json

# 输出：{"success": true, "message": "Email sent successfully to 1 recipient(s)"}
```

## 📖 命令行参数

| 参数 | 简写 | 必填 | 说明 |
|------|------|------|------|
| `--to` | `-t` | ✅ | 收件人邮箱，多个用逗号分隔 |
| `--subject` | `-s` | ✅ | 邮件主题 |
| `--content` | `-c` | ✅ | 邮件内容 |
| `--html` | - | ❌ | 以 HTML 格式发送 |
| `--attachment` | `-a` | ❌ | 附件文件路径 |
| `--json` | - | ❌ | 以 JSON 格式输出结果 |

## ⚠️ 注意事项

1. **授权码 ≠ 登录密码** - 必须使用 QQ 邮箱生成的 16 位授权码
2. **发送限制** - 免费账号约 50 封/小时
3. **附件大小** - 单封邮件附件最大 50MB
4. **发送记录** - 所有邮件会保存在 QQ 邮箱"已发送"文件夹
5. **安全提示** - 授权码请妥善保管，不要提交到代码仓库

## 🐛 故障排除

### "Authentication failed"
- 检查是否使用了授权码（不是 QQ 登录密码）
- 确认 POP3/SMTP 服务已开启
- 授权码是否过期或被重置

### "Connection timed out"
- 检查网络连接
- 确认防火墙未阻止 465 端口
- 尝试增加超时时间（修改 `SMTP_TIMEOUT`）

### "Recipient address rejected"
- 检查收件人邮箱地址格式
- 确认邮箱是否存在
- QQ 邮箱可能限制发送到某些域名

## 📝 在 OpenClaw 中使用

配置完成后，你可以直接对我说：

- "给 test@example.com 发封邮件，主题是测试，内容是你好"
- "把这个文件通过邮件发送给 boss@company.com"
- "用 QQ 邮箱发个通知给团队"

我会自动调用这个技能帮你发送邮件！

## 📄 License

MIT License - 自由使用和修改
