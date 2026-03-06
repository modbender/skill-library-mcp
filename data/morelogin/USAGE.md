# MoreLogin Skill Usage

This guide is aligned with the current implementation in:
- `bin/morelogin.js`
- `index.js`

## 1) Entrypoints

Both entrypoints are equivalent (same args, behavior, and exit code):

```bash
openclaw morelogin ...
node bin/morelogin.js ...
```

## 2) Prerequisites

- MoreLogin desktop app is running and logged in
- Local API is available at `http://127.0.0.1:40000`
- Node.js installed
- For CloudPhone ADB: `adb` and `expect`

## 3) Browser Profile Commands

```bash
node bin/morelogin.js browser list --page 1 --page-size 20
node bin/morelogin.js browser start --env-id <envId>
node bin/morelogin.js browser status --env-id <envId>
node bin/morelogin.js browser detail --env-id <envId>
node bin/morelogin.js browser refresh-fingerprint --env-id <envId>
node bin/morelogin.js browser close --env-id <envId>
```

Cache operations:

```bash
node bin/morelogin.js browser clear-cache --env-id <envId> --cookie true
node bin/morelogin.js browser clean-cloud-cache --env-id <envId> --cookie true --others true
```

Delete:

```bash
node bin/morelogin.js browser delete --env-ids "<id1,id2>"
```

## 4) CloudPhone Commands

Lifecycle:

```bash
node bin/morelogin.js cloudphone list --page 1 --page-size 20
node bin/morelogin.js cloudphone create --payload '{"skuId":"10005","proxyId":"<proxyId>","quantity":1}'
node bin/morelogin.js cloudphone start --id <cloudPhoneId>
node bin/morelogin.js cloudphone stop --id <cloudPhoneId>
node bin/morelogin.js cloudphone info --id <cloudPhoneId>
```

Command execution:

`cloudphone exec` has been removed from this skill.

ADB:

```bash
node bin/morelogin.js cloudphone adb-info --id <cloudPhoneId>
node bin/morelogin.js cloudphone update-adb --id <cloudPhoneId> --enable true
```

App operations:

```bash
node bin/morelogin.js cloudphone app-installed --id <cloudPhoneId>
node bin/morelogin.js cloudphone app-start --id <cloudPhoneId> --package-name com.android.chrome
node bin/morelogin.js cloudphone app-stop --id <cloudPhoneId> --package-name com.android.chrome
node bin/morelogin.js cloudphone app-restart --id <cloudPhoneId> --package-name com.android.chrome
node bin/morelogin.js cloudphone app-uninstall --id <cloudPhoneId> --package-name com.example.app
```

## 5) Proxy / Group / Tag Commands

Proxy:

```bash
node bin/morelogin.js proxy list --page 1 --page-size 20
node bin/morelogin.js proxy add --payload '{"proxyIp":"1.2.3.4","proxyPort":8000,"proxyType":0,"proxyProvider":"0"}'
node bin/morelogin.js proxy update --payload '{"id":"<proxyId>","proxyIp":"5.6.7.8","proxyPort":9000}'
node bin/morelogin.js proxy delete --ids "<id1,id2>"
```

Group:

```bash
node bin/morelogin.js group list --page 1 --page-size 20
node bin/morelogin.js group create --name "My Group"
node bin/morelogin.js group edit --id "<groupId>" --name "My Group V2"
node bin/morelogin.js group delete --ids "<id1,id2>"
```

Tag:

```bash
node bin/morelogin.js tag list
node bin/morelogin.js tag create --name "vip"
node bin/morelogin.js tag edit --id "<tagId>" --name "vip-new"
node bin/morelogin.js tag delete --ids "<id1,id2>"
```

## 6) Generic API Mode

Use API mode when a dedicated subcommand is not yet implemented:

```bash
node bin/morelogin.js api --endpoint /api/env/page --method POST --data '{"page":1,"pageSize":20}'
```

CloudPhone remark batch edit example:

```bash
node bin/morelogin.js api \
  --endpoint /api/cloudphone/edit/batch \
  --method POST \
  --data '{"id":[1685965493158051,1682923785306426],"envRemark":"11"}'
```

## 7) Smoke Test Checklist

```bash
node bin/morelogin.js browser list --page 1 --page-size 1
node bin/morelogin.js cloudphone list --page 1 --page-size 1
node bin/morelogin.js tag list
```

