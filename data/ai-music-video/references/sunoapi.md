# SunoAPI Reference (sunoapi.org)

## Base URL
`https://api.sunoapi.org/api/v1`

## Auth
`Authorization: Bearer $SUNO_API_KEY`

## Models
| Model | Max Duration | Notes |
|-------|-------------|-------|
| V4_5ALL | 8 min | **Default** — best overall song structure |
| V5 | 8 min | Latest (Sep 2025), best quality |
| V4_5PLUS | 8 min | Richer tones |
| V4_5 | 8 min | Smart prompts |
| V4 | 4 min | Improved vocals |

## Endpoints

### Generate Music
```
POST /generate
{
  "prompt": "lyrics or description (max 5000 chars for V5)",
  "model": "V4_5ALL",
  "customMode": true,           // enables style+title
  "instrumental": false,
  "style": "90s boy band pop",  // max 1000 chars (V5)
  "title": "Song Title",        // max 100 chars (V5)
  "negativeTags": "Heavy Metal",
  "vocalGender": "m",           // m/f
  "styleWeight": 0.65,          // optional
  "weirdnessConstraint": 0.65,  // optional
  "audioWeight": 0.65,          // optional
  "personaId": "persona_123",   // optional
  "personaModel": "style_persona", // optional
  "callBackUrl": "https://..."  // optional callback
}
→ {"code":200,"data":{"taskId":"xxx"}}
```

### Poll Status
```
GET /generate/record-info?taskId=xxx
→ {
  "code": 200,
  "data": {
    "taskId": "xxx",
    "status": "SUCCESS|PENDING|PROCESSING|FAILED",
    "response": {
      "sunoData": [{
        "id": "audio_id",
        "audioUrl": "https://...",
        "imageUrl": "https://...",
        "videoUrl": "https://...",
        "title": "...",
        "tags": "...",
        "duration": 180.5,
        "prompt": "[Verse] ..."
      }]
    }
  }
}
```

### Get Timestamped Lyrics
```
POST /generate/get-timestamped-lyrics
{
  "taskId": "5c79****be8e",
  "audioId": "e231****-****-****-****-****8cadc7dc"
}
→ {
  "code": 200,
  "msg": "success",
  "data": {
    "alignedWords": [
      {"word": "첫 번째 ", "startS": 0.5, "endS": 3.2, "success": true, "palign": 0},
      {"word": "가사\n", "startS": 3.5, "endS": 6.1, "success": true, "palign": 0}
    ]
  }
}
```
- Returns word-level timestamps (not line-level) via `alignedWords` array
- `startS`/`endS` in seconds; `\n` in `word` indicates line break
- Group words into lines by splitting on `\n`, then convert to SRT
- Instrumental tracks return empty array
- Use for karaoke-style display or SRT subtitle generation

### Create Music Video (Suno Native)
```
POST /mp4/generate
{
  "taskId": "taskId_xxx",
  "audioId": "e231****",
  "callBackUrl": "https://...",
  "author": "Artist Name",       // optional, max 50 chars
  "domainName": "music.example.com" // optional watermark, max 50 chars
}
→ {"code":200,"msg":"success","data":{"taskId":"mv_task_id"}}
```

### Poll Music Video Status
```
GET /mp4/record-info?taskId=mv_task_id
→ {
  "code": 200,
  "data": {
    "taskId": "mv_task_id",
    "successFlag": "SUCCESS|PENDING|FAILED",
    "response": {
      "videoUrl": "https://tempfile.aiquickdraw.com/r/xxx.mp4"
    }
  }
}
```
- Generates MP4 with visual effects synced to music
- Generated videos retained 15 days
- Poll via `/mp4/record-info` (NOT `/generate/record-info`)
- 409 = video already exists for this track

### Check Credits
```
GET /get-credits → {"code":200,"data": 100}
```

### Generate Lyrics
```
POST /lyrics
{"prompt": "theme description"}
→ {"code":200,"data":{"taskId":"xxx"}}
```

### Extend Music
```
POST /generate/extend
{
  "audioId": "xxx",
  "continueAt": 120,
  "prompt": "Continue with guitar solo",
  "model": "V4_5ALL"
}
```

## Status Codes
- 200: Success
- 400: Invalid params
- 401: Unauthorized
- 404: Invalid path
- 405: Rate limit exceeded
- 409: Conflict (MP4 already exists)
- 413: Prompt too long
- 429: Insufficient credits
- 430: Rate limited (call frequency)
- 455: Maintenance
- 500: Server error

### Generate Persona
`POST /generate/generate-persona`

페르소나(음악 캐릭터) 생성 — 보컬 스타일을 추출해서 다음 곡에 재사용.

```json
{
  "taskId": "5c79****be8e",
  "audioId": "e231****8cadc7dc",
  "name": "개발자 노동요 싱어",
  "description": "코딩하며 듣기 좋은 인디록/일렉 보컬",
  "vocalStart": 0,
  "vocalEnd": 30,
  "style": "indie rock, electronic"
}
```

**Params:**
- `taskId` (required): 음악 생성 task ID
- `audioId` (required): 분석할 오디오 ID
- `name` (required): 페르소나 이름
- `description` (required): 음악 특성, 스타일, 성격 설명
- `vocalStart` / `vocalEnd` (optional): 분석 구간 (10-30초, default 0-30)
- `style` (optional): 스타일 라벨

**Response:** `personaId` 반환 → generate 시 `personaId` + `personaModel: "style_persona"` 전달

**주의:**
- 음악 생성 완료 후에만 호출 가능
- V4 이상 모델만 지원
- 각 audioId당 1회만 생성 가능 (409 Conflict)

## Notes
- Each generation produces 2 tracks (~10 credits)
- Poll every 15-30s; timeout ~10 min
- Audio files: MP3 format
- Generated files retained 15 days on CDN
