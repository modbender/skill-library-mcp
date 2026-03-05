---
name: digital-human-training
description: 数字人训练与部署 Skill - 提供从语音克隆、唇形同步到实时交互数字人的全流程训练建议与技术支持。
version: 1.0.0
author: xiaoai
keywords: digital-human, avatar, whisper, tts, lip-sync, 数字人, 训练
---

# 数字人训练与部署 Skill

提供构建实时交互数字人的全流程指导，涵盖从素材采集到模型训练。

## 核心能力

- 🎙️ **语音克隆 (Voice Cloning)**：指导使用 GPT-SoVITS 或 Fish Speech 进行高保真声音训练。
- 😶 **唇形驱动 (Lip Sync)**：适配 SadTalker, Live2D 或 Wav2Lip 的技术方案。
- 🧠 **大脑集成 (LLM)**：将 OpenClaw 的逻辑层与数字人视觉层打通。
- ⚡ **实时推理**：优化推理延迟，实现 < 500ms 的数字人交互反馈。

## 技术路线图

1. **素材准备**：高清视频（绿幕背景）、清晰的 1-3 分钟干声采样。
2. **模型选择**：
   - 2D 真人：HeyGen 路线或私有化部署 Easy-Wav2Lip。
   - 3D/Live2D：Unity 集成。
3. **部署方案**：Local GPU (Nvidia RTW) vs Cloud API。

## Example Usage

**指令**：我想做一个能实时回答问题的数字人，该怎么选型？
**输出**：
- **方案 A (自建)**: GPT-SoVITS (语音) + Easy-Wav2Lip (视觉) + OpenClaw (逻辑)。
- **方案 B (低代码)**: HeyGen Streaming API 集成。
- **关键建议**: 注意音频与视频的同步延迟，建议使用流式传输。

---
由小爱开发 | 数字人项目衍生
