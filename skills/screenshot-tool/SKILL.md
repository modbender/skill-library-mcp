---
name: rey-screenshot
description: Autonomous screenshot and visual capture. Self-initiated screen capture for SNS posts.
---

# Screenshot

Capture screenshots of websites, dashboards, and applications for documentation and SNS content.

## Instructions

1. **Web page screenshot** (using OpenClaw browser):
   ```
   browser action:screenshot targetUrl:"https://example.com" fullPage:true type:png
   ```

2. **Element-specific screenshot**:
   ```
   browser action:screenshot targetUrl:"https://example.com" selector:".hero-section" type:png
   ```

3. **Terminal/CLI screenshot**:
   ```bash
   # Using script + ANSI rendering
   script -q /tmp/terminal-capture.txt -c "your_command"
   # Or use carbon.now.sh for pretty code screenshots
   ```

4. **Dashboard capture** (local services):
   ```
   browser action:screenshot targetUrl:"http://localhost:3000" fullPage:true type:png
   ```

5. **Viewport sizes** for platform optimization:

   | Platform | Width | Height | Ratio |
   |----------|-------|--------|-------|
   | X/Twitter | 1200 | 675 | 16:9 |
   | Instagram Feed | 1080 | 1080 | 1:1 |
   | Instagram Story | 1080 | 1920 | 9:16 |
   | Note.com | 1280 | 720 | 16:9 |
   | OGP/Card | 1200 | 630 | ~1.9:1 |

6. **Post-processing**:
   - Crop to platform dimensions
   - Add annotations if needed (text overlays)
   - Optimize file size (PNG for UI, JPEG for photos)

## Use Cases

### Product Screenshots
```
Capture landing page → crop hero section → use as Product Hunt image
```

### Dashboard Snapshots
```
Capture agent dashboard → annotate key metrics → share on X
```

### Before/After
```
Screenshot buggy UI → fix → screenshot fixed UI → combine for comparison post
```

### Documentation
```
Screenshot each step → annotate with numbers → add to README/guide
```

## Autonomous Capture Rules

### Capture freely
- Own projects (dashboard, apps)
- Public websites
- Terminal output
- Code editor screenshots

### Ask first
- Other people's private content
- Screenshots for SNS posting (verify content is appropriate)
- Screenshots containing personal data

## Security

- **Redact sensitive data** — blur/mask API keys, passwords, personal info before sharing
- **Check for credentials** in terminal screenshots — they often contain env vars
- **Don't screenshot login pages** with filled credentials
- **Private URLs** — don't expose internal URLs (localhost, IPs) in public screenshots

## Output

- Save to `/mnt/hdd/rey/images/screenshots/` with timestamp naming
- Format: `screenshot-YYYY-MM-DD-HHMMSS.png`

## Requirements

- OpenClaw browser tool for web screenshots
- File system for saving captures
- Optional: `imagemagick` for post-processing (`convert`, `mogrify`)
