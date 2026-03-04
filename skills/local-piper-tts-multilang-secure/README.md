# local-piper-tts-multilang-secure

Fully offline text-to-speech via Piper TTS. Self-contained setup, automatic language detection for 20+ languages, and per-call voice selection. Writes audio files into the OpenClaw workspace for easy attachment and sending.

## Features

- Fully offline — no API keys required
- Self-contained setup — `setup()` installs Piper into an isolated venv, no system packages modified
- Automatic language detection for 20+ languages with English as default
- Per-call voice and speed selection: pass `voice: "voice-stem"` and `lengthScale: 0.85` to `tts()`
- Dynamic voice discovery: `listVoices()` returns whatever is installed — no hardcoded assumptions
- On-demand voice download: `downloadVoices(["en_US-ryan-medium", ...])` fetches models from HuggingFace
- Voice removal: `removeVoice("en_US-ryan-medium")` deletes models you no longer need
- Extensible: add any language by dropping in a Piper `.onnx` model
- Writes outputs into the OpenClaw workspace for easy attachment
- Default output: OGG/Opus (compact, widely compatible)

## Requirements

- `python3` (3.8+) — for the one-time `setup()` step
- `ffmpeg` — for WAV → OGG/Opus conversion
- `espeak-ng` — system library used by Piper for phonemization (see note below)

No API keys. No system-wide package installation. Everything stays inside the skill directory.

## Platform support

| Platform | Status |
|---|---|
| Linux x86_64 | Fully supported |
| macOS x86_64 / arm64 | Fully supported |
| Linux ARM (Raspberry Pi, etc.) | May require building piper-tts from source |
| Windows | Not supported (bash dependency) |

## espeak-ng

Piper uses `espeak-ng` internally for text-to-phoneme conversion. On many systems it is
already installed. `setup()` checks for it and warns if missing. If needed, install via
your package manager:

```bash
# Debian / Ubuntu
sudo apt install espeak-ng

# Fedora / RHEL
sudo dnf install espeak-ng

# macOS
brew install espeak
```

After installing, TTS should work without re-running `setup()`.

## Installation

```bash
cp -r local-piper-tts-multilang-secure ~/.openclaw/skills/local-piper-tts-multilang-secure
```

Then ask your agent to set it up — it will call `setup()` after asking for your confirmation.
`setup()` is a one-time operation that:
1. Creates a Python venv inside the skill directory
2. Installs `piper-tts` from PyPI into that venv
3. Checks for `espeak-ng` and warns if missing

## First run

After installation, tell your agent:
> "Set up the local TTS skill"

The agent will:
1. Call `status()` and explain what needs to be done
2. Ask for confirmation, then run `setup()`
3. Offer to download English voice models (ryan-medium and/or amy-medium)
4. Ask if you need any other languages (German, French, Spanish, Polish, Italian, Russian, …)
5. Download your chosen voices, generate a short sample for each, and send them to you
6. Ask which voice you prefer
7. Ask about preferred speech speed in % (default 100% = normal, e.g. 125% = faster), play a sample at your chosen speed

## Voice models

The skill ships with no voice models — you choose what to install.
English is recommended as a baseline. Browse available models at:
https://github.com/rhasspy/piper/blob/master/VOICES.md

### Recommended English defaults

| Stem | Gender | Size |
|---|---|---|
| `en_US-ryan-medium` | Male, American | ~65 MB |
| `en_US-amy-medium` | Female, American | ~65 MB |

Download programmatically:
```js
const { downloadVoices } = require('./index');
await downloadVoices(['en_US-ryan-medium', 'en_US-amy-medium']);
```

Or just ask your agent: *"Download the English voices"* — it will handle everything including
playing samples so you can choose.

To see what is installed:
```js
require('./index').listVoices()
// ["en_US-ryan-medium", "de_DE-thorsten-medium", ...]
```

Or ask your agent: *"What voices do you have available?"*

## Changing voices

Just tell your agent:
- *"I don't like this voice, use a different one"*
- *"Download a female English voice"*
- *"Switch to British accent"*
- *"Get a German voice"*

The agent will check what is installed, download what is needed, play a sample, and use the right model.

## Removing voices

Just tell your agent:
- *"Remove the German voice"*
- *"Delete the Ryan voice, I only use Amy"*
- *"Clean up unused voices"*

The agent will confirm which voice to remove and delete the model files. Each voice takes ~65 MB, so removing unused ones can free significant disk space.

Programmatically:
```js
require('./index').removeVoice('en_US-ryan-medium')
// { removed: 'en_US-ryan-medium', filesDeleted: ['en_US-ryan-medium.onnx', 'en_US-ryan-medium.onnx.json'] }
```

## Changing speech speed

Just tell your agent:
- *"Speak faster"*
- *"Too slow, speed it up"*
- *"Use 120% speed"*
- *"Back to normal"*

The agent will suggest options in %, play a sample, and apply the change. Speed is expressed as a percentage — 100% is normal. `lengthScale` is the inverse: `lengthScale = 1 / (speed% / 100)`.

| Speed | lengthScale |
|---|---|
| 125% (fast) | 0.8 |
| 115% | 0.87 |
| 100% (normal) | 1.0 |
| 80% (slow) | 1.25 |

Default is 100% (lengthScale 1.0).

To persist your preferred speed across sessions, ask your agent to save it — it will call `saveConfig({ lengthScale: 0.8 })` which writes to `config.json` inside the skill directory. The skill picks this up automatically on every subsequent call — no need to repeat your preference each session.

## Language detection

Detection logic lives in `piper-tts.sh` and works automatically based on character and script analysis:

**Non-Latin scripts (unambiguous):**
- Cyrillic → Russian (with Ukrainian detection via і/ї/є/ґ), Bulgarian, Serbian
- Greek → Greek
- Arabic script → Arabic (with Persian detection via پ/چ/ژ/گ)
- CJK ideographs → Chinese (with Japanese detection via Hiragana/Katakana)
- Hangul → Korean
- Georgian → Georgian

**Latin-script languages (by distinctive characters):**
- Vietnamese (ăơưđ)
- Polish (ąćęłńśźż)
- Romanian (șț)
- Turkish (ğışİ)
- Czech/Slovak (ěščřžďťň, ů for Czech)
- Hungarian (őű)
- Portuguese (ãõ)
- Spanish (ñ¿¡)
- Catalan (l·l)
- German (ß, äöü)
- Finnish (äö, when no Scandinavian markers)
- Scandinavian — Norwegian/Danish (æø), Swedish (åäö)
- French (œçèêëïî)
- Italian (àèìòù)

**Fallback:** English keywords → first English model → any installed model.

No detection needed when `voice` is specified explicitly.

## Security

- `execFile` throughout — no shell interpreter, user text cannot inject commands
- Voice path validated to stay within the skill directory — no path traversal
- Output filename sanitised with `path.basename()` — no directory traversal
- HTTPS-only downloads — non-HTTPS URLs and redirects are rejected
- URL path components validated against expected patterns
- Atomic downloads (write to .tmp, rename on success) — no corrupt models from interrupted downloads
- Piper installed in isolated venv — no system Python packages touched
- No credentials, no network calls during TTS (only during setup and voice downloads)

## Remove

```bash
rm -rf ~/.openclaw/skills/local-piper-tts-multilang-secure
```

This removes everything: skill code, venv, and all voice models.

## License

MIT
