# Scrapling Skill - Installation Guide

## Skill Location

The skill has been built and is located at:
```
~/.openclaw/skills/scrapling/
```

## Deliverable Format

**The deliverable is a FOLDER**, not a single file. OpenClaw skills are directory structures containing:
- `SKILL.md` - Instructions for AI agents
- `scrape.py` - Main executable script
- `requirements.txt` - Python dependencies
- `skill.json` - Metadata for the Gateway UI
- `README.md` - Human-readable documentation
- `examples/` - Example scripts

## Installation Methods

### Method 1: Via OpenClaw Gateway UI (Recommended)

**Step 1: Check if ClawHub CLI is installed**
```bash
which clawhub
# or
npm list -g clawhub
```

If not installed:
```bash
npm install -g clawhub
```

**Step 2: Publish to ClawHub (or use local)**

You have two options:

**Option A: Publish to ClawHub.com (public)**
```bash
cd ~/.openclaw/skills/scrapling

# Initialize (creates .clawhub metadata)
clawhub init

# Publish
clawhub publish

# This uploads your skill to clawhub.com and gives you a skill ID
```

**Option B: Use Local/Private Installation**

Since the skill is already in the standard OpenClaw skills directory (`~/.openclaw/skills/`), OpenClaw should auto-detect it.

**Step 3: Access Gateway UI**

1. Open OpenClaw Gateway UI
   - If running locally: Check `openclaw status` for Gateway URL
   - Usually: http://localhost:PORT (port varies)

2. Navigate to **Skills** section

3. You should see one of:
   - **"Scrapling Web Scraper"** listed (if auto-detected from local skills dir)
   - **Search button** to find published skills on ClawHub
   - **"Install from folder"** or **"Upload skill"** option

4. Click **Install** or **Enable**

5. Wait for dependencies to install:
   - Python packages (~30 seconds)
   - Browser downloads (~2-5 minutes, 500MB)
   - Progress shown in UI

**Step 4: Verify Installation**

Run test command:
```bash
cd ~/.openclaw/skills/scrapling
python scrape.py --url https://quotes.toscrape.com --selector .quote --extract text
```

Should output quotes from the test site.

---

### Method 2: Manual Installation (CLI)

If you don't want to use the Gateway UI:

**Step 1: Navigate to skill directory**
```bash
cd ~/.openclaw/skills/scrapling
```

**Step 2: Install Python dependencies**
```bash
pip install -r requirements.txt
```

**Step 3: Install browsers (required for stealth/dynamic modes)**
```bash
scrapling install
```

This downloads Chromium and required system libraries (~500MB).

**Step 4: Test the skill**
```bash
# Basic test
python scrape.py --url https://quotes.toscrape.com --selector .quote::text

# Stealth mode test (Cloudflare bypass)
python scrape.py --url https://nopecha.com/demo/cloudflare --stealth --selector '#padded_content'

# Dynamic mode test (JavaScript)
python scrape.py --url https://quotes.toscrape.com/js/ --dynamic --selector .quote::text
```

**Step 5: Make it available to OpenClaw**

The skill is already in the standard location (`~/.openclaw/skills/scrapling/`), so OpenClaw should auto-detect it. To manually register:

```bash
# Restart OpenClaw gateway
openclaw gateway restart

# Or use the skill directly in chat
# Just reference it: "Use the scrapling skill to scrape https://example.com"
```

---

### Method 3: Share/Distribute the Skill

To share this skill with others or install on another machine:

**Step 1: Create a tarball**
```bash
cd ~/.openclaw/skills
tar -czf scrapling-skill.tar.gz scrapling/
```

**Step 2: Transfer the tarball**
Upload to GitHub, email, cloud storage, etc.

**Step 3: Install on target machine**
```bash
# Extract to OpenClaw skills directory
cd ~/.openclaw/skills
tar -xzf scrapling-skill.tar.gz

# Install dependencies
cd scrapling
pip install -r requirements.txt
scrapling install
```

**Alternatively: Create a ZIP file**
```bash
cd ~/.openclaw/skills
zip -r scrapling-skill.zip scrapling/
```

---

## Gateway UI Installation - Detailed Steps

### Finding the Gateway UI

1. **Check OpenClaw status:**
```bash
openclaw status
```

Look for output like:
```
Gateway: running
URL: http://localhost:3939
```

2. **Open in browser:**
```
http://localhost:3939
```

3. **Authentication:**
- If prompted, use your OpenClaw credentials
- Default setup usually doesn't require auth for local access

### Installing the Skill

**Scenario A: Skill Auto-Detected**

If OpenClaw auto-detects the skill in `~/.openclaw/skills/`:

