const { test } = require('playwright/test');
const path = require('path');
const fs = require('fs');

const imagePath = path.resolve(__dirname, 'test.png');
const outDir = path.resolve(__dirname, 'verification-artifacts');
const logPath = path.join(outDir, 'run-log.txt');

function log(lines, msg) {
  const line = `[${new Date().toISOString()}] ${msg}`;
  lines.push(line);
  // eslint-disable-next-line no-console
  console.log(line);
}

async function tryClickFirstVisible(page, selectors, lines) {
  for (const selector of selectors) {
    const locator = page.locator(selector).first();
    try {
      if (await locator.isVisible({ timeout: 2000 })) {
        await locator.click({ timeout: 5000 });
        log(lines, `clicked selector: ${selector}`);
        return true;
      }
    } catch {}
  }
  return false;
}

test('verify taobao image search flow with test.png', async ({ page }) => {
  if (!fs.existsSync(imagePath)) {
    throw new Error(`image not found: ${imagePath}`);
  }

  fs.mkdirSync(outDir, { recursive: true });
  const lines = [];

  page.on('console', msg => log(lines, `browser console [${msg.type()}]: ${msg.text().slice(0, 180)}`));
  page.on('pageerror', err => log(lines, `pageerror: ${err.message}`));
  page.on('response', res => {
    if (res.status() >= 400) {
      log(lines, `http ${res.status()} ${res.url().slice(0, 180)}`);
    }
  });

  log(lines, `image path: ${imagePath}`);
  await page.goto('https://www.taobao.com', { waitUntil: 'domcontentloaded', timeout: 90000 });
  await page.waitForTimeout(4000);
  await page.screenshot({ path: path.join(outDir, '01-home.png'), fullPage: true });
  log(lines, 'captured homepage screenshot');

  const cameraSelectors = [
    "text=搜同款",
    "text=拍立淘",
    "text=相机",
    "[aria-label*='相机']",
    "[class*='camera']",
    "[class*='image-search']",
    "[class*='search-suggest-image-search']"
  ];

  const clicked = await tryClickFirstVisible(page, cameraSelectors, lines);
  if (!clicked) {
    log(lines, 'no camera入口 found by selector; continue with direct file input lookup');
  }

  await page.waitForTimeout(2500);

  const contexts = [page, ...page.frames()];
  let uploaded = false;
  for (const ctx of contexts) {
    const name = ctx === page ? 'main-page' : `frame:${ctx.url().slice(0, 120)}`;
    const inputs = ctx.locator("input[type='file']");
    const count = await inputs.count();
    if (!count) continue;

    for (let i = 0; i < count; i++) {
      try {
        await inputs.nth(i).setInputFiles(imagePath, { timeout: 7000 });
        log(lines, `uploaded via ${name} input#${i}`);
        uploaded = true;
        break;
      } catch (e) {
        log(lines, `upload failed via ${name} input#${i}: ${String(e.message || e).slice(0, 180)}`);
      }
    }
    if (uploaded) break;
  }

  if (!uploaded) {
    await page.screenshot({ path: path.join(outDir, '02-no-upload-input.png'), fullPage: true });
    fs.writeFileSync(logPath, lines.join('\n'));
    throw new Error('no usable file input found for image upload');
  }

  await page.waitForTimeout(7000);
  await page.screenshot({ path: path.join(outDir, '03-after-upload.png'), fullPage: true });
  log(lines, 'captured post-upload screenshot');

  const titleCandidates = await page.locator('a').allInnerTexts();
  const sampledTitles = titleCandidates
    .map(s => s.trim())
    .filter(Boolean)
    .filter(t => t.length >= 6 && t.length <= 80)
    .slice(0, 15);

  log(lines, `sample titles: ${JSON.stringify(sampledTitles)}`);

  fs.writeFileSync(logPath, lines.join('\n'));
});
