---
name: audio-mastering-cli
description: CLI audio mastering without a reference track using ffmpeg; accepts audio or video inputs and outputs mastered WAV/MP3 or remuxed MP4.
metadata: {"openclaw":{"emoji":"🎚️","homepage":"https://github.com/alesys/openclaw-skill-audio-mastering-cli","os":["win32"],"requires":{"bins":["ffmpeg","powershell"]}}}
---

# Audio Mastering CLI

Usa este skill cuando el usuario quiera masterizar audio sin referencia, por CLI, sobre archivo de audio o video.

## Entradas soportadas
- Audio: `wav`, `aiff`, `flac`, `mp3`, `m4a`
- Video: `mp4`, `mov`, `m4v`, `mkv`, `webm`

## Flujo
1. Verifica que existe el archivo de entrada.
2. Ejecuta:
   `powershell -ExecutionPolicy Bypass -File "{baseDir}/scripts/master_media.ps1" -InputFile "<ruta-archivo>" -MakeMp3`
3. Entrega salidas:
   - WAV master: `<base>_master.wav`
   - MP3 master: `<base>_master.mp3` (si `-MakeMp3`)
   - Si la entrada es video: `<base>_master.mp4` con video original + audio masterizado AAC 320k
4. Reporta loudness/true peak del log.

## Cadena aplicada
- `highpass` + `lowpass`
- EQ suave de correccion/mejora
- `acompressor`
- `alimiter`
- `loudnorm` dos pasadas (objetivo conservador multiplaforma)

## Verificacion opcional
`ffmpeg -hide_banner -i "<archivo_master.wav>" -af "loudnorm=I=-14:TP=-1:LRA=7:print_format=summary" -f null NUL`

## Notas
- Para video: se conserva el stream de video (`-c:v copy`) y solo se reemplaza audio.
- Si hay avisos de clipping interno en EQ, bajar input o ganancias de EQ y reexportar.
