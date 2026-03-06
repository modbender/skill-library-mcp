/**
 * Morelogin + Puppeteer example script
 *
 * This script demonstrates how to connect Puppeteer to Morelogin browser and run automation
 *
 * Usage:
 * 1. Install dependencies: npm install puppeteer-core
 * 2. Start Morelogin profile: morelogin start --profile-id <your_profile_id>
 * 3. Run this script: node puppeteer-example.js
 */

const puppeteer = require('puppeteer-core');

// Config - get from morelogin connect command
const CDP_ADDRESS = 'http://localhost:9222';

async function main() {
  console.log('🚀 Connecting to Morelogin browser...\n');
  
  let browser;
  
  try {
    // Connect to running Morelogin browser instance
    browser = await puppeteer.connect({
      browserURL: CDP_ADDRESS,
      defaultViewport: null // Use browser default viewport
    });
    
    console.log('✅ Connected!');
    console.log(`Browser version: ${browser.version()}`);
    
    // Get all pages
    const pages = await browser.pages();
    const page = pages.length > 0 ? pages[0] : await browser.newPage();
    
    // Enable request interception (optional)
    await page.setRequestInterception(true);
    page.on('request', request => {
      // Can modify requests here
      request.continue();
    });
    
    // Example 1: Navigate to webpage
    console.log('\n📍 Navigating to example.com...');
    await page.goto('https://example.com', { 
      waitUntil: 'networkidle2',
      timeout: 30000 
    });
    
    // Screenshot
    console.log('📸 Taking screenshot...');
    await page.screenshot({ 
      path: 'screenshot-example.png',
      fullPage: true 
    });
    console.log('✅ Screenshot saved: screenshot-example.png');
    
    // Get the page title
    const title = await page.title();
    console.log(`Page title: ${title}`);
    
    // Example 2: Execute JavaScript
    console.log('\n📜 Executing JavaScript...');
    const html = await page.evaluate(() => {
      return document.body.innerHTML;
    });
    console.log(`Page HTML length: ${html.length} characters`);
    
    // Example 3: Wait and click element
    console.log('\n🖱️  Waiting for element...');
    try {
      await page.waitForSelector('h1', { timeout: 5000 });
      const h1Element = await page.$('h1');
      const h1Text = h1Element
        ? await page.evaluate((el) => el.textContent, h1Element)
        : null;
      console.log(`H1 text: ${h1Text}`);
    } catch (e) {
      console.log('H1 element not found');
    }
    
    // Example 4: Navigate to new page and search
    console.log('\n🔍 Opening new tab...');
    const newPage = await browser.newPage();
    await newPage.goto('https://www.google.com', { waitUntil: 'networkidle2' });
    
    // Example 5: Get cookies
    console.log('\n🍪 Getting cookies...');
    const cookies = await page.cookies();
    console.log(`Cookie count: ${cookies.length}`);
    cookies.slice(0, 5).forEach(cookie => {
      console.log(`  - ${cookie.name}: ${cookie.value.substring(0, 20)}...`);
    });
    
    // Example 6: Modify User-Agent (Morelogin usually handles this)
    console.log('\n👤 Checking User-Agent...');
    const userAgent = await page.evaluate(() => navigator.userAgent);
    console.log(`User-Agent: ${userAgent.substring(0, 80)}...`);
    
    console.log('\n✅ All examples completed!');
    
    // Keep browser open, or close
    // await browser.close();
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    if (browser) {
      await browser.close();
    }
    process.exit(1);
  }
}

// Run
main();
