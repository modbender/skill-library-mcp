---
name: SunoMaker
description: Automated Suno AI Music Generation - Create professional songs without manual intervention. Headless browser automation for servers with Gemini 3.1 Pro integration.
metadata: {"openclaw": {"emoji": "🎵", "requires": {"bins": ["google-chrome", "Xvfb"]}, "model": "openrouter/google/gemini-3.1-pro-preview"}}
---

# 🎵 SunoMaker - Automated Suno AI Music Generation

Designed for **Linux servers without a graphical interface** (Headless). Uses **Xvfb Virtual Display** to run Chrome in GUI mode without a monitor, bypassing Google's anti-automation systems.

Two core functions: **Account Login** (via Google OAuth) and **Song Creation** (custom lyrics + style + download).

---

## 0. Prerequisite Check

Before any operation, the environment must be checked:

```bash
bash {baseDir}/suno-headless/check_env.sh
```

Return values:
- `0` = OK, logged in → songs can be created directly
- `1` = Dependencies missing → installation required
- `2` = Not logged in → start the login process

---

## 1. Install Dependencies (first time only)

### 1.1 System Dependencies

```bash
# Xvfb Virtual Display (core dependency for headless environments)
sudo apt update && sudo apt install -y xvfb

# Google Chrome Browser
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update && sudo apt install -y google-chrome-stable

# Fonts for various languages
sudo apt install -y fonts-noto-cjk
```

### 1.2 Python Dependencies

```bash
cd {baseDir}/suno-headless
pip3 install -r requirements.txt
playwright install
```

---

## 2. Login Process

**⚠️ Important: Never hardcode credentials in the code! Always ask the user.**

Two login methods are available:
- **Method A: Cookie Import (🌟 Recommended! Perfectly bypasses Google security checks)**
- **Method B: Direct Email/Password Login (can trigger Google security prompts)**

### 2.1 Method A: Cookie Import (Recommended)

The most stable login method for cloud servers. Completely bypasses Google's security checks.

**Steps:**

If login is required, explain to the user:

> 🍪 Recommended Cookie Import Method (bypasses Google security checks):
>
> **Step 1**: On your local computer (with a browser), run:
> ```bash
> pip install playwright && playwright install
> python3 export_cookies.py
> ```
> A browser window will open. Log in to Suno manually. After a successful login, cookies will be exported automatically.
>
> **Step 2**: Upload the cookie file to the server:
> ```bash
> scp <exported-cookie-file> user@server:/root/suno_cookie/suno_cookies.json
> ```
>
> **Step 3**: After uploading, perform the import.

After uploading, run the import (default path: `/root/suno_cookie/suno_cookies.json`):

```bash
cd {baseDir}/suno-headless
python3 suno_login.py --import-cookies
```

### 2.2 Method B: Email/Password Login

**⚠️ Caution: On cloud servers, this can trigger Google security prompts. Prefer Method A.**

If login is required, **always ask the user**:

> Suno.com login required (via Google account). Please provide:
> 1. **Gmail address**
> 2. **Gmail password**
>
> ⚠️ Credentials are only used for this login, not stored or shared with third parties.

After user input:

```bash
cd {baseDir}/suno-headless
python3 suno_login.py --email "<user-email>" --password "<user-password>"
```

**Headless Linux Mode Explanation**:
- The script automatically detects a GUI-free environment (no `$DISPLAY` variable)
- It automatically starts an Xvfb Virtual Display, simulating a display in memory
- Chrome runs in GUI mode (`headless=False`), but nothing is displayed on the screen
- This bypasses Google's headless browser detection

### 2.3 Check Login Status

```bash
cd {baseDir}/suno-headless
python3 suno_login.py --check-only
```

Exit codes: `0` = Logged in, `2` = Not logged in

### 2.4 Force Re-login

```bash
# Method A: Re-import cookies
cd {baseDir}/suno-headless
python3 suno_login.py --import-cookies "<new-cookie-file>"

# Method B: Re-enter email/password
cd {baseDir}/suno-headless
python3 suno_login.py --email "<email>" --password "<password>" --force-login
```

---

## 3. Create a Song

### 3.1 Prerequisites

1. Logged in (`suno_login.py --check-only` returns 0)
2. **Gemini API Key** required (for automatic hCaptcha solving)

### 3.2 Get a Gemini API Key

If the user does not have a Gemini API Key:

