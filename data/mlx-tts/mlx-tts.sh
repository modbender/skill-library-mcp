#!/bin/bash

text=${1:-"Hello, Human!"}
model=mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16
outdir="$(mktemp -d)"
mlx_audio.tts.generate \
  --instruct="Be nice" \
  --output_path="${outdir}" \
  --file_prefix="audio" \
  --audio_format="wav" \
  --model=${model} \
  --text="${text}" >/dev/null 2>&1

ffmpeg -y -loglevel error -i "${outdir}/audio_000.wav" -vn -acodec libopus -b:a 32k "${outdir}/audio.ogg"
echo "${outdir}/audio.ogg"
