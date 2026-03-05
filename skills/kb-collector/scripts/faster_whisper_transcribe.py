#!/usr/bin/env python3
import sys
from faster_whisper import WhisperModel

def transcribe(audio_path, language="zh", model_size="tiny"):
    model = WhisperModel(model_size, device="auto", compute_type="int8")
    segments, info = model.transcribe(audio_path, language=language)
    
    text = ""
    for segment in segments:
        text += segment.text + " "
    
    print(text.strip())

if __name__ == "__main__":
    audio_path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/youtube_audio.m4a"
    transcribe(audio_path)
