---
name: protonmail-claw
title: ProtonMail
description: Manage ProtonMail emails via Playwright browser automation. Login, read, send, and manage your encrypted inbox.
homepage: https://proton.me/mail
metadata: {"clawdbot":{"emoji":"📧","requires":{"bins":["playwright","node"]},"install":[{"id":"npm","kind":"npm","package":"playwright","bins":["npx playwright"],"label":"Install Playwright (npm)"},{"id":"chromium","kind":"exec","command":"npx playwright install chromium","label":"Install Chromium browser"}]}}
---

# ProtonMail 📨

Your encrypted inbox, automated. Because checking emails manually is so 2010.

## What it does

- **Login** to any ProtonMail account securely
- **Read** emails from your inbox
- **Send** new emails with compose functionality
- **Manage** your mailbox like a pro

All via Playwright browser automation. No API keys, no IMAP/SMTP headaches - just a real browser doing real browser things.

## Why this exists

You have better things to do than clicking through ProtonMail's beautiful (but slow) UI. Let your agent handle it. While you relax. Or code. Or whatever it is you do.

We built this because:
1. ProtonMail's web UI is... leisurely
2. Automation is hot
3. Why click when you can script?

## Requirements

### The Basics
- **Node.js** 18+ (20+ recommended)
- **Playwright** 1.40+ (`npm install playwright`)
- **Chromium** browser (`npx playwright install chromium`)

### System Dependencies (Linux)
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 libpango-1.0-0 libcairo2

# Raspberry Pi / ARM
sudo apt-get install -y chromium-browser
```

### The Secret Sauce (Bot Detection Bypass)
This skill includes enterprise-grade bot detection evasion:
```javascript
// Launch with stealth args
await chromium.launch({ 
  headless: true,
  args: [
    '--disable-blink-features=AutomationControlled',
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-dev-shm-usage'
  ]
});

// Hide webdriver property
await page.addInitScript(() => {
  Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
});
```

This makes Chrome think it's being controlled by a human. Mostly works. ✨

## Quick Start

### 1. Login
```javascript
const { chromium } = require('playwright');

async function loginProton(email, password) {
  const browser = await chromium.launch({ 
    headless: true,
    args: ['--disable-blink-features=AutomationControlled', '--no-sandbox']
  });
  
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
  });
  
  const page = await context.newPage();
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
  });
  
  await page.goto('https://account.proton.me/login');
  await page.waitForTimeout(2000);
  
  await page.fill('#username', email);
  await page.fill('#password', password);
  await page.click('button[type=submit]');
  await page.waitForTimeout(3000);
  
  return { browser, context, page };
}
```

### 2. Check Inbox
```javascript
await page.goto('https://mail.proton.me/inbox');
await page.waitForTimeout(2000);

const emails = await page.evaluate(() => {
  return Array.from(document.querySelectorAll('.item')).map(e => ({
    subject: e.querySelector('.subject')?.innerText,
    sender: e.querySelector('.sender')?.innerText,
    time: e.querySelector('.time')?.innerText
  }));
});

console.log(emails);
```

### 3. Read Email
```javascript
await page.click('.item:first-child');
await page.waitForTimeout(2000);

const content = await page.evaluate(() => 
  document.querySelector('.message-content')?.innerText
);
```

### 4. Send Email (Tested & Working)
```javascript
// Navigate to compose
await page.goto('https://mail.proton.me/compose');
await page.waitForTimeout(3000);

// Use keyboard navigation (most reliable)
// Tab to recipient field
await page.keyboard.press('Tab');
await page.waitForTimeout(500);

// Type recipient
await page.keyboard.type('recipient@email.com');
await page.waitForTimeout(500);

// Tab to subject
await page.keyboard.press('Tab');
await page.waitForTimeout(500);

// Type subject
await page.keyboard.type('Your subject here');
await page.waitForTimeout(500);

// Tab to body
await page.keyboard.press('Tab');
await page.waitForTimeout(500);

// Type message
await page.keyboard.type('Your message here...');

// Send with Ctrl+Enter
await page.keyboard.press('Control+Enter');
await page.waitForTimeout(3000);
```

### 5. Logout (please, it's polite)
```javascript
await page.click('button[aria-label="Settings"]');
await page.click('text=Sign out');
await browser.close();
```

## Environment Variables

Don't hardcode passwords (seriously, don't):

```bash
export PROTON_EMAIL="your@email.com"
export PROTON_PASSWORD="yourpassword"
```

Then in code:
```javascript
const email = process.env.PROTON_EMAIL;
const password = process.env.PROTON_PASSWORD;
```

## Complete Example

```javascript
const { chromium } = require('playwright');

async function main() {
  const email = process.env.PROTON_EMAIL || 'your@email.com';
  const password = process.env.PROTON_PASSWORD || 'yourpassword';
  
  const browser = await chromium.launch({ 
    headless: true,
    args: ['--disable-blink-features=AutomationControlled', '--no-sandbox']
  });
  
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
  });
  
  const page = await context.newPage();
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
  });
  
  // Login
  await page.goto('https://account.proton.me/login');
  await page.fill('#username', email);
  await page.fill('#password', password);
  await page.click('button[type=submit]');
  await page.waitForTimeout(5000);
  
  // Go to compose
  await page.goto('https://mail.proton.me/compose');
  await page.waitForTimeout(3000);
  
  // Send email using keyboard navigation (most reliable)
  await page.keyboard.press('Tab');
  await page.keyboard.type('recipient@email.com');
  await page.keyboard.press('Tab');
  await page.keyboard.type('Test Subject');
  await page.keyboard.press('Tab');
  await page.keyboard.type('Hello! This is a test email.');
  await page.keyboard.press('Control+Enter');
  
  await page.waitForTimeout(3000);
  console.log('📧 Email sent!');
  
  await browser.close();
}

main();
```

## Limitations

- **2FA**: Can't do 2FA via automation (use a browser on your device for initial login, then cookie session)
- **Rate limiting**: ProtonMail might throttle you if you go crazy
- **Dynamic UI**: Class names change. Use text selectors or ARIA when possible
- **Headless detection**: Works mostly, but Proton might occasionally notice

## Troubleshooting

### "chromium not found"
```bash
npx playwright install chromium
```

### Bot detection / Login fails
- Verify bot detection bypass is enabled
- Check user agent string is current
- Try headed mode for testing

### Timeout errors
- Increase waitForTimeout values
- Check your internet
- ProtonMail might be rate limiting

### "libX11 not found"
Install system dependencies (see Requirements section)

## Security Notes

- 🔒 Credentials should come from environment variables, not hardcoded
- 🔑 Use app-specific passwords if ProtonMail supports them
- 📝 Always logout when done
- 🍪 Session cookies can be saved for re-use (advanced)

---

**Made with 🦞🔒**

*From Claws for Claws. Because reading emails manually is for plebs.*

*HQ Quality Approved.*
