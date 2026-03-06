---
name: win-whisper
description: Record audio and transcribe speech to text using Whisper — runs fully local, optional Intel GPU/NPU acceleration.
metadata:
  {
    "openclaw":
      {
        "emoji": "🎙️",
        "os": ["win32"],
        "requires": { "bins": ["whisper-cli"] },
      },
  }
---

# win-whisper

Record audio and transcribe speech to text using OpenAI Whisper models.
Runs completely local — no API keys, no network required after setup.

Uses [whisper.cpp](https://github.com/ggml-org/whisper.cpp) v1.8.3+ for fast inference.
Supports Intel GPU acceleration (12x boost), OpenVINO for NPU, and Voice Activity Detection.

Supported audio formats: WAV, MP3, FLAC, OGG.

## Setup (One-Time)

### 1. Download whisper-cli

```powershell
powershell.exe -NoProfile -Command "
$whisperDir = \"$env:USERPROFILE\.pcclaw\whisper\"
New-Item -ItemType Directory -Force $whisperDir | Out-Null

# Download whisper.cpp pre-built binary (OpenBLAS accelerated, ~16MB)
$zipUrl = 'https://github.com/ggml-org/whisper.cpp/releases/download/v1.8.3/whisper-blas-bin-x64.zip'
$zipPath = \"$env:TEMP\whisper-blas-bin-x64.zip\"
Write-Host 'Downloading whisper-cli...' -ForegroundColor Cyan
Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath
Expand-Archive $zipPath -DestinationPath $whisperDir -Force
Remove-Item $zipPath

# Binary extracts to Release/ subdirectory — add that to PATH
$binDir = \"$whisperDir\Release\"
$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if ($userPath -notlike \"*$binDir*\") {
    [Environment]::SetEnvironmentVariable('Path', \"$userPath;$binDir\", 'User')
    $env:Path += \";$binDir\"
    Write-Host 'Added to PATH.' -ForegroundColor Green
}

Write-Host 'Done. whisper-cli installed.' -ForegroundColor Green
"
```

### 2. Download a Model

```powershell
powershell.exe -NoProfile -Command "
$whisperDir = \"$env:USERPROFILE\.pcclaw\whisper\"
$model = 'base'

$modelUrl = \"https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-$model.bin\"
$modelPath = \"$whisperDir\ggml-$model.bin\"
Write-Host \"Downloading ggml-$model.bin...\" -ForegroundColor Cyan
Invoke-WebRequest -Uri $modelUrl -OutFile $modelPath
Write-Host \"Model saved to $modelPath\" -ForegroundColor Green
"
```

Change `$model` to `tiny`, `small`, `medium`, or `large-v3-turbo`. See [Model Guide](#model-guide).

### 3. Verify

```powershell
powershell.exe -NoProfile -Command "whisper-cli --help 2>&1 | Select-Object -First 3"
```

## Record Audio from Microphone

### Timed Recording (N seconds)

```powershell
powershell.exe -NoProfile -Command "
Add-Type -MemberDefinition '[DllImport(\"winmm.dll\", CharSet=CharSet.Unicode)] public static extern int mciSendStringW(string cmd, System.Text.StringBuilder ret, int retLen, IntPtr cb);' -Name WinMM -Namespace PCClaw

$outPath = \"$env:TEMP\pcclaw-recording.wav\"
$seconds = DURATION

[PCClaw.WinMM]::mciSendStringW('open new Type waveaudio Alias mic', $null, 0, [IntPtr]::Zero) | Out-Null
[PCClaw.WinMM]::mciSendStringW('set mic bitspersample 16 channels 1 samplespersec 22050', $null, 0, [IntPtr]::Zero) | Out-Null
[PCClaw.WinMM]::mciSendStringW('record mic', $null, 0, [IntPtr]::Zero) | Out-Null

Write-Host \"Recording for $seconds seconds...\" -ForegroundColor Yellow
Start-Sleep -Seconds $seconds

[PCClaw.WinMM]::mciSendStringW('stop mic', $null, 0, [IntPtr]::Zero) | Out-Null
[PCClaw.WinMM]::mciSendStringW(\"save mic $outPath\", $null, 0, [IntPtr]::Zero) | Out-Null
[PCClaw.WinMM]::mciSendStringW('close mic', $null, 0, [IntPtr]::Zero) | Out-Null

Write-Host \"Saved to $outPath\" -ForegroundColor Green
"
```

Replace `DURATION` with seconds to record (e.g., `5`, `10`, `30`).

### Interactive Recording (Press Enter to Stop)

```powershell
powershell.exe -NoProfile -Command "
Add-Type -MemberDefinition '[DllImport(\"winmm.dll\", CharSet=CharSet.Unicode)] public static extern int mciSendStringW(string cmd, System.Text.StringBuilder ret, int retLen, IntPtr cb);' -Name WinMM -Namespace PCClaw

$outPath = \"$env:TEMP\pcclaw-recording.wav\"

[PCClaw.WinMM]::mciSendStringW('open new Type waveaudio Alias mic', $null, 0, [IntPtr]::Zero) | Out-Null
[PCClaw.WinMM]::mciSendStringW('set mic bitspersample 16 channels 1 samplespersec 22050', $null, 0, [IntPtr]::Zero) | Out-Null
[PCClaw.WinMM]::mciSendStringW('record mic', $null, 0, [IntPtr]::Zero) | Out-Null

Write-Host 'Recording... Press Enter to stop.' -ForegroundColor Yellow
Read-Host

[PCClaw.WinMM]::mciSendStringW('stop mic', $null, 0, [IntPtr]::Zero) | Out-Null
[PCClaw.WinMM]::mciSendStringW(\"save mic $outPath\", $null, 0, [IntPtr]::Zero) | Out-Null
[PCClaw.WinMM]::mciSendStringW('close mic', $null, 0, [IntPtr]::Zero) | Out-Null

Write-Host \"Saved to $outPath\" -ForegroundColor Green
"
```

## Transcribe Audio File

### Basic Transcription

```powershell
powershell.exe -NoProfile -Command "
$model = \"$env:USERPROFILE\.pcclaw\whisper\ggml-base.bin\"
whisper-cli -m $model -f 'AUDIO_PATH' -nt -np 2>&1
"
```

Replace `AUDIO_PATH` with the path to an audio file (WAV, MP3, FLAC, or OGG).
`-nt` = no timestamps, `-np` = no progress (clean output).

### With Language Specification

```powershell
powershell.exe -NoProfile -Command "
$model = \"$env:USERPROFILE\.pcclaw\whisper\ggml-base.bin\"
whisper-cli -m $model -f 'AUDIO_PATH' -l LANG_CODE -nt -np 2>&1
"
```

Replace `LANG_CODE` with: `en`, `zh`, `ja`, `ko`, `de`, `fr`, `es`, or `auto` (auto-detect).

### With Timestamps

```powershell
powershell.exe -NoProfile -Command "
$model = \"$env:USERPROFILE\.pcclaw\whisper\ggml-base.bin\"
whisper-cli -m $model -f 'AUDIO_PATH' -l auto -np 2>&1
"
```

Output: `[00:00:00.000 --> 00:00:05.000] Transcribed text here`

### Translate to English

Transcribe and translate any language to English:

```powershell
powershell.exe -NoProfile -Command "
$model = \"$env:USERPROFILE\.pcclaw\whisper\ggml-base.bin\"
whisper-cli -m $model -f 'AUDIO_PATH' -l auto -tr -nt -np 2>&1
"
```

### Output as SRT Subtitles

```powershell
powershell.exe -NoProfile -Command "
$model = \"$env:USERPROFILE\.pcclaw\whisper\ggml-base.bin\"
whisper-cli -m $model -f 'AUDIO_PATH' -l auto -osrt -of 'OUTPUT_PATH' -np 2>&1
"
```

Replace `OUTPUT_PATH` with desired path (without extension). Produces `OUTPUT_PATH.srt`.

### With Voice Activity Detection (VAD)

Skip silence and only transcribe speech segments:

```powershell
powershell.exe -NoProfile -Command "
$model = \"$env:USERPROFILE\.pcclaw\whisper\ggml-base.bin\"
$vadModel = \"$env:USERPROFILE\.pcclaw\whisper\silero-vad.onnx\"
whisper-cli -m $model -f 'AUDIO_PATH' -l auto --vad -vm $vadModel -nt -np 2>&1
"
```

Download the VAD model (one-time, ~2MB):
```powershell
powershell.exe -NoProfile -Command "
Invoke-WebRequest -Uri 'https://github.com/ggml-org/whisper.cpp/raw/master/models/silero-vad.onnx' -OutFile \"$env:USERPROFILE\.pcclaw\whisper\silero-vad.onnx\"
"
```

## Record and Transcribe (Combined)

Record from microphone then immediately transcribe:

```powershell
powershell.exe -NoProfile -Command "
Add-Type -MemberDefinition '[DllImport(\"winmm.dll\", CharSet=CharSet.Unicode)] public static extern int mciSendStringW(string cmd, System.Text.StringBuilder ret, int retLen, IntPtr cb);' -Name WinMM -Namespace PCClaw

$wavPath = \"$env:TEMP\pcclaw-recording.wav\"
$model = \"$env:USERPROFILE\.pcclaw\whisper\ggml-base.bin\"
$seconds = DURATION

# Record
[PCClaw.WinMM]::mciSendStringW('open new Type waveaudio Alias mic', $null, 0, [IntPtr]::Zero) | Out-Null
[PCClaw.WinMM]::mciSendStringW('set mic bitspersample 16 channels 1 samplespersec 22050', $null, 0, [IntPtr]::Zero) | Out-Null
[PCClaw.WinMM]::mciSendStringW('record mic', $null, 0, [IntPtr]::Zero) | Out-Null
Write-Host \"Recording for $seconds seconds...\" -ForegroundColor Yellow
Start-Sleep -Seconds $seconds
[PCClaw.WinMM]::mciSendStringW('stop mic', $null, 0, [IntPtr]::Zero) | Out-Null
[PCClaw.WinMM]::mciSendStringW(\"save mic $wavPath\", $null, 0, [IntPtr]::Zero) | Out-Null
[PCClaw.WinMM]::mciSendStringW('close mic', $null, 0, [IntPtr]::Zero) | Out-Null

# Transcribe
Write-Host 'Transcribing...' -ForegroundColor Cyan
whisper-cli -m $model -f $wavPath -l auto -nt -np 2>&1
"
```

Replace `DURATION` with seconds to record.

## Real-Time Streaming Transcription

`whisper-stream.exe` (included in the download) captures from the microphone and transcribes in real-time:

```powershell
powershell.exe -NoProfile -Command "
$model = \"$env:USERPROFILE\.pcclaw\whisper\ggml-base.bin\"
whisper-stream -m $model -l auto --step 500 --length 5000 2>&1
"
```

Press `Ctrl+C` to stop. Requires SDL2.dll (included in the download).

## Model Guide

| Model | Disk | RAM | Speed | Quality | Best For |
|-------|------|-----|-------|---------|----------|
| `tiny` | 75 MB | 390 MB | Fastest | Basic | Quick notes, commands |
| `base` | 148 MB | 500 MB | Fast | Good | **General use (recommended)** |
| `small` | 488 MB | 1.0 GB | Medium | Better | Meetings, interviews |
| `medium` | 1.5 GB | 2.6 GB | Slow | Great | High accuracy needs |
| `large-v3-turbo` | 1.6 GB | 3.0 GB | Slow | Best | Professional transcription |

For English-only, append `.en` (e.g., `base.en`) for better accuracy.

Download any model:
```powershell
powershell.exe -NoProfile -Command "
$model = 'MODEL_NAME'
$dir = \"$env:USERPROFILE\.pcclaw\whisper\"
Invoke-WebRequest -Uri \"https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-$model.bin\" -OutFile \"$dir\ggml-$model.bin\"
Write-Host \"Downloaded ggml-$model.bin\" -ForegroundColor Green
"
```

## GPU / NPU Acceleration

### Intel GPU (Arc / Iris Xe) — via OpenVINO

For Intel GPU/NPU acceleration, use the `--ov-e-device` flag with an OpenVINO-enabled build:

```powershell
# GPU acceleration
whisper-cli -m MODEL -f AUDIO --ov-e-device GPU

# NPU acceleration (Intel AIPC)
whisper-cli -m MODEL -f AUDIO --ov-e-device NPU
```

This requires building whisper.cpp from source with OpenVINO:
```powershell
# Requires: cmake, Visual Studio Build Tools, OpenVINO toolkit
cmake -B build -DWHISPER_OPENVINO=1
cmake --build build --config Release
```

Pre-converted OpenVINO encoder models are available at `huggingface.co/Intel/whisper.cpp-openvino-models`.

### Disable GPU

If you encounter GPU issues, force CPU-only:
```powershell
whisper-cli -m MODEL -f AUDIO --no-gpu
```

## Recommended Workflows

### Voice memo → Text
```
1. win-whisper: record audio
2. win-whisper: transcribe the recording
3. Agent processes/summarizes the text
```

### Voice command → Action
```
1. win-whisper: record 5 seconds
2. win-whisper: transcribe
3. Agent interprets the command
4. win-ui-auto: execute the action
```

### Meeting notes
```
1. win-whisper: record with medium/large model
2. Agent summarizes key points and action items
3. ms-todo or google-tasks: create tasks
```

### Multilingual transcription
```
1. win-whisper: transcribe with -l auto
2. win-whisper: translate to English with -tr
3. Agent processes both original and translation
```

## Notes

- Requires one-time setup: download whisper-cli (~16 MB) and a model (75 MB – 1.6 GB).
- Audio recording uses Windows Multimedia API (winmm.dll) — zero external dependencies.
- whisper.cpp v1.8.3 includes 12x performance boost on Intel integrated/discrete GPUs.
- GPU and Flash Attention are enabled by default. Use `--no-gpu` to force CPU-only.
- Supported audio formats: WAV, MP3, FLAC, OGG (built-in decoder).
- Recording format: 22050 Hz, 16-bit, mono. If your mic doesn't support this, remove the `set` line to record at default format — whisper-cli handles resampling.
- Thread count: `-t N` (default 4). Use `-t 8` for faster inference on many-core CPUs.
- The download includes `whisper-stream.exe` for real-time mic transcription via SDL2.
- For Intel NPU: build with OpenVINO (`-DWHISPER_OPENVINO=1`), then use `--ov-e-device NPU`.
- Combine with `win-screenshot` + `win-ocr` for a complete See + Hear + Act agent loop.
