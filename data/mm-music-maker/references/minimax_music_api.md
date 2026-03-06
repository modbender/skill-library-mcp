# MiniMax Music Generation API (music-2.5)

Source: https://platform.minimaxi.com/docs/api-reference/music-generation

## Endpoint

`POST https://api.minimaxi.com/v1/music_generation`

## Auth

`Authorization: Bearer <token>`

Use your MiniMax API key from the platform console. In scripts, read it from MINIMAX_MUSIC_API_KEY.

## Request (JSON)

Required:
- `model`: string (use `music-2.5`)
- `lyrics`: string (1–3500 chars). Use `\n` for line breaks. You may include structure tags like `[Verse]`, `[Chorus]`, `[Bridge]`, etc.

Optional:
- `prompt`: string (0–2000 chars for music-2.5)
- `stream`: boolean (default `false`)
- `output_format`: `hex` (default) or `url`
- `audio_setting`:
  - `sample_rate` (e.g., 44100)
  - `bitrate` (e.g., 256000)
  - `format` (e.g., `mp3`)
  - `aigc_watermark` (boolean, default false; only applies when `stream=false`)

Example:
```json
{
  "model": "music-2.5",
  "prompt": "indie folk, melancholic, introspective",
  "lyrics": "[verse]\n...\n[chorus]\n...",
  "audio_setting": {
    "sample_rate": 44100,
    "bitrate": 256000,
    "format": "mp3"
  }
}
```

## Response (JSON)

- `data.audio`: audio in **hex** (if `output_format=hex`) or URL (if `output_format=url`)
- `data.status`: generation status
- `extra_info`: duration, sample rate, channels, bitrate, size
- `base_resp.status_code`: `0` on success

If using `url`, the link is valid for **24 hours**.

## Notes

- For `music-2.5`, `prompt` is optional but recommended for style control.
- When `stream=true`, only `hex` output is supported.
