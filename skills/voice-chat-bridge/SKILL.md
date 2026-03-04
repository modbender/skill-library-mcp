---
skill_id: voice-chat-bridge
version: 1.1.0
author: laoxu
description: 双向语音对话系统 - 语音识别转文字 + Edge TTS语音合成 + Cloudflare Tunnel公网访问
categories: [voice, speech, communication]
requires: [ffmpeg]
optional: [cloudflared, ngrok]
---

# Voice Chat Bridge Skill

让你的 OpenClaw 助手具备完整的双向语音对话能力。

## 功能特性

- 🎤 **语音识别**: 接收语音消息，自动转文字
- 🗣️ **语音合成**: 用文字生成自然的中文语音（Edge TTS）
- 🔊 **本地播放**: 无需域名，直接在电脑上播放语音
- 🌐 **公网访问**: 通过 Cloudflare Tunnel 让语音文件全球可访问
- 💻 **Web界面**: 内置简单的语音播放器界面
- 📱 **多平台**: 支持 Telegram、Discord、Slack、Webhook 等多种集成方式
- 🔗 **灵活输出**: 链接、本地文件路径、或直接播放

## 安装要求

### 必需
1. **ffmpeg** - 音频格式转换
   ```bash
   brew install ffmpeg
   ```

2. **Python 依赖**
   ```bash
   pip3 install edge-tts
   ```

### 可选（根据部署方式选择）

**方案A：本地模式（最简单）**
- 无需额外工具，直接在本机播放语音

**方案B：公网访问**
- **Cloudflare Tunnel**（推荐，免费稳定）
  ```bash
  brew install cloudflared
  ```
- **Ngrok**（临时使用，随机域名）
  ```bash
  brew install ngrok
  ```
- **LocalTunnel**（npm安装）
  ```bash
  npm install -g localtunnel
  ```

**方案C：Web界面模式**
- 仅需要浏览器访问 `http://localhost:8765`

4. **语音识别工具**（二选一）
   - **macOS 推荐**: `hear` - 本地识别，无需联网
     ```bash
     curl -LO https://github.com/sveinbjornt/hear/releases/download/0.7/hear-0.7.zip
     unzip hear-0.7.zip && cp hear-0.7/hear ~/.local/bin/
     ```
   - **云端方案**: 阿里云 DashScope（国内稳定）

## 部署方案对比

| 方案 | 需要域名 | 公网访问 | 适用场景 |
|------|----------|----------|----------|
| **本地模式** | ❌ 不需要 | ❌ 仅本机 | 个人使用，电脑上直接听 |
| **Web界面** | ❌ 不需要 | ❌ 局域网 | 同一WiFi下多设备访问 |
| **Ngrok** | ❌ 不需要 | ✅ 临时域名 | 快速测试，分享给朋友 |
| **Cloudflare** | ✅ 需要自有域名 | ✅ 永久 | 长期使用，生产环境 |
| **LocalTunnel** | ❌ 不需要 | ✅ 临时域名 | 免费替代Ngrok |

## 快速开始

### 方案1：本地模式（最简单，无需域名）

适合：只想在电脑上听语音回复

```bash
# 1. 初始化
bash skills/voice-chat-bridge/scripts/init.sh

# 2. 配置为本地模式
cat > ~/.openclaw/workspace/voice_config.json << 'EOF'
{
  "mode": "local",
  "tts_engine": "edge-tts",
  "voice": "zh-CN-XiaoxiaoNeural",
  "auto_play": true
}
EOF

# 3. 生成语音并自动播放
python3 skills/voice-chat-bridge/scripts/generate_voice.py "你好，这是本地模式测试"
```

**AGENTS.md 配置:**
```markdown
## Voice Chat Bridge (本地模式)

当用户发送语音消息时：
1. 使用 `transcribe.py` 转文字
2. 生成回复后，使用 `generate_voice.py` 生成语音
3. **自动播放**: 调用 `afplay` (macOS) 或 `mpg123` (Linux) 播放语音
4. 回复文字内容: "[已播放语音] 回复内容..."
```

