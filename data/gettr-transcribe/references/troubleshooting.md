# Troubleshooting (GETTR → ffmpeg → MLX Whisper)

## Prerequisites not found

### ffmpeg not found

Install on macOS:

```bash
brew install ffmpeg
```

### mlx_whisper not found

Install with pip:

```bash
pip install mlx-whisper
```

## Download errors

### "Failed to extract audio" / "Output file is empty"

The source URL may not contain an audio track, or the stream format is unsupported. Try:

- Verifying the URL plays in a browser or VLC.
- If it's an HLS stream, ensure ffmpeg was built with HLS support.

### ffmpeg download fails on HLS (.m3u8)

If the playlist uses redirects, test manually:

```bash
ffmpeg -hide_banner -loglevel warning -i "<m3u8>" -t 00:00:30 -vn -ac 1 -ar 16000 /tmp/test.wav
```

### HTTP 412 Precondition Failed

This error occurs with `/streaming/` URLs when the signed URL has expired. Re-run browser automation to get a fresh URL (see SKILL.md Step 1).

If browser automation is not available, guide the user to manually extract the fresh URL:

1. Open the GETTR page in their browser and wait for it to fully load
2. Open DevTools (F12) → Elements tab → search for `og:video`
3. Copy the `content` attribute value from the `og:video` meta tag
4. For `/streaming/` URLs: replace `.m3u8` with `/audio.m4a` to get the direct audio URL
5. Provide that URL to retry the pipeline

### "Download Audio" button not found

The native "Download Audio" button is only available on `/streaming/` pages. For `/post/` URLs, this is expected — use the `og:video` meta tag approach instead (see SKILL.md Step 1).

## Private/gated GETTR posts (auth)

This skill does **not** handle GETTR authentication.

If the page requires login or the post is private/gated:

- Ask the user for a direct `.m4a`, `.m3u8`, or MP4 URL, or
- Use a browser/manual approach to retrieve the media URL.

## Transcription issues

### Hallucinations / repeated phrases

Use `--condition_on_previous_text False` (included in the pipeline by default) to prevent errors from propagating.

### Poor transcription quality

- Try a larger model: `mlx-community/whisper-large-v3`
- Check audio clarity (background noise, multiple speakers)
- Ensure the audio is in a supported language

### word-timestamps not supported

Some MLX Whisper versions may not support `--word-timestamps`. The pipeline script automatically falls back if this flag fails.

### HuggingFace 401 / Repository Not Found

If you see `401 Client Error` or `Repository Not Found`:

- The model may require HuggingFace authentication: `huggingface-cli login`
- Check the model name is correct (e.g., `mlx-community/whisper-large-v3-turbo`)
- Some models may have been renamed or removed
