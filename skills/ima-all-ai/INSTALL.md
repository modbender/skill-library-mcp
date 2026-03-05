# Installation Guide — ima-all-ai

## Prerequisites

### 1. Python Dependencies

This skill requires Python 3.7+ and the `requests` library.

**Install dependencies:**
```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install requests>=2.25.0
```

### 2. IMA API Key

**Required environment variable:** `IMA_API_KEY`

1. Get your API key at https://imastudio.com
2. Set the environment variable:

**For OpenClaw agents:**
```json
{
  "env": {
    "IMA_API_KEY": "ima_your_key_here"
  }
}
```

**For terminal/CLI:**
```bash
export IMA_API_KEY=ima_your_key_here
```

**For persistent setup (add to ~/.bashrc or ~/.zshrc):**
```bash
echo 'export IMA_API_KEY=ima_your_key_here' >> ~/.bashrc
source ~/.bashrc
```

---

## File System Access

### What This Skill Reads/Writes

This skill stores user preferences and logs locally:

| Path | Purpose | Auto-created | User Control |
|------|---------|--------------|--------------|
| `~/.openclaw/memory/ima_prefs.json` | User model preferences | ✅ Yes | Can be deleted anytime |
| `~/.openclaw/logs/ima_skills/` | Generation logs (7-day rotation) | ✅ Yes | Auto-cleanup after 7 days |

### Why These Files?

- **Preferences** (`ima_prefs.json`): Remembers your favorite models for images, videos, and music
- **Logs**: Helps debug issues and track API usage across all content types

### Privacy & Security

- ✅ **No API keys stored** — only model preferences (e.g., "last used: SeeDream 4.5")
- ✅ **No personal data** — only timestamps and model IDs
- ✅ **Local only** — never sent to external servers
- ✅ **User-deletable** — you can delete these files anytime without breaking the skill

### Disable Preferences/Logs (Optional)

If you don't want local file storage:

1. Remove write permissions:
   ```bash
   chmod -w ~/.openclaw/memory/ima_prefs.json
   chmod -w ~/.openclaw/logs/ima_skills/
   ```

2. The skill will fall back to default models (no saved preferences)

---

## Permissions Summary

This skill requires:

| Permission | Purpose | Justification |
|------------|---------|---------------|
| **network_access** | Call IMA Open API | Required to generate images, videos, and music |
| **file_read_write** | Store preferences & logs | Optional but recommended for better UX |
| **IMA_API_KEY** | Authenticate with IMA API | Required for all API calls |

---

## Installation Steps

### Step 1: Install from ClawHub

```bash
clawhub install ima-all-ai
```

Or manually:
```bash
git clone https://git.joyme.sg/imagent/skills/ima-all-ai.git
cd ima-all-ai
pip install -r requirements.txt
```

### Step 2: Set API Key

```bash
export IMA_API_KEY=ima_your_key_here
```

### Step 3: Test Installation

**Test image generation:**
```bash
cd scripts
python3 ima_create.py \
  --api-key $IMA_API_KEY \
  --task-type text_to_image \
  --model-id doubao-seedream-4.5 \
  --prompt "a beautiful sunset over mountains" \
  --output-json
```

**Test video generation:**
```bash
python3 ima_create.py \
  --api-key $IMA_API_KEY \
  --task-type text_to_video \
  --model-id wan2.6-t2v \
  --prompt "a cat playing with yarn" \
  --output-json
```

**Test music generation:**
```bash
python3 ima_create.py \
  --api-key $IMA_API_KEY \
  --task-type text_to_music \
  --model-id sonic \
  --prompt "upbeat lo-fi hip hop, 90 BPM" \
  --output-json
```

Expected output (JSON):
```json
{
  "task_id": "task_xxx",
  "status": "success",
  "url": "https://...",
  "media_type": "image|video|music",
  "model": "...",
  "cost": 5
}
```

---

## Troubleshooting

### Error: "requests not installed"

**Solution:**
```bash
pip install requests
```

### Error: "API key not found"

**Solution:**
```bash
export IMA_API_KEY=ima_your_key_here
```

Verify:
```bash
echo $IMA_API_KEY
```

### Error: "Permission denied" when writing to ~/.openclaw

