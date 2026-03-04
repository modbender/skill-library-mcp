# Playwright Controller

智能网页浏览工具，基于 Playwright，自动等待页面加载，支持截图和文本提取。

## 技能名称

**playwright controller** - 专门用于网页浏览、截图和内容提取。

## 快速开始

## 快速开始

### 基本用法

```bash
playwright:fetch https://baike.baidu.com/item/兴盛优选/23451097
```

自动完成：
- ⏳ 等待 JS/CSS 加载完成
- 📸 截取全屏截图
- 📝 提取页面文本内容
- 💾 保存到 `./screenshots/` 目录

## 命令参考

### fetch - 获取网页

获取整个网页的内容和截图。

**语法：**
```bash
playwright:fetch <url>
```

**参数：**
- `<url>`: 目标网页 URL（必需）

**可选参数：**
- `--timeout=120000`: 超时时间（毫秒），默认 60000
- `--dir=/path`: 截图保存目录，默认 `./screenshots`

**示例：**
```bash
playwright:fetch https://baike.baidu.com/item/绊酸灵牙膏
playwright:fetch --timeout=120000 --dir=/Users/chenkuan/Desktop/screenshots https://baike.baidu.com/item/绊酸灵牙膏
```

### fetch-element - 获取元素

获取指定 CSS 选择器元素的截图和文本。

**语法：**
```bash
playwright:fetch-element --selector=".content" <url>
```

**参数：**
- `--selector=<selector>`: CSS 选择器（必需）
- `<url>`: 目标网页 URL（必需）

**示例：**
```bash
playwright:fetch-element --selector="h1" https://baike.baidu.com/item/绊酸灵牙膏
playwright:fetch-element --selector=".article-content" https://baike.baidu.com/item/绊酸灵牙膏
```

## 输出文件

执行后会生成以下文件（保存在指定目录）：

```
screenshots/
├── 1716982345678_www_baike_baidu_com_item_兴盛优选_23451097.png       # 全屏截图
├── 1716982345678_www_baike_baidu_com_item_兴盛优选_23451097_content.txt # 页面文本
├── 1716982345678_www_baike_baidu_com_item_兴盛优选_23451097_element.png # 元素截图
└── 1716982345678_www_baike_baidu_com_item_兴盛优选_23451097_error.png  # 错误截图
```

## 工作流程

1. **启动浏览器** - 使用 Chromium，约 2-3 秒
2. **设置拦截规则** - 跳过图片、CSS、字体等资源
3. **访问页面** - 等待 `networkidle`（网络空闲）
4. **等待渲染** - 额外等待 2 秒确保完全渲染
5. **截取截图** - 全屏 PNG 截图（1920x1080）
6. **提取文本** - 移除广告、脚本等元素，提取文本
7. **保存文件** - 截图和文本文件保存到指定目录

## 特点

### ✅ 智能加载等待
- 自动等待 JavaScript 和 CSS 加载完成
- 使用 `networkidle` 等待策略
- 额外等待 2 秒确保完全渲染

### ✅ 智能资源拦截
- 自动拦截图片、CSS、字体等资源
- 提高加载速度，减少数据传输
- 只保留文本和结构信息

### ✅ 全屏截图
- 高清 PNG 格式（1920x1080）
- 完整保存页面视觉信息
- 适合图像识别模型处理

### ✅ 文本提取
- 自动移除无关元素（广告、脚本、导航等）
- 提取纯净的页面文本内容
- 适合后续文本处理

### ✅ 错误处理
- 失败时自动保存截图
- 详细的错误信息输出
- 友好的用户提示

### ✅ 稳定可靠
- 使用有头模式便于调试
- 完善的错误处理机制
- 时间戳命名避免冲突

## 使用场景

### 1. 网页内容采集
```bash
playwright:fetch https://baike.baidu.com/item/兴盛优选/23451097
```

### 2. 网页截图保存
```bash
playwright:fetch https://www.xsyxsc.com/
```

### 3. 元素内容提取
```bash
playwright:fetch-element --selector=".content" https://baike.baidu.com/item/绊酸灵牙膏
```

### 4. 自定义目录保存
```bash
playwright:fetch --dir=/Users/chenkuan/Desktop/爬虫结果 https://baike.baidu.com/item/绊酸灵牙膏
```

## 技术细节

### 依赖
- Node.js
- Playwright (v1.58.2+)
- Chromium 浏览器

### 拦截规则
以下资源类型会被拦截：
- `image` - 图片
- `stylesheet` - CSS 样式
- `media` - 音视频
- `font` - 字体文件
- `websocket` - WebSocket 连接
- `manifest` - 应用清单

### 等待策略
- `networkidle` - 等待网络空闲（主策略）
- 2秒额外等待 - 确保完全渲染
- `domcontentloaded` - DOM 加载完成

### 截图规格
- 分辨率：1920x1080
- 格式：PNG（无损）
- 全屏：包含滚动内容

## 注意事项

1. **浏览器启动** - 首次使用需要启动浏览器，约 2-3 秒
2. **网络依赖** - 需要网络连接访问目标网页
3. **文件权限** - 确保目标目录有写入权限
4. **超时时间** - 复杂网页可能需要 60-120 秒
5. **有头模式** - 默认使用有头模式，可观察浏览器操作

## 故障排除

### 问题：找不到浏览器
**解决方案：** 首次使用会自动下载 Chromium，需要几分钟

### 问题：权限被拒绝
**解决方案：** 检查目标目录的写入权限

### 问题：超时错误
**解决方案：** 增加 `--timeout` 参数值
```bash
playwright:fetch --timeout=180000 <url>
```

### 问题：文件名过长
**解决方案：** 使用自定义目录，减少 URL 长度

## 版本信息

- **版本：** 1.0.0
- **发布时间：** 2026-02-28
- **作者：** chenkuan
- **更新日志：**
  - v1.0.0 (2026-02-28): 初始版本，支持基本网页抓取和截图功能

## 许可证

MIT License
