# Callmac Skill | 远程 Mac 语音控制

Remote voice control for your Mac from mobile devices. Broadcast announcements, play alarms, tell stories, wake up kids - all triggered from messaging apps.

从移动设备远程控制 Mac 语音功能。广播公告、播放闹钟、讲故事、叫孩子起床 - 全部通过即时通讯应用触发。

## Quick Start | 快速开始

```bash
# Install dependencies
pip3 install edge-tts
brew install ffmpeg

# Make scripts executable
chmod +x scripts/*.py

# Test the skill
python3 scripts/generate_tts.py --text "Hello 你好" --play
```

## Features | 功能特性

- 🎯 **Mixed Language Support**: Auto-detects Chinese/English and uses appropriate voices
- 🎵 **High Quality Voices**: Uses Microsoft Edge neural TTS voices
- 🔊 **Local Playback**: Plays directly on Mac using `afplay`
- 🔁 **Loop Playback**: Supports repeated playback (1 to infinite loops)
- 📊 **Volume Control**: Adjust system volume during playback
- 💾 **File Export**: Save generated audio as MP3 files
- 🔗 **Audio Merging**: Combine multiple audio segments
- ⏰ **Scheduling**: Integrate with cron for scheduled announcements

## Usage Examples | 使用示例

### Basic Announcement
```bash
python3 scripts/generate_tts.py --text "System ready" --play
```

### Mixed Language
```bash
python3 scripts/generate_tts.py --text "Hello 你好" --play
```

### Custom Voices
```bash
python3 scripts/generate_tts.py \
  --text "Welcome 欢迎" \
  --play \
  --voice-en "en-US-AriaNeural" \
  --voice-zh "zh-CN-XiaoyiNeural"
```

### Loop Playback
```bash
python3 scripts/generate_tts.py --text "Reminder" --play --loops 3 --volume 80
```

### Save to File
```bash
python3 scripts/generate_tts.py --text "Announcement" --output announcement.mp3
```

## Scripts | 脚本说明

- `generate_tts.py` - Main TTS generation and playback script
- `play_audio.py` - Audio playback control utilities
- `merge_audio.py` - Merge multiple audio files

## Integration with Clawdbot

This skill can be integrated into Clawdbot workflows:

1. **Heartbeat checks**: Play audio notifications during periodic checks
2. **Event triggers**: Play announcements based on system events
3. **Scheduled tasks**: Use with cron for regular announcements
4. **User interactions**: Respond to user requests with voice output

## Dependencies

- Python 3.8+
- `edge-tts` Python package
- `ffmpeg` (for audio merging)
- macOS `afplay` and `osascript` commands

## Installation

See [references/INSTALLATION.md](references/INSTALLATION.md) for detailed setup instructions.

## Voice Selection

See [references/VOICES.md](references/VOICES.md) for complete voice list and recommendations.

## Examples

See [references/EXAMPLES.md](references/EXAMPLES.md) for comprehensive usage examples and patterns.

## License

MIT License