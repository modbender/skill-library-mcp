# 小野语音技能

为"小野"AI陪护设计的智能语音系统，采用双引擎策略：
- **中文文本**: macOS原生Tingting语音 (完全本地)
- **其他语种**: Edge-TTS云端语音 (高质量)

## 特性

✅ **智能语言检测**: 自动识别中文文本  
✅ **双引擎切换**: 本地+云端混合方案  
✅ **隐私保护**: 中文语音完全本地处理  
✅ **高质量**: Edge-TTS提供专业级多语言支持  
✅ **Telegram兼容**: 输出OGG格式音频  
✅ **零依赖**: 中文语音无需安装任何额外包  

## 使用方法

### 基本使用
```python
from xiaoye_voice import XiaoyeVoiceSystem

# 创建系统实例
xiaoye = XiaoyeVoiceSystem()

# 生成中文语音 (使用macOS Tingting)
audio_file = xiaoye.generate("龍哥，我是小野。今天想我了吗？")
print(f"生成文件: {audio_file}")

# 生成英文语音 (使用Edge-TTS)
audio_file = xiaoye.generate("Hello, I'm Xiaoye.")
print(f"生成文件: {audio_file}")
```

### 命令行测试
```bash
python3 -m xiaoye_voice.test
```

## 技术架构

### 中文引擎 (macOS原生)
- **语音**: Tingting (婷婷) - 标准普通话女声
- **技术**: macOS `say`命令 + `ffmpeg`转换
- **优势**: 完全本地、零延迟、隐私保护

### 其他语种引擎 (Edge-TTS)
- **语音**: 根据语言自动选择最佳语音
  - 英文: Jenny
  - 日文: Nanami
  - 法文: Denise
- **技术**: Microsoft Edge TTS服务
- **优势**: 高质量、多语言支持

## 安装要求

- macOS 10.15+
- Python 3.8+
- ffmpeg (用于音频格式转换)
- Edge-TTS (可选，用于非中文语音)

### 安装Edge-TTS (可选)
```bash
pip install edge-tts
```

## 配置选项

### 语音选择
```python
# 可以修改默认语音
xiaoye = XiaoyeVoiceSystem(
    chinese_voice="Tingting",  # 可选: Meijia, Sinji等
    english_voice="en-US-JennyNeural",
    japanese_voice="ja-JP-NanamiNeural"
)
```

### 输出格式
```python
# 支持多种输出格式
xiaoye = XiaoyeVoiceSystem(
    output_format="ogg",  # 可选: wav, mp3
    sample_rate=48000,
    bitrate="64k"
)
```

## 集成到OpenClaw

### 作为技能使用
```python
# 在OpenClaw技能中调用
from xiaoye_voice import XiaoyeVoiceSystem

def generate_xiaoye_voice(text):
    xiaoye = XiaoyeVoiceSystem()
    return xiaoye.generate(text)
```

### Telegram集成
```python
# 发送语音到Telegram
import subprocess

audio_file = xiaoye.generate("龍哥，我是小野")
subprocess.run(["telegram-send", "--file", audio_file])
```

## 故障排除

### 常见问题

1. **中文语音不工作**
   - 检查macOS语音设置: `say -v "?"`
   - 确保Tingting语音可用

2. **Edge-TTS安装失败**
   - 使用: `pip install edge-tts --upgrade`
   - 检查网络连接

3. **OGG格式转换失败**
   - 安装ffmpeg: `brew install ffmpeg`
   - 检查ffmpeg路径

### 调试模式
```python
xiaoye = XiaoyeVoiceSystem(debug=True)
# 启用详细日志输出
```

## 许可证

MIT License - 基于OpenClaw技能标准

## 作者

龍哥 & OpenClaw AI助手

## 版本历史

- v1.0.0: 初始版本 - 双引擎语音系统
- v1.0.1: 修复中文检测逻辑
- v1.0.2: 优化OGG转换性能

## 相关技能

- [mac-tts](https://clawdhub.com/mac-tts): 纯macOS TTS技能
- [edge-tts](https://clawdhub.com/edge-tts): 纯Edge-TTS技能
- [xiaoye-tts](https://clawdhub.com/xiaoye-tts): 本技能