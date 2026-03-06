---
name: Audio Editor
description: 音频处理技能，支持剪辑、音量调整、格式转换、提取视频音频等操作。
---

# Audio Editor
## Description
音频处理技能，支持剪辑、音量调整、格式转换、提取视频音频等操作。
## Dependencies
- ffmpeg >= 5.0
## Commands
### edit_audio
- Description: 自然语言执行音频处理
- Parameters:
  - command: 音频处理需求（必填）
  - output: 输出路径（可选）
- Output: 处理后的音频路径

### extract_audio
- Description: 从视频提取音频
- Parameters:
  - input: 视频路径（必填）
  - output: 输出音频路径（可选）
- Output: 提取的音频路径
