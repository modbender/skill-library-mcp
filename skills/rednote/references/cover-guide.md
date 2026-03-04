# 小红书封面图生成详细指南

## 封面图结构（3:4 = 1080x1440）

```
┌──────────────────┐
│                  │
│  AI 生成图片      │  上半部分 1080x720 (3:2)
│  (根据主题生成)    │
│                  │
├──────────────────┤
│                  │
│  纯色底 + 标题    │  下半部分 1080x720 (3:2)
│  「标题文字」      │
│                  │
└──────────────────┘
```

## AI 图片 Prompt 编写规范

- **风格关键词**：`clean, minimal, aesthetic, soft lighting, pastel colors, cozy atmosphere`
- **场景描述**：根据文案主题描述具体场景（如收纳→整洁的房间，美食→精致的摆盘）
- **禁止内容**：不包含文字、水印、人脸特写、logo
- **质量词**：`high quality, professional photography, 4k, detailed`
- **构图词**：`centered composition, top-down view, flat lay`（根据主题选择）
- **色调提示**：prompt 中要指明整体色调（如 warm tones、cool tones、pastel pink），方便后续底色与图片色调呼应

### Prompt 示例

- 居家收纳 → `A clean and organized living room with minimal furniture, soft natural lighting, warm beige and white tones, cozy aesthetic, high quality photography, no text no watermark`
- 美食探店 → `Delicious gourmet food beautifully plated on a wooden table, warm golden lighting, top-down flat lay photography, rich warm color palette, aesthetic food photography, no text no watermark`
- 穿搭分享 → `Stylish outfit flat lay on a cream linen sheet, aesthetic fashion photography, soft natural light, minimal composition, dusty rose and beige tones, no text no watermark`

## 配色搭配规则（重要）

Agent 必须根据主题和图片色调主动搭配底色与字色，不要用默认白底黑字。

### 原则

1. **底色与图片色调呼应**：底色应从 AI 图片的主色调中提取同色系的浅色/淡色
2. **字色与底色形成对比**：字色要在底色上清晰可读
3. **整体风格一致**：暖色主题用暖色搭配，冷色主题用冷色搭配
4. **小红书审美偏好**：偏向柔和、温暖、高级感的色调

### 配色参考库

底色必须有明显视觉辨识度，不能接近纯白。浅色底色明度控制在 75%-90% 之间。

| 风格 | 底色 | 字色 | 适用场景 | 视觉感受 |
|------|------|------|---------|---------|
| 奶油温暖 | `#F5E6D0` | `#6B4226` | 美食、烘焙、咖啡、家居 | 温馨舒适 |
| 蜜桃甜美 | `#FCDBD3` | `#D4545B` | 美妆、护肤、穿搭、恋爱 | 少女心 |
| 薄荷清新 | `#D4EDDF` | `#1B5E40` | 健身、户外、植物、环保 | 清新自然 |
| 雾蓝理性 | `#CEDAEB` | `#2B4A7C` | 科技、效率、学习、职场 | 专业冷静 |
| 薰衣草梦幻 | `#DDD0F0` | `#5A3A8A` | 旅行、艺术、香氛、冥想 | 浪漫高级 |
| 鹅黄活力 | `#F5ECC8` | `#8B6D0B` | 育儿、宠物、手工、日常 | 明亮温暖 |
| 烟粉优雅 | `#F2D5E5` | `#8B1C4E` | 婚礼、花艺、甜品、仪式感 | 精致浪漫 |
| 暗夜高级 | `#1C1C1E` | `#E8C872` | 奢侈品、数码、夜景、酒 | 高级沉稳 |
| 莫兰迪灰 | `#D5D0C8` | `#4A453F` | 极简、设计、建筑、摄影 | 高级克制 |
| 珊瑚活力 | `#FBCEC5` | `#C04030` | 运动、夏日、派对、潮流 | 热情洋溢 |

### 自定义搭配原则

- 浅色底色明度控制在 75%-90%，不能接近纯白（≥95%会显得平淡）
- 字色与底色需形成强对比，确保清晰可读
- 暗色底色（如暗夜高级）配亮色/金色字
- 底色饱和度适中（15%-35%），太低会像灰色，太高会抢 AI 图片视线
- 推荐从 AI 图片的主色调中吸色，降低饱和度作为底色
