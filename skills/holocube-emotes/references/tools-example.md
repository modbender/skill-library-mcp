# TOOLS.md Example — Holocube Section

Add something like this to your workspace TOOLS.md after setup:

```markdown
### Holocube (GeekMagic HelloCubic-Lite)
- IP: http://<YOUR_IP>
- Display: 240x240px square
- Format: JFIF JPEG only (use Pillow to save, not raw ffmpeg)
- Images do NOT need to be flipped — displays right-side up
- Upload: `POST /doUpload?dir=/image` with form field `file`
- Set active: `/set?img=%2Fimage%2Ffilename.jpg`
- Set theme: `/set?theme=2` (Photo Album)
- ⚠️ NEVER use `/set?reset=1` — that's factory reset, wipes WiFi config
- Reboot: `/set?reboot=1` (response may time out)
- Art style: Glass display — dark/black backgrounds so glass disappears.

#### Emote Controller
- Script: `scripts/holocube.py`
- Usage: `python3 scripts/holocube.py <emote|state> [--static]`
- Sprites on device: `adam-{emote}.gif` (animated) and `adam-{emote}.jpg` (static)

When to set emotes:
- `neutral` — Default idle state
- `thinking` — Processing, running tools, spawning sub-agents
- `happy` — Task completed, good news
- `surprised` — Unexpected input
- `concerned` — Error occurred
- `laughing` — Funny moment
- `sleeping` — Late night (11pm-7am)
```
