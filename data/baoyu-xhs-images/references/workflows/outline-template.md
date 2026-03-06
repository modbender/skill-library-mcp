# Xiaohongshu Outline Template

Template for generating infographic series outlines with layout specifications.

## File Naming

Outline files use strategy identifier in the name:
- `outline-strategy-a.md` - Story-driven variant
- `outline-strategy-b.md` - Information-dense variant
- `outline-strategy-c.md` - Visual-first variant
- `outline.md` - Final selected (copied from chosen variant)

## Image File Naming

Images use meaningful slugs for readability:
```
NN-{type}-[slug].png
NN-{type}-[slug].md (in prompts/)
```

| Type | Usage |
|------|-------|
| `cover` | First image (cover) |
| `content` | Middle content images |
| `ending` | Last image |

**Examples**:
- `01-cover-ai-tools.png`
- `02-content-why-ai.png`
- `03-content-chatgpt.png`
- `04-content-midjourney.png`
- `05-content-notion-ai.png`
- `06-ending-summary.png`

**Slug rules**:
- Derived from image content (kebab-case)
- Must be unique within the series
- Keep short but descriptive (2-4 words)

## Layout Selection Guide

### Density-Based Layouts

| Layout | When to Use | Info Points | Whitespace |
|--------|-------------|-------------|------------|
| sparse | Covers, quotes, impact statements | 1-2 | 60-70% |
| balanced | Standard content, tutorials | 3-4 | 40-50% |
| dense | Knowledge cards, cheat sheets | 5-8 | 20-30% |

### Structure-Based Layouts

| Layout | When to Use | Structure |
|--------|-------------|-----------|
| list | Rankings, checklists, steps | Numbered/bulleted vertical |
| comparison | Before/after, pros/cons | Left vs right split |
| flow | Processes, timelines | Connected nodes with arrows |

### Position-Based Recommendations

| Position | Recommended | Reasoning |
|----------|-------------|-----------|
| Cover | sparse | Maximum impact, clear title |
| Setup | balanced | Context without overwhelming |
| Core | balanced/dense/list | Match content density |
| Payoff | balanced/list | Clear takeaways |
| Ending | sparse | Clean CTA, memorable |

## Outline Format

```markdown
# Xiaohongshu Infographic Series Outline

---
strategy: a  # a, b, or c
name: Story-Driven
style: notion
default_layout: dense
image_count: 6
generated: YYYY-MM-DD HH:mm
---

## Image 1 of 6

**Position**: Cover
**Layout**: sparse
**Hook**: 打工人必看！
**Slug**: ai-tools
**Filename**: 01-cover-ai-tools.png

**Text Content**:
- Title: 「5个AI神器让你效率翻倍」
- Subtitle: 亲测好用，建议收藏

**Visual Concept**:
科技感背景，多个AI工具图标环绕，中心大标题，
霓虹蓝+深色背景，未来感十足

**Swipe Hook**: 第一个就很强大👇

---

## Image 2 of 6

**Position**: Content
**Layout**: balanced
**Core Message**: 为什么你需要AI工具
**Slug**: why-ai
**Filename**: 02-content-why-ai.png

**Text Content**:
- Title: 「为什么要用AI？」
- Points:
  - 重复工作自动化
  - 创意辅助不卡壳
  - 效率提升10倍

**Visual Concept**:
对比图：左边疲惫打工人，右边轻松使用AI的人
科技线条装饰，简洁有力

**Swipe Hook**: 接下来是具体工具推荐👇

---

## Image 3 of 6

**Position**: Content
**Layout**: dense
**Core Message**: ChatGPT使用技巧
**Slug**: chatgpt
**Filename**: 03-content-chatgpt.png

**Text Content**:
- Title: 「ChatGPT」
- Subtitle: 最强AI助手
- Points:
  - 写文案：给出框架，秒出初稿
  - 改文章：润色、翻译、总结
  - 编程：写代码、找bug
  - 学习：解释概念、出题练习

**Visual Concept**:
ChatGPT logo居中，四周放射状展示功能点
深色科技背景，霓虹绿点缀

**Swipe Hook**: 下一个更适合创意工作者👇

---

## Image 4 of 6

**Position**: Content
**Layout**: dense
**Core Message**: Midjourney绘图
**Slug**: midjourney
**Filename**: 04-content-midjourney.png

**Text Content**:
- Title: 「Midjourney」
- Subtitle: AI绘画神器
- Points:
  - 输入描述，秒出图片
  - 风格多样：写实/插画/3D
  - 做封面、做头像、做素材
  - 不会画画也能当设计师

**Visual Concept**:
展示几张MJ生成的不同风格图片
画框/画布元素装饰

**Swipe Hook**: 还有一个效率神器👇

---

## Image 5 of 6

**Position**: Content
**Layout**: balanced
**Core Message**: Notion AI笔记
**Slug**: notion-ai
**Filename**: 05-content-notion-ai.png

**Text Content**:
- Title: 「Notion AI」
- Subtitle: 智能笔记助手
- Points:
  - 自动总结长文
  - 头脑风暴出点子
  - 整理会议记录

**Visual Concept**:
Notion界面风格，简洁黑白配色
展示笔记整理前后对比

**Swipe Hook**: 最后总结一下👇

---

## Image 6 of 6

**Position**: Ending
**Layout**: sparse
**Core Message**: 总结与互动
**Slug**: summary
**Filename**: 06-ending-summary.png

**Text Content**:
- Title: 「工具只是工具」
- Subtitle: 关键是用起来！
- CTA: 收藏备用 | 转发给需要的朋友
- Interaction: 你最常用哪个？评论区见👇

**Visual Concept**:
简洁背景，大字标题
底部互动引导文字
收藏/分享图标

---
```

## Swipe Hook Strategies

Each image should end with a hook for the next:

| Strategy | Example |
|----------|---------|
| Teaser | "第一个就很强大👇" |
| Numbering | "接下来是第2个👇" |
| Superlative | "下一个更厉害👇" |
| Question | "猜猜下一个是什么？👇" |
| Promise | "最后一个最实用👇" |
| Urgency | "最重要的来了👇" |

## Strategy Differentiation

Three strategies should differ meaningfully:

| Strategy | Focus | Structure | Page Count |
|----------|-------|-----------|------------|
| A: Story-Driven | Emotional, personal | Hook→Problem→Discovery→Experience→Conclusion | 4-6 |
| B: Information-Dense | Factual, structured | Core→Info Cards→Comparison→Recommendation | 3-5 |
| C: Visual-First | Atmospheric, minimal text | Hero→Details→Lifestyle→CTA | 3-4 |

**Example for "AI工具推荐"**:
- `outline-strategy-a.md`: Warm + Balanced - Personal journey with AI
- `outline-strategy-b.md`: Notion + Dense - Knowledge card style
- `outline-strategy-c.md`: Minimal + Sparse - Sleek tech aesthetic
