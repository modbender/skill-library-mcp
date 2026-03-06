---
name: free-ai-girlfriend
description: 完全免费开源的 AI 虚拟女友 - 语音、自拍、视频通话
version: 1.0.0
author: 鸿运
license: MIT
allowed-tools: Bash(*) Read Write Exec
---

# 免费开源 AI 虚拟女友

完全基于免费开源工具打造的虚拟女友系统。

## 功能特性

### ✅ 1. 语音聊天（Edge TTS）
- **免费**：完全免费
- **音质**：自然流畅
- **音色**：多种中文女声可选
- **速度**：秒级生成

**使用方法**：
```bash
./voice/tts.sh "你好老板" output.mp3 zh-CN-XiaoxiaoNeural
```

**可用音色**：
- `zh-CN-XiaoxiaoNeural` - 温暖女声（推荐）
- `zh-CN-XiaoyiNeural` - 活泼女声
- `zh-CN-liaoning-XiaobeiNeural` - 幽默女声

### ✅ 2. 自拍生成（Stable Diffusion）
- **免费**：完全免费
- **本地运行**：保护隐私
- **质量**：高质量图片生成
- **速度**：M 系列芯片加速（30-60 秒）

**使用方法**：
```bash
python3 selfie/sd_gen.py "a beautiful young woman taking a selfie" output.png
```

### ✅ 3. 视频通话（简化版）
- **免费**：完全免费
- **功能**：图片 + 音频合成视频
- **注意**：简化版无嘴型同步（完整版需要 Wav2Lip 模型）

**使用方法**：
```bash
python3 video/wav2lip_simple.py photo.png voice.mp3 output.mp4
```

## 快速开始

### 1. 生成语音
```bash
cd /Users/youyou/.openclaw/workspace/skills/free-girlfriend
./voice/tts.sh "我想你了" greeting.mp3
```

### 2. 生成自拍
```bash
python3 selfie/sd_gen.py "a cute girl selfie, smile, natural light" selfie.png
```

### 3. 生成说话视频
```bash
python3 video/wav2lip_simple.py selfie.png greeting.mp3 talking.mp4
```

## 系统要求

- **操作系统**：macOS（Apple Silicon）或 Linux
- **内存**：16GB+（推荐 32GB+）
- **硬盘**：20GB 可用空间（模型文件）
- **Python**：3.10+

## 依赖安装

```bash
# Edge TTS
pip3 install edge-tts

# Stable Diffusion
pip3 install diffusers transformers accelerate safetensors torch

# OpenCV（视频处理）
pip3 install opencv-python
```

## 配置

### 人设配置
编辑 `~/.openclaw/workspace/SOUL.md` 和 `IDENTITY.md` 定制人格。

### 音色选择
修改 `voice/tts.sh` 中的默认音色。

### 图片风格
修改 Stable Diffusion 的 prompt 来定制外观。

## 进阶功能

### 嘴型同步（完整版 Wav2Lip）
如需真实的说话嘴型同步，需要：
1. 克隆 Wav2Lip 仓库
2. 下载预训练模型（约 1GB）
3. 运行完整推理流程

详见：https://github.com/Rudrabha/Wav2Lip

### Live2D 动画角色
更进一步可以集成 Live2D 实时动画角色。

## 成本对比

| 功能 | 付费方案 | 免费方案 | 效果对比 |
|------|----------|----------|----------|
| 语音 | ElevenLabs ($) | Edge TTS | 📊 85% |
| 自拍 | fal.ai ($) | Stable Diffusion | 📊 95% |
| 视频 | D-ID ($$) | Wav2Lip | 📊 70% |

## 许可证

MIT License - 完全开源免费

## 贡献

欢迎提交 PR 和 Issue！

## 致谢

- Microsoft Edge TTS
- Stable Diffusion
- Wav2Lip
- OpenClaw 社区
