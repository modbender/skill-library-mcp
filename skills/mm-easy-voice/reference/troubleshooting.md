# Troubleshooting

Common issues and solutions.

## Environment Issues

### MINIMAX_VOICE_API_KEY not set

**Error**: `ValueError: MINIMAX_VOICE_API_KEY is required`

**Solution**:
```bash
export MINIMAX_VOICE_API_KEY="your-api-key"
```

### FFmpeg not found

**Error**: `RuntimeError: FFmpeg not installed`

**Solution**:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Verify
ffmpeg -version
```

---

## API Errors

### Authentication failure

**Error**: `401 Unauthorized`

**Solution**:
- Verify API key is correct
- Check key hasn't expired
- Ensure no extra spaces in key

### Rate limiting

**Error**: `429 Too Many Requests`

**Solution**:
- Add delays between requests
- Check your plan limits

---

## Audio Issues

### Merge failed

**Error**: `RuntimeError: FFmpeg command failed`

**Solution**:
- Ensure all input files exist
- Check formats are compatible
- Verify FFmpeg is installed

### Volume inconsistent

**Solution**: Normalize after merging
```bash
python mmvoice.py merge a.mp3 b.mp3 -o merged.mp3 --no-normalize
```

---

## Voice Issues

### Voice not found

**Solution**: List available voices
```bash
python mmvoice.py list-voices
```

### Cloned voice expired

**Issue**: Voice deleted after 7 days

**Solution**: Use voice with TTS within 7 days to save permanently.

### Clone failed

**Check requirements**:
- Duration: 10s–5min
- File size: ≤20MB
- Format: mp3, wav, m4a

---

## Quick Reference

| Error | Solution |
|-------|----------|
| `MINIMAX_VOICE_API_KEY is required` | `export MINIMAX_VOICE_API_KEY="key"` |
| `FFmpeg not installed` | `brew install ffmpeg` |
| `Voice not found` | `python mmvoice.py list-voices` |
| `401 Unauthorized` | Check API key validity |
| `429 Too Many Requests` | Add delays between requests |

## Getting Help

1. Check `reference/voice_catalog.md` for voice selection
2. Verify environment with `python check_environment.py`