## 8) Troubleshooting

- `Request timeout after 10000ms` on `browser start`:
  - Re-run `browser status --env-id <envId>`; profile may already be running asynchronously.
- `cloudphone create validation failed`:
  - Current CLI follows `local-api.yaml` strict fields (`skuId`, `quantity`).
  - Add missing fields or use `--payload` with full body.


## 9) Related Files

- `bin/morelogin.js` (main CLI)
- `index.js` (entrypoint passthrough)
- `bin/common.js` (API helpers)
- `local-api.yaml` (official OpenAPI source used in this repo)
- `API-CONTRACT.md` (CLI-aligned parameter contract)
- `SKILL.md`, `QUICKSTART.md`, `README.md`
# MoreLogin CLI Usage Guide

This document is regenerated from the current implementation in:
- `bin/morelogin.js`
- `index.js`

It reflects the commands and behavior that are available right now.

## 1) What This Project Provides

This project is a local CLI wrapper around the MoreLogin Local API (`http://127.0.0.1:40000`).

Main capability areas:
- Browser profile lifecycle and cache operations
- Cloud phone lifecycle, ADB connection, and app operations
- Proxy / group / tag management
- Generic API passthrough for endpoints not yet wrapped by dedicated subcommands

## 2) Command Entrypoints (Equivalent)

Two entrypoints are supported and equivalent:

- `openclaw morelogin ...`
- `node bin/morelogin.js ...`

They forward the same arguments to the same CLI implementation and return the same exit code.

Examples:

```bash
openclaw morelogin browser list --page 1 --page-size 20
node bin/morelogin.js browser list --page 1 --page-size 20
```

## 3) Prerequisites

- MoreLogin desktop app is running and logged in
- Local API is reachable at `http://127.0.0.1:40000`
- Node.js installed
- For cloud phone operations in this skill:
  - No local ADB/SSH tooling is required

## 4) Global Help

```bash
node bin/morelogin.js help
node bin/morelogin.js browser help
node bin/morelogin.js cloudphone help
node bin/morelogin.js proxy help
node bin/morelogin.js group help
node bin/morelogin.js tag help
```

## 5) Browser Commands

### 5.1 List

```bash
node bin/morelogin.js browser list --page 1 --page-size 20
```

### 5.2 Start / Status / Close

```bash
node bin/morelogin.js browser start --env-id <envId>
node bin/morelogin.js browser status --env-id <envId>
node bin/morelogin.js browser close --env-id <envId>
```

`start`/`status`/`close` also support `--unique-id <number>`.

### 5.3 Detail

```bash
node bin/morelogin.js browser detail --env-id <envId>
```

### 5.4 Quick Create and Fingerprint Refresh

```bash
node bin/morelogin.js browser create-quick --browser-type-id 1 --operator-system-id 1 --quantity 1
node bin/morelogin.js browser refresh-fingerprint --env-id <envId>
```

### 5.5 Cache Operations

Local cache clear requires at least one cache switch.

```bash
node bin/morelogin.js browser clear-cache --env-id <envId> --cookie true
node bin/morelogin.js browser clear-cache --env-id <envId> --local-storage true --indexed-db true
```

Cloud cache clear requires at least one of `--cookie` or `--others`.

```bash
node bin/morelogin.js browser clean-cloud-cache --env-id <envId> --cookie true --others true
```

### 5.6 Delete

```bash
node bin/morelogin.js browser delete --env-ids "<id1,id2>"
```

## 6) CloudPhone Commands

### 6.1 List / Create / Start / Stop / Info

```bash
node bin/morelogin.js cloudphone list --page 1 --page-size 20
node bin/morelogin.js cloudphone create --payload '{"skuId":"10005","proxyId":"<proxyId>","quantity":1}'
node bin/morelogin.js cloudphone start --id <cloudPhoneId>
node bin/morelogin.js cloudphone stop --id <cloudPhoneId>
node bin/morelogin.js cloudphone info --id <cloudPhoneId>
```

### 6.2 Device Command Execution

`cloudphone exec` has been removed from this skill.

### 6.3 ADB Management

Inspect ADB metadata first:

```bash
node bin/morelogin.js cloudphone adb-info --id <cloudPhoneId>
```

Enable/disable ADB:

```bash
node bin/morelogin.js cloudphone update-adb --id <cloudPhoneId> --enable true
node bin/morelogin.js cloudphone update-adb --id <cloudPhoneId> --enable false
```