**Solution:**
```bash
mkdir -p ~/.openclaw/memory ~/.openclaw/logs/ima_skills
chmod 755 ~/.openclaw/memory ~/.openclaw/logs/ima_skills
```

### Error: "API call failed: 401 Unauthorized"

**Causes:**
- Invalid API key
- Expired API key
- Incorrect API key format (must start with `ima_`)

**Solution:**
1. Verify your API key at https://imastudio.com
2. Check the format: `ima_xxx...`
3. Regenerate if expired

---

## Uninstallation

### Remove Skill

```bash
clawhub uninstall ima-all-ai
```

### Clean Up Files (Optional)

```bash
# Remove preferences and logs
rm -rf ~/.openclaw/memory/ima_prefs.json
rm -rf ~/.openclaw/logs/ima_skills/

# Remove Python dependencies (if not used by other skills)
pip uninstall requests
```

---

## Security Best Practices

1. **API Key Management**
   - Never commit API keys to Git
   - Use environment variables
   - Rotate keys periodically

2. **File Permissions**
   - Keep ~/.openclaw readable only by your user:
     ```bash
     chmod 700 ~/.openclaw
     ```

3. **Isolated Testing**
   - Test with a limited-scope API key first
   - Use a separate user account for skill testing

4. **Code Review**
   - Review `scripts/ima_create.py` to verify endpoints
   - Confirm it calls only IMA-owned domains:
     - `api.imastudio.com` (main API)
     - `imapi.liveme.com` (upload service, for image/video tasks)

5. **Security Checklist (Before First Use)**
   - [ ] Verify DNS resolution: `dig api.imastudio.com` and `dig imapi.liveme.com`
   - [ ] Code review: Inspect `scripts/ima_create.py` for network calls
   - [ ] Use scoped API key: Test with limited-permissions key first
   - [ ] Monitor network: Run `sudo tcpdump -i any -n 'host api.imastudio.com or host imapi.liveme.com'` during test
   - [ ] Review `SECURITY.md`: Understand dual-domain architecture and hardcoded `APP_KEY`
   - [ ] Set up key rotation: Plan to regenerate API key monthly

---

## Support

- **Issues**: https://git.joyme.sg/imagent/skills/ima-all-ai/-/issues
- **Documentation**: See [SKILL.md](SKILL.md)
- **IMA API**: https://imastudio.com

---

**Installation complete! Start generating images, videos, and music 🎨🎬🎵**

## Prerequisites

### 1. Python Dependencies

This skill requires Python 3.7+ and the `requests` library.

**Install dependencies:**
```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install requests>=2.25.0
```

### 2. IMA API Key

**Required environment variable:** `IMA_API_KEY`

1. Get your API key at https://imastudio.com
2. Set the environment variable:

**For OpenClaw agents:**
```json
{
  "env": {
    "IMA_API_KEY": "ima_your_key_here"
  }
}
```

**For terminal/CLI:**
```bash
export IMA_API_KEY=ima_your_key_here
```

**For persistent setup (add to ~/.bashrc or ~/.zshrc):**
```bash
echo 'export IMA_API_KEY=ima_your_key_here' >> ~/.bashrc
source ~/.bashrc
```

---

## File System Access

### What This Skill Reads/Writes

This skill stores user preferences and logs locally:

| Path | Purpose | Auto-created | User Control |
|------|---------|--------------|--------------|
| `~/.openclaw/memory/ima_prefs.json` | User model preferences | ✅ Yes | Can be deleted anytime |
| `~/.openclaw/logs/ima_skills/` | Generation logs (7-day rotation) | ✅ Yes | Auto-cleanup after 7 days |

### Why These Files?

- **Preferences** (`ima_prefs.json`): Remembers your favorite models so you don't have to specify them every time
- **Logs**: Helps debug issues and track API usage

### Privacy & Security

- ✅ **No API keys stored** — only model preferences (e.g., "last used: Suno")
- ✅ **No personal data** — only timestamps and model IDs
- ✅ **Local only** — never sent to external servers
- ✅ **User-deletable** — you can delete these files anytime without breaking the skill

### Disable Preferences/Logs (Optional)

If you don't want local file storage:

