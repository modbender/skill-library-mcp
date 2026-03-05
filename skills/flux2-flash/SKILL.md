---
name: Flux 2 Flash 图像生成
description: 使用 Flux 2 Flash 模型生成或编辑图像。当用户想要文生图、图像编辑，或提到 flux 2、FLUX.2 时使用此 skill。
category: image
tags: [图像生成, 文生图, 图像编辑, Flux, 极速]
featured: true
---

# Flux 2 Flash 图像生成与编辑

Black Forest Labs 推出的 FLUX.2 [dev] 图像生成和编辑模型，具有增强的写实感、更清晰的文字渲染和原生编辑能力。

## 可用模型

| 模型 ID | 功能 | 说明 |
|--------|------|------|
| `fal-ai/flux-2/flash` | 文生图 / 图像编辑 | 统一入口，根据是否提供图片自动切换模式 |

**自动切换逻辑**：
- 未提供 `image_urls` → 文生图模式
- 提供 `image_urls` → 图像编辑模式

## 工作流

### 1. 调用 submit_task

使用 MCP 工具 `submit_task` 提交任务：

**文生图模式**（无图片输入）：

```json
{
  "model_id": "fal-ai/flux-2/flash",
  "parameters": {
    "prompt": "A beautiful sunset over the ocean with sailboats"
  }
}
```

**图像编辑模式**（有图片输入）：

```json
{
  "model_id": "fal-ai/flux-2/flash",
  "parameters": {
    "prompt": "Remove the meat from the hamburger",
    "image_urls": ["https://example.com/hamburger.png"]
  }
}
```

### 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|-----|-------|------|
| prompt | string | **是** | - | 图像生成/编辑提示词 |
| image_urls | array | 否 | - | 输入图片 URL 列表（1-4 张），提供时自动切换为编辑模式 |
| image_size | string | 否 | landscape_4_3 | 图像尺寸预设 |
| num_images | integer | 否 | 1 | 生成图像数量（1-4） |
| guidance_scale | number | 否 | 2.5 | 引导强度（0-20），控制遵循提示词程度 |
| seed | integer | 否 | - | 随机种子，用于复现结果 |
| enable_prompt_expansion | boolean | 否 | false | 启用提示词扩展以获得更好的结果 |
| output_format | string | 否 | png | 输出图像格式：jpeg, png, webp |
| enable_safety_checker | boolean | 否 | true | 是否启用安全检查 |

#### image_size 可选值

- `square_hd` - 1024x1024（高清正方形）
- `square` - 512x512（标准正方形）
- `portrait_4_3` - 768x1024（竖屏 4:3）
- `portrait_16_9` - 576x1024（竖屏 16:9）
- `landscape_4_3` - 1024x768（横屏 4:3，默认）
- `landscape_16_9` - 1024x576（横屏 16:9）

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

**用户请求**：生成一张日落海景图片

**执行步骤**：

1. 调用 `submit_task`：

```json
{
  "model_id": "fal-ai/flux-2/flash",
  "parameters": {
    "prompt": "An army of ants battles for a sugar cube in a giant sandbox, with tiny plastic soldier toys caught in the melee. Ant bodies shine against gritty beige sand and the glossy, crystalline cube. Fiery sunrise spills golden highlights, throwing dramatic shadows.",
    "image_size": "landscape_16_9",
    "num_images": 1
  }
}
```

2. 获取 `task_id` 后调用 `get_task` 查询结果

### 示例 2：图像编辑

**用户请求**：把汉堡里的肉去掉

**执行步骤**：

1. 调用 `submit_task`：

```json
{
  "model_id": "fal-ai/flux-2/flash",
  "parameters": {
    "prompt": "Remove the meat from the hamburger",
    "image_urls": ["https://storage.googleapis.com/falserverless/example_outputs/flux-2-flash-edit-input.png"],
    "image_size": "square_hd"
  }
}
```

2. 获取 `task_id` 后调用 `get_task` 查询结果

## 提示词技巧

1. **详细描述**：提供详细的场景、光影、构图描述，模型会生成更精确的结果
2. **文字渲染**：Flux 2 对文字渲染有特别优化，可以在提示词中包含想要显示的文字
3. **编辑模式**：编辑时使用明确的动作词，如 "Remove"、"Add"、"Change"、"Replace"
4. **多图输入**：编辑模式支持最多 4 张图片，可用于组合或对比编辑

## 定价

每次调用扣除 **2 积分**（按 num_images 数量计费）
