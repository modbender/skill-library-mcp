#!/usr/bin/env node
// Usage: NODE_PATH=/tmp/node_modules node post-tweet.js <text> [--image path] [--port 18802] [--account @handle] [--dry-run]

const { connect, goto, typeIntoComposer, clickSend, attachImages, verifyAccount, dryRunScreenshot, cleanup, DEFAULT_PORT } = require('./lib/cdp-utils');
const { parseArgs } = require('./lib/args');

const args = parseArgs(process.argv, {
  positional: ['text'],
  flags: { image: 'string[]', port: 'number', account: 'string', 'dry-run': 'boolean' },
  defaults: { text: '', image: [], port: DEFAULT_PORT, account: '', 'dry-run': false },
});

if (!args.text) {
  console.error('Usage: node post-tweet.js "tweet text" [--image /path] [--port 18802] [--account @handle] [--dry-run]');
  process.exit(1);
}

(async () => {
  const { browser, newPage } = await connect(args.port);
  const page = await newPage();

  try {
    await goto(page, 'https://x.com/home');
    await verifyAccount(page, args.account || null);

    await goto(page, 'https://x.com/compose/post');
    await typeIntoComposer(page, args.text);

    if (args.image.length > 0) {
      await attachImages(page, args.image);
    }

    if (args['dry-run']) {
      await dryRunScreenshot(page, 'post-tweet');
      console.log('DRY RUN: Tweet composed but not sent.');
      browser.disconnect();
      return;
    }

    await clickSend(page);
    console.log('OK: Tweet posted');
  } catch (e) {
    console.error('FAIL: ' + e.message);
    process.exit(1);
  } finally {
    if (!args['dry-run']) await cleanup(page, browser);
  }
})();