1. Navigate to **Skills** tab
2. Find **"Scrapling Web Scraper"** in the list
3. Click **Enable** or **Activate**
4. Click **Install Dependencies** (if prompted)
5. Wait for installation (progress bar shown)
6. Status changes to **"Installed"** or **"Active"**

**Scenario B: Manual Upload**

If there's an upload option:

1. Create the tarball:
```bash
cd ~/.openclaw/skills
tar -czf /tmp/scrapling-skill.tar.gz scrapling/
```

2. In Gateway UI:
   - Click **"Upload Skill"** or **"Install from file"**
   - Select `/tmp/scrapling-skill.tar.gz`
   - Click **Upload**

3. Wait for:
   - File upload
   - Extraction
   - Dependency installation

**Scenario C: Install from ClawHub**

If you published to ClawHub:

1. In Gateway UI, click **"Browse Skills"** or **"ClawHub"**
2. Search for **"scrapling"** or your username
3. Click **Install**
4. Accept permissions (if asked)
5. Wait for download + installation

---

## Post-Installation

### Verify Installation

**Method 1: CLI Test**
```bash
cd ~/.openclaw/skills/scrapling
python scrape.py --url https://quotes.toscrape.com --selector .quote --output /tmp/test.json
cat /tmp/test.json
```

**Method 2: In OpenClaw Chat**

Ask the agent:
```
Use the scrapling skill to scrape https://news.ycombinator.com and extract the top story titles
```

The agent should:
1. Read `SKILL.md`
2. Run `scrape.py` with appropriate flags
3. Return the results

**Method 3: Check Gateway UI**

- Navigate to Skills section
- **Scrapling Web Scraper** should show status: **Installed** ✅
- Dependencies should show: **Installed** ✅

### First Use Example

In OpenClaw chat:
```
I need to scrape https://quotes.toscrape.com and extract all the quotes and authors. 
Use the scrapling skill to do this.
```

Expected agent behavior:
1. Read `~/.openclaw/skills/scrapling/SKILL.md`
2. Execute command:
```bash
python ~/.openclaw/skills/scrapling/scrape.py \
  --url "https://quotes.toscrape.com" \
  --selector ".quote" \
  --fields "text:.text::text,author:.author::text" \
  --output quotes.json
```
3. Return the JSON results

---

## Troubleshooting

### Issue: "Scrapling not found"

**Solution:**
```bash
cd ~/.openclaw/skills/scrapling
pip install -r requirements.txt
```

### Issue: "Browser not found" or "Playwright error"

**Solution:**
```bash
scrapling install
# This downloads Chromium and dependencies
```

### Issue: "Permission denied" when running scrape.py

**Solution:**
```bash
chmod +x ~/.openclaw/skills/scrapling/scrape.py
```

### Issue: Skill doesn't appear in Gateway UI

**Solution 1: Restart Gateway**
```bash
openclaw gateway restart
```

**Solution 2: Check skill location**
```bash
# Skill must be in:
~/.openclaw/skills/scrapling/

# Verify:
ls -la ~/.openclaw/skills/scrapling/SKILL.md
```

**Solution 3: Check skill.json format**
```bash
# Validate JSON:
cat ~/.openclaw/skills/scrapling/skill.json | python -m json.tool
```

### Issue: Installation hangs at "Installing browsers"

This is normal! Browser download is ~500MB and can take 2-10 minutes depending on connection.

**Monitor progress:**
```bash
# In another terminal:
du -sh ~/.cache/ms-playwright  # Shows download size
```

---

## System Requirements

- **Python:** 3.10 or higher
- **Disk Space:** ~1GB
  - Dependencies: ~100MB
  - Browsers: ~500MB
  - Cache: ~100MB
- **RAM:** 2GB minimum (4GB recommended for stealth/dynamic mode)
- **Network:** Required for first-time browser download

---

## Uninstalling

**Remove skill:**
```bash
rm -rf ~/.openclaw/skills/scrapling
```

**Remove dependencies (optional):**
```bash
pip uninstall scrapling -y
```

**Remove browsers (optional):**
```bash
rm -rf ~/.cache/ms-playwright
```

---

## Next Steps

After installation:

1. **Read SKILL.md** - Full documentation of all features
2. **Run examples** - Try the scripts in `examples/` directory
3. **Test in chat** - Ask OpenClaw to scrape websites
4. **Build custom scrapers** - Use the skill as a foundation

---

## Support

- **Scrapling Library:** https://scrapling.readthedocs.io
- **GitHub Issues:** https://github.com/D4Vinci/Scrapling/issues
- **Discord:** https://discord.gg/EMgGbDceNQ

---

**Skill built successfully!** ✅

Location: `~/.openclaw/skills/scrapling/`
