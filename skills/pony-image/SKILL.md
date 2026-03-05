---
name: pony-image-agent
description: AI 商业图片生成工具，支持单图生成、风格复刻、套图生成三大能力
metadata: {"openclaw":{"requires":{"env":["PONY_SUPABASE_ANON_KEY"]},"primaryEnv":"PONY_SUPABASE_ANON_KEY"}}
---

# Pony Image Agent — AI 商业图片生成

> 版本: v2.0 | 最后更新: 2026-02-23

## 环境配置

本技能需要以下环境变量：

- `PONY_SUPABASE_ANON_KEY` — Supabase anon 公钥（JWT 格式，以 `eyJ` 开头）

API 基础地址（固定）：

```
BASE_URL=https://vecarpahagopuqbwxbjh.supabase.co/functions/v1
```

所有请求需携带以下 Header：

```
Authorization: Bearer $PONY_SUPABASE_ANON_KEY
Content-Type: application/json
```

---

## 快速决策

🤔 **不知道选哪个功能？按以下决策树选择：**

1. 有参考图片想复制风格吗？ → **风格复刻** (`/image replicate`)
2. 需要多张主题统一的图片？ → **套图生成** (`/image suite`)
3. 只需要一张新图片？ → **单图生成** (`/image generate`)

---

## 对话式交互指南

### 🎨 场景1：单图生成

**何时使用**：只需要一张新图片，无需参考图

**对话示例**：
```
用户：帮我生成一张产品图
助手：好的！请告诉我：
  1. 产品描述是什么？
  2. 想要什么风格？（product/lifestyle/minimalist/vintage/dark）
  3. 图片比例？（默认 1:1）
```

**执行方式**：收集完信息后，执行以下命令：

```bash
curl -s -X POST "$BASE_URL/generate-image" \
  -H "Authorization: Bearer $PONY_SUPABASE_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "用户描述的内容",
    "style": "minimalist",
    "ratio": "1:1"
  }'
```

**返回格式**：
```json
{
  "imageUrl": "data:image/png;base64,...",
  "prompt": "增强后的完整 prompt"
}
```

将 `imageUrl` 展示给用户即可。

---

### 🖼️ 场景2：风格复刻（两步流程）

**何时使用**：有参考图片，想让新图片保持相同视觉风格

**对话示例**：
```
用户：我想复刻这张图的风格
助手：收到参考图！正在分析风格...

（执行 Step 1）

助手：✅ 风格分析完成：
  - 主色调：暖金色
  - 光影：柔和侧光
  - 构图：居中对称
  
  请上传你的产品图，我将按此风格生成新图。
```

**Step 1 — 分析参考图风格**：

```bash
curl -s -X POST "$BASE_URL/replicate-image" \
  -H "Authorization: Bearer $PONY_SUPABASE_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "analyze",
    "referenceImages": ["参考图URL或Base64"]
  }'
```

返回 `plan` 对象，包含 `styleAnalysisSummary`、`colorSystem`、`photographyStyle` 等。

**Step 2 — 用风格生成新图**：

```bash
curl -s -X POST "$BASE_URL/replicate-image" \
  -H "Authorization: Bearer $PONY_SUPABASE_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "productImages": ["产品图URL或Base64"],
    "plan": { "...Step1返回的plan对象..." },
    "ratio": "1:1"
  }'
```

返回 `imageUrl`（生成的图片）。

---

### 📦 场景3：套图生成（两步流程）

**何时使用**：需要一组视觉统一的系列图片（如电商主图+详情图）

**对话示例**：
```
用户：帮我生成一组电商产品图
助手：好的！我需要了解：
  1. 产品名称和描述？
  2. 需要哪些场景？（主图/场景图/细节图/对比图）
  3. 整体风格偏好？
  
  我会先生成统一设计方案，确认后再逐张生成。
```

**Step 1 — 生成统一设计方案**：

```bash
curl -s -X POST "$BASE_URL/generate-suite-plan" \
  -H "Authorization: Bearer $PONY_SUPABASE_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "productName": "产品名称",
    "productDesc": "产品描述",
    "scenes": ["主图", "场景图", "细节图"],
    "style": "minimalist",
    "ratio": "1:1"
  }'
```

返回 `plan` 对象，包含 `overallDesign`（配色、字体、光影）和每张图的 `images` 数组。

**Step 2 — 逐张生成**：对 `plan.images` 中每张图，将 `overallDesign` + 该图信息合并到 prompt，调用：

```bash
curl -s -X POST "$BASE_URL/generate-image" \
  -H "Authorization: Bearer $PONY_SUPABASE_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "合并 overallDesign 和 images[i] 信息的完整描述",
    "style": "minimalist",
    "ratio": "1:1"
  }'
```

---

## 参数参考

### 风格预设 (style)

| 值 | 说明 | 适用场景 |
|------|------|----------|
| `product` | 专业产品摄影，干净背景，影棚灯光 | 电商主图、产品展示 |
| `lifestyle` | 生活场景，自然环境，温暖氛围 | 社交媒体、品牌故事 |
| `minimalist` | 极简风格，白色背景，现代感 | 官网、品牌手册 |
| `vintage` | 复古美学，暖色调，怀旧感 | 文艺品牌、咖啡/手工艺 |
| `dark` | 暗调高级感，戏剧性灯光，高对比 | 科技产品、奢侈品 |

### 宽高比预设 (ratio)

| 值 | 适用场景 |
|------|----------|
| `1:1` | Instagram 帖子、电商主图 |
| `3:4` | 产品详情页 |
| `4:5` | Instagram 竖版帖子 |
| `9:16` | 手机竖屏、TikTok/抖音 |
| `4:3` | 横版展示 |
| `16:9` | 网页横幅、YouTube 封面 |
| `2:3` | 海报、杂志 |
| `21:9` | 超宽电影画幅 |

### AI 模型 (model)

| 值 | 说明 |
|------|------|
| `google/gemini-2.5-flash-image` | 默认，快速生成，仅 1K |
| `google/gemini-3-pro-image-preview` | 高质量，支持 2K/4K |

---

## 错误处理

| HTTP 状态 | 错误信息 | 解决方案 |
|-----------|----------|----------|
| 401 | Unauthorized | 检查 `PONY_SUPABASE_ANON_KEY` 是否已配置 |
| 429 | 请求频率超限 | 等待几秒后重试 |
| 402 | AI 额度不足 | 充值后继续使用 |
| 500 | 图片生成失败 | 简化 prompt 描述，避免过长内容 |

---

## 限制

- 单次请求超时 60 秒
- Base64 图片大小建议 < 4MB
- 生成结果为 Base64 格式
- 2K/4K 分辨率仅限 Pro 模型
