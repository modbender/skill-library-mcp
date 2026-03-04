import { chromium } from 'playwright';

/**
 * Web Scraping Example
 * Extracts article titles and links from Hacker News.
 * 
 * Usage: node examples/scrape.mjs [url]
 */

const url = process.argv[2] || 'https://news.ycombinator.com';

const browser = await chromium.launch();
const page = await browser.newPage();

console.log(`Scraping ${url}...`);
await page.goto(url, { waitUntil: 'networkidle' });

// Extract data using page.$$eval
const stories = await page.$$eval('.titleline > a', links =>
  links.slice(0, 10).map(a => ({
    title: a.innerText.trim(),
    url: a.href
  }))
);

console.log(`\nFound ${stories.length} stories:\n`);
console.log(JSON.stringify(stories, null, 2));

await browser.close();
