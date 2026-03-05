# Troubleshooting

Common issues and solutions for the voiceai-creator-voiceover-pipeline.

---

## FFmpeg not found

**Symptom:** Warning about skipping master stitch or video muxing.

**Solution:** Install ffmpeg for your platform:

```bash
# macOS
brew install ffmpeg

# Ubuntu / Debian
sudo apt update && sudo apt install ffmpeg

# Windows (Chocolatey)
choco install ffmpeg

# Windows (winget)
winget install ffmpeg

# Windows (manual)
# Download from https://ffmpeg.org/download.html
# Add the bin/ folder to your PATH
```

After installing, verify:
```bash
ffmpeg -version
ffprobe -version
```

> **Note:** The pipeline still works without ffmpeg — you get individual segments, the review page, chapters, and captions. Only master stitching and video muxing require ffmpeg.

---

## Rate limits / API errors

**Symptom:** `Voice.ai TTS error 429` or similar.

**Solutions:**
- Wait a few minutes and retry
- Use `--mock` mode for pipeline testing
- For large scripts, the pipeline renders segments sequentially — this naturally stays under most rate limits
- If you hit limits frequently, consider adding retry logic in `src/api.ts` (a TODO for production use)

---

## Long scripts

**Symptom:** Script has many segments and takes a long time.

**Solutions:**
- Segments are cached by content hash — subsequent builds only re-render changed segments
- Use `--max-chars` to control segment size (larger = fewer API calls, but longer per-segment)
- Split very long scripts into separate build runs
- Use `--mock` mode for testing the pipeline before using real API credits

---

## Windows path quoting

**Symptom:** Paths with spaces cause errors.

**Solutions:**
```powershell
# PowerShell — wrap in quotes
voiceai-vo build --input "C:\Users\Me\My Scripts\script.md" --voice v-warm-narrator --mock

# Or use short paths / avoid spaces
voiceai-vo build --input C:\scripts\video.md --voice v-warm-narrator --mock
```

---

## "Real API not yet configured" error

**Symptom:** Error when running without `--mock` and without setting up real API endpoints.

**Explanation:** The current release uses placeholder API endpoints. The full pipeline works in `--mock` mode.

**Solutions:**
- Always use `--mock` flag until real API endpoints are configured
- See `references/VOICEAI_API.md` for what endpoints to fill in
- Contact the Voice.ai team for production API access

---

## Audio playback issues in review.html

**Symptom:** Audio players don't work in review.html.

**Solutions:**
- Open `review.html` directly in your browser (file:// protocol works)
- Make sure the `segments/` folder is next to `review.html`
- Some browsers block file:// audio — try a local server:
  ```bash
  cd out/my-project/
  python3 -m http.server 8000
  # Then open http://localhost:8000/review.html
  ```

---

## Segment caching

**How it works:**
- Each segment is hashed based on: text content + voice ID + language
- Hashes are stored in `segments/.cache.json`
- On rebuild, unchanged segments are skipped
- Use `--force` to regenerate everything

**To clear cache manually:**
```bash
rm out/my-project/segments/.cache.json
```