> When creating a song, Suno shows captchas. A Gemini API Key is required for automatic solving.
> 1. Visit https://aistudio.google.com/app/apikey
> 2. Click "Create API key"
> 3. Copy the generated key

Save it in an environment file:

```bash
mkdir -p ~/.suno
echo "GEMINI_API_KEY=<user-key>" > ~/.suno/.env
```

Or as an environment variable:

```bash
export GEMINI_API_KEY="<user-key>"
```

### 3.3 hCaptcha Compatibility Patch

Run this once before the first use (Suno uses its own hCaptcha domain, a patch is required):

```bash
cd {baseDir}/suno-headless
python3 patch_hcaptcha.py
```

### 3.4 Song Creation Command

```bash
cd {baseDir}/suno-headless
python3 suno_create_song.py \
  --lyrics "<lyrics-content>" \
  --style "<music-style-tags>" \
  --title "<song-title>" \
  --output-dir "<download-dir>"
```

Read lyrics from a file:

```bash
cd {baseDir}/suno-headless
python3 suno_create_song.py \
  --lyrics-file "<lyrics-file-path>" \
  --style "<music-style-tags>" \
  --title "<song-title>"
```

**Headless Mode Explanation**:
- `suno_create_song.py` automatically detects a GUI-free environment
- It automatically starts an Xvfb Virtual Display, running Chrome in GUI mode in the virtual display
- After the script finishes, the Virtual Display is automatically closed, no manual action needed

### 3.5 Parameter Explanation

| Parameter | Description | Required | Default Value |
|-----------|--------------|:------------:|--------------|
| `--lyrics` | Song lyrics (alternative to `--lyrics-file`) | ✅ | - |
| `--lyrics-file` | Path to the lyrics file (alternative to `--lyrics`) | ✅ | - |
| `--style` | Music style tags (English, comma-separated) | ❌ | `rock, electric guitar, energetic, male vocals` |
| `--title` | Song title | ❌ | `My Song` |
| `--output-dir` | MP3 download directory | ❌ | `{baseDir}/output_mp3` |
| `--gemini-key` | Gemini API Key (alternatively: environment variable or `~/.suno/.env`) | ❌ | Auto-Read |

### 3.6 Music Style Tags Reference

Common style tags (English, combinable):

- **Genres**: rock, pop, jazz, blues, electronic, hip-hop, R&B, classical, folk, metal, country, reggae, latin, indie
- **Instruments**: electric guitar, acoustic guitar, piano, synthesizer, drums, bass, violin, saxophone, trumpet
- **Mood**: energetic, emotional, melancholic, upbeat, dark, dreamy, aggressive, peaceful, romantic
- **Vocals**: male vocals, female vocals, choir, rap, whisper, powerful vocals, falsetto
- **Language**: german, english, french, spanish, chinese, japanese
- **Other**: fast tempo, slow tempo, instrumental, lo-fi, cinematic, epic

**Examples**:
- Rock: `rock, electric guitar, energetic, male vocals, english`
- Ballad: `pop, piano, emotional, female vocals, slow tempo, english`
- Electronic: `electronic, synthesizer, upbeat, fast tempo, dance`
- Hip-Hop: `hip-hop, rap, bass, drums, energetic, english`

---

## 4. Complete Example

### Example: Create a Rock Song on a Linux Server

```bash
# 1. Check environment (automatically detects Xvfb, Chrome, etc.)
bash {baseDir}/suno-headless/check_env.sh

# 2. If not logged in, use the cookie import method (recommended)
#    Step 1: Run export_cookies.py on the local computer
#    Step 2: scp <cookie-file> user@server:/root/suno_cookie/suno_cookies.json
#    Step 3: Import on the server (default: /root/suno_cookie/suno_cookies.json)
cd {baseDir}/suno-headless
python3 suno_login.py --import-cookies

# Or use the email/password method (can trigger Google security prompts)
# python3 suno_login.py --email "user@gmail.com" --password "password123"

# 3. Apply hCaptcha patch
python3 patch_hcaptcha.py

# 4. Create song (automatically with Xvfb Virtual Display)
python3 suno_create_song.py \
  --lyrics "The sun rises over the city
A new day is dawning
We walk through the streets
And sing our song" \
  --style "rock, electric guitar, energetic, male vocals, english" \
  --title "Morning Song Rock Version"
```

---

## 5. Differences from the Original Version

