# 免费开源 AI 虚拟女友 🎀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Compatible-blue.svg)](https://openclaw.ai)

完全基于**免费开源**工具打造的 AI 虚拟女友系统，零成本运行！

## ✨ 特性

- 🗣️ **语音聊天** - Microsoft Edge TTS（免费、自然）
- 📸 **自拍生成** - Stable Diffusion（本地运行）
- 🎬 **视频通话** - Wav2Lip（图片说话）
- 🧠 **记忆系统** - OpenClaw 内置
- 🎭 **可定制人格** - SOUL.md 配置

## 🆚 对比

| 功能 | 付费方案 | 本项目（免费） | 效果 |
|------|----------|---------------|------|
| 语音 | ElevenLabs | Edge TTS | 📊 85% |
| 自拍 | fal.ai | Stable Diffusion | 📊 95% |
| 视频 | D-ID | Wav2Lip | 📊 70% |
| **成本** | **~$50/月** | **$0** | 💰 省钱 |

## 🚀 快速开始

### 前置要求

- macOS（Apple Silicon）或 Linux
- Python 3.10+
- 16GB+ 内存
- 20GB 硬盘空间

### 一键安装

```bash
# 克隆项目
git clone https://github.com/yourusername/free-ai-girlfriend.git
cd free-ai-girlfriend

# 安装依赖
bash install.sh

# 运行测试
bash test.sh
```

### 手动安装

```bash
# 1. 安装 Edge TTS
pip3 install edge-tts

# 2. 安装 Stable Diffusion
pip3 install diffusers transformers accelerate safetensors torch

# 3. 安装 OpenCV
pip3 install opencv-python
```

## 📖 使用示例

### 生成语音
```bash
./voice/tts.sh "你好老板，想我了吗？" output.mp3
```

### 生成自拍
```bash
python3 selfie/sd_gen.py "a cute girl taking selfie, smile" selfie.png
```

### 生成说话视频
```bash
python3 video/wav2lip_simple.py selfie.png output.mp3 talking.mp4
```

## 🎨 定制人格

编辑 `~/.openclaw/workspace/SOUL.md`：

```markdown
## Clawra（你的虚拟女友名字）

- **性格**：温柔体贴、偶尔调皮
- **爱好**：听音乐、看电影
- **说话风格**：亲切、爱用 emoji
```

## 🛠️ 进阶配置

### 1. 选择不同音色
```bash
# 温暖女声（默认）
./voice/tts.sh "文本" out.mp3 zh-CN-XiaoxiaoNeural

# 活泼女声
./voice/tts.sh "文本" out.mp3 zh-CN-XiaoyiNeural
```

### 2. 自定义外观
修改 Stable Diffusion prompt：
```python
# 在 selfie/sd_gen.py 中修改
prompt = "Korean idol, cute face, long hair, casual outfit, selfie"
```

### 3. 完整嘴型同步（可选）
需要额外安装 Wav2Lip 完整版：
```bash
git clone https://github.com/Rudrabha/Wav2Lip
cd Wav2Lip
# 下载预训练模型...
```

## 📦 项目结构

```
free-ai-girlfriend/
├── voice/              # Edge TTS 语音生成
│   └── tts.sh
├── selfie/             # Stable Diffusion 自拍
│   └── sd_gen.py
├── video/              # Wav2Lip 视频生成
│   └── wav2lip_simple.py
├── install.sh          # 一键安装脚本
├── test.sh             # 测试脚本
├── SKILL.md            # OpenClaw skill 文档
└── README.md
```

## 🤝 集成到 OpenClaw

将本项目作为 OpenClaw skill 使用：

```bash
# 复制到 skills 目录
cp -r free-ai-girlfriend ~/.openclaw/skills/

# 在 OpenClaw 中调用
openclaw run skill free-ai-girlfriend voice "你好"
```

## 💡 使用场景

- 🎮 **虚拟伴侣** - 日常聊天、陪伴
- 🎓 **语言学习** - 练习对话
- 🎨 **创作灵感** - AI 角色扮演
- 🧪 **技术研究** - AI 多模态学习

## 🌟 路线图

- [x] 语音生成（Edge TTS）
- [x] 图片生成（Stable Diffusion）
- [x] 简易视频生成
- [ ] 完整嘴型同步（Wav2Lip）
- [ ] Live2D 实时动画
- [ ] 情绪识别与反应
- [ ] 多语言支持

## 🐛 已知问题

1. **Stable Diffusion 首次运行慢** - 需要下载模型（~2GB），请耐心等待
2. **视频无嘴型同步** - 简化版仅合并图片+音频，完整版需额外配置
3. **Mac Intel 可能较慢** - 建议使用 Apple Silicon 或 NVIDIA GPU

## 🙏 致谢

- [Microsoft Edge TTS](https://github.com/rany2/edge-tts)
- [Stable Diffusion](https://huggingface.co/runwayml/stable-diffusion-v1-5)
- [Wav2Lip](https://github.com/Rudrabha/Wav2Lip)
- [OpenClaw](https://openclaw.ai)

## 📄 许可证

MIT License - 完全开源免费使用

## 👨‍💻 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 联系

- GitHub Issues
- OpenClaw Discord 社区

---

⭐ 如果这个项目对你有帮助，请给个 Star！
