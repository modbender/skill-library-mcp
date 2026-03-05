---
name: siliconflow-media
description: SiliconFlow 多模态服务，支持图片生成(FLUX/Qwen)、视频生成(Wan)、TTS语音合成、ASR语音识别。使用代金券支付。
metadata:
  openclaw:
    emoji: "🚀"
    requires:
      env:
        - SILICONFLOW_API_KEY
    primaryEnv: SILICONFLOW_API_KEY
---

# SiliconFlow 媒体服务

SiliconFlow 提供丰富的 AI 模型服务，支持代金券支付（当前余额 3000+）。

## 环境变量

- `SILICONFLOW_API_KEY` - SiliconFlow API Key

## 🎨 图片生成

```bash
uv run {baseDir}/scripts/image_gen.py --prompt "描述" --filename "output.png" [--model MODEL]
```

**可用模型**：
| 参数 | 模型 | 说明 |
|------|------|------|
| `flux` (默认) | FLUX.1-schnell | 快速高质量，约 5-10 秒 |
| `flux-dev` | FLUX.1-dev | 开发版 |
| `flux-pro` | FLUX.1-pro | 专业版 |
| `qwen` | Qwen/Qwen-Image | 通义图片生成 |
| `qwen-edit` | Qwen/Qwen-Image-Edit | 图片编辑 |
| `qwen-edit-2509` | Qwen/Qwen-Image-Edit-2509 | 最新编辑版 |

**示例**：
```bash
# FLUX 快速生成
uv run {baseDir}/scripts/image_gen.py --prompt "a cute robot assistant" --filename "robot.png"

# Qwen 生成
uv run {baseDir}/scripts/image_gen.py --prompt "山水画" --filename "landscape.png" --model qwen
```

## 🎬 视频生成

```bash
# 文生视频
uv run {baseDir}/scripts/video_gen.py --prompt "描述" --filename "output.mp4"

# 图生视频
uv run {baseDir}/scripts/video_gen.py --prompt "描述" --image "input.png" --filename "output.mp4"
```

**模型**：
- 文生视频: `Wan-AI/Wan2.2-T2V-A14B`
- 图生视频: `Wan-AI/Wan2.2-I2V-A14B`

⚠️ 视频生成时间较长（约 2-5 分钟）

## 🎤 语音合成 (TTS)

```bash
uv run {baseDir}/scripts/tts.py --text "要合成的文字" --filename "output.mp3" [--model MODEL]
```

**可用模型**：
| 参数 | 模型 | 说明 |
|------|------|------|
| `fish-speech` (默认) | fish-speech-1.5 | Fish Audio 高质量 |
| `cosyvoice` | CosyVoice2-0.5B | 阿里语音克隆 |
| `indextts` | IndexTTS-2 | Index TTS |
| `moss` | MOSS-TTSD-v0.5 | MOSS 多语言 |

**示例**：
```bash
uv run {baseDir}/scripts/tts.py --text "你好世界" --filename "hello.mp3"
```

## 👂 语音识别 (ASR)

```bash
uv run {baseDir}/scripts/asr.py --audio "input.mp3" [--model MODEL]
```

**可用模型**：
| 参数 | 模型 | 说明 |
|------|------|------|
| `sensevoice` (默认) | SenseVoiceSmall | 阿里语音识别 |
| `teleai` | TeleSpeechASR | TeleAI 识别 |

**示例**：
```bash
uv run {baseDir}/scripts/asr.py --audio "recording.mp3"
```

## 注意事项

1. ✅ 费用从代金券扣除，无需额外付费
2. ⏱️ 图片生成约 5-10 秒
3. ⏱️ 视频生成约 2-5 分钟（耐心等待）
4. 📝 所有脚本会打印 `MEDIA:` 行用于自动附加文件
