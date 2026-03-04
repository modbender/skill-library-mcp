import { chromium } from 'playwright';

/**
 * Scrape Template
 * 
 * Reusable template for web scraping tasks.
 * 
 * Usage:
 *   cp scripts/scrape-template.mjs tmp/my-scrape.mjs
 *   node tmp/my-scrape.mjs [url]
 */

// Configuration
const url = process.argv[2] || 'https://example.com';
const selectors = {
  // Define your selectors here
  items: '.item',
  title: '.title',
  link: 'a'
};

const browser = await chromium.launch();
const page = await browser.newPage();

try {
  console.log(`Scraping ${url}...`);
  await page.goto(url, { waitUntil: 'networkidle' });
  
  // Wait for content to load
  await page.waitForSelector(selectors.items);
  
  // Extract data
  const data = await page.$$eval(selectors.items, (elements, selectors) => {
    return elements.map(el => ({
      title: el.querySelector(selectors.title)?.innerText?.trim(),
      url: el.querySelector(selectors.link)?.href,
      // Add more fields as needed
    }));
  }, selectors);
  
  console.log(`\nFound ${data.length} items:\n`);
  console.log(JSON.stringify(data, null, 2));
  
  // Optional: save to file
  // import fs from 'fs';
  // fs.writeFileSync('tmp/scraped.json', JSON.stringify(data, null, 2));
  
} catch (error) {
  console.error('Error:', error.message);
  
  // Debug: screenshot on error
  await page.screenshot({ path: 'tmp/scrape-error.png' });
  console.log('Error screenshot saved to tmp/scrape-error.png');
  
  process.exit(1);
} finally {
  await browser.close();
}
