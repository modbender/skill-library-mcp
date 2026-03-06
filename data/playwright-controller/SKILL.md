---
name: playwright controller
description: "Browse webpages using Playwright with automatic loading wait, screenshots, and text extraction. Use playwright:fetch or playwright:screenshot commands. API: fetchWithPlaywright(url, options), fetchElementAndScreenshot(url, selector, options)"
---

# Playwright Controller

使用 Playwright 智能浏览网页，支持截图和文本提取。

## 核心特性

- 📱 **移动端模拟**: 模拟 iPhone 浏览器（375x667 分辨率）
- 🎨 **移动端 User-Agent**: 使用真实的移动端浏览器标识
- 🔄 **有头模式**: 可见浏览器窗口，支持手动操作（如点击登录）
- 📸 **完整资源加载**: 所有资源正常加载，包括图片、CSS、字体等
- ⏳ **智能等待**: 自动等待页面完全加载
- 📝 **文本提取**: 自动提取页面文本内容

## 基本用法

### fetch - 获取网页内容和截图

```bash
playwright:fetch <url>
```

自动等待 JS/CSS 加载完成，截取全屏截图，并提取页面文本内容。

**特点：**
- 📱 移动端模拟（375x800 分辨率）
- 🎨 移动端 User-Agent（iPhone 17.0）
- 🔄 有头模式（可见浏览器，支持手动操作如登录）
- 📸 完整资源加载（图片、CSS、字体全部正常加载）
- ⏳ 自动等待网络空闲
- 📄 同时保存截图和文本文件

**示例：**
```bash
playwright:fetch https://baike.baidu.com/item/兴盛优选/23451097
```

**输出：**
- 截图：`./screenshots/<timestamp>_<url_hash>.png`
- 文本：`./screenshots/<timestamp>_<url_hash>_content.txt`
- 命令执行信息输出到控制台

## 高级用法

### 自定义配置

```bash
playwright:fetch --timeout=120000 --dir=/custom/path <url>
```

参数：
- `--timeout`: 超时时间（毫秒），默认 60000
- `--dir`: 截图和文本文件保存目录，默认 `./screenshots`
- `<url>`: 目标网页 URL

**示例：**
```bash
playwright:fetch --timeout=120000 --dir=/Users/chenkuan/Desktop/screenshots https://baike.baidu.com/item/兴盛优选/23451097
```

### 截取特定元素

```bash
playwright:fetch-element --selector=".content" <url>
```

截取指定 CSS 选择器元素的截图和文本内容。

**示例：**
```bash
playwright:fetch-element --selector="h1" https://baike.baidu.com/item/兴盛优选/23451097
```

## 输出文件结构

执行后会生成以下文件：

```
screenshots/
├── 1716982345678_www_baike_baidu_com_item_兴盛优选_23451097.png    # 全屏截图
├── 1716982345678_www_baike_baidu_com_item_兴盛优选_23451097_content.txt  # 页面文本
└── 1716982345678_www_baike_baidu_com_item_兴盛优选_23451097_element.png # 元素截图
```

## 工作流程

1. **启动浏览器** - 使用 Chromium
2. **设置拦截规则** - 跳过图片、CSS、字体等资源
3. **访问页面** - 等待网络空闲（networkidle）
4. **等待渲染** - 额外等待 2 秒确保完全渲染
5. **截取截图** - 全屏 PNG 截图
6. **提取文本** - 移除广告/脚本元素，提取文本内容
7. **保存文件** - 截图和文本文件保存到指定目录

## 优势特点

✅ **自动加载等待** - 无需手动等待 JS/CSS 加载
✅ **智能资源拦截** - 跳过图片等无关资源，提高速度
✅ **全屏截图** - 保存完整的页面视觉信息
✅ **文本提取** - 适合后续文本处理和 AI 分析
✅ **稳定可靠** - 使用有头模式便于调试
✅ **错误处理** - 即使失败也会保存截图
✅ **时间戳命名** - 避免文件名冲突

## 注意事项

1. **浏览器启动时间** - 首次使用需要启动浏览器，约 2-3 秒
2. **网络依赖** - 需要网络连接访问目标网页
3. **文件权限** - 确保目录有写入权限
4. **长时间任务** - 复杂网页可能需要较长时间（60-120秒）

## 主要 API 描述

### fetchWithPlaywright(url, options)
获取整个网页的内容和截图。

**参数：**
- `url` (string, 必需): 目标网页 URL
- `options` (object, 可选):
  - `headless` (boolean): 是否无头模式，默认 false
  - `timeout` (number): 超时时间（毫秒），默认 60000
  - `screenshotDir` (string): 截图保存目录，默认 './screenshots'

**返回：**
```javascript
{
  content: string,        // 页面文本内容
  screenshotPath: string, // 截图文件路径
  title: string,          // 页面标题
  timestamp: number       // 时间戳
}
```

