---
name: weibo
description: Operate Weibo via browser automation for composing posts, publishing content, replying to comments, checking mentions, and monitoring basic account metrics. Use when users ask to manage 微博运营、发布内容、互动回复、或查看近期账号表现.
---

# Weibo Skill

Use browser automation for Weibo workflows.

## Workflow

1. Open Weibo web/creator pages in browser tool.
2. Let user complete login or secondary verification when required.
3. Ask for explicit confirmation before posting or deleting content.
4. Execute with snapshot + act.
5. Return concise operation report.

## Supported Tasks

- Draft and publish posts (text/image where web supports)
- Reply to comments and mentions
- Check notifications and @mentions queue
- Pull visible performance stats from creator pages
- Clean up or pin/unpin posts (after confirmation)

## Safety

- Require explicit confirmation for publish/delete actions.
- Do not attempt anti-bot bypass.
- If session invalid/CAPTCHA appears, pause and request user action.
- Keep operations reversible when possible.

## Trigger Examples

- “发条微博，文案是…”
- “帮我回复今天的@”
- “看下这周微博数据”
- “把这条微博置顶/取消置顶”

## Output Template

- Action: <compose/publish/reply/metrics/moderation>
- Account: <name>
- Result: <success|partial|failed>
- Details:
  - ...
- Next step:
  - ...
