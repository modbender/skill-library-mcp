#!/usr/bin/env node
// Usage: NODE_PATH=/tmp/node_modules node quote-tweet.js <tweet_url> <quote_text> [--image path] [--port 18802] [--account @handle] [--dry-run]

const { connect, goto, typeIntoComposer, clickSend, attachImages, verifyAccount, dryRunScreenshot, cleanup, sleep, SELECTORS, QUOTE_LABELS, DEFAULT_PORT } = require('./lib/cdp-utils');
const { parseArgs } = require('./lib/args');

const args = parseArgs(process.argv, {
  positional: ['url', 'text'],
  flags: { image: 'string[]', port: 'number', account: 'string', 'dry-run': 'boolean' },
  defaults: { url: '', text: '', image: [], port: DEFAULT_PORT, account: '', 'dry-run': false },
});

if (!args.url || !args.text) {
  console.error('Usage: node quote-tweet.js <tweet_url> "quote text" [--image /path] [--port 18802] [--account @handle] [--dry-run]');
  process.exit(1);
}

(async () => {
  const { browser, newPage } = await connect(args.port);
  const page = await newPage();

  try {
    await goto(page, args.url);
    await verifyAccount(page, args.account || null);

    // Open retweet menu
    const retweetBtn = await page.$(SELECTORS.retweetButton);
    if (!retweetBtn) throw new Error('Retweet button not found');
    await retweetBtn.click();

    // Wait for menu to appear
    await page.waitForSelector('[role="menuitem"]', { timeout: 5000 })
      .catch(() => { throw new Error('Retweet menu did not appear'); });

    // Find and click quote option via page.evaluate (JS click)
    // Must use JS-level click, NOT puppeteer protocol click, so X's SPA router
    // correctly passes the quote context to /compose/post
    const clickResult = await page.evaluate((labels) => {
      const items = document.querySelectorAll('[role="menuitem"]');
      const available = [];
      for (const item of items) {
        const text = item.textContent?.trim();
        available.push(text);
        if (text && labels.some(l => text.toLowerCase().includes(l))) {
          item.click();
          return { ok: true, clicked: text };
        }
      }
      return { ok: false, available };
    }, QUOTE_LABELS);
    if (!clickResult.ok) {
      throw new Error(`Quote option not found. Available: ${JSON.stringify(clickResult.available)}`);
    }

    // Wait for quote composer
    await page.waitForSelector(SELECTORS.tweetTextarea, { timeout: 8000 })
      .catch(() => { throw new Error('Quote composer did not appear'); });

    await typeIntoComposer(page, args.text);

    if (args.image.length > 0) {
      await attachImages(page, args.image);
    }

    if (args['dry-run']) {
      await dryRunScreenshot(page, 'quote-tweet');
      console.log('DRY RUN: Quote composed but not sent.');
      browser.disconnect();
      return;
    }

    await clickSend(page);
    console.log('OK: Quote tweet posted for ' + args.url);
  } catch (e) {
    console.error('FAIL: ' + e.message);
    process.exit(1);
  } finally {
    if (!args['dry-run']) await cleanup(page, browser);
  }
})();
