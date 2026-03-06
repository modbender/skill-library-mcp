#!/usr/bin/env node
/**
 * Screenshot tool via Chrome DevTools Protocol
 * Usage: node screenshot.js <url> <output-path> [options]
 * 
 * Options:
 *   --width=<n>    Viewport width (default: 1920)
 *   --height=<n>   Viewport height (default: 1080)
 *   --wait=<ms>    Wait time after load in ms (default: 3000)
 *   --fullpage     Capture full page (default: true)
 *   --cdp=<url>    CDP endpoint (default: http://127.0.0.1:9222)
 */

const puppeteer = require('/tmp/node_modules/puppeteer');
const fs = require('fs');
const path = require('path');

function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    url: null,
    output: null,
    width: 1920,
    height: 1080,
    wait: 3000,
    fullPage: true,
    cdp: 'http://127.0.0.1:9222'
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg.startsWith('--')) {
      if (arg === '--fullpage') {
        options.fullPage = true;
      } else if (arg.includes('=')) {
        const [key, value] = arg.slice(2).split('=');
        if (key === 'width') options.width = parseInt(value);
        if (key === 'height') options.height = parseInt(value);
        if (key === 'wait') options.wait = parseInt(value);
        if (key === 'cdp') options.cdp = value;
      }
    } else if (!options.url) {
      options.url = arg;
    } else if (!options.output) {
      options.output = arg;
    }
  }

  return options;
}

async function takeScreenshot(options) {
  let browser;
  try {
    // Connect to existing Chrome
    browser = await puppeteer.connect({
      browserURL: options.cdp,
      defaultViewport: {
        width: options.width,
        height: options.height
      }
    });

    console.log(`Connected to Chrome at ${options.cdp}`);

    // Create new page
    const page = await browser.newPage();
    console.log(`Navigating to ${options.url}...`);

    // Navigate and wait for load
    await page.goto(options.url, {
      waitUntil: 'networkidle2',
      timeout: 60000
    });

    // Additional wait for dynamic content
    if (options.wait > 0) {
      console.log(`Waiting ${options.wait}ms for dynamic content...`);
      await new Promise(r => setTimeout(r, options.wait));
    }

    // Ensure output directory exists
    const outputDir = path.dirname(options.output);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    // Take screenshot
    console.log(`Taking screenshot...`);
    await page.screenshot({
      path: options.output,
      fullPage: options.fullPage
    });

    console.log(`Screenshot saved to: ${options.output}`);
    console.log(`Dimensions: ${options.width}x${options.height}`);
    console.log(`Full page: ${options.fullPage}`);

  } catch (err) {
    console.error('Error:', err.message);
    if (err.message.includes('connect')) {
      console.error('\nMake sure Chrome is running with CDP enabled:');
      console.error('  chrome --remote-debugging-port=9222 --remote-debugging-address=0.0.0.0');
      console.error('\nOr check if the CDP port is correct with:');
      console.error('  curl http://127.0.0.1:9222/json/version');
    }
    process.exit(1);
  } finally {
    if (browser) {
      await browser.disconnect();
    }
  }
}

// Main
const options = parseArgs();

if (!options.url || !options.output) {
  console.log('Usage: node screenshot.js <url> <output-path> [options]');
  console.log('');
  console.log('Options:');
  console.log('  --width=<n>    Viewport width (default: 1920)');
  console.log('  --height=<n>   Viewport height (default: 1080)');
  console.log('  --wait=<ms>    Wait time after load in ms (default: 3000)');
  console.log('  --cdp=<url>    CDP endpoint (default: http://127.0.0.1:9222)');
  console.log('');
  console.log('Examples:');
  console.log('  node screenshot.js https://baidu.com /tmp/baidu.png');
  console.log('  node screenshot.js https://xiaohongshu.com /tmp/xhs.png --wait=5000');
  process.exit(1);
}

takeScreenshot(options);
