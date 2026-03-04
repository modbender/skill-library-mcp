# 模板设计规范

## 模板列表

| 模板名称 | 文件名 | 尺寸 | 适用场景 |
|---------|--------|------|---------|
| quote-card | quote-card.html | 800x800 | 金句/引用 |
| moment-card | moment-card.html | 800x1000 | 瞬间/照片 |
| daily-journal | daily-journal.html | 800x1200 | 日记手账 |
| social-share | social-share.html | 1200x630 | 社交分享 |
| dashboard | dashboard.html | 1200x800 | 数据仪表盘 |

## 模板变量规范

### quote-card (金句卡片)

**必需变量:**
- `{{QUOTE}}` - 引用内容 (纯文本)

**可选变量:**
- `{{AUTHOR}}` - 作者/来源
- `{{DATE}}` - 日期
- `{{THEME}}` - 主题色 (purple/blue/orange/green/dark)

**示例:**
```json
{
  "QUOTE": "行动是治愈恐惧的良药",
  "AUTHOR": "威廉·詹姆斯",
  "DATE": "2026-02-01",
  "THEME": "purple"
}
```

---

### moment-card (瞬间卡片)

**必需变量:**
- `{{DESCRIPTION}}` - 描述文字

**可选变量:**
- `{{IMAGE_URL}}` - 照片 URL (需公开可访问)
- `{{TIME}}` - 时间
- `{{MOOD}}` - 心情 emoji

**示例:**
```json
{
  "IMAGE_URL": "https://example.com/photo.jpg",
  "TIME": "19:30",
  "DESCRIPTION": "回家路上看到的美丽日落",
  "MOOD": "😊"
}
```

---

### daily-journal (日记手账)

**必需变量:**
- `{{DATE}}` - 日期

**可选变量:**
- `{{WEEKDAY}}` - 星期
- `{{MOOD}}` - 心情 emoji
- `{{ENERGY}}` - 能量值
- `{{HIGHLIGHTS}}` - 是否有亮点部分 (boolean)
- `{{HIGHLIGHTS_LIST}}` - 亮点列表 (array)
- `{{MOMENTS}}` - 是否有瞬间部分 (boolean)
- `{{MOMENTS_CONTENT}}` - 瞬间内容 (HTML)
- `{{REFLECTIONS}}` - 是否有反思部分 (boolean)
- `{{REFLECTIONS_CONTENT}}` - 反思内容 (HTML)
- `{{GROWTH}}` - 是否有成长部分 (boolean)
- `{{GROWTH_CONTENT}}` - 成长内容 (HTML)

**示例:**
```json
{
  "DATE": "2026-02-01",
  "WEEKDAY": "Saturday",
  "MOOD": "😊",
  "ENERGY": "high",
  "HIGHLIGHTS": true,
  "HIGHLIGHTS_LIST": [
    "修好了困扰两天的 bug",
    "拍到了美丽的日落"
  ],
  "MOMENTS": true,
  "MOMENTS_CONTENT": "...",
  "REFLECTIONS": true,
  "REFLECTIONS_CONTENT": "...",
  "GROWTH": true,
  "GROWTH_CONTENT": "..."
}
```

---

### social-share (社交分享)

**必需变量:**
- `{{TITLE}}` - 标题
- `{{HEADLINE}}` - 主标题

**可选变量:**
- `{{SUBTITLE}}` - 副标题
- `{{THEME}}` - 主题色
- `{{STATS}}` - 是否有统计 (boolean)
- `{{STATS_LIST}}` - 统计数据列表
- `{{DATE}}` - 日期

**示例:**
```json
{
  "TITLE": "今日亮点",
  "HEADLINE": "完成了重要里程碑",
  "SUBTITLE": "项目提前一周交付",
  "THEME": "blue",
  "STATS": true,
  "STATS_LIST": [
    {"ICON": "✅", "VALUE": "15", "LABEL": "任务完成"},
    {"ICON": "🎯", "VALUE": "95%", "LABEL": "效率"}
  ],
  "DATE": "2026-02-01"
}
```

---

### dashboard (数据仪表盘)

**必需变量:**
- `{{PERIOD}}` - 周期 (本周/本月)

**可选变量:**
- `{{DATE_RANGE}}` - 日期范围
- `{{STATS}}` - 是否有统计 (boolean)
- `{{STATS_LIST}}` - 统计数据列表
- `{{MOOD_DATA}}` - 是否有心情数据 (boolean)
- `{{MOOD_CHART_BARS}}` - 心情图表 HTML
- `{{ENERGY_DATA}}` - 是否有能量数据 (boolean)
- `{{ENERGY_CHART_CONTENT}}` - 能量图表 HTML
- `{{TIMELINE}}` - 是否有时间线 (boolean)
- `{{TIMELINE_EVENTS}}` - 时间线事件列表

**示例:**
```json
{
  "PERIOD": "本周",
  "DATE_RANGE": "2026-W05 (01/27 - 02/02)",
  "STATS": true,
  "STATS_LIST": [
    {"ICON": "✅", "VALUE": "15", "LABEL": "完成任务"},
    {"ICON": "📝", "VALUE": "7", "LABEL": "日记天数"},
    {"ICON": "📸", "VALUE": "12", "LABEL": "记录瞬间"}
  ],
  "MOOD_DATA": true,
  "MOOD_CHART_BARS": "...",
  "TIMELINE": true,
  "TIMELINE_EVENTS": [
    {"DATE": "Mon", "EVENT": "项目启动"},
    {"DATE": "Wed", "EVENT": "完成原型"}
  ]
}
```

## 模板选择逻辑

```
内容类型判断:
├── 单条短文本 (< 100字)
│   └── 包含引号或哲理 → quote-card
│   └── 普通文本 → quote-card (默认)
├── 单张照片 + 描述
│   └── moment-card
├── PhoenixClaw 日志
│   ├── 用户要求社交分享 → social-share
│   └── 默认 → daily-journal
├── 周/月度汇总
│   └── dashboard
└── 聊天记录总结
    ├── 有统计数据 → dashboard
    └── 无统计数据 → social-share
```

## 添加新模板

1. 在 `assets/templates/` 创建 `.html` 文件
2. 使用 Mustache 语法定义变量: `{{VARIABLE}}`
3. 条件渲染: `{{#VAR}}...{{/VAR}}`
4. 在本文档添加模板规范
5. 在 `SKILL.md` 更新模板列表
6. 更新模板选择逻辑

## 样式规范

### 配色主题

- **purple**: #667eea → #764ba2 (优雅紫)
- **blue**: #4facfe → #00f2fe (清新蓝)
- **orange**: #fa709a → #fee140 (活力橙)
- **green**: #11998e → #38ef7d (自然绿)
- **dark**: #232526 → #414345 (深邃黑)

### 字体规范

- **中文标题**: LXGW WenKai (霞鹜文楷)
- **中文正文**: Noto Sans SC
- **英文标题**: Playfair Display
- **英文正文**: Inter

### 尺寸规范

- **社交卡片**: 1200x630 (OG Image 标准)
- **方形卡片**: 800x800 (Instagram)
- **竖版卡片**: 800x1000/1200 (Story)
- **横版卡片**: 1200x800 (Twitter)
