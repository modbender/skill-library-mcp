---
name: webfetch-md
version: 1.1.0
description: 抓取网页并转换为 Markdown，保留图片链接
author: ShiJianwen
metadata:
  openclaw:
    requires:
      bins: ["node"]
    tools:
      - name: webfetch-md
        description: 抓取任意网页并转换为 Markdown 格式，自动保留图片链接
        command: "node cli.js --url {{url}}"
        parameters:
          url:
            type: string
            description: 要抓取的网页 URL
            required: true
---

# WebFetch MD - 网页转 Markdown

抓取任意网页，转换为干净的 Markdown 格式，保留图片链接。

## 使用方法

### 作为 OpenClaw 工具调用

```yaml
webfetch-md url="https://example.com"
```

### CLI 使用

```bash
# 基本使用（输出 JSON 格式）
npx webfetch-md https://example.com

# 或使用 --url 参数
npx webfetch-md --url https://example.com

# 提取 Markdown 内容（配合 jq）
npx webfetch-md https://example.com | jq -r '.markdown'

# 保存到文件
npx webfetch-md https://example.com | jq -r '.markdown' > article.md
```

### 输出格式

CLI 和工具都输出统一的 JSON 格式：

```json
{
  "success": true,
  "title": "文章标题",
  "markdown": "# 文章标题\n\n正文内容...",
  "images": ["https://example.com/img1.png"],
  "imageCount": 1,
  "contentLength": 1523
}
```

### 作为模块使用

```javascript
const { fetchAsMarkdown } = require('./index');
const result = await fetchAsMarkdown('https://example.com');
console.log(result.markdown);
```

## 功能特点

- ✅ 抓取任意网页 HTML
- ✅ 智能提取正文内容（过滤导航、广告等）
- ✅ 保留图片链接（转换为 `![alt](url)` 格式）
- ✅ 自动转换相对路径为绝对路径
- ✅ 输出干净的 Markdown

## 依赖

- turndown: HTML to Markdown 转换
- cheerio: HTML 解析和提取

## 技术实现

### 核心流程
1. **网页抓取**：使用 fetch API 获取 HTML，模拟浏览器 User-Agent
2. **HTML解析**：使用 cheerio 加载和解析 HTML 内容
3. **内容提取**：智能识别正文区域，过滤无关元素
4. **URL处理**：将相对路径转换为绝对路径
5. **Markdown转换**：使用 turndown 转换为标准 Markdown 格式

### 智能内容提取算法
按优先级选择正文容器：
1. `article` 标签
2. `main` 标签  
3. `[role="main"]` 属性
4. `.post-content` / `.entry-content` 类
5. `.content` / `.post` 类
6. `#content` / `#main` ID
7. 回退到 `body` 标签

### 自动过滤的元素
- 脚本和样式标签
- 导航、页眉、页脚
- 侧边栏和广告区域
- 评论区

## 错误处理

工具返回统一的 JSON 格式，包含 `success` 字段标识操作状态：

```json
{
  "success": false,
  "error": "错误信息"
}
```

## 开发说明

### 项目结构
```
webfetch-md/
├── index.js          # 核心功能模块
├── cli.js           # CLI 和 OpenClaw 工具入口
├── package.json     # 依赖配置
├── test.js          # 测试脚本
└── SKILL.md         # 技能文档
```

### 测试
```bash
# 运行测试
npm test

# 或直接测试
node test.js https://example.com
```

## 版本历史

- **v1.1.0** (当前): 统一 CLI 和 OpenClaw 工具入口，优化错误处理
- **v1.0.1**: 基础功能实现，支持网页抓取和 Markdown 转换
- **v1.0.0**: 初始版本发布