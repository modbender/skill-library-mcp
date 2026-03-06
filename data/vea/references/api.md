# VEA API Reference

Base URL: `http://localhost:8000/video-edit/v1`

## Endpoints

### GET /movies
List available videos in the library.

**Response:**
```json
[
  {"name": "basketball", "path": "data/videos/basketball/game.mp4", "duration": 4537}
]
```

### POST /index
Index a video for AI comprehension. Required before any editing operations.

**Request:**
```json
{
  "blob_path": "data/videos/project/video.mp4"
}
```

**Response:**
```json
{
  "status": "success",
  "indexing_path": "data/indexing/project/media_indexing.json"
}
```

### POST /flexible_respond
Generate video response or answer questions about indexed video.

**Request:**
```json
{
  "blob_path": "data/videos/project/video.mp4",
  "prompt": "Create a highlight reel",
  "video_response": true,
  "original_audio": true,
  "music": true,
  "narration": true,
  "aspect_ratio": 1.78,
  "subtitles": true,
  "snap_to_beat": false,
  "output_path": null
}
```

**Parameters:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `blob_path` | string | required | Path to video in data/videos/ |
| `prompt` | string | required | User instruction |
| `video_response` | bool | false | Generate video (true) or text (false) |
| `original_audio` | bool | true | Include original video audio |
| `music` | bool | true | Add background music |
| `narration` | bool | true | Generate AI voiceover |
| `aspect_ratio` | float | 0 | Target ratio (0=source, 1.78=16:9, 1.0=square) |
| `subtitles` | bool | true | Burn subtitles |
| `snap_to_beat` | bool | false | Align cuts to music beats |

**Response:**
```json
{
  "response": "Here's your highlight reel...",
  "response_type": "video",
  "evidence_paths": ["data/outputs/project/project.mp4"],
  "run_id": "abc123"
}
```

### POST /movie_to_shorts
Convert long-form video into multiple short clips.

**Request:**
```json
{
  "blob_path": "data/videos/project/video.mp4",
  "target_duration": 60,
  "num_shorts": 5,
  "aspect_ratio": 0.5625
}
```

### POST /quality_assessment
Assess quality of an indexed video.

**Request:**
```json
{
  "blob_path": "data/videos/project/video.mp4"
}
```

## Output Structure

After `/flexible_respond` with `video_response: true`:

```
data/outputs/PROJECT_NAME/
├── PROJECT_NAME.mp4        # Final rendered video
├── PROJECT_NAME.fcpxml     # Final Cut Pro project
├── clip_plan.json          # Clip definitions with narration
├── footage/                # Normalized source clips
├── narrations/             # TTS audio (1.mp3, 2.mp3, ...)
├── subtitles/              # subtitles.srt
└── music/                  # Background music files
```

## clip_plan.json Schema

```json
[
  {
    "id": 1,
    "file_name": "video.mp4",
    "start": "00:05:10,220",
    "end": "00:05:21,718",
    "narration": "This clip shows...",
    "priority": "clip_video",
    "cloud_storage_path": "data/videos/project/video.mp4"
  }
]
```

**Priority values:**
- `narration` — Trim to narration length, mute original
- `clip_audio` — Play with narration, then original audio
- `clip_video` — Use full clip with original audio
