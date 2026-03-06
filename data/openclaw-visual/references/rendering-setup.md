# 本地图片渲染配置

## 简介

OpenClaw Visual 使用本地渲染引擎将 HTML/CSS 转换为图片，无需外部 API。

支持两种渲染方案：
- **node-html-to-image** (默认): 轻量快速，基于 Puppeteer
- **Playwright** (高级): 更好的 CSS 支持，处理复杂效果

---

## 安装

### 1. 基础安装

在 skill 目录下运行：

```bash
cd skills/openclaw-visual
npm install
```

这将安装默认渲染引擎 `node-html-to-image`。

### 2. (可选) 安装 Playwright

如果你需要更好的渲染效果或处理复杂 CSS：

```bash
npm install playwright
npx playwright install chromium
```

---

## 渲染引擎对比

| 特性 | node-html-to-image | Playwright |
|-----|-------------------|------------|
| **安装大小** | ~100MB | ~150MB |
| **启动速度** | 快 (~0.5s) | 中等 (~1s) |
| **CSS 支持** | 良好 | 优秀 |
| **动画支持** | 有限 | 完整 |
| **字体渲染** | 良好 | 优秀 |
| **适用场景** | 日常快速生成 | 精美/复杂效果 |

---

## 使用方法

### 命令行调用

```bash
# 默认渲染 (node-html-to-image)
node scripts/generate-image.js \
  --template quote-card \
  --content '{"QUOTE":"Hello World","AUTHOR":"Author Name"}' \
  --output ./output.png

# 指定渲染引擎
node scripts/generate-image.js \
  --template quote-card \
  --content '{"QUOTE":"Hello World"}' \
  --renderer playwright \
  --output ./output.png

# 指定尺寸
node scripts/generate-image.js \
  --template social-share \
  --content '{"TITLE":"Hello"}' \
  --width 1200 \
  --height 630 \
  --output ./output.png
```

### 自动选择逻辑

当 `renderer` 设置为 `auto` 时：

1. **默认使用 node-html-to-image** - 快速、轻量
2. **自动切换到 Playwright** - 当用户请求包含以下关键词时：
   - 中文: "精美", "复杂", "高级", "动画", "特效"
   - 英文: "beautiful", "complex", "advanced", "animation"

---

## 配置

在 `~/.openclaw/visual/config.yaml`:

```yaml
# 渲染引擎设置
renderer: auto  # auto | nodejs | playwright

# 输出设置
output:
  path: "~/OpenClaw/Visuals/"
  format: "png"      # png | jpeg
  quality: 90        # JPEG 质量 (1-100)

# 默认模板设置
default_template: "quote-card"
default_theme: "light"
```

---

## 故障排除

### Chromium 安装失败

如果在安装 `node-html-to-image` 时 Chromium 下载失败：

```bash
# 设置镜像源
export PUPPETEER_DOWNLOAD_HOST=https://npm.taobao.org/mirrors
npm install

# 或手动安装 Chromium
npx puppeteer browsers install chrome
```

### 字体显示问题

确保系统安装了常用中文字体：

```bash
# macOS
brew install font-noto-sans-cjk

# Ubuntu/Debian
sudo apt-get install fonts-noto-cjk
```

### 权限问题 (Linux)

如果在 Linux 上遇到 sandbox 错误：

```bash
# 脚本已自动添加 --no-sandbox 参数
# 如需永久解决，可以设置环境变量:
export PUPPETEER_ARGS='--no-sandbox --disable-setuid-sandbox'
```

---

## 性能优化

### 批量生成

对于批量生成图片，建议使用 Playwright 的持久化浏览器：

```javascript
const { chromium } = require('playwright');

// 启动一次浏览器，多次使用
const browser = await chromium.launch();

for (const item of items) {
  const page = await browser.newPage();
  // ... 生成图片
  await page.close();
}

await browser.close();
```

### 内存管理

- 单张图片生成后及时关闭浏览器实例
- 大量生成时考虑分批处理
- 监控内存使用，必要时重启进程
