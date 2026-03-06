# 📦 发布指南 - QQ 邮箱监控技能

## 技能信息

| 项目 | 值 |
|------|-----|
| **技能名称** | qq-mail-monitor |
| **版本** | 1.0.0 |
| **描述** | QQ 邮箱自动监控，定时检查新邮件，TTS 语音播报提醒 |
| **作者** | OpenClaw Community |
| **许可证** | MIT |

---

## 📁 文件结构

```
qq-mail-monitor/
├── SKILL.md                      # 技能说明（必需）
├── README.md                     # 使用文档（必需）
├── PUBLISH.md                    # 发布指南
├── _meta.json                    # 元数据（必需）
├── requirements.txt              # 依赖列表
├── .clawhub/
│   └── origin.json               # ClawHub 注册信息
└── scripts/
    ├── qq_mail_auto_check.py     # 主脚本 ⭐
    ├── qq_mail_check.py          # 查看邮件
    ├── qq_mail_send.py           # 发送邮件
    └── qq_mail_monitor.py        # 备用监控
```

---

## 🚀 发布步骤

### 1. 本地测试

```bash
# 测试主脚本
python3 scripts/qq_mail_auto_check.py

# 测试查看邮件
python3 scripts/qq_mail_check.py

# 测试发送邮件
python3 scripts/qq_mail_send.py
```

### 2. 更新元数据

编辑 `_meta.json`：

```json
{
  "ownerId": "你的用户 ID",
  "slug": "qq-mail-monitor",
  "version": "1.0.0",
  "publishedAt": 1772419200000
}
```

### 3. 发布到 ClawHub

#### 方式 A：使用 CLI（推荐）

```bash
# 进入技能目录
cd /Users/qin/.openclaw/workspace/skills/qq-mail-monitor

# 发布技能
openclaw skill publish .
```

#### 方式 B：手动上传

1. 访问 [ClawHub 控制台](https://clawhub.ai)
2. 登录账号
3. 点击 "发布技能"
4. 上传技能目录或 ZIP 包
5. 填写技能信息
6. 提交审核

### 4. 验证发布

```bash
# 搜索技能
openclaw skill search qq-mail-monitor

# 查看技能详情
openclaw skill info qq-mail-monitor
```

---

## 📝 发布清单

发布前请确认：

- [ ] `SKILL.md` 包含完整功能说明
- [ ] `README.md` 包含使用指南
- [ ] `_meta.json` 填写正确的 ownerId 和 version
- [ ] `.clawhub/origin.json` 配置正确
- [ ] 所有脚本可以正常运行
- [ ] 代码中有清晰的中文注释
- [ ] 已移除敏感信息（邮箱、授权码等）
- [ ] `requirements.txt` 列出所有依赖

---

## 🔐 安全注意事项

### 发布前必须删除的敏感信息

```python
# ❌ 不要硬编码邮箱和授权码
EMAIL = "289688826@qq.com"        # 删除或替换为占位符
AUTH_CODE = "rnpaosialrosbgeh"    # 删除或替换为占位符

# ✅ 使用占位符
EMAIL = "your_qq_number@qq.com"
AUTH_CODE = "your_auth_code"
```

### 使用环境变量（推荐）

```python
import os

EMAIL = os.getenv("QQ_MAIL_EMAIL", "your_qq_number@qq.com")
AUTH_CODE = os.getenv("QQ_MAIL_AUTH_CODE", "your_auth_code")
```

### 创建 .env.example

```bash
# .env.example
QQ_MAIL_EMAIL=your_qq_number@qq.com
QQ_MAIL_AUTH_CODE=your_auth_code
```

---

## 📊 技能分类

建议分类标签：

```
# 主要分类
email
notification
automation

# 功能标签
qq-mail
imap
smtp
tts
cron
reminder

# 使用场景
monitoring
alert
productivity
```

---

## 🎯 推广建议

### 技能描述优化

```markdown
📧 QQ 邮箱监控技能 - 让你的邮箱会"说话"！

✨ 核心功能：
- 🔍 自动检查新邮件（可配置频率）
- 🔔 实时通知提醒
- 🔊 TTS 语音播报
- 📤 邮件发送功能

🎯 适用场景：
- 等待重要邮件（面试、客户、系统通知）
- 自动提取验证码
- 邮件日报汇总
- 自动回复

🔧 技术特点：
- 使用 IMAP/SMTP 协议
- 支持 HTML 邮件
- 状态持久化
- 定时任务集成
```

### 截图建议

1. 技能目录结构
2. 运行输出示例
3. 邮件通知效果
4. 定时任务配置

---

## 🔄 版本更新

### 语义化版本

```
主版本。次版本.修订版本
  ↑      ↑      ↑
  |      |      └─  bug 修复
  |      └─ 新功能（向下兼容）
  └─ 不兼容的重大更新
```

### 更新流程

1. 修改 `_meta.json` 中的 version
2. 更新 `SKILL.md` 和 `README.md`
3. 编写 CHANGELOG
4. 重新发布

---

## 📞 支持

遇到问题？

- 📖 文档：[ClawHub 技能开发指南](https://clawhub.ai/docs)
- 💬 社区：[OpenClaw Discord](https://discord.gg/openclaw)
- 🐛 反馈：[GitHub Issues](https://github.com/openclaw/skills/issues)

---

**最后更新：** 2026-03-02  
**维护者：** OpenClaw Community
