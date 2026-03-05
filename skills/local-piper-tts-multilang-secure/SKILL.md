---
name: local-piper-tts-multilang-secure
description: Local offline text-to-speech via Piper TTS. Self-contained setup, automatic language detection, per-call voice selection. Extensible to any language. Writes output into the OpenClaw workspace.
metadata: {"openclaw":{"emoji":"🔊","requires":{"bins":["ffmpeg","python3"]}}}
---

# local-piper-tts-multilang-secure

## Description
Local (offline) text-to-speech via Piper.

**Purpose:** generate audio files (OGG/Opus by default) from text, fully offline.
**No sending** is performed by the skill — sending is handled by the agent after the file is ready.

## Features
- Fully offline (no API keys)
- Self-contained setup via `setup()` — installs Piper into an isolated venv, no system-wide changes
- Automatic language detection for 20+ languages with English as default
- Per-call voice selection via `voice` parameter
- On-demand voice download via `downloadVoices()` — no models bundled, choose what you need
- Voice removal via `removeVoice()` — clean up voices you no longer want
- Extensible: add any language by installing a Piper `.onnx` model
- Writes outputs into OpenClaw workspace

## First-run flow — full agent procedure

Follow this sequence exactly when the user asks to use TTS for the first time in a setup context.

### Step 1 — check status
```js
const s = await status();
```

### Step 2 — install Piper if needed
If `s.stage` is `not-setup` or `no-piper`:
- Tell the user: *"To use local TTS I need to install piper-tts into the skill's venv (~30 seconds, one-time). OK to proceed?"*
- Wait for confirmation, then call `setup()`.
- If setup returns a step containing "WARNING: espeak-ng not found", relay the warning and install instructions to the user.
- Call `status()` again after setup completes.

### Step 3 — offer voice download if no models present
If `s.stage` is `no-model` (Piper installed but no `.onnx` files):

**3a. Offer English defaults:**
Explain that two English voices are available as defaults (~65 MB each):
- `en_US-ryan-medium` — male, American
- `en_US-amy-medium` — female, American

Ask which they want, or both: *"Which English voice(s) should I download? Ryan (male), Amy (female), or both?"*

**3b. Ask about other languages:**
After the English choice, ask: *"Do you need any other languages? For example German, French, Spanish, Polish, Italian, Portuguese, Russian… Just tell me and I'll check what's available."*

If the user names a language, look up the available models at https://github.com/rhasspy/piper/blob/master/VOICES.md and list the options. Download whatever the user picks using the same `downloadVoices()` call.

**3c. Download everything at once:**
```js
const result = await downloadVoices(['en_US-ryan-medium', 'en_US-amy-medium', /* + any others */]);
// result.downloaded — succeeded
// result.failed     — [{stem, error}] if any failed
```
Each voice requires internet access. Download takes ~1–2 min per voice on a typical connection.

If any downloads fail:
- Check internet connectivity
- Verify the stem exists at https://github.com/rhasspy/piper/blob/master/VOICES.md
- Offer to retry

### Step 4 — play samples so the user can choose
After downloading, generate a short audio sample for each downloaded voice and send it to the user.

For each voice, use a greeting **in the voice's language**:
- English: `"Hello, I'm [name]. How can I help you today?"`
- German: `"Hallo, ich heiße [Name]. Wie kann ich Ihnen helfen?"`
- French: `"Bonjour, je m'appelle [prénom]. Comment puis-je vous aider?"`
- Spanish: `"Hola, me llamo [nombre]. ¿Cómo puedo ayudarte?"`
- Polish: `"Cześć, mam na imię [imię]. Jak mogę Ci pomóc?"`
- Italian: `"Ciao, mi chiamo [nome]. Come posso aiutarti?"`
- Portuguese: `"Olá, meu nome é [nome]. Como posso ajudar?"`
- Russian: `"Привет, меня зовут [имя]. Чем могу помочь?"`
- For other languages: use an equivalent native greeting.

Replace `[name]` with the voice name (e.g. *Ryan*, *Amy*, *Thorsten*).

```js
const sample = await tts({ text: 'Hello, I\'m Ryan. How can I help you today?', voice: 'en_US-ryan-medium' });
// send sample.path to the user as a voice message
```

Send all samples, then ask: *"Which voice do you prefer? Or shall I download a different one?"*

### Step 5 — choose speech speed
After the user picks a voice, ask:
*"How fast should I speak? Normal is 100%. Some options: 125% (faster), 115% (slightly faster), 100% (normal), 80% (slower) — or tell me a percentage."*

Always present speed as a percentage to the user. Never mention `lengthScale` directly.

`lengthScale` is the internal duration multiplier — lower = faster. To convert: `lengthScale = 1 / (speed% / 100)`.
Examples:
- 125% speed → lengthScale 0.8
- 115% speed → lengthScale 0.87
- 100% speed → lengthScale 1.0 (default)
- 80% speed  → lengthScale 1.25

Generate a short sample at the chosen speed so the user can hear the difference:
```js
const sample = await tts({ text: 'This is how I sound at this speed.', voice: 'chosen-voice', lengthScale: 0.8 });
// send sample.path to the user
```

