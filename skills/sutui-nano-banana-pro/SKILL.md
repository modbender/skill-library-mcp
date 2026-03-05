---
name: Nano Banana Pro 图像生成
description: 使用 Nano Banana Pro 模型生成或编辑图像。当用户想要文生图、图像编辑，或提到 nano banana、Google 图像生成时使用此 skill。
category: image
tags: [图像生成, 文生图, 图像编辑, Google, Nano Banana]
featured: false
---

# Nano Banana Pro 图像生成

Nano Banana Pro (又名 Nano Banana 2) 是 Google 最新的高质量图像生成和编辑模型，支持写实风格和文字渲染。

## 可用模型

| 模型 ID | 功能 | 说明 |
|--------|------|------|
| `fal-ai/nano-banana-pro` | 文生图/图像编辑 | 无图片时为文生图，提供图片时自动切换为编辑模式 |

**积分消耗**：60 积分/张

## 工作流

### 1. 调用 submit_task

使用 MCP 工具 `submit_task` 提交任务：

**文生图示例**：

```json
{
  "model_id": "fal-ai/nano-banana-pro",
  "parameters": {
    "prompt": "A majestic lion standing on a cliff at sunset, photorealistic",
    "aspect_ratio": "16:9",
    "resolution": "2K"
  }
}
```

**图像编辑示例**：

```json
{
  "model_id": "fal-ai/nano-banana-pro",
  "parameters": {
    "prompt": "make a photo of the man driving the car down the california coastline",
    "image_urls": [
      "https://example.com/man.png",
      "https://example.com/car.png"
    ],
    "aspect_ratio": "auto"
  }
}
```

### 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|-----|-------|------|
| prompt | string | **是** | - | 图像生成/编辑提示词 |
| image_urls | array | 否 | - | 输入图片 URL 列表（提供此参数时自动切换为编辑模式） |
| num_images | integer | 否 | 1 | 生成图像数量（1-4） |
| aspect_ratio | string | 否 | "1:1" | 宽高比：21:9, 16:9, 3:2, 4:3, 5:4, 1:1, 4:5, 3:4, 2:3, 9:16（编辑模式额外支持 "auto"） |
| resolution | string | 否 | "1K" | 分辨率：1K, 2K, 4K |
| output_format | string | 否 | "png" | 输出格式：jpeg, png, webp |
| seed | integer | 否 | - | 随机种子，用于复现结果 |
| enable_web_search | boolean | 否 | false | 启用网页搜索以获取最新信息辅助生成 |

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

## 完整示例

### 示例 1：文生图

**用户请求**：生成一张黑色拉布拉多犬在泳池游泳的照片

**执行步骤**：

1. 调用 `submit_task`：

```json
{
  "model_id": "fal-ai/nano-banana-pro",
  "parameters": {
    "prompt": "An action shot of a black lab swimming in an inground suburban swimming pool. The camera is placed meticulously on the water line, dividing the image in half, revealing both the dogs head above water holding a tennis ball in it's mouth, and it's paws paddling underwater.",
    "aspect_ratio": "16:9",
    "resolution": "2K"
  }
}
```

2. 获取 `task_id` 后调用 `get_task` 查询结果

### 示例 2：图像编辑

**用户请求**：将这个人放到加州海岸线驾车的场景中

**执行步骤**：

1. 调用 `submit_task`：

```json
{
  "model_id": "fal-ai/nano-banana-pro",
  "parameters": {
    "prompt": "make a photo of the man driving the car down the california coastline",
    "image_urls": [
      "https://example.com/man-portrait.png",
      "https://example.com/car-interior.png"
    ],
    "aspect_ratio": "auto"
  }
}
```

2. 获取 `task_id` 后调用 `get_task` 查询结果

## 提示词技巧

1. **详细描述**：提供尽可能详细的场景描述，包括光线、角度、风格等
2. **写实风格**：Nano Banana Pro 擅长写实风格，可以使用 "photorealistic"、"photo of" 等词汇
3. **文字渲染**：模型支持在图像中渲染文字，可以在提示词中指定要显示的文字
4. **多图编辑**：在编辑模式下可以提供多张参考图片，在提示词中引用它们进行合成
5. **网页搜索**：启用 `enable_web_search` 可以让模型使用最新的网络信息辅助生成

## 模式自动切换

- **无 image_urls**：自动使用文生图模式
- **有 image_urls**：自动切换为图像编辑模式

无需手动指定模式，系统会根据是否提供图片自动选择。
