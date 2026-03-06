---
name: feishu-audio
description: 将音频文件转换为飞书可播放的语音消息。先用 ffmpeg 转为 opus 格式，再上传到飞书，最后发送 audio 消息。适用于用户想要在飞书中收到可播放的语音消息的场景。
---

# feishu-audio

将本地音频文件转换为飞书可播放的语音消息。

## 适用场景

- 用户说"朗读 xxx"、"语音播报"
- 需要发送可播放的语音消息到飞书

## 前置条件

1. **ffmpeg** - 音频格式转换
   ```bash
   brew install ffmpeg
   ```

2. **飞书应用配置** - 需要以下环境变量：
   - `FEISHU_APP_ID`
   - `FEISHU_APP_SECRET`

3. **接收者** - 飞书用户 Open ID（从上下文获取或手动指定）

## 使用方法

### 方式 1：使用已有音频文件

```bash
bash scripts/send_audio.sh <音频文件路径> [接收者OpenID]
```

### 方式 2：结合 TTS 使用

先生成音频，再用本技能发送：

```bash
# 1. 用 edge-tts 生成音频
edge-tts -t "你好，我是小曦" -v zh-CN-XiaoxiaoNeural --write-media /tmp/voice.mp3

# 2. 转为 opus 并发送到飞书
bash scripts/send_audio.sh /tmp/voice.mp3
```

## 脚本说明

### send_audio.sh

主脚本，完整的音频消息发送流程。

**参数：**
- `$1` - 音频文件路径（必需）
- `$2` - 接收者 Open ID（可选，默认从环境变量 FEISHU_RECEIVER 获取）

**环境变量：**
- `FEISHU_APP_ID` - 飞书应用 ID
- `FEISHU_APP_SECRET` - 飞书应用密钥
- `FEISHU_RECEIVER` - 接收者 Open ID（可选）

**流程：**
1. 检查 ffmpeg 是否可用
2. 检查音频文件是否存在
3. 用 ffmpeg 转换为 opus 格式（飞书要求）
4. 获取飞书 tenant_access_token
5. 上传到飞书（file_type=opus）
6. 发送 audio 消息

## 音频格式要求

飞书语音消息要求：
- **格式**: opus (OGG 容器)
- **编码**: libopus
- **采样率**: 24000 Hz
- **声道**: 单声道

## 故障排查

### ffmpeg 未安装

```bash
brew install ffmpeg
```

### 上传失败

检查飞书应用权限：
- `im:message`
- `im:message:send_as_bot`

### 消息发送成功但无法播放

确认：
1. 上传时使用了 `file_type=opus`
2. 上传时传递了 `duration` 参数
