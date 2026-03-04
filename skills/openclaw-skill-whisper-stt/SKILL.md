---
name: whisper-stt
description: 语音转文字 - 使用OpenAI Whisper将音频文件识别为文字
---

# Whisper 语音转文字技能

将音频/语音文件识别并转换为文字。

## 使用方式

### 自动处理（推荐）

当用户发送语音/音频文件时，自动：
1. 识别语音内容
2. 转换为文字
3. 发送文字到飞书

### 手动命令

用户发送音频文件后，技能自动处理。

## 支持格式

- MP3, WAV, M4A, OGG, FLAC, WebM
- 任何音频格式（FFmpeg支持即可）

## 模型选择

| 模型 | 大小 | 速度 | 精度 |
|------|------|------|------|
| tiny | ~1GB | 最快 | 基础 |
| base | ~1GB | 快 | 一般 |
| small | ~2GB | 中等 | 较好 |
| medium | ~5GB | 较慢 | 很好 |
| large | ~10GB | 最慢 | 最佳 |
| turbo | ~6GB | 快 | 接近large |

## 技术实现

```python
import whisper

# 加载模型（首次使用会下载）
model = whisper.load_model("base")  # 可选: tiny/base/small/medium/large/turbo

# 识别语音
result = model.transcribe("audio.mp3")

# 输出文字
print(result["text"])
```

## 依赖

- Python 3.8+
- PyTorch
- openai-whisper
- ffmpeg

## 注意事项

1. 首次使用会下载模型（1-10GB）
2. 大模型需要较多内存
3. 中文识别效果很好
