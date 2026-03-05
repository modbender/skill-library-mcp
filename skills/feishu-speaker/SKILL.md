---
name: feishu-speaker
description: 飞书双向语音消息工具 - 支持语音转文字接收和文字转语音发送（TTS+Whisper）
version: 1.1.0
author: 巴克
---

# feishu-speaker Skill v1.0

**飞书双向语音消息工具** - 让AI助手像真人一样语音交流

> ✅ **支持双向**：接收语音（转文字）+ 发送语音（TTS）
> 
> ✅ **智能回复**：根据接收消息类型自动选择回复方式

---

## 🎯 核心特性

### 🎤 接收语音（语音 → 文字）
- 使用 OpenAI Whisper 本地转录
- 支持中文语音识别
- 无需联网，本地处理

### 🔊 发送语音（文字 → 语音）
- 使用 Edge-TTS 生成高质量语音
- 支持多种中文音色（男/女/年轻/成熟）
- 可调节语速（0.5x - 2.0x）

### 🔄 智能交互
- 收到语音消息 → 自动转文字理解 → 语音回复
- 收到文字消息 → 文字理解 → 根据配置选择回复方式

---

## 📦 安装依赖

```bash
# 1. 安装Whisper（语音转文字）
pip install openai-whisper

# 2. 安装Edge-TTS（文字转语音）
npm install -g edge-tts

# 3. 安装FFmpeg（音频格式转换）
# macOS: brew install ffmpeg
# Ubuntu: apt-get install ffmpeg
```

---

## 🚀 快速开始

### 1. 配置飞书API凭证

创建文件 `~/.openclaw/.credentials/feishu-app-secret.txt`：

```
你的飞书App Secret
```

获取方式：
1. 访问 https://open.feishu.cn/app/
2. 进入你的应用 → 凭证与基础信息
3. 复制 App Secret

### 2. 接收语音（自动转文字）

```bash
# 转录收到的语音消息
feishu-speaker listen voice.ogg

# 使用更大的模型（更准确但更慢）
feishu-speaker listen voice.ogg --model small
```

### 3. 发送语音消息

```bash
# 基本使用
feishu-speaker say "你好，这是语音消息"

# 指定音色
feishu-speaker say "晚上好" --voice zh-CN-YunxiNeural

# 调整语速
feishu-speaker say "加快速度" --rate "+30%"
```

### 4. 智能回复

```bash
# 根据收到的消息类型自动选择回复方式
feishu-speaker reply "收到，我马上处理"
```

---

## 🎨 支持的音色

| 音色ID | 性别 | 风格 | 推荐场景 |
|:---|:---:|:---|:---|
| `zh-CN-YunxiNeural` | 男 | 年轻、干脆利落 ⭐ | 日常交流、快速回复 |
| `zh-CN-YunjianNeural` | 男 | 成熟稳重 | 正式场合、商务沟通 |
| `zh-CN-XiaoxiaoNeural` | 女 | 标准女声 | 温和回复、客服场景 |
| `zh-CN-XiaoyiNeural` | 女 | 温柔女声 | 亲切交流、情感场景 |

---

## 🔧 命令详解

### `feishu-speaker listen` - 语音转文字

```bash
feishu-speaker listen <音频文件> [选项]

选项:
  -m, --model <模型>    Whisper模型（tiny/base/small，默认：base）
  -l, --language <语言> 指定语言（默认：zh）
  -o, --output <文件>   输出到文件

示例:
  feishu-speaker listen message.ogg
  feishu-speaker listen voice.mp3 --model small
```

### `feishu-speaker say` - 文字转语音并发送

```bash
feishu-speaker say <文字内容> [选项]

选项:
  -v, --voice <音色>    指定音色（默认：zh-CN-YunxiNeural）
  -r, --rate <速率>     语速调整（默认：+20%）
  -t, --to <用户ID>     指定接收者
  -s, --save <文件>     保存音频文件（不发送）

示例:
  feishu-speaker say "你好"
  feishu-speaker say "会议开始" --voice zh-CN-YunjianNeural
  feishu-speaker say "快速播报" --rate "+50%"
```

### `feishu-speaker reply` - 智能回复

```bash
feishu-speaker reply <文字内容> [选项]

选项:
  --voice               强制语音回复
  --text                强制文字回复
  --auto                根据对方消息类型自动选择（默认）

示例:
  feishu-speaker reply "收到"
  feishu-speaker reply "好的" --voice
```

---

## ⚙️ 配置选项

配置文件：`~/.openclaw/skills/feishu-speaker/config/config.json`