ADB connection strategy:
- Local ADB/SSH connection methods are removed in this skill.
- `adb-info` is retained only for metadata visibility.

### 6.4 New Machine and App Operations

```bash
node bin/morelogin.js cloudphone new-machine --id <cloudPhoneId>
node bin/morelogin.js cloudphone app-installed --id <cloudPhoneId>
node bin/morelogin.js cloudphone app-start --id <cloudPhoneId> --package-name com.android.chrome
node bin/morelogin.js cloudphone app-stop --id <cloudPhoneId> --package-name com.android.chrome
node bin/morelogin.js cloudphone app-restart --id <cloudPhoneId> --package-name com.android.chrome
node bin/morelogin.js cloudphone app-uninstall --id <cloudPhoneId> --package-name com.example.app
```

## 7) Proxy Commands

```bash
node bin/morelogin.js proxy list --page 1 --page-size 20
node bin/morelogin.js proxy add --payload '{"proxyIp":"1.2.3.4","proxyPort":8000,"proxyType":0,"proxyProvider":"0"}'
node bin/morelogin.js proxy update --payload '{"id":"<proxyId>","proxyIp":"5.6.7.8","proxyPort":9000}'
node bin/morelogin.js proxy delete --ids "<proxyId1,proxyId2>"
```

## 8) Group Commands

```bash
node bin/morelogin.js group list --page 1 --page-size 20
node bin/morelogin.js group create --name "My Group"
node bin/morelogin.js group edit --id "<groupId>" --name "My Group V2"
node bin/morelogin.js group delete --ids "<groupId1,groupId2>"
```

## 9) Tag Commands

```bash
node bin/morelogin.js tag list
node bin/morelogin.js tag create --name "vip"
node bin/morelogin.js tag edit --id "<tagId>" --name "vip-new"
node bin/morelogin.js tag delete --ids "<tagId1,tagId2>"
```

## 10) Generic API Passthrough

Use this when a dedicated CLI subcommand is not available yet.

```bash
node bin/morelogin.js api --endpoint /api/env/page --method POST --data '{"page":1,"pageSize":20}'
```

### 10.1 Example: Batch edit cloud phone remark

Current project does not yet expose `cloudphone edit` as a direct subcommand, so use API mode:

```bash
node bin/morelogin.js api \
  --endpoint /api/cloudphone/edit/batch \
  --method POST \
  --data '{"id":[1685965493158051,1682923785306426],"envRemark":"11"}'
```

## 11) Error Handling Notes

- Most wrapped commands call `unwrapApiResult`; if API `code != 0`, command fails with the API message.
- In `api` mode, raw response body is printed directly.
- For cloud phone power-on and ADB operations, wait for initialization (commonly 1-2 minutes) before intensive operations.

## 12) Known Limitations (Current State)

- Legacy top-level commands (`list/start/stop/info/connect`) are listed in CLI help but can be unstable with empty trailing args.
- Prefer namespaced commands:
  - `browser ...`
  - `cloudphone ...`
  - `proxy ...`
  - `group ...`
  - `tag ...`

## 13) Quick Smoke Test

```bash
node bin/morelogin.js browser list --page 1 --page-size 1
node bin/morelogin.js cloudphone list --page 1 --page-size 1
node bin/morelogin.js tag list
```

## 14) Related Files

- CLI implementation: `bin/morelogin.js`
- Entrypoint passthrough: `index.js`
- Common helpers: `bin/common.js`
- Quick start: `QUICKSTART.md`
- Skill definition: `SKILL.md`
#Morelogin Skill - Complete User Guide

## 📦 Skill structure

```
skills/morelogin/
├── SKILL.md # OpenClaw Skill definition (metadata and description)
├── README.md # Detailed tutorial document
├── INSTALL.md # Installation and Configuration Guide
├── QUICKSTART.md # 5 minutes quick start
├── package.json # Node.js package configuration
├── .gitignore # Git ignores files
├── index.js # OpenClaw integration portal
├── bin/
│ ├── morelogin.js # CLI main program
│ └── test-api.js # API connection testing tool
└── examples/
    ├── puppeteer-example.js # Puppeteer example
    └── playwright-example.js # Playwright example
```

---

## 🚀 Quick Start (3 steps)

### 1️⃣ Install dependencies

