# Amber Voice Assistant - Setup Wizard Demo

This directory contains demo recordings of the interactive setup wizard.

## Live Demo

**🎬 [Watch on asciinema.org](https://asciinema.org/a/l1nOHktunybwAheQ)** - Interactive player with copyable text and adjustable playback speed.

## Files

### `demo.gif` (167 KB)
Animated GIF showing the complete setup wizard flow. Use this for:
- GitHub README embeds
- Documentation
- Quick previews

**Example usage in Markdown:**
```markdown
![Setup Wizard Demo](demo/demo.gif)
```

### `demo.cast` (9 KB)
Asciinema recording file. Use this for:
- Web embeds with asciinema player
- Higher quality playback
- Smaller file size

**Play locally:**
```bash
asciinema play demo.cast
```

**Embed on web:**
```html
<script src="https://asciinema.org/a/14.js" id="asciicast-14" async></script>
```

**Upload to asciinema.org:**
```bash
asciinema upload --server-url https://asciinema.org demo.cast
```

Note: The `--server-url` flag is required on this system even though authentication exists.

## What the Demo Shows

The wizard guides users through:

1. **Twilio Configuration**
   - Account SID validation (must start with "AC")
   - Real-time credential testing via Twilio API
   - Phone number format validation (E.164)

2. **OpenAI Configuration**
   - API key validation via OpenAI API
   - Project ID and webhook secret (required for OpenAI Realtime)
   - Voice selection (alloy/echo/fable/onyx/nova/shimmer)

3. **Server Setup**
   - Port configuration
   - Automatic ngrok detection and tunnel discovery
   - Public URL configuration

4. **Optional Integrations**
   - OpenClaw gateway (brain-in-loop features)
   - Assistant personalization (name, operator info)
   - Call screening customization

5. **Post-Setup**
   - Automatic dependency installation
   - TypeScript build
   - Clear next steps with webhook URL

## Demo Flow

The demo uses these example values (not real credentials):
- **Twilio SID:** AC1234567890abcdef1234567890abcd
- **Phone:** +15551234567
- **OpenAI Key:** sk-proj-demo1234567890abcdefghijklmnopqrstuvwxyz
- **OpenAI Project ID:** proj_demo1234567890abcdef
- **OpenAI Webhook Secret:** whsec_demo9876543210fedcba
- **Assistant:** Amber
- **Operator:** John Smith
- **Organization:** Acme Corp

## Recreation

To record your own demo:

```bash
# Install dependencies
brew install asciinema agg expect

# 1. CRITICAL: Copy demo-wizard.js to /tmp/amber-wizard-test/ first!
cp demo-wizard.js /tmp/amber-wizard-test/

# 2. Record with asciinema wrapping expect (NOT running expect directly!)
asciinema rec demo.cast --command "expect demo.exp" --overwrite --title "Amber Phone-Capable Voice Agent - Setup Wizard"

# 3. Convert to GIF
agg --font-size 14 --speed 2 --cols 80 --rows 30 demo.cast demo.gif

# 4. Upload to asciinema.org
asciinema upload --server-url https://asciinema.org demo.cast
```

### ⚠️ CRITICAL RECORDING NOTES

**MUST DO:**
1. **Always copy demo-wizard.js to /tmp/amber-wizard-test/ BEFORE recording** - The expect script runs the file from /tmp, not from the skill directory
2. **Use `asciinema rec --command "expect demo.exp"`** - This actually records the session
3. **Include `--overwrite` flag** - Prevents creating multiple demo.cast files
4. **Use `--title` flag** - Sets the recording title in metadata (can't be changed easily after upload)

**NEVER DO:**
1. ❌ Run `expect demo.exp` directly - This executes the wizard but doesn't record it
2. ❌ Edit demo-wizard.js without copying to /tmp - Recording will use the old version
3. ❌ Upload without verifying demo.cast timestamp - Ensure the file was actually regenerated

**Verification checklist:**
- [ ] demo-wizard.js copied to /tmp/amber-wizard-test/
- [ ] demo.cast timestamp is current (check with `ls -la demo.cast`)
- [ ] Banner alignment looks correct in the .cast file
- [ ] Title is set correctly (visible on asciinema.org after upload)

---

*Demo last updated on 2026-02-21 using asciinema 3.1.0 and agg 1.7.0*
