#!/usr/bin/env node

const { chromium } = require('playwright-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');

chromium.use(StealthPlugin());

const args = process.argv.slice(2);
const command = args[0];

if (!command) {
  console.error('Usage: stealth-browser <open|screenshot|pdf|parallel> <url> [url2] [url3] ...');
  process.exit(1);
}

// Handle parallel command with multiple URLs
const urls = command === 'parallel' ? args.slice(1) : [args[1]];

if (urls.length === 0 || !urls[0]) {
  console.error('Error: No URL(s) provided');
  process.exit(1);
}

(async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath: '/usr/bin/chromium',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-accelerated-2d-canvas',
      '--disable-gpu',
      '--window-size=1920,1080',
      '--disable-blink-features=AutomationControlled',
    ]
  });

  try {
    if (command === 'parallel') {
      // Fetch multiple URLs in parallel using browser contexts
      console.log(`Fetching ${urls.length} URLs in parallel...`);
      
      const results = await Promise.all(
        urls.map(async (url, index) => {
          const context = await browser.newContext({
            viewport: { width: 1920, height: 1080 },
            userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
          });
          
          try {
            const page = await context.newPage();
            
            await page.goto(url, {
              waitUntil: 'networkidle',
              timeout: 60000
            });
            
            await page.waitForTimeout(5000);
            
            const content = await page.content();
            const title = await page.title();
            
            await context.close();
            
            return {
              index: index + 1,
              url: url,
              title: title,
              content: content.substring(0, 5000) + (content.length > 5000 ? '\n... [truncated]' : ''),
              status: 'success'
            };
          } catch (error) {
            await context.close();
            return {
              index: index + 1,
              url: url,
              error: error.message,
              status: 'failed'
            };
          }
        })
      );
      
      console.log(JSON.stringify(results, null, 2));
      
    } else {
      // Single URL commands (open, screenshot, pdf)
      const url = urls[0];
      
      const context = await browser.newContext({
        viewport: { width: 1920, height: 1080 },
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
      });
      
      const page = await context.newPage();
      
      await page.goto(url, {
        waitUntil: 'networkidle',
        timeout: 60000
      });
      
      await page.waitForTimeout(5000);
      
      switch (command) {
        case 'open':
          const content = await page.content();
          console.log(content);
          break;
          
        case 'screenshot':
          const screenshotPath = `/tmp/stealth-screenshot-${Date.now()}.png`;
          await page.screenshot({ 
            path: screenshotPath,
            fullPage: true 
          });
          console.log(`Screenshot saved: ${screenshotPath}`);
          break;
          
        case 'pdf':
          const pdfPath = `/tmp/stealth-page-${Date.now()}.pdf`;
          await page.pdf({ 
            path: pdfPath,
            format: 'A4',
            printBackground: true
          });
          console.log(`PDF saved: ${pdfPath}`);
          break;
          
        default:
          console.error(`Unknown command: ${command}`);
          process.exit(1);
      }
      
      await context.close();
    }
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
})();
