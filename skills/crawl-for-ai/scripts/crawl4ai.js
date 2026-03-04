#!/usr/bin/env node
/**
 * Crawl4AI Fetcher - Local crawl4ai instance for web scraping
 * 
 * Usage: node crawl4ai.js "url" [--json]
 * 
 * Output: Markdown content from the page
 */

const http = require('http');

const CRAWL4AI_URL = process.env.CRAWL4AI_URL;
const CRAWL4AI_KEY = process.env.CRAWL4AI_KEY;

if (!CRAWL4AI_URL) {
  console.error('CRAWL4AI_URL environment variable is required');
  process.exit(1);
}

// Parse URL to get hostname and port
let hostname, port, basePath;
try {
  const parsed = new URL(CRAWL4AI_URL);
  hostname = parsed.hostname;
  port = parsed.port || 11235;
  basePath = parsed.pathname.replace(/\/$/, ''); // Remove trailing slash
} catch (e) {
  console.error('Invalid CRAWL4AI_URL:', CRAWL4AI_URL);
  process.exit(1);
}

async function crawl(urls) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({ urls: Array.isArray(urls) ? urls : [urls] });
    
    const headers = {
      'Content-Type': 'application/json',
      'Content-Length': Buffer.byteLength(body)
    };
    if (CRAWL4AI_KEY) {
      headers['Authorization'] = `Bearer ${CRAWL4AI_KEY}`;
    }
    
    const req = http.request({
      hostname,
      port,
      path: basePath + '/crawl',
      method: 'POST',
      headers
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(e);
        }
      });
    });
    
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    console.log('Crawl4AI Fetcher - Local web scraper');
    console.log('');
    console.log('Usage: node crawl4ai.js "url" [--json]');
    console.log('');
    console.log('Options:');
    console.log('  --json    Output full JSON response');
    console.log('');
    console.log('Environment:');
    console.log('  CRAWL4AI_URL  Crawl4AI instance URL (default: http://localhost:11235)');
    console.log('  CRAWL4AI_KEY  API key (default: 1234)');
    process.exit(0);
  }
  
  const url = args.find(a => !a.startsWith('--'));
  const jsonOutput = args.includes('--json');
  
  try {
    const result = await crawl(url);
    
    if (!result.success) {
      console.error('Crawl failed:', result);
      process.exit(1);
    }
    
    const page = result.results[0];
    
    if (jsonOutput) {
      console.log(JSON.stringify(result, null, 2));
    } else {
      // Output clean markdown
      const md = page.markdown?.raw_markdown || page.markdown || '';
      console.log(md);
    }
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

main();