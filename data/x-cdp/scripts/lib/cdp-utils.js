/**
 * Shared CDP utilities for X (Twitter) automation.
 * All scripts connect to a local Chromium instance via puppeteer-core.
 */

module.paths.unshift('/tmp/node_modules');
const puppeteer = require('puppeteer-core');
const fs = require('fs');

const DEFAULT_PORT = 18802;
const SELECTORS = {
  tweetTextarea: '[data-testid="tweetTextarea_0"]',
  tweetButton: '[data-testid="tweetButton"]',
  tweetButtonInline: '[data-testid="tweetButtonInline"]',
  replyButton: '[data-testid="reply"]',
  retweetButton: '[data-testid="retweet"]',
  unretweetConfirm: '[data-testid="unretweetConfirm"]',
  retweetConfirm: '[data-testid="retweetConfirm"]',
  fileInput: 'input[type="file"][accept*="image"]',
  // Article editor
  articleCreateBtn: '[aria-label="create"]',
  articleTitle: 'textarea[placeholder="添加标题"], textarea[placeholder="Add a title"]',
  articleComposer: '[data-testid="composer"]',
  // Format menu
  menuItem: '[role="menuitem"]',
};

// Quote menu text variants by locale
const QUOTE_LABELS = ['quote', 'quote post', '引用', '引用帖子'];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/**
 * Connect to Chromium CDP with error handling.
 * @param {number} port - debugging port (default 18802)
 * @returns {{ browser, newPage: () => Promise<Page> }}
 */
async function connect(port = DEFAULT_PORT) {
  let browser;
  try {
    browser = await puppeteer.connect({
      browserURL: `http://localhost:${port}`,
    });
  } catch (e) {
    console.error(`FAIL: Cannot connect to Chromium on port ${port}.`);
    console.error(`  Is Chromium running with --remote-debugging-port=${port}?`);
    console.error(`  Original error: ${e.message}`);
    process.exit(1);
  }
  return {
    browser,
    async newPage() {
      return browser.newPage();
    },
  };
}

/**
 * Navigate and wait for page to settle.
 */
async function goto(page, url, { timeout = 25000 } = {}) {
  await page.goto(url, { waitUntil: 'networkidle2', timeout });
  await sleep(2500);
}

/**
 * Wait for and type into the tweet composer.
 * Handles both inline and modal composers.
 */
async function typeIntoComposer(page, text) {
  const editor = await page.waitForSelector(SELECTORS.tweetTextarea, { timeout: 10000 })
    .catch(() => null);
  if (!editor) throw new Error('Tweet editor not found. Page may not have loaded correctly.');
  await editor.click();
  await sleep(300);
  await page.keyboard.type(text, { delay: 25 });
  await sleep(500);
}

/**
 * Click the send/post button. Waits for button to be enabled.
 */
async function clickSend(page) {
  await sleep(500);
  // Wait for either button variant
  let btn = await page.$(SELECTORS.tweetButton);
  if (!btn) btn = await page.$(SELECTORS.tweetButtonInline);
  if (!btn) throw new Error('Send button not found');

  // Wait for button to be enabled
  await page.waitForFunction(
    (sel1, sel2) => {
      const b = document.querySelector(sel1) || document.querySelector(sel2);
      return b && !b.disabled;
    },
    { timeout: 5000 },
    SELECTORS.tweetButton,
    SELECTORS.tweetButtonInline
  ).catch(() => {});

  await btn.click();
  await sleep(3000);
}

/**
 * Attach images to the composer (up to 4).
 * Validates file paths before upload and waits for preview.
 * @param {Page} page
 * @param {string[]} imagePaths - absolute paths to images
 */
async function attachImages(page, imagePaths) {
  if (!imagePaths || imagePaths.length === 0) return;

  // Validate all paths first
  for (const p of imagePaths) {
    if (!fs.existsSync(p)) {
      throw new Error(`Image file not found: ${p}`);
    }
  }

  const fileInput = await page.$('input[type="file"][accept*="image"]');
  if (!fileInput) throw new Error('Image file input not found');

  for (let idx = 0; idx < Math.min(imagePaths.length, 4); idx++) {
    await fileInput.uploadFile(imagePaths[idx]);
    await sleep(1500);
    // Wait for image preview to appear
    const preview = await page.waitForSelector('[data-testid="attachments"] img, [data-testid="tweetPhoto"] img', { timeout: 8000 })
      .catch(() => null);
    if (!preview) {
      throw new Error(`Image upload failed or preview not detected for: ${imagePaths[idx]}`);
    }
  }
}

/**
 * Get the currently logged-in handle from the page.
 * @returns {string|null} handle like "@yourhandle" or null
 */
async function getLoggedInHandle(page) {
  return page.evaluate(() => {
    const btn = document.querySelector('[data-testid="SideNav_AccountSwitcher_Button"]');
    if (!btn) return null;
    const text = btn.textContent || '';
    const match = text.match(/@\w+/);
    return match ? match[0] : null;
  }).catch(() => null);
}

/**
 * Verify the logged-in account matches expected handle.
 * Logs account and optionally enforces match.
 * @param {Page} page
 * @param {string} [expectedHandle] - if provided, exits on mismatch
 */
async function verifyAccount(page, expectedHandle) {
  const handle = await getLoggedInHandle(page);
  if (handle) console.log(`Account: ${handle}`);
  if (expectedHandle && handle && handle.toLowerCase() !== expectedHandle.toLowerCase()) {
    console.error(`FAIL: Expected account ${expectedHandle} but got ${handle}`);
    process.exit(1);
  }
  return handle;
}

/**
 * Take a dry-run screenshot.
 * @param {Page} page
 * @param {string} label - descriptive label for the file
 * @returns {string} path to screenshot
 */
async function dryRunScreenshot(page, label) {
  const path = `/tmp/x-cdp-dryrun-${label}-${Date.now()}.png`;
  await page.screenshot({ path, fullPage: false });
  console.log(`DRY RUN screenshot: ${path}`);
  return path;
}

/**
 * Clean up: close page, disconnect browser (never browser.close()).
 */
async function cleanup(page, browser) {
  try { if (page) await page.close(); } catch (_) {}
  try { if (browser) browser.disconnect(); } catch (_) {}
}

module.exports = {
  SELECTORS,
  QUOTE_LABELS,
  sleep,
  connect,
  goto,
  typeIntoComposer,
  clickSend,
  attachImages,
  getLoggedInHandle,
  verifyAccount,
  dryRunScreenshot,
  cleanup,
  DEFAULT_PORT,
};
