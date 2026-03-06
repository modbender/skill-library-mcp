# 更新日志

所有重要的项目更改都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [1.0.0] - 2026-03-02

### 新增 ✨

- 📧 QQ 邮箱 IMAP/SMTP 连接功能
- 🔍 新邮件自动检测
- 🔔 定时检查任务（默认每 5 分钟）
- 🔊 TTS 语音播报提醒
- 📤 邮件发送功能（纯文本 + HTML）
- 📋 邮件列表查看
- 📁 状态持久化（避免重复提醒）
- 📖 完整的中文文档

### 脚本清单

| 脚本 | 功能 |
|------|------|
| `qq_mail_auto_check.py` | 定时监控主脚本 |
| `qq_mail_check.py` | 手动查看邮件列表 |
| `qq_mail_send.py` | 发送邮件 |
| `qq_mail_monitor.py` | 备用监控脚本 |

### 技术栈

- Python 3.x（标准库）
- IMAP4_SSL（收件）
- SMTP_SSL（发件）
- OpenClaw Cron（定时任务）

### 配置说明

```python
EMAIL = "your_qq_number@qq.com"
AUTH_CODE = "your_auth_code"  # 16 位授权码
```

---

## 待发布

### 计划功能 📋

- [ ] 附件下载功能
- [ ] 邮件自动分类
- [ ] 验证码自动提取
- [ ] 多邮箱支持
- [ ] 邮件规则引擎
- [ ] Webhook 通知

---

## 版本说明

### 语义化版本

- **主版本号**：不兼容的重大更新
- **次版本号**：向下兼容的新功能
- **修订号**：向下兼容的问题修复

### 发布周期

- 小版本：每周
- 大版本：每月或按需

---

## 贡献者

- OpenClaw Community

---

**[1.0.0]**: 2026-03-02 - 初始发布
