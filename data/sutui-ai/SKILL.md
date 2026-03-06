---
name: sutui-ai
description: 使用速推AI生成图像和视频。当用户需要画图、生成图片、制作视频、图生图、文生图、文生视频、图生视频时使用此 skill。支持即梦、Flux、Kling 等多种模型。
---

# 速推AI - 图像与视频生成

通过速推AI MCP服务进行AI图像和视频生成，支持多种模型。

## MCP 服务信息

- **服务标识**: `user-速推AI`
- **调用方式**: 使用 `CallMcpTool` 工具

## 快速开始

### 1. 生成图像（推荐 Flux 2 Flash）

使用异步任务流程调用 Flux 2 Flash 模型：

```json
// Step 1: 提交任务
{
  "server": "user-速推AI",
  "toolName": "submit_task",
  "arguments": {
    "model_id": "fal-ai/flux/dev",
    "parameters": {
      "prompt": "一只可爱的猫咪在花园里玩耍",
      "image_size": "landscape_16_9"
    }
  }
}

// Step 2: 查询任务状态（轮询直到完成）
{
  "server": "user-速推AI",
  "toolName": "get_task",
  "arguments": {
    "task_id": "返回的任务ID"
  }
}
```

**备选同步方式**（即梦模型，30-70秒）：

```json
{
  "server": "user-速推AI",
  "toolName": "sync_generate_image",
  "arguments": {
    "prompt": "一只可爱的猫咪在花园里玩耍",
    "model": "jimeng-4.5"
  }
}
```

**图生图**: 添加 `image_url` 参数即可

### 2. 同步生成视频（推荐）

直接返回视频结果：

```json
{
  "server": "user-速推AI",
  "toolName": "sync_generate_video",
  "arguments": {
    "prompt": "一只猫咪在奔跑，16:9",
    "model": "jimeng-video-3.5-pro"
  }
}
```

**支持的模型**: jimeng-video-3.5-pro、jimeng-video-3.5-pro-10s、jimeng-video-3.5-pro-12s

**图生视频**: 添加 `image_url` 参数
**首尾帧视频**: 同时添加 `image_url` 和 `end_image_url`

## 异步任务流程

对于需要更多模型选择的场景，使用异步任务流程：

### Step 1: 查询可用模型

```json
{
  "server": "user-速推AI",
  "toolName": "list_models",
  "arguments": {
    "category": "image"  // 可选: image, video, audio, all
  }
}
```

### Step 2: 获取模型参数要求

```json
{
  "server": "user-速推AI",
  "toolName": "get_model_info",
  "arguments": {
    "model_id": "fal-ai/flux/schnell"
  }
}
```

### Step 3: 提交任务

```json
{
  "server": "user-速推AI",
  "toolName": "submit_task",
  "arguments": {
    "model_id": "fal-ai/flux/schnell",
    "parameters": {
      "prompt": "a beautiful sunset over the ocean",
      "image_size": "landscape_16_9"
    }
  }
}
```

### Step 4: 查询任务状态

```json
{
  "server": "user-速推AI",
  "toolName": "get_task",
  "arguments": {
    "task_id": "返回的任务ID"
  }
}
```

轮询直到状态为 `completed` 或 `failed`。

## 辅助功能

### 上传图片

将本地图片或网络图片上传到云存储：

```json
{
  "server": "user-速推AI",
  "toolName": "upload_image",
  "arguments": {
    "image_url": "https://example.com/image.jpg"
  }
}
```

### 查询任务列表

```json
{
  "server": "user-速推AI",
  "toolName": "list_tasks",
  "arguments": {
    "status": "processing",
    "limit": 10
  }
}
```

## 工作流程选择

| 场景 | 推荐模型 | 工具 |
|------|---------|------|
| 生成图片（默认） | Flux 2 Flash | `submit_task` + `get_task` |
| 生成视频（默认） | jimeng-video-3.5-pro | `sync_generate_video` |
| 快速生成图片 | jimeng-4.5 | `sync_generate_image` |
| 使用其他模型 | 先查询 | `list_models` → `get_model_info` |

## 注意事项

1. **同步接口耗时**: 图像 30-70秒，视频 60-160秒
2. **图生图/视频**: 需要提供公开可访问的图片URL
3. **本地图片**: 先用 `upload_image` 上传获取URL
4. **异步任务**: 需轮询 `get_task` 直到完成