Confirm with the user, then offer to save it permanently:
*"Should I save this as your default speed? It'll be used automatically every session."*

If the user agrees:
```js
await saveConfig({ lengthScale: 0.8 });
```

Once saved, `tts()` reads it from `config.json` in the skill directory automatically — no need to pass `lengthScale` on every call.

### Step 6 — note the preferred voice and speed
Once confirmed, remember both `voice` and `lengthScale` for the session. Pass them to every subsequent `tts()` call unless the user asks to change them.

---

## Before first use — always call status()

**Always call `status()` before the first `tts()` call in a session** to determine what is needed.

| `stage` | Meaning | What to do |
|---|---|---|
| `ready` | Fully installed, at least one voice model present | Proceed with `tts()` |
| `not-setup` | Piper not installed | Ask user for confirmation, then call `setup()` |
| `no-piper` | Venv exists but piper binary missing | Ask user for confirmation, then call `setup()` |
| `no-model` | Piper installed but no voice model downloaded | Follow Steps 3–5 of first-run flow above |

**IMPORTANT: Always ask the user for confirmation before calling `setup()`.**
It installs the `piper-tts` package from PyPI into a venv inside the skill directory.

## Usage
- Input: `text`, optional `format` (`"ogg"` or `"wav"`), optional `voice` (model stem), optional `lengthScale` (speech speed, default `1.0`)
- Output: path to generated file (usually `.ogg`)

## Controlling voice and language

**To list installed voices**, call `listVoices()` — returns stems of all installed `.onnx` models.
Never assume a fixed list; it varies per user and installation.

**Auto-detection (no `voice` param):**
The script detects language from the text using character and script analysis:
- Non-Latin scripts: Cyrillic (Russian, Ukrainian, Bulgarian), Greek, Arabic, Persian, Chinese, Japanese, Korean, Georgian
- Latin-script languages: Vietnamese, Polish, Romanian, Turkish, Czech, Slovak, Hungarian, Portuguese, Spanish, Catalan, German, Finnish, Scandinavian (Swedish, Norwegian, Danish), French, Italian
- Fallback: English keywords → first English model → any installed model

Auto-detection is best-effort. For reliable results with a specific language, always pass the `voice` parameter explicitly.

**Explicit override:** set `PIPER_VOICE_MODEL` env var to a full `.onnx` path (overrides everything).

**When the user requests a specific voice or language:**
1. Call `listVoices()` to see what is installed
2. Pass the matching stem as `voice` to `tts()`, e.g. `voice: "en_US-amy-medium"`
3. If the requested voice is not installed, offer to download it with `downloadVoices([stem])`

**To switch back to auto-detect**, omit the `voice` parameter.

## Downloading additional voices

The user may say things like *"I don't like this voice, use a female one"* or
*"Download a German voice"*. When this happens:
1. Find the model at https://github.com/rhasspy/piper/blob/master/VOICES.md
2. Confirm the stem (e.g. `de_DE-thorsten-medium`) and call `downloadVoices([stem])`
3. Generate a sample and send it to the user
4. Confirm with `listVoices()` — the new voice is immediately usable

## Removing voices

The user may say *"remove that voice"* or *"I don't need the German voice anymore"*. When this happens:
1. Call `listVoices()` to confirm which voices are installed
2. Confirm with the user which voice to remove
3. Call `removeVoice(stem)` — e.g. `removeVoice('de_DE-thorsten-medium')`
4. Returns `{ removed, filesDeleted }` on success
5. If the removed voice was the user's preferred voice, ask them to pick a new one

**Never remove the last remaining voice without warning the user that TTS will stop working.**

## Changing speech speed

The user may say things like *"speak faster"*, *"too slow"*, or *"speed it up"*. When this happens:
1. Ask what speed they want in %, or suggest: 125% (faster), 115%, 100% (normal), 80% (slower)
2. Convert their % to lengthScale: `lengthScale = 1 / (speed% / 100)`
3. Generate a short sample: `await tts({ text: '...', voice: 'current-voice', lengthScale: 0.8 })`
4. Send the sample and confirm
5. Offer to persist: *"Save this as default?"* — if yes, call `saveConfig({ lengthScale: 0.8 })`
6. Use the new `lengthScale` for all subsequent `tts()` calls in the session

## Where files are written
- `OPENCLAW_WORKSPACE/tts/` if `OPENCLAW_WORKSPACE` env var is set
- otherwise: `~/.openclaw/workspace/tts/`

## Dependencies
- `python3` (3.8+) — required for `setup()` to create the venv
- `ffmpeg` — for WAV → OGG/Opus conversion
- `espeak-ng` — system library used by Piper internally; `setup()` checks for it and warns if missing.
  Install: `sudo apt install espeak-ng` (Debian/Ubuntu), `sudo dnf install espeak-ng` (Fedora),
  `brew install espeak` (macOS)
- At least one Piper `.onnx` + `.onnx.json` voice model pair in the skill directory

## Platform support
- Linux x86_64: fully supported
- macOS x86_64 / arm64: fully supported
- Linux ARM: may require building piper-tts from source
- Windows: not supported

## Remove
```bash
rm -rf ~/.openclaw/skills/local-piper-tts-multilang-secure
```
This removes everything: skill code, venv, and all voice models.
