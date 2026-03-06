# 飞书语音消息发送技能

将文本转换为语音消息并发送到飞书，支持在飞书聊天窗口直接播放。

## 功能特性

- ✅ TTS 文字转语音（使用 zhipu-tts）
- ✅ 自动转换为 opus 格式（飞书要求）
- ✅ 读取音频时长
- ✅ 上传到飞书服务器
- ✅ 发送可播放的语音消息
- ✅ 支持多种声音和语速

## 前置要求

### 环境变量

```bash
# 飞书配置
export FEISHU_APP_ID="cli_xxx"              # 飞书应用 ID
export FEISHU_APP_SECRET="your_secret"      # 飞书应用密钥
export FEISHU_RECEIVER="ou_xxx"             # 接收者 Open ID（可选，默认从上下文获取）

# 智谱 AI 配置（用于 TTS）
export ZHIPU_API_KEY="your_zhipu_key"       # 智谱 API 密钥
```

### 必需工具

- `ffmpeg` - 音频格式转换
- `ffprobe` - 读取音频信息
- `jq` - JSON 处理

### 依赖技能

- `zhipu-tts` - 文字转语音

## 快速开始

```bash
# 安装依赖（如果需要）
sudo apt-get install ffmpeg ffprobe jq

# 设置环境变量
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"
export ZHIPU_API_KEY="your_zhipu_key"

# 发送语音消息（默认声音）
bash scripts/send_voice.sh "你好，这是一条语音消息"

# 指定声音和语速
bash scripts/send_voice.sh "你好" tongtong 1.2
```

## 可用声音

- **tongtong** (彤彤) - 默认女声，平衡音色
- **chuichui** (锤锤) - 男声，深沉音色
- **xiaochen** (小陈) - 年轻声音

## 语速范围

- 0.5 - 2.0（默认 1.0）

## 技术细节

### 音频格式要求

飞书语音消息要求：
- **格式**: opus (OGG 容器)
- **编码**: libopus
- **比特率**: 24k
- **采样率**: 24000 Hz
- **声道**: 单声道

### Duration 参数

**关键**: 必须在上传时提供 `duration` 参数（整数秒），否则时长显示为 0。

## 使用场景

- 📢 飞书机器人语音通知
- 🤖 智能客服语音回复
- 📝 自动语音播报
- 🎙️ 语音消息群发
- 👥 飞书群语音互动

## 故障排查

### 语音没有时长

**问题**: 发送的语音消息时长显示为 0

**解决**: 确保在上传时传递了 `duration` 参数（整数秒）

### 无法播放

**可能原因**:
1. 格式不是 opus
2. `file_type` 参数错误
3. 文件损坏

## Author

franklu0819-lang

## License

MIT
