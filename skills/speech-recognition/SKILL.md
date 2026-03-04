---
name: speech-recognition
description: "通用语音识别 Skill。支持多种音频格式（ogg/mp3/wav/m4a），使用硅基流动 SenseVoice API 进行语音转文字。当用户发送语音消息、音频文件，或需要转录音频时触发。"
version: "1.0.0"
---

# 通用语音识别

使用硅基流动 SenseVoice API 进行语音识别，支持多种音频格式。

---

## 激活条件

| 触发场景 | 说明 |
|----------|------|
| 用户发送语音消息 | `.ogg` / `.mp3` / `.wav` / `.m4a` 文件 |
| 用户要求转录音频 | "转录这个音频"、"语音转文字" |
| 音频文件处理 | 需要提取音频中的文字内容 |

---

## 配置

### API Key

在 `~/.openclaw/openclaw.json` 中配置：

```json
{
  "providers": {
    "siliconflow": {
      "apiKey": "sk-xxx"
    }
  }
}
```

### API 端点

```
POST https://api.siliconflow.cn/v1/audio/transcriptions
```

### 支持的模型

| 模型 | 说明 |
|------|------|
| `FunAudioLLM/SenseVoiceSmall` | 默认，中文效果好 |

---

## 使用方法

### 方法一：直接调用 API

```python
import requests

api_key = "sk-xxx"

with open("/path/to/audio.mp3", "rb") as f:
    audio_data = f.read()

response = requests.post(
    "https://api.siliconflow.cn/v1/audio/transcriptions",
    headers={"Authorization": f"Bearer {api_key}"},
    files={"file": ("audio.mp3", audio_data, "audio/mpeg")},
    data={"model": "FunAudioLLM/SenseVoiceSmall"},
    timeout=60
)

print(response.json().get("text", ""))
```

### 方法二：处理用户语音消息

当用户发送 `.ogg` 语音消息时：

```bash
# 1. 转换格式（如果是 ogg）
ffmpeg -i /path/to/audio.ogg -ar 16000 -ac 1 /tmp/audio.mp3 -y

# 2. 调用硅基流动 API（API Key 从环境变量读取）
python3 -c "
import requests
import os

api_key = os.environ.get('SILICONFLOW_API_KEY')
if not api_key:
    raise ValueError('请设置 SILICONFLOW_API_KEY 环境变量')

with open('/tmp/audio.mp3', 'rb') as f:
    audio_data = f.read()

response = requests.post(
    'https://api.siliconflow.cn/v1/audio/transcriptions',
    headers={'Authorization': f'Bearer {api_key}'},
    files={'file': ('audio.mp3', audio_data, 'audio/mpeg')},
    data={'model': 'FunAudioLLM/SenseVoiceSmall'},
    timeout=60
)
print(response.json().get('text', ''))
"
```

---

## 支持的音频格式

| 格式 | 扩展名 | 说明 |
|------|--------|------|
| MP3 | `.mp3` | 推荐，兼容性好 |
| OGG | `.ogg` | Telegram/Signal 语音格式，需转换 |
| WAV | `.wav` | 无压缩，文件大 |
| M4A | `.m4a` | iOS 录音格式 |
| FLAC | `.flac` | 无损压缩 |

---

## 格式转换

如果音频不是 MP3 格式，用 FFmpeg 转换：

```bash
# OGG → MP3
ffmpeg -i input.ogg -ar 16000 -ac 1 output.mp3 -y

# WAV → MP3
ffmpeg -i input.wav -ar 16000 -ac 1 output.mp3 -y

# M4A → MP3
ffmpeg -i input.m4a -ar 16000 -ac 1 output.mp3 -y
```

参数说明：
- `-ar 16000`: 采样率 16kHz（语音识别推荐）
- `-ac 1`: 单声道（减少文件大小）
- `-y`: 覆盖已存在的文件

---

## 错误处理

| 错误 | 原因 | 解决 |
|------|------|------|
| `401 Unauthorized` | API Key 无效 | 检查配置 |
| `413 Payload Too Large` | 文件太大 | 压缩或分割音频 |
| `timeout` | 网络超时 | 重试或检查网络 |
| `Invalid audio format` | 格式不支持 | 用 FFmpeg 转换 |

---

## 注意事项

1. **文件大小限制**：建议 < 10MB
2. **时长限制**：建议 < 5 分钟
3. **语言支持**：中文效果最好，英文也支持
4. **隐私**：音频会上传到硅基流动服务器

---

## 相关 Skills

| Skill | 说明 |
|-------|------|
| `douyin-video` | 抖音视频语音提取 |
| `cosyvoice-tts` | 文字转语音 |

---

*版本：1.0.0*
*创建于：2026-02-26*
