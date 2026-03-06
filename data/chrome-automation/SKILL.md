---
name: chrome-automation
description: Linux服务器Chrome浏览器自动化方案。支持2K高清截图、表单填写、自动登录、绕过反爬虫检测。适用于B站、YouTube等网站自动化操作。
metadata:
  openclaw:
    requires:
      bins: ["google-chrome", "python3"]
    install:
      - id: google-chrome
        kind: shell
        command: |
          # 下载并安装Google Chrome
          wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O /tmp/chrome.deb
          sudo apt update && sudo apt install -y /tmp/chrome.deb xvfb
        label: Install Google Chrome
      - id: playwright-env
        kind: shell
        command: |
          # 创建Python虚拟环境并安装Playwright
          sudo apt install -y python3.11-venv
          python3 -m venv ~/.playwright-env
          source ~/.playwright-env/bin/activate
          pip install playwright
          playwright install chromium
        label: Setup Playwright Environment
---

# Chrome 浏览器自动化

服务器环境下的Chrome浏览器自动化方案，支持2K高清截图和复杂交互操作。

## 🚀 快速开始

### 方案1：Chrome 无头模式（简单截图）

```bash
# 2K高清截图（推荐默认）
google-chrome --headless=new --no-sandbox --disable-gpu \
  --window-size=1920,1080 --force-device-scale-factor=2 \
  --screenshot=/home/Kano/.openclaw/workspace/screenshot.png \
  https://www.bilibili.com
```

**参数说明：**
| 参数 | 作用 |
|------|------|
| `--headless=new` | 新版无头模式 |
| `--window-size=1920,1080` | 窗口分辨率 |
| `--force-device-scale-factor=2` | 2倍缩放（2K清晰度）|
| `--no-sandbox` | 跳过沙箱（服务器必需）|
| `--disable-gpu` | 禁用GPU（服务器必需）|

---

### 方案2：Playwright + Stealth（高级自动化）

**适用于：** 填表、登录、发帖、绕过反爬虫检测

```bash
# Stealth模式截图
python3 ~/.openclaw/workspace/skills/chrome-automation/scripts/playwright_stealth.py <URL>

# 指定输出路径
python3 ~/.openclaw/workspace/skills/chrome-automation/scripts/playwright_stealth.py <URL> -o <输出路径>
```

**Python调用：**
```python
import sys
sys.path.insert(0, '/home/Kano/.playwright-env/lib/python3.11/site-packages')
sys.path.insert(0, '/home/Kano/.openclaw/workspace/skills/chrome-automation/scripts')

from playwright_stealth import screenshot_with_stealth, auto_fill_form

# 截图（自动绕过反爬虫）
screenshot_with_stealth('https://bilibili.com')

# 自动填表登录
auto_fill_form('https://login.example.com', {
    '#username': '用户名',
    '#password': '密码'
}, submit_selector='button[type=submit]')
```

---

## 📊 方案对比

| 特性 | Chrome无头 | Playwright |
|------|-----------|------------|
| **启动速度** | ⚡ 最快 | 🚀 快 |
| **截图质量** | ✅ 2K高清 | ✅ 2K高清 |
| **绕过反爬虫** | ⚠️ 容易被检测 | ✅ Stealth模式 |
| **填表/登录** | ❌ 不支持 | ✅ 完美支持 |
| **资源占用** | 低 | 中 |
| **推荐场景** | 简单截图 | 复杂自动化 |

---

## 🔧 常用命令

```bash
# ========== 基础截图 ==========
# 默认分辨率
google-chrome --headless=new --no-sandbox --disable-gpu \
  --screenshot=output.png https://example.com

# 2K高清（推荐）
google-chrome --headless=new --no-sandbox --disable-gpu \
  --window-size=1920,1080 --force-device-scale-factor=2 \
  --screenshot=output.png https://example.com

# 全页面截图
google-chrome --headless=new --no-sandbox --disable-gpu \
  --window-size=1920,1080 --hide-scrollbars \
  --screenshot=output.png https://example.com

# ========== Playwright ==========
# Stealth截图
python3 ~/.openclaw/workspace/skills/chrome-automation/scripts/playwright_stealth.py <URL>

# 自定义输出
python3 ~/.openclaw/workspace/skills/chrome-automation/scripts/playwright_stealth.py <URL> -o <路径>
```

---

## 🛠️ 环境信息

| 组件 | 版本/路径 |
|------|----------|
| Google Chrome | `/usr/bin/google-chrome` (v145+) |
| Playwright | `~/.playwright-env/` (v1.58.0) |
| Python虚拟环境 | `~/.playwright-env/` |
| Stealth脚本 | `scripts/playwright_stealth.py` |

---

## ⚠️ 注意事项

1. **每次运行都是新会话**，不会保留登录状态
2. **截图默认保存到** `/home/Kano/.openclaw/workspace/`
3. **B站等网站可能触发验证码**，需要人工处理或使用已登录的Cookie

---

## 🔗 相关文件

- Stealth脚本：`scripts/playwright_stealth.py`
- 测试脚本：`scripts/test_playwright.py`
