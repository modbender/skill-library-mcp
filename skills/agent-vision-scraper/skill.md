# Dockerized Vision Agent Scraper

## Description
这是一个运行在独立 Docker 容器中的拟人化网页操作与抓取工具。它内置了虚拟屏幕 (Xvfb) 和 Playwright 隐身指纹，完全依靠 AI 的视觉能力 (Vision) 来读取和破解图形验证码，不依赖任何第三方打码服务。

**Base Image**: `mcr.microsoft.com/playwright:v1.58.2-jammy`

## Usage Instructions
当用户要求进行复杂网页自动化、数据抓取、或遇到具备反爬/图形验证码的网站时，请调用此工具。

**重要说明**：必须通过 `docker run` 命令来启动它，以确保它运行在配置好的虚拟屏幕环境中。

**Command Format:**
```bash
docker run --rm --env-file .env -p 5900:5900 agent-scraper-image node agent-scraper.js
```

**Examples:**
```bash
docker run --rm --env-file .env -p 5900:5900 agent-scraper-image node agent-scraper.js "https://example.com/login" "查看页面，如果发现图形验证码，读出图片上的字母，并与账号 admin 和密码 123456 一起填入表单，点击登录。"
```

## Build Image
```bash
cd ~/.openclaw/skills/agent-vision-scraper
docker build -t agent-scraper-image .
```

## Features
- ✅ 虚拟屏幕 (Xvfb) - 无头服务器也能运行有头浏览器
- ✅ VNC 远程查看 - 端口 5900 可连接查看实时操作
- ✅ Playwright Stealth - 绕过常见反爬检测
- ✅ Vision 验证码识别 - 利用 LLM 视觉能力破解图形验证码
- ✅ 最新 Playwright v1.58.2 - 与当前环境保持一致

---
_最后更新：2026-03-03_
