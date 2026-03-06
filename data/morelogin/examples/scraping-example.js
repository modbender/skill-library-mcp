const fs = require('fs');
const puppeteer = require('puppeteer-core');

const CDP_URL = process.env.CDP_URL || 'http://127.0.0.1:9222';
const TARGET_URL = process.env.SCRAPE_URL || 'https://example.com/products';

async function main() {
  const browser = await puppeteer.connect({
    browserURL: CDP_URL,
    defaultViewport: null,
  });

  try {
    const page = await browser.newPage();
    await page.goto(TARGET_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });

    const products = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('.product')).map((el) => ({
        name: el.querySelector('.name')?.textContent?.trim() || '',
        price: el.querySelector('.price')?.textContent?.trim() || '',
        url: el.querySelector('a')?.href || '',
      }));
    });

    fs.writeFileSync('products.json', `${JSON.stringify(products, null, 2)}\n`, 'utf8');
    console.log(`Scraped ${products.length} products`);
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(`scraping-example failed: ${error.message}`);
  process.exit(1);
});
