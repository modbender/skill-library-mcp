---
name: zhipu-tts
description: Text-to-speech conversion using Zhipu AI (BigModel) GLM-TTS model. Use when you need to convert text to audio files with various voice options. Supports Chinese text synthesis with multiple voice personas, speed control, and output formats.
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["jq"], "env": ["ZHIPU_API_KEY"] },
      },
  }
---

# Zhipu AI Text-to-Speech

Convert Chinese text to natural-sounding speech using Zhipu AI's GLM-TTS model.

## Setup

**1. Get your API Key:**
Get a key from [Zhipu AI Console](https://bigmodel.cn/usercenter/proj-mgmt/apikeys)

**2. Set it in your environment:**
```bash
export ZHIPU_API_KEY="your-key-here"
```

## Available Voices

### System Voices (Pre-built)

- **tongtong** (彤彤) - Default voice, balanced tone
- **chuichui** (锤锤) - Male voice, deeper tone
- **xiaochen** (小陈) - Young professional voice
- **jam** - 动动动物圈 Jam voice
- **kazi** - 动动动物圈 Kazi voice
- **douji** - 动动动物圈 Douji voice
- **luodo** - 动动动物圈 Luodo voice

## Usage

### Basic Text-to-Speech

Convert text to speech with default settings (tongtong voice, normal speed, WAV format):

```bash
bash scripts/text_to_speech.sh "你好，今天天气怎么样"
```

### Advanced Options

Specify voice, speed, format, and output filename:

```bash
bash scripts/text_to_speech.sh "欢迎使用智能语音服务" xiaochen 1.2 wav greeting.wav
```

**Parameters:**
- `text` (required): Chinese text to convert (max 1024 characters)
- `voice` (optional): tongtong (default), chuichui, xiaochen, jam, kazi, douji, luodo
- `speed` (optional): Speech speed from 0.5 to 2.0 (default: 1.0)
- `output_format` (optional): wav (default), pcm
- `output_file` (optional): Output filename (default: output.{format})

## Voice Selection Guide

**Choose tongtong (default) for:**
- General purpose narration
- Professional presentations
- Balanced tone requirements

**Choose chuichui for:**
- Male voice needed
- Deeper, authoritative tone
- Documentary or formal content

**Choose xiaochen for:**
- Young, energetic tone
- Modern, casual content
- Friendly assistant vibe

**Choose jam/kazi/douji/luodo for:**
- Entertainment content
- Character voices
- Creative projects

## Speed Control

**Recommended speeds:**
- **0.8-1.0**: Clear, professional narration
- **1.0-1.2**: Natural conversational pace (default: 1.0)
- **1.2-1.5**: Energetic, upbeat delivery
- **1.5-2.0**: Fast-paced summaries (may reduce clarity)

## Output Formats

**WAV (recommended):**
- Standard audio format
- Widely compatible
- Better quality preservation

**PCM:**
- Raw audio format
- Smaller file size
- Requires additional processing for playback

## Examples

Create a professional greeting:

```bash
bash scripts/text_to_speech.sh "您好，感谢致电智能客服，请按1选择中文服务" tongtong 1.0 wav greeting.wav
```

Generate an energetic announcement:

```bash
bash scripts/text_to_speech.sh "热烈欢迎各位嘉宾参加今天的活动！" xiaochen 1.3 wav announcement.wav
```

Create a calm narration:

```bash
bash scripts/text_to_speech.sh "在这个宁静的夜晚，让我们一起欣赏美丽的星空" chuichui 0.9 wav narration.wav
```

## Character Limits

- Maximum input: **1024 characters** per request
- For longer texts, split into multiple segments
- Combine audio files post-generation

## Audio Quality Tips

**Best practices:**
- Use punctuation for natural pauses (commas, periods)
- Break long sentences into shorter segments
- Use appropriate line breaks for paragraph pauses
- Test speed settings for your specific content

**Sample rate:** Generated audio uses 24000 Hz sampling rate for optimal quality.

## Troubleshooting

**Text Length Issues:**
- Split texts longer than 1024 characters
- Process segments separately
- Combine using audio editing tools

**Audio Quality Issues:**
- Check text encoding (use UTF-8)
- Verify punctuation placement
- Adjust speed settings
- Try different voices

**File Playback Issues:**
- Ensure format compatibility with your player
- WAV format works on most systems
- PCM may require conversion

## API Notes

- Responses are returned as audio files
- Watermarking enabled by default (can be disabled in account settings)
- No strict rate limiting documented
- Audio generation typically completes in 1-3 seconds
