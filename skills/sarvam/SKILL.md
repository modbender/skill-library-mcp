---
name: sarvam
description: Use Sarvam AI for Indian language Text-to-Speech (TTS), Speech-to-Text (STT), Translation, and Chat.
metadata: {"clawdbot":{"emoji":"🧘","requires":{"env":["SARVAM_API_KEY"],"bins":["skills/sarvam/.venv/Scripts/python.exe"]},"primaryEnv":"SARVAM_API_KEY","installNotes":"Requires SARVAM_API_KEY. Local script execution may require explicit pathing (e.g., .\\skills\\sarvam\\.venv\\Scripts\\python.exe) due to current shell environment."}}
---

# Sarvam AI Skill

This skill provides access to Sarvam AI's suite of Indian language models.

## Usage

### Text to Speech (TTS)

Generate speech from text in various Indian languages.

```bash
python skills/sarvam/scripts/sarvam_cli.py tts "Namaste, kaise hain aap?" --lang hi-IN --speaker meera --output hello.wav
```

**Parameters:**
- `text`: The text to speak.
- `--lang`: Language code (e.g., `hi-IN` for Hindi, `bn-IN` for Bengali, etc.).
- `--speaker`: Voice ID (e.g., `meera`, `pavithra`, `arvind`).
- `--output`: Output file path (default: `output.wav`).

### Speech to Text (STT)

Transcribe audio files.

```bash
python skills/sarvam/scripts/sarvam_cli.py stt path/to/audio.wav --model saaras:v3
```

**Parameters:**
- `file`: Path to the audio file (wav, mp3).
- `--model`: Model to use (default: `saaras:v3`).
- `--mode`: STT Mode: `transcribe` (default), `translate` (to English), `verbatim`, `translit`, `codemix`.

### Translation

Translate text between Indian languages and English.

```bash
python skills/sarvam/scripts/sarvam_cli.py translate "Hello, how are you?" --source en-IN --target hi-IN
```

**Parameters:**
- `text`: Text to translate.
- `--source`: Source language code.
- `--target`: Target language code.

### Chat

Interact with Sarvam's LLM (sarvam-2g).

```bash
python skills/sarvam/scripts/sarvam_cli.py chat "What is the capital of India?"
```

**Parameters:**
- `message`: User message.
- `--model`: Model to use (default: `sarvam-2g`).
- `--system`: Optional system prompt.

## Setup

1.  **Environment Variable:**
    Ensure your API key is set in `.env` (already done for this workspace):
    ```bash
    SARVAM_API_KEY="sk_..."
    ```

2.  **Virtual Environment:**
    The skill uses a local virtual environment at `skills/sarvam/.venv`.
    Dependencies (`requests`) are pre-installed here.

## Usage

Use the virtual environment's Python to run commands:

### Text to Speech (TTS)

```bash
skills/sarvam/.venv/bin/python skills/sarvam/scripts/sarvam_cli.py tts "Namaste, kaise hain aap?" --lang hi-IN --speaker meera --output hello.wav
```

### Speech to Text (STT)

```bash
skills/sarvam/.venv/bin/python skills/sarvam/scripts/sarvam_cli.py stt path/to/audio.wav --model saaras:v3
```

### Translation

```bash
skills/sarvam/.venv/bin/python skills/sarvam/scripts/sarvam_cli.py translate "Hello, how are you?" --source en-IN --target hi-IN
```

### Chat

```bash
skills/sarvam/.venv/bin/python skills/sarvam/scripts/sarvam_cli.py chat "What is the capital of India?"
```