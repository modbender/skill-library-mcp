# Telegram Offline Voice 🎙️

**让你的 AI 助手开口说话：本地化、工程化、零成本的 Telegram 语音解决方案。**

这是一个专为 OpenClaw 和 AI 智能体设计的语音生成技能。它不仅能将文字转为声音，更能通过智能清洗和分段，将枯燥的 AI 输出转化为自然、优雅的 Telegram 语音气泡。

## 🚀 重大工程化更新

本次更新将本项目从一个简单的“工具脚本”提升到了“生产级组件”：

1.  **智能文本清洗**：内置强大的正则引擎，自动剔除 Markdown 语法噪音（如加粗、代码块、链接地址等），让 AI 像真人一样读出干净的文本。
2.  **长文本自动分段**：突破 TTS 的长度限制和听觉疲劳，根据标点符号自动切分为连续的语音气泡，完美适配 Telegram 的交互习惯。
3.  **UUID 临时文件管理**：采用唯一标识符处理并发请求，即使多个子代理同时工作，也不会发生文件覆盖或读取冲突。
4.  **一键封装脚本**：全新的 `voice_gen.py`，支持 `uv` 运行，无需复杂的环境配置，一个命令直接输出最终的 `.ogg` 文件。

## ✨ 核心优势

- 🔒 **隐私保护**：100% 本地音频处理，不经过任何额外云端 TTS 提供商。
- 💰 **零token消耗**：使用免费的 Edge-TTS 引擎，省下昂贵的 API 额度。
- 🎧 **原生体验**：生成的 OGG Opus 编码文件会被 Telegram 识别为“语音消息”，而非普通的音频文件附件。

## 🔧 快速开始

### 1. 安装依赖
```bash
sudo apt update && sudo apt install ffmpeg python3-pip -y
```

### 2. 运行生成
```bash
uv run scripts/voice_gen.py --text "你好，我是阿威。这是我的最新版语音引擎测试！"
```

## 📖 文档

有关参数配置说明和 OpenClaw 集成指南，请阅读 [SKILL.md](./SKILL.md)。

---

## 👨💻 联系作者

调优与维护：**[@sanwe](https://x.com/sanwe)**
Twitter: [https://x.com/sanwe](https://x.com/sanwe)

欢迎 Star 或提交 PR 共同完善 OpenClaw 生态！🦞