1. Remove write permissions:
   ```bash
   chmod -w ~/.openclaw/memory/ima_prefs.json
   chmod -w ~/.openclaw/logs/ima_skills/
   ```

2. The skill will fall back to default models (no saved preferences)

---

## Permissions Summary

This skill requires:

| Permission | Purpose | Justification |
|------------|---------|---------------|
| **network_access** | Call IMA Open API | Required to generate music |
| **file_read_write** | Store preferences & logs | Optional but recommended for better UX |
| **IMA_API_KEY** | Authenticate with IMA API | Required for all API calls |

---

## Installation Steps

### Step 1: Install from ClawHub

```bash
clawhub install ima-voice-ai
```

Or manually:
```bash
git clone https://git.joyme.sg/imagent/skills/ima-voice-ai.git
cd ima-voice-ai
pip install -r requirements.txt
```

### Step 2: Set API Key

```bash
export IMA_API_KEY=ima_your_key_here
```

### Step 3: Test Installation

```bash
cd scripts
python3 ima_voice_create.py \
  --api-key $IMA_API_KEY \
  --model-id sonic \
  --prompt "upbeat lo-fi hip hop, 90 BPM, no vocals" \
  --output-json
```

Expected output:
```json
{
  "task_id": "task_xxx",
  "status": "success",
  "url": "https://ws.esxscloud.com/.../audio.mp3",
  "duration": "60s",
  "model": "Suno sonic-v5",
  "cost": 25
}
```

---

## Troubleshooting

### Error: "requests not installed"

**Solution:**
```bash
pip install requests
```

### Error: "API key not found"

**Solution:**
```bash
export IMA_API_KEY=ima_your_key_here
```

Verify:
```bash
echo $IMA_API_KEY
```

### Error: "Permission denied" when writing to ~/.openclaw

**Solution:**
```bash
mkdir -p ~/.openclaw/memory ~/.openclaw/logs/ima_skills
chmod 755 ~/.openclaw/memory ~/.openclaw/logs/ima_skills
```

### Error: "API call failed: 401 Unauthorized"

**Causes:**
- Invalid API key
- Expired API key
- Incorrect API key format (must start with `ima_`)

**Solution:**
1. Verify your API key at https://imastudio.com
2. Check the format: `ima_xxx...`
3. Regenerate if expired

---

## Uninstallation

### Remove Skill

```bash
clawhub uninstall ima-voice-ai
```

### Clean Up Files (Optional)

```bash
# Remove preferences and logs
rm -rf ~/.openclaw/memory/ima_prefs.json
rm -rf ~/.openclaw/logs/ima_skills/

# Remove Python dependencies (if not used by other skills)
pip uninstall requests
```

---

## Security Best Practices

1. **API Key Management**
   - Never commit API keys to Git
   - Use environment variables
   - Rotate keys periodically

2. **File Permissions**
   - Keep ~/.openclaw readable only by your user:
     ```bash
     chmod 700 ~/.openclaw
     ```

3. **Isolated Testing**
   - Test with a limited-scope API key first
   - Use a separate user account for skill testing

4. **Code Review**
   - Review `scripts/ima_create.py` to verify endpoints
   - Confirm it calls only IMA-owned domains:
     - `api.imastudio.com` (main API)
     - `imapi.liveme.com` (upload service, for image/video tasks)

5. **Security Checklist (Before First Use)**
   - [ ] Verify DNS resolution: `dig api.imastudio.com` and `dig imapi.liveme.com`
   - [ ] Code review: Inspect `scripts/ima_create.py` for network calls
   - [ ] Use scoped API key: Test with limited-permissions key first
   - [ ] Monitor network: Run `sudo tcpdump -i any -n 'host api.imastudio.com or host imapi.liveme.com'` during test
   - [ ] Review `SECURITY.md`: Understand dual-domain architecture and hardcoded `APP_KEY`
   - [ ] Set up key rotation: Plan to regenerate API key monthly

---

## Support

- **Issues**: https://git.joyme.sg/imagent/skills/ima-voice-ai/-/issues
- **Documentation**: See [SKILL.md](SKILL.md)
- **IMA API**: https://imastudio.com

---

**Installation complete! Start generating music 🎵**
