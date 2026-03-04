---
name: xiaohongshu-automation
description: A complete automation suite for Xiaohongshu (Little Red Book). Includes long-text publishing, comment management (reply/check), and stealth login helpers.
author: Dingkang Wang
---

# Xiaohongshu Automation Suite

This skill bundle provides a set of tools to automate your Xiaohongshu content creation and community management.

## Included Tools

### 1. 📝 Publishing (xiaohongshu-publish)
- **publish_long_text**: Automatically publish long-form articles with titles and content.
- Supports "Pro" platform (pro.xiaohongshu.com).

### 2. 💬 Community Management (xiaohongshu-reply)
- **check_comments**: Fetch and reply to latest comments.
- **reply_fixed**: Alternative reply logic.
- **generate_replies**: Generate template replies.

### 3. 🔐 Authentication
- **login_helper**: Stealth login script using Playwright (independent, no plugin required).
- Cookie management and persistence.

## Usage

### Login (First Time)
Run the login helper to capture cookies:
```bash
python3 skills/xiaohongshu-skill/login_helper.py
```

### Publish an Article
```bash
python3 skills/xiaohongshu-skill/xiaohongshu-publish/publish_long_text.py --title "My Title" --content "My Content"
```

## Requirements
- Python 3.8+
- Playwright (`pip install playwright && playwright install chromium`)
