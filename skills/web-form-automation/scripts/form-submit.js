const { chromium } = require('playwright');
const fs = require('fs');

/**
 * Generic web form automation template
 * 
 * Usage:
 *   node form-submit.js <config.json>
 * 
 * Config format:
 * {
 *   "url": "https://example.com/form",
 *   "sessionFile": "session.json", // optional
 *   "uploads": [
 *     { "selector": "input[name='file1']", "path": "/path/to/file1.webp" },
 *     { "selector": "input[name='file2']", "path": "/path/to/file2.webp" }
 *   ],
 *   "selects": [
 *     { "selector": "text=Option Name", "value": "Option Value" }
 *   ],
 *   "textInputs": [
 *     { "selector": "textarea", "text": "Your text here", "delay": 30 }
 *   ],
 *   "submitSelector": "button[type='submit']",
 *   "waitTime": 5000,
 *   "screenshot": "result.png"
 * }
 */

async function run(configPath) {
  const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  
  const browser = await chromium.launch({ 
    headless: true, 
    args: ['--no-sandbox', '--disable-setuid-sandbox'] 
  });
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const page = await context.newPage();
  
  // Load session if provided
  if (config.sessionFile && fs.existsSync(config.sessionFile)) {
    console.log('🍪 Loading session...');
    const session = JSON.parse(fs.readFileSync(config.sessionFile, 'utf8'));
    
    // Set cookies
    if (session.cookies) {
      for (const cookie of session.cookies) {
        try {
          await context.addCookies([cookie]);
        } catch (e) {}
      }
    }
    
    // Set storage
    await page.goto(config.url, { waitUntil: 'domcontentloaded', timeout: 10000 });
    if (session.localStorage) {
      await page.evaluate((data) => {
        for (const [k, v] of Object.entries(data)) localStorage.setItem(k, v);
      }, session.localStorage);
    }
    if (session.sessionStorage) {
      await page.evaluate((data) => {
        for (const [k, v] of Object.entries(data)) sessionStorage.setItem(k, v);
      }, session.sessionStorage);
    }
    await page.reload({ waitUntil: 'domcontentloaded' });
  } else {
    await page.goto(config.url, { waitUntil: 'domcontentloaded', timeout: 60000 });
  }
  
  await page.waitForTimeout(3000);
  console.log('🔗 Page loaded');
  
  // Upload files
  if (config.uploads) {
    for (const upload of config.uploads) {
      console.log(`🖼️ Uploading ${upload.path}...`);
      const input = page.locator(upload.selector).first();
      await input.setInputFiles(upload.path);
      await page.waitForTimeout(3000);
    }
  }
  
  // Select options
  if (config.selects) {
    for (const sel of config.selects) {
      console.log(`🎬 Selecting ${sel.value}...`);
      await page.click(sel.selector);
      await page.waitForTimeout(500);
      await page.click(`text=${sel.value}`);
      await page.waitForTimeout(500);
    }
  }
  
  // Type text inputs
  if (config.textInputs) {
    for (const ti of config.textInputs) {
      console.log('📝 Typing text...');
      const input = page.locator(ti.selector).first();
      await input.click();
      await page.waitForTimeout(500);
      await input.pressSequentially(ti.text, { delay: ti.delay || 30 });
      await page.waitForTimeout(2000);
    }
  }
  
  // Screenshot before submit
  if (config.beforeScreenshot) {
    await page.screenshot({ path: config.beforeScreenshot, fullPage: true });
    console.log('📸 Before-submit screenshot saved');
  }
  
  // Submit form
  if (config.submitSelector) {
    console.log('🚀 Submitting...');
    const btn = page.locator(config.submitSelector).first();
    await btn.click({ force: true });
  }
  
  // Wait and screenshot
  const waitTime = config.waitTime || 5000;
  await page.waitForTimeout(waitTime);
  
  if (config.screenshot) {
    await page.screenshot({ path: config.screenshot, fullPage: true });
    console.log(`📸 Screenshot saved: ${config.screenshot}`);
  }
  
  await browser.close();
  console.log('✅ Done');
}

const configPath = process.argv[2];
if (!configPath) {
  console.error('Usage: node form-submit.js <config.json>');
  process.exit(1);
}

run(configPath).catch(console.error);
