---
name: weibo-fresh-posts
description: 用于监控微博关注流，先切换到最新微博时间线，再按发帖时间抓取并去重写入每日 Markdown，减少关键微博漏看。
homepage: https://github.com/hwb96/weibo-fresh-posts-skill
metadata:
  {
    "openclaw":
      {
        "emoji": "🧭",
        "requires": { "config": ["browser.enabled"] },
      },
  }
---

# Weibo Timeline Monitor（微博关键信息不漏看）

将微博「最新微博」时间线的新增帖子稳定写入本地日报，方便随时打开 Markdown 查看，不再漏看关键信息。

## 本 Skill 强制约束

- 抓取前必须先点击左侧 `最新微博`，不能直接在推荐流抓取。
- 表格时间列必须是帖子原始发布时间，禁止写抓取时间。
- `发帖内容` 必须是原帖正文，不能写成概括句。
- `内容总结` 只写简短摘要（<= 30 字）。
- 以原始链接全文件去重，避免重复记录。
- 在时间窗口内执行滚动补抓，降低漏抓概率。

## 参考文档

- `references/workflow.md`：完整抓取流程与时间解析规则。
- `references/markdown-schema.md`：Markdown 表头与字段语义。
- `references/cron-setup.md`：如何与 OpenClaw Cron 组合。

## 快速开始

1. 确保 `openclaw` 浏览器 profile 已登录微博。
2. 按 `references/workflow.md` 执行抓取流程。
3. 按 `references/markdown-schema.md` 写入日报。
4. 使用 `scripts/install_cron.sh` 创建周期任务。

## 安全注意

- 不在提示词、仓库或输出文件中保存账号密码、Cookie。
- 时间文本无法解析时跳过该条，并在运行摘要中统计跳过数。
- 无法稳定进入「最新微博」时，返回可读失败信息，避免静默错抓。
