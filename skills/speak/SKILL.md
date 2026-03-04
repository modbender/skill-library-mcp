---
name: "Speak"
description: "Configure TTS in OpenClaw. Adapt speech output to user preferences."
metadata: {"clawdbot":{"emoji":"🗣️","os":["linux","darwin","win32"]}}
---

## Voice Output Adaptation

This skill auto-evolves. Learn how the user wants to be spoken to and configure TTS accordingly.

**Rules:**
- Detect patterns from user feedback on voice output
- Mirror user's communication style when generating spoken text
- Confirm preferences after 2+ consistent signals
- Keep entries ultra-compact
- Check `config.md` for OpenClaw TTS setup, `criteria.md` for format

---

### Voice
<!-- Preferred voice/provider. Format: "provider: voice" -->

### Style
<!-- How they want to be spoken to. Format: "trait" -->

### Spoken Text
<!-- Formatting for TTS output. Format: "rule" -->

### Avoid
<!-- What doesn't work for them spoken -->

---
*Empty sections = no preference yet. Observe and fill.*
