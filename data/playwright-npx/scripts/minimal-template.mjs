import { chromium } from 'playwright';

/**
 * Minimal Template
 * 
 * A clean starting point for any Playwright script.
 * Copy this file and modify for your needs.
 * 
 * Usage:
 *   cp scripts/minimal-template.mjs tmp/my-task.mjs
 *   node tmp/my-task.mjs
 */

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();

try {
  await page.goto('https://example.com');
  
  // Your code here
  const title = await page.title();
  console.log('Page title:', title);
  
} catch (error) {
  console.error('Error:', error.message);
  await page.screenshot({ path: 'tmp/error.png' });
} finally {
  await browser.close();
}
