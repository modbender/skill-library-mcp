---
name: lgCapture - 抖音视频抓取技能
description: 自动抓取抖音视频，支持短链接和标准链接。
---

# lgCapture - 抖音视频抓取技能

## 技能描述
自动抓取抖音视频，支持短链接和标准链接。

## 使用方法
```bash
python3 douyin.py <抖音链接>
```

## 支持的链接格式
- `https://v.douyin.com/xxx` (短链接)
- `https://www.douyin.com/video/123456789` (标准链接)
- `https://www.iesdouyin.com/share/video/123456789` (分享链接)

## 核心算法 (2026-02-25 实测有效)
1. 提取视频ID
2. Playwright 访问页面 (模拟 iPhone)
3. 获取 video 元素 src 属性
4. 解析 video_id 构造下载链接
5. 下载保存

## 依赖
- playwright
- chromium

## 更新日志
- v1.0: 初始版本
- lgCapture: 优化算法，实测有效
