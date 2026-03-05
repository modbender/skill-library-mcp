---
name: bilibili-monitor
description: 生成B站热门视频日报并发送邮件。触发词：B站热门、bilibili日报、视频日报、热门视频
metadata: {"openclaw":{"emoji":"📺","requires":{"bins":["python3"]},"os":["darwin","linux","win32"]}}
---

# B站热门视频日报

## 🔒 安全说明

- 所有凭据仅存储在用户本地设备上，Skill 发布包中不包含任何凭据
- 配置文件 `bilibili-monitor.json` 已通过 `.gitignore` 排除，不会被意外上传或分享
- 网络传输使用 HTTPS 和 TLS/STARTTLS 加密
- 同时支持环境变量和命令行参数传递凭据，用户可自行选择

## 执行流程（分步询问）

### 检查配置文件

首先检查是否存在配置文件：
```bash
test -f {baseDir}/bilibili-monitor.json && echo "CONFIG_EXISTS" || echo "CONFIG_NOT_EXISTS"
```

- 如果输出 `CONFIG_EXISTS` → 跳到【直接执行】
- 如果输出 `CONFIG_NOT_EXISTS` → 进入【分步创建配置】

---

### 分步创建配置（首次使用）

**第1步：询问 B站 Cookies**
```
请提供 B站 Cookies：
（获取方法：登录B站首页 → F12 → Network选项卡 → 刷新页面 → 点击 www.bilibili.com 请求 → 找到 Request Headers 中的 Cookie 字段 → 复制整个值）
```
等待用户回复，保存为变量 `COOKIES`

**第2步：询问 AI 服务**
```
AI 功能说明：
- 需要 OpenRouter API Key
- 用于生成视频内容总结（基于字幕）和 AI 点评

是否启用 AI 功能？
1 = 是（推荐，需要 OpenRouter API Key）
2 = 否（将无法生成视频总结和点评）
请回复数字：
```
等待用户回复

**第3步：如果选了 1（启用 AI）**
```
请选择模型：
1 = Gemini（推荐，便宜快速）
2 = Claude（高质量）
3 = GPT
4 = DeepSeek（性价比）
```
等待用户回复，然后：
```
请提供 OpenRouter API Key：
获取地址：https://openrouter.ai/keys
```
保存为 `OPENROUTER_KEY` 和 `MODEL`

**第4步：询问发件邮箱**
```
请提供 Gmail 发件邮箱：
```
等待用户回复，保存为 `SMTP_EMAIL`

**第5步：询问应用密码**
```
请提供 Gmail 应用密码（16位）：
获取地址：https://myaccount.google.com/apppasswords
```
保存为 `SMTP_PASSWORD`

**第6步：询问收件人**
```
请提供收件人邮箱（多个用逗号分隔）：
```
保存为 `RECIPIENTS`

**第7步：生成配置文件**

根据收集的信息创建配置文件：
```bash
cat > {baseDir}/bilibili-monitor.json << 'EOF'
{
  "bilibili": {
    "cookies": "COOKIES值"
  },
  "ai": {
    "openrouter_key": "OPENROUTER_KEY值或空",
    "model": "MODEL值"
  },
  "email": {
    "smtp_email": "SMTP_EMAIL值",
    "smtp_password": "SMTP_PASSWORD值",
    "recipients": ["收件人1", "收件人2"]
  },
  "report": {"num_videos": 10}
}
EOF
```

---

### 确认并执行

向用户展示确认信息：
```
✅ 配置已就绪
🚀 即将开始执行：获取热门视频 → 提取字幕 → AI生成总结和点评 → 发送邮件
⏱️ 预计耗时：10-15 分钟，请耐心等待

是否开始执行？
```
等待用户确认后，执行以下命令。

⚠️ **AI Agent 注意事项**：
- 脚本执行需要 10-15 分钟，这是正常的，请设置超时 900 秒以上
- 脚本会在 25%、50%、75%、100% 时自动输出进度，**请只转发脚本实际输出**
- **不要**在等待期间发送"等待中..."、"继续等待..."等自定义消息，会导致刷屏
- 执行完成后再向用户汇报结果即可

**生成报告：**
```bash
python3 {baseDir}/generate_report.py --config {baseDir}/bilibili-monitor.json --output /tmp/bilibili_report.md
```

**发送邮件（邮件标题自动使用当前日期）：**
```bash
python3 {baseDir}/send_email.py --config {baseDir}/bilibili-monitor.json --body-file /tmp/bilibili_report.md --html
```

---

## OpenRouter 模型映射

| 用户选择 | model 值 |
|---------|---------|
| 1 / Gemini | google/gemini-3-flash-preview |
| 2 / Claude | anthropic/claude-sonnet-4.5 |
| 3 / GPT | openai/gpt-5.2-chat |
| 4 / DeepSeek | deepseek/deepseek-chat-v3-0324 |

## 配置文件示例

见 `bilibili-monitor.example.json`

## ⏱️ 执行时间

| 阶段 | 预计时间 |
|------|---------|
| 获取视频列表 | 5-10 秒 |
| 字幕提取+AI总结（20个视频） | 2-3 分钟 |
| AI点评（20个视频） | 8-12 分钟 |
| 生成报告+发送邮件 | 10-20 秒 |
| **总计** | **10-15 分钟** |

⚠️ 完整执行需要 10-15 分钟，请确保命令超时设置足够长（建议 900 秒以上）。

## ⚠️ 重要提示

**AI 视频总结说明：**
- 视频总结基于字幕生成，需要视频有字幕（CC字幕或AI字幕）
- 部分视频可能没有字幕，这些视频将无法生成总结
- 推荐启用 AI 功能以获得完整的视频分析体验
- 需要 OpenRouter API Key（支持 Gemini、Claude、GPT、DeepSeek 等模型）
