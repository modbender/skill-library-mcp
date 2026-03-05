---
name: redbook
description: Publish and manage Xiaohongshu (RED/小红书) content via browser automation with confirm-before-publish safety. Trigger when users say things like “发小红书/发笔记/保存草稿/立即发布/回复评论/看数据”, including image posts and no-image longform notes on creator.xiaohongshu.com.
---

# Redbook (Xiaohongshu) Publishing Skill

Use browser automation on the official creator site.

## Read this first

- Main entry: `https://creator.xiaohongshu.com`
- If user is not logged in, pause and ask user to complete SMS login.
- Never bypass CAPTCHA, SMS, or risk controls.
- Never publish without explicit confirmation in the current chat turn.

## Supported tasks

- Create a note draft (with or without images)
- Publish immediately (only after explicit confirmation)
- Save and leave as draft
- Reply to comments/messages
- Check dashboard metrics (7d/30d where visible)

## Publish flow (deterministic)

1. Confirm inputs:
   - title
   - body
   - image paths (optional)
   - mode: `publish_now` or `draft_only`
2. Open creator page and verify logged-in account name.
3. Enter publish page:
   - with images: choose 图文上传
   - no image: use 长文创作入口
4. Fill title/body.
5. Validate before submit:
   - title not empty
   - body not empty
   - hashtags formatted
6. If `draft_only`: click save/draft and report success.
7. If `publish_now`: ask one final yes/no confirmation, then publish.
8. Return result summary with account, title, mode, status.

## Required confirmation policy

For publish action, require exact confirmation intent such as:
- “立即发布”
- “确认发布”
- “继续发布”

If user says vague words (“随便”, “你看着办”), default to draft-only and explain why.

## Failure handling

- Login expired: ask user to login, then continue from current page.
- Missing controls due to UI changes: snapshot again and switch to nearest equivalent button.
- Publish button unavailable: keep draft and report manual step clearly.

## Output template

- Action: draft | publish | reply | metrics
- Account: <name>
- Title: <title>
- Mode: publish_now | draft_only
- Result: success | partial | failed
- Details:
  - ...
- Next step:
  - ...

## Reference

For reusable copy templates, read `references/post-templates.md`.
