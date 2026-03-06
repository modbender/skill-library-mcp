---
name: qwen-video
description: Generate videos using Alibaba Cloud DashScope Wan (通义万相) text-to-video (t2v) API (e.g., wan2.6-t2v). Use when the user asks to create a short video from a text prompt via 百炼/通义万相/wan 文生视频, and wants the agent to submit an async task, poll status, and download the mp4 locally (e.g., to Windows Desktop from WSL2).
---

# Qwen / Wan Video (DashScope) — 文生视频

This skill provides simple CLI scripts to:
1) submit an async Wan t2v job
2) poll task status until SUCCEEDED/FAILED
3) download the resulting mp4

## Requirements

- Set API key:

```bash
export DASHSCOPE_API_KEY="sk-..."
```

## Quick start (one command)

Generate a video and download to Windows Desktop (WSL2):

```bash
bash {baseDir}/scripts/generate.sh \
  --prompt "4秒赛博朋克雨夜城市镜头，霓虹反射，电影感镜头运动，高清" \
  --duration 4 \
  --size 1280*720 \
  --out "/mnt/c/Users/<USERNAME>/Desktop/wan_video.mp4"
```

## Submit only (returns task_id)

```bash
bash {baseDir}/scripts/submit.sh --prompt "..." --duration 4 --size 1280*720
```

## Poll status only

```bash
bash {baseDir}/scripts/poll.sh --task-id "<task_id>"
```

## 高级功能

### 多镜头叙事 (Multi-shot)

仅 wan2.6 系列模型支持此功能。通过设置 `prompt_extend: true` 和 `shot_type: "multi"` 启用。

```bash
curl --location 'https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis' \
  -H 'X-DashScope-Async: enable' \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "wan2.6-t2v",
    "input": {
      "prompt": "史诗级战斗场景..."
    },
    "parameters": {
      "size": "1280*720",
      "prompt_extend": true,
      "duration": 10,
      "shot_type": "multi"
    }
  }'
```

### 自动配音 (Auto Audio)

仅 wan2.6 和 wan2.5 系列模型支持。若不提供 `input.audio_url`，模型将根据视频内容自动生成匹配的背景音乐或音效。

```bash
curl --location 'https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis' \
  -H 'X-DashScope-Async: enable' \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "wan2.5-t2v-preview",
    "input": {
      "prompt": "史诗级战斗场景..."
    },
    "parameters": {
      "size": "832*480",
      "prompt_extend": true,
      "duration": 10
    }
  }'
```

### 传入音频文件 (Custom Audio)

仅 wan2.6 和 wan2.5 系列模型支持。通过 `input.audio_url` 参数传入自定义音频的 URL。

```bash
curl --location 'https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis' \
  -H 'X-DashScope-Async: enable' \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "wan2.5-t2v-preview",
    "input": {
      "prompt": "史诗级战斗场景...",
      "audio_url": "https://example.com/audio.mp3"
    },
    "parameters": {
      "size": "832*480",
      "prompt_extend": true,
      "duration": 10
    }
  }'
```

### 生成无声视频 (Silent Video)

仅 wan2.2 和 wanx2.1 系列模型支持生成无声视频。默认生成无声视频，无需设置。

> wan2.6 及 wan2.5 系列模型默认生成有声视频。

```bash
curl --location 'https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis' \
  -H 'X-DashScope-Async: enable' \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "wan2.2-t2v-plus",
    "input": {
      "prompt": "低对比度，复古70年代风格地铁站..."
    },
    "parameters": {
      "size": "832*480",
      "prompt_extend": true
    }
  }'
```

### 使用反向提示词 (Negative Prompt)

通过 `negative_prompt` 排除不需要的元素。

```bash
curl --location 'https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis' \
  -H 'X-DashScope-Async: enable' \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "wan2.2-t2v-plus",
    "input": {
      "prompt": "一只小猫在月光下奔跑",
      "negative_prompt": "花朵"
    },
    "parameters": {
      "size": "832*480"
    }
  }'
```

## API Endpoint (current)

- Submit: `POST https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis`
- Status: `GET  https://dashscope.aliyuncs.com/api/v1/tasks/<task_id>`

Scripts print:
- `TASK_ID: ...`
- `VIDEO_URL: ...` (when succeeded)
- `MEDIA: <local_path>` (when downloaded)

## 模型功能对照表

| 模型 | 多镜头叙事 | 自动配音 | 自定义音频 | 无声视频 | 反向提示词 |
|------|-----------|---------|-----------|---------|-----------|
| wan2.6-t2v | ✅ | ✅ | ✅ | - | ✅ |
| wan2.5-t2v-preview | - | ✅ | ✅ | - | ✅ |
| wan2.2-t2v-plus | - | - | - | ✅ | ✅ |
| wanx2.1 | - | - | - | ✅ | - |
