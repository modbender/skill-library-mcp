---
name: openclaw-visual
description: |
  将 OpenClaw 中的信息（PhoenixClaw 日志、聊天记录、单条消息等）转换为精美排版的图片，
  便于在聊天窗口（Telegram/Slack/Discord 等）中直接展示和分享。

  Use when:
  - 用户要求将内容做成图片 ("帮我把这段话做成图片")
  - 用户要求生成日志可视化 ("生成今日日志分享图")
  - 用户要求将聊天记录可视化 ("把今天的对话做成总结图")
depends:
  - node-html-to-image
metadata:
  version: 0.0.1
---

# OpenClaw Visual - 精美图文生成器

将 OpenClaw 中的任何信息转换为精美排版的图片，直接在聊天窗口中展示。

**设计风格**: 现代极简 / 瑞士风格 / 编辑排版
**核心流程**: 内容 → HTML 模板 → 本地生成图片 → OpenClaw 发送图片给用户

**图片生成**: 本地渲染，无需外部 API
- **默认**: `node-html-to-image` (轻量快速)
- **高级**: `playwright` (用户要求精美/复杂效果时)

## 🎯 使用场景

### 1. 单条消息转图片
用户说: "帮我把这段话做成好看的分享图"

AI 将：
1. 分析内容类型（金句/引用/想法）
2. 选择合适模板（引用卡片/金句卡片）
3. 生成精美图片
4. 在聊天窗口发送图片

### 2. PhoenixClaw 日志可视化
用户说: "生成今天的日志分享图"

AI 将：
1. 读取 `~/PhoenixClaw/Journal/daily/YYYY-MM-DD.md`
2. 解析 frontmatter 和 sections
3. 选择模板（社交卡片/手账风格）
4. 生成精美图片
5. 在聊天窗口发送图片

### 3. 聊天记录摘要
用户说: "把今天的对话做成总结图"

AI 将：
1. 扫描今日会话记录
2. 提取关键信息
3. 生成时间线/仪表盘风格图片
4. 在聊天窗口发送图片

## 🛠️ 核心工作流

### 步骤 1: 内容识别

分析用户请求，识别内容类型：

| 内容类型 | 识别方式 | 示例 |
|---------|---------|------|
| 单条消息 | 用户直接提供文本 | "帮我把这段话做成图片" |
| PhoenixClaw 日志 | 用户提及日志/日记 | "生成今日日志图" |
| 聊天记录 | 用户提及对话/聊天 | "把今天的对话做成图" |
| 引用/金句 | 文本包含引号或哲理内容 | 名言警句 |

### 步骤 2: 模板选择

根据内容类型自动选择最佳模板：

**quote-card** - 金句/引用卡片
- 适用: 名言、哲理、简短感悟
- 尺寸: 800x800 (方形，适合 Instagram)
- 特点: 大字体编辑排版、纯色背景、无装饰引号、SVG 图标
- 主题: light / dark / accent / blue

**moment-card** - 瞬间/时刻卡片
- 适用: 单张照片 + 描述
- 尺寸: 800x1000 (竖版)
- 特点: 杂志风格、大图留白、时间/位置 SVG 图标

**daily-journal** - 日记编辑风格
- 适用: PhoenixClaw 完整日志
- 尺寸: 800x1200 (竖版)
- 特点: 瑞士网格系统、清晰层级、SVG 图标、大日期数字

**social-share** - 社交媒体卡片
- 适用: 分享亮点/成就
- 尺寸: 1200x630 (OG Image)
- 特点: 双栏布局、纯色/深色主题、统计数据展示

**dashboard** - 数据仪表盘
- 适用: 周/月度汇总、统计数据
- 尺寸: 1200x800 (横版)
- 特点: 数据可视化、单色图表、网格布局、SVG 图标

### 步骤 3: HTML/CSS 生成

根据选定模板，填充内容生成 HTML：

1. 读取模板文件 `assets/templates/{template-name}.html`
2. 替换占位符变量:
   - `{{TITLE}}` - 标题
   - `{{CONTENT}}` - 主要内容
   - `{{DATE}}` - 日期
   - `{{MOOD}}` - 心情文字
   - `{{ENERGY}}` - 能量值
   - `{{IMAGE_URL}}` - 图片 URL
3. 应用基础样式 `assets/css/base-styles.css`
4. 使用系统字体栈 (无需外部字体):
   - 中文: system-ui, PingFang SC, Microsoft YaHei
   - 英文: system-ui, Segoe UI, Roboto

