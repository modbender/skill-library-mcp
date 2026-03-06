# Seedream 4.5 Prompt Engineering Guide

## Core Principles

### 1. Natural Language Description
Use clear, flowing natural language: **Subject + Action + Environment**
- ✅ "A girl in elegant clothes walking down a tree-lined avenue with a parasol, Monet oil painting style"
- ❌ "girl, umbrella, tree-lined street, oil painting brushstrokes"

### 2. Specify Use Case
State the image purpose and type when relevant.
- ✅ "Design a game company logo featuring a dog playing with a controller, text 'PITBULL'"
- ❌ "abstract image, dog with controller, PITBULL text"

### 3. Style Precision
Use precise style keywords or provide reference images.
- Keywords: 绘本, 儿童绘本, 水彩, 油画, 赛博朋克, 极简主义, 日式动漫

### 4. Text Rendering
Put text content in **double quotes** for accurate rendering.
- ✅ `生成一张海报，标题为 "Seedream 4.5"`
- ❌ `生成一张海报，标题为 Seedream 4.5`

### 5. Image Editing Clarity
Be explicit about what to edit AND what to preserve.
- ✅ "让图中最高的那只熊猫穿上粉色的京剧服饰，保持动作不变"
- ❌ "让它穿上粉色衣服"

---

## Prompt Templates by Task

### Text-to-Image
```
[主体描述], [行为/状态], [环境/背景], [风格/美学要求]
```
Example: 一位穿着维多利亚时代礼服的女子，手持蕾丝扇子站在玫瑰花园中，柔和的午后阳光，拉斐尔前派油画风格

### Image Editing
```
[操作动词: 增加/删除/替换/修改] + [目标对象的明确描述] + [具体要求] + [保持不变的部分]
```
Operations:
- **增加**: 给图中女生增加相同款式的银色耳线
- **删除**: 去掉女生的帽子
- **替换**: 把最大的面包人换成牛角包形象
- **修改**: 让机器人变成透明水晶材质

### Reference Image Generation
```
参考[图中的XX元素/风格], [生成内容描述], [具体要求]
```
- 人物: 参考图中的人物形象，生成一个动漫手办
- 风格: 参考图标的线性简约风格，设计9个应用icon
- 款式: 衣服款式与图中女生身上的衣服一致

### Multi-Image Fusion
```
将[图X的元素]与[图Y的元素]进行[操作], [额外要求]
```
- 替换: 将图一的主体替换为图二的主体
- 组合: 让图一人物穿上图二的服装
- 迁移: 参考图二的风格，对图一进行风格转换

### Sequential Image Generation
Use trigger words: 一系列, 一套, 组图, 共X张
```
生成[数量]张[类型], [内容描述], [一致性要求]
```
Example: 生成四张图，影视分镜，分别对应：宇航员维修飞船、遇到陨石带、紧急躲避、逃回飞船

---

## Visual Control Techniques

When text alone is insufficient, use visual markers on the reference image:

| Marker | Use Case | Prompt Pattern |
|--------|----------|----------------|
| 涂鸦/涂抹 | Area designation | 将红色涂抹位置放入电视 |
| 线框/方框 | Size/position | 放大标题至红框大小 |
| 箭头 | Direction/target | 箭头指向的位置添加XX |

---

## Recommended Sizes

| Aspect Ratio | Size | Use Case |
|--------------|------|----------|
| 1:1 | 2048x2048 | Social media, icons |
| 4:3 | 2304x1728 | Presentations |
| 3:4 | 1728x2304 | Portraits |
| 16:9 | 2560x1440 | Wallpapers, banners |
| 9:16 | 1440x2560 | Mobile wallpapers, stories |
| 21:9 | 3024x1296 | Ultra-wide, cinematic |

Use `2K` or `4K` with natural language aspect ratio description for automatic sizing.

---

## Common Style Keywords

### Art Styles
- 油画/oil painting, 水彩/watercolor, 素描/sketch
- 浮世绘, 国画/Chinese painting, 工笔画
- 像素风/pixel art, 矢量插画/vector illustration
- 3D渲染, 赛博朋克/cyberpunk, 蒸汽朋克/steampunk

### Photography Styles  
- 大片摄影, 电影画面/cinematic
- 特写/close-up, 远景/wide shot, 俯视/bird's eye
- 柔光/soft lighting, 逆光/backlit, 黄金时刻/golden hour

### Illustration Styles
- 绘本/picture book, 儿童绘本/children's book
- 日式动漫/anime, 美式漫画/comic
- 扁平化/flat design, 极简/minimalist
