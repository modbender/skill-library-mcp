const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const COOKIE_FILE = path.join(__dirname, '../cookies.json');

async function listPosts() {
    if (!fs.existsSync(COOKIE_FILE)) {
        throw new Error('No cookies found. Please run login first.');
    }
    const cookies = JSON.parse(fs.readFileSync(COOKIE_FILE));
    
    console.log(`[Weibo] Listing recent posts...`);
    
    const browser = await puppeteer.launch({
        headless: "new",
        executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
    });

    const page = await browser.newPage();
    await page.setCookie(...cookies);
    
    try {
        await page.goto('https://weibo.com/u/5347147372', { waitUntil: 'networkidle2' });
        await page.waitForSelector('.woo-panel-main', { timeout: 10000 });
        
        // Extract post texts
        const posts = await page.evaluate(() => {
            const items = document.querySelectorAll('article, .woo-panel-main'); // Adjust selector
            return Array.from(items).map(item => {
                // Try to find the text content div
                // Usually `.detail_text` or similar
                const textEl = item.querySelector('.detail_text_1upyt') || item.querySelector('.feed_content') || item;
                return textEl.innerText.trim().substring(0, 100); // First 100 chars
            }).filter(text => text.length > 0);
        });

        console.log('--- Recent Posts ---');
        posts.forEach((p, i) => console.log(`${i + 1}. ${p.replace(/\n/g, ' ')}`));
        
        // Take a screenshot to prove what we see
        await page.screenshot({ path: path.join(__dirname, '../debug_list_posts.png') });

    } catch (error) {
        console.error('[Weibo] List Error:', error);
    } finally {
        await browser.close();
    }
}

if (require.main === module) {
    listPosts().catch(console.error);
}

module.exports = { listPosts };
