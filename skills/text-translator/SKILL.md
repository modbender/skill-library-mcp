---
description: Translate text between languages using translate-shell (trans) — no API keys required.
---

# Text Translator

Translate text between languages using free, no-API-key methods.

## Requirements

- `translate-shell` (`trans`) — install: `sudo apt-get install translate-shell`
- No API keys needed

## Instructions

### Basic translation
```bash
# Translate with explicit source/target
trans -b en:ja "Hello, how are you?"

# Auto-detect source language
trans -b :en "こんにちは"

# Detailed output with alternatives and pronunciation
trans en:de "Good morning"

# Translate a file
trans -b en:fr -i input.txt -o output.txt
```

### Common language codes
`en` English, `ja` Japanese, `zh` Chinese, `ko` Korean, `fr` French, `de` German, `es` Spanish, `pt` Portuguese, `it` Italian, `ru` Russian, `ar` Arabic, `hi` Hindi, `th` Thai, `vi` Vietnamese

### Batch translation
```bash
# Translate multiple lines (one per line)
while IFS= read -r line; do
  trans -b :en "$line"
  sleep 0.5  # Rate limit courtesy
done < input.txt
```

### Output format
```
**Translation** (en → ja):
| Original | Translation |
|----------|-------------|
| Hello | こんにちは |
| Thank you | ありがとうございます |

*Powered by Google Translate via translate-shell*
```

## Edge Cases

- **`trans` not installed**: Check with `which trans`. Provide install command for the user's OS.
- **Rate limiting**: Google Translate may throttle after many requests. Add `sleep 0.5` between batch calls.
- **Long text**: Split into paragraphs for better translation quality and to avoid timeouts.
- **Unsupported language**: `trans -R` lists all supported languages. Suggest closest match.
- **Special characters**: Quote the input string to prevent shell interpretation.
- **Offline**: `trans` requires internet — no offline fallback available.

## Security

- Translation sends text to Google Translate servers — **never translate sensitive data** (passwords, API keys, private documents).
- Warn user if the text appears to contain credentials or PII.

## Notes

- `translate-shell` is the recommended method — stable, packaged in most Linux distros.
- The undocumented Google Translate API endpoint may break without notice — prefer `trans`.
