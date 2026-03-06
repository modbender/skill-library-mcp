# homepod-tts 🎙️

使用 Qwen3-TTS 语音克隆和 Home Assistant，通过 HomePod 播放带情绪的 TTS 语音。

## ✨ 特性

- 🎭 **自动情绪识别** - 根据文本内容自动判断情绪（开心、悲伤、生气、惊讶等）
- 🔊 **音量自动调节** - 播放前设为 40%，播放完成后恢复原音量
- ⏱️ **动态等待时间** - 根据音频时长自动计算等待时间
- 🏠 **无缝集成 Home Assistant** - 通过 HA API 控制 HomePod

## 📋 前置要求

### 1. Home Assistant

- Home Assistant 已安装并运行
- 获取 **Long-Lived Access Token**：
  - 登录 Home Assistant → 点击右上角头像
  - → Long-Lived Access Tokens → 创建令牌
- 确认 HomePod 实体 ID（开发者工具 → 状态 → 搜索 `media_player`）

### 2. Qwen3-TTS

```bash
# 安装 Miniforge/Miniconda
# 创建并激活环境
conda create -n qwen-tts python=3.10
conda activate qwen-tts

# 安装依赖
pip install torch soundfile
pip install modelscope
pip install Qwen/Qwen3-TTS-12Hz-0___6B-Base

# 或参考官方文档：https://github.com/Qwen/Qwen3-TTS
```

### 3. 参考音频

准备一段你的参考音频（.wav 格式，5-30 秒清晰人声），用于语音克隆。

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/homepod-tts.git
cd homepod-tts
```

### 2. 准备 TTS 脚本

本仓库提供 `tts/tts_sample.py` 示例脚本，你需要：

```bash
# 1. 创建 tts 目录并放入脚本
mkdir -p tts
# 复制 tts_sample.py 到 tts/ 目录

# 2. 准备参考音频
mkdir -p tts/your_ref_audio
# 放入你的参考音频 .wav 文件

# 3. 编辑 tts_sample.py
vim tts/tts_sample.py
# 修改 REF_AUDIO 和 REF_TEXT 为你的配置
```

### 3. 配置环境

```bash
cp .env.example .env
vim .env
```

### 4. 运行

```bash
./scripts/play-tts.sh "你好，这是测试消息"
```

## 📁 文件结构

```
homepod-tts/
├── README.md           # 本说明文件
├── .env.example       # 配置模板
├── .gitignore
├── scripts/
│   └── play-tts.sh    # 主播放脚本
└── tts/
    └── tts_sample.py  # TTS 示例脚本（需配置）
```

## ⚙️ 配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `HASS_URL` | Home Assistant URL | `http://homeassistant.local:8123` |
| `HASS_TOKEN` | Home Assistant 访问令牌 | 必填 |
| `HASS_ENTITY_ID` | HomePod 实体 ID | `media_player.ci_wo` |
| `HTTP_PORT` | 本地 HTTP 服务端口 | `8080` |
| `LOCAL_IP` | 本机 IP 地址 | 必填 |
| `CONDA_ENV_NAME` | Conda 环境名 | `qwen-tts` |
| `TTS_DIR` | TTS 脚本目录 | 必填 |

## 🎭 情绪识别

根据文本关键词自动识别情绪，支持：happy, excited, sad, angry, surprised, scared, serious, gentle, calm, funny, tired, nervous

## 🔧 故障排除

- **CondaError**: 确保 conda 已正确安装
- **Could not resolve host**: 检查 `HASS_URL` 配置
- **无声音**: 检查 HA 连接和实体 ID

## 📝 许可证

MIT License

## 🙏 致谢

- [Qwen3-TTS](https://github.com/Qwen/Qwen3-TTS)
- [Home Assistant](https://www.home-assistant.io/)