```json
{
  "default_voice": "zh-CN-YunxiNeural",
  "default_rate": "+20%",
  "default_volume": "+0%",
  "default_pitch": "default",
  "reply_mode": "auto",
  "app_id": "cli_a9037acd2ba19bb5",
  "receiver_id": "ou_94f3936f1896b5378404f377da3fae6f"
}
```

配置说明：
- `default_voice`: 默认TTS音色
- `default_rate`: 默认语速（+20% = 1.2倍速）
- `reply_mode`: 回复模式
  - `auto`: 自动匹配（语音→语音，文字→文字）
  - `voice`: 总是语音回复
  - `text`: 总是文字回复

---

## 📝 使用场景

### 场景1：AI助手语音交互

```bash
# 用户发送语音 → AI转录理解 → 语音回复
# 自动流程：
# 1. 用户：发送语音"帮我查一下明天的天气"
# 2. AI：feishu-speaker listen voice.ogg → 转录为文字
# 3. AI：处理请求 → feishu-speaker reply "明天北京晴天，25度"
```

### 场景2：定时语音播报

```bash
# 在cron任务中使用
feishu-speaker say "早上好！今日热点已更新，请查看。"
```

### 场景3：多音色切换

```bash
# 正式场合
feishu-speaker say "会议将在10分钟后开始。" --voice zh-CN-YunjianNeural

# 活泼场合  
feishu-speaker say "好消息！任务提前完成了！" --voice zh-CN-YunxiNeural --rate "+30%"
```

---

## 🔌 技术架构

```
接收语音流程:
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  飞书语音消息  │ ──→ │  Whisper    │ ──→ │   文字结果   │
│  (ogg格式)   │     │  (本地转录)  │     │  (中文文本)  │
└─────────────┘     └─────────────┘     └─────────────┘

发送语音流程:
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   文字输入   │ ──→ │  Edge-TTS   │ ──→ │   FFmpeg    │ ──→ │  飞书API    │
│  (中文文本)  │     │  (生成MP3)  │     │ (转opus/ogg)│     │ (发送语音)  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

---

## ⚠️ 注意事项

1. **音频格式**：飞书语音消息支持 opus/ogg 格式，脚本会自动转换
2. **文件大小**：单条语音建议不超过 10MB
3. **语速范围**：支持 -50% 到 +100%，建议 +20% 左右最自然
4. **网络要求**：发送语音需要访问飞书API（国内网络即可）
5. **隐私安全**：语音转文字在本地处理，不上传到云端

---

## 🐛 故障排查

### Whisper模型下载失败

```bash
# 手动下载模型
python3 -c "import whisper; whisper.load_model('base')"
```

### 飞书API返回错误

1. 检查 App Secret 是否正确配置
2. 检查接收者ID格式（应以 `ou_` 开头）
3. 检查音频文件格式是否为 opus/ogg

### Edge-TTS安装失败

```bash
# 使用npx直接运行
npx edge-tts "测试" --voice zh-CN-YunxiNeural --write-media output.mp3
```

---

## 📊 与其他skill对比

| 功能 | feishu-voice | feishu-speaker (本skill) |
|:---|:---:|:---:|
| 发送语音 | ✅ | ✅ |
| 接收语音（转文字） | ❌ | ✅ |
| 双向交互 | ❌ | ✅ |
| 智能回复模式 | ❌ | ✅ |
| 多音色支持 | ✅ | ✅ |
| 语速调节 | ✅ | ✅ |

---

## 🔄 更新计划

### v1.1.0 (计划中)
- [ ] 支持更多语音合成引擎（Azure、科大讯飞）
- [ ] 支持语音情感调节（开心、严肃、温柔）
- [ ] 支持实时语音对话（WebSocket）

### v1.2.0 (计划中)
- [ ] 支持语音克隆（自定义音色）
- [ ] 支持语音转写后自动摘要
- [ ] 支持批量语音处理

---

## 📄 License

MIT License

---

**让飞书沟通更自然，像真人一样语音交流！** 🎙️✨

---

## 🚀 新增：一键语音回复

### `reply-voice` 脚本（v1.1.0新增）

**功能**：自动处理完整的语音消息回复流程
- 接收语音消息 → 转录为文字 → 生成语音回复 → 发送

**用法**：
```bash
# 转录语音并发送回复
reply-voice voice.ogg "这是回复内容"

# 仅转录，不发送
reply-voice voice.ogg
```

**完整流程**：
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 飞书语音消息 │ → │  Whisper   │ → │  Edge-TTS  │ → │  飞书API    │
│  (ogg格式)  │    │  转录文字   │    │  生成语音   │    │  发送语音   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

**依赖**：
- Python 3.8+
- openai-whisper
- edge-tts
- ffmpeg

