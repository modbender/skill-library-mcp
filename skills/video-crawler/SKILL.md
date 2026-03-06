---
name: Video Crawler - 视频抓取技能
description: 一键抓取抖音和推特视频。
---

# Video Crawler - 视频抓取技能

一键抓取抖音和推特视频。

## 依赖安装

```bash
pip install playwright requests yt-dlp
playwright install chromium
```

## 使用方法

```bash
python3 video_crawler.py <平台> <链接> [输出文件]
```

### 抓取抖音视频
```bash
python3 video_crawler.py douyin "https://v.douyin.com/xxx"
```

### 抓取推特视频
```bash
python3 video_crawler.py twitter "https://x.com/i/status/xxx"
```

## 支持的平台

| 平台 | 命令 | 示例 |
|------|------|------|
| 抖音 | douyin | https://v.douyin.com/xxx |
| 推特 | twitter | https://x.com/i/status/xxx |

## 输出

- 成功：输出文件路径
- 失败：输出错误信息

## 注意事项

- 抖音视频可能需要 15-25 秒
- 推特视频文件较大，注意 Telegram 16MB 限制