### 步骤 4: 图片生成

使用本地脚本生成图片：

```bash
# 调用本地生成脚本
node scripts/generate-image.js \
  --template quote-card \
  --content '{"QUOTE":"行动是治愈恐惧的良药","AUTHOR":"威廉·詹姆斯"}' \
  --output ~/OpenClaw/Visuals/output.png
```

**渲染引擎选择**:
- **默认** (`node-html-to-image`): 轻量快速，适合大多数场景
- **高级** (`playwright`): 当用户要求"精美/复杂/高级"效果时自动切换

### 步骤 5: 返回结果

脚本返回 JSON 结果：

```json
{
  "success": true,
  "outputPath": "/Users/xxx/OpenClaw/Visuals/output.png",
  "renderer": "nodejs",
  "template": "quote-card",
  "dimensions": { "width": 800, "height": 800 }
}
```

OpenClaw 读取生成的图片文件并发送给用户。

## 📋 模板详情

### quote-card (金句卡片)

**适用场景**: 名言、哲理、简短感悟

**布局**:
```
┌─────────────────────┐
│                     │
│      "引用内容"      │
│                     │
│    —— 作者/来源      │
│                     │
│  [装饰元素]  [日期]  │
└─────────────────────┘
```

**样式特点**:
- 渐变背景 (紫→粉 / 蓝→青 / 橙→红)
- 大号衬线字体 (Playfair Display / 霞鹜文楷)
- 装饰性引号
- 底部装饰线和日期

**变量**:
- `{{QUOTE}}` - 引用内容
- `{{AUTHOR}}` - 作者/来源
- `{{DATE}}` - 日期 (可选)
- `{{THEME}}` - 配色主题 (purple/blue/orange)

---

### moment-card (瞬间卡片)

**适用场景**: 单张照片 + 描述

**布局**:
```
┌─────────────────────┐
│  [照片]             │
│                     │
│  🕐 时间            │
│                     │
│  描述文字...        │
│                     │
│  [心情 emoji]       │
└─────────────────────┘
```

**样式特点**:
- 照片占 60% 高度
- 圆角设计
- 时间戳带图标
- 心情 emoji 装饰

**变量**:
- `{{IMAGE_URL}}` - 照片 URL (需为公开可访问)
- `{{TIME}}` - 时间
- `{{DESCRIPTION}}` - 描述
- `{{MOOD}}` - 心情 emoji

---

### daily-journal (日记手账)

**适用场景**: PhoenixClaw 完整日志

**布局**:
```
┌─────────────────────┐
│  📅 日期  星期       │
│  😊 心情  ⚡ 能量    │
│  ─────────────────  │
│  ✨ Highlights      │
│  • 成就1            │
│  • 成就2            │
│                     │
│  🖼️ Moments         │
│  [照片] [照片]      │
│                     │
│  💭 Reflections     │
│  反思内容...        │
│                     │
│  🌱 Growth          │
│  成长笔记...        │
└─────────────────────┘
```

**样式特点**:
- 米黄色纸质背景
- 手绘风格边框
- 贴纸式 emoji
- 分栏布局

**变量**:
- `{{DATE}}` - 日期
- `{{WEEKDAY}}` - 星期
- `{{MOOD}}` - 心情
- `{{ENERGY}}` - 能量
- `{{HIGHLIGHTS}}` - 亮点列表
- `{{MOMENTS}}` - 瞬间列表
- `{{REFLECTIONS}}` - 反思
- `{{GROWTH}}` - 成长笔记

---

### social-share (社交分享)

**适用场景**: 分享亮点/成就

**布局**:
```
┌─────────────────────────────┐
│                             │
│        ✨ 今日亮点          │
│                             │
│    "完成了重要里程碑"       │
│                             │
│    📊 3 个任务完成          │
│    🎯 效率 95%              │
│                             │
│         [Logo]              │
└─────────────────────────────┘
```

**样式特点**:
- 1200x630 横向布局
- 渐变背景
- 大标题 + 统计数据
- 底部品牌标识

**变量**:
- `{{TITLE}}` - 标题
- `{{SUBTITLE}}` - 副标题
- `{{STATS}}` - 统计数据
- `{{DATE}}` - 日期

---

### dashboard (数据仪表盘)

**适用场景**: 周/月度汇总

