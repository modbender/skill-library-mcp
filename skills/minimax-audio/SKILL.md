---
name: 海螺语音合成与设计
description: 使用 Minimax（海螺）API 进行语音合成、声音克隆和音色设计。当用户想要语音合成、TTS、声音克隆、音色设计时使用此 skill。
category: audio
tags: [语音合成, TTS, 声音克隆, 音色设计, MiniMax, 海螺]
featured: false
---

# 海螺语音合成与设计

使用 Minimax（海螺）API 进行语音合成、声音克隆和音色设计。

## 功能概述

| 功能 | 工具名称 | 费用 | 说明 |
|------|----------|------|------|
| 获取音色列表 | `list_voices` | 免费 | 获取系统音色和用户自定义音色 |
| 语音合成 | `text_to_audio` | 1积分/千字符 | 将文本转换为语音 |
| 语音设计 | `voice_design` | 5积分/次 | 用自然语言创建自定义音色 |
| 声音克隆 | `voice_clone` | 10积分/次 | 通过音频样本克隆声音 |
| 上传音频 | `upload_audio` | 免费 | 上传音频用于声音克隆 |

## 可用工具

### 1. list_voices - 获取音色列表

获取系统音色和用户创建的自定义音色。

**参数：**
- `status`（可选）: 音色状态过滤，可选值：`active`（有效）、`expired`（过期）、`all`（全部）

**示例：**
```json
{
  "name": "list_voices",
  "arguments": {
    "status": "active"
  }
}
```

**返回：**
```json
{
  "success": true,
  "user_voices": [...],      // 用户创建的音色
  "public_voices": [...],    // 系统公共音色
  "statistics": {
    "user_total_count": 5,
    "user_active_count": 3,
    "public_voices_count": 500
  }
}
```

### 2. text_to_audio - 语音合成

将文本转换为语音。

**参数：**
- `text`（必填）: 要合成的文本内容，最大 10000 字符
- `voice_id`（必填）: 音色 ID，可通过 `list_voices` 获取
- `model`（可选）: 模型版本，默认 `speech-2.8-hd`
  - `speech-2.8-hd`: 最新高清模型，支持语气词标签
  - `speech-2.8-turbo`: 最新快速模型，支持语气词标签
  - `speech-2.6-hd`: 高清音质，支持 fluent/whisper 情绪
  - `speech-2.6-turbo`: 快速模式，支持 fluent/whisper 情绪
- `output_format`（可选）: 输出格式，`url` 或 `base64`，默认 `url`
- `language_boost`（可选）: 语言增强，可选 `Chinese`、`English`、`Japanese`、`Korean`、`auto`
- `speed`（可选）: 语速，取值 0.5-2，默认 1.0。值越大语速越快
- `pitch`（可选）: 语调，取值 -12 到 12，默认 0。正值音调升高，负值音调降低
- `vol`（可选）: 音量，取值 0-10，默认 1.0

**示例：**
```json
{
  "name": "text_to_audio",
  "arguments": {
    "text": "各位听众朋友们，大家好！今天我们来聊聊人工智能的发展。",
    "voice_id": "male-qn-qingse",
    "model": "speech-2.8-hd",
    "speed": 1.2,
    "pitch": 2
  }
}
```

**返回：**
```json
{
  "success": true,
  "audio_url": "https://...",
  "trace_id": "xxx",
  "price": 1,
  "balance": 990.0
}
```

### 3. voice_design - 语音设计

用自然语言描述创建自定义音色，无需上传音频样本。

**参数：**
- `prompt`（必填）: 音色描述，用自然语言描述想要的声音特征
- `preview_text`（可选）: 试听文本，默认 "各位听众朋友们，大家好！"
- `voice_name`（可选）: 音色名称，方便后续识别

**示例：**
```json
{
  "name": "voice_design",
  "arguments": {
    "prompt": "年轻女性，声音甜美温柔，语速适中，适合讲故事和温馨内容",
    "preview_text": "今天天气真不错，我们一起出去走走吧。",
    "voice_name": "温柔女声"
  }
}
```

**返回：**
```json
{
  "success": true,
  "voice_id": "design_abc123_def456",
  "audio_url": "https://...",
  "voice_name": "温柔女声",
  "expires_at": "2024-01-08 12:00:00",
  "price": 5,
  "balance": 985.0,
  "message": "音色创建成功！可在 7 天内使用此音色进行语音合成"
}
```

