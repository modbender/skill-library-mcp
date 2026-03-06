const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const COOKIE_FILE = path.join(__dirname, '../cookies.json');
const PROFILE_URL = 'https://weibo.com/u/5347147372';

(async () => {
    if (!fs.existsSync(COOKIE_FILE)) {
        console.error('No cookies found.');
        process.exit(1);
    }
    const cookies = JSON.parse(fs.readFileSync(COOKIE_FILE));
    
    console.log('[Weibo] Launching browser for DOM inspection...');
    const browser = await puppeteer.launch({
        headless: "new",
        executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
    });

    const page = await browser.newPage();
    await page.setCookie(...cookies);
    
    try {
        await page.goto(PROFILE_URL, { waitUntil: 'networkidle2', timeout: 60000 });
        console.log('[Weibo] Loaded profile page.');

        // Wait a bit for dynamic content
        await new Promise(r => setTimeout(r, 5000));

        // Inspect the feed container
        // Modern Weibo usually wraps feed in a div, often with class 'vue-recycle-scroller__item-view' or just 'wbpro-feed-content'
        // Let's grab the HTML of the main feed area to analyze locally
        
        // Try to identify the first "card"
        // Common classes in recent versions: .woo-panel-main, .feed_content, article
        
        const feedStructure = await page.evaluate(() => {
            // Helper to get simple structure
            const getStructure = (el, depth = 0) => {
                if (depth > 4) return '...';
                let str = `<${el.tagName.toLowerCase()} class="${el.className}"`;
                // check for specific attributes
                ['action-type', 'node-type', 'aria-label', 'title'].forEach(attr => {
                    if (el.hasAttribute(attr)) str += ` ${attr}="${el.getAttribute(attr)}"`;
                });
                str += '>';
                
                // Add text snippet if meaningful
                if (el.innerText && el.innerText.length < 50 && el.children.length === 0) {
                    str += el.innerText;
                }
                
                Array.from(el.children).forEach(child => {
                    str += '\n' + '  '.repeat(depth + 1) + getStructure(child, depth + 1);
                });
                // str += `\n${'  '.repeat(depth)}</${el.tagName.toLowerCase()}>`;
                return str;
            };

            // Try to find the first feed item
            // Strategy: Look for something that contains the text of the recent post "正在努力进化中"
            // This ensures we are looking at the right component type
            const allDivs = document.querySelectorAll('div');
            let targetDiv = null;
            for (const div of allDivs) {
                if (div.innerText && div.innerText.includes('正在努力进化中')) {
                    // Walk up to find the container card
                    let p = div;
                    while (p && p.tagName !== 'BODY') {
                        // A feed card usually has a specific class or is a direct child of a list
                        // Often has class containing 'card' or 'feed'
                        if (p.className && (p.className.includes('card') || p.className.includes('Feed_retweet'))) {
                             targetDiv = p;
                             break;
                        }
                        // Stop if we hit a very large container
                        if (p.offsetHeight > 1000) break; 
                        p = p.parentElement;
                    }
                    if (targetDiv) break;
                }
            }
            
            if (!targetDiv) {
                // Fallback: Just grab the first substantial div that looks like a post
                // Look for class 'woo-panel-main' (often used in V7)
                targetDiv = document.querySelector('.woo-panel-main') || document.querySelector('article') || document.querySelector('div[class*="feed_item"]');
            }

            if (targetDiv) {
                return {
                    found: true,
                    html: targetDiv.outerHTML, // Full HTML for offline analysis
                    structure: getStructure(targetDiv) // Simplified tree
                };
            }
            return { found: false };
        });

        if (feedStructure.found) {
            console.log('[Weibo] Found feed item structure!');
            fs.writeFileSync(path.join(__dirname, '../feed_item_dump.html'), feedStructure.html);
            fs.writeFileSync(path.join(__dirname, '../feed_item_structure.txt'), feedStructure.structure);
            
            // Take a screenshot of this specific element if possible, or just the page
            await page.screenshot({ path: path.join(__dirname, '../profile_debug.png') });
        } else {
            console.warn('[Weibo] Could not identify a distinct feed item.');
            await page.screenshot({ path: path.join(__dirname, '../profile_debug_fail.png') });
        }

    } catch (error) {
        console.error('[Weibo] Inspection Error:', error);
    } finally {
        await browser.close();
    }
})();
