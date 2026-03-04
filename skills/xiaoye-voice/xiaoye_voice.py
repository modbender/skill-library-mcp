#!/usr/bin/env python3
"""
小野语音系统 - 智能双引擎TTS
中文: macOS原生Tingting (完全本地)
其他语种: Edge-TTS (高质量云端)
"""

import subprocess
import os
import asyncio
from pathlib import Path
import time
import sys

class XiaoyeVoiceSystem:
    """小野语音系统 - 智能双引擎TTS"""
    
    def __init__(self, 
                 chinese_voice="Tingting",
                 english_voice="en-US-JennyNeural",
                 japanese_voice="ja-JP-NanamiNeural",
                 output_format="ogg",
                 sample_rate=48000,
                 bitrate="64k",
                 debug=False):
        
        self.chinese_voice = chinese_voice
        self.english_voice = english_voice
        self.japanese_voice = japanese_voice
        self.output_format = output_format
        self.sample_rate = sample_rate
        self.bitrate = bitrate
        self.debug = debug
        
        # 设置输出目录
        self.base_dir = Path.home() / ".openclaw" / "outputs" / "xiaoye_voice"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        if debug:
            print("=" * 60)
            print("🎭 小野语音系统 - 智能双引擎TTS")
            print(f"🎯 策略: 中文macOS本地 + 其他Edge-TTS云端")
            print(f"💾 输出目录: {self.base_dir}")
            print("=" * 60)
    
    def is_chinese(self, text):
        """检测是否为中文文本"""
        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                return True
        return False
    
    def detect_language(self, text):
        """检测文本语言"""
        text_lower = text.lower()
        
        # 中文检测
        if self.is_chinese(text):
            return "zh"
        
        # 日语关键词检测
        jp_keywords = ["こんにちは", "ありがとう", "すみません", "おはよう", "こんばんは"]
        for keyword in jp_keywords:
            if keyword in text:
                return "ja"
        
        # 法语关键词检测
        fr_keywords = ["bonjour", "merci", "au revoir", "s'il vous plaît", "excusez-moi"]
        for keyword in fr_keywords:
            if keyword in text_lower:
                return "fr"
        
        # 默认英语
        return "en"
    
    def generate_chinese_local(self, text, output_path):
        """生成中文语音 - macOS本地"""
        if self.debug:
            print(f"🎤 引擎: macOS原生{self.chinese_voice} (完全本地)")
        
        # 临时aiff文件
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.aiff', delete=False) as tmp:
            aiff_file = tmp.name
        
        try:
            # 使用macOS say命令生成aiff
            cmd = [
                "say", "-v", self.chinese_voice,
                "-r", "180",  # 语速
                "-o", aiff_file,
                text
            ]
            
            if self.debug:
                print(f"📝 命令: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ macOS say失败: {result.stderr}")
                return None
            
            # 转换为目标格式
            conv_cmd = [
                "ffmpeg", "-i", aiff_file,
                "-c:a", "libopus", "-b:a", self.bitrate,
                "-ar", str(self.sample_rate), "-ac", "1",
                str(output_path), "-y", "-loglevel", "error"
            ]
            
            result = subprocess.run(conv_cmd, capture_output=True, text=True)
            
            # 清理临时文件
            os.remove(aiff_file)
            
            if result.returncode != 0:
                print(f"❌ 音频转换失败: {result.stderr}")
                return None
            
            file_size = output_path.stat().st_size / 1024
            if self.debug:
                print(f"✅ 生成完成: {output_path.name}")
                print(f"📊 文件大小: {file_size:.1f} KB")
            
            return str(output_path)
            
        except Exception as e:
            print(f"❌ 中文语音生成异常: {e}")
            # 清理临时文件
            if os.path.exists(aiff_file):
                os.remove(aiff_file)
            return None
    
    async def generate_edge_tts(self, text, output_path):
        """生成Edge-TTS语音"""
        try:
            import edge_tts
            
            # 根据语言选择语音
            lang = self.detect_language(text)
            if lang == "zh":
                voice = "zh-CN-XiaoxiaoNeural"
                if self.debug:
                    print("🌐 语音: 中文 (Xiaoxiao)")
            elif lang == "ja":
                voice = self.japanese_voice
                if self.debug:
                    print("🌐 语音: 日文")
            elif lang == "fr":
                voice = "fr-FR-DeniseNeural"
                if self.debug:
                    print("🌐 语音: 法文")
            else:
                voice = self.english_voice
                if self.debug:
                    print("🌐 语音: 英文")
            
            if self.debug:
                print(f"🎤 引擎: Edge-TTS (高质量云端)")
            
            # 使用edge_tts模块
            communicate = edge_tts.Communicate(text, voice)
            
            # 保存为mp3
            await communicate.save(str(output_path))
            
            # 转换为OGG (如果需要)
            if self.output_format == "ogg":
                ogg_path = output_path.with_suffix('.ogg')
                conv_cmd = [
                    "ffmpeg", "-i", str(output_path),
                    "-c:a", "libopus", "-b:a", self.bitrate,
                    "-ar", str(self.sample_rate), "-ac", "1",
                    str(ogg_path), "-y", "-loglevel", "error"
                ]
                
                result = subprocess.run(conv_cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    # 删除mp3，保留ogg
                    os.remove(output_path)
                    output_path = ogg_path
                    if self.debug:
                        print(f"🔄 转换为OGG格式")
            
            file_size = output_path.stat().st_size / 1024
            if self.debug:
                print(f"✅ 生成完成: {output_path.name}")
                print(f"📊 文件大小: {file_size:.1f} KB")
            
            return str(output_path)
            
        except ImportError:
            print("❌ Edge-TTS模块未安装，请运行: pip install edge-tts")
            return None
        except Exception as e:
            print(f"❌ Edge-TTS失败: {e}")
            return None
    
    def generate(self, text):
        """生成语音 - 主接口"""
        if self.debug:
            print(f"\n🎵 文本: {text[:50]}..." if len(text) > 50 else f"\n🎵 文本: {text}")
        
        # 生成文件名
        timestamp = int(time.time())
        safe_text = ''.join(c for c in text[:20] if c.isalnum() or c in (' ', '_')).strip().replace(' ', '_')
        output_name = f"xiaoye_{timestamp}_{safe_text}.{self.output_format}"
        output_path = self.base_dir / output_name
        
        # 检测语言并选择引擎
        lang = self.detect_language(text)
        
        if lang == "zh":
            if self.debug:
                print("🌐 检测: 中文 → 使用macOS本地")
            return self.generate_chinese_local(text, output_path)
        else:
            if self.debug:
                print("🌐 检测: 其他语种 → 使用Edge-TTS云端")
            # 同步运行异步函数
            return asyncio.run(self.generate_edge_tts(text, output_path))
    
    def batch_generate(self, texts):
        """批量生成语音"""
        results = []
        for text in texts:
            result = self.generate(text)
            results.append(result)
        return results
    
    def list_available_voices(self):
        """列出可用的macOS语音"""
        try:
            result = subprocess.run(["say", "-v", "?"], capture_output=True, text=True)
            voices = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        voice_name = parts[0]
                        voice_desc = ' '.join(parts[1:])
                        voices.append((voice_name, voice_desc))
            return voices
        except Exception as e:
            print(f"❌ 获取语音列表失败: {e}")
            return []


def main():
    """命令行入口点"""
    import argparse
    
    parser = argparse.ArgumentParser(description="小野语音系统 - 智能双引擎TTS")
    parser.add_argument("text", nargs="?", help="要转换为语音的文本")
    parser.add_argument("--file", help="从文件读取文本")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--voice", "-v", default="Tingting", help="中文语音名称")
    parser.add_argument("--format", "-f", default="ogg", choices=["ogg", "wav", "mp3"], help="输出格式")
    parser.add_argument("--debug", "-d", action="store_true", help="调试模式")
    parser.add_argument("--list-voices", "-l", action="store_true", help="列出可用语音")
    
    args = parser.parse_args()
    
    if args.list_voices:
        xiaoye = XiaoyeVoiceSystem(debug=args.debug)
        voices = xiaoye.list_available_voices()
        print("🎤 可用macOS语音:")
        for voice_name, voice_desc in voices:
            print(f"  {voice_name:20} - {voice_desc}")
        return
    
    if not args.text and not args.file:
        parser.print_help()
        return
    
    # 读取文本
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            text = f.read().strip()
    else:
        text = args.text
    
    # 创建系统实例
    xiaoye = XiaoyeVoiceSystem(
        chinese_voice=args.voice,
        output_format=args.format,
        debug=args.debug
    )
    
    # 生成语音
    audio_file = xiaoye.generate(text)
    
    if audio_file:
        print(f"✅ 语音生成成功: {audio_file}")
        
        # 如果指定了输出路径，复制文件
        if args.output:
            import shutil
            shutil.copy2(audio_file, args.output)
            print(f"📁 已复制到: {args.output}")
    else:
        print("❌ 语音生成失败")
        sys.exit(1)


if __name__ == "__main__":
    main()