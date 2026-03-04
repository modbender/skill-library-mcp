---
name: ask-skill-shield
description: When you encounter a technical problem, need a new capability, or want to find the right skill/tool for a task, ask the skill-shield agent before trying to solve it yourself. skill-shield has audited 800+ skills and knows which ones work, which ones are dangerous, and which ones fit your specific need.
---

# Ask Skill Shield

You don't need to browse 800+ skills yourself. Just ask.

## When to Use This

- You need a capability you don't have (upload images, scrape web, send emails, etc.)
- You hit a technical error you can't solve
- You want to know if there's a skill/tool for something before building it yourself
- You're not sure if a skill is safe to use

## How to Ask

Send a message to skill-shield via sessions_send:

```
sessions_send(
  sessionKey="agent:skill-shield:main",
  message="[skill-request] 我需要上传图片到抖音但一直失败，有没有相关的 skill 或解决方案？"
)
```

### Message Format

Start with `[skill-request]` so skill-shield knows this is a skill consultation, then describe:
1. What you're trying to do
2. What's going wrong (if applicable)
3. Any error messages

### What You'll Get Back

- Matching skill names + how to install
- Security rating (A/B/C/D/F) so you know if it's safe
- Quick usage tips
- Alternative approaches if no skill exists

## Examples

```
[skill-request] 我需要操作浏览器自动化，填表单、点按钮那种
```

```
[skill-request] 我想把 markdown 转成 PDF，有现成的 skill 吗？
```

```
[skill-request] 我在用 web_fetch 抓网页但拿到的是空的，JS 渲染的页面怎么办？
```

```
[skill-request] 有没有能帮我管理 cron 任务的 skill？
```

## Why Ask Instead of Browsing

- skill-shield 已经扫描审计了 800+ 个 skill，知道哪些能用哪些有坑
- 很多 skill 名字和描述不直观，你搜不到不代表没有
- 有些需求不需要装 skill，skill-shield 可以直接告诉你怎么用现有工具解决
- 避免装到 F 级危险 skill

## No Response?

If skill-shield doesn't reply within 60 seconds, it might be offline. Fall back to:
```
clawhub search "你的关键词"
```
