---
name: mlx-tts
description: Text-To-Speech with MLX (Apple Silicon) and opensource models (default QWen3-TTS) locally.
author: guoqiao
metadata: {"openclaw":{"always":true,"emoji":"🦞","homepage":"https://clawhub.ai/guoqiao/mlx-tts","os":["darwin"],"requires":{"bins":["brew"]}}}
triggers:
- "/mlx-tts <text>"
- "TTS ..."
- "Convert text to audio ..."
- "Say <text>"
- "Reply with voice message ..."
---

# MLX TTS

Text-To-Speech with MLX (Apple Silicon) and open-source models (default QWen3-TTS) locally.

Free and Fast. No API key required. No server required.

## Requirements

- `mlx`: macOS with Apple Silicon
- `brew`: used to install deps if not available

## Installation

```bash
bash ${baseDir}/install.sh
```
This script will use `brew` to install these CLI tools if not available:
- `uv`: install python package and run python script
- `mlx_audio`: do the real job

## Usage

To generate audio from text, run this script:

```bash
bash ${baseDir}/mlx-tts.sh "<text>"
```

### Agent Instructions

1. **Run the script**: Pass the text to be spoken as an argument.
2. **Handle Output**: The script will output a path to a audio file.
Use the `message` tool to send the audio file to the user as an voice message:
```json
{
   "action": "send",
   "filePath": "<filepath>"
}
```

Example:
User: "Say hello world"
Agent:
1. Runs `bash path/to/mlx-tts.sh "hello world"`
2. Receives output: `/tmp/folder/audio.ogg`
3. Calls `message(action="send", filePath="/tmp/folder/audio.ogg", ...)`
