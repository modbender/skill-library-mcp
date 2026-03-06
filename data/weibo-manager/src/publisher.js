const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const COOKIE_FILE = path.join(__dirname, '../cookies.json');

async function publishWeibo(content, images = []) {
    if (!fs.existsSync(COOKIE_FILE)) {
        throw new Error('No cookies found. Please run login first.');
    }
    const cookies = JSON.parse(fs.readFileSync(COOKIE_FILE));
    
    console.log(`[Weibo] Publishing: "${content}" with ${images.length} images...`);
    
    const browser = await puppeteer.launch({
        headless: "new",
        executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
    });

    const page = await browser.newPage();
    await page.setCookie(...cookies);
    
    try {
        await page.goto('https://weibo.com', { waitUntil: 'networkidle2' });
        
        // Check if we are redirected to login page
        if (page.url().includes('login.php') || page.url().includes('passport.weibo.com')) {
            throw new Error('Cookies invalid, redirected to login page.');
        }

        // Wait for the main input area
        // Try multiple selectors
        const inputSelectors = [
            'textarea.Form_input_3o77k', 
            'div[contenteditable="true"][title="微博输入框"]',
            'textarea[placeholder*="有什么新鲜事"]',
            'textarea[title="微博输入框"]',
            'div[contenteditable="true"]' // Very generic, might match comment box too, but main feed usually first
        ];
        
        let inputFound = false;
        for (const selector of inputSelectors) {
            try {
                // Short timeout for each check
                await page.waitForSelector(selector, { timeout: 3000 });
                await page.click(selector);
                inputFound = true;
                console.log(`[Weibo] Found input with selector: ${selector}`);
                break;
            } catch (e) {
                // Continue to next selector
            }
        }
        
        if (!inputFound) {
            throw new Error('Input box not found with any known selector.');
        }

        // Clear existing content if any (usually empty)
        // Type the content with explicit Enter key simulation for newlines
        // This avoids issues with shell escaping or editor parsing
        const lines = content.split('\\n').join('\n').split('\n'); // Handle both literal \n string and actual newlines
        
        for (let i = 0; i < lines.length; i++) {
            if (lines[i]) {
                await page.keyboard.type(lines[i]);
            }
            // Press Enter between lines
            if (i < lines.length - 1) {
                await page.keyboard.press('Enter');
                await new Promise(r => setTimeout(r, 100)); // Small pause
            }
        }
            
        // Handle images
        if (images.length > 0) {
                // Find file input
                // Usually input[type="file"] hidden near the image icon
                const fileInputSelector = 'input[type="file"]';
                const fileInput = await page.$(fileInputSelector);
                if (fileInput) {
                    await fileInput.uploadFile(...images);
                    // Wait for upload to complete
                    await new Promise(r => setTimeout(r, 3000 * images.length));
                } else {
                    console.warn('[Weibo] Image upload input not found.');
                }
            }
            
            // Click publish button
            // Look for button with text "发送" or "发布"
            // Using a more robust selector strategy
            const buttonSelectors = [
                'a[title="发布"]', 
                'button.Tool_btn_1EClz',
                'a.Tool_btn_1EClz',
                'div[title="发布"]',
                '.Tool_btn_1EClz' // Class name might change, but let's try
            ];
            
            let button = null;
            // Try explicit selectors first
            for (const sel of buttonSelectors) {
                try {
                    button = await page.$(sel);
                    if (button) break;
                } catch (e) {}
            }
            
            // Fallback: evaluate in browser context to find the button
            if (!button) {
                const handle = await page.evaluateHandle(() => {
                    const candidates = Array.from(document.querySelectorAll('button, a, div[role="button"], div.W_btn_a, a.W_btn_a'));
                    return candidates.find(el => {
                        const text = el.textContent ? el.textContent.trim() : '';
                        const title = el.getAttribute('title');
                        // Visibility check (simple)
                        return (text === '发送' || text === '发布' || title === '发布');
                    });
                });
                if (handle) { 
                   const json = await handle.jsonValue();
                   if (json) button = handle;
                }
            }
            
            if (button) {
                await button.click();
                console.log('[Weibo] Clicked publish button.');
                
                // Wait for success confirmation or feed update
                await new Promise(r => setTimeout(r, 5000));
            } else {
                throw new Error('Publish button not found.');
            }

    } catch (error) {
        console.error('[Weibo] Publish Error:', error);
        await page.screenshot({ path: path.join(__dirname, '../debug_publish_fail.png') });
        throw error;
    } finally {
        await browser.close();
    }
}

// CLI usage
if (require.main === module) {
    const content = process.argv[2];
    const images = process.argv.slice(3);
    publishWeibo(content, images).catch(err => {
        console.error(err);
        process.exit(1);
    });
}

module.exports = { publishWeibo };
