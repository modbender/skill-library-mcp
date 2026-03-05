# Speech-to-Speech (Voice Changer)

## Endpoint
- `POST /v1/speech-to-speech/:voice_id`

## Core inputs
- `voice_id` (path)
- audio input (file or stream per API)
- `output_format` (query param)

## Notes
- `enable_logging=false` enables zero-retention mode (enterprise only).
