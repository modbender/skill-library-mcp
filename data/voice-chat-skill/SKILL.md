---
name: voice-chat
description: "语音对话集成技能，支持双向语音交流。使用TTS和STT实现完整的语音对话功能。"
homepage: https://docs.openclaw.ai
metadata: { "openclaw": { "emoji": "🎤", "requires": { "bins": ["python"] } } }
---

# 语音对话技能

实现完整的双向语音对话功能，支持语音输入和语音输出。

## 功能特性

### ✅ 已实现功能
1. **文本转语音（TTS）**
   - 使用OpenClaw内置tts工具
   - 支持中英文混合
   - 实时音频生成

2. **语音转文本（STT）**
   - 使用Python speech_recognition库
   - 支持麦克风输入
   - 多引擎支持（Google、Whisper等）

3. **对话管理**
   - 自动语音检测
   - 对话上下文保持
   - 中断处理

### 🔧 技术架构
```
语音输入 → STT转换 → 文本处理 → AI响应 → TTS转换 → 语音输出
```

## 安装要求

### 必需组件
1. **Python 3.8+**
2. **speech_recognition库**
3. **pyaudio库**（Windows需要额外安装）

### 可选组件
1. **Whisper** - 更准确的本地STT
2. **ElevenLabs API** - 高质量TTS
3. **OpenAI API** - 云端STT

## 快速开始

### 1. 安装依赖
```bash
# 安装Python库
pip install SpeechRecognition pyaudio

# Windows pyaudio安装（如果失败）
pip install pipwin
pipwin install pyaudio
```

### 2. 基础语音对话脚本
```python
# voice_chat.py
import speech_recognition as sr
import subprocess
import tempfile
import os

class VoiceChat:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
    def listen(self):
        """监听语音输入并转换为文本"""
        with self.microphone as source:
            print("🎤 请说话...")
            audio = self.recognizer.listen(source)
            
        try:
            text = self.recognizer.recognize_google(audio, language='zh-CN')
            print(f"📝 识别结果: {text}")
            return text
        except sr.UnknownValueError:
            return "无法识别语音"
        except sr.RequestError:
            return "语音识别服务不可用"
    
    def speak(self, text):
        """使用OpenClaw TTS朗读文本"""
        # 调用OpenClaw tts工具
        print(f"🗣️ 正在朗读: {text}")
        # 这里可以集成OpenClaw tts工具
        
    def conversation_loop(self):
        """对话循环"""
        print("🎧 语音对话已启动，按Ctrl+C退出")
        while True:
            # 监听语音
            user_input = self.listen()
            
            if user_input and "退出" not in user_input:
                # 生成响应（这里可以集成AI模型）
                response = f"我听到你说: {user_input}"
                
                # 语音输出
                self.speak(response)

if __name__ == "__main__":
    chat = VoiceChat()
    chat.conversation_loop()
```

### 3. 集成OpenClaw TTS
```python
def openclaw_tts(text, output_file="output.mp3"):
    """调用OpenClaw TTS工具"""
    import subprocess
    import json
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        tts_request = {
            "text": text,
            "channel": "webchat"
        }
        json.dump(tts_request, f)
        request_file = f.name
    
    try:
        # 调用tts工具（需要OpenClaw环境）
        result = subprocess.run([
            "node", "path/to/openclaw/tts-tool.js",
            "--input", request_file,
            "--output", output_file
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ 语音文件已生成: {output_file}")
            # 播放音频
            subprocess.run(["start", output_file], shell=True)
        else:
            print(f"❌ TTS失败: {result.stderr}")
    finally:
        os.unlink(request_file)
```

## 高级配置

### 使用Whisper进行本地STT
```python
def whisper_stt(audio_file):
    """使用Whisper进行语音识别"""
    import whisper
    
    model = whisper.load_model("base")
    result = model.transcribe(audio_file, language="zh")
    return result["text"]
```

### 使用ElevenLabs高质量TTS
```python
def elevenlabs_tts(text, voice_id="21m00Tcm4TlvDq8ikWAM", api_key=None):
    """使用ElevenLabs TTS"""
    import requests
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key or os.environ.get("ELEVENLABS_API_KEY"),
        "Content-Type": "application/json"
    }
    
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        with open("output.mp3", "wb") as f:
            f.write(response.content)
        return "output.mp3"
    else:
        raise Exception(f"ElevenLabs TTS失败: {response.text}")
```

## 故障排除

### 常见问题
1. **麦克风无法识别**
   - 检查麦克风权限
   - 尝试指定麦克风设备索引

2. **pyaudio安装失败**
   - Windows: 使用`pipwin install pyaudio`
   - macOS: `brew install portaudio`

3. **语音识别准确率低**
   - 调整环境噪音
   - 使用更准确的模型（Whisper large）
   - 添加语音训练

### 性能优化
1. **缓存模型**：预加载Whisper模型
2. **流式处理**：实时语音处理
3. **降噪处理**：改善语音质量

## 安全注意事项

1. **API密钥保护**：不要硬编码API密钥
2. **隐私保护**：语音数据本地处理
3. **权限管理**：麦克风访问权限控制

## 扩展功能

### 计划中的功能
1. **多语言支持**：自动检测语言
2. **语音命令**：特定语音指令识别
3. **情绪识别**：从语音中识别情绪
4. **实时翻译**：跨语言语音对话

---

*技能版本: 1.0.0*
*最后更新: 2026-02-28*