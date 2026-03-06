# Sketch Illustration Prompt Guide

## 基础模板（必须包含的风格关键词）

```
Whimsical hand-drawn sketch illustration, very soft muted pastel colors, light blue-white background, product explainer style like Notion or Linear website. All text labels and annotations in Chinese. Pencil sketch lines, light watercolor wash, no harsh colors, gentle pastel palette (light blue, soft peach, pale yellow, light gray), charming and friendly, clean minimal layout, white card background with subtle shadow.

At the top center, a clear bold handwritten-style title in Chinese: '[标题]'.

[在这里插入具体内容描述]
```

## 常用元素描述

### 人物（猫南北/用户）
```
a simple cute stick figure person (representing the user 猫南北)
```

### 吉祥物（小龙虾/AI）
```
a cute friendly red lobster character (representing the AI assistant 小龙虾) sitting at a desk, helpful expression
```

### 流程箭头
```
connected by soft dashed arrows, small handwritten-style Chinese annotation labels
```

### 信息框/卡片
```
rounded rectangle boxes with soft colored tint, subtle drop shadow
```

## 场景模板

### 消息格式降级链
```
Whimsical hand-drawn sketch illustration, very soft muted pastel colors, light blue-white background, product explainer style like Notion or Linear website. All text labels and annotations in Chinese.

At the top center, a clear bold handwritten-style title: '飞书消息格式降级链'.

Left: a simple cute stick figure person (猫南北) sending a chat message.
Center: a cute friendly red lobster (小龙虾) at a computer, processing the message.
Right: vertical flowchart showing message format fallback chain:
- Top box '富文本' (soft green tint, document icon)
- Middle box '互动卡片' (soft yellow tint, card icon)  
- Bottom box '纯文本' (soft gray tint, text icon)
Downward dashed arrows between boxes labeled '格式降级', annotation '发送失败时自动降级'.

Pencil sketch lines, light watercolor wash, gentle pastel palette, charming and friendly, clean minimal layout.
```

### 功能流程图（通用）
```
Whimsical hand-drawn sketch illustration, very soft muted pastel colors, light blue-white background, product explainer style like Notion or Linear website. All text labels in Chinese.

[步骤1描述] → [步骤2描述] → [步骤3描述]
Connected by hand-drawn dashed arrows. Small annotated labels in Chinese handwriting style.
Simple stick figure for the user, cute lobster mascot for the AI.

Pencil sketch lines, light watercolor wash, gentle pastel palette, clean minimal layout.
```

### 对比图（A vs B）
```
Whimsical hand-drawn sketch illustration, soft pastel colors, light background. All text in Chinese.

Split into two panels:
Left panel labeled '[A方案]': [描述]
Right panel labeled '[B方案]': [描述]
Center dividing line with subtle style.

Hand-drawn style, watercolor wash, stick figure characters, friendly and clean.
```

## 调优技巧

- 颜色太饱和：加 `very muted, desaturated, soft watercolor only`
- 中文字显示差：加 `clear readable Chinese text, printed style not cursive`
- 内容太复杂：拆分为多张图，每张聚焦一个步骤
- 风格不够手绘：加 `rough pencil texture, imperfect lines, sketchy`
