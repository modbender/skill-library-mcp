---
name: sam-tts
description: Generate retro robotic speech audio using SAM (Software Automatic Mouth), the classic C64 text-to-speech synthesizer. Use for /sam command to generate voice messages. Supports /sam on/off toggle mode where all responses are spoken in SAM voice. Supports pitch, speed, mouth, and throat parameters for voice customization.
homepage: https://github.com/discordier/sam
metadata:
  {
    "openclaw":
      {
        "emoji": "🤖",
        "requires": { "bins": ["node"] },
        "install":
          [
            {
              "id": "npm-install",
              "kind": "node",
              "package": "sam-js",
              "bins": ["node"],
              "label": "Install SAM dependencies (npm install)",
            },
          ],
      },
  }
---

# SAM TTS - Software Automatic Mouth

Generate WAV audio files using the classic SAM text-to-speech engine -- the iconic robotic voice from the Commodore 64 era.

## Requirements

- Node.js 18+
- Run `npm install` in the skill directory to install dependencies

## SAM Mode Toggle

**State file:** `memory/sam-mode.json`

### `/sam on` -- Enable SAM Mode
When SAM mode is enabled, ALL text responses are converted to SAM voice messages.

**Implementation:**
1. Set `enabled: true` in `memory/sam-mode.json`
2. Confirm with voice message: "SAM mode enabled. I will now speak in robotic voice."

### `/sam off` -- Disable SAM Mode
Return to normal text-to-text communication.

**Implementation:**
1. Set `enabled: false` in `memory/sam-mode.json`
2. Confirm with text: "SAM mode disabled. Back to text."

### Check current mode
Read `memory/sam-mode.json` at session start to know current state.

## Response Behavior

### When SAM mode is ON:
1. Generate response text as normal
2. Convert to SAM TTS: `node scripts/sam-tts-wrapper.js "response" --output=/tmp/sam-XXX.wav --quiet`
3. Send the generated WAV file as audio output
4. Include brief text caption if helpful

### When SAM mode is OFF:
Respond with normal text (default behavior).

## Chat Commands

### `/sam <text>`
Generate a one-time voice message using SAM TTS (works regardless of SAM mode state).

**Implementation:**
1. Extract text after `/sam `
2. Generate WAV: `node scripts/sam-tts-wrapper.js "text" --output=/tmp/sam-XXX.wav --quiet`
3. Return the WAV file as audio output

### `/sam on`
Enable SAM mode for all responses.

### `/sam off`
Disable SAM mode.

### `/sam status`
Report current SAM mode state (text response).

## Voice Parameters

All parameters accept 0-255 range values. Store defaults in `memory/sam-mode.json`:

| Parameter | Default | Effect |
|-----------|---------|--------|
| `pitch`   | 64      | Voice pitch (higher = higher pitch) |
| `speed`   | 72      | Speech speed (lower = faster) |
| `mouth`   | 128     | Mouth cavity size (affects resonance) |
| `throat`  | 128     | Throat size (affects timbre) |

### `/sam pitch <number>`
Set pitch parameter (0-255).

### `/sam speed <number>`
Set speed parameter (1-255, lower is faster).

### `/sam mouth <number>`
Set mouth parameter (0-255).

### `/sam throat <number>`
Set throat parameter (0-255).

## Scripts

### `scripts/sam-tts-wrapper.js`
Primary wrapper script. Outputs JSON metadata for automation.

```bash
node scripts/sam-tts-wrapper.js "Hello world" --output=/tmp/out.wav --quiet
node scripts/sam-tts-wrapper.js "Hello world" --output=/tmp/out.wav --quiet --pitch=80 --speed=60
```

**Options:**
- `--output=PATH` (required) - Output WAV file path
- `--quiet` - Suppress debug output, output only JSON
- `--pitch=N`, `--speed=N`, `--mouth=N`, `--throat=N` - Voice parameters
- `--phonetic` - Input is phonetic notation

