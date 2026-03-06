---
name: Feishu Voice Skill - 飞书语音交互技能
description: 本技能用于实现飞书与 ElevenLabs 的语音交互，包括：
---

# Feishu Voice Skill - 飞书语音交互技能

## 概述

本技能用于实现飞书与 ElevenLabs 的语音交互，包括：
- 语音转文字（用户发语音 → 识别内容）
- 文字转语音（生成语音回复用户）
- 飞书语音消息的收发

---

## 1. 环境配置

### 1.1 ElevenLabs API Key

```bash
export ELEVENLABS_API_KEY="你的API Key"
```

### 1.2 FFmpeg 安装

```bash
apt-get update && apt-get install -y ffmpeg
```

---

## 2. 语音转文字（用户语音识别）

### 2.1 下载飞书语音

用户发送语音时，收到的是 `file_key`，需要通过以下步骤下载：

```bash
TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"app_id":"你的app_id","app_secret":"你的app_secret"}' | grep -o '"tenant_access_token":"[^"]*"' | cut -d'"' -f4)

# 下载语音文件
curl -s "https://open.feishu.cn/open-apis/im/v1/messages/{message_id}/resources/{file_key}?type=file" \
  -H "Authorization: Bearer $TOKEN" -o /path/to/voice.ogg
```

### 2.2 ElevenLabs 语音转文字

```bash
curl -s -X POST "https://api.elevenlabs.io/v1/speech-to-text?enable_logging=true" \
  -H "xi-api-key: ${ELEVENLABS_API_KEY}" \
  -F model_id="scribe_v1" \
  -F file=@/path/to/voice.ogg
```

返回结果包含 `text` 字段，即识别出的文字内容。

---

## 3. 文字转语音

### 3.1 ElevenLabs TTS 生成

```bash
curl -s -X POST "https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgDQGcFmaJgB" \
  -H "Content-Type: application/json" \
  -H "xi-api-key: ${ELEVENLABS_API_KEY}" \
  -d '{
    "text": "要转换的文字",
    "model_id": "eleven_multilingual_v2"
  }' -o /path/to/output.mp3
```

### 3.2 转换为飞书兼容格式

飞书语音需要 **Ogg/Opus 格式**，需要用 FFmpeg 转换：

```bash
ffmpeg -i input.mp3 -ar 16000 -ac 1 -acodec libopus output.ogg -y
```

---

## 4. 发送语音消息（飞书）

### 4.1 Node.js 实现

```javascript
const { Client } = require('@larksuiteoapi/node-sdk');
const fs = require('fs');

const client = new Client({
  appId: '你的appId',
  appSecret: '你的appSecret',
});

async function sendVoice(filePath, durationMs, receiveId) {
  // 1. 上传语音文件
  const uploadRes = await client.im.file.create({
    data: {
      file_type: 'opus',
      file_name: 'voice.ogg',
      file: fs.createReadStream(filePath),
      duration: durationMs
    }
  });
  
  const fileKey = uploadRes.file_key;
  
  // 2. 发送语音消息
  const sendRes = await client.im.message.create({
    params: { receive_id_type: 'open_id' },
    data: {
      receive_id: receiveId,
      msg_type: 'audio',
      content: JSON.stringify({ file_key: fileKey, duration: durationMs })
    }
  });
  
  return sendRes;
}
```

---

## 5. 常见问题

### 5.1 语音下载失败

**错误**: `"The app is not the resource sender"`

**原因**: 飞书安全限制，机器人只能下载自己发送的文件

**解决**: 用户需将语音转发给机器人（转发后机器人成为发送者）

### 5.2 TTS 生成文件为空

**检查**: 确认 `ELEVENLABS_API_KEY` 已设置且有余额

### 5.3 语音无法播放

**检查**: 
- 文件格式是否为 Ogg/Opus
- duration 参数是否正确
- 文件是否在允许的目录（workspace 目录）

### 5.4 消息太长被拦截

- 钉钉：单条消息超过约7000字符会被拦截，需要拆分多条发送
- 飞书：同样有限制

---

## 6. 飞书权限配置

需要以下权限：
- `im:message` - 消息收发
- `im:resource` - 文件/媒体资源
- `im:resource:download` - 下载消息资源

---

## 7. 完整流程示例

```
用户发送语音
    ↓
1. 获取 message_id 和 file_key
2. 下载语音文件 (type=file)
3. ElevenLabs 语音转文字 → 理解内容
4. 生成回复内容
5. ElevenLabs TTS 生成语音
6. FFmpeg 转为 Ogg 格式
7. 上传并发送语音消息给用户
```

---

## 8. 相关文件位置

- 临时语音文件: `/root/.openclaw/workspace/`
- TTS 转换: 需要 ffmpeg 支持

---

_最后更新: 2026-02-23_
