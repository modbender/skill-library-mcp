#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版语音对话系统 - 支持多种语音识别模式
1. Google在线识别 (默认，需网络)
2. 模拟键盘输入 (离线，用于测试)
3. Vosk离线识别 (可选，需额外安装)
"""

import sys
import os
import time
import tempfile
import json
import subprocess
from typing import Optional, Dict, Any

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    print("⚠️  speech_recognition库未安装")

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("⚠️  pyaudio库未安装，部分音频功能受限")

class EnhancedVoiceChat:
    """增强版语音对话系统"""
    
    def __init__(self, language: str = "zh-CN", recognition_mode: str = "auto"):
        """
        初始化
        
        Args:
            language: 语言代码 (zh-CN, en-US等)
            recognition_mode: 识别模式 auto|google|simulate|keyboard
        """
        self.language = language
        self.recognition_mode = recognition_mode
        
        # 识别器实例
        self.recognizer = None
        self.microphone = None
        
        # 自动检测最佳模式
        if recognition_mode == "auto":
            self.recognition_mode = self._detect_best_mode()
        
        print(f"🎤 语音对话系统初始化")
        print(f"📝 语言设置: {self.language}")
        print(f"🔧 识别模式: {self.recognition_mode}")
        print("=" * 50)
        
        # 初始化选定的模式
        self._initialize_mode()
    
    def _detect_best_mode(self) -> str:
        """自动检测最佳识别模式"""
        # 检查网络连接
        network_ok = self._check_network()
        
        if network_ok and SPEECH_RECOGNITION_AVAILABLE and PYAUDIO_AVAILABLE:
            return "google"
        elif SPEECH_RECOGNITION_AVAILABLE and PYAUDIO_AVAILABLE:
            # 有依赖但网络可能不可用
            return "google"  # 尝试Google，失败后降级
        else:
            return "simulate"
    
    def _check_network(self) -> bool:
        """检查网络连接"""
        import urllib.request
        import socket
        
        try:
            # 快速测试连接
            socket.setdefaulttimeout(3)
            urllib.request.urlopen('https://www.baidu.com', timeout=3)
            return True
        except:
            return False
    
    def _initialize_mode(self):
        """初始化选定模式"""
        if self.recognition_mode in ["google", "auto"] and SPEECH_RECOGNITION_AVAILABLE:
            self._init_google_mode()
        elif self.recognition_mode == "simulate":
            self._init_simulate_mode()
        elif self.recognition_mode == "keyboard":
            self._init_keyboard_mode()
        else:
            print(f"❌ 不支持的识别模式: {self.recognition_mode}")
            print("🔧 回退到模拟模式")
            self.recognition_mode = "simulate"
            self._init_simulate_mode()
    
    def _init_google_mode(self):
        """初始化Google语音识别模式"""
        print("🔧 初始化Google语音识别...")
        
        if not SPEECH_RECOGNITION_AVAILABLE:
            print("❌ speech_recognition库未安装")
            print("💡 请运行: pip install SpeechRecognition")
            return
        
        if not PYAUDIO_AVAILABLE:
            print("⚠️  pyaudio未安装，无法使用麦克风")
            print("💡 回退到模拟模式")
            self.recognition_mode = "simulate"
            self._init_simulate_mode()
            return
        
        try:
            self.recognizer = sr.Recognizer()
            
            # 检测音频设备
            mic_list = sr.Microphone.list_microphone_names()
            if mic_list:
                print(f"✅ 找到 {len(mic_list)} 个音频设备")
                for i, name in enumerate(mic_list[:5]):  # 只显示前5个
                    print(f"  {i}: {name}")
                
                # 选择默认麦克风
                default_mic_index = 0
                self.microphone = sr.Microphone(device_index=default_mic_index)
                
                # 校准环境噪音
                with self.microphone as source:
                    print("🎧 正在校准环境噪音，请保持安静...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    print("✅ 环境噪音校准完成")
            else:
                print("⚠️  未检测到麦克风设备")
                print("💡 回退到模拟模式")
                self.recognition_mode = "simulate"
                self._init_simulate_mode()
                
        except Exception as e:
            print(f"❌ Google模式初始化失败: {e}")
            print("💡 回退到模拟模式")
            self.recognition_mode = "simulate"
            self._init_simulate_mode()
    
    def _init_simulate_mode(self):
        """初始化模拟模式"""
        print("🔧 初始化模拟语音模式...")
        print("💡 此模式下将模拟语音输入进行对话")
        
        # 模拟语音序列
        self.simulated_inputs = [
            "你好",
            "现在几点了",
            "今天天气怎么样",
            "谢谢",
            "再见"
        ]
        self.simulated_index = 0
    
    def _init_keyboard_mode(self):
        """初始化键盘输入模式"""
        print("🔧 初始化键盘输入模式...")
        print("💡 此模式下将通过键盘输入文本进行对话")
    
    def listen(self, timeout: int = 5, phrase_time_limit: int = 10) -> Optional[str]:
        """
        监听语音输入
        
        Args:
            timeout: 等待语音开始的超时时间（秒）
            phrase_time_limit: 单次语音最大时长（秒）
            
        Returns:
            str: 识别到的文本，失败返回None
        """
        if self.recognition_mode == "google":
            return self._listen_google(timeout, phrase_time_limit)
        elif self.recognition_mode == "simulate":
            return self._listen_simulate()
        elif self.recognition_mode == "keyboard":
            return self._listen_keyboard()
        else:
            print(f"❌ 未知识别模式: {self.recognition_mode}")
            return None
    
    def _listen_google(self, timeout: int, phrase_time_limit: int) -> Optional[str]:
        """Google语音识别"""
        if not self.microphone:
            print("❌ 麦克风不可用")
            return None
        
        try:
            with self.microphone as source:
                print(f"\n🎤 请说话（{timeout}秒内开始）...")
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
            
            # 使用Google语音识别
            print("🔍 正在识别语音...")
            text = self.recognizer.recognize_google(
                audio, 
                language=self.language,
                show_all=False
            )
            
            print(f"✅ 识别结果: {text}")
            return text
            
        except sr.WaitTimeoutError:
            print("⏰ 等待超时，未检测到语音")
            return None
        except sr.UnknownValueError:
            print("❓ 无法识别语音内容")
            return None
        except sr.RequestError as e:
            print(f"🌐 语音识别服务错误: {e}")
            print("💡 尝试切换到模拟模式...")
            self.recognition_mode = "simulate"
            self._init_simulate_mode()
            return self._listen_simulate()
        except Exception as e:
            print(f"❌ 监听错误: {e}")
            return None
    
    def _listen_simulate(self) -> Optional[str]:
        """模拟语音输入"""
        if self.simulated_index >= len(self.simulated_inputs):
            self.simulated_index = 0
        
        text = self.simulated_inputs[self.simulated_index]
        self.simulated_index += 1
        
        print(f"\n🎤 模拟语音输入: {text}")
        time.sleep(1)  # 模拟识别时间
        
        return text
    
    def _listen_keyboard(self) -> Optional[str]:
        """键盘输入"""
        try:
            print("\n⌨️  请输入文本:")
            text = input("> ").strip()
            if text:
                return text
            return None
        except (EOFError, KeyboardInterrupt):
            return None
    
    def openclaw_tts(self, text: str, voice_preference: Optional[str] = None) -> bool:
        """
        使用OpenClaw TTS生成语音
        
        Args:
            text: 要朗读的文本
            voice_preference: 语音偏好设置
            
        Returns:
            bool: 是否成功
        """
        try:
            print(f"\n🗣️  语音输出: {text}")
            print("💡 实际环境中会调用OpenClaw TTS工具播放语音")
            
            # 模拟TTS延迟
            time.sleep(0.5)
            
            return True
            
        except Exception as e:
            print(f"❌ TTS生成失败: {e}")
            return False
    
    def simple_ai_response(self, user_input: str) -> str:
        """
        简单的AI响应生成
        
        Args:
            user_input: 用户输入文本
            
        Returns:
            str: AI响应文本
        """
        # 预设响应
        responses = {
            "你好": "你好！我是天元，你的增强版AI助手。",
            "时间": f"现在是 {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "天气": "今天天气不错，适合外出。模拟模式中无法获取实时天气。",
            "谢谢": "不客气，很高兴能帮到你！",
            "再见": "再见！期待下次对话。",
            "退出": "好的，结束对话。再见！",
            "结束": "好的，结束对话。再见！",
            "停止": "好的，结束对话。再见！",
        }
        
        # 查找匹配的响应
        for keyword, response in responses.items():
            if keyword in user_input:
                return response
        
        # 默认响应
        return f"我听到你说：{user_input}。有什么我可以帮你的吗？"
    
    def conversation_loop(self):
        """主对话循环"""
        print("\n" + "=" * 50)
        print("🎧 语音对话模式已启动")
        print(f"📱 当前模式: {self.recognition_mode}")
        
        if self.recognition_mode == "simulate":
            print("💡 模拟模式：将自动播放预设对话")
        elif self.recognition_mode == "keyboard":
            print("💡 键盘模式：请输入文本进行对话")
        else:
            print("🎤 请开始说话，说'退出'结束对话")
        
        print("=" * 50)
        
        conversation_history = []
        
        while True:
            # 监听用户输入
            user_input = self.listen()
            
            if not user_input:
                print("🔄 重新尝试...")
                time.sleep(1)
                continue
            
            # 添加到历史记录
            conversation_history.append(f"用户: {user_input}")
            
            # 检查退出命令
            exit_keywords = ["退出", "结束", "停止", "quit", "exit", "stop"]
            if any(keyword in user_input for keyword in exit_keywords):
                print("👋 结束对话")
                self.openclaw_tts("好的，结束对话。再见！")
                break
            
            # 生成AI响应
            print("🤖 生成响应...")
            ai_response = self.simple_ai_response(user_input)
            conversation_history.append(f"AI: {ai_response}")
            
            # 语音输出
            success = self.openclaw_tts(ai_response)
            
            if success:
                print(f"💬 AI: {ai_response}")
            else:
                print(f"📝 AI（文本）: {ai_response}")
            
            # 短暂暂停
            time.sleep(1)
        
        # 显示对话历史
        print("\n" + "=" * 50)
        print("📝 对话历史记录:")
        for entry in conversation_history:
            print(f"  {entry}")
        print("=" * 50)

def test_recognition_modes():
    """测试所有识别模式"""
    print("🧪 测试语音识别模式...")
    
    modes_to_test = ["auto", "simulate", "keyboard"]
    
    for mode in modes_to_test:
        print(f"\n🔧 测试模式: {mode}")
        print("-" * 30)
        
        try:
            chat = EnhancedVoiceChat(recognition_mode=mode)
            
            # 测试监听
            print("测试监听功能...")
            result = chat.listen(timeout=2)
            
            if result:
                print(f"✅ 监听成功: {result}")
            else:
                print("⚠️  监听返回空")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")

def main():
    """主函数"""
    print("🚀 增强版语音对话系统 v1.1")
    print("=" * 50)
    
    # 解析命令行参数
    mode = "auto"
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    
    # 显示可用模式
    if mode == "--help":
        print("用法:")
        print("  python voice_chat_enhanced.py [模式]")
        print("")
        print("模式选项:")
        print("  auto    自动选择最佳模式（默认）")
        print("  google  Google在线识别（需网络）")
        print("  simulate 模拟语音输入（离线测试）")
        print("  keyboard 键盘输入模式")
        print("  test    测试所有模式")
        print("")
        print("示例:")
        print("  python voice_chat_enhanced.py simulate")
        print("  python voice_chat_enhanced.py keyboard")
        return
    
    if mode == "test":
        test_recognition_modes()
        return
    
    # 创建增强版语音对话实例
    print(f"🔧 使用模式: {mode}")
    voice_chat = EnhancedVoiceChat(recognition_mode=mode)
    
    # 检查依赖
    if mode == "google" and (not SPEECH_RECOGNITION_AVAILABLE or not PYAUDIO_AVAILABLE):
        print("❌ 依赖不满足，无法使用Google模式")
        print("💡 建议使用模拟模式:")
        print("  python voice_chat_enhanced.py simulate")
        return
    
    # 显示菜单
    print("\n" + "=" * 50)
    print("📱 增强版语音对话菜单")
    print("=" * 50)
    print("1. 🎧 开始语音对话")
    print("2. 🔧 测试当前模式")
    print("3. 📋 显示系统信息")
    print("4. ❌ 退出")
    print("=" * 50)
    
    try:
        choice = input("请选择 (1-4): ").strip()
        
        if choice == "1":
            voice_chat.conversation_loop()
        elif choice == "2":
            print("🧪 测试当前模式...")
            for i in range(3):
                result = voice_chat.listen()
                if result:
                    print(f"测试 {i+1}: ✅ {result}")
                else:
                    print(f"测试 {i+1}: ❌ 失败")
        elif choice == "3":
            print("📊 系统信息:")
            print(f"  识别模式: {voice_chat.recognition_mode}")
            print(f"  语言设置: {voice_chat.language}")
            print(f"  speech_recognition: {'✅ 已安装' if SPEECH_RECOGNITION_AVAILABLE else '❌ 未安装'}")
            print(f"  pyaudio: {'✅ 已安装' if PYAUDIO_AVAILABLE else '❌ 未安装'}")
        elif choice == "4":
            print("👋 再见！")
        else:
            print("❌ 无效选择")
            
    except KeyboardInterrupt:
        print("\n👋 用户中断，退出程序")
    except Exception as e:
        print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    main()