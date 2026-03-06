# Qwen3-ASR (mlx_audio) quick notes (used by telegram-voice-smart-reply)

Source (upstream README): https://github.com/Blaizzy/mlx-audio/blob/main/mlx_audio/stt/models/qwen3_asr/README.md

## Models

- ASR:
  - `mlx-community/Qwen3-ASR-0.6B-8bit`
  - `mlx-community/Qwen3-ASR-1.7B-8bit`
- Forced aligner:
  - `mlx-community/Qwen3-ForcedAligner-0.6B-8bit`

## Supported languages (upstream)

Chinese, Cantonese, English, German, Spanish, French, Italian, Portuguese, Russian, Korean, Japanese

## Upstream CLI examples

```bash
uv run mlx_audio.stt.generate --model mlx-community/Qwen3-ASR-0.6B-8bit --audio audio.wav --output-path output
uv run mlx_audio.stt.generate --model mlx-community/Qwen3-ASR-1.7B-8bit --audio audio.wav --output-path output --language English
uv run mlx_audio.stt.generate --model mlx-community/Qwen3-ASR-0.6B-8bit --audio audio.wav --output-path output --stream

uv run mlx_audio.stt.generate --model mlx-community/Qwen3-ForcedAligner-0.6B-8bit --audio audio.wav --text "The transcript to align" --language English
```

## Python API shape (upstream)

- `from mlx_audio.stt import load`
- `model = load(<model_id>)`
- `result = model.generate(<audio>, language=...)`
- `result.text` is the full transcription
- `result.segments` contains `[{"text": ..., "start": ..., "end": ...}, ...]`
