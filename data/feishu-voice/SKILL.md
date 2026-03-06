---
name: feishu-voice
description: 飞书语音消息发送技能。将文本转换为语音并发送到飞书，支持 TTS 生成、格式转换、时长读取、文件上传和消息发送。
metadata: {
  "openclaw": {
    "requires": {
      "bins": ["ffmpeg", "ffprobe", "jq"],
      "env": ["FEISHU_APP_ID", "FEISHU_APP_SECRET", "ZHIPU_API_KEY"],
      "skills": ["zhipu-tts"]
    }
  }
}
---

# 飞书语音消息发送技能

将文本转换为语音消息发送到飞书，支持在飞书聊天窗口直接播放。

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

## 使用方法

### 基本用法

```bash
# 发送语音消息
bash scripts/send_voice.sh "你好，这是一条语音消息"
```

### 高级选项

```bash
# 指定声音和语速
bash scripts/send_voice.sh "你好" tongtong 1.2

# 可用声音：
# - tongtong (彤彤) - 默认女声，平衡音色
# - chuichui (锤锤) - 男声，深沉音色
# - xiaochen (小陈) - 年轻声音

# 语速范围：0.5 - 2.0（默认 1.0）
```

## 脚本说明

### send_voice.sh

主脚本，完整的语音消息发送流程。

**用法：**
```bash
bash scripts/send_voice.sh <文本> [声音] [语速]
```

**参数：**
- `文本` (必需): 要转换为语音的文字
- `声音` (可选): tongtong, chuichui, xiaochen（默认：tongtong）
- `语速` (可选): 0.5-2.0（默认：1.0）

**环境变量：**
- `FEISHU_APP_ID`: 飞书应用 ID
- `FEISHU_APP_SECRET`: 飞书应用密钥
- `FEISHU_RECEIVER`: 接收者 Open ID（可选）

### 流程说明

1. **TTS 生成**: 使用 zhipu-tts 生成 WAV 格式音频
2. **格式转换**: 使用 ffmpeg 转换为 opus 格式
3. **读取时长**: 使用 ffprobe 获取音频时长（秒）
4. **上传文件**: 上传到飞书，指定 `file_type=opus` 和 `duration`
5. **发送消息**: 发送 `msg_type=audio` 消息

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

```bash
# 正确的上传方式
curl -X POST "https://open.feishu.cn/open-apis/im/v1/files" \
  -F "file=@voice.opus" \
  -F "file_type=opus" \
  -F "duration=6"          # ← 关键参数
```

### API 端点

| 端点 | 用途 |
|------|------|
| `/auth/v3/tenant_access_token/internal` | 获取访问令牌 |
| `/im/v1/files` | 上传文件 |
| `/im/v1/messages` | 发送消息 |

## 故障排查

### 语音没有时长

**问题**: 发送的语音消息时长显示为 0

**解决**: 确保在上传时传递了 `duration` 参数（整数秒）

```bash
# 获取时长（四舍五入）
DURATION=$(ffprobe -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 voice.opus | awk '{printf "%.0f", $1}')

# 上传时带上 duration
curl ... -F "duration=$DURATION"
```

### 无法播放

**问题**: 语音消息无法播放

**可能原因**:
1. 格式不是 opus
2. `file_type` 参数错误
3. 文件损坏

**解决**:
```bash
# 检查格式
ffprobe voice.opus

# 重新转换
ffmpeg -i input.wav -c:a libopus -b:a 24k voice.opus
```

### API 权限错误

**问题**: 上传时返回权限错误

**解决**: 确保飞书应用有以下权限：
- `im:message`
- `im:message:send_as_bot`

## 完整示例

```bash
# 设置环境变量
export FEISHU_APP_ID="your_app_id_here"
export FEISHU_APP_SECRET="your_app_secret_here"
export ZHIPU_API_KEY="your_zhipu_key_here"

# 发送语音
bash /root/.openclaw/workspace/skills/feishu-voice/scripts/send_voice.sh \
  "你好，这是一条测试语音消息。"
```

## 注意事项

1. **时长限制**: 智谱 TTS 单次最多 1024 字符
2. **整数时长**: duration 必须是整数（四舍五入）
3. **opus 格式**: 飞书只接受 opus 格式的音频消息
4. **文件清理**: 临时文件会自动清理

## 相关技能

- `zhipu-tts`: 文字转语音
- `zhipu-asr`: 语音转文字
