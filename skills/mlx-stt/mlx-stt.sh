#!/bin/bash

set -ueo pipefail

audio=${1:-"~/Music/audio.mp3"}
model=mlx-community/GLM-ASR-Nano-2512-8bit

tmpdir="$(mktemp -d)"
audio_wav="${tmpdir}/audio.wav"
ffmpeg -y -loglevel error -i "${audio}" -ar 16000 -ac 1 -c:a pcm_s16le "${audio_wav}"

mlx_audio.stt.generate \
  --model "${model}" \
  --audio "${audio_wav}" \
  --output-path "${tmpdir}/out" > /dev/null 2>&1

find "${tmpdir}" -type f -name "*.txt" -exec cat {} \;
rm -rf "${tmpdir}"
