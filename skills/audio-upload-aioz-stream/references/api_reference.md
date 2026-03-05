# W3Stream Audio API Reference

## Authentication

All requests require HTTP headers:
- `stream-public-key`: Your W3Stream public API key
- `stream-secret-key`: Your W3Stream secret API key

## Quality Presets

Available quality presets for the `resolution` field:

- `standard` — Standard quality
- `good` — Good quality
- `highest` — Highest quality
- `lossless` — Lossless quality

## Streaming Formats

Available formats for the `type` field:

- `hls` — HTTP Live Streaming (container: `mpegts` or `mp4`)
- `dash` — Dynamic Adaptive Streaming (container: `fmp4`)

## Audio Configuration

### Codec
- `aac` — Only supported audio codec

### Bitrate Recommendations

| Use Case | Bitrate (bps) |
|----------|---------------|
| Podcast/Voice | 64000 - 128000 |
| Music (standard) | 128000 - 192000 |
| Music (high quality) | 192000 - 256000 |
| Music (highest) | 256000 - 320000 |

### Sample Rate Options

Supported sample rates (Hz):
- `8000`, `11025`, `16000`, `22050`, `32000`, `44100`, `48000`, `88200`, `96000`

**Recommendations:**
- Voice: `22050` or `32000`
- Music: `44100` or `48000`

### Other Audio Config Fields

- `channels`: `"2"` (stereo)
- `language`: BCP 47 language code (e.g., `en`, `vi`, `fr`)
- `index`: `0` (audio track index)

## Example Configurations

### Standard Quality (Voice/Podcast)

```json
{
  "resolution": "standard",
  "type": "hls",
  "container_type": "mpegts",
  "audio_config": {
    "codec": "aac",
    "bitrate": 128000,
    "channels": "2",
    "sample_rate": 44100,
    "language": "en",
    "index": 0
  }
}
```

### Highest Quality (Music)

```json
{
  "resolution": "highest",
  "type": "hls",
  "container_type": "mpegts",
  "audio_config": {
    "codec": "aac",
    "bitrate": 320000,
    "channels": "2",
    "sample_rate": 48000,
    "language": "en",
    "index": 0
  }
}
```

### Lossless Quality

```json
{
  "resolution": "lossless",
  "type": "hls",
  "container_type": "mpegts",
  "audio_config": {
    "codec": "aac",
    "bitrate": 320000,
    "channels": "2",
    "sample_rate": 96000,
    "language": "en",
    "index": 0
  }
}
```

## API Response Fields

### Create Audio Response

```json
{
  "data": {
    "id": "audio_id_here",
    "title": "Audio Title",
    "type": "audio",
    "status": "transcoding",
    ...
  }
}
```

**Key fields:**
- `data.id` — Audio ID (needed to fetch details)
- `data.status` — Processing status (`transcoding`, `ready`, etc.)

### Get Audio Detail Response

```json
{
  "data": {
    "id": "audio_id",
    "hls": "https://cdn.example.com/audio.m3u8",
    "assets": {
      "hls": "https://cdn.example.com/audio.m3u8"
    },
    "status": "ready"
  }
}
```

**Key fields:**
- `data.hls` — HLS streaming URL (primary)
- `data.assets.hls` — Alternative HLS URL field
- `data.status` — Current status

**Note:** Audio objects do NOT have an `mp4_url` field. Only HLS/DASH streaming links are available.

## Error Codes

- `401` — Invalid API keys (public or secret key incorrect)
- `400` — Bad request (malformed JSON or invalid parameters)
- `404` — Audio not found
- `500` — Server error (retry recommended)
