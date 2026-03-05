# Voice Skill (Edge TTS)

Text-to-speech skill using Microsoft Edge TTS engine with real-time streaming playback support.

## Features 功能特点

- **Edge TTS Engine** - High quality text-to-speech using Microsoft Edge
- **Streaming Playback** - Real-time audio streaming (边生成边播放)
- **Multiple Voices** - Support for Chinese, English, Japanese, Korean voices
- **Customizable** - Adjust rate, volume, and pitch
- **Secure Implementation** - No command injection vulnerabilities

## Installation 安装

### 1. Install Python dependencies

```bash
pip install edge-tts
```

### 2. Install ffmpeg (required for streaming)

**Windows:**
Download from: https://github.com/GyanD/codexffmpeg/releases
Extract and add `bin` folder to PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

## Usage 使用

### Streaming Playback (Recommended) 流式播放（推荐）

Real-time audio generation and playback:

```javascript
// Basic usage
await skill.execute({
  action: 'stream',
  text: '你好，我是小九'
});

// With custom voice
await skill.execute({
  action: 'stream',
  text: 'Hello, how are you?',
  options: {
    voice: 'en-US-Standard-A',
    rate: '+10%',
    volume: '+0%',
    pitch: '+0Hz'
  }
});
```

### Text-to-Speech with File 生成语音文件

```javascript
await skill.execute({
  action: 'tts',
  text: 'Hello, how are you today?',
  options: {
    voice: 'zh-CN-XiaoxiaoNeural'
  }
});
// Returns: { success: true, media: 'MEDIA: /path/to/file.mp3' }
```

### Direct Speak 直接播放

```javascript
await skill.execute({
  action: 'speak',
  text: 'Hello!'
});
```

### List Available Voices 查看可用语音

```javascript
await skill.execute({
  action: 'voices'
});
```

## Available Voices 可用语音

| Language | Voice ID |
|----------|----------|
| Chinese (Female) | zh-CN-XiaoxiaoNeural |
| Chinese (Male) | zh-CN-YunxiNeural |
| Chinese (Male) | zh-CN-YunyangNeural |
| English (US Female) | en-US-Standard-A |
| English (US Male) | en-US-Standard-D |
| English (UK) | en-GB-Standard-A |
| Japanese | ja-JP-NanamiNeural |
| Korean | ko-KR-SunHiNeural |

## Options 参数

| Option | Default | Description |
|--------|---------|-------------|
| voice | zh-CN-XiaoxiaoNeural | Voice ID |
| rate | +0% | Speech rate (-50% to +100%) |
| volume | +0% | Volume adjustment (-50% to +50%) |
| pitch | +0Hz | Pitch adjustment |

## Security 安全

This skill implements **enterprise-grade security** best practices:

### 🛡️ Security Features

| Feature | Implementation |
|---------|----------------|
| **Input Validation** | Voice parameter whitelist validation - only allowed voices can be used |
| **No Shell Execution** | Uses `spawn()` with array arguments instead of shell command concatenation |
| **Command Injection Prevention** | All user inputs are properly validated and escaped |
| **Path Safety** | Fixed script path prevents path traversal |

### Security Details

```javascript
// ❌ UNSAFE - Don't use exec with string concatenation
exec(`py script.py "${userText}" --voice ${userVoice}`);

// ✅ SAFE - Use spawn with array arguments
spawn('py', [scriptPath, text, '--voice', voice], { shell: false });
```

### Voice Whitelist

Only these voices are allowed:

```javascript
const allowedVoices = [
  'zh-CN-XiaoxiaoNeural', 'zh-CN-YunxiNeural', 'zh-CN-YunyangNeural',
  'zh-CN-YunyouNeural', 'zh-CN-XiaomoNeural',
  'en-US-Standard-C', 'en-US-Standard-D', 'en-US-Wavenet-F',
  'en-GB-Standard-A', 'en-GB-Wavenet-A',
  'ja-JP-NanamiNeural', 'ko-KR-SunHiNeural'
];
```

Any invalid voice parameter will be rejected and replaced with the default voice.

## Changelog 更新日志

### v1.10 (2026-02-24)
- **Enterprise-grade security** - Full command injection protection
- Voice whitelist validation
- Replaced exec with spawn for secure process execution
- Input sanitization for all parameters

### v1.1.0
- Add streaming playback support (边生成边播放)
- Add ffmpeg dependency
- Fix command injection vulnerability
- Add voice whitelist validation

### v1.0.0
- Initial release with basic TTS support
