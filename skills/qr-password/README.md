# QR Password Skill

Air-gapped credential bridge for OpenClaw. Transfers credentials between networked and air-gapped devices using QR codes as the optical channel.

## Modes

- **Mode A (Outbound):** Agent retrieves credential → generates QR → displays on canvas → air-gapped device scans
- **Mode B (Inbound):** Air-gapped device shows QR → agent reads via camera → decodes credential

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Agent instructions |
| `scripts/generate-qr.py` | Credential → QR image |
| `scripts/read-qr.py` | QR image → credential |
| `scripts/qr-format.py` | Shared v1 payload encode/decode |
| `assets/qr-generator.html` | Standalone offline QR generator |

## Dependencies

```bash
python3 -m pip install --user qrcode Pillow opencv-python-headless
```

## QR Format (v1)

```json
{"v":1,"u":"username","p":"password","d":"example.com"}
```
