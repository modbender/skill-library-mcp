# Morelogin Browser Integration Guide

## 📖 Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Configure Morelogin](#configure-morelogin)
4. [Using CLI Tools](#using-cli-tools)
5. [CDP Connection Details](#cdp-connection-details)
6. [Automation Examples](#automation-examples)
7. [FAQ](#faq)
8. [Advanced Usage](#advanced-usage)

---

## Introduction

Morelogin is a fingerprint browser that supports multi-account management and browser environment isolation. This Skill provides the ability to connect to and control Morelogin browsers via **CDP (Chrome DevTools Protocol)**, and works with automation tools such as Puppeteer and Playwright.

### Why Use CDP?

- **Native support**: Morelogin is Chromium-based and natively supports the CDP protocol
- **Powerful features**: Control almost all browser capabilities
- **Rich ecosystem**: Use mature tools like Puppeteer and Playwright
- **No WebDriver needed**: Connect directly to the browser without WebDriver

---

## Installation

### 1. Install Morelogin Desktop App

**macOS:**
```bash
# Download the installer
open https://morelogin.com/download

# Or use Homebrew (if available)
brew install --cask morelogin
```

**Windows:**
```powershell
# Download the installer from official website
# https://morelogin.com/download
```


### 2. Install This Skill

```bash
# Navigate to the skill directory
cd ~/.openclaw/workspace/skills/morelogin

# Install dependencies
npm install
```

### 3. Install Puppeteer or Playwright (Optional)

```bash
# Using Puppeteer
npm install puppeteer-core

# Or using Playwright
npm install playwright
```

---

## Configure Morelogin

### 1. Log in to Morelogin

Open the Morelogin app and log in with your account.

### 2. Create Browser Profiles

1. Click "Create Profile"
2. Select browser type (Chrome/Edge/Firefox)
3. Configure proxy (optional)
4. Configure fingerprint info (optional; Morelogin auto-generates)
5. Save the profile

### 3. Enable CDP Support

Morelogin supports CDP by default, but ensure:

1. CDP is enabled when the profile starts
2. CDP port is not in use (default: 9222)
3. Local API service is running

### 4. Configure TOOLS.md

Add to `~/.openclaw/workspace/TOOLS.md`:

```markdown
### Morelogin

- API Token: your_api_token_here (if needed)
- Install Path: /Applications/Morelogin.app (macOS)
- Default CDP Port: 9222
- Local API: http://localhost:40000
```

---

## Using CLI Tools

### Basic Commands

```bash
# Navigate to the skill directory
cd ~/.openclaw/workspace/skills/morelogin

# View all commands
node bin/morelogin.js help

# Or use npm script
npm start -- help
```

> The CLI is organized by the official Local API into five namespaces: `browser` / `cloudphone` / `proxy` / `group` / `tag`.  
> Legacy commands `list/start/stop/info/connect` still work, but the new command format is recommended.

### Browser: Browser Profiles

```bash
# List profiles
node bin/morelogin.js browser list --page 1 --page-size 20

# Start a profile
node bin/morelogin.js browser start --env-id abc123def
# Note: start may occasionally timeout at 10s while profile still launches.
# Always re-check with status before retrying.

# View running status (debugPort can be used directly for CDP connection when present)
node bin/morelogin.js browser status --env-id abc123def

# View details
node bin/morelogin.js browser detail --env-id abc123def

# Clear local cache (select cleanup items by official fields)
node bin/morelogin.js browser clear-cache --env-id abc123def --cookie true --local-storage true

# Clear cloud cache (cookie / other cache)
node bin/morelogin.js browser clean-cloud-cache --env-id abc123def --cookie true --others true

# Close profile
node bin/morelogin.js browser close --env-id abc123def
```

### CloudPhone: Cloud Phones

```bash
# List cloud phones
node bin/morelogin.js cloudphone list --page 1 --page-size 20

# Start/Stop
node bin/morelogin.js cloudphone start --id <cloudPhoneId>
node bin/morelogin.js cloudphone stop --id <cloudPhoneId>

# Get details (includes ADB info)
node bin/morelogin.js cloudphone info --id <cloudPhoneId>

# Query ADB connection info (for identifying connection method)
node bin/morelogin.js cloudphone adb-info --id <cloudPhoneId>

# Enable ADB (official fields: ids + enableAdb)
node bin/morelogin.js cloudphone update-adb --id <cloudPhoneId> --enable true
```

### Proxy: Proxy Management

```bash
# Query proxy list
node bin/morelogin.js proxy list --page 1 --page-size 20

# Add proxy (recommend using --payload for full parameters)
node bin/morelogin.js proxy add --payload '{"proxyIp":"1.2.3.4","proxyPort":8000,"proxyType":0,"proxyProvider":"0"}'

# Update proxy
node bin/morelogin.js proxy update --payload '{"id":"<proxyId>","proxyIp":"5.6.7.8","proxyPort":9000}'

# Delete proxy
node bin/morelogin.js proxy delete --ids "<proxyId1>,<proxyId2>"
```

### Group: Group Management

```bash
# Query groups
node bin/morelogin.js group list --page 1 --page-size 20

# Create group
node bin/morelogin.js group create --name "US-Group"

# Edit group
node bin/morelogin.js group edit --id "<groupId>" --name "US-Group-New"

# Delete group
node bin/morelogin.js group delete --ids "<groupId1>,<groupId2>"
```

### Tag: Tag Management

```bash
# Query tags (GET /api/envtag/all)
node bin/morelogin.js tag list

# Create tag
node bin/morelogin.js tag create --name "vip"

# Edit tag
node bin/morelogin.js tag edit --id "<tagId>" --name "vip-new"

# Delete tag
node bin/morelogin.js tag delete --ids "<tagId1>,<tagId2>"
```

---

## CDP Connection Details

### CDP Address Format

After Morelogin starts, the following endpoints are exposed:

```
HTTP:  http://127.0.0.1:<debugPort>/json/version
HTTP:  http://127.0.0.1:<debugPort>/json/list
WS:    ws://127.0.0.1:<debugPort>/devtools/browser/<browser_id>
WS:    ws://127.0.0.1:<debugPort>/devtools/page/<page_id>
```

### Using Chrome DevTools

1. After starting the profile, open Chrome browser
2. Visit: `chrome://inspect/#devices`
3. Morelogin instances appear under "Remote Target"
4. Click "inspect" to open DevTools

### Connecting with Puppeteer

```javascript
const puppeteer = require('puppeteer-core');

// Get debugPort from:
// node bin/morelogin.js browser status --env-id <envId>
const browser = await puppeteer.connect({
  browserURL: 'http://127.0.0.1:<debugPort>',
  defaultViewport: null
});

const pages = await browser.pages();
const page = pages[0];
await page.goto('https://example.com');
```

### Connecting with Playwright

```javascript
const { chromium } = require('playwright');

// Get debugPort from:
// node bin/morelogin.js browser status --env-id <envId>
const browser = await chromium.connectOverCDP('http://127.0.0.1:<debugPort>');
const context = browser.contexts()[0];
const page = context.pages()[0];
await page.goto('https://example.com');
```

### Using Raw CDP Protocol

```javascript
const WebSocket = require('ws');

const ws = new WebSocket('ws://127.0.0.1:<debugPort>/devtools/browser/<browser_id>');

ws.on('open', () => {
  ws.send(JSON.stringify({
    id: 1,
    method: 'Page.navigate',
    params: { url: 'https://example.com' }
  }));
});

ws.on('message', (data) => {
  console.log(JSON.parse(data));
});
```

---

## Automation Examples

### Example 1: Basic Web Page Operations

```javascript
// examples/basic-example.js
const puppeteer = require('puppeteer-core');

async function main() {
  // Get debugPort from:
  // node bin/morelogin.js browser status --env-id <envId>
  const browser = await puppeteer.connect({
    browserURL: 'http://127.0.0.1:<debugPort>'
  });
  
  const page = await browser.newPage();
  
  // Navigate
  await page.goto('https://example.com');
  
  // Screenshot
  await page.screenshot({ path: 'screenshot.png' });
  
  // Get content
  const title = await page.title();
  console.log('Title:', title);
  
  await browser.close();
}

main();
```

### Example 2: Form Fill and Submit

```javascript
// examples/form-example.js
const puppeteer = require('puppeteer-core');

async function main() {
  // Get debugPort from:
  // node bin/morelogin.js browser status --env-id <envId>
  const browser = await puppeteer.connect({
    browserURL: 'http://127.0.0.1:<debugPort>'
  });
  
  const page = await browser.newPage();
  await page.goto('https://example.com/login');
  
  // Fill form
  await page.type('#username', 'myuser');
  await page.type('#password', 'mypassword');
  
  // Click submit
  await page.click('button[type="submit"]');
  
  // Wait for navigation
  await page.waitForNavigation();
  
  // Verify login
  const isLoggedIn = await page.$('.user-profile');
  console.log('Login successful:', !!isLoggedIn);
  
  await browser.close();
}

main();
```

### Example 3: Data Scraping

```javascript
// examples/scraping-example.js
const puppeteer = require('puppeteer-core');
const fs = require('fs');

async function main() {
  // Get debugPort from:
  // node bin/morelogin.js browser status --env-id <envId>
  const browser = await puppeteer.connect({
    browserURL: 'http://127.0.0.1:<debugPort>'
  });
  
  const page = await browser.newPage();
  await page.goto('https://example.com/products');
  
  // Scrape data
  const products = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('.product')).map(el => ({
      name: el.querySelector('.name')?.textContent,
      price: el.querySelector('.price')?.textContent,
      url: el.querySelector('a')?.href
    }));
  });
  
  // Save to file
  fs.writeFileSync('products.json', JSON.stringify(products, null, 2));
  console.log(`Scraped ${products.length} products`);
  
  await browser.close();
}

main();
```

### Example 4: Multi-Tab Operations

```javascript
// examples/multi-tab-example.js
const puppeteer = require('puppeteer-core');

async function main() {
  // Get debugPort from:
  // node bin/morelogin.js browser status --env-id <envId>
  const browser = await puppeteer.connect({
    browserURL: 'http://127.0.0.1:<debugPort>'
  });
  
  // Open multiple tabs
  const page1 = await browser.newPage();
  const page2 = await browser.newPage();
  
  await page1.goto('https://example.com');
  await page2.goto('https://github.com');
  
  // Parallel operations
  await Promise.all([
    page1.screenshot({ path: 'page1.png' }),
    page2.screenshot({ path: 'page2.png' })
  ]);
  
  console.log('Screenshots completed');
  
  await browser.close();
}

main();
```

### Example 5: Using Playwright

```javascript
// examples/playwright-example.js
const { chromium } = require('playwright');

async function main() {
  // Get debugPort from:
  // node bin/morelogin.js browser status --env-id <envId>
  const browser = await chromium.connectOverCDP('http://127.0.0.1:<debugPort>');
  const context = browser.contexts()[0];
  const page = context.pages()[0] || await context.newPage();
  
  await page.goto('https://example.com');
  
  // Use Playwright features
  await page.pdf({ path: 'page.pdf', format: 'A4' });
  
  console.log('PDF generated');
  
  // Keep browser open
  await new Promise(() => {});
}

main();
```

---

## FAQ

### Q1: Cannot Connect to Morelogin

**Issue**: `Error: connect ECONNREFUSED`

**Solutions**:
1. Ensure the Morelogin app is running
2. Check that the profile is running
3. Verify CDP port is not in use: `lsof -i :9222`
4. Try a different CDP port: `--cdp-port 9223`

### Q2: Browser Crashes After CDP Connection

**Issue**: Browser closes immediately after connecting

**Solutions**:
1. Use `puppeteer-core` instead of `puppeteer`
2. Set `defaultViewport: null`
3. Do not call `browser.close()` unless you want to close the browser

### Q3: Profile Fails to Start

**Issue**: Error when starting the profile

**Solutions**:
1. Check if Morelogin is logged in
2. Verify the profile ID is correct
3. If `browser start` times out at 10s, run `browser status` to confirm actual running state
4. Check Morelogin log files
5. Try restarting the Morelogin app

### Q4: Automation Script Runs Slowly

**Issue**: Script execution is very slow

**Solutions**:
1. Reduce unnecessary wait times
2. Use `waitForSelector` instead of fixed `setTimeout`
3. Disable image loading: `page.setRequestInterception(true)`
4. Use headless mode (if Morelogin supports it)

### Q5: How to Get Profile ID?

**Method 1**: List via CLI
```bash
node bin/morelogin.js browser list
```

**Method 2**: From Morelogin app
- Right-click the profile in the Morelogin app
- Select "Copy ID" or view profile details

**Method 3**: From Morelogin data files
```bash
# macOS
cat ~/Library/Application\ Support/Morelogin/profiles.json

# Windows
cat %APPDATA%\Morelogin\profiles.json
```

---

## Advanced Usage

### 1. OpenClaw Integration

Using Morelogin in OpenClaw:

```bash
# Invoke via OpenClaw
openclaw morelogin browser start --env-id <envId>
openclaw morelogin cloudphone info --id <cloudPhoneId>
openclaw morelogin proxy list --page 1 --page-size 20
```

### 2. Batch Operations

```javascript
// Batch start multiple profiles
const profileIds = ['id1', 'id2', 'id3'];

for (const id of profileIds) {
  await callApi('/api/env/start', { envId: id });
  await sleep(2000); // Wait 2 seconds
}
```

### 3. Custom CDP Commands

```javascript
const browser = await puppeteer.connect({
  browserURL: 'http://127.0.0.1:<debugPort>'
});

const client = await browser.target().createCDPSession();

// Send raw CDP commands
await client.send('Network.setCookies', {
  cookies: [{ name: 'test', value: '123', domain: 'example.com' }]
});

await client.send('Emulation.setDeviceMetricsOverride', {
  width: 1920,
  height: 1080,
  deviceScaleFactor: 1,
  mobile: false
});
```

### 4. Performance Monitoring

```javascript
const browser = await puppeteer.connect({
  browserURL: 'http://127.0.0.1:<debugPort>'
});

const page = await browser.newPage();

// Listen for performance metrics
page.on('metrics', ({ metrics }) => {
  console.log('JS Heap Size:', metrics.JSHeapUsedSize);
});

// Enable performance monitoring
await page.setCacheEnabled(false);
await page.setViewport({ width: 1920, height: 1080 });
```

### 5. Network Interception and Modification

```javascript
const browser = await puppeteer.connect({
  browserURL: 'http://127.0.0.1:<debugPort>'
});

const page = await browser.newPage();

await page.setRequestInterception(true);

page.on('request', request => {
  // Block ads
  if (request.url().includes('ads')) {
    request.abort();
  }
  // Modify request headers
  else {
    const headers = request.headers();
    headers['x-custom-header'] = 'my-value';
    request.continue({ headers });
  }
});

page.on('response', response => {
  console.log(`${response.status()} ${response.url()}`);
});
```

---

## Resources

- [Morelogin Official Site](https://morelogin.com)
- [Morelogin API Document](https://guide.morelogin.com/api-reference/local-api)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [Puppeteer Docs](https://pptr.dev/)
- [Playwright Docs](https://playwright.dev/)
- [OpenClaw Docs](https://docs.openclaw.ai)

---

## Changelog

### v1.0.0
- Initial release
- Profile management support
- CDP connection support
- Puppeteer and Playwright examples
- OpenClaw integration

---

**Enjoy! 🎉**

For issues, see the FAQ section or contact support.
