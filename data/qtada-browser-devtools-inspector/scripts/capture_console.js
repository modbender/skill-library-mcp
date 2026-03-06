#!/usr/bin/env node
/**
 * Capture Console Logs from Browser DevTools
 * Usage: node capture_console.js <url> [--filter=error] [--verbose]
 */

const puppeteer = require('puppeteer');

async function captureConsole(url, filter = 'all', verbose = false) {
  let browser;
  
  try {
    // Launch browser
    browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await puppeteer.newPage();
    const logs = [];
    
    // Listen to console events
    page.on('console', msg => {
      const entry = {
        level: msg.type(),
        message: msg.text(),
        source: msg.location().url || 'unknown',
        lineNumber: msg.location().lineNumber || 0
      };
      
      // Apply filter
      if (filter === 'all' || entry.level === filter) {
        logs.push(entry);
        if (verbose) {
          console.error(`[${entry.level.toUpperCase()}] ${entry.message}`);
        }
      }
    });
    
    // Listen to page errors
    page.on('pageerror', error => {
      const entry = {
        level: 'error',
        message: error.message,
        source: error.stack ? error.stack.split('\n')[1] : 'unknown',
        lineNumber: 0
      };
      
      if (filter === 'all' || filter === 'error') {
        logs.push(entry);
        if (verbose) {
          console.error(`[ERROR] ${entry.message}`);
        }
      }
    });
    
    // Navigate to URL
    if (verbose) console.error(`Loading ${url}...`);
    await page.goto(url, { 
      waitUntil: 'networkidle2',
      timeout: 30000 
    });
    
    // Wait a bit for async logs
    await page.waitForTimeout(2000);
    
    // Generate summary
    const summary = {
      total: logs.length,
      errors: logs.filter(l => l.level === 'error').length,
      warnings: logs.filter(l => l.level === 'warn').length,
      logs: logs.filter(l => l.level === 'log').length,
      info: logs.filter(l => l.level === 'info').length
    };
    
    // Output JSON
    const output = {
      url,
      timestamp: new Date().toISOString(),
      filter,
      logs,
      summary
    };
    
    console.log(JSON.stringify(output, null, 2));
    
    await browser.close();
    process.exit(0);
    
  } catch (error) {
    console.error(JSON.stringify({
      error: true,
      message: error.message,
      stack: error.stack
    }, null, 2));
    
    if (browser) await browser.close();
    process.exit(1);
  }
}

// Parse arguments
const args = process.argv.slice(2);
const url = args[0];
const filter = args.find(a => a.startsWith('--filter='))?.split('=')[1] || 'all';
const verbose = args.includes('--verbose');

if (!url) {
  console.error('Usage: node capture_console.js <url> [--filter=error] [--verbose]');
  console.error('Filters: all, log, warn, error, info');
  process.exit(1);
}

captureConsole(url, filter, verbose);
