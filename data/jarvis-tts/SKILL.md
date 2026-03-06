---
name: jarvis-tts
description: Jarvis TTS text-to-speech using Microsoft edge-tts with afplay playback. Use when users request voice output, audio responses, or text-to-speech. Provides natural-sounding Chinese TTS.
---

# Jarvis TTS 语音合成

## 功能

用 Microsoft edge-tts 生成高质量语音，然后用 macOS afplay 播放。提供自然流畅的中文语音输出。

## 使用场景

- AI 助手语音回复
- 文字转语音
- 有声读物播放
- 语音通知/提醒

## 优势

- ✅ **自然** - 微软 Neural TTS，接近真人声音
- ✅ **流畅** - 完整播放，不会中断
- ✅ **多音色** - 支持多种中文语音（男声/女声）
- ✅ **离线** - 生成后可重复播放

## 使用方法

### 基本用法

```bash
jarvis-tts.sh "要说的内容"
```

### 示例

```bash
# 简单回复
jarvis-tts.sh "好的，马上执行"

# 长文本
jarvis-tts.sh "从一数到一百：一、二、三...一百。数完了！"

# 指定语音
jarvis-tts.sh "你好" --voice zh-CN-YunxiNeural
```

## 可用语音

### 中文男声
- `zh-CN-YunxiNeural` - 阳光活泼（默认）
- `zh-CN-YunjianNeural` - 激情运动风
- `zh-CN-YunyangNeural` - 专业新闻播报

### 中文女声
- `zh-CN-XiaoxiaoNeural` - 温暖
- `zh-CN-XiaoyiNeural` - 活泼

## 工作流程

```
文字输入 → edge-tts 生成 MP3 → afplay 播放 → 完成
```

### 详细步骤

1. **生成语音** - edge-tts 调用微软 TTS API 生成 MP3
2. **检查文件** - 确认生成成功且文件大小正常
3. **播放音频** - afplay 播放直到完成
4. **清理** - 删除临时文件

## 脚本说明

### jarvis-tts.py

Python 脚本，执行 TTS 生成和播放。

**依赖：**
- Python 3
- edge-tts (`pip3 install edge-tts`)

**用法：**
```bash
python3 jarvis-tts.py "要说的内容"
```

### jarvis-tts.sh

Shell 封装脚本，方便直接调用。

**用法：**
```bash
./jarvis-tts.sh "要说的内容"
```

## 技术细节

### 音频生成

```python
python3 -m edge_tts \
  --voice zh-CN-YunxiNeural \
  --text "要说的内容" \
  --write-media /tmp/output.mp3
```

### 播放保证

- 等待生成完成再播放
- 检查文件大小确保成功
- 同步播放直到完成

### 超时处理

- 生成超时：60 秒
- 播放超时：根据音频长度自动计算

## 限制

- 仅支持 macOS（依赖 afplay）
- 需要安装 edge-tts
- 需要网络连接（调用微软 API）

## 扩展建议

如需支持其他平台：

- **Linux**: 用 `aplay` 或 `paplay` 替代 `afplay`
- **Windows**: 用 `powershell -c (New-Object Media.SoundPlayer)` 播放

## 相关文件

- `scripts/jarvis-tts.py` - 主脚本
- `scripts/jarvis-tts.sh` - Shell 封装
