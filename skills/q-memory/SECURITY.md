# Security Policy for Q Memory

## v1.8.5-no-crypto (No Encryption)

This version of Q Memory does **not** include encryption functionality to avoid ClawHub security scan false positives.

### Data Privacy

- ✅ All data stored locally (Markdown + JSON)
- ✅ No network transmission
- ✅ No remote access
- ✅ User has full control of their data

### Data Storage

All memories are stored in plain text:

- `data/qst_memories.md` - Memories (Markdown format)
- `data/qst_doing-state.json` - Agent state (JSON format)
- `data/qst_events.json` - Event history (JSON format)

### Security Recommendations

If you need to store sensitive information:

1. **Do not store sensitive data**: Avoid storing passwords, API keys, or secrets
2. **Use system-level encryption**: Encrypt your entire disk or filesystem
3. **Use v1.8.4 with encryption**: If encryption is critical, use v1.8.4 or manually add crypto.py

### Source Code Audit

All source code is open source and can be audited:
- GitHub: https://github.com/tikchowjp-blip/QST-Memory-Skill
- License: MIT

---

## Contact

For security concerns, please open an issue on GitHub.
