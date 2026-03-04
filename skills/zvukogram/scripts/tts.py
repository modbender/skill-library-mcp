#!/usr/bin/env python3
"""
Zvukogram TTS Script
Генерация речи через API Zvukogram
"""

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

API_BASE = "https://zvukogram.com/index.php?r=api"


def load_config():
    """Загрузка конфигурации"""
    config_path = Path.home() / ".config/zvukogram/config.json"
    
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    
    # Environment variables
    token = os.environ.get("ZVUKOGRAM_TOKEN")
    email = os.environ.get("ZVUKOGRAM_EMAIL")
    
    if token and email:
        return {"token": token, "email": email}
    
    return None


def api_call(endpoint, data):
    """Вызов API"""
    url = f"{API_BASE}/{endpoint}"
    encoded_data = urllib.parse.urlencode(data).encode()
    
    req = urllib.request.Request(url, data=encoded_data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None


def generate_tts(text, voice, token, email, speed=1.0, format="mp3"):
    """Генерация TTS"""
    data = {
        "token": token,
        "email": email,
        "voice": voice,
        "text": text,
        "format": format,
        "speed": speed,
    }
    
    result = api_call("text", data)
    
    if result and result.get("status") == 1:
        return result.get("file")
    
    print(f"TTS Error: {result.get('error', 'Unknown')}", file=sys.stderr)
    return None


def download_audio(url, output_path):
    """Скачивание аудио"""
    try:
        urllib.request.urlretrieve(url, output_path)
        return True
    except Exception as e:
        print(f"Download error: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Zvukogram TTS")
    parser.add_argument("--text", "-t", help="Текст для озвучки")
    parser.add_argument("--file", "-f", help="Файл с текстом")
    parser.add_argument("--voice", "-v", default="Алена", help="Голос")
    parser.add_argument("--speed", "-s", type=float, default=1.0, help="Скорость (0.1-2.0)")
    parser.add_argument("--output", "-o", required=True, help="Выходной файл")
    parser.add_argument("--format", default="mp3", help="Формат (mp3, wav, ogg)")
    
    args = parser.parse_args()
    
    # Загрузка конфигурации
    config = load_config()
    if not config:
        print("Error: Не найдена конфигурация. Создайте ~/.zvukogram.json", file=sys.stderr)
        sys.exit(1)
    
    # Получение текста
    if args.text:
        text = args.text
    elif args.file:
        with open(args.file) as f:
            text = f.read()
    else:
        print("Error: Укажите --text или --file", file=sys.stderr)
        sys.exit(1)
    
    # Генерация
    print(f"Генерация: {args.voice}, скорость {args.speed}x...")
    audio_url = generate_tts(text, args.voice, config["token"], config["email"], args.speed, args.format)
    
    if audio_url:
        print(f"Скачивание: {audio_url}")
        if download_audio(audio_url, args.output):
            print(f"Сохранено: {args.output}")
        else:
            sys.exit(1)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