### 4. upload_audio - 上传音频

上传音频文件到 Minimax，用于声音克隆。

**参数：**
- `audio_url`（必填）: 音频文件的 URL 地址
- `purpose`（可选）: 用途，默认 `voice_clone`
  - `voice_clone`: 声音克隆音频，时长 10秒-5分钟
  - `prompt_audio`: 示例音频，时长 <8秒

**文件要求：**
- 格式: mp3, m4a, wav
- 大小: ≤ 20MB
- 声音克隆建议时长: 10秒-5分钟

**示例：**
```json
{
  "name": "upload_audio",
  "arguments": {
    "audio_url": "https://example.com/my-voice-sample.mp3",
    "purpose": "voice_clone"
  }
}
```

**返回：**
```json
{
  "success": true,
  "file_id": 123456,
  "filename": "audio_20240101120000.mp3",
  "bytes": 5896337,
  "purpose": "voice_clone",
  "message": "音频上传成功！可使用返回的 file_id 进行声音克隆"
}
```

### 5. voice_clone - 声音克隆

通过音频样本创建克隆音色。

**参数：**
- `file_id`（必填）: 音频文件 ID，通过 `upload_audio` 获得
- `voice_name`（可选）: 音色名称
- `text`（可选）: 试听文本，默认 "各位听众朋友们，大家好！"
- `model`（可选）: 模型版本，默认 `speech-2.6-hd`

**示例：**
```json
{
  "name": "voice_clone",
  "arguments": {
    "file_id": 123456,
    "voice_name": "我的声音",
    "text": "这是用我的声音合成的一段话。"
  }
}
```

**返回：**
```json
{
  "success": true,
  "voice_id": "clone_abc123_def456",
  "audio_url": "https://...",
  "voice_name": "我的声音",
  "expires_at": "2024-01-08 12:00:00",
  "price": 10,
  "balance": 975.0,
  "message": "声音克隆成功！可在 7 天内使用此音色进行语音合成"
}
```

## 使用流程

### 场景 1：直接使用系统音色合成

最简单的方式，直接使用系统内置的音色。

```
1. 调用 list_voices 获取音色列表
2. 从 public_voices 中选择合适的 voice_id
3. 调用 text_to_audio 进行合成
```

### 场景 2：创建自定义音色后合成

用自然语言描述想要的声音，然后使用新音色合成。

```
1. 调用 voice_design 描述想要的声音特征
2. 获取返回的 voice_id
3. 调用 text_to_audio 使用新音色合成
```

### 场景 3：克隆特定声音

上传真实人声样本，克隆后使用。

```
1. 准备音频文件（10秒-5分钟的清晰人声）
2. 调用 upload_audio 上传音频，获取 file_id
3. 调用 voice_clone 克隆声音，获取 voice_id
4. 调用 text_to_audio 使用克隆音色合成
```

## 常用系统音色

| voice_id | 名称 | 特点 |
|----------|------|------|
| `male-qn-qingse` | 青涩男声 | 年轻活力 |
| `male-qn-jingying` | 精英男声 | 成熟稳重 |
| `female-shaonv` | 少女音 | 清新甜美 |
| `female-yujie` | 御姐音 | 成熟知性 |
| `female-tianmei` | 甜美女声 | 亲切温柔 |
| `presenter_male` | 男主播 | 专业播音 |
| `presenter_female` | 女主播 | 专业播音 |

> 完整音色列表请调用 `list_voices` 获取

## 注意事项

1. **音色有效期**: 用户创建的音色（克隆/设计）有效期为 7 天
2. **文本长度**: 单次合成最大 10000 字符
3. **音频要求**: 声音克隆的音频需要清晰的人声，避免背景噪音
4. **费用说明**: 
   - 语音合成按字符数计费，每 1000 字符 1 积分（不足 1000 按 1000 算）
   - 语音设计 5 积分/次
   - 声音克隆 10 积分/次

## 模型版本说明

| 模型 | 特点 | 适用场景 |
|------|------|----------|
| `speech-2.6-hd` | 高清音质 | 正式内容、播客、有声书 |
| `speech-2.6-turbo` | 快速响应 | 实时对话、即时反馈 |

## 关联模型

- `minimax/t2a` - 语音合成
- `minimax/voice-design` - 语音设计
- `minimax/voice-clone` - 声音克隆
- `minimax/music-gen` - 音乐生成
