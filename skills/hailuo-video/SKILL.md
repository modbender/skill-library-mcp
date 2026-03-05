---
name: hailuo-video
description: 使用 MiniMax Hailuo 2.3 模型生成视频。当用户想要文生视频、图生视频，或提到 hailuo、海螺视频时使用此 skill。
category: video
tags: [video, image-to-video, text-to-video, hailuo, minimax]
featured: false
---

# MiniMax Hailuo 2.3 视频生成

MiniMax Hailuo 2.3 系列视频生成模型，支持图生视频和文生视频。分为 Fast（快速）和标准两个系列，每个系列有 Pro（1080p 高质量）和 Standard（768p 高性价比）两个版本。

## 可用模型

### Fast 系列（生成更快）

| 模型 ID | 功能 | 分辨率 | 价格 |
|--------|------|--------|------|
| `fal-ai/minimax/hailuo-2.3-fast/pro/image-to-video` | 图生视频 | 1080p | 132 积分/次 |
| `fal-ai/minimax/hailuo-2.3-fast/standard/image-to-video` | 图生视频 | 768p | 76 积分/6s, 128 积分/10s |

### 标准系列（质量更高）

| 模型 ID | 功能 | 分辨率 | 价格 |
|--------|------|--------|------|
| `fal-ai/minimax/hailuo-2.3/pro/image-to-video` | 图生视频 | 1080p | 196 积分/次 |
| `fal-ai/minimax/hailuo-2.3/pro/text-to-video` | 文生视频 | 1080p | 196 积分/次 |
| `fal-ai/minimax/hailuo-2.3/standard/image-to-video` | 图生视频 | 768p | 112 积分/6s, 224 积分/10s |
| `fal-ai/minimax/hailuo-2.3/standard/text-to-video` | 文生视频 | 768p | 112 积分/6s, 224 积分/10s |

## 工作流

### 1. 调用 submit_task

使用 MCP 工具 `submit_task` 提交任务。

**图生视频示例**：

```json
{
  "model_id": "fal-ai/minimax/hailuo-2.3/pro/image-to-video",
  "parameters": {
    "prompt": "The camera follows the mountain biker as they navigate a technical forest trail at high speed",
    "image_url": "https://example.com/input-image.jpg"
  }
}
```

**文生视频示例**：

```json
{
  "model_id": "fal-ai/minimax/hailuo-2.3/pro/text-to-video",
  "parameters": {
    "prompt": "The camera follows the snowboarder as they carve down the mountain through deep powder"
  }
}
```

**Standard 模型（可选时长）**：

```json
{
  "model_id": "fal-ai/minimax/hailuo-2.3/standard/text-to-video",
  "parameters": {
    "prompt": "An intense electrical storm rages over a modern city skyline at night",
    "duration": "10"
  }
}
```

### 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|-----|-------|------|
| prompt | string | **是** | - | 视频生成提示词 |
| image_url | string | 图生视频**是** | - | 首帧图片 URL（仅图生视频） |
| duration | string | 否 | "6" | 视频时长，"6" 或 "10"（仅 Standard 模型） |
| prompt_optimizer | boolean | 否 | true | 是否使用提示词优化器 |

## 查询任务状态

提交任务后会返回 `task_id`，使用 `get_task` 查询结果：

```json
{
  "task_id": "返回的任务ID"
}
```

任务状态：
- `pending` - 排队中
- `processing` - 处理中
- `completed` - 完成，结果在 `result` 中
- `failed` - 失败，查看 `error` 字段

## 模型选择建议

1. **追求速度** → 选 Fast 系列（`hailuo-2.3-fast`）
2. **追求质量** → 选标准系列（`hailuo-2.3`）
3. **追求高分辨率** → 选 Pro 版本（1080p）
4. **追求性价比** → 选 Standard 版本（768p，可选时长）
5. **有参考图片** → 选图生视频（image-to-video）
6. **纯文本描述** → 选文生视频（text-to-video）

## 提示词技巧

1. 描述具体的动作和场景变化，而不是静态画面
2. 包含镜头运动描述（如 "camera follows", "slow zoom in"）
3. 描述光线、氛围等视觉细节
4. 可以在提示词末尾添加音频描述（如 "Audio: wind rushing, birds chirping"）