| Feature | suno (Original) | suno-headless (This Version) |
|---------|-----------------|-------------------------------|
| Target Environment | macOS / Linux with GUI | **Linux Server without GUI** |
| Display Mode | Real Chrome window | **Xvfb Virtual Display (RAM simulation)** |
| Additional Dependencies | None | `xvfb` + `PyVirtualDisplay` |
| Login Xvfb | ✅ Supported | ✅ Supported |
| Song Creation Xvfb | ❌ Not supported | ✅ **Supported** |
| Environment Check | Basic | **Incl. Xvfb/Chrome/Font Check** |

---

## 6. Technical Details

### Xvfb Virtual Display Solution

```
┌─────────────────────────────────────────┐
│          Linux Server (no monitor)      │
│                                         │
│  ┌─────────────┐    ┌────────────────┐  │
│  │   Xvfb      │    │  Chrome        │  │
│  │ (Virtual    │◄───│ (GUI Mode)     │  │
│  │  Display)   │    │ headless=False │  │
│  │ :99 1280x800│    └────────────────┘  │
│  └─────────────┘           │             │
│        ▲                   │             │
│        │              Automated          │
│   PyVirtualDisplay     Suno.com Control  │
│   Auto-Lifecycle            │             │
│        │                   ▼             │
│        │            ┌────────────────┐   │
│        │            │ Song Generation│   │
│        │            │ + Download     │   │
│        │            └────────────────┘   │
└────────┼────────────────────────────────┘
         │
         ▼
     Memory (RAM)
```

- **Why not headless=True?** Google OAuth detects headless browsers and blocks logins
- **Xvfb solution**: Creates a virtual X11 display in RAM, Chrome "thinks" there's a real GUI, so Google can't detect the automation
- **Auto-detection**: The script checks the `$DISPLAY` environment variable and starts Xvfb automatically if no GUI is present
- **Resources**: Xvfb uses minimal RAM and is automatically released after the script finishes

### Login Solution
- Playwright + Real Chrome browser (`channel='chrome'`)
- `persistent context` maintains browser state (cookies, localStorage)
- `headless=False` + Xvfb Virtual Display bypasses Google's anti-automation
- After the first login, the session is maintained through the persistent context

### Song Creation Solution
- Browser automation controls the suno.com/create page
- hcaptcha-challenger + Gemini API solves hCaptcha automatically
- New clip ID is obtained by intercepting browser network responses
- Suno's internal API (`studio-api.prod.suno.com`) polls the song generation status
- Automatic MP3 download upon completion

### File Structure

```
suno-headless/
├── suno_login.py          # Login tool (Google OAuth / Cookie Import + Xvfb)
├── suno_create_song.py    # Song creation + download (Xvfb support)
├── export_cookies.py      # Cookie export tool (run on local computer)
├── patch_hcaptcha.py      # hCaptcha domain compatibility patch
├── check_env.sh           # Environment check (incl. Xvfb/Chrome check)
├── requirements.txt       # Python dependencies (incl. PyVirtualDisplay)
└── SKILL.md               # This documentation
```

---

## 7. Important Notes

1. **Never hardcode credentials** — Always ask the user (prefer cookie import)
2. **Xvfb must be installed** — `sudo apt install -y xvfb`, otherwise it won't run in a headless environment
3. **Real Chrome is required** — Playwright's own Chromium can be detected by Google
4. Suno Free accounts have a daily point limit, approx. 100 points per song
5. Song generation typically takes 1-3 minutes
6. Each creation generates 2 different song versions
7. If Google login is rejected: wait 10-30 minutes, then try again
8. Gemini API Free limit: 15 Requests/Minute, 1500/Day
9. hCaptcha may take several attempts, success rate depends on Gemini's image recognition

## 8. Troubleshooting

```bash
# Check environment (incl. Xvfb status)
bash {baseDir}/suno-headless/check_env.sh

# Test Xvfb manually
Xvfb :99 -screen 0 1280x800x24 &
DISPLAY=:99 google-chrome --no-sandbox --version
kill %1

# View login screenshots
ls -la /tmp/suno_debug_*.png

# Check persistent context
ls -la ~/.suno/chrome_gui_profile/

# View cookies
python3 -c "import json; d=json.load(open('$HOME/.suno/cookies.json')); print(f'{len(d)} cookies')"

# Check Gemini API Key
cat ~/.suno/.env

# View downloaded songs
ls -la {baseDir}/output_mp3/
```
