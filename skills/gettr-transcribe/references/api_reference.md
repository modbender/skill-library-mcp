# URL Patterns & Reference

## GETTR URL types

### `/streaming/` URLs

Streaming pages host live or recorded streams. The audio is available as a direct `.m4a` download.

- **`og:video` meta tag**: Contains an HLS URL like `https://stream.video.gettr.com/{playback_id}/low.m3u8`
- **Direct audio URL**: Derived by replacing `.m3u8` with `/audio.m4a`:
  `https://stream.video.gettr.com/{playback_id}/audio.m4a`
- The `.m4a` URL is preferred — it's a direct file download (faster, more reliable than HLS)

### `/post/` URLs

Post pages host native video uploads. No direct audio download is available.

- **`og:video` meta tag**: Contains an HLS URL like `https://media.gettr.com/{path}/out.m3u8`
- Use the `.m3u8` URL directly with ffmpeg (the pipeline handles HLS extraction)
- No `.m4a` equivalent exists for post URLs

## Output directory

`./out/gettr-transcribe/<slug>/`

The slug is the last path segment of the GETTR URL (e.g., `/post/p1abc2def` → `p1abc2def`).

## Output files

- `audio.wav` – 16kHz mono audio (optimized for Whisper)
- `audio.vtt` – timestamped transcript (VTT format)
