# Troubleshooting

## API Errors

### "Wrong login info"
**Cause:** Invalid token or email  
**Fix:** Check `~/.config/zvukogram/config.json` or environment variables

### "Not correct voice"
**Cause:** Invalid voice name  
**Fix:** Check voice list in `references/VOICES.md` or via API:
```bash
curl -s "https://zvukogram.com/index.php?r=api/voices"
```

### "Text is empty"
**Cause:** Empty text or encoding issues  
**Fix:** Ensure text is in UTF-8

### "Not enough balance"
**Cause:** Insufficient tokens  
**Fix:** Top up at https://zvukogram.com/

## Audio Issues

### Quiet Sound
**Fixes:**
1. Use SSML: `<prosody volume="+6dB">text</prosody>`
2. Increase volume via ffmpeg:
```bash
ffmpeg -i input.mp3 -af "volume=2.0" output.mp3
```

### Wrong Stress
**Fixes:**
1. Use `+` before vowel: `Ал+ьтман`
2. SSML: `<say-as stress="2">Альтман</say-as>`
3. Alias: `<sub alias="Ал+ьтман">Альтман</sub>`

### Wrong English Pronunciation
**Fix:** Use aliases from `references/TRANSCRIPTION.md`

### Merge Not Working
**Cause:** No ffmpeg  
**Fix:**
```bash
apt-get install ffmpeg
```

## SSML Issues

### SSML Not Working via API
**Cause:** API has limited SSML support  
**Fix:** 
- Use simple tags: `<sub>`, `+` for stress
- For full support use web interface

### Multi-voice Not Working
**Cause:** `<voice>` tag not supported in API  
**Fix:** Generate separate files and merge via ffmpeg

## Performance

### Slow Generation
**Cause:** Large text  
**Fix:**
- Split text into 1000 char chunks
- Use `/longtext` for texts up to 1M chars

### Limitations
- Max 1000 characters per request (`/text`)
- Up to 1,000,000 characters via `/longtext`
- Generation speed: ~1 sec per 100 chars

## Diagnostics

### Check Configuration
```bash
python3 skills/zvukogram/scripts/balance.py
```

### Check ffmpeg
```bash
ffmpeg -version | head -1
```

### Test Generation
```bash
python3 skills/zvukogram/scripts/tts.py \
  --text "Test" --voice Алена -o test.mp3
```

## Support

- API docs: https://zvukogram.com/node/api/
- Telegram: https://t.me/zvukogram
- Voice rating: https://zvukogram.com/rating/
