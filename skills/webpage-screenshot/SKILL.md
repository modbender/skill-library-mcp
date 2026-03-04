---
name: webpage-screenshot
description: 打开指定网页并截图为图片文件。在用户要求对某 URL 截图、保存网页为图片、或需要网页快照时使用。
---

# 网页截图

## 何时使用

- 用户给出一个 URL，要求「打开并截图」或「保存网页为图片」
- 需要网页快照、页面留档或可视化结果时

## 方式一：运行项目脚本（推荐，得到文件）

使用项目内 TypeScript 脚本，可保存为本地图片文件：

```bash
# 在项目根目录执行
npm run screenshot -- <URL> [输出路径]
```

示例：

```bash
npm run screenshot -- https://example.com
# 默认保存为 ./screenshot.png

npm run screenshot -- https://example.com ./output/page.png
```

**前置条件**：已执行 `npm install` 且已安装浏览器：`npx playwright install chromium`。

## 方式二：使用 MCP 浏览器

若仅需在对话中「看到」页面内容而不必保存为文件，可使用 Cursor 的 browser MCP：

1. `browser_navigate` 打开目标 URL
2. `browser_snapshot` 获取页面结构（相当于当前状态的“快照”信息）

注意：MCP 浏览器不直接生成截图文件，适合快速查看与交互。

## 输出

- 脚本方式：在指定路径生成 PNG 截图（默认 `screenshot.png`）。
- 截图为整页（含滚动区域），视口宽度默认 1280px。
