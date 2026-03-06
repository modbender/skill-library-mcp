---
name: mailme-x-news
description: 抓取 X/Twitter 帖子，通过 AI 翻译成中文，并发送邮件。完全通过技能控制，无需额外脚本。
---

# MailMe X News

抓取 X/Twitter 帖子，通过 AI 翻译成中文，生成综述，并发送邮件。

## 配置

创建配置文件 `config.json`（与 SKILL.md 同目录）：

```json
{
  "to": "chenguangming@gd.chinamobile.com",
  "cc": "fanliang@gd.chinamobile.com"
}
```

- **to**: 主收件人（必填）
- **cc**: 抄送人（可选）

## 前置要求

1. **crawl-from-x** - X/Twitter 抓取工具（Browser Relay + 登录 X）
2. **send-email** - 邮件发送工具（已配置 SMTP 和密钥）
3. **translate** - 翻译技能（已安装）

## 使用方法

### 快速开始

```
使用 crawl-from-x 技能抓取 X 推文
```

AI 会自动完成所有步骤：抓取 → 翻译 → 生成综述 → 合并 → 发送邮件 ✨

---

### 工作流程

1. **抓取** - 调用 crawl-from-x 技能，保存到 `results/posts_YYYYMMDD_HHMMSS.md`
2. **翻译** - 翻译为中文，保存为 `posts_YYYYMMDD_HHMMSS_zh.md`
3. **生成综述** - 分析推文内容，生成综述，保存为 `summary_YYYYMMDD_HHMMSS.md`
4. **合并** - 将综述和翻译推文合并为 `summary_complete_YYYYMMDD_HHMMSS.md`
5. **发送邮件** - 使用合并后的文件发送邮件，内嵌图片，应用模板

### 文件说明

- **posts_*.md** - 原始抓取文件
- **posts_*_zh.md** - 翻译后的文件
- **summary_*.md** - 仅包含综述部分
- **summary_complete_*.md** - 综述 + 翻译推文的完整内容（用于邮件发送）

### 发送邮件

邮件发送会自动：
- 读取 `config.json` 中的收件人和抄送人
- 查找最新的 `summary_complete_*.md` 文件
- 切换到 `results/` 目录（确保图片相对路径正确）
- 使用 `default` 模板（仿照 x.com 样式）
- 自动检测 Markdown 格式并内嵌图片

**关键：** 必须在 `results/` 目录下执行发送命令，否则图片无法正确解析。

---

## 注意事项

1. Browser Relay 必须启动并已连接浏览器扩展
2. 浏览器必须登录 X 账号
3. 确保 send-email 技能已正确配置 SMTP 和密钥
4. 定期清理旧文件，避免占用磁盘空间

---

## 故障排查

### 抓取失败
- 检查 Browser Relay 状态：`openclaw browser status`
- 确认浏览器扩展已连接（绿色图标）

### 翻译失败
- 确认抓取已完成：`ls -lht $CLAWD/skills/crawl-from-x/results/`

### 发送失败
- 检查配置：`cat $CLAWD/skills/mailme-x-news/config.json`
- 检查 SMTP：`cd $CLAWD/skills/send-email/scripts && python3 send_email.py config`
- 检查密钥：`python3 send_email.py username` 和 `python3 send_email.py password`
- 确认合并文件存在：`ls -lht $CLAWD/skills/crawl-from-x/results/summary_complete_*.md`

### 邮件中没有图片
- 确认在 `results/` 目录下执行发送命令
- 检查图片文件存在：`ls -lh $CLAWD/skills/crawl-from-x/results/images/`

---

## 定时任务

通过 OpenClaw cron 设置定时任务，每天自动发送 X 推文摘要。

示例：每天早上 8:00 执行
```
mailme-x-news
```

---

## 更新日志

- **2026-03-02 v6** - 明确工作流程：抓取 → 翻译 → 生成综述 → 合并 → 发送邮件
