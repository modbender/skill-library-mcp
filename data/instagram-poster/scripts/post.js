#!/usr/bin/env node
/**
 * Instagram Auto-Poster
 * Uses Human Browser (residential proxy) to post images to Instagram
 *
 * Usage:
 *   node post.js --image ./photo.jpg --caption "Hello world 🌍" --user USERNAME --pass PASSWORD
 *   node post.js --image https://example.com/image.jpg --caption "..." --user u --pass p
 *   node post.js --image ./photo.jpg --caption "..." --session /tmp/ig-session.json
 *
 * Env vars:
 *   IG_USERNAME, IG_PASSWORD, IG_SESSION_PATH
 */

const path = require('path');
const fs   = require('fs');
const https = require('https');
const os   = require('os');

// --- Args ---
const args = process.argv.slice(2);
const get  = (flag) => { const i = args.indexOf(flag); return i !== -1 ? args[i + 1] : null; };

const imageArg    = get('--image')   || process.env.IG_IMAGE;
const caption     = get('--caption') || process.env.IG_CAPTION || '';
const username    = get('--user')    || process.env.IG_USERNAME;
const password    = get('--pass')    || process.env.IG_PASSWORD;
const sessionPath = get('--session') || process.env.IG_SESSION_PATH || path.join(os.homedir(), '.openclaw', 'ig-session.json');

if (!imageArg) { console.error('❌  --image required'); process.exit(1); }
if (!username && !fs.existsSync(sessionPath)) {
  console.error('❌  --user / --pass required (or saved session at', sessionPath, ')');
  process.exit(1);
}

// --- Helpers ---
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function downloadImage(url, dest) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(dest);
    https.get(url, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        file.close();
        downloadImage(res.headers.location, dest).then(resolve).catch(reject);
        return;
      }
      res.pipe(file);
      file.on('finish', () => file.close(resolve));
    }).on('error', (e) => { fs.unlink(dest, () => {}); reject(e); });
  });
}

