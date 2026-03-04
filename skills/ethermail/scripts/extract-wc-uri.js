#!/usr/bin/env node
/**
 * Extract WalletConnect URI from EtherMail login page
 * 
 * EtherMail embeds WalletConnect in Shadow DOM, requiring special extraction.
 * This script uses Puppeteer to navigate and extract the URI.
 * 
 * Usage:
 *   node extract-wc-uri.js [--url <login-url>] [--timeout <ms>]
 * 
 * Output:
 *   Prints the WalletConnect URI (wc:...) to stdout
 */

const puppeteer = require('puppeteer');

const DEFAULT_URL = 'https://ethermail.io/accounts/login';
const DEFAULT_TIMEOUT = 30000;

async function extractWalletConnectURI(url, timeout) {
  // Note: Running without --no-sandbox for better security isolation
  // If you encounter permission issues on Linux, consider running with proper user permissions
  // rather than disabling sandbox
  const browser = await puppeteer.launch({
    headless: 'new',
    // Security: Sandbox enabled by default (removed --no-sandbox)
  });
  
  try {
    const page = await browser.newPage();
    
    // Navigate to login page
    console.error('📧 Navigating to EtherMail...');
    await page.goto(url, { waitUntil: 'networkidle2', timeout });
    
    // Wait for page to stabilize
    await page.waitForTimeout(2000);
    
    // Click the wallet login button
    console.error('🔑 Looking for wallet login button...');
    const walletButton = await page.$('[data-testid="wallet-login"], button:has-text("wallet"), [class*="wallet"]');
    if (walletButton) {
      await walletButton.click();
      await page.waitForTimeout(3000);
    }
    
    // Search Shadow DOM for WalletConnect URI
    console.error('🔍 Searching Shadow DOM for WalletConnect URI...');
    const wcUri = await page.evaluate(() => {
      function searchShadow(root, depth = 0) {
        if (depth > 10) return null;
        const elements = root.querySelectorAll('*');
        for (const el of elements) {
          if (el.shadowRoot) {
            const html = el.shadowRoot.innerHTML;
            const match = html.match(/wc:[a-f0-9]+@2\?[^"'<>\s]+/);
            if (match) return match[0];
            const found = searchShadow(el.shadowRoot, depth + 1);
            if (found) return found;
          }
        }
        return null;
      }
      return searchShadow(document);
    });
    
    if (wcUri) {
      console.error('✅ Found WalletConnect URI!');
      console.log(wcUri);
      return wcUri;
    } else {
      console.error('❌ Could not find WalletConnect URI in Shadow DOM');
      console.error('   Make sure the WalletConnect modal is open');
      process.exit(1);
    }
  } finally {
    await browser.close();
  }
}

// Parse arguments
const args = process.argv.slice(2);
let url = DEFAULT_URL;
let timeout = DEFAULT_TIMEOUT;

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--url' && args[i + 1]) {
    url = args[++i];
  } else if (args[i] === '--timeout' && args[i + 1]) {
    timeout = parseInt(args[++i], 10);
  } else if (args[i] === '--help' || args[i] === '-h') {
    console.log(`
Extract WalletConnect URI from EtherMail login page

Usage:
  node extract-wc-uri.js [options]

Options:
  --url <url>      Login page URL (default: ${DEFAULT_URL})
  --timeout <ms>   Navigation timeout in ms (default: ${DEFAULT_TIMEOUT})
  --help, -h       Show this help

Output:
  Prints WalletConnect URI (wc:...) to stdout
  Progress messages go to stderr
`);
    process.exit(0);
  }
}

extractWalletConnectURI(url, timeout).catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
