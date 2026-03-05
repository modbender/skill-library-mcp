# Zhipu AI TTS Skill

Text-to-speech conversion using Zhipu AI (BigModel) GLM-TTS model. Convert Chinese text to natural-sounding speech with multiple voice options.

## Features

- 🎙️ **Multiple Voices**: 7 different voice personas (tongtong, chuichui, xiaochen, jam, kazi, douji, luodo)
- ⚡ **Speed Control**: Adjustable speech speed from 0.5x to 2.0x
- 🎵 **Multiple Formats**: WAV and PCM output formats
- 🇨🇳 **Chinese Language**: Optimized for Mandarin Chinese synthesis
- 📝 **Long Text Support**: Up to 1024 characters per request
- 🔊 **High Quality**: 24000 Hz sampling rate for optimal audio quality

## Requirements

- `jq` - JSON processor
- `ZHIPU_API_KEY` environment variable

## Quick Start

```bash
# Install dependencies (if needed)
sudo apt-get install jq

# Set your API key
export ZHIPU_API_KEY="your-key-here"

# Convert text to speech (default settings)
bash scripts/text_to_speech.sh "你好，今天天气怎么样"

# With custom voice and speed
bash scripts/text_to_speech.sh "欢迎使用智能语音服务" xiaochen 1.2 wav greeting.wav
```

## Available Voices

- **tongtong** (彤彤) - Default balanced tone
- **chuichui** (锤锤) - Male voice, deeper tone
- **xiaochen** (小陈) - Young professional voice
- **jam** - 动动动物圈 Jam voice
- **kazi** - 动动动物圈 Kazi voice
- **douji** - 动动动物圈 Douji voice
- **luodo** - 动动动物圈 Luodo voice

## Use Cases

- 📚 Audiobook creation
- 🎮 Game character voices
- 📢 Announcement systems
- 🤖 Virtual assistants
- 🎬 Video dubbing
- 📻 Radio content generation

## Parameters

- `text` (required): Chinese text to convert (max 1024 characters)
- `voice` (optional): Voice persona (default: tongtong)
- `speed` (optional): Speech speed 0.5-2.0 (default: 1.0)
- `output_format` (optional): wav or pcm (default: wav)
- `output_file` (optional): Output filename (default: output.{format})

## Examples

```bash
# Professional greeting
bash scripts/text_to_speech.sh "您好，感谢致电智能客服" tongtong 1.0 wav greeting.wav

# Energetic announcement
bash scripts/text_to_speech.sh "热烈欢迎各位嘉宾！" xiaochen 1.3 wav announcement.wav

# Calm narration
bash scripts/text_to_speech.sh "在这个宁静的夜晚" chuichui 0.9 wav narration.wav
```

## Author

franklu0819-lang

## License

MIT
