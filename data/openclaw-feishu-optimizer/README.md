# OpenClaw 飞书体验优化者

## 📱 项目介绍

专为 OpenClaw 在飞书平台上优化体验的技能包，提供语音识别、消息格式化、智能回复等增强功能。

**版本**: 1.0.0  
**作者**: 黄绍帅（黄白）  
**语言**: 中文/英文  
**类型**: OpenClaw 技能包

## ✨ 核心功能

### 🔊 语音识别
- **自动语音识别**: 收到语音消息时自动识别为文字
- **多语言支持**: 支持中文、英文等多种语言
- **格式自动转换**: 自动处理各种音频格式（MP3、WAV、FLAC、OGG等）

### 📝 消息优化
- **智能回复格式化**: 优化回复内容的排版
- **表情识别**: 理解并回应表情符号
- **上下文感知**: 根据对话上下文提供更合适的回复

### 💬 飞书平台优化
- **消息类型支持**: 处理文字、语音、图片、文件等各种消息类型
- **响应时间优化**: 提升消息处理和回复速度
- **错误处理**: 优雅处理各种异常情况

## 🚀 快速开始

### 1. 安装依赖

```bash
pip3 install SpeechRecognition pydub
```

### 2. 使用技能

#### 处理语音消息

```bash
# 识别中文语音
python3 /root/.openclaw/workspace/skills/openclaw-feishu-optimizer/voice-recognize.py <音频文件路径>

# 识别英文语音
python3 /root/.openclaw/workspace/skills/openclaw-feishu-optimizer/voice-recognize.py <音频文件路径> --language en-US
```

#### 处理消息

```bash
# 处理消息
python3 /root/.openclaw/workspace/skills/openclaw-feishu-optimizer/process-message.py <消息数据>

# 处理音频文件
python3 /root/.openclaw/workspace/skills/openclaw-feishu-optimizer/process-message.py /path/to/audio.mp3
```

## 📖 使用示例

### 示例 1: 处理语音消息

```bash
python3 /root/.openclaw/workspace/skills/openclaw-feishu-optimizer/voice-recognize.py /tmp/audio.mp3 --language zh-CN
```

**输出**:
```
正在识别语音（语言: zh-CN）...
识别成功: 你好，我是虾姐！有什么需要我帮助的吗？

识别结果: 你好，我是虾姐！有什么需要我帮助的吗？
```

### 示例 2: 处理文字消息

```bash
python3 /root/.openclaw/workspace/skills/openclaw-feishu-optimizer/process-message.py "你好"
```

**输出**:
```
检测到文字消息

原始内容: 你好
格式化后: 你好。
处理状态: 成功
```

### 示例 3: 完整流程

```bash
# 处理语音文件并保存结果
python3 /root/.openclaw/workspace/skills/openclaw-feishu-optimizer/process-message.py /path/to/audio.ogg --language zh-CN --output /tmp/result.json
```

## 🔧 技能配置

技能配置文件位于 `config.json`，可以根据需要调整以下参数：

```json
{
  "features": {
    "voice_recognition": {
      "enabled": true,
      "default_language": "zh-CN"
    },
    "message_formatting": {
      "auto_punctuation": true,
      "emoji_support": true
    }
  },
  "settings": {
    "timeout": 30,
    "retry_attempts": 3
  }
}
```

## 🛠️ 故障排除

### 1. 依赖安装失败

```bash
# 使用国内源安装
pip3 install SpeechRecognition pydub -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 语音识别失败

- 检查网络连接
- 检查音频文件是否损坏
- 尝试指定语言参数 `--language zh-CN`
- 检查音频质量

### 3. 运行权限问题

```bash
# 确保脚本有执行权限
chmod +x /root/.openclaw/workspace/skills/openclaw-feishu-optimizer/voice-recognize.py
chmod +x /root/.openclaw/workspace/skills/openclaw-feishu-optimizer/process-message.py
```

## 📈 性能优化

### 1. 识别速度优化

- 使用本地音频处理
- 提前转换音频格式
- 避免同时处理多个语音消息

### 2. 资源使用优化

- 合理设置超时时间
- 避免重复处理同一消息
- 定期清理临时文件

## 🤝 贡献指南

### 报告问题

- 详细描述问题现象
- 提供使用场景和配置
- 包括错误信息和日志

### 功能建议

- 说明功能需求
- 解释应用场景
- 提供预期的行为

## 📄 许可证

本技能包遵循 OpenClaw 技能协议，仅供学习和个人使用。

## 📞 联系方式

如有问题或建议，欢迎联系作者：
- **微信**: [黄白]
- **邮箱**: 847193417@qq.com
- **小红书/抖音**: 黄白

---

**OpenClaw 飞书体验优化者** - 让飞书使用体验更出色！🚀
