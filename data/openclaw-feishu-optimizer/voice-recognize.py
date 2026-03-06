#!/usr/bin/env python3
"""
OpenClaw 飞书体验优化者 - 语音识别模块
Voice Recognition Module for OpenClaw Feishu Optimizer

作者: 黄绍帅（黄白）
版本: 1.0.0
"""

import argparse
import speech_recognition as sr
from pydub import AudioSegment
from pathlib import Path
import os
import tempfile


def convert_to_wav(audio_path):
    """
    转换音频文件为 WAV 格式（Google Speech Recognition 支持的格式）
    """
    audio_path = Path(audio_path)
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "temp.wav")
    
    try:
        if audio_path.suffix.lower() == ".wav":
            return str(audio_path)
        
        print(f"正在转换音频格式: {audio_path.suffix} → WAV")
        
        if audio_path.suffix.lower() == ".mp3":
            audio = AudioSegment.from_mp3(str(audio_path))
        elif audio_path.suffix.lower() == ".flac":
            audio = AudioSegment.from_flac(str(audio_path))
        elif audio_path.suffix.lower() == ".ogg":
            audio = AudioSegment.from_ogg(str(audio_path))
        elif audio_path.suffix.lower() == ".m4a":
            audio = AudioSegment.from_file(str(audio_path), format="m4a")
        elif audio_path.suffix.lower() == ".wma":
            audio = AudioSegment.from_file(str(audio_path), format="wma")
        else:
            raise ValueError(f"不支持的音频格式: {audio_path.suffix}")
        
        audio.export(output_path, format="wav")
        return output_path
        
    except Exception as e:
        print(f"音频格式转换失败: {e}")
        return None


def recognize_speech(audio_path, language="zh-CN"):
    """
    使用 Google Speech Recognition 识别语音
    """
    r = sr.Recognizer()
    
    try:
        # 转换音频格式（如果需要）
        wav_path = convert_to_wav(audio_path)
        if not wav_path:
            return None
        
        print(f"正在识别语音（语言: {language}）...")
        
        with sr.AudioFile(wav_path) as source:
            audio = r.record(source)
            
            text = r.recognize_google(audio, language=language)
            
            print(f"识别成功: {text}")
            return text
            
    except sr.UnknownValueError:
        print("错误: 无法识别音频内容")
        return None
    except sr.RequestError as e:
        print(f"错误: 请求 Google Speech Recognition 服务失败 - {e}")
        return None
    except Exception as e:
        print(f"错误: {e}")
        return None
    finally:
        # 清理临时文件
        if 'wav_path' in locals() and wav_path != str(audio_path):
            try:
                os.remove(wav_path)
                os.rmdir(os.path.dirname(wav_path))
            except:
                pass


def main():
    parser = argparse.ArgumentParser(
        description="OpenClaw 飞书体验优化者 - 语音识别模块",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 voice-recognize.py audio.mp3
  python3 voice-recognize.py audio.ogg --language zh-CN
  python3 voice-recognize.py audio.wav --language en-US

支持的语言:
  zh-CN: 中文（普通话）
  en-US: 英文（美国）
  zh-TW: 中文（繁体）
  ja-JP: 日语
  ko-KR: 韩语
  fr-FR: 法语
  de-DE: 德语
  es-ES: 西班牙语
  ru-RU: 俄语
  pt-BR: 葡萄牙语（巴西）
        """)
    
    parser.add_argument("audio_file", help="音频文件路径（支持 MP3、WAV、FLAC、OGG 等格式）")
    parser.add_argument(
        "--language", 
        "-l", 
        default="zh-CN",
        help="识别语言（默认: zh-CN, 支持多种语言代码）"
    )
    parser.add_argument(
        "--output", 
        "-o",
        help="将识别结果保存到指定文件"
    )
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.audio_file):
        print(f"错误: 文件 '{args.audio_file}' 不存在")
        return
    
    # 识别语音
    result = recognize_speech(args.audio_file, args.language)
    
    if result:
        # 如果指定了输出文件，保存结果
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"识别结果已保存到: {args.output}")
        
        print(f"\n识别结果: {result}")
    else:
        print("\n语音识别失败")
        return 1


if __name__ == "__main__":
    main()