### 方案2：Web界面模式（局域网可用）

适合：同一WiFi下手机/平板也能访问

```bash
# 1. 配置为Web模式
cat > ~/.openclaw/workspace/voice_config.json << 'EOF'
{
  "mode": "web",
  "local_port": 8765,
  "tts_engine": "edge-tts",
  "voice": "zh-CN-XiaoxiaoNeural"
}
EOF

# 2. 启动Web服务器
python3 skills/voice-chat-bridge/scripts/voice_server.py --web

# 3. 浏览器访问 http://localhost:8765
```

内置Web界面包含：
- 语音播放器
- 历史记录
- 二维码（方便手机扫描访问）

### 方案3：Ngrok模式（快速公网访问，无需域名）

适合：临时分享给朋友，或不想配置域名

```bash
# 1. 安装Ngrok
brew install ngrok

# 2. 注册获取token（免费）
ngrok config add-authtoken YOUR_TOKEN

# 3. 启动语音服务器
python3 skills/voice-chat-bridge/scripts/voice_server.py

# 4. 在另一个终端启动Ngrok
ngrok http 8765

# 5. 获取临时域名（如 https://abc123.ngrok.io）
# 6. 更新配置
cat > ~/.openclaw/workspace/voice_config.json << 'EOF'
{
  "mode": "ngrok",
  "domain": "https://abc123.ngrok.io",
  "local_port": 8765
}
EOF
```

### 方案4：Cloudflare Tunnel模式（完整方案）

适合：有域名，长期稳定使用

```bash
# 参考原教程...
```

## 多平台集成

### Telegram（当前方案）
- 生成语音 → 上传文件或发送链接

### Discord
```python
# 使用Discord的tts参数
await channel.send("回复内容", tts=True)  # 使用Discord内置TTS
# 或发送语音文件
await channel.send(file=discord.File("voice.mp3"))
```

### Slack
```python
# 使用Slack的音频附件
client.chat_postMessage(
    channel="#general",
    text="回复内容",
    attachments=[{
        "audio_url": voice_url
    }]
)
```

### 纯Webhook/API
```python
# 返回JSON
{
    "text": "回复内容",
    "voice_url": "http://localhost:8765/voice.mp3",
    "voice_base64": "..."  # 可选
}
```

### 命令行/本地交互
```bash
# 直接对话模式
python3 skills/voice-chat-bridge/scripts/chat.py
# > 你说: [语音输入或文字]
# > AI回复: [文字]
# > [自动播放语音]
```

### 方案0: 完整本地语音对话循环（推荐）

适合：完整的本地化语音交互体验

```bash
# 启动完整对话循环
python3 skills/voice-chat-bridge/scripts/voice_chat_loop.py
```

**完整流程**：
```
按住 Ctrl+T
    ↓
🎤 开始录音（听到提示音）
    ↓
说话...
    ↓
松开按键
    ↓
✅ 录音结束 → 自动转文字
    ↓
🤖 AI处理（写入.voice_trigger文件）
    ↓
💬 生成回复文字
    ↓
🔊 生成语音回复
    ↓
🔈 自动播放语音
    ↓
返回等待下一段录音
```

**特点**：
- 完全本地化，无需网络（除语音合成外）
- 完整的闭环：说 → 识别 → 思考 → 回复 → 听
- 支持连续对话

### 快捷键录音模式

适合：只想快速语音输入，不依赖完整对话循环

```bash
# 启动快捷键监听（后台运行）
python3 skills/voice-chat-bridge/scripts/hotkey_recorder.py

# 然后任何时候：
# 1. 按住 Ctrl+T（可配置）
# 2. 说话
# 3. 松开按键
# 4. 自动转文字并复制到剪贴板/发送给AI
```

