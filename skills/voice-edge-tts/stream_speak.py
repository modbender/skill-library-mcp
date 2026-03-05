# -*- coding: utf-8 -*-
"""
流式语音播放脚本
edge-tts 边生成边播放，需要 ffmpeg 在 PATH 中
"""
import asyncio
import edge_tts
import subprocess
import sys
import os

# ffmpeg 路径（根据实际情况修改）
FFMPEG_PATH = r"E:\tools\ffmpeg\bin\ffplay"

async def stream_speak(text, voice="zh-CN-XiaoxiaoNeural", rate="+0%", volume="+0%", pitch="+0Hz"):
    """流式播放语音 - 边生成边播放"""
    if not text:
        print("Error: Text is required")
        return False
    
    print(f"流式播放: {text}")
    
    # 创建 edge-tts 通信对象
    communicate = edge_tts.Communicate(text, voice, rate=rate, volume=volume, pitch=pitch)
    
    try:
        # 启动 ffplay 进程
        ffplay_process = subprocess.Popen(
            [FFMPEG_PATH, "-nodisp", "-autoexit", "-i", "pipe:0", "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # 流式写入音频数据
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                ffplay_process.stdin.write(chunk["data"])
        
        # 关闭输入流并等待播放完成
        ffplay_process.stdin.close()
        ffplay_process.wait()
        
        print("播放完成")
        return True
        
    except Exception as e:
        print(f"播放失败: {e}")
        return False

def main():
    # 从命令行参数获取文本
    # 参数格式: script.py "文本" --voice xxx
    args = sys.argv[1:]
    
    if not args:
        text = "你好，我是小九"
        voice = "zh-CN-XiaoxiaoNeural"
    else:
        # 找到第一个不是 -- 开头的参数作为文本
        text = None
        voice = "zh-CN-XiaoxiaoNeural"
        
        i = 0
        while i < len(args):
            if not args[i].startswith('--'):
                text = args[i]
            elif args[i] == '--voice' and i + 1 < len(args):
                voice = args[i + 1]
                i += 1
            i += 1
        
        if not text:
            text = "你好，我是小九"
    
    asyncio.run(stream_speak(text, voice))

if __name__ == "__main__":
    main()