**布局**:
```
┌──────────────────────────────────────┐
│  📊 本周总结          2026-W05       │
│  ─────────────────────────────────── │
│  [心情趋势图]  [能量分布图]           │
│                                      │
│  关键指标:                           │
│  ✅ 完成: 15  📝 日记: 7  📸 照片: 12 │
│                                      │
│  时间线:                             │
│  Mon → Tue → Wed → Thu → Fri         │
└──────────────────────────────────────┘
```

**样式特点**:
- 深色背景
- 数据可视化
- 时间线展示
- 关键指标卡片

**变量**:
- `{{PERIOD}}` - 周期 (本周/本月)
- `{{DATE_RANGE}}` - 日期范围
- `{{MOOD_DATA}}` - 心情数据
- `{{ENERGY_DATA}}` - 能量数据
- `{{STATS}}` - 统计数据
- `{{TIMELINE}}` - 时间线事件

## 🔧 配置说明

### 前置要求

1. **安装依赖**:
   ```bash
   cd skills/openclaw-visual
   npm install
   ```

2. **(可选) 安装 Playwright** - 用于高级渲染:
   ```bash
   npm install playwright
   npx playwright install chromium
   ```

### 可选配置

在 `~/.openclaw/visual/config.yaml` 中可配置：

```yaml
# 默认模板
default_template: "quote-card"

# 默认配色主题
default_theme: "light"  # light/dark/accent/blue

# 渲染引擎
renderer: auto  # auto | nodejs | playwright
# auto 模式: 默认 nodejs, 用户要求"精美/复杂"时自动切换 playwright

# 输出设置
output:
  path: "~/OpenClaw/Visuals/"
  format: "png"  # png | jpeg
  quality: 90    # JPEG 质量 (1-100)
```

## 💡 使用示例

### 示例 1: 金句卡片

用户: "帮我把这句话做成图片: '行动是治愈恐惧的良药'"

AI:
1. 识别为金句类型
2. 选择 `quote-card` 模板
3. 生成 HTML 内容
4. 调用本地生成脚本:
   ```bash
   node scripts/generate-image.js \
     --template quote-card \
     --content '{"QUOTE":"行动是治愈恐惧的良药","AUTHOR":"威廉·詹姆斯","THEME":"light"}' \
     --output ~/OpenClaw/Visuals/quote-20240201.png
   ```
5. 读取生成的图片文件，在聊天窗口发送给用户

### 示例 2: 日志可视化

用户: "生成今天的日志分享图"

AI:
1. 读取 `~/PhoenixClaw/Journal/daily/2026-02-01.md`
2. 解析内容
3. 选择 `daily-journal` 或 `social-share` 模板
4. 生成并发送图片

### 示例 3: 聊天记录总结

用户: "把今天的对话做成总结图"

AI:
1. 扫描 `~/.openclaw/sessions/` 今日记录
2. 提取关键话题和决策
3. 选择 `dashboard` 或 `social-share` 模板
4. 生成并发送图片

## 📚 参考文档

- `references/templates.md` - 模板设计规范
- `references/content-parsing.md` - 内容解析规则
- `references/rendering-setup.md` - 本地渲染配置

## 🎨 扩展开发

### 添加新模板

1. 在 `assets/templates/` 创建新的 `.html` 文件
2. 定义模板变量占位符
3. 在 `references/templates.md` 添加文档
4. 更新模板选择逻辑

### 添加新主题

1. 在 CSS 中定义新的配色方案
2. 更新 `config.yaml` 中的主题选项
3. 在模板选择时传入 `{{THEME}}` 变量

---

## 设计原则

### 视觉风格
- **极简主义**: 去除多余装饰，留白充足
- **瑞士风格**: 网格系统，清晰层级
- **编辑排版**: 大字号标题，精致细节

### 配色方案
- **主色**: #1a1a1a (深灰)
- **辅色**: #525252, #737373, #a3a3a3 (灰度)
- **背景**: #fafafa, #f5f5f5 (米白)
- **强调**: #ea580c (橙红), #4f46e5 (靛蓝)

### 图标系统
使用 Lucide 风格 SVG 图标，替代所有 emoji：
- 所有图标内联在 HTML 中
- 统一 stroke-width: 1.5
- 支持通过 CSS 控制大小: .icon-sm, .icon-md, .icon-lg

### 字体策略
- 使用系统字体栈，无需加载外部字体
- 中文: system-ui, PingFang SC, Microsoft YaHei
- 英文: system-ui, Segoe UI, Roboto, Helvetica Neue

---

*OpenClaw Visual - 让每一条记录都值得被看见*
