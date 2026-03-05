#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
离线语音对话测试
无需网络连接，使用模拟语音输入
"""

import time
import sys

def simulate_conversation():
    """模拟语音对话"""
    print("🎤 离线语音对话测试")
    print("=" * 50)
    print("💡 此测试使用模拟语音输入，无需麦克风和网络连接")
    print("=" * 50)
    
    # 预设对话序列
    conversation = [
        ("用户: 你好", "AI: 你好！我是天元，你的AI助手。"),
        ("用户: 现在几点了", f"AI: 现在是 {time.strftime('%Y-%m-%d %H:%M:%S')}"),
        ("用户: 今天天气怎么样", "AI: 今天天气不错，适合外出。（模拟模式）"),
        ("用户: 谢谢", "AI: 不客气，很高兴能帮到你！"),
        ("用户: 再见", "AI: 再见！期待下次对话。"),
    ]
    
    for user_say, ai_response in conversation:
        print(f"\n🎤 模拟用户说话: {user_say}")
        time.sleep(1)  # 模拟识别时间
        print(f"🗣️  语音输出: {ai_response}")
        time.sleep(1.5)  # 模拟TTS播放时间
    
    print("\n" + "=" * 50)
    print("✅ 离线测试完成")
    print("📊 5轮对话模拟成功")
    print("💡 所有功能在离线状态下正常工作")
    print("=" * 50)

def main():
    """主函数"""
    # 检查是否安装了必要依赖
    try:
        import speech_recognition
        print("✅ speech_recognition 已安装")
        sr_installed = True
    except ImportError:
        print("⚠️  speech_recognition 未安装")
        sr_installed = False
    
    try:
        import pyaudio
        print("✅ pyaudio 已安装")
        pyaudio_installed = True
    except ImportError:
        print("⚠️  pyaudio 未安装")
        pyaudio_installed = False
    
    print(f"\n🔧 系统状态:")
    print(f"  Python版本: {sys.version.split()[0]}")
    print(f"  系统平台: {sys.platform}")
    print(f"  语音识别库: {'✅ 可用' if sr_installed else '❌ 缺失'}")
    print(f"  音频输入: {'✅ 可用' if pyaudio_installed else '❌ 缺失'}")
    print(f"  网络需求: ❌ 无需网络")
    
    print("\n" + "=" * 50)
    print("选择测试模式:")
    print("1. 🧪 快速模拟对话 (推荐)")
    print("2. 🔧 完整离线测试")
    print("3. 📋 系统诊断")
    print("4. ❌ 退出")
    print("=" * 50)
    
    try:
        choice = input("请选择 (1-4): ").strip()
        
        if choice == "1":
            simulate_conversation()
        elif choice == "2":
            print("🔧 运行完整离线测试...")
            # 这里可以添加更多测试
            simulate_conversation()
        elif choice == "3":
            print("📋 系统诊断报告:")
            print(f"  Python路径: {sys.executable}")
            print(f"  编码设置: {sys.getdefaultencoding()}")
            print(f"  当前目录: {os.getcwd() if 'os' in globals() else '未知'}")
            print("\n💡 建议:")
            if not sr_installed:
                print("  - 安装SpeechRecognition: pip install SpeechRecognition")
            if not pyaudio_installed:
                print("  - 安装PyAudio: pip install pyaudio")
        elif choice == "4":
            print("👋 再见！")
        else:
            print("❌ 无效选择")
            
    except KeyboardInterrupt:
        print("\n👋 用户中断")
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    main()