# 📧 QQ 邮箱监控技能

> 自动监控 QQ 邮箱新邮件，支持定时检查、语音播报、邮件收发

[![ClawHub](https://img.shields.io/badge/ClawHub-Skill-blue)](https://clawhub.ai)
[![Version](https://img.shields.io/badge/version-1.0.0-green)](https://clawhub.ai/skills/qq-mail-monitor)
[![License](https://img.shields.io/badge/license-MIT-gray)](LICENSE)

---

## ✨ 特性亮点

- 🔍 **自动监控** - 定时检查新邮件，无需手动刷新
- 🔔 **实时提醒** - 发现新邮件立即通知
- 🔊 **语音播报** - TTS 播报邮件主题和发件人
- 📤 **邮件发送** - 支持纯文本和 HTML 格式
- ⏰ **灵活配置** - 可自定义检查频率
- 🔐 **安全可靠** - 使用授权码，不存储登录密码

---

## 🚀 快速开始

### 1. 安装技能

```bash
# 通过 ClawHub 安装
openclaw skill install qq-mail-monitor
```

### 2. 配置邮箱

编辑 `scripts/qq_mail_auto_check.py`：

```python
EMAIL = "你的 QQ 号@qq.com"
AUTH_CODE = "你的授权码"
```

### 3. 获取授权码

1. 登录 [QQ 邮箱](https://mail.qq.com)
2. **设置** → **账户**
3. 开启 **IMAP/SMTP 服务**
4. 生成授权码（需短信验证）

### 4. 启动监控

告诉助手：
> "启动 QQ 邮箱监控"

---

## 📖 使用指南

### 基本命令

| 命令 | 说明 |
|------|------|
| `现在检查邮件` | 立即检查一次新邮件 |
| `查看邮件列表` | 显示最近 10 封邮件 |
| `发送测试邮件` | 发送测试邮件验证功能 |
| `暂停邮件监控` | 暂时停止定时检查 |
| `恢复邮件监控` | 恢复定时检查 |
| `改成每 X 分钟检查` | 修改检查频率 |

### 高级用法

#### 读取特定邮件
> "读取 GitHub 那封验证邮件"

#### 发送邮件
> "发一封邮件到 xxx@qq.com，主题是测试，内容是你好"

#### 提取验证码
> "帮我找最新的验证码"

---

## 🔧 技术细节

### 脚本说明

| 脚本 | 用途 | 执行方式 |
|------|------|----------|
| `qq_mail_auto_check.py` | 定时监控 | cron 自动调用 |
| `qq_mail_check.py` | 查看列表 | 手动执行 |
| `qq_mail_send.py` | 发送邮件 | 手动执行 |
| `qq_mail_monitor.py` | 备用监控 | 手动执行 |

### API 端点

```python
IMAP_SERVER = "imap.qq.com"   # 收件服务器
IMAP_PORT = 993               # IMAP SSL 端口
SMTP_SERVER = "smtp.qq.com"   # 发件服务器
SMTP_PORT = 465               # SMTP SSL 端口
```

### 状态文件

`.mail_state.json` 记录已检查的邮件 ID，用于判断新邮件：

```json
{
  "latest_id": "91",
  "checked_at": 1772419200
}
```

---

## 📋 定时任务

### 默认配置

- **频率：** 每 5 分钟
- **任务类型：** systemEvent
- **通知方式：** 消息 + TTS

### 管理任务

```bash
# 查看任务
cron list

# 立即运行
cron run <jobId>

# 更新任务
cron update <jobId> --patch '{"schedule": {"everyMs": 60000}}'

# 删除任务
cron remove <jobId>
```

---

## 🎯 使用场景

### 场景 1：重要邮件提醒
```
配置频率：每 1 分钟
适用：等待重要通知、面试回复、客户邮件
```

### 场景 2：验证码自动提取
```
配置频率：每 2 分钟
适用：注册账号、登录验证、支付确认
```

### 场景 3：日报汇总
```
配置频率：每 30 分钟
适用：订阅通知、系统告警、资讯推送
```

---

## ⚠️ 注意事项

1. **授权码安全**
   - 授权码 ≠ 登录密码
   - 不要分享给他人
   - 定期更换

2. **检查频率**
   - 建议 ≥ 5 分钟
   - 过频可能触发风控

3. **网络要求**
   - 确保可访问 qq.com
   - 防火墙需放行 993/465 端口

4. **状态文件**
   - 不要手动删除 `.mail_state.json`
   - 删除后会重新检查所有邮件

---

## 🆘 故障排查

### 连接失败
```
错误：IMAP 错误：LOGIN failed
解决：检查授权码是否正确
```

### 收不到提醒
```
检查：cron list 查看任务状态
解决：cron run <jobId> 手动触发测试
```

### 重复提醒
```
原因：状态文件被删除
解决：重新运行一次脚本生成状态
```

---

## 📄 许可证

MIT License

---

## 🙏 致谢

- [OpenClaw](https://openclaw.ai) - 技能框架
- [ClawHub](https://clawhub.ai) - 技能平台
- QQ 邮箱 - 邮件服务

---

**版本：** 1.0.0  
**更新时间：** 2026-03-02  
**作者：** OpenClaw Community
