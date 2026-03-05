#!/usr/bin/env node
// Usage: NODE_PATH=/tmp/node_modules node reply-tweet.js <tweet_url> <reply_text> [--image path] [--port 18802] [--account @handle] [--dry-run]

const { connect, goto, clickSend, attachImages, verifyAccount, dryRunScreenshot, cleanup, sleep, SELECTORS, DEFAULT_PORT } = require('./lib/cdp-utils');
const { parseArgs } = require('./lib/args');

const args = parseArgs(process.argv, {
  positional: ['url', 'text'],
  flags: { image: 'string[]', port: 'number', account: 'string', 'dry-run': 'boolean' },
  defaults: { url: '', text: '', image: [], port: DEFAULT_PORT, account: '', 'dry-run': false },
});

if (!args.url || !args.text) {
  console.error('Usage: node reply-tweet.js <tweet_url> "reply text" [--image /path] [--port 18802] [--account @handle] [--dry-run]');
  process.exit(1);
}

(async () => {
  const { browser, newPage } = await connect(args.port);
  const page = await newPage();

  try {
    await goto(page, args.url);
    await verifyAccount(page, args.account || null);

    // Click reply button and wait for editor
    const replyBtn = await page.$(SELECTORS.replyButton);
    if (!replyBtn) throw new Error('Reply button not found on this tweet');
    await replyBtn.click();

    const editor = await page.waitForSelector(SELECTORS.tweetTextarea, { timeout: 10000 })
      .catch(() => null);
    if (!editor) throw new Error('Reply editor did not appear');
    await editor.click();
    await sleep(300);
    await page.keyboard.type(args.text, { delay: 25 });
    await sleep(500);

    if (args.image.length > 0) {
      await attachImages(page, args.image);
    }

    if (args['dry-run']) {
      await dryRunScreenshot(page, 'reply-tweet');
      console.log('DRY RUN: Reply composed but not sent.');
      browser.disconnect();
      return;
    }

    await clickSend(page);
    console.log('OK: Reply sent to ' + args.url);
  } catch (e) {
    console.error('FAIL: ' + e.message);
    process.exit(1);
  } finally {
    if (!args['dry-run']) await cleanup(page, browser);
  }
})();
