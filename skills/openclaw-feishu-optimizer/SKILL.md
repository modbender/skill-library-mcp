---
name: openclaw-feishu-optimizer
description: OpenClaw 飞书体验优化者 | 飞书消息处理增强技能包

提供语音识别、消息格式化、智能回复优化等功能，提升 OpenClaw 在飞书平台上的使用体验。

read_when:
  - 飞书体验优化
  - 语音识别消息
  - 飞书消息格式化
  - 飞书智能回复
metadata: {"clawdbot":{"emoji":"📱","requires":{"bins":["python3","pip3"]}}}
allowed-tools: Bash(openclaw-feishu-optimizer:*)
---

# OpenClaw 飞书体验优化者

专为 OpenClaw 在飞书平台上优化体验的技能包，提供语音识别、消息格式化、智能回复等增强功能。

## 功能特性

### 1. 语音识别处理
- **自动语音识别**：收到语音消息时自动识别为文字
- **多语言支持**：支持中文、英文等多种语言识别
- **格式自动转换**：自动处理各种音频格式（MP3、WAV、FLAC、OGG等）

### 2. 消息优化
- **智能回复格式化**：优化回复内容的排版
- **表情识别**：理解并回应表情符号
- **上下文感知**：根据对话上下文提供更合适的回复

### 3. 飞书平台优化
- **消息类型支持**：处理文字、语音、图片、文件等各种消息类型
- **响应时间优化**：提升消息处理和回复速度
- **错误处理**：优雅处理各种异常情况

## 依赖安装

```bash
pip3 install SpeechRecognition pydub
```

## 使用方法

### 识别语音消息

```bash
# 识别中文语音
python3 /root/.openclaw/workspace/skills/openclaw-feishu-optimizer/voice-recognize.py <音频文件路径> --language zh-CN

# 识别英文语音
python3 /root/.openclaw/workspace/skills/openclaw-feishu-optimizer/voice-recognize.py <音频文件路径> --language en-US
```

### 自动处理飞书消息

```bash
# 处理飞书消息的完整流程
python3 /root/.openclaw/workspace/skills/openclaw-feishu-optimizer/process-message.py <消息数据>
```

## 配置文件

### 技能配置

```json
{
  "name": "openclaw-feishu-optimizer",
  "version": "1.0.0",
  "description": "OpenClaw 飞书体验优化者",
  "author": "黄绍帅（黄白）",
  "language": "zh-CN",
  "auto_recognize_voice": true,
  "auto_format_response": true,
  "voice_recognition": {
    "provider": "google",
    "default_language": "zh-CN"
  },
  "message_formatting": {
    "enable_emoji": true,
    "enable_markdown": true,
    "enable_mention": true
  }
}
```

## 工作流程

### 处理语音消息

1. 检测到语音消息
2. 自动调用语音识别服务
3. 将识别结果转换为文字
4. 格式化回复内容
5. 发送优化后的回复

### 处理文字消息

1. 解析消息内容
2. 识别关键词和需求
3. 格式化回复
4. 添加表情和优化排版
5. 发送智能回复

## 故障排除

### 语音识别失败

1. 检查网络连接（Google Speech Recognition 需要联网）
2. 检查音频文件是否损坏
3. 尝试指定语言参数 `--language zh-CN`
4. 检查音频质量（确保音量适中、无明显噪音）

### 依赖安装失败

```bash
# 检查 pip 是否正常工作
pip3 --version

# 尝试使用国内源安装
pip3 install SpeechRecognition pydub -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 贡献与改进

欢迎提出改进意见和功能建议！你可以：

1. 报告问题和 bug
2. 建议新功能
3. 提交代码改进
4. 完善文档

## 许可证

本技能包遵循 OpenClaw 技能协议，仅供学习和个人使用。