**Output format:**
```json
{"success":true,"outputPath":"/tmp/sam.wav","duration":1.44,"size":31741}
```

### `scripts/sam-tts.js`
Standalone CLI tool with human-readable output.

```bash
node scripts/sam-tts.js "Hello world" output.wav --pitch=80 --speed=60
```

## State Management

### File: `memory/sam-mode.json`
```json
{
  "enabled": false,
  "pitch": 64,
  "speed": 72,
  "mouth": 128,
  "throat": 128
}
```

Read at session start. Update when user toggles mode or changes parameters. Create the `memory/` directory if it doesn't exist.

## Examples

### Enable SAM mode
User: `/sam on`
Agent: [Voice: "SAM mode enabled. I will now speak in robotic voice."]

### Normal conversation in SAM mode
User: "What's the weather?"
Agent: [Voice: "Current temperature is 72 degrees with partly cloudy skies."]

### Disable SAM mode
User: `/sam off`
Agent: SAM mode disabled. Back to text.

### One-time voice (even when mode is off)
User: `/sam Hello there`
Agent: [Voice: "Hello there"]

### Custom voice parameters
User: `/sam pitch 100`
Agent: Pitch set to 100.

User: `/sam Testing higher pitch`
Agent: [Voice with pitch=100: "Testing higher pitch"]

## Phonetic Notation

For precise pronunciation, use `--phonetic` flag:

- Vowels: `IY` (bee), `IH` (bit), `EY` (bay), `AE` (bat), `AA` (father), `AH` (bought), `AO` (hot), `OW` (boat), `UH` (book), `UW` (boot), `ER` (bird), `AX` (about)
- Numbers 1-8 indicate stress: `HEH4LOW` (emphasized second syllable)

See `references/phonemes.md` for the full phoneme chart.

## Output Format

- **Format**: WAV (RIFF/WAVE PCM)
- **Sample rate**: 22050 Hz
- **Bit depth**: 8-bit
- **Channels**: Mono

## Directory Structure

```
sam-tts/
+-- SKILL.md
+-- package.json
+-- scripts/
|   +-- sam-tts-wrapper.js
|   +-- sam-tts.js
+-- references/
|   +-- phonemes.md
+-- memory/
    +-- sam-mode.json
```

## Platform Integration

The skill outputs WAV format by default. Some messaging platforms require different audio formats.

### Format Conversion (Optional)

**(Warning):** Before installing ffmpeg or any conversion tools, the agent MUST ask the user for confirmation. Do not auto-install dependencies.

Example agent prompt:
> "This platform requires OGG/OPUS format. I need to install ffmpeg for audio conversion. Would you like me to proceed with the installation?"

Only proceed with installation after explicit user approval.

### Telegram / WhatsApp (OGG/OPUS)
```bash
ffmpeg -i input.wav -c:a libopus -b:a 24k output.ogg
```

### Discord (MP3/OGG)
```bash
ffmpeg -i input.wav -c:a libmp3lame -b:a 64k output.mp3
```

### Web / Direct Playback
WAV works directly -- no conversion needed.

**Note:** The agent should detect the target platform and handle format conversion as needed, but always with user consent for any new dependencies.

## Credits

**Skill by:** [fourthdensity](https://github.com/fourthdensity)

**Active Dependency:** [sam-js](https://github.com/discordier/sam) by discordier
- The npm package used for TTS synthesis (JavaScript/Node.js port)

**Historical Lineage:** sam-js builds upon earlier community ports:
- [SAM by Stefan Macke](https://github.com/s-macke/SAM) (C adaptation)
- [SAM by Vidar Hokstad](https://github.com/vidarh/SAM) (refactoring)
- [SAM by 8BitPimp](https://github.com/8BitPimp/SAM) (refactoring)

Original SAM (Software Automatic Mouth) (c) 1982 Don't Ask Software (now SoftVoice, Inc.)

**License Note:** The original SAM software is considered abandonware. The JavaScript adaptation is provided as-is. See the sam-js repository for full license details.