// --- Main ---
(async () => {
  const { launchHuman, getTrial } = require(
    path.resolve(__dirname, '../../../human-browser/scripts/browser-human')
  );

  // Resolve image to local file
  let localImage = imageArg;
  if (imageArg.startsWith('http://') || imageArg.startsWith('https://')) {
    const tmp = path.join(os.tmpdir(), `ig-upload-${Date.now()}.jpg`);
    console.log('📥  Downloading image...');
    await downloadImage(imageArg, tmp);
    localImage = tmp;
    console.log('✅  Downloaded to', tmp);
  } else {
    localImage = path.resolve(imageArg);
  }

  if (!fs.existsSync(localImage)) {
    console.error('❌  Image file not found:', localImage);
    process.exit(1);
  }

  // Get residential proxy
  console.log('🌐  Connecting via residential proxy...');
  await getTrial();

  const { browser, page } = await launchHuman({ mobile: false });
  console.log('✅  Browser ready');

  try {
    // --- Login or restore session ---
    if (fs.existsSync(sessionPath)) {
      console.log('🍪  Restoring session from', sessionPath);
      const ctx = browser.contexts()[0];
      const saved = JSON.parse(fs.readFileSync(sessionPath, 'utf8'));
      await ctx.addCookies(saved);
      await page.goto('https://www.instagram.com/', { waitUntil: 'networkidle', timeout: 30000 });
      await sleep(3000);

      // Check if still logged in
      const isLoggedIn = await page.evaluate(() => {
        return !document.querySelector('input[name="username"]');
      });

      if (!isLoggedIn) {
        console.log('⚠️   Session expired, logging in fresh...');
        fs.unlinkSync(sessionPath);
        await doLogin(page, username, password);
        await saveSession(browser, sessionPath);
      } else {
        console.log('✅  Session valid');
      }
    } else {
      await page.goto('https://www.instagram.com/accounts/login/', { waitUntil: 'networkidle', timeout: 30000 });
      await sleep(3000);
      await doLogin(page, username, password);
      await saveSession(browser, sessionPath);
    }

    // --- Post image ---
    console.log('📸  Starting post flow...');
    await sleep(2000);

    // Click the Create/+ button (new post)
    // Try multiple selectors for the create button
    let createClicked = false;

    // Method 1: aria-label
    try {
      await page.click('[aria-label="New post"]', { timeout: 5000 });
      createClicked = true;
      console.log('✅  Clicked New post (aria-label)');
    } catch {}

    // Method 2: SVG-based create button
    if (!createClicked) {
      try {
        const createBtn = await page.evaluateHandle(() => {
          const links = document.querySelectorAll('a[href], button');
          for (const el of links) {
            const text = el.getAttribute('aria-label') || el.textContent || '';
            if (text.toLowerCase().includes('new post') || text.toLowerCase().includes('create')) {
              return el;
            }
          }
          return null;
        });
        if (createBtn) {
          await createBtn.click();
          createClicked = true;
          console.log('✅  Clicked create button');
        }
      } catch {}
    }

    // Method 3: Navigate directly to create flow
    if (!createClicked) {
      console.log('⚠️   Trying direct navigation to create...');
      await page.goto('https://www.instagram.com/', { waitUntil: 'networkidle', timeout: 20000 });
      await sleep(2000);

      // Look for + button in navbar
      const svgClicked = await page.evaluate(() => {
        const svgs = document.querySelectorAll('svg[aria-label]');
        for (const svg of svgs) {
          const lbl = svg.getAttribute('aria-label') || '';
          if (lbl.toLowerCase().includes('new post') || lbl.toLowerCase().includes('create')) {
            svg.closest('a, button, div[role="button"]')?.click();
            return true;
          }
        }
        return false;
      });
      if (svgClicked) createClicked = true;
    }

    if (!createClicked) {
      throw new Error('Could not find Create/New Post button. Instagram UI may have changed.');
    }

    await sleep(2000);

    // Upload file input (Instagram uses a hidden file input)
    const [fileChooser] = await Promise.all([
      page.waitForFileChooser({ timeout: 10000 }).catch(() => null),
      page.click('input[type="file"]').catch(async () => {
        // Sometimes the file input is hidden — trigger it
        await page.evaluate(() => {
          const input = document.querySelector('input[type="file"]');
          if (input) input.click();
        });
      })
    ]);

    if (fileChooser) {
      await fileChooser.setFiles(localImage);
    } else {
      // Direct set via input element
      const input = await page.$('input[type="file"]');
      if (!input) throw new Error('No file input found');
      await input.setInputFiles(localImage);
    }
    console.log('✅  Image uploaded');
    await sleep(3000);

    // Click "Next" (may appear multiple times - aspect ratio → filters → caption)
    for (let i = 0; i < 3; i++) {
      const nextBtn = await page.$('button:has-text("Next")') ||
                      await page.evaluateHandle(() => {
                        const btns = document.querySelectorAll('button');
                        for (const b of btns) {
                          if (b.textContent.trim() === 'Next') return b;
                        }
                        return null;
                      });
      if (nextBtn) {
        await nextBtn.click();
        console.log(`✅  Clicked Next (step ${i + 1})`);
        await sleep(2500);
      } else {
        break;
      }
    }

    // Add caption
    if (caption) {
      const captionArea = await page.$('div[aria-label="Write a caption..."]') ||
                          await page.$('[contenteditable="true"]') ||
                          await page.$('textarea');

      if (captionArea) {
        await captionArea.click();
        await sleep(500);
        await page.keyboard.type(caption, { delay: 30 });
        console.log('✅  Caption added');
      } else {
        console.warn('⚠️   Caption field not found — posting without caption');
      }
      await sleep(1000);
    }

    // Click Share
    const shareBtn = await page.$('button:has-text("Share")') ||
                     await page.evaluateHandle(() => {
                       const btns = document.querySelectorAll('button');
                       for (const b of btns) {
                         if (b.textContent.trim() === 'Share') return b;
                       }
                       return null;
                     });

    if (!shareBtn) throw new Error('Share button not found');
    await shareBtn.click();
    console.log('🚀  Share clicked!');

    // Wait for confirmation
    await sleep(5000);
    const posted = await page.evaluate(() => {
      return document.body.innerText.includes('Your post has been shared') ||
             document.body.innerText.includes('Post shared') ||
             document.querySelector('[aria-label="Post shared"]') !== null;
    });

    if (posted) {
      console.log('🎉  Post published successfully!');
    } else {
      console.log('✅  Share button clicked. Check your Instagram profile to confirm.');
    }

  } finally {
    await browser.close();
    console.log('🏁  Done');
  }
})();

// --- Helpers ---

async function doLogin(page, user, pass) {
  if (!user || !pass) {
    throw new Error('Username and password required for fresh login');
  }
  console.log('🔐  Logging in as', user);

  try {
    await page.waitForSelector('input[name="username"]', { timeout: 15000 });
  } catch {
    throw new Error('Login form not found. Instagram may have changed their UI.');
  }

  await page.locator('input[name="username"]').fill(user);
  await sleep(800);
  await page.locator('input[name="password"]').fill(pass);
  await sleep(1000);
  await page.keyboard.press('Enter');
  await sleep(8000);

  // Handle "Save login info?" dialog
  const saveBtn = await page.$('button:has-text("Save info")');
  if (saveBtn) { await saveBtn.click(); await sleep(1000); }

  // Handle "Turn on notifications?" dialog
  const notNow = await page.$('button:has-text("Not now")');
  if (notNow) { await notNow.click(); await sleep(1000); }

  console.log('✅  Logged in');
}

async function saveSession(browser, sessionPath) {
  const ctx = browser.contexts()[0];
  const cookies = await ctx.cookies();
  fs.mkdirSync(path.dirname(sessionPath), { recursive: true });
  fs.writeFileSync(sessionPath, JSON.stringify(cookies, null, 2));
  console.log('💾  Session saved to', sessionPath);
}
