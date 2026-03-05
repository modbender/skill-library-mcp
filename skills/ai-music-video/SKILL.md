---
name: ai-music-video
description: Generate AI music videos end-to-end. Creates music with Suno (sunoapi.org), generates visuals with OpenAI/Seedream/Google/Seedance, and assembles into music video with ffmpeg. Supports timestamped lyrics (auto SRT), Suno native music video generation, slideshow/video/hybrid modes. Token-based cost tracking per generation.
metadata:
  openclaw:
    requires:
      bins: [curl, python3, ffmpeg]
      env:
        - SUNO_API_KEY
        - OPENAI_API_KEY
      optionalEnv:
        - BYTEPLUS_API_KEY
        - TOGETHER_API_KEY
---

# AI Music Video Generator

Create complete music videos: AI music + AI visuals + ffmpeg assembly.

## Quick Start

```
"90년대 보이밴드 풍 한국어 노래 만들어줘" → music only
"발라드 뮤비 만들어줘" → music + slideshow MV
"EDM 뮤비 풀영상으로" → music + video clips MV
"Suno 뮤비로 만들어줘" → Suno native music video
```

## Workflow

### 1. Plan scenes from lyrics/mood
Before generating, create `prompts.json` — array of scene descriptions derived from the song's lyrics, mood, and narrative. 8-12 scenes for a 3-min song.

```json
[
  {"prompt": "Neon-lit city street at night, rain reflections", "type": "image"},
  {"prompt": "Camera slowly panning across a rooftop at sunset", "type": "video"},
  "A lone figure walking through cherry blossoms"
]
```

### 2. Generate music
```bash
bash scripts/suno_music.sh \
  --prompt "가사 또는 설명" \
  --style "90s boy band pop, korean" \
  --title "너만을 원해" \
  --model V4_5ALL --custom \
  --outdir /tmp/mv_project
```

**Options:**
- `--model V4_5ALL` (default), `V5`, `V4_5PLUS`, `V4_5`, `V4`
- `--instrumental` — no vocals
- `--vocal-gender m|f` — vocal gender hint
- `--negative-tags "Heavy Metal, Drums"` — styles to avoid
- `--music-video` — generate Suno native music video (MP4)
- `--dry-run` — cost check only

**Persona (일관된 스타일 유지):**
- `--persona-id ID` — 기존 페르소나 사용 (같은 보컬/스타일로 여러 곡 생성)
- `--create-persona` — 생성된 곡에서 페르소나 생성 → `persona.json` 저장
- `--persona-name "이름"` / `--persona-desc "설명"` / `--persona-style "스타일"`

**Auto features:**
- 🎤 **Timestamped Lyrics**: Non-instrumental tracks automatically fetch lyrics timestamps and save as `{outdir}/lyrics.srt`
- 🎬 **Suno Native MV**: With `--music-video`, Suno generates a visualized MP4 video directly
- 🎭 **Persona**: With `--create-persona`, extracts voice/style identity for reuse

### 3. Generate visuals (custom MV flow)
```bash
bash scripts/gen_visuals.sh \
  --mode slideshow \
  --prompts-file /tmp/mv_project/prompts.json \
  --image-provider seedream \
  --outdir /tmp/mv_project
```

Or with OpenAI (cheaper, lower res):
```bash
bash scripts/gen_visuals.sh \
  --mode slideshow \
  --prompts-file /tmp/mv_project/prompts.json \
  --image-provider openai --image-model gpt-image-1-mini --image-quality medium \
  --outdir /tmp/mv_project
```
Add `--dry-run` first to show cost estimate before spending.

### 4. Assemble
```bash
bash scripts/assemble_mv.sh \
  --audio /tmp/mv_project/track_0_xxx.mp3 \
  --outdir /tmp/mv_project \
  --output /tmp/mv_project/final_mv.mp4 \
  --transition fade
```

**Subtitle behavior:**
- Auto-detects `{outdir}/lyrics.srt` and overlays lyrics automatically
- `--subtitle /path/to/custom.srt` — use custom SRT file
- `--no-subtitle` — disable lyrics overlay entirely

## Modes

