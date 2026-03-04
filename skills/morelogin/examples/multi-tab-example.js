const puppeteer = require('puppeteer-core');

const CDP_URL = process.env.CDP_URL || 'http://127.0.0.1:9222';

async function main() {
  const browser = await puppeteer.connect({
    browserURL: CDP_URL,
    defaultViewport: null,
  });

  try {
    const page1 = await browser.newPage();
    const page2 = await browser.newPage();

    await page1.goto('https://example.com', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page2.goto('https://github.com', { waitUntil: 'domcontentloaded', timeout: 30000 });

    await Promise.all([
      page1.screenshot({ path: 'page1.png', fullPage: true }),
      page2.screenshot({ path: 'page2.png', fullPage: true }),
    ]);

    console.log('Screenshots completed');
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(`multi-tab-example failed: ${error.message}`);
  process.exit(1);
});
