#!/usr/bin/env node
/**
 * Check for CORS Issues
 * Usage: node check_cors.js <url> [--verbose]
 */

const puppeteer = require('puppeteer');

async function checkCors(url, verbose = false) {
  let browser;
  
  try {
    browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await puppeteer.newPage();
    const corsIssues = [];
    const requests = [];
    
    // Listen to console for CORS errors
    page.on('console', msg => {
      const text = msg.text();
      if (text.includes('CORS') || text.includes('Access-Control')) {
        corsIssues.push({
          type: 'console',
          level: msg.type(),
          message: text,
          source: msg.location().url || 'unknown'
        });
        
        if (verbose) {
          console.error(`[CORS Console] ${text}`);
        }
      }
    });
    
    // Listen to network responses
    page.on('response', async (response) => {
      const request = response.request();
      const requestUrl = request.url();
      const headers = response.headers();
      const origin = new URL(url).origin;
      
      // Check for CORS headers
      const corsHeaders = {
        'access-control-allow-origin': headers['access-control-allow-origin'],
        'access-control-allow-methods': headers['access-control-allow-methods'],
        'access-control-allow-headers': headers['access-control-allow-headers'],
        'access-control-allow-credentials': headers['access-control-allow-credentials']
      };
      
      // Detect potential CORS issues
      const hasCorsHeaders = corsHeaders['access-control-allow-origin'];
      const isCrossOrigin = !requestUrl.startsWith(origin);
      const isAPI = requestUrl.includes('/api/') || request.resourceType() === 'xhr' || request.resourceType() === 'fetch';
      
      if (isAPI && isCrossOrigin) {
        const issue = {
          url: requestUrl,
          origin: origin,
          hasCorsHeaders,
          corsHeaders: hasCorsHeaders ? corsHeaders : null,
          status: response.status()
        };
        
        if (!hasCorsHeaders) {
          issue.problem = 'Missing CORS headers';
          corsIssues.push({
            type: 'network',
            severity: 'high',
            ...issue
          });
          
          if (verbose) {
            console.error(`[CORS Missing] ${requestUrl}`);
          }
        } else if (corsHeaders['access-control-allow-origin'] !== '*' && 
                   corsHeaders['access-control-allow-origin'] !== origin) {
          issue.problem = 'Incorrect Access-Control-Allow-Origin';
          corsIssues.push({
            type: 'network',
            severity: 'medium',
            ...issue
          });
          
          if (verbose) {
            console.error(`[CORS Mismatch] ${requestUrl}`);
          }
        }
        
        requests.push(issue);
      }
    });
    
    // Navigate to URL
    if (verbose) console.error(`Checking CORS on ${url}...`);
    await page.goto(url, { 
      waitUntil: 'networkidle2',
      timeout: 30000 
    });
    
    await page.waitForTimeout(2000);
    
    // Summary
    const summary = {
      totalCorsIssues: corsIssues.length,
      missingHeaders: corsIssues.filter(i => i.problem === 'Missing CORS headers').length,
      incorrectHeaders: corsIssues.filter(i => i.problem === 'Incorrect Access-Control-Allow-Origin').length,
      consoleErrors: corsIssues.filter(i => i.type === 'console').length,
      hasCorsIssues: corsIssues.length > 0
    };
    
    // Output
    const output = {
      url,
      timestamp: new Date().toISOString(),
      corsIssues,
      crossOriginRequests: requests,
      summary
    };
    
    console.log(JSON.stringify(output, null, 2));
    
    await browser.close();
    process.exit(corsIssues.length > 0 ? 1 : 0);
    
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
const verbose = args.includes('--verbose');

if (!url) {
  console.error('Usage: node check_cors.js <url> [--verbose]');
  process.exit(1);
}

checkCors(url, verbose);
