#!/usr/bin/env node
/**
 * Capture Network Requests from Browser DevTools
 * Usage: node capture_network.js <url> [--filter=failed] [--type=xhr] [--pattern=/api/*]
 */

const puppeteer = require('puppeteer');

async function captureNetwork(url, filter = 'all', type = 'all', pattern = null, verbose = false) {
  let browser;
  
  try {
    browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await puppeteer.newPage();
    const requests = [];
    
    // Listen to request/response
    page.on('response', async (response) => {
      const request = response.request();
      const requestUrl = request.url();
      
      // Apply pattern filter
      if (pattern && !requestUrl.includes(pattern.replace('*', ''))) {
        return;
      }
      
      // Apply type filter
      const resourceType = request.resourceType();
      if (type !== 'all' && resourceType !== type) {
        return;
      }
      
      const timing = response.timing();
      const status = response.status();
      const headers = response.headers();
      
      const entry = {
        url: requestUrl,
        method: request.method(),
        status,
        statusText: response.statusText(),
        type: resourceType,
        size: headers['content-length'] ? parseInt(headers['content-length']) : 0,
        time: timing ? Math.round(timing.responseEnd) : 0,
        headers: headers,
        failed: status >= 400,
        slow: timing && timing.responseEnd > 1000
      };
      
      // Apply filter
      const shouldInclude = 
        filter === 'all' ||
        (filter === 'failed' && entry.failed) ||
        (filter === 'slow' && entry.slow);
      
      if (shouldInclude) {
        requests.push(entry);
        if (verbose) {
          const symbol = entry.failed ? '❌' : entry.slow ? '⏱️' : '✅';
          console.error(`${symbol} [${entry.status}] ${entry.method} ${entry.url} (${entry.time}ms)`);
        }
      }
    });
    
    // Navigate to URL
    if (verbose) console.error(`Loading ${url}...`);
    await page.goto(url, { 
      waitUntil: 'networkidle2',
      timeout: 30000 
    });
    
    // Wait for additional async requests
    await page.waitForTimeout(2000);
    
    // Generate summary
    const summary = {
      total: requests.length,
      failed: requests.filter(r => r.failed).length,
      slow: requests.filter(r => r.slow).length,
      totalSize: requests.reduce((sum, r) => sum + r.size, 0),
      totalTime: requests.reduce((sum, r) => sum + r.time, 0)
    };
    
    // Output JSON
    const output = {
      url,
      timestamp: new Date().toISOString(),
      filter,
      type,
      pattern,
      requests,
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
const type = args.find(a => a.startsWith('--type='))?.split('=')[1] || 'all';
const pattern = args.find(a => a.startsWith('--pattern='))?.split('=')[1] || null;
const verbose = args.includes('--verbose');

if (!url) {
  console.error('Usage: node capture_network.js <url> [--filter=failed] [--type=xhr] [--pattern=/api/*]');
  console.error('Filters: all, failed, slow');
  console.error('Types: all, xhr, fetch, script, stylesheet, image, font, media, document');
  process.exit(1);
}

captureNetwork(url, filter, type, pattern, verbose);