**快捷键配置**（编辑 `voice_config.json`）：
```json
{
  "hotkey": {
    "enabled": true,
    "combination": ["ctrl", "t"],
    "on_release": "transcribe_and_send",
    "beep_on_start": true,
    "beep_on_end": true
  }
}
```

**工作流程**：
```
按住 Ctrl+T
    ↓
🎤 开始录音（听到提示音）
    ↓
说话...
    ↓
松开按键
    ↓
✅ 录音结束 → 自动转文字
    ↓
📋 复制到剪贴板 或 直接发给AI
```

## 快速开始

### 1. 初始化

```bash
bash skills/voice-chat-bridge/scripts/init.sh
```

这会创建：
- `voice_output/` - 语音文件输出目录
- `voice_config.json` - 配置文件

### 2. 配置域名

编辑 `voice_config.json`：
```json
{
  "domain": "https://your-domain.com",
  "local_port": 8765,
  "voice": "zh-CN-XiaoxiaoNeural"
}
```

### 3. 启动服务

```bash
# 启动语音服务器
python3 skills/voice-chat-bridge/scripts/voice_server.py

# 在另一个终端启动 Cloudflare Tunnel
cloudflared tunnel --config ~/.cloudflared/config.yml run
```

### 4. 配置 AGENTS.md

在 `AGENTS.md` 中添加：

```markdown
## Voice Chat Bridge

当用户发送语音消息时：
1. 使用 `skills/voice-chat-bridge/scripts/transcribe.py` 转文字
2. 理解内容并生成回复
3. 使用 `skills/voice-chat-bridge/scripts/generate_voice.py` 生成语音
4. 回复文字内容 + 语音链接

### 情绪状态更新（每次语音交互）
- connection: +0.2（语音交流增强连接感）
- 记录语音交互频率到 habits.json
```

## 使用示例

### 转写语音
```bash
python3 skills/voice-chat-bridge/scripts/transcribe.py /path/to/audio.ogg
```

### 生成语音
```bash
python3 skills/voice-chat-bridge/scripts/generate_voice.py "要合成的文字内容"
# 输出: https://your-domain.com/abc123.mp3
```

### 完整对话流程（在 AGENTS.md 中配置）

```python
# 伪代码示例
if user_message.is_voice:
    # 1. 转写
    text = transcribe(user_message.audio_path)
    
    # 2. 理解并回复
    reply = generate_reply(text)
    
    # 3. 生成语音
    voice_url = generate_voice(reply)
    
    # 4. 发送回复
    send_message(f"{reply}\n\n🎙️ {voice_url}")
```

## 文件结构

```
skills/voice-chat-bridge/
├── SKILL.md              # 本文件
├── scripts/
│   ├── init.sh           # 初始化脚本
│   ├── transcribe.py     # 语音转文字
│   ├── generate_voice.py # 文字转语音
│   └── voice_server.py   # HTTP服务器
└── templates/
    └── config.json       # 配置模板
```

## 多语言支持

本 Skill 默认使用 Edge TTS，支持 **100+ 种语言和方言**：

### 中文
| 语音ID | 描述 |
|--------|------|
| zh-CN-XiaoxiaoNeural | 晓晓 - 自然女声（中国大陆推荐）|
| zh-CN-YunxiNeural | 云希 - 自然男声（中国大陆）|
| zh-TW-HsiaoChenNeural | 曉臻 - 台湾女声 |
| zh-HK-HiuMaanNeural | 曉曼 - 香港粤语女声 |

### 英语
| 语音ID | 描述 |
|--------|------|
| en-US-AriaNeural | Aria - 美式英语女声 |
| en-US-GuyNeural | Guy - 美式英语男声 |
| en-GB-SoniaNeural | Sonia - 英式英语女声 |
| en-AU-NatashaNeural | Natasha - 澳洲英语女声 |

### 日语
| 语音ID | 描述 |
|--------|------|
| ja-JP-NanamiNeural | 七海 - 日语女声 |
| ja-JP-KeitaNeural | 圭太 - 日语男声 |

