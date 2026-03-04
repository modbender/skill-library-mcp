#!/usr/bin/env node
/**
 * Stealth Browser - Anti-detection browsing with proxy support
 * 
 * Usage:
 *   node browser.js <url>                    # Open URL with stealth
 *   node browser.js <url> --proxy            # With Smartproxy residential
 *   node browser.js <url> --screenshot out.png
 *   node browser.js <url> --html             # Output page HTML
 */

import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';
import fs from 'fs';
import path from 'path';

puppeteer.use(StealthPlugin());

// Load Smartproxy credentials
function getProxyConfig() {
  const proxyPath = path.join(process.env.HOME, '.config/smartproxy/proxy.json');
  if (fs.existsSync(proxyPath)) {
    return JSON.parse(fs.readFileSync(proxyPath, 'utf8'));
  }
  return null;
}

async function createBrowser(useProxy = false) {
  const args = [
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-dev-shm-usage',
    '--disable-accelerated-2d-canvas',
    '--disable-gpu',
    '--window-size=1920,1080',
    '--disable-blink-features=AutomationControlled'
  ];
  
  if (useProxy) {
    const proxy = getProxyConfig();
    if (proxy) {
      args.push(`--proxy-server=http://${proxy.host}:${proxy.port}`);
    }
  }
  
  const browser = await puppeteer.launch({
    headless: 'new',
    args,
    ignoreHTTPSErrors: true
  });
  
  return browser;
}

async function browse(url, options = {}) {
  const browser = await createBrowser(options.proxy);
  const page = await browser.newPage();
  
  // Set realistic viewport and user agent
  await page.setViewport({ width: 1920, height: 1080 });
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36');
  
  // Authenticate proxy if needed
  if (options.proxy) {
    const proxy = getProxyConfig();
    if (proxy && proxy.username) {
      await page.authenticate({
        username: proxy.username,
        password: proxy.password
      });
    }
  }
  
  // Add some human-like behaviors
  await page.evaluateOnNewDocument(() => {
    // Override webdriver detection
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    
    // Add realistic plugins
    Object.defineProperty(navigator, 'plugins', {
      get: () => [1, 2, 3, 4, 5]
    });
    
    // Add languages
    Object.defineProperty(navigator, 'languages', {
      get: () => ['en-US', 'en']
    });
  });
  
  try {
    await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
    
    const result = {
      url: page.url(),
      title: await page.title(),
      status: 'success'
    };
    
    if (options.screenshot) {
      await page.screenshot({ path: options.screenshot, fullPage: true });
      result.screenshot = options.screenshot;
    }
    
    if (options.html) {
      result.html = await page.content();
    }
    
    if (options.text) {
      result.text = await page.evaluate(() => document.body.innerText);
    }
    
    return result;
    
  } catch (error) {
    return { status: 'error', error: error.message };
  } finally {
    await browser.close();
  }
}

// CLI interface
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('Usage: node browser.js <url> [--proxy] [--screenshot file.png] [--html] [--text]');
    process.exit(1);
  }
  
  const url = args[0];
  const options = {
    proxy: args.includes('--proxy'),
    html: args.includes('--html'),
    text: args.includes('--text')
  };
  
  const screenshotIdx = args.indexOf('--screenshot');
  if (screenshotIdx !== -1 && args[screenshotIdx + 1]) {
    options.screenshot = args[screenshotIdx + 1];
  }
  
  console.error(`🌐 Browsing: ${url}`);
  if (options.proxy) console.error('🔒 Using Smartproxy');
  
  const result = await browse(url, options);
  
  if (result.html) {
    console.log(result.html);
  } else if (result.text) {
    console.log(result.text);
  } else {
    console.log(JSON.stringify(result, null, 2));
  }
}

export { browse, createBrowser };

main().catch(console.error);
