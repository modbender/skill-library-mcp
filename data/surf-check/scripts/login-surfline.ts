#!/usr/bin/env npx ts-node
/**
 * Surfline Login Script
 * 
 * One-time script to log into Surfline and save session cookies.
 * Run this when session expires to refresh authentication.
 * 
 * Usage:
 *   SURFLINE_EMAIL=xxx SURFLINE_PASSWORD=xxx npx ts-node scripts/login-surfline.ts
 * 
 * Or run interactively (will open browser for manual login):
 *   npx ts-node scripts/login-surfline.ts --interactive
 */

import { chromium } from 'playwright';
import * as fs from 'fs/promises';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SESSION_DIR = path.join(__dirname, '..', 'data', 'session');
const COOKIES_FILE = path.join(SESSION_DIR, 'cookies.json');

async function ensureSessionDir() {
  await fs.mkdir(SESSION_DIR, { recursive: true });
}

async function saveCookies(cookies: any[]) {
  await ensureSessionDir();
  await fs.writeFile(COOKIES_FILE, JSON.stringify(cookies, null, 2));
  console.log(`✅ Saved ${cookies.length} cookies to ${COOKIES_FILE}`);
}

async function loginInteractive() {
  console.log('🌐 Opening browser for interactive login...');
  console.log('   Log in manually, then close the browser when done.\n');

  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  await page.goto('https://www.surfline.com/sign-in');
  
  // Wait for user to log in (detect navigation to home or dashboard)
  console.log('⏳ Waiting for login...');
  
  try {
    await page.waitForURL('**/surf-reports-forecasts-cams/**', { timeout: 300000 });
    console.log('✅ Login detected!');
  } catch {
    // User might close browser or navigate elsewhere
    console.log('⚠️  Login check timed out, saving cookies anyway...');
  }

  const cookies = await context.cookies();
  await saveCookies(cookies);

  await browser.close();
}

async function loginAutomated() {
  const email = process.env.SURFLINE_EMAIL;
  const password = process.env.SURFLINE_PASSWORD;

  if (!email || !password) {
    console.error('❌ SURFLINE_EMAIL and SURFLINE_PASSWORD must be set');
    console.error('   Or use --interactive for manual login');
    process.exit(1);
  }

  console.log(`🌐 Logging into Surfline as ${email}...`);

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    await page.goto('https://www.surfline.com/sign-in');
    
    // Wait for form to load
    await page.waitForSelector('input[name="email"]', { timeout: 10000 });

    // Fill credentials
    await page.fill('input[name="email"]', email);
    await page.fill('input[name="password"]', password);

    // Submit
    await page.click('button[type="submit"]');

    // Wait for redirect after login
    await page.waitForURL('**/surf-reports-forecasts-cams/**', { timeout: 30000 });
    
    console.log('✅ Login successful!');

    const cookies = await context.cookies();
    await saveCookies(cookies);

  } catch (error) {
    console.error('❌ Login failed:', error);
    
    // Take screenshot for debugging
    const screenshotPath = path.join(SESSION_DIR, 'login-error.png');
    await page.screenshot({ path: screenshotPath });
    console.log(`   Screenshot saved to ${screenshotPath}`);
    
    process.exit(1);
  } finally {
    await browser.close();
  }
}

async function main() {
  const interactive = process.argv.includes('--interactive');

  if (interactive) {
    await loginInteractive();
  } else {
    await loginAutomated();
  }

  console.log('\n🏄 Session saved! You can now fetch premium forecast data.');
}

main().catch(console.error);
