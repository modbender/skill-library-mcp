#!/usr/bin/env node
/**
 * Analyze Page Performance
 * Usage: node analyze_performance.js <url> [--verbose]
 */

const puppeteer = require('puppeteer');

async function analyzePerformance(url, verbose = false) {
  let browser;
  
  try {
    browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await puppeteer.newPage();
    const resources = [];
    
    // Track resource loading
    page.on('response', async (response) => {
      const request = response.request();
      const timing = response.timing();
      const headers = response.headers();
      
      if (timing) {
        resources.push({
          url: request.url(),
          type: request.resourceType(),
          size: headers['content-length'] ? parseInt(headers['content-length']) : 0,
          time: Math.round(timing.responseEnd),
          status: response.status()
        });
      }
    });
    
    // Navigate and measure
    if (verbose) console.error(`Analyzing performance for ${url}...`);
    
    const startTime = Date.now();
    await page.goto(url, { 
      waitUntil: 'networkidle2',
      timeout: 30000 
    });
    const endTime = Date.now();
    
    // Get performance metrics
    const performanceMetrics = await page.evaluate(() => {
      const perf = window.performance;
      const timing = perf.timing;
      const navigation = perf.getEntriesByType('navigation')[0];
      
      return {
        // Navigation Timing
        ttfb: timing.responseStart - timing.requestStart,
        domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
        loadComplete: timing.loadEventEnd - timing.navigationStart,
        
        // Resource Timing
        domInteractive: timing.domInteractive - timing.navigationStart,
        domComplete: timing.domComplete - timing.navigationStart,
        
        // Paint Timing
        firstPaint: performance.getEntriesByType('paint').find(e => e.name === 'first-paint')?.startTime || 0,
        firstContentfulPaint: performance.getEntriesByType('paint').find(e => e.name === 'first-contentful-paint')?.startTime || 0,
        
        // Navigation
        redirectTime: timing.redirectEnd - timing.redirectStart,
        dnsTime: timing.domainLookupEnd - timing.domainLookupStart,
        tcpTime: timing.connectEnd - timing.connectStart,
        requestTime: timing.responseEnd - timing.requestStart
      };
    });
    
    // Analyze resources
    const slowResources = resources.filter(r => r.time > 1000).sort((a, b) => b.time - a.time);
    const largeResources = resources.filter(r => r.size > 1000000).sort((a, b) => b.size - a.size);
    const failedResources = resources.filter(r => r.status >= 400);
    
    // Summary
    const totalPageLoadTime = endTime - startTime;
    const summary = {
      pageLoadTime: totalPageLoadTime,
      ttfb: performanceMetrics.ttfb,
      domContentLoaded: performanceMetrics.domContentLoaded,
      loadComplete: performanceMetrics.loadComplete,
      firstPaint: performanceMetrics.firstPaint,
      firstContentfulPaint: performanceMetrics.firstContentfulPaint,
      
      resourceCount: resources.length,
      totalSize: resources.reduce((sum, r) => sum + r.size, 0),
      slowResourcesCount: slowResources.length,
      largeResourcesCount: largeResources.length,
      failedResourcesCount: failedResources.length,
      
      // Performance Assessment
      isSlow: totalPageLoadTime > 3000,
      hasSlowBackend: performanceMetrics.ttfb > 1000,
      hasSlowResources: slowResources.length > 0,
      hasFailedResources: failedResources.length > 0
    };
    
    // Output
    const output = {
      url,
      timestamp: new Date().toISOString(),
      metrics: performanceMetrics,
      slowResources: slowResources.slice(0, 10),
      largeResources: largeResources.slice(0, 10),
      failedResources,
      summary
    };
    
    console.log(JSON.stringify(output, null, 2));
    
    if (verbose) {
      console.error(`\n===== Performance Summary =====`);
      console.error(`Page Load Time: ${totalPageLoadTime}ms`);
      console.error(`Time to First Byte: ${performanceMetrics.ttfb}ms`);
      console.error(`DOM Content Loaded: ${performanceMetrics.domContentLoaded}ms`);
      console.error(`Slow Resources: ${slowResources.length}`);
      console.error(`Failed Resources: ${failedResources.length}`);
    }
    
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
const verbose = args.includes('--verbose');

if (!url) {
  console.error('Usage: node analyze_performance.js <url> [--verbose]');
  process.exit(1);
}

analyzePerformance(url, verbose);
