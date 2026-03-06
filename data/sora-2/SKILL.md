---
name: Sora 2 视频生成
description: 使用 Sora 2 模型生成视频。当用户想要文生视频、图生视频、视频重混，或提到 sora、OpenAI 视频生成时使用此 skill。
category: video
tags: [视频生成, 文生视频, 图生视频, OpenAI, Sora, 电影级]
featured: true
---

# Sora 2

OpenAI Sora 2 是一款先进的视频生成模型，能够从自然语言或图像生成带有音频的高质量动态视频。

## 可用模型

| 模型 ID | 功能 | 分辨率 | 说明 |
|--------|------|--------|------|
| `fal-ai/sora-2/text-to-video` | 文生视频 | 720p | 标准版文字生成视频 |
| `fal-ai/sora-2/image-to-video` | 图生视频 | 720p | 以图片为首帧生成视频 |
| `fal-ai/sora-2/text-to-video/pro` | 文生视频 Pro | 1080p | 专业版高清文生视频 |
| `fal-ai/sora-2/image-to-video/pro` | 图生视频 Pro | 1080p | 专业版高清图生视频 |
| `fal-ai/sora-2/video-to-video/remix` | 视频重混 | - | 对 Sora 生成的视频进行风格转换 |

## 计费方式

| 模型版本 | 分辨率 | 单价 | 4秒 | 8秒 | 12秒 |
|---------|--------|------|-----|-----|------|
| 标准版 | 720p | 40积分/秒 | 160 | 320 | 480 |
| Remix | - | 40积分/秒 | 160 | 320 | 480 |
| Pro | 720p | 120积分/秒 | 480 | 960 | 1440 |
| Pro | 1080p | 200积分/秒 | 800 | 1600 | 2400 |

## 工作流

### 1. 调用 submit_task

使用 MCP 工具 `submit_task` 提交任务。

#### 文生视频示例

```json
{
  "model_id": "fal-ai/sora-2/text-to-video",
  "parameters": {
    "prompt": "一只金色猎犬在草地上奔跑，阳光明媚，慢镜头，电影质感",
    "duration": 8,
    "aspect_ratio": "16:9"
  }
}
```

#### 图生视频示例

```json
{
  "model_id": "fal-ai/sora-2/image-to-video",
  "parameters": {
    "prompt": "人物微微转头，露出温暖的微笑",
    "image_url": "https://example.com/portrait.jpg",
    "duration": 4,
    "aspect_ratio": "auto"
  }
}
```

#### 视频重混示例

```json
{
  "model_id": "fal-ai/sora-2/video-to-video/remix",
  "parameters": {
    "video_id": "video_123",
    "prompt": "将场景改为夜晚，添加霓虹灯效果"
  }
}
```

### 参数说明

#### 文生视频 (text-to-video / text-to-video/pro)

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|-----|-------|------|
| prompt | string | **是** | - | 视频生成提示词 |
| duration | integer | 否 | 4 | 视频时长：4/8/12 秒 |
| aspect_ratio | string | 否 | "16:9" | 宽高比：9:16 / 16:9 |
| resolution | string | 否 | 720p/1080p | 分辨率（Pro 版默认 1080p） |
| model | string | 否 | "sora-2" | 模型版本（仅标准版支持） |

#### 图生视频 (image-to-video / image-to-video/pro)

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|-----|-------|------|
| prompt | string | **是** | - | 视频生成提示词 |
| image_url | string | **是** | - | 首帧图片 URL |
| duration | integer | 否 | 4 | 视频时长：4/8/12 秒 |
| aspect_ratio | string | 否 | "auto" | 宽高比：auto/9:16/16:9 |
| resolution | string | 否 | "auto" | 分辨率：auto/720p/1080p |
| model | string | 否 | "sora-2" | 模型版本（仅标准版支持） |

#### 视频重混 (video-to-video/remix)

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|-----|-------|------|
| video_id | string | **是** | - | Sora 生成的视频 ID |
| prompt | string | **是** | - | 重混提示词 |

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

**用户请求**：帮我生成一个 8 秒的视频，内容是城市日落延时摄影

**执行步骤**：

1. 调用 `submit_task`：

```json
{
  "model_id": "fal-ai/sora-2/text-to-video/pro",
  "parameters": {
    "prompt": "城市天际线的延时摄影，太阳缓缓落下，天空从金黄变为粉紫色，建筑物的灯光逐渐亮起，车流形成光轨，电影级画质，4K 风格",
    "duration": 8,
    "aspect_ratio": "16:9",
    "resolution": "1080p"
  }
}
```

2. 获取 `task_id` 后调用 `get_task` 查询结果

## 提示词技巧

1. **描述动作和运动**：明确描述镜头运动（推进、拉远、环绕）和主体动作
2. **包含音频描述**：Sora 2 支持音频生成，可以描述环境音效或对话
3. **设置视觉风格**：指定光线、色调、氛围（如"电影级质感"、"暖色调"）
4. **口型同步**：如需人物说话，描述对话内容可获得口型同步效果
5. **时间顺序**：按时间顺序描述场景变化

### 提示词示例

**动作场景**：
```
正面视角的运动相机锁定跳伞者的脸部，他在明亮的云层上方自由落体。他对着镜头说话，口型清晰同步："这太刺激了！你一定要试试！" 自然的风声，人声清晰可辨。正午阳光，护目镜和跳伞服随风飘动，稳定的镜头带有轻微抖动。
```

**电影场景**：
```
黄昏时分安静的郊区街道上的好莱坞式分手场景。一对三十多岁的男女面对面站着，轻声但情绪激动地交谈，口型同步。电影级打光，温暖的夕阳色调，浅景深，微风吹动秋叶，真实自然的环境音。
```

## 注意事项

1. **视频重混限制**：video-to-video/remix 只能处理 Sora 生成的视频，不支持任意上传的视频
2. **delete_video 参数**：默认为 true，生成后视频会被删除以保护隐私。如需保留视频用于后续重混，需设为 false
3. **模型版本**：Pro 版不支持选择模型版本，始终使用最新版本
4. **生成时间**：视频生成需要较长时间，请耐心等待任务完成
