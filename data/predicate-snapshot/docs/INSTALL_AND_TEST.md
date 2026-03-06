# OpenClaw + Predicate Snapshot Skill Installation Guide

This guide walks you through installing OpenClaw and the Predicate Snapshot skill to test ML-powered DOM snapshots.

## Prerequisites

- Node.js 20+ (`node --version`)
- npm 9+ (`npm --version`)
- A terminal (macOS Terminal, iTerm2, Windows Terminal, etc.)

## Step 1: Install OpenClaw

```bash
# Install OpenClaw globally
npm install -g @anthropic/openclaw

# Verify installation
openclaw --version
```

Or use npx (no global install):
```bash
npx @anthropic/openclaw --version
```

## Step 2: Install the Predicate Snapshot Skill

### Option A: From ClawHub (Recommended)

```bash
npx clawdhub@latest install predicate-snapshot
```

### Option B: From npm

```bash
# Create skills directory if it doesn't exist
mkdir -p ~/.openclaw/skills/predicate-snapshot

# Install the package
cd ~/.openclaw/skills/predicate-snapshot
npm init -y
npm install @predicatesystems/openclaw-snapshot-skill
```

### Option C: From Source (Development)

```bash
# Clone the repo
git clone https://github.com/predicate-systems/predicate-snapshot-skill ~/.openclaw/skills/predicate-snapshot

# Build
cd ~/.openclaw/skills/predicate-snapshot
npm install
npm run build
```

## Step 3: Configure API Key (Optional)

For ML-powered ranking (95% token reduction), get a free API key:

1. Visit https://predicate.systems/keys
2. Sign up and create an API key
3. Set the environment variable:

```bash
# Add to ~/.bashrc, ~/.zshrc, or ~/.profile
export PREDICATE_API_KEY="sk-your-api-key-here"

# Reload shell
source ~/.zshrc  # or ~/.bashrc
```

Or configure in `~/.openclaw/config.yaml`:
```yaml
skills:
  predicate-snapshot:
    api_key: "sk-your-api-key-here"
```

**Note:** Without an API key, the skill still works with local heuristic-based pruning (~80% token reduction).

## Step 4: Verify Installation

```bash
# List installed skills
openclaw skills list

# You should see:
# - predicate-snapshot
```

## Step 5: Test the Skill

### Start OpenClaw with a browser session

```bash
# Start OpenClaw in browser mode
openclaw --browser

# Or specify a URL to navigate to
openclaw --browser --url "https://amazon.com"
```

### Use the skill commands

Once in the OpenClaw session with a browser:

```
# Take a snapshot of the current page
/predicate-snapshot

# Take a snapshot with custom limit
/predicate-snapshot --limit=30

# Use local mode (no API key required)
/predicate-snapshot-local

# Click an element by its Predicate ID
/predicate-act click 42

# Type into an element
/predicate-act type 15 "search query"

# Scroll to an element
/predicate-act scroll 23
```

## Example Test Session

```bash
$ openclaw --browser --url "https://amazon.com"

OpenClaw v1.0.0
Browser session started.
Navigated to: https://amazon.com

> /predicate-snapshot

# Predicate Snapshot
# URL: https://www.amazon.com/
# Elements: showing top 50
# Format: ID|role|text|imp|is_primary|docYq|ord|DG|href

42|searchbox|Search Amazon|0.98|true|180|1|search-bar|
15|button|Go|0.95|true|180|2|search-bar|
23|link|Today's Deals|0.89|false|120|1|nav-main|/deals
...

> /predicate-act type 42 "wireless headphones"

Typed "wireless headphones" into element 42

> /predicate-act click 15

Clicked element 15

> /predicate-snapshot

# New snapshot showing search results...
```

## Troubleshooting

### Skill not found

```bash
# Check skill directory exists
ls -la ~/.openclaw/skills/predicate-snapshot/

# Rebuild if needed
cd ~/.openclaw/skills/predicate-snapshot
npm run build
```

### API key not working

```bash
# Verify environment variable is set
echo $PREDICATE_API_KEY

# Test API connectivity
curl -H "Authorization: Bearer $PREDICATE_API_KEY" https://api.predicate.systems/v1/health
```

### Browser not starting

```bash
# Install Playwright browsers
npx playwright install chromium

# Or install all browsers
npx playwright install
```

### Module not found errors

```bash
# Reinstall dependencies
cd ~/.openclaw/skills/predicate-snapshot
rm -rf node_modules package-lock.json
npm install
npm run build
```

## Comparing Results

To see the difference between default accessibility tree and Predicate Snapshot:

1. **Without skill (default A11y tree):**
   - ~18,000 tokens
   - ~800 elements
   - Low signal quality

2. **With Predicate Snapshot:**
   - ~800 tokens (95% reduction)
   - 50 ranked elements
   - High signal quality

## Running the Demo

The skill includes a demo that compares both approaches using a purpose-built test site:

**Test Site:** `https://www.localllamaland.com/login`
- Fake login with intentional SPA challenges
- Delayed hydration (~600ms)
- Button disabled until form filled
- Late-loading profile content
- Test credentials: `testuser` / `password123`

### Option 1: Run with Docker (Recommended)

```bash
cd ~/.openclaw/skills/predicate-snapshot

# Set up environment (optional for enhanced features)
export PREDICATE_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-..."

# Run the test
./docker-test.sh
```

### Option 2: Run Locally

```bash
cd ~/.openclaw/skills/predicate-snapshot

# Set up environment
export PREDICATE_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-..."  # For LLM comparison

# Run the login demo
npm run demo:login

# Run with visible browser
npm run demo:login -- --headed

# Run with element overlay (shows green boxes on captured elements)
npm run demo:login -- --headed --overlay
```

This will:
1. Navigate to the test login page
2. Compare A11y tree vs Predicate Snapshot token usage
3. Show how an LLM performs with each approach
4. Complete a full login flow and verify profile page

## Next Steps

- Read the full documentation: https://predicatesystems.ai/docs
- Report issues: https://github.com/predicate-systems/predicate-snapshot-skill/issues
- Join Discord: https://discord.gg/predicate
