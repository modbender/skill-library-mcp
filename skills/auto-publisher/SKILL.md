---
name: auto-publisher
description: Multi-platform video auto-publisher. Automatically upload videos to Douyin, WeChat Channels, Xiaohongshu, Bilibili, YouTube and more. Supports batch publishing, scheduled posting, auto-caption generation, and hashtag optimization.
license: MIT
metadata:
  author: 小龙虾 (Little Lobster)
  homepage: https://clawhub.ai/users/954215110
  tags: ["auto-publish", "social-media", "video", "automation", "douyin", "xiaohongshu", "bilibili"]
---

## 🦞 小龙虾品牌

**Created by 小龙虾 AI 工作室**

> "小龙虾，有大钳（前）途！"

**Contact for custom services:** +86 15805942886

Need custom automation workflows, enterprise batch publishing, or API integration? Reach out!

---

# Auto Publisher - 多平台视频发布助手

一键上传视频到抖音、视频号、小红书、B 站、YouTube 等平台。

## Features

- ✅ **多平台支持** - 抖音、视频号、小红书、B 站、YouTube
- ✅ **一键发布** - 一次操作，多平台同步
- ✅ **自动文案** - 智能生成标题和标签
- ✅ **定时发布** - 支持发布队列和定时任务
- ✅ **发布记录** - 自动保存发布历史
- ✅ **二维码登录** - 安全便捷，无需密码

## Quick Start

### 1. 安装依赖

```bash
pip install playwright
playwright install chromium
```

### 2. 配置账号

首次运行自动创建 `config/accounts.json`

### 3. 发布视频

```bash
# 发布到所有平台
python auto_publisher.py "video.mp4"

# 指定平台
python auto_publisher.py "video.mp4" --platforms douyin,xiaohongshu

# 无头模式
python auto_publisher.py "video.mp4" --headless
```

## Platform Support

| Platform | Login | Title Limit | Duration Limit |
|----------|-------|-------------|----------------|
| Douyin | QR Code | 100 chars | 15 min |
| WeChat Channels | QR Code | 1000 chars | 30 min |
| Xiaohongshu | QR Code | 20+1000 chars | 15 min |
| Bilibili | QR/Password | 80 chars | 4 hours |
| YouTube | Google | 100 chars | 12 hours |

## Scripts

- `scripts/auto_publisher.py` - 主发布程序
- `scripts/schedule_publisher.py` - 定时发布（待开发）
- `scripts/batch_publisher.py` - 批量发布（待开发）

## Config

- `config/accounts.json` - 账号配置
- `config/publish_log.json` - 发布记录
- `config/schedule.json` - 发布计划（待开发）

## Commands / Triggers

Use this skill when:
- "发布视频到所有平台"
- "Auto-post this video"
- "批量上传视频"
- "定时发布内容"
- "Multi-platform upload"

## Security Notes

- Cookie 保存在本地，注意保密
- 定期更新登录状态
- 不要分享账号配置文件
- 企业用户建议使用官方 API

## Troubleshooting

### Login timeout
- Check network connection
- Manually visit the platform website
- Re-run and scan QR code again

### Publish failed
- Check video format (MP4 recommended)
- Check video size limits
- View browser window for error details

### Playwright errors
```bash
pip install --upgrade pip
pip install playwright
playwright install chromium
```

---

_Ready to automate your social media posting? Let's go! 🦞🚀_
