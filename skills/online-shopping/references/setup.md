# Stealth Browser Setup

## Automatic Setup

Run the bundled setup script:

```bash
bash <skill-dir>/scripts/setup.sh
```

This handles everything below automatically and verifies the install.

## Manual Setup

### Prerequisites

- Node.js 22+
- OpenClaw installed globally via npm/pnpm

### 1. Install xvfb (virtual display)

```bash
# Debian/Ubuntu
sudo apt-get install -y xvfb

# Fedora/RHEL
sudo dnf install -y xorg-x11-server-Xvfb

# Arch
sudo pacman -S xorg-server-xvfb
```

### 2. Install Patchright

```bash
cd $(npm root -g)/openclaw   # or your OpenClaw install path
npm install patchright --legacy-peer-deps
```

### 3. Install browser

```bash
# x86_64 — Google Chrome (recommended for best stealth)
npx patchright install chrome

# ARM64 — Chromium only (Chrome not available)
npx patchright install chromium
```

### 4. Install system dependencies for Chromium

```bash
npx patchright install-deps chromium
```

### 5. Verify

```bash
xvfb-run --auto-servernum node -e "
const { chromium } = require('patchright');
(async () => {
  const b = await chromium.launch({ headless: false, args: ['--no-sandbox'] });
  const p = await b.newPage();
  await p.goto('https://example.com');
  console.log(await p.title());
  await b.close();
})();
"
```

Should print "Example Domain".

## Platform Notes

### ARM64 (aarch64)
- Google Chrome is NOT available for Linux ARM64
- Use Chromium: `npx patchright install chromium`
- Snap Chromium does NOT work with OpenClaw (AppArmor sandbox conflicts)
- Playwright's Chromium (separate from Patchright's) also works for non-protected sites

### x86_64
- Google Chrome recommended: `npx patchright install chrome`
- Use `channel: "chrome"` in launch options for best stealth fingerprint

### macOS
- xvfb not needed (has a display)
- Remove `xvfb-run` wrapper from commands
- Chrome: `npx patchright install chrome`

## OpenClaw Browser Config (optional)

For sites WITHOUT Cloudflare/bot protection, OpenClaw's built-in browser tool works fine and is easier to use:

```json
{
  "browser": {
    "enabled": true,
    "headless": true,
    "noSandbox": true,
    "defaultProfile": "openclaw"
  }
}
```

For Cloudflare-protected sites, always use Patchright scripts directly.

## Why Not OpenClaw's Browser Tool for Protected Sites?

OpenClaw connects to Chrome via CDP (Chrome DevTools Protocol) and uses `Runtime.enable`, which is the #1 signal Cloudflare uses to detect automation. Patchright patches this by executing JavaScript in isolated execution contexts instead. This patch only works when using Patchright's own API (`chromium.launch()`) — not when connecting via raw CDP (`connectOverCDP()`).

## Troubleshooting

- **"Browser closed unexpectedly"** — missing system deps. Run `npx patchright install-deps chromium`
- **Still getting Cloudflare challenges** — make sure you're using `headless: false` and NOT setting custom userAgent
- **"Cannot find Patchright"** — run `npm install patchright --legacy-peer-deps` in your OpenClaw directory
- **xvfb errors** — make sure xvfb is installed: `which Xvfb`
