# 🎤 语音对话系统

基于OpenClaw的完整双向语音对话解决方案，支持语音输入和语音输出。

## ✨ 功能特性

### 🎯 核心功能
- **语音转文本（STT）**：实时识别用户语音
- **文本转语音（TTS）**：使用OpenClaw TTS生成语音响应
- **双向对话**：自然的语音交流体验
- **多语言支持**：中文优先，可扩展其他语言

### 🔧 技术特点
- **离线/在线混合**：支持本地和云端语音识别
- **模块化设计**：易于扩展和定制
- **错误处理**：完善的异常处理和用户反馈
- **配置灵活**：支持多种语音引擎和参数调整

## 🚀 快速开始

### 1. 安装依赖
```powershell
# 运行安装脚本
.\install_deps.ps1
```

### 2. 启动系统
```powershell
# 方法1：使用启动脚本
.\voice_chat_launcher.ps1

# 方法2：直接运行
python voice_chat.py
```

### 3. 使用菜单
```
📱 语音对话系统菜单
==================================================
1. 🎧 开始语音对话
2. 🔊 测试麦克风
3. 🗣️  测试TTS功能
4. 📋 显示系统信息
5. ❌ 退出
==================================================
```

## 📁 文件结构

```
voice-chat-skill/
├── SKILL.md              # OpenClaw技能定义
├── voice_chat.py         # 主程序
├── install_deps.ps1      # 依赖安装脚本
├── voice_chat_launcher.ps1 # 快速启动脚本
└── README.md            # 本文档
```

## 🔧 系统要求

### 必需组件
- **Python 3.8+**
- **麦克风**（内置或外接）
- **扬声器/耳机**

### Python依赖
```bash
# 核心依赖
SpeechRecognition    # 语音识别库
pyaudio             # 音频输入输出

# Windows特殊安装
pipwin              # Windows音频库安装工具
```

## 🎛️ 配置选项

### 语音识别引擎
系统支持多种语音识别引擎：

1. **Google Speech Recognition**（默认）
   - 免费，需要网络
   - 支持多种语言
   - 准确度较高

2. **Whisper**（本地）
   - 离线运行
   - 需要安装Whisper模型
   - 隐私保护更好

3. **其他引擎**
   - Sphinx（离线）
   - Azure Speech Services
   - Google Cloud Speech

### 语言设置
```python
# 修改语言设置
voice_chat = VoiceChatSystem(language='zh-CN')  # 中文
voice_chat = VoiceChatSystem(language='en-US')  # 英文
```

## 💡 使用技巧

### 最佳实践
1. **环境准备**
   - 在安静环境中使用
   - 首次使用校准环境噪音
   - 确保麦克风音量适中

2. **对话技巧**
   - 说话清晰，语速适中
   - 每句话后稍作停顿
   - 使用明确的结束词（如"完毕"）

3. **故障排除**
   - 如果无法识别，检查麦克风权限
   - 网络问题可切换本地引擎
   - 音频问题检查驱动设置

### 命令示例
```
用户: "你好，今天天气怎么样？"
AI: "今天天气晴朗，温度适宜。"

用户: "现在几点了？"
AI: "现在是下午3点20分。"

用户: "退出"
AI: "好的，结束对话。再见！"
```

## 🔄 扩展开发

### 添加新功能
```python
class EnhancedVoiceChat(VoiceChatSystem):
    def __init__(self):
        super().__init__()
        # 添加自定义功能
        
    def custom_response(self, user_input):
        # 自定义响应逻辑
        pass
```

### 集成AI模型
```python
def integrate_ai_model(self, user_input):
    """集成真正的AI模型"""
    # 调用OpenAI API
    # 或使用本地LLM
    # 返回AI生成的响应
```

### 添加语音命令
```python
def voice_commands(self, text):
    """语音命令识别"""
    commands = {
        "打开灯": self.turn_on_light,
        "播放音乐": self.play_music,
        "设置提醒": self.set_reminder,
    }
    
    for cmd, func in commands.items():
        if cmd in text:
            return func()
```

## 🛠️ 故障排除

### 常见问题

#### 1. 麦克风无法识别
```
✅ 解决方案：
- 检查麦克风是否连接
- 检查系统音频设置
- 运行麦克风测试功能
```

#### 2. 语音识别准确率低
```
✅ 解决方案：
- 降低环境噪音
- 调整麦克风距离
- 使用更准确的识别引擎
```

#### 3. TTS无法工作
```
✅ 解决方案：
- 检查OpenClaw TTS配置
- 验证网络连接
- 检查音频输出设备
```

#### 4. Python依赖安装失败
```
✅ 解决方案：
- 使用管理员权限运行
- 尝试国内镜像源
- 手动安装依赖
```

### 调试模式
```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 相关资源

### 文档链接
- [SpeechRecognition文档](https://pypi.org/project/SpeechRecognition/)
- [PyAudio文档](https://people.csail.mit.edu/hubert/pyaudio/)
- [OpenClaw TTS文档](https://docs.openclaw.ai/tools/tts)

### 学习资源
- 语音识别原理
- 自然语言处理基础
- 音频处理技术

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发流程
1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

### 代码规范
- 遵循PEP 8编码规范
- 添加适当的注释
- 编写单元测试

## 📄 许可证

本项目采用MIT许可证。详见LICENSE文件。

## 📞 支持与反馈

如有问题或建议，请：
1. 查看[常见问题](#故障排除)
2. 提交GitHub Issue
3. 联系维护者

---

**最后更新：2026-02-28**
**版本：1.0.0**