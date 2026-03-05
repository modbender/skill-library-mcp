import { chromium } from 'playwright';

/**
 * Screenshot Example
 * Takes a full-page screenshot of a website.
 * 
 * Usage: node examples/screenshot.mjs <url> [output-path]
 */

const url = process.argv[2] || 'https://example.com';
const outputPath = process.argv[3] || 'tmp/screenshot.png';

const browser = await chromium.launch();
const page = await browser.newPage();

// Set viewport for consistent screenshots
await page.setViewportSize({ width: 1280, height: 800 });

console.log(`Navigating to ${url}...`);
await page.goto(url, { waitUntil: 'networkidle' });

// Wait a moment for any final renders
await page.waitForTimeout(500);

// Take screenshot
await page.screenshot({ path: outputPath, fullPage: true });
console.log(`Screenshot saved to ${outputPath}`);

await browser.close();