**工作流程：**
1. 启动 Chromium 浏览器（有头模式）
2. 设置请求拦截（跳过图片、CSS、字体等）
3. 访问 URL，等待 networkidle（网络空闲）
4. 等待 2 秒确保完全渲染
5. 截取全屏截图（1920x1080）
6. 提取文本内容（移除广告、脚本等）
7. 保存截图和文本文件

**示例：**
```javascript
const { fetchWithPlaywright } = require('./playwright-crawler-v3.js');

const result = await fetchWithPlaywright('https://example.com', {
  headless: false,
  timeout: 60000,
  screenshotDir: './screenshots'
});

console.log(result.content);        // 页面文本
console.log(result.screenshotPath); // 截图路径
```

### fetchElementAndScreenshot(url, selector, options)
获取指定 CSS 选择器元素的截图和文本。

**参数：**
- `url` (string, 必需): 目标网页 URL
- `selector` (string, 必需): CSS 选择器（如 '.content', 'h1', '#article'）
- `options` (object, 可选):
  - `headless` (boolean): 是否无头模式，默认 false
  - `timeout` (number): 超时时间（毫秒），默认 60000
  - `screenshotDir` (string): 截图保存目录，默认 './screenshots'

**返回：**
```javascript
{
  content: string,        // 元素文本内容
  screenshotPath: string, // 元素截图文件路径
  title: string,          // 页面标题
  timestamp: number       // 时间戳
}
```

**示例：**
```javascript
const { fetchElementAndScreenshot } = require('./playwright-crawler-v3.js');

const result = await fetchElementAndScreenshot(
  'https://example.com',
  '.article-content',
  {
    headless: false,
    screenshotDir: './screenshots'
  }
);

console.log(result.content);        // 元素文本
console.log(result.screenshotPath); // 截图路径
```

### Playwright 核心功能

**1. 智能页面加载等待**
- 使用 `page.goto(url, { waitUntil: 'networkidle' })`
- 等待网络空闲（所有网络请求完成）
- 移动端模拟和完整资源加载
- 避免页面未加载完成的截图

**2. 完整资源加载**
```javascript
// 不设置任何拦截规则，让所有资源正常加载
// 包括：图片、CSS、字体、JavaScript 等
// 这样截图才能看到完整的页面效果
```

**3. 移动端模拟**
```javascript
const context = await browser.newContext({
  userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)...',
  viewport: { width: 375, height: 667 },
  isMobile: true
});
```

**3. 截图功能**
- 全屏截图：`page.screenshot({ fullPage: true })`
- 元素截图：`element.screenshot()`
- PNG 格式（无损）
- 分辨率：1920x1080

**4. 文本提取**
```javascript
const content = await page.evaluate(() => {
  document.body.innerText;  // 获取文本内容
});
```

**5. 元素定位**
```javascript
// CSS 选择器
const element = await page.$('.content');      // 单个元素
const elements = await page.$$('.article');    // 多个元素

// 使用选择器
await element.$eval('h2', el => el.innerText);  // 提取元素文本
```

### 常用配置选项

**headless 模式**
```javascript
// 有头模式（可见浏览器，适合调试）
const browser = await chromium.launch({ headless: false });

// 无头模式（后台运行，速度更快）
const browser = await chromium.launch({ headless: true });
```

**viewport（视口大小）- 默认移动端**
```javascript
const context = await browser.newContext({
  viewport: { width: 375, height: 800 }  // 375x800
});
```

**userAgent（浏览器标识）- 默认移动端**
```javascript
const context = await browser.newContext({
  userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
});
```

**isMobile（移动设备模拟）**
```javascript
const context = await browser.newContext({
  isMobile: true  // 开启移动设备模拟
});
```

### 输出文件

**自动生成的文件：**
```
screenshots/
├── 1716982345678_www_example_com_content.png        # 全屏截图
├── 1716982345678_www_example_com_content.txt        # 页面文本
├── 1716982345678_www_example_com_article.png        # 元素截图
└── 1716982345678_www_example_com_error.png         # 错误截图
```

**文件命名规则：**
- 时间戳 + URL 哈希 + 后缀
- URL 哈希：移除 `https://` 并替换非字母数字字符为下划线

## 技术实现

基于 Node.js Playwright 库实现，提供以下功能：
- 智能页面加载等待
- 自动资源拦截
- 元素定位和截图
- 文本内容提取
- 错误处理和日志

实现文件：
- `playwright-cmd.js` - 命令行接口
- `playwright-crawler-v3.js` - 核心抓取功能

## 依赖

- Node.js (>=16.0.0)
- Playwright (v1.58.2+)
- Chromium 浏览器（已自动安装）

## 安装

Skill 已内置所有依赖，无需额外安装：
```bash
# 直接使用即可
playwright:fetch https://example.com
```
