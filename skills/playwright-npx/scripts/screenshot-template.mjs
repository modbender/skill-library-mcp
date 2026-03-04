import { chromium } from 'playwright';

/**
 * Screenshot Template
 * 
 * Reusable template for capturing screenshots.
 * 
 * Usage:
 *   cp scripts/screenshot-template.mjs tmp/my-screenshot.mjs
 *   node tmp/my-screenshot.mjs [url] [output.png]
 */

// Configuration
const url = process.argv[2] || 'https://example.com';
const outputPath = process.argv[3] || 'tmp/screenshot.png';
const viewport = { width: 1280, height: 800 };
const fullPage = true;

const browser = await chromium.launch();
const page = await browser.newPage();

// Set viewport for consistent screenshots
await page.setViewportSize(viewport);

try {
  console.log(`Navigating to ${url}...`);
  await page.goto(url, { 
    waitUntil: 'networkidle',
    timeout: 30000 
  });
  
  // Optional: wait for specific element
  // await page.waitForSelector('.loaded-indicator');
  
  // Optional: additional wait for animations
  await page.waitForTimeout(500);
  
  // Take screenshot
  await page.screenshot({ 
    path: outputPath, 
    fullPage 
  });
  
  console.log(`✓ Screenshot saved: ${outputPath}`);
  
} catch (error) {
  console.error('✗ Error:', error.message);
  process.exit(1);
} finally {
  await browser.close();
}
