# Morelogin Skill Installation and Configuration Guide

## 📋 Prerequisites

Before you begin, ensure the following:

### Required
- ✅ Node.js 18 or higher
- ✅ npm package manager
- ✅ Morelogin desktop app (installed and logged in)
- ✅ At least one browser profile

### Optional
- Puppeteer or Playwright (for automation scripts)
- Git (for version control)

---

## 🔧 Installation Steps

### Step 1: Verify Node.js Installation

```bash
node --version
# Should show v18.x.x or higher

npm --version
# Should show 8.x.x or higher
```

If Node.js is not installed, go to [nodejs.org](https://nodejs.org/) to download.

### Step 2: Install Morelogin Desktop App

**macOS:**
```bash
# Method 1: Download from official site
open https://morelogin.com/download

# Method 2: Use Homebrew (if available)
brew install --cask morelogin
```

**Windows:**
1. Visit https://morelogin.com/download
2. Download the Windows installer
3. Run the installer

**Linux:**
```bash
# Download AppImage
wget https://morelogin.com/download/linux-amd64.AppImage
chmod +x morelogin-linux-amd64.AppImage
./morelogin-linux-amd64.AppImage
```

### Step 3: Configure Morelogin

1. **Start the Morelogin app**
2. **Log in** (register a new account or log in to an existing one)
3. **Create a browser profile**:
   - Click "Create Profile"
   - Select browser type (Chrome recommended)
   - Configure proxy (optional)
   - Save the profile

4. **Enable API access** (if needed):
   - Open Morelogin settings
   - Find "API" or "Developer options"
   - Enable local API service
   - Note the API port (default: 5050)

### Step 4: Install Skill Dependencies

```bash
# Navigate to the skill directory
cd ~/.openclaw/workspace/skills/morelogin

# Install dependencies
npm install
```

### Step 5: Install Automation Tools (Optional)

**Using Puppeteer:**
```bash
npm install puppeteer-core
```

**Using Playwright:**
```bash
npm install playwright
# Install browsers
npx playwright install chromium
```

### Step 6: Test Installation

```bash
# Test CLI tool
node bin/morelogin.js help

# Test API connection
node bin/morelogin.js browser list --page 1 --page-size 1

# List profiles
node bin/morelogin.js list
```

---

## ⚙️ Configuration

### Configure Morelogin CLI

Run the setup wizard:

```bash
node bin/morelogin.js setup
```

Follow the prompts to configure:
- Morelogin local API address (default: http://localhost:5050)
- Default CDP port (default: 9222)

### Configure TOOLS.md

Edit `~/.openclaw/workspace/TOOLS.md` and add:

```markdown
### Morelogin

- Install Path: /Applications/Morelogin.app (macOS)
- Local API: http://localhost:5050
- Default CDP Port: 9222
- Profiles:
  - work-account: abc123def (US IP)
  - social-media: xyz789ghi (EU IP)
```

### Configure Environment Variables (Optional)

Add to `~/.bashrc` or `~/.zshrc`:

```bash
export MORELOGIN_API_URL=http://localhost:40000
export MORELOGIN_CDP_PORT=9222
export MORELOGIN_DEFAULT_PROFILE=abc123def
```

---

## 🧪 Verify Installation

### Test 1: List Profiles

```bash
cd ~/.openclaw/workspace/skills/morelogin
node bin/morelogin.js list
```

**Expected output:**
```
📋 Fetching profile list...

Found X profiles:

1. Profile name (ID: xxxxx)
   Status: ⚫ Stopped
   Browser: Chrome
```

### Test 2: Start Profile

```bash
node bin/morelogin.js start --profile-id <your_profile_id>
```

**Expected output:**
```
🚀 Starting profile: xxxxx
✅ Profile started
🔗 CDP address: http://localhost:9222
```

### Test 3: Connect to CDP

```bash
node bin/morelogin.js connect --profile-id <your_profile_id>
```

**Expected output:**
```
🔌 Connecting to CDP: xxxxx
✅ CDP address: http://localhost:9222

Usage examples:
  Puppeteer: puppeteer.connect({ browserURL: 'http://localhost:9222' })
  Playwright: playwright.chromium.connectOverCDP('http://localhost:9222')
```

### Test 4: Run Example Script

```bash
# Ensure profile is running
node examples/puppeteer-example.js
```

**Expected output:**
```
🚀 Connecting to Morelogin browser...

✅ Connected!
Browser version: Chrome/xxx.x.x.xxx

📍 Navigating to example.com...
📸 Taking screenshot...
✅ Screenshot saved: screenshot-example.png
Page title: Example Domain

✅ All examples completed!
```

---

## 🐛 Troubleshooting

### Issue 1: "Cannot find module"

**Error:**
```
Error: Cannot find module 'xxx'
```

**Solution:**
```bash
cd ~/.openclaw/workspace/skills/morelogin
npm install
```

### Issue 2: "ECONNREFUSED"

**Error:**
```
Error: connect ECONNREFUSED 127.0.0.1:5050
```

**Solution:**
1. Ensure the Morelogin desktop app is running
2. Check if Morelogin is logged in
3. Verify local API is enabled
4. Try restarting the Morelogin app

### Issue 3: "Port already in use"

**Error:**
```
Error: Port 9222 is already in use
```

**Solution:**
```bash
# Find process using the port
lsof -i :9222

# Kill the process
kill -9 <PID>

# Or use a different port
node bin/morelogin.js start --profile-id <ID> --cdp-port 9223
```

### Issue 4: "Profile not found"

**Error:**
```
Error: Profile not found: xxxxx
```

**Solution:**
1. Verify the profile ID is correct
2. Run `node bin/morelogin.js list` to see available profiles
3. Confirm the profile exists in the Morelogin app

### Issue 5: Morelogin App Fails to Start

**macOS:**
```bash
# Check if app exists
ls -la /Applications/Morelogin.app

# Reinstall
brew reinstall --cask morelogin
```

**Windows:**
1. Run as administrator
2. Check if antivirus is blocking it
3. Reinstall the app

### Issue 6: CDP Disconnects Immediately After Connection

**Solution:**
1. Use `puppeteer-core` instead of `puppeteer`
2. Set `defaultViewport: null`
3. Do not call `browser.close()` unless you want to close the browser
4. Ensure Morelogin profile supports CDP

---

## 🔐 Security Recommendations

### 1. Protect API Token

```bash
# Do not commit token to version control
echo "~/.morelogin-cli/" >> ~/.gitignore_global

# Use environment variables
export MORELOGIN_TOKEN="your_token_here"
```

### 2. Restrict CDP Access

```bash
# Listen only on local interface
# Morelogin defaults to localhost only

# Use firewall rules
sudo pfctl -f /etc/pf.conf  # macOS
```

### 3. Isolate Profiles

- Create separate profiles for different purposes
- Use different proxy IPs
- Regularly clear browser data

### 4. Monitor Activity

```bash
# View running profiles
node bin/morelogin.js config

# Check network connections
lsof -i :9222
```

---

## 📚 Next Steps

After installation, you can:

1. **Read full guide**: `cat README.md`
2. **View quick start**: `cat QUICKSTART.md`
3. **Run example script**: `node examples/puppeteer-example.js`
4. **Create your own script**: Use examples as reference for automation logic
5. **Integrate with OpenClaw**: Use `openclaw morelogin` in OpenClaw

---

## 🆘 Get Help

### Documentation
- Local docs: `cat README.md`
- Morelogin official docs: https://morelogin.com/docs
- CDP protocol docs: https://chromedevtools.github.io/devtools-protocol/

### Community
- Morelogin support: support@morelogin.com
- OpenClaw Discord: https://discord.com/invite/clawd

### Debugging Tools

```bash
# Test API connection
node bin/morelogin.js browser list --page 1 --page-size 1

# View detailed logs
DEBUG=* node bin/morelogin.js start --profile-id <ID>

# Check port status
netstat -an | grep 9222
```

---

*Last updated: 2024-02-26*
