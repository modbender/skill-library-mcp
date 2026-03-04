---
name: edge-browser
description: Control Microsoft Edge browser to fetch web pages and extract content. Use when the user wants to access a specific URL using Edge browser instead of Chrome, or when regular web fetching tools fail due to anti-scraping protections. Useful for accessing pages that require JavaScript rendering or have bot detection.
metadata:
  version: 1.0.0
---

# Edge Browser Controller

使用 Microsoft Edge 浏览器访问指定 URL 并提取页面内容。

## 适用场景

- 用户明确要求使用 Edge 浏览器访问链接
- Chrome 浏览器工具不可用或连接失败
- 网页有反爬虫保护，常规抓取工具无法获取内容
- 页面需要 JavaScript 渲染才能显示完整内容

## 前置要求

需要安装 Playwright：
```bash
pip install playwright
playwright install chromium
```

## 使用方法

### 基本用法

```bash
python ~/.openclaw/skills/edge-browser/scripts/fetch.py <URL>
```

### 带等待时间（用于动态加载页面）

```bash
python ~/.openclaw/skills/edge-browser/scripts/fetch.py <URL> --wait 5
```

### 保存到文件

```bash
python ~/.openclaw/skills/edge-browser/scripts/fetch.py <URL> --wait 5 --output result.json
```

## 输出格式

```json
{
  "url": "https://example.com",
  "title": "Page Title",
  "content": "<html>...</html>",
  "text": "Extracted text content...",
  "status": "success"
}
```

## 故障排除

### Edge 未找到

如果 Edge 浏览器未在默认位置安装，脚本会自动回退到 Chromium。

### 页面内容不完整

增加 `--wait` 时间，等待动态内容加载完成：
```bash
python scripts/fetch.py <URL> --wait 10
```

### 反爬虫检测

脚本已配置 Edge User-Agent，大多数网站应能正常访问。如遇问题，可能需要额外配置代理或验证码处理。
