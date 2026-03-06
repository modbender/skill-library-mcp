---
name: elevenlabs-stt
description: 使用 ElevenLabs Scribe V2 进行语音转文字。当用户想要语音识别、音频转录、语音转文字，或提到 elevenlabs、scribe 时使用此 skill。
category: audio
tags: [speech-to-text, transcription, elevenlabs, scribe]
---

# ElevenLabs Scribe V2 语音转文字

ElevenLabs Scribe V2 是一款高速语音转文字模型，支持多语言识别、说话人分离、音频事件标注。

## 可用模型

| 模型 ID | 功能 | 说明 |
|--------|------|------|
| `fal-ai/elevenlabs/speech-to-text/scribe-v2` | 语音转文字 | 高速 STT，支持说话人分离和音频事件标注 |

## 工作流

### 1. 调用 submit_task

使用 MCP 工具 `submit_task` 提交任务：

```json
{
  "model_id": "fal-ai/elevenlabs/speech-to-text/scribe-v2",
  "parameters": {
    "audio_url": "https://example.com/audio.mp3"
  }
}
```

### 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|-----|-------|------|
| audio_url | string | **是** | - | 音频文件 URL（支持 mp3/ogg/wav/m4a/aac） |
| language_code | string | 否 | 自动检测 | 语言代码，如 eng/spa/fra/cmn/jpn |
| tag_audio_events | boolean | 否 | true | 是否标注音频事件（笑声、掌声等） |
| diarize | boolean | 否 | true | 是否启用说话人分离 |
| keyterms | array | 否 | [] | 关键词列表，提升专业术语识别准确度（最多100个，每个最多50字符）。使用后费用增加30% |

### 常用语言代码

| 代码 | 语言 |
|-----|------|
| eng | 英语 |
| cmn | 中文（普通话） |
| jpn | 日语 |
| kor | 韩语 |
| spa | 西班牙语 |
| fra | 法语 |
| deu | 德语 |

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

## 输出格式

```json
{
  "text": "完整的转录文本",
  "language_code": "eng",
  "language_probability": 1.0,
  "words": [
    {
      "text": "Hello,",
      "start": 0.079,
      "end": 0.539,
      "type": "word",
      "speaker_id": "speaker_0"
    }
  ]
}
```

## 完整示例

**用户请求**：帮我把这段英文音频转成文字

**执行步骤**：

1. 调用 `submit_task`：
```json
{
  "model_id": "fal-ai/elevenlabs/speech-to-text/scribe-v2",
  "parameters": {
    "audio_url": "https://storage.googleapis.com/falserverless/example_inputs/elevenlabs/scribe_v2_in.mp3",
    "language_code": "eng",
    "diarize": true,
    "tag_audio_events": true
  }
}
```

2. 获取 `task_id` 后调用 `get_task` 查询结果

## 定价

- **基础价格**：4 积分/分钟（约 $0.008/分钟）
- **使用 keyterms**：5 积分/分钟（+30%）
- **最低计费**：1 分钟

## 使用技巧

1. 不指定 `language_code` 时模型会自动检测语言，但指定语言可以提升准确度
2. 对于多人对话场景，建议启用 `diarize: true` 来区分说话人
3. 如果音频中包含专业术语，使用 `keyterms` 参数可以显著提升识别准确度
4. 支持的音频格式包括 mp3、ogg、wav、m4a、aac
