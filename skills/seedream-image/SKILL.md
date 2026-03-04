---
name: Seedream 4.5 图像生成
description: 使用 Seedream 4.5 模型生成或编辑图像。当用户想要文生图、图生图、图像编辑，或提到 seedream、字节跳动图像生成时使用此 skill。
category: image
tags: [图像生成, 文生图, 图像编辑, Seedream, 字节跳动]
featured: false
---

# Seedream 4.5 图像生成

使用字节跳动 Seedream 4.5 模型进行文生图和图生图（图像编辑）。

## 可用模型

| 模型 ID | 功能 | 说明 |
|--------|------|------|
| `fal-ai/bytedance/seedream/v4.5/text-to-image` | 文生图 | 根据提示词生成图像 |
| `fal-ai/bytedance/seedream/v4.5/edit` | 图生图 | 基于参考图进行编辑 |

## 文生图工作流

### 1. 调用 submit_task

使用 MCP 工具 `submit_task` 提交任务：

```json
{
  "model_id": "fal-ai/bytedance/seedream/v4.5/text-to-image",
  "parameters": {
    "prompt": "用户的提示词",
    "image_size": "auto_2K",
    "num_images": 1
  }
}
```

### 文生图参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|-----|-------|------|
| prompt | string | **是** | - | 图像生成提示词 |
| image_size | string | 否 | auto_2K | 尺寸预设 |
| num_images | integer | 否 | 1 | 生成数量 (1-6) |
| seed | integer | 否 | - | 随机种子 |
| enable_safety_checker | boolean | 否 | true | 安全检查 |

### image_size 可选值

- `auto_2K` - 自动 2K（默认）
- `auto_4K` - 自动 4K（高清）
- `square_hd` - 正方形高清
- `square` - 正方形
- `portrait_4_3` - 竖版 4:3
- `portrait_16_9` - 竖版 16:9
- `landscape_4_3` - 横版 4:3
- `landscape_16_9` - 横版 16:9

---

## 图生图（图像编辑）工作流

### 1. 调用 submit_task

```json
{
  "model_id": "fal-ai/bytedance/seedream/v4.5/edit",
  "parameters": {
    "prompt": "将 Figure 1 的背景换成海滩",
    "image_urls": ["https://example.com/input.jpg"],
    "image_size": "auto_2K"
  }
}
```

### 图生图参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|-----|-------|------|
| prompt | string | **是** | - | 编辑提示词，可用 Figure 1/2/3 引用图片 |
| image_urls | array | **是** | - | 输入图片 URL 列表 (1-10 张) |
| image_size | string | 否 | auto_2K | 尺寸预设 |
| num_images | integer | 否 | 1 | 生成数量 (1-6) |
| seed | integer | 否 | - | 随机种子 |
| enable_safety_checker | boolean | 否 | true | 安全检查 |

### 多图引用语法

提示词中可以用 `Figure 1`、`Figure 2` 等引用 `image_urls` 中的图片：

```json
{
  "prompt": "将 Figure 1 中的人物放到 Figure 2 的场景中",
  "image_urls": [
    "https://example.com/person.jpg",
    "https://example.com/background.jpg"
  ]
}
```

---

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
- `completed` - 完成，结果在 `result.images` 中
- `failed` - 失败，查看 `error` 字段

---

## 完整示例

### 文生图示例

**用户请求**：帮我生成一张赛博朋克风格的城市夜景

**执行步骤**：

1. 调用 `submit_task`：
```json
{
  "model_id": "fal-ai/bytedance/seedream/v4.5/text-to-image",
  "parameters": {
    "prompt": "A cyberpunk cityscape at night, neon lights, rain-slicked streets, futuristic skyscrapers, holographic advertisements, flying cars in the distance, highly detailed, cinematic lighting",
    "image_size": "landscape_16_9",
    "num_images": 1
  }
}
```

2. 获取 `task_id` 后调用 `get_task` 查询结果

### 图生图示例

**用户请求**：把这张照片的背景换成日落海滩

**执行步骤**：

1. 调用 `submit_task`：
```json
{
  "model_id": "fal-ai/bytedance/seedream/v4.5/edit",
  "parameters": {
    "prompt": "Replace the background of Figure 1 with a beautiful sunset beach, golden hour lighting, ocean waves, palm trees silhouette",
    "image_urls": ["用户提供的图片URL"],
    "image_size": "auto_2K"
  }
}
```

2. 获取 `task_id` 后调用 `get_task` 查询结果

---

## 提示词技巧

1. **使用英文提示词**效果通常更好
2. **具体描述**：包含风格、光线、细节等
3. **多图编辑**：清晰说明每张图的作用
4. **4K 输出**：对高质量要求使用 `auto_4K`
