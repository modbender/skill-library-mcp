const puppeteer = require('puppeteer-core');

const CDP_URL = process.env.CDP_URL || 'http://127.0.0.1:9222';

async function main() {
  const browser = await puppeteer.connect({
    browserURL: CDP_URL,
    defaultViewport: null,
  });

  try {
    const page = await browser.newPage();
    await page.goto('https://example.com', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.screenshot({ path: 'basic-example.png', fullPage: true });
    console.log('Title:', await page.title());
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(`basic-example failed: ${error.message}`);
  process.exit(1);
});
