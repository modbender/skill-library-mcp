/**
 * Morelogin + Playwright example script
 *
 * This script demonstrates how to connect Playwright to Morelogin browser and run automation
 *
 * Usage:
 * 1. Install dependencies: npm install playwright
 * 2. Start Morelogin profile: morelogin start --profile-id <your_profile_id>
 * 3. Run this script: node playwright-example.js
 */

const { chromium } = require('playwright');

// Config - get from morelogin connect command
const CDP_ADDRESS = 'http://localhost:9222';

async function main() {
  console.log('🚀 Connecting to Morelogin browser...\n');
  
  let browser;
  
  try {
    // Connect to running Morelogin browser instance
    browser = await chromium.connectOverCDP(CDP_ADDRESS);
    
    console.log('✅ Connected!');
    
    // Get default context and page
    const context = browser.contexts()[0];
    const page = context.pages()[0] || await context.newPage();
    
    // Example 1: Navigate to webpage
    console.log('\n📍 Navigating to example.com...');
    const response = await page.goto('https://example.com', { 
      waitUntil: 'networkidle',
      timeout: 30000 
    });
    console.log(`Status code: ${response.status()}`);
    
    // Screenshot
    console.log('📸 Taking screenshot...');
    await page.screenshot({ 
      path: 'screenshot-playwright.png',
      fullPage: true 
    });
    console.log('✅ Screenshot saved: screenshot-playwright.png');
    
    // Get the page title
    const title = await page.title();
    console.log(`Page title: ${title}`);
    
    // Example 2: Execute JavaScript
    console.log('\n📜 Executing JavaScript...');
    const dimensions = await page.evaluate(() => {
      return {
        width: document.documentElement.clientWidth,
        height: document.documentElement.clientHeight,
        userAgent: navigator.userAgent
      };
    });
    console.log(`Viewport size: ${dimensions.width}x${dimensions.height}`);
    console.log(`User-Agent: ${dimensions.userAgent.substring(0, 60)}...`);
    
    // Example 3: Wait and get element
    console.log('\n🖱️  Waiting for element...');
    try {
      const h1 = await page.waitForSelector('h1', { timeout: 5000 });
      const h1Text = await h1.textContent();
      console.log(`H1 text: ${h1Text}`);
    } catch (e) {
      console.log('H1 element not found');
    }
    
    // Example 4: Open new tab
    console.log('\n🔍 Opening new tab...');
    const newPage = await context.newPage();
    await newPage.goto('https://www.github.com', { waitUntil: 'networkidle' });
    console.log(`New page title: ${await newPage.title()}`);
    
    // Example 5: Get cookies
    console.log('\n🍪 Getting cookies...');
    const cookies = await context.cookies();
    console.log(`Cookie count: ${cookies.length}`);
    cookies.slice(0, 5).forEach(cookie => {
      console.log(`  - ${cookie.name}: ${cookie.value?.substring(0, 20) || ''}...`);
    });
    
    // Example 6: Network request listener
    console.log('\n📡 Listening for network requests...');
    const requests = [];
    page.on('request', request => {
      requests.push({
        url: request.url(),
        method: request.method(),
        type: request.resourceType()
      });
    });
    
    await page.reload({ waitUntil: 'networkidle' });
    console.log(`Captured requests: ${requests.length}`);
    console.log('First 5 requests:');
    requests.slice(0, 5).forEach(req => {
      console.log(`  ${req.method} ${req.type} - ${req.url.substring(0, 50)}...`);
    });
    
    // Example 7: Device simulation (Morelogin usually handles fingerprint)
    console.log('\n📱 Checking device info...');
    const isMobile = await page.evaluate(() => {
      return /Mobile|Android|iPhone/i.test(navigator.userAgent);
    });
    console.log(`Mobile device: ${isMobile ? 'Yes' : 'No'}`);
    
    // Example 8: Geolocation (requires permission)
    console.log('\n🌍 Checking geolocation...');
    try {
      const geo = await page.evaluate(() => {
        return new Promise((resolve) => {
          if ('geolocation' in navigator) {
            navigator.geolocation.getCurrentPosition(
              pos => resolve({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
              () => resolve(null),
              { timeout: 3000 }
            );
          } else {
            resolve(null);
          }
        });
      });
      console.log(geo ? `Location: ${geo.lat}, ${geo.lng}` : 'Cannot get location');
    } catch (e) {
      console.log('Location access denied');
    }
    
    console.log('\n✅ All examples completed!');
    console.log('\n💡 Tip: Browser stays open, press Ctrl+C to exit');
    
    // Keep running
    await new Promise(() => {});
    
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