| Mode | Visual | Best For | Cost (10 scenes) |
|------|--------|----------|---------------------|
| `slideshow` | AI images | Fast, cheap | ~$0.02 (mini low) / ~$0.09 (mini med) / ~$0.45 (Seedream) |
| `video` | AI video clips | Premium | ~$1.40 (Seedance Lite) / ~$8.00 (Sora 2) |
| `hybrid` | Mix of both | Balanced | ~$0.50-$4.00 |
| `suno-native` | Suno MV | Easiest | Suno credits only |

**Image cost is token-based** — actual billing may be lower than listed estimates. Use `--dry-run` for precise cost.

## Provider Options

**Images:** `--image-provider seedream` (recommended), `openai`, or `google-together`
**Image Model (OpenAI):** `--image-model gpt-image-1-mini` (default, cheap) or `gpt-image-1` (premium)
**Videos:** `--video-provider sora` (default), `sora-pro`, `seedance-lite`, `seedance-pro`, `veo-fast`, `veo-audio`
**Quality:** `--image-quality low|medium|high`

## Cost Tracking

Every script outputs cost before and after. Always `--dry-run` first.
Cost data saved to `{outdir}/cost_estimate.json` and `{outdir}/visuals_meta.json`.

## Environment Variables

```bash
export SUNO_API_KEY="your-sunoapi-key"      # Required — sunoapi.org
export OPENAI_API_KEY="your-openai-key"     # Required — images + Sora video
export BYTEPLUS_API_KEY="your-byteplus-key" # Optional — Seedream 4.5 (recommended for images)
export TOGETHER_API_KEY="your-together-key" # Optional — Seedance, Veo, Imagen
export SUNO_CALLBACK_URL=""                 # Optional — see Callback URL below
```

**⚠️ Required keys:** `SUNO_API_KEY` and `OPENAI_API_KEY` must be set before running any script.
`BYTEPLUS_API_KEY` is needed for Seedream image provider (sign up at [console.byteplus.com](https://console.byteplus.com), 200 free images).
`TOGETHER_API_KEY` is only needed for Seedance/Veo/Imagen providers.

### Callback URL

The Suno API requires a `callBackUrl` field for music generation requests.
By default, if `SUNO_CALLBACK_URL` is not set, the script uses `https://localhost/noop`
as a harmless no-op endpoint (an unreachable localhost URL that effectively disables callbacks).

**To customize:** set `SUNO_CALLBACK_URL` to your own endpoint, or set it to
any dummy URL you control. The callback payload contains task metadata and
audio URLs — no API keys are sent.

**To disable:** set `SUNO_CALLBACK_URL=https://localhost/noop` or any unreachable URL.
Generation still works via polling; the callback is not required for the script to function.

## Persona Workflow (채널 컨셉 유지)

YouTube 채널처럼 일관된 스타일로 여러 곡을 만들 때:

```bash
# 1. 첫 곡 생성 + 페르소나 만들기
bash scripts/suno_music.sh \
  --prompt "코드 리뷰하며 듣는 노래" \
  --style "indie rock, energetic, coding vibe" \
  --title "Pull Request" \
  --custom --create-persona \
  --persona-name "개발자 노동요 싱어" \
  --persona-desc "개발자가 코딩하며 듣기 좋은 에너지 넘치는 보컬. 인디록, 일렉, 팝 장르를 넘나든다." \
  --persona-style "indie rock, electronic, developer work music" \
  --outdir /tmp/dev-bgm-01

# 2. persona.json에서 personaId 확인
cat /tmp/dev-bgm-01/persona.json

# 3. 같은 페르소나로 다음 곡 생성 — 보컬/스타일 일관성 유지
bash scripts/suno_music.sh \
  --prompt "야근하면서 듣는 노래" \
  --style "electronic pop, night coding" \
  --title "Midnight Deploy" \
  --custom --persona-id <PERSONA_ID> \
  --outdir /tmp/dev-bgm-02
```

페르소나는 보컬 특성 + 음악 스타일을 기억해서, 채널 전체의 통일감을 유지해줌.

## Prerequisites

- `curl`, `python3`, `ffmpeg` (for assembly)

## References

- **SunoAPI details:** Read `references/sunoapi.md`
- **Visual provider details:** Read `references/visual-providers.md`
