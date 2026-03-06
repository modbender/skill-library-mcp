#!/usr/bin/env python3
"""
TTS Converter - 使用 edge-tts 将文本转换为语音

用法:
  python3 tts_converter.py "文本内容" --voice zh-CN-XiaoxiaoNeural --rate +10% -o output.mp3
  python3 tts_converter.py -f input.txt --voice en-US-AriaNeural -o output.mp3
  python3 tts_converter.py --list-voices
  python3 tts_converter.py --list-voices --lang zh
"""

import argparse
import asyncio
import os
import tempfile
import time
import random
import string

import edge_tts

# 默认语音映射
DEFAULT_VOICES = {
    "en": "en-US-MichelleNeural",
    "es": "es-ES-ElviraNeural",
    "fr": "fr-FR-DeniseNeural",
    "de": "de-DE-KatjaNeural",
    "it": "it-IT-ElsaNeural",
    "ja": "ja-JP-NanamiNeural",
    "zh": "zh-CN-XiaoxiaoNeural",
    "ar": "ar-SA-ZariyahNeural",
}

TEMP_DIR = os.path.join(tempfile.gettempdir(), "edge-tts-temp")
MAX_TEXT_LENGTH = 10000

# TTS 触发关键词，转换前自动过滤
TTS_KEYWORDS = {"tts", "text-to-speech", "text to speech"}


def generate_temp_path(ext=".mp3"):
    """生成唯一临时文件路径"""
    os.makedirs(TEMP_DIR, exist_ok=True)
    ts = int(time.time() * 1000)
    rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return os.path.join(TEMP_DIR, f"tts_{ts}_{rand}{ext}")


def filter_tts_keywords(text):
    """过滤文本中的 TTS 触发关键词"""
    import re  # noqa: C0415
    words = text.split()
    filtered = [w for w in words if re.sub(r"[^\w\s-]", "", w.lower()) not in TTS_KEYWORDS]
    result = " ".join(filtered)
    if result != text.strip():
        print(f"  Filtered TTS keywords: \"{text}\" -> \"{result}\"")
    return result


async def text_to_speech(text, voice=None, lang="en-US", rate="+0%", volume="+0%",
                         pitch="+0Hz", output_path=None, subtitle_path=None,
                         proxy=None, timeout=60):
    """
    将文本转换为语音

    Args:
        text: 待转换文本
        voice: 语音名称，如 zh-CN-XiaoxiaoNeural
        lang: 语言代码，用于选择默认语音
        rate: 语速，如 +10%、-20%
        volume: 音量，如 +0%、-50%
        pitch: 音高，如 +0Hz、-10Hz
        output_path: 输出文件路径，None 则使用临时文件
        subtitle_path: 字幕文件路径（.vtt/.srt），None 则不生成
        proxy: 代理 URL
        timeout: 接收超时（秒）

    Returns:
        生成的音频文件路径
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    if len(text) > MAX_TEXT_LENGTH:
        print(f"  Warning: Text is very long ({len(text)} characters), may cause issues")

    # 确定语音
    if not voice:
        lang_prefix = lang.split("-")[0] if lang else "en"
        voice = DEFAULT_VOICES.get(lang_prefix, DEFAULT_VOICES["en"])

    # 过滤关键词
    text = filter_tts_keywords(text)

    # 确定输出路径
    final_path = output_path or generate_temp_path(".mp3")
    os.makedirs(os.path.dirname(os.path.abspath(final_path)), exist_ok=True)

    print("Converting text to speech...")
    print(f"  Text: {text[:50]}{'...' if len(text) > 50 else ''}")
    print(f"  Voice: {voice}")
    print(f"  Rate: {rate}  Pitch: {pitch}  Volume: {volume}")

    communicate = edge_tts.Communicate(
        text,
        voice,
        rate=rate,
        volume=volume,
        pitch=pitch,
        proxy=proxy,
        receive_timeout=timeout,
    )

    await communicate.save(final_path, subtitle_path)

    size = os.path.getsize(final_path)
    print(f"\nAudio saved to: {final_path}")
    print(f"File size: {size} bytes")

    if subtitle_path and os.path.exists(subtitle_path):
        print(f"Subtitles saved to: {subtitle_path}")

    return final_path


async def list_voices(lang_filter=None, proxy=None):
    """列出可用语音"""
    voices = await edge_tts.list_voices(proxy=proxy)

    if lang_filter:
        voices = [v for v in voices if v["Locale"].lower().startswith(lang_filter.lower())]

    if not voices:
        print(f"No voices found for language: {lang_filter}")
        return

    current_lang = None
    for v in sorted(voices, key=lambda x: x["Locale"]):
        locale = v["Locale"]
        if locale != current_lang:
            current_lang = locale
            print(f"\n{locale}:")
        gender = v.get("Gender", "Unknown")
        print(f"  {v['ShortName']:40s} ({gender})")


def main():
    parser = argparse.ArgumentParser(description="Text-to-speech using Microsoft Edge TTS")
    parser.add_argument("text", nargs="?", help="Text to convert to speech")
    parser.add_argument("-f", "--file", help="Read text from file instead")
    parser.add_argument("-v", "--voice", help="Voice name (e.g., zh-CN-XiaoxiaoNeural)")
    parser.add_argument("-l", "--lang", default="en-US", help="Language code (default: en-US)")
    parser.add_argument("-r", "--rate", default="+0%", help="Rate adjustment (e.g., +10%%, -20%%)")
    parser.add_argument("--volume", default="+0%", help="Volume adjustment (e.g., +0%%, -50%%)")
    parser.add_argument("--pitch", default="+0Hz", help="Pitch adjustment (e.g., +0Hz, -10Hz)")
    parser.add_argument("-o", "--output", help="Output file path (default: temp file)")
    parser.add_argument("-s", "--subtitles", help="Save subtitles to file (.vtt or .srt)")
    parser.add_argument("-p", "--proxy", help="Proxy URL")
    parser.add_argument("--timeout", type=int, default=60, help="Receive timeout in seconds (default: 60)")
    parser.add_argument("-L", "--list-voices", action="store_true", help="List available voices")
    parser.add_argument("--lang-filter", help="Filter voices by language (used with --list-voices)")

    args = parser.parse_args()

    if args.list_voices:
        asyncio.run(list_voices(args.lang_filter, args.proxy))
        return

    # 从文件或参数获取文本
    text = None
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        parser.error("No text provided. Use positional argument or --file")

    asyncio.run(text_to_speech(
        text,
        voice=args.voice,
        lang=args.lang,
        rate=args.rate,
        volume=args.volume,
        pitch=args.pitch,
        output_path=args.output,
        subtitle_path=args.subtitles,
        proxy=args.proxy,
        timeout=args.timeout,
    ))


if __name__ == "__main__":
    main()
