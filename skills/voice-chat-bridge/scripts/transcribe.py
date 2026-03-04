#!/usr/bin/env python3
"""
语音转文字工具 - 使用 macOS 原生语音识别
需要先授权：系统设置 > 隐私与安全 > 语音识别
"""

import subprocess
import sys
import os

def transcribe_audio(audio_path):
    """使用 hear 命令转写语音"""
    
    # 先转换为 16kHz 单声道 WAV
    wav_path = "/tmp/hear_temp.wav"
    
    # ffmpeg 转换
    ffmpeg_cmd = [
        "ffmpeg", "-i", audio_path,
        "-ar", "16000", "-ac", "1",
        "-c:a", "pcm_s16le",
        wav_path, "-y"
    ]
    
    try:
        subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"音频转换失败: {e}")
        return None
    
    # 使用 hear 识别
    hear_path = os.path.expanduser("~/.local/bin/hear")
    hear_cmd = [hear_path, "-i", wav_path, "-l", "zh-CN", "-p"]
    
    try:
        result = subprocess.run(hear_cmd, capture_output=True, text=True, timeout=30)
        
        # 清理临时文件
        os.remove(wav_path)
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            error = result.stderr.strip()
            if "No speech detected" in error:
                return "[未检测到语音，请检查音频文件]"
            elif "denied" in error.lower() or "not authorized" in error.lower():
                return "[需要在系统设置中授权语音识别权限]"
            else:
                return f"[识别失败: {error}]"
                
    except subprocess.TimeoutExpired:
        os.remove(wav_path)
        return "[识别超时]"
    except Exception as e:
        if os.path.exists(wav_path):
            os.remove(wav_path)
        return f"[错误: {e}]"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python3 transcribe.py <音频文件>")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    if not os.path.exists(audio_file):
        print(f"文件不存在: {audio_file}")
        sys.exit(1)
    
    result = transcribe_audio(audio_file)
    if result:
        print(result)