```bash
cd ~/.openclaw/workspace/skills/morelogin
npm install
```

### 2️⃣ Start Morelogin

```bash
# Open the Morelogin app and log in
# Make sure there is at least one configuration file

# List configuration files
node bin/morelogin.js list

# Start the profile (replace <ID> with your profile ID)
node bin/morelogin.js start --profile-id <ID>
```

### 3️⃣ Run automation

```bash
# Run the Puppeteer example
node examples/puppeteer-example.js

# Or run the Playwright example
node examples/playwright-example.js
```

---

## 💡 Core Concepts

### CDP (Chrome DevTools Protocol)

Morelogin provides automated control capabilities through the CDP protocol:

```
Morelogin Profile → CDP Endpoint (localhost:9222) → Puppeteer/Playwright → Automation Script
```

**Advantages:**
- 🚀 No WebDriver required
- 🔌 Connect directly to the browser
- 🛠️ Complete browser control
- 📊 Performance monitoring and debugging

### Profile

Each profile is an independent browser environment:

- Separate cookies and cache
- Independent fingerprint information
- Different proxy IPs can be configured
- Can run multiple at the same time

---

## 📖 Command Reference

### Configuration file management

```bash
# List all configuration files
node bin/morelogin.js list

# Start configuration file
node bin/morelogin.js start --profile-id <ID> [--cdp-port 9222]

# Stop configuration file
node bin/morelogin.js stop --profile-id <ID>

# View configuration file information
node bin/morelogin.js info --profile-id <ID>
```

### CDP connection

```bash
# Connect to the running configuration file
node bin/morelogin.js connect --profile-id <ID>

# Output example:
# 🔗 CDP address: http://localhost:9222
# 📍 WebSocket: ws://localhost:9222/devtools/browser/xxx
```

### Script execution

```bash
#Run automation script
node bin/morelogin.js run <ID> script.js

# Use sample script
node examples/puppeteer-example.js
node examples/playwright-example.js
```

### Configuration and Tools

```bash
# View configuration
node bin/morelogin.js config

# Setup Wizard
node bin/morelogin.js setup

# Test API connection
node bin/morelogin.js browser list --page 1 --page-size 1

# Show help
node bin/morelogin.js help
```

---

## 🔌 Code Example

### Puppeteer connection

```javascript
const puppeteer = require('puppeteer-core');

const browser = await puppeteer.connect({
  browserURL: 'http://localhost:9222',
  defaultViewport: null
});

const page = await browser.newPage();
await page.goto('https://example.com');
await page.screenshot({ path: 'example.png' });
```

### Playwright Connection

```javascript
const { chromium } = require('playwright');

const browser = await chromium.connectOverCDP('http://localhost:9222');
const context = browser.contexts()[0];
const page = context.pages()[0];

await page.goto('https://example.com');
```

### Basic automation

```javascript
// Navigation and screenshots
await page.goto('https://example.com');
await page.screenshot({ path: 'screenshot.png', fullPage: true });

//fill in the form
await page.type('#username', 'user');
await page.type('#password', 'pass');
await page.click('button[type="submit"]');

// Wait and extract data
await page.waitForSelector('.result');
const resultEl = await page.$('.result');
const data = resultEl ? await page.evaluate((el) => el.textContent, resultEl) : null;

//Execute JavaScript
const html = await page.evaluate(() => document.body.innerHTML);
```

### Advanced features

```javascript
//Network interception
await page.setRequestInterception(true);
page.on('request', request => {
  if (request.url().includes('ads')) {
    request.abort();
  } else {
    request.continue();
  }
});

// Cookie management
const cookies = await page.cookies();
await page.setCookie({ name: 'session', value: 'abc123' });

//Device simulation
await page.emulate(puppeteer.devices['iPhone 13']);

//Performance monitoring
const metrics = await page.metrics();
console.log('JS Heap:', metrics.JSHeapUsedSize);
```

---

## 🎯 Usage scenarios

### 1. Multiple account management

```javascript
// Use different configuration files for each account
const profiles = {
  account1: 'profile_id_1',
  account2: 'profile_id_2',
  account3: 'profile_id_3'
};

// Operate multiple accounts in parallel
await Promise.all(
  Object.entries(profiles).map(async ([name, id]) => {
    const browser = await connectToProfile(id);
    await performTask(browser, name);
  })
);
```

