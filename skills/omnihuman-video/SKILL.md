---
name: omnihuman-video
description: 使用 OmniHuman v1.5 生成音频驱动的口型同步视频。当用户想要让图片中的人物说话、配音、口型同步，或提到 omnihuman 时使用此 skill。
category: video
tags: [image-to-video, lipsync, audio-driven, omnihuman]
featured: true
---

# OmniHuman v1.5 音频驱动视频

字节跳动 OmniHuman v1.5 是一款音频驱动的视频生成模型。输入一张人物图片和一段音频，即可生成口型同步、表情生动的高质量视频。角色的情感和动作与音频高度关联。

## 可用模型

| 模型 ID | 功能 | 说明 |
|--------|------|------|
| `fal-ai/bytedance/omnihuman/v1.5` | 图片+音频→视频 | 口型同步、表情驱动，$0.16/秒 |

## 工作流

### 1. 调用 submit_task

使用 MCP 工具 `submit_task` 提交任务：

```json
{
  "model_id": "fal-ai/bytedance/omnihuman/v1.5",
  "parameters": {
    "image_url": "人物图片URL",
    "audio_url": "音频文件URL"
  }
}
```

### 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|-----|-------|------|
| image_url | string | **是** | - | 人物图片 URL，需要清晰的人物形象 |
| audio_url | string | **是** | - | 音频文件 URL（mp3/wav/m4a/ogg/aac） |
| prompt | string | 否 | - | 文本提示词，引导视频生成风格 |
| resolution | string | 否 | "1080p" | 视频分辨率：720p 或 1080p |
| turbo_mode | boolean | 否 | false | 加速模式，更快但画质略降 |

### 分辨率限制

| 分辨率 | 最大音频时长 | 说明 |
|-------|------------|------|
| 1080p | 30 秒 | 高清画质，时长受限 |
| 720p | 60 秒 | 画质高且生成更快，支持更长音频 |

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

### 示例 1：基础用法（人物说话）

**用户请求**：让这张图片里的人说这段话

**执行步骤**：

1. 先用 TTS 生成音频（可选，如果用户没有提供音频）
2. 调用 `submit_task`：

```json
{
  "model_id": "fal-ai/bytedance/omnihuman/v1.5",
  "parameters": {
    "image_url": "https://storage.googleapis.com/falserverless/example_inputs/omnihuman_v15_input_image.png",
    "audio_url": "https://storage.googleapis.com/falserverless/example_inputs/omnihuman_v15_input_audio.mp3",
    "resolution": "1080p"
  }
}
```

3. 获取 `task_id` 后调用 `get_task` 查询结果

### 示例 2：使用加速模式

```json
{
  "model_id": "fal-ai/bytedance/omnihuman/v1.5",
  "parameters": {
    "image_url": "https://example.com/portrait.jpg",
    "audio_url": "https://example.com/speech.mp3",
    "resolution": "720p",
    "turbo_mode": true
  }
}
```

## 计费说明

- **按秒计费**：64 积分/秒（$0.16/秒）
- 视频时长由音频长度决定
- 最低计费 3 秒

| 音频时长 | 费用（积分） |
|---------|------------|
| 5 秒 | 320 |
| 10 秒 | 640 |
| 20 秒 | 1,280 |
| 30 秒 | 1,920 |

## 使用技巧

1. **图片要求**：使用清晰的人物正面或半侧面照片，人脸占比适中
2. **音频质量**：使用清晰的语音音频，背景噪音越少效果越好
3. **分辨率选择**：短音频（< 30s）推荐 1080p；长音频推荐 720p
4. **加速模式**：测试阶段可开启 turbo_mode 加快生成速度
5. **配合 TTS**：可先用海螺语音合成生成音频，再用 OmniHuman 生成视频

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| 口型不同步 | 确保音频清晰，避免过多背景音乐 |
| 生成失败 | 检查图片是否包含清晰人物，音频时长是否超限 |
| 画质不够好 | 使用 1080p 分辨率，关闭 turbo_mode |
