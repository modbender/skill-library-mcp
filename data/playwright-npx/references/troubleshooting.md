# Troubleshooting Guide

Common Playwright issues and solutions.

## Browser Binary Not Found

### Error
```
Executable doesn't exist at /path/to/chromium
```

### Solution

Install browser binaries:

```bash
# Install all browsers
npx playwright install

# Or just Chromium
npx playwright install chromium

# Or specific browser
npx playwright install firefox
npx playwright install webkit
```

### System Dependencies (Linux)

On Linux, you may need system dependencies:

```bash
# Ubuntu/Debian
npx playwright install-deps

# Or for specific browser
npx playwright install-deps chromium
```

### Verify Installation

```javascript
// test-browsers.mjs
import { chromium, firefox, webkit } from 'playwright';

for (const browserType of [chromium, firefox, webkit]) {
  try {
    const browser = await browserType.launch();
    console.log(`${browserType.name()}: OK`);
    await browser.close();
  } catch (e) {
    console.error(`${browserType.name()}: ${e.message}`);
  }
}
```

## Timeout Issues

### Page Load Timeout

```javascript
// Increase navigation timeout
await page.goto(url, { timeout: 60000 });

// Wait for specific state
await page.goto(url, { waitUntil: 'domcontentloaded' });  // faster
await page.goto(url, { waitUntil: 'networkidle' });       // wait for network
```

### Selector Timeout

```javascript
// Increase selector timeout
await page.waitForSelector('.result', { timeout: 60000 });

// Wait for different states
await page.waitForSelector('.loading', { state: 'hidden' });
await page.waitForSelector('.result', { state: 'visible' });

// Wait for function
await page.waitForFunction(() => 
  document.querySelectorAll('.item').length > 0
);
```

## Selector Not Found

### Strict Mode Violation

```
Error: locator.click: Error: strict mode violation: 
"button" resolved to 5 elements
```

**Fix:** Make selector more specific:

```javascript
// ❌ Too broad
await page.click('button');

// ✅ Specific
await page.click('button[type="submit"]');
await page.click('button:has-text("Submit")');
await page.click('[data-testid="submit-btn"]');

// Or use first/last/nth
await page.locator('button').first().click();
await page.locator('button').nth(2).click();
```

### Element Not Visible

```javascript
// Scroll into view first
await page.locator('.item').scrollIntoViewIfNeeded();
await page.locator('.item').click();

// Or force click
await page.locator('.item').click({ force: true });
```

## Network Issues

### Connection Refused

```
Error: net::ERR_CONNECTION_REFUSED
```

**Check:**
- URL is correct (including protocol)
- Site is running and accessible
- No VPN/proxy blocking

```javascript
// Add http:// if missing
const url = userInput.startsWith('http') ? userInput : `https://${userInput}`;
```

### SSL Certificate Errors

```javascript
// Ignore HTTPS errors (dev only!)
const browser = await chromium.launch({
  ignoreHTTPSErrors: true
});
```

### Proxy Configuration

```javascript
const browser = await chromium.launch({
  proxy: {
    server: 'http://proxy.example.com:3128',
    username: 'user',
    password: 'pass'
  }
});
```

## Module/Import Errors

### Cannot Find Module

```
Error: Cannot find module 'playwright'
```

**Fix:**

```bash
# Install playwright
npm install playwright

# Verify node_modules exists
ls node_modules/playwright
```

### ES Module Errors

```
SyntaxError: Cannot use import statement outside a module
```

**Fix:** Use `.mjs` extension or add `"type": "module"` to package.json:

```bash
# Rename to .mjs
mv script.js script.mjs

# Or create package.json
echo '{"type": "module"}' > package.json
```

## Permission Errors

### Cannot Write Screenshot

```javascript
// Ensure directory exists
import fs from 'fs';
fs.mkdirSync('tmp', { recursive: true });

await page.screenshot({ path: 'tmp/screenshot.png' });
```

### Permission Denied (Linux)

```bash
# Fix permissions on node_modules
chmod -R 755 node_modules

# Or reinstall
rm -rf node_modules package-lock.json
npm install
```

## Memory Issues

### Out of Memory

```javascript
// Close pages when done
const page = await browser.newPage();
// ... do work ...
await page.close();  // Free memory

// Process in batches
for (const url of urls) {
  const page = await browser.newPage();
  await processPage(page, url);
  await page.close();
}
```

## File Upload Issues

```javascript
// Upload single file
await page.locator('input[type="file"]').setInputFiles('/path/to/file.pdf');

// Upload multiple files
await page.locator('input[type="file"]').setInputFiles([
  '/path/to/file1.pdf',
  '/path/to/file2.pdf'
]);

// From buffer
await page.locator('input[type="file"]').setInputFiles({
  name: 'file.txt',
  mimeType: 'text/plain',
  buffer: Buffer.from('file content')
});
```

## Dialog Handling

```javascript
// Handle alerts
page.on('dialog', dialog => {
  console.log(`Dialog: ${dialog.message()}`);
  dialog.accept();
});

// Handle confirm dialogs
page.on('dialog', async dialog => {
  if (dialog.type() === 'confirm') {
    await dialog.accept();
  } else {
    await dialog.dismiss();
  }
});
```

## Context/Isolation Issues

```javascript
// Use new context for clean session
const context = await browser.newContext();
const page = await context.newPage();

// Isolate cookies/storage per context
const context1 = await browser.newContext();
const context2 = await browser.newContext();  // Separate cookies
```

## Getting Help

1. **Check Playwright docs:** https://playwright.dev
2. **Use codegen:** `npx playwright codegen <url>`
3. **Enable debug mode:** `DEBUG=pw:* node script.mjs`
4. **Check trace:** Record and view traces for detailed debugging
