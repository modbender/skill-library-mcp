#!/usr/bin/env node
/**
 * 🐉 VHAGAR Amazon Purchase - With Saved Session
 * 
 * Run amazon-login.js first to save your session.
 * Then run this to complete a purchase.
 */

const { chromium } = require('playwright');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const USER_DATA_DIR = path.join(__dirname, '.chrome-session');
const SCREENSHOT_DIR = '/tmp/vhagar-purchase';
const SEARCH_TERM = 'USB-C cable';
const MAX_PRICE = 10.00;

if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

function log(msg) {
  const ts = new Date().toISOString().slice(11, 19);
  console.log(`[${ts}] ${msg}`);
}

async function screenshot(page, name) {
  const p = `${SCREENSHOT_DIR}/${name}.png`;
  await page.screenshot({ path: p });
  log(`📸 ${p}`);
  return p;
}

async function main() {
  log('🐉 VHAGAR Amazon Purchase (with session)');
  log('=========================================');
  
  if (!fs.existsSync(USER_DATA_DIR)) {
    console.error('❌ No session found! Run amazon-login.js first.');
    process.exit(1);
  }
  
  log('Loading saved session...');
  const browser = await chromium.launchPersistentContext(USER_DATA_DIR, {
    headless: false,
    slowMo: 300,
    viewport: { width: 1280, height: 800 }
  });
  
  const page = browser.pages()[0] || await browser.newPage();
  
  try {
    // Navigate to Amazon
    log('Navigating to Amazon...');
    await page.goto('https://www.amazon.com', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
    await screenshot(page, '01-home');
    
    // Check login status
    const greeting = await page.$eval('#nav-link-accountList-nav-line-1', el => el.textContent).catch(() => '');
    log(`Login status: ${greeting}`);
    
    if (greeting.includes('Sign in') || !greeting || greeting.includes('Hello, sign')) {
      log('⚠️ Not logged in. Please run amazon-login.js first.');
      await browser.close();
      return;
    }
    
    // Search
    log(`Searching: ${SEARCH_TERM}`);
    await page.fill('#twotabsearchtextbox', SEARCH_TERM);
    await page.click('#nav-search-submit-button');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);
    await screenshot(page, '02-search');
    
    // Find item under budget
    log(`Finding items under $${MAX_PRICE}...`);
    const results = await page.$$('[data-component-type="s-search-result"]');
    log(`Found ${results.length} results`);
    
    let selected = null;
    let price = null;
    let title = '';
    
    for (const r of results.slice(0, 15)) {
      try {
        const whole = await r.$eval('.a-price-whole', e => e.textContent.replace(',', ''));
        const frac = await r.$eval('.a-price-fraction', e => e.textContent).catch(() => '00');
        const p = parseFloat(`${whole}${frac}`);
        if (p > 0 && p < MAX_PRICE) {
          title = await r.$eval('h2 span', e => e.textContent).catch(() => 'Unknown');
          log(`✓ ${title.slice(0, 50)}... $${p}`);
          selected = r;
          price = p;
          break;
        }
      } catch (e) {}
    }
    
    if (!selected) {
      throw new Error(`No items under $${MAX_PRICE}`);
    }
    
    // Add to cart
    log('Adding to cart...');
    const atc = await selected.$('button[name="submit.addToCart"]');
    if (atc) {
      await atc.click();
    } else {
      const link = await selected.$('h2 a');
      if (link) await link.click();
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(2000);
      await screenshot(page, '03-product');
      
      const addBtn = await page.$('#add-to-cart-button');
      if (addBtn) await addBtn.click();
      else throw new Error('No add to cart button');
    }
    
    await page.waitForTimeout(2000);
    await screenshot(page, '04-added');
    
    // Go to cart
    log('Going to cart...');
    await page.goto('https://www.amazon.com/gp/cart/view.html');
    await page.waitForTimeout(2000);
    await screenshot(page, '05-cart');
    
    // Checkout
    log('Proceeding to checkout...');
    await page.click('input[name="proceedToRetailCheckout"]').catch(() => {});
    await page.waitForTimeout(3000);
    await screenshot(page, '06-checkout');
    
    log('');
    log('═══════════════════════════════════════');
    log('⚠️  READY TO PLACE ORDER');
    log('═══════════════════════════════════════');
    log(`Item: ${title.slice(0, 40)}...`);
    log(`Price: $${price}`);
    log('');
    log('The browser is showing checkout.');
    log('Type "yes" to place the order, anything else to cancel:');
    
    const answer = await new Promise(resolve => {
      process.stdin.once('data', data => resolve(data.toString().trim()));
    });
    
    if (answer.toLowerCase() === 'yes') {
      log('🔥 PLACING ORDER...');
      
      // Click place order
      const placeOrderBtn = await page.$('[name="placeYourOrder1"], input[name="placeYourOrder1"], #submitOrderButtonId input');
      if (placeOrderBtn) {
        await placeOrderBtn.click();
        await page.waitForTimeout(5000);
        await screenshot(page, '07-confirmation');
        
        // Get order number
        const orderText = await page.textContent('body').catch(() => '');
        const orderMatch = orderText.match(/order\s*#?\s*(\d{3}-\d{7}-\d{7})/i);
        const orderId = orderMatch ? orderMatch[1] : 'PENDING';
        
        log('');
        log('═══════════════════════════════════════');
        log('🎉 ORDER PLACED!');
        log('═══════════════════════════════════════');
        log(`Order ID: ${orderId}`);
        log(`Amount: $${price}`);
        log('');
        
        // Generate proof hash
        const proofData = JSON.stringify({
          orderId,
          amount: price,
          item: title,
          timestamp: Date.now(),
          retailer: 'amazon'
        });
        const proofHash = '0x' + crypto.createHash('sha256').update(proofData).digest('hex');
        
        log(`Proof Hash: ${proofHash}`);
        log('');
        log('This proof hash can be submitted to ClawPay for verification.');
        
        // Save proof
        const proofFile = `${SCREENSHOT_DIR}/proof.json`;
        fs.writeFileSync(proofFile, JSON.stringify({
          orderId,
          amount: price,
          item: title,
          timestamp: Date.now(),
          proofHash,
          screenshots: [
            '01-home.png', '02-search.png', '03-product.png',
            '04-added.png', '05-cart.png', '06-checkout.png', '07-confirmation.png'
          ]
        }, null, 2));
        log(`Proof saved: ${proofFile}`);
        
      } else {
        log('❌ Could not find Place Order button');
      }
    } else {
      log('Order cancelled.');
    }
    
    log('');
    log('Keeping browser open for 30 seconds...');
    await page.waitForTimeout(30000);
    
  } catch (err) {
    log(`❌ Error: ${err.message}`);
    await screenshot(page, 'error');
  } finally {
    await browser.close();
  }
}

main().catch(console.error);
