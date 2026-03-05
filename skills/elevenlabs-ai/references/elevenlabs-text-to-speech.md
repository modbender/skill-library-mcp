# Text-to-Speech (TTS)

## Endpoint
- `POST /v1/text-to-speech/:voice_id`

## Core inputs
- `voice_id` (path)
- `text` (request body)
- `model_id` (optional)
- `output_format` (query param)

## Notes
- `enable_logging=false` enables zero-retention mode (enterprise only).
