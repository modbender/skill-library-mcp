#!/usr/bin/env node
/**
 * ChatGPT Image Generation Skill
 * Uses Playwright to automate ChatGPT web UI for free image generation.
 * 
 * Usage:
 *   node generate.js --prompts prompts.json --output ./images
 *   node generate.js --prompts prompts.json --output ./images --start 5
 *   node generate.js --prompts prompts.json --output ./images --profile "~/Library/Application Support/Google/Chrome/Default"
 *   node generate.js --prompts prompts.json --output ./images --headless
 * 
 * Prerequisites:
 *   npm install playwright
 *   npx playwright install chromium
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const os = require('os');

// Cross-platform default Chrome profile path
function getDefaultProfilePath() {
  const home = os.homedir();
  const platform = process.platform;
  
  if (platform === 'darwin') {
    // macOS
    return path.join(home, 'Library', 'Application Support', 'Google', 'Chrome', 'Default');
  } else if (platform === 'win32') {
    // Windows
    return path.join(home, 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default');
  } else {
    // Linux
    return path.join(home, '.config', 'google-chrome', 'Default');
  }
}

const DEFAULT_PROFILE_PATH = getDefaultProfilePath();

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = { start: 0, headless: false };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--prompts' && args[i + 1]) opts.promptsPath = args[++i];
    else if (args[i] === '--output' && args[i + 1]) opts.outputDir = args[++i];
    else if (args[i] === '--start' && args[i + 1]) opts.start = parseInt(args[++i], 10);
    else if (args[i] === '--profile' && args[i + 1]) opts.profilePath = args[++i];
    else if (args[i] === '--headless') opts.headless = true;
  }
  if (!opts.promptsPath || !opts.outputDir) {
    console.error('Usage: node generate.js --prompts prompts.json --output ./images [--start N] [--profile path] [--headless]');
    process.exit(1);
  }
  return opts;
}

function loadPrompts(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const data = JSON.parse(content);
  if (Array.isArray(data)) return data;
  if (data.prompts && Array.isArray(data.prompts)) return data.prompts;
  throw new Error('Invalid prompts format');
}

function ensureDir(dir) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

function logResults(resultsPath, entry) {
  fs.appendFileSync(resultsPath, JSON.stringify(entry) + '\n');
}

async function waitForSendButtonEnabled(page, timeout = 180000) {
  console.log('  → Waiting for send button to enable...');
  
  // Try multiple selectors
  const selectors = [
    'button[data-testid="send-button"]:',
    'buttonnot([disabled])[aria-label="Send message"]:not([disabled])',
    'button:not([disabled]):has(svg[mask*="send"])'
  ];
  
  for (const sel of selectors) {
    try {
      await page.waitForSelector(sel, { timeout: 5000, state: 'visible' });
      console.log('  → Send button enabled');
      return true;
    } catch (e) {}
  }
  
  // Fallback: just wait for any button to be enabled
  console.log('  → Using fallback wait');
  await page.waitForTimeout(5000);
  return true;
}

async function waitForImageFullyReady(page, timeout = 180000) {
  console.log('  → Waiting for image to be fully ready...');
  const deadline = Date.now() + timeout;
  let lastSrc = null;
  let stableCount = 0;

  while (Date.now() < deadline) {
    const state = await page.evaluate(() => {
      const imgs = Array.from(document.querySelectorAll('img[alt="Generated image"], img[alt*="Generated"]'));
      const img = imgs.length ? imgs[imgs.length - 1] : null;
      const src = img?.src || null;
      const w = img?.naturalWidth || 0;
      const h = img?.naturalHeight || 0;
      
      // Check for download button
      const dlButtons = Array.from(document.querySelectorAll('button[aria-label*="Download"], button[aria-label*="download"]'));
      const dlBtn = dlButtons.length ? dlButtons[dlButtons.length - 1] : null;
      const dlReady = dlBtn && !dlBtn.disabled && dlBtn.offsetParent !== null;
      
      // Check for progress
      const progress = document.querySelector('[role="progressbar"], .animate-spin');
      const hasProgress = progress && progress.offsetParent !== null;
      
      return { src, w, h, dlReady, hasProgress };
    });

    const { src, w, h, dlReady, hasProgress } = state;
    const dimsOk = w >= 1024 && h >= 1024;

    if (src === lastSrc) {
      stableCount++;
    } else {
      stableCount = 0;
      lastSrc = src;
    }

    // Debug output
    console.log(`    → src: ${src ? 'yes' : 'no'}, dims: ${w}x${h}, dlReady: ${dlReady}, stable: ${stableCount}, progress: ${hasProgress}`);

    if (src && dimsOk && dlReady && stableCount >= 2 && !hasProgress) {
      console.log('  → Image fully ready!');
      return true;
    }

    await new Promise(r => setTimeout(r, 1500));
  }

  console.log('  → Timeout waiting for image ready, proceeding anyway');
  return false;
}

async function downloadImage(page, outputPath) {
  console.log('  → Hovering over image to reveal download button...');
  
  // Hover on the generated image
  const imgSelector = 'img[alt="Generated image"], img[alt*="Generated"]';
  await page.hover(imgSelector);
  await new Promise(r => setTimeout(r, 500));

  // Find and click download button
  console.log('  → Clicking download button...');
  
  const downloadPromise = page.waitForEvent('download', { timeout: 30000 });
  
  // Click the download button
  await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll('button[aria-label*="Download"], button[aria-label*="download"]'));
    const btn = buttons[buttons.length - 1];
    if (btn) btn.click();
  });
  
  try {
    const download = await downloadPromise;
    await download.saveAs(outputPath);
    console.log(`  → Saved: ${outputPath}`);
    return true;
  } catch (e) {
    console.log('  → Download button click failed, trying direct image fetch...');
    
    // Fallback: direct fetch
    const src = await page.evaluate(() => {
      const imgs = Array.from(document.querySelectorAll('img[alt="Generated image"]'));
      return imgs.length ? imgs[imgs.length - 1].src : null;
    });
    
    if (src) {
      const response = await page.request.get(src);
      const buffer = await response.body();
      if (buffer.length > 5000) {
        fs.writeFileSync(outputPath, buffer);
        console.log(`  → Saved via direct fetch: ${outputPath}`);
        return true;
      }
    }
    
    console.log('  → Failed to download image');
    return false;
  }
}

async function sendNewMessage(page, prompt) {
  console.log('  → Sending new message...');
  
  // Try multiple selectors for the input textarea (ChatGPT UI changes frequently)
  const selectors = [
    'textarea[data-testid="prompt-textarea"]',
    'textarea[placeholder*="Message"]',
    'div[contenteditable="true"][role="textbox"]',
    'div[contenteditable="true"]'
  ];
  
  let textarea = null;
  for (const sel of selectors) {
    try {
      textarea = await page.$(sel);
      if (textarea && await textarea.isVisible()) {
        console.log(`  → Found input with selector: ${sel}`);
        break;
      }
    } catch (e) {}
  }
  
  if (!textarea) {
    throw new Error('Could not find ChatGPT input textarea');
  }
  
  await textarea.fill('');
  await textarea.type(prompt, { delay: 20 });
  
  // Try multiple selectors for send button
  const sendSelectors = [
    'button[data-testid="send-button"]',
    'button[aria-label="Send message"]',
    'button:has(svg[mask*="send"])',
    'form button[type="submit"]'
  ];
  
  let sendBtn = null;
  for (const sel of sendSelectors) {
    try {
      sendBtn = await page.$(sel);
      if (sendBtn && await sendBtn.isVisible()) {
        break;
      }
    } catch (e) {}
  }
  
  if (sendBtn) {
    await sendBtn.click();
  } else {
    // Try pressing Enter instead
    await textarea.press('Enter');
  }
  
  console.log('  → Message sent, waiting for generation...');
}

async function generateImages(opts) {
  const prompts = loadPrompts(opts.promptsPath);
  const outputDir = opts.outputDir;
  const startIdx = opts.start || 0;
  
  // Expand ~ to home directory
  let profilePath = opts.profilePath || DEFAULT_PROFILE_PATH;
  if (profilePath.startsWith('~')) {
    profilePath = path.join(os.homedir(), profilePath.slice(1));
  }
  
  const resultsPath = path.join(outputDir, 'results.jsonl');

  ensureDir(outputDir);
  ensureDir(profilePath);

  console.log(`\n=== ChatGPT Image Generation ===`);
  console.log(`Prompts: ${opts.promptsPath}`);
  console.log(`Output: ${outputDir}`);
  console.log(`Start index: ${startIdx}`);
  console.log(`Profile: ${profilePath}`);
  console.log(`Headless: ${opts.headless}\n`);

  // Remove singleton lock if exists (allows running while Chrome is open)
  const lockFile = path.join(profilePath, 'SingletonLock');
  if (fs.existsSync(lockFile)) {
    try {
      fs.unlinkSync(lockFile);
      console.log('→ Removed stale SingletonLock\n');
    } catch (e) {}
  }

  const context = await chromium.launchPersistentContext(profilePath, {
    headless: opts.headless,
    args: ['--disable-blink-features=AutomationControlled']
  });

  const page = await context.newPage();

  // Navigate to ChatGPT
  console.log('→ Opening chatgpt.com...');
  await page.goto('https://chatgpt.com/', { waitUntil: 'domcontentloaded', timeout: 30000 });
  
  // Wait for page to settle
  await page.waitForTimeout(3000);

  // Check if logged in
  const needsLogin = await page.$('text=Log in') !== null || await page.$('text=Sign up') !== null;
  if (needsLogin) {
    console.log('⚠️ Not logged in! Please sign in to ChatGPT in the browser, then press Enter...');
    await new Promise(r => {
      process.stdin.once('data', () => r());
    });
  }

  // Start a new chat (don't select any project)
  console.log('→ Starting new chat...');

  let successCount = 0;
  let failCount = 0;

  for (let i = startIdx; i < prompts.length; i++) {
    const prompt = prompts[i];
    const paddedNum = String(i + 1).padStart(3, '0');
    const outputPath = path.join(outputDir, `${paddedNum}.png`);

    console.log(`\n[${i + 1}/${prompts.length}] ${prompt.substring(0, 60)}...`);

    try {
      // Send the prompt
      await sendNewMessage(page, prompt);
      
      // Wait for generation to complete (bulletproof detection)
      await waitForSendButtonEnabled(page);
      await waitForImageFullyReady(page);
      
      // Download the image
      const ok = await downloadImage(page, outputPath);
      
      if (ok && fs.existsSync(outputPath) && fs.statSync(outputPath).size > 5000) {
        console.log(`✅ Success: ${outputPath}`);
        logResults(resultsPath, { index: i, prompt, status: 'success', output: outputPath });
        successCount++;
      } else {
        console.log(`❌ Failed: no valid image`);
        logResults(resultsPath, { index: i, prompt, status: 'failed', error: 'no image' });
        failCount++;
      }

    } catch (e) {
      console.log(`❌ Error: ${e.message}`);
      logResults(resultsPath, { index: i, prompt, status: 'error', error: e.message });
      failCount++;
    }

    // Small delay between prompts
    await new Promise(r => setTimeout(r, 2000));
  }

  await context.close();

  console.log(`\n=== Complete ===`);
  console.log(`Success: ${successCount}, Failed: ${failCount}`);
  console.log(`Results: ${resultsPath}`);
}

const opts = parseArgs();
generateImages(opts).catch(console.error);