### 2. Web crawler

```javascript
const data = [];
let page = 1;

while (true) {
  await page.goto(`https://example.com/products?page=${page}`);
  
  const items = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('.product')).map(el => ({
      name: el.querySelector('.name').textContent,
      price: el.querySelector('.price').textContent
    }));
  });
  
  if (items.length === 0) break;
  data.push(...items);
  page++;
}
```

### 3. Automated testing

```javascript
//Login test
await page.goto('https://example.com/login');
await page.type('#email', 'test@example.com');
await page.type('#password', 'password123');
await page.click('button[type="submit"]');
await page.waitForNavigation();

// Verify successful login
const isLoggedIn = await page.$('.user-menu');
console.assert(isLoggedIn, 'Login failed!');

// test function
await page.click('.create-button');
await page.waitForSelector('.modal');
```

### 4. Data entry

```javascript
const records = [
  { name: 'John', email: 'john@example.com' },
  { name: 'Jane', email: 'jane@example.com' }
];

for (const record of records) {
  await page.goto('https://example.com/add');
  await page.type('#name', record.name);
  await page.type('#email', record.email);
  await page.click('button[type="submit"]');
  await page.waitForSelector('.success');
}
```

---

## ⚠️ Notes

### Performance optimization

- ✅ Reuse browser instances and do not start/stop frequently
- ✅ Use `waitForSelector` instead of fixed wait
- ✅ Disable image loading acceleration crawler: `page.setRequestInterception(true)`
- ✅ Clear cookies and cache regularly

### Anti-crawler countermeasures

- ✅ Use real User-Agent
- ✅ Add random delay
- ✅ Simulate human behavior (mouse movement, scrolling)
- ✅ Use proxy IP rotation

### Error handling

```javascript
try {
  await page.goto('https://example.com', { timeout: 30000 });
} catch (error) {
  if (error.message.includes('timeout')) {
    console.log('Page loading timeout, try again...');
    await page.reload();
  } else {
    throw error;
  }
}
```

---

## 🆘 Troubleshooting

### Quick FAQ

| Problem | Solution |
|------|---------|
| Unable to connect to CDP | Check if the configuration file is running and the port is correct |
| Script execution is slow | Reduce waiting time and disable image loading |
| Configuration file startup failed | Restart the Morelogin application and check the login status |
| High memory usage | Close unused pages regularly and clear cache |
| Detected by website | Use more realistic fingerprints, add random delays |

### Diagnostic commands

```bash
# Test API connection
node bin/morelogin.js browser list --page 1 --page-size 1

# Check the running status
node bin/morelogin.js config

# Check port occupancy
lsof -i :9222

# View detailed logs
DEBUG=* node bin/morelogin.js start --profile-id <ID>
```

---

## 📚 Related resources

### document
- 📖[Full Tutorial](README.md)
- 🚀 [Quick Start](QUICKSTART.md)
- 🔧[Installation Guide](INSTALL.md)
- 📋 [Skill definition](SKILL.md)

### External resources
- [Morelogin official website](https://morelogin.com)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [Puppeteer Documentation](https://pptr.dev/)
- [Playwright Documentation](https://playwright.dev/)

### Sample code
- `examples/puppeteer-example.js` - Puppeteer complete example
- `examples/playwright-example.js` - Full Playwright example

---

## 🎓 Learning Path

### Beginner
1. ✅ Complete installation and configuration
2. ✅ Run the sample script
3. ✅ Understand the CDP connection principle
4. ✅ Modify the sample script and try simple operations

### Advanced User
1. ✅ Create custom automation scripts
2. ✅ Manage multiple profiles
3. ✅ Implement error handling and retry
4. ✅ Optimize performance and stability

### Advanced User
1. ✅ Build a distributed crawler system
2. ✅ Implement intelligent anti-detection strategy
3. ✅ Integrate into production environment
4. ✅ Monitoring and logging system

---

## 📞 Get help

Having a problem? Try these methods:

1. **View document**: `cat README.md`
2. **Run test**: `node bin/morelogin.js browser list --page 1 --page-size 1`
3. **Check configuration**: `node bin/morelogin.js config`
4. **View log**: Enable DEBUG mode
5. **Contact Support**: Morelogin Official Support or OpenClaw Community

---

**Wish you happy using it! 🎉**

*Feedback is welcome if you have any questions or suggestions. *
