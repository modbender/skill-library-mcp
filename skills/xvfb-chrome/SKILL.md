---
name: xvfb-chrome
description: 在Linux服务器上使用Chrome浏览器(无头/有头模式)配合xvfb运行，可连接chrome-devtools MCP进行浏览器自动化
---

# XVFB + Chrome 浏览器自动化

在无GUI的Linux服务器上运行Chrome浏览器的完整指南，支持配合 chrome-devtools MCP 使用。

## 模式选择

| 场景 | 推荐方式 |
|------|----------|
| 快速爬取、截图、自动化脚本 | `--headless=new` (无头) |
| 需要调试/连接DevTools MCP | xvfb-run + 非无头 + `--remote-debugging-port=9222` |
| 需要看到浏览器窗口(VNC截图等) | xvfb-run + 非无头 |

## 启动命令

### 1. 无头模式 (常规自动化)

```bash
google-chrome --headless=new --no-sandbox --disable-gpu --user-data-dir=/tmp/chrome-data
```

### 2. 有头 + xvfb + DevTools (推荐 MCP 用户)

```bash
xvfb-run -a google-chrome --no-sandbox \
  --disable-gpu --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-profile
```

关键点：
- `-a` = 自动分配 display 编号
- 去掉 `--headless` 就是有头模式
- DevTools 监听 `ws://127.0.0.1:9222/devtools/browser/xxx`

### 3. 重启 Chrome (杀旧进程)

```bash
pkill -f "chrome.*remote-debugging-port=9222" 2>/dev/null
sleep 1
xvfb-run -a google-chrome --no-sandbox \
  --disable-gpu --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-profile &
```

## Chrome DevTools MCP 配合使用

MCP server `chrome-devtools` 已安装，连接 `http://127.0.0.1:9222`：

```bash
mcporter list chrome-devtools --schema   # 查看可用工具
mcporter call chrome-devtools.list_pages # 列出页面
```

### 常用 MCP 工具

| 工具 | 功能 |
|------|------|
| `new_page url:"https://xxx"` | 打开新页面 |
| `navigate_page type:"url" url:"https://xxx"` | 导航 |
| `take_screenshot filePath:"/path/xxx.png"` | 截图 |
| `take_snapshot` | 获取页面元素快照 |
| `click uid:"xxx"` | 点击元素 |
| `fill uid:"xxx" value:"xxx"` | 填入表单 |
| `type_text text:"xxx"` | 输入文本 |
| `list_network_requests` | 查看网络请求 |
| `evaluate_script function:"() => { return document.title }"` | 执行JS |

### 完整示例

```bash
# 1. 启动浏览器
xvfb-run -a google-chrome --no-sandbox \
  --disable-gpu --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-profile &

# 2. 检查是否就绪
curl -s http://127.0.0.1:9222/json/version

# 3. 用 MCP 操作
mcporter call chrome-devtools.new_page url:"https://www.baidu.com"
mcporter call chrome-devtools.take_screenshot filePath:"/root/screenshot.png"
```

## 参数解释

| 参数 | 作用 |
|------|------|
| `--headless=new` | 无头模式(不显示窗口) |
| `--remote-debugging-port=9222` | 开启调试端口，供MCP连接 |
| `--no-sandbox` | 跳过沙箱(服务器必加) |
| `--disable-gpu` | 禁用GPU(服务器必加) |
| `--user-data-dir=/tmp/xxx` | 用户数据目录(避免冲突) |
| `-a` (xvfb-run) | 自动分配 display 编号 |
| `DISPLAY=:99` | 指定使用某个 Xvfb 显示编号 |

## 分辨率配置

### 查看当前 Xvfb

```bash
ps aux | grep Xvfb | grep -v grep
```

输出示例：
```
Xvfb :99 -screen 0 1280x720x24
Xvfb :100 -screen 0 640x480x24
```

### 启动指定分辨率的 Xvfb

```bash
# 1280x720 分辨率
Xvfb :99 -screen 0 1280x720x24 -nolisten tcp &

# 1920x1080 分辨率
Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp &
```

### 绑定 Chrome 到指定 Xvfb

```bash
# 方式1：使用 xvfb-run 自动分配
xvfb-run -a google-chrome --no-sandbox ...

# 方式2：手动指定 display 编号
DISPLAY=:99 google-chrome --no-sandbox ...
```

### 常用分辨率

| 分辨率 | 适用场景 |
|--------|----------|
| 640x480 | 轻量爬取、简单截图 |
| 1280x720 (720p) | 常规浏览、推荐配置 |
| 1920x1080 (1080p) | 高清截图、复杂页面 |

### 常用操作

```bash
# 查看当前运行的 Xvfb
ps aux | grep Xvfb | grep -v grep

# 杀掉所有 Chrome 进程
killall chrome

# 杀掉所有 Xvfb
pkill Xvfb

# 重启 Chrome（绑定到 :99）
killall chrome 2>/dev/null
sleep 1
DISPLAY=:99 google-chrome --no-sandbox \
  --disable-gpu --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-profile &
```
