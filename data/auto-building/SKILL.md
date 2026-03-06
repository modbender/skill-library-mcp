---
name: auto-building
description: 基于 AUTO-BUILDING 源码，生成定制化信息采集管理系统。用户指定栏目、分类、数据源后，系统自动采集、审核、发布内容。
version: 1.0.0
homepage: https://sora.wboke.com/
emoji: 🏗️
metadata:
  openclaw:
    requires:
      bins:
      - node
      - npm
    install:
    - id: clone
      kind: clone
      repo: hasd52636-a11y/Auto_Building_new
      label: Clone AUTO-BUILDING 源码
---

# AUTO-BUILDING
基于 AI 的自动化信息采集管理系统技能。

## 什么是 AUTO-BUILDING
AUTO-BUILDING 是一个开源的信息采集管理平台，可以帮助用户快速构建定制化的内容采集系统。用户只需指定想要采集的栏目、分类和数据源，系统会自动完成采集、审核、展示的全流程。

## 何时使用此技能
当用户想要：
- 构建自己的新闻早报系统
- 监控系统监控竞品价格和动态
- 采集特定行业资讯（如科技、财经、医疗）
- 建立资源导航页面（如 AI 工具集、开源项目）
- 定制化信息聚合平台

## 快速开始

### 步骤 1：克隆源码
```bash
git clone https://github.com/hasd52636-a11y/Auto_Building_new
cd Auto_Building_new
```

### 步骤 2：安装依赖
```bash
npm install
```

### 步骤 3：启动服务
```bash
npm run dev
```

### 步骤 4：访问
- 首页：`http://localhost:3000`
- 管理后台：`http://localhost:3000/admin`

## 如何根据用户需求生成系统

### 步骤 1：理解用户需求
当用户提出需求时，识别：
1. **目标栏目**（如：新闻早报、产品监控、行业资讯）
2. **分类规则**（如：科技/财经/体育、亚马逊/淘宝/京东）
3. **数据来源**（如：36kr、虎嗅、GitHub 仓库、RSS 订阅）

### 步骤 2：修改配置文件
根据用户需求修改以下文件：

#### 2.1 修改 `config/sources.json`
```json
{
  "primaryCategories": ["智能母体", "用户想要的栏目"],
  "secondaryCategories": {
    "智能母体": ["agent", "skill", "mcp", "prompt", "opensource_soft"],
    "用户想要的栏目": ["分类1", "分类2", "分类3"]
  },
  "sources": [
    {
      "name": "数据源名称",
      "type": "github|rss|directory|custom",
      "url": "地址",
      "enabled": true
    }
  ]
}
```

#### 2.2 修改 `src/data/resources.ts`
```typescript
export const PRIMARY_CATEGORIES = [
  '智能母体',
  '用户想要的栏目',
];

export const SECONDARY_CATEGORIES = [
  { labelKey: 'type.agent', value: 'agent' },
  { labelKey: 'type.skill', value: 'skill' },
  { labelKey: 'type.分类1', value: 'category1' },
  { labelKey: 'type.分类2', value: 'category2' },
];
```

### 步骤 3：指导用户配置
告诉用户执行以下操作：
1. 运行 `npm install && npm run dev`
2. 访问 `http://localhost:3000/admin`
3. 在「采集规则」Tab 添加具体采集规则
4. 在「数据源」Tab 确认数据源已添加
5. 点击「执行采集」开始采集内容
6. 在「审核」Tab 审核采集的内容
7. 内容自动展示在首页

## 配置说明

### 数据源类型
| 类型 | 说明 | 示例 |
|------|------|------|
| `github` | GitHub 仓库 | `composiohq/awesome-claude-skills` |
| `rss` | RSS 订阅 | `https://36kr.com/feed/` |
| `directory` | 目录网站 | `https://skills.sh/` |
| `custom` | 自定义 URL | 任意网页地址 |

### 采集规则
用户可通过管理后台 `/admin` 的「采集规则」Tab：
- 手动添加正则匹配规则
- 使用 AI 自然语言生成规则
- 设置关键词过滤
- 设置内容类型（视频/图文/全部）

## 示例对话

### 示例 1：新闻早报系统
**用户**："帮我做个科技新闻早报，每天采集36kr和虎嗅"
**修改内容**：
`config/sources.json`:
```json
{
  "primaryCategories": ["智能母体", "新闻早报"],
  "secondaryCategories": {
    "新闻早报": ["科技", "财经", "创投"]
  },
  "sources": [
    {
      "name": "36kr",
      "type": "rss",
      "url": "https://36kr.com/feed/",
      "enabled": true
    },
    {
      "name": "虎嗅",
      "type": "rss",
      "url": "https://www.huxiu.com/rss",
      "enabled": true
    }
  ]
}
```
**告诉用户**：
```
系统已配置完成！运行以下命令启动：
cd Auto_Building_new
npm install
npm run dev

然后访问 http://localhost:3000/admin
1. 在「采集规则」添加：只采集今天发布的文章
2. 点击「执行采集」
3. 在「审核」Tab 审核内容
```

### 示例 2：产品监控系统
**用户**："做个电商产品价格监控系统，监控亚马逊和淘宝"
**修改内容**：
`config/sources.json`:
```json
{
  "primaryCategories": ["智能母体", "产品监控"],
  "secondaryCategories": {
    "产品监控": ["亚马逊", "淘宝", "京东"]
  },
  "sources": [
    {
      "name": "亚马逊",
      "type": "directory",
      "url": "https://www.amazon.cn",
      "enabled": true
    },
    {
      "name": "淘宝",
      "type": "directory",
      "url": "https://www.taobao.com",
      "enabled": true
    }
  ]
}
```

### 示例 3：AI 工具集
**用户**："我想做一个 AI 编程工具导航页面"
**修改内容**：
`config/sources.json`:
```json
{
  "primaryCategories": ["AI编程工具"],
  "secondaryCategories": {
    "AI编程工具": ["代码补全", "代码审查", "自动化测试"]
  },
  "sources": [
    {
      "name": "GitHub Copilot",
      "type": "github",
      "repo": "github/copilot",
      "enabled": true
    },
    {
      "name": "Cursor",
      "type": "github",
      "repo": "getcursor/cursor",
      "enabled": true
    }
  ]
}
```

## 核心功能（不可修改）
- 采集脚本：`scripts/scrape-all.ts`, `scripts/classify.ts`
- 审核流程：`pending-review.json` → `approved-resources.json`
- 展示极面：动态读取配置渲染栏目和分类

## 注意事项
1. **只修改配置文件**：`config/sources.json` 和 `src/data/resources.ts`
2. **不要修改采集脚本和页面逻辑**
3. 运行后需要执行 `npm run daily` 采集内容
4. 在 `/admin` 审核采集的内容后才会展示在首页
5. 如果需要更多自定义，可以通过管理后台的「采集规则」和「数据源」Tab 进行配置