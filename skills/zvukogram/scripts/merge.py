#!/usr/bin/env python3
"""
Zvukogram Audio Merger
Склейка аудио-фрагментов через ffmpeg
"""

import argparse
import subprocess
import sys
from pathlib import Path


def merge_audio(files, output):
    """Склейка аудио через ffmpeg"""
    if not files:
        print("Error: Нет файлов для склейки", file=sys.stderr)
        return False
    
    # Создаём файл списка для ffmpeg
    list_file = Path(output).parent / "merge_list.txt"
    with open(list_file, "w") as f:
        for file in files:
            f.write(f"file '{file}'\n")
    
    # Запуск ffmpeg
    cmd = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file),
        "-acodec", "copy",
        output
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        list_file.unlink()  # Удаляем временный файл
        
        if result.returncode == 0:
            print(f"Склеено: {output}")
            return True
        else:
            print(f"FFmpeg error: {result.stderr}", file=sys.stderr)
            return False
    except FileNotFoundError:
        print("Error: ffmpeg не найден. Установите: apt install ffmpeg", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Склейка аудио")
    parser.add_argument("files", nargs="+", help="Файлы для склейки")
    parser.add_argument("--output", "-o", required=True, help="Выходной файл")
    
    args = parser.parse_args()
    
    if not merge_audio(args.files, args.output):
        sys.exit(1)


if __name__ == "__main__":
    main()