### 韩语
| 语音ID | 描述 |
|--------|------|
| ko-KR-SunHiNeural | 선희 - 韩语女声 |
| ko-KR-InJoonNeural | 인준 - 韩语男声 |

### 法语/德语/西班牙语等
| 语音ID | 描述 |
|--------|------|
| fr-FR-DeniseNeural | Denise - 法语女声 |
| de-DE-KatjaNeural | Katja - 德语女声 |
| es-ES-ElviraNeural | Elvira - 西班牙语女声 |
| ru-RU-SvetlanaNeural | Svetlana - 俄语女声 |
| ar-SA-ZariyahNeural | Zariyah - 阿拉伯语女声 |
| hi-IN-SwaraNeural | Swara - 印地语女声 |

**完整列表**: 运行 `edge-tts --list-voices`

### 配置语言

编辑 `voice_config.json`：
```json
{
  "domain": "https://your-domain.com",
  "local_port": 8765,
  "voice": "en-US-AriaNeural",  // 改成你想要的语音
  "language": "en-US"           // 用于语音识别
}
```

### 自动语言检测（进阶）

结合 `inner-life` skill，根据用户语言自动切换：

```python
# 在 AGENTS.md 中添加
if user_message.language == "zh":
    voice_config["voice"] = "zh-CN-XiaoxiaoNeural"
elif user_message.language == "en":
    voice_config["voice"] = "en-US-AriaNeural"
elif user_message.language == "ja":
    voice_config["voice"] = "ja-JP-NanamiNeural"
```

## 备用 TTS 方案

如果 Edge TTS 在某些地区访问受限，支持以下备选：

### 1. macOS say（本地，免费）
```bash
# 修改 scripts/generate_voice.py 中的 TTS_ENGINE
TTS_ENGINE = "say"
say -v "Ting-Ting" "你好"  # 中文
say -v "Samantha" "Hello"  # 英文
```

### 2. Google Cloud TTS（需 API Key）
- 支持更多语言
- 音质更好
- 需要付费（但有免费额度）

### 3. ElevenLabs（高质量）
- 最自然的 AI 语音
- 支持语音克隆
- 每月 10k 字符免费

### 4. 阿里云/百度（国内稳定）
- 国内访问快
- 中文效果极好
- 有免费额度

## 自定义配置

### 更换语音角色

修改 `voice_config.json` 中的 `voice` 字段：

### 调整音频质量

在 `generate_voice.py` 中修改：
```python
# 默认 16kHz，可提高至 24kHz
"-ar", "16000"  # → "-ar", "24000"
```

## 故障排除

**问题**: 转写失败，提示 "No speech detected"
- **解决**: 音频文件太短（< 1秒）或格式不支持，尝试转换格式

**问题**: Cloudflare Tunnel 连接失败
- **解决**: 检查 `~/.cloudflared/config.yml` 配置，确保域名和端口正确

**问题**: Edge TTS 生成语音失败
- **解决**: 检查网络连接，Edge TTS 需要访问微软服务器

## 进阶用法

### 情感化语音

结合 `inner-life-core` skill，根据情绪状态调整语音风格：

```python
if inner_state.confidence > 0.8:
    voice_style = "cheerful"
elif inner_state.connection < 0.3:
    voice_style = "gentle"
```

### 语音日记

自动将每日日记转为语音：

```bash
python3 skills/voice-chat-bridge/scripts/diary_to_voice.py
```

## 成本估算

- **Edge TTS**: 免费（微软 Azure 免费额度）
- **Cloudflare Tunnel**: 免费
- **hear (macOS)**: 免费
- **流量**: 每个语音文件约 20-100KB

## 参考

- [Edge TTS GitHub](https://github.com/rany2/edge-tts)
- [hear - macOS语音识别](https://github.com/sveinbjornt/hear)
- [Cloudflare Tunnel文档](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/)

## License

MIT - 随便用，欢迎改进！
