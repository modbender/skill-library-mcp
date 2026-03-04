# 小野语音技能

为"小野"AI陪护设计的智能语音系统，采用双引擎策略：
- **中文文本**: macOS原生Tingting语音 (完全本地)
- **其他语种**: Edge-TTS云端语音 (高质量)

## 快速开始

### 安装
```bash
# 使用ClawdHub安装
clawdhub install xiaoye-voice

# 或手动安装
git clone <repository>
cd xiaoye-voice-skill
```

### 基本使用
```python
from xiaoye_voice import XiaoyeVoiceSystem

# 创建系统实例
xiaoye = XiaoyeVoiceSystem()

# 生成中文语音
audio = xiaoye.generate("龍哥，我是小野。今天想我了吗？")
print(f"生成文件: {audio}")

# 生成英文语音
audio = xiaoye.generate("Hello, I'm Xiaoye.")
print(f"生成文件: {audio}")
```

### 命令行使用
```bash
# 生成语音
python3 -m xiaoye_voice "龍哥，我是小野" --output greeting.ogg

# 测试系统
python3 test_xiaoye.py

# 列出可用语音
python3 -m xiaoye_voice --list-voices
```

## 特性

- ✅ **智能语言检测**: 自动识别中、英、日、法文
- ✅ **双引擎切换**: 本地+云端混合方案
- ✅ **隐私保护**: 中文语音完全本地处理
- ✅ **高质量**: Edge-TTS提供专业级多语言支持
- ✅ **Telegram兼容**: 默认输出OGG格式
- ✅ **零依赖**: 中文语音无需安装额外包

## 系统要求

- **操作系统**: macOS 10.15+
- **Python**: 3.8+
- **系统工具**: 
  - `ffmpeg` (音频转换): `brew install ffmpeg`
  - macOS `say`命令 (内置)

### 可选依赖
```bash
# 用于非中文语音
pip install edge-tts
```

## 配置选项

### 初始化参数
```python
xiaoye = XiaoyeVoiceSystem(
    chinese_voice="Tingting",      # 中文语音
    english_voice="en-US-JennyNeural",  # 英文语音
    japanese_voice="ja-JP-NanamiNeural", # 日文语音
    output_format="ogg",           # 输出格式: ogg, wav, mp3
    sample_rate=48000,             # 采样率
    bitrate="64k",                 # 比特率
    debug=False                    # 调试模式
)
```

### 可用中文语音
macOS内置中文语音包括:
- `Tingting` (婷婷) - 标准普通话女声
- `Meijia` (美佳) - 台湾口音女声
- `Sinji` (新机) - 标准普通话男声
- 更多: 使用 `--list-voices` 查看

## 集成示例

### OpenClaw技能集成
```python
# 在OpenClaw技能中调用
from xiaoye_voice import XiaoyeVoiceSystem

class XiaoyeVoiceSkill:
    def __init__(self):
        self.tts = XiaoyeVoiceSystem()
    
    def speak(self, text):
        """生成并返回语音文件路径"""
        return self.tts.generate(text)
```

### Telegram机器人集成
```python
import telebot
from xiaoye_voice import XiaoyeVoiceSystem

bot = telebot.TeleBot("YOUR_TOKEN")
tts = XiaoyeVoiceSystem()

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # 生成语音
    audio_file = tts.generate(message.text)
    
    # 发送语音
    with open(audio_file, 'rb') as audio:
        bot.send_voice(message.chat.id, audio)
```

## 故障排除

### 常见问题

1. **中文语音不工作**
   ```bash
   # 检查macOS语音
   say -v "?"
   
   # 测试Tingting语音
   say -v Tingting "测试"
   ```

2. **Edge-TTS安装失败**
   ```bash
   # 升级pip
   pip install --upgrade pip
   
   # 安装edge-tts
   pip install edge-tts
   ```

3. **OGG转换失败**
   ```bash
   # 安装ffmpeg
   brew install ffmpeg
   
   # 检查ffmpeg版本
   ffmpeg -version
   ```

### 调试模式
```python
xiaoye = XiaoyeVoiceSystem(debug=True)
# 启用详细日志输出
```

## 性能优化

### 批量处理
```python
# 批量生成语音
texts = ["文本1", "文本2", "文本3"]
results = xiaoye.batch_generate(texts)
```

### 缓存机制
```python
import hashlib
from pathlib import Path

class CachedXiaoyeVoiceSystem(XiaoyeVoiceSystem):
    def generate(self, text):
        # 生成缓存键
        cache_key = hashlib.md5(text.encode()).hexdigest()
        cache_file = self.base_dir / f"{cache_key}.ogg"
        
        # 检查缓存
        if cache_file.exists():
            return str(cache_file)
        
        # 生成新语音
        return super().generate(text)
```

## 许可证

MIT License

## 支持与贡献

- **问题报告**: GitHub Issues
- **功能请求**: GitHub Discussions
- **贡献代码**: Pull Requests

## 版本历史

- **v1.0.0**: 初始版本 - 双引擎语音系统
- **v1.0.1**: 修复中文检测逻辑
- **v1.0.2**: 优化OGG转换性能

## 相关链接

- [OpenClaw中文社区](https://clawd.org.cn)
- [ClawdHub技能市场](https://clawdhub.com)
- [项目源代码](https://github.com/your-repo/xiaoye-voice-skill)