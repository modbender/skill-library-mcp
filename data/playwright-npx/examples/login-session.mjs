import { chromium } from 'playwright';
import fs from 'fs';

/**
 * Login Session Example
 * Demonstrates persistent sessions - login once, reuse session.
 * 
 * Usage: node examples/login-session.mjs
 * 
 * This example uses GitHub login page structure but won't actually
 * log in (no credentials). Replace with your actual login flow.
 */

const SESSION_FILE = 'tmp/session.json';
const TARGET_URL = 'https://github.com';

const browser = await chromium.launch({ headless: false });
let context;
let page;

// Check for existing session
if (fs.existsSync(SESSION_FILE)) {
  console.log('Loading saved session...');
  context = await browser.newContext({
    storageState: SESSION_FILE
  });
  page = await context.newPage();
  
  // Navigate to target - should already be logged in
  await page.goto(TARGET_URL);
  console.log('Session restored!');
  
  // Check if we're logged in (look for avatar or username indicator)
  const isLoggedIn = await page.locator('[data-testid="header-menu-button"]').isVisible().catch(() => false);
  
  if (isLoggedIn) {
    console.log('Successfully logged in via saved session');
  } else {
    console.log('Session expired or invalid. Please log in manually.');
    // Delete invalid session
    fs.unlinkSync(SESSION_FILE);
  }
} else {
  console.log('No saved session found. Creating new session...');
  context = await browser.newContext();
  page = await context.newPage();
  
  await page.goto(`${TARGET_URL}/login`);
  
  console.log('\n=== MANUAL LOGIN REQUIRED ===');
  console.log('Please log in manually in the browser window.');
  console.log('After logging in, press Enter in this terminal to save the session.\n');
  
  // Wait for user input
  process.stdin.once('data', async () => {
    // Save session after login
    await context.storageState({ path: SESSION_FILE });
    console.log(`Session saved to ${SESSION_FILE}`);
    
    await browser.close();
    process.exit(0);
  });
  
  // Keep running until user presses Enter
  await new Promise(() => {});
}

// If we got here with a valid session, take a screenshot
if (page) {
  await page.screenshot({ path: 'tmp/session-test.png' });
  console.log('Screenshot saved to tmp/session-test.png');
}

await browser.close();
