const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
require('dotenv').config();

const COOKIE_FILE = path.join(__dirname, '../cookies.json');

async function deletePostByContent(targetText) {
    if (!fs.existsSync(COOKIE_FILE)) {
        throw new Error('No cookies found. Please run login first.');
    }
    const cookies = JSON.parse(fs.readFileSync(COOKIE_FILE));
    
    console.log(`[Weibo] Searching for post containing: "${targetText}"`);
    
    const browser = await puppeteer.launch({
        headless: "new",
        executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 }); // Ensure desktop view
    await page.setCookie(...cookies);
    
    try {
        await page.goto('https://weibo.com/u/5347147372', { waitUntil: 'networkidle2' });
        await page.waitForSelector('.woo-panel-main', { timeout: 10000 });
        
        // Wait a bit for list to render
        await new Promise(r => setTimeout(r, 3000));

        // 1. Find the target post element
        // We evaluate in browser to find the feed item that contains the text
        const targetPostHandle = await page.evaluateHandle((text) => {
            const feeds = document.querySelectorAll('article, .woo-panel-main'); // Adjust selectors based on V6/V7
            for (const feed of feeds) {
                if (feed.innerText.includes(text)) {
                    return feed;
                }
            }
            return null;
        }, targetText);

        if (!targetPostHandle.asElement()) {
            throw new Error(`Post containing "${targetText}" not found on the first page.`);
        }
        
        console.log('[Weibo] Target post found.');
        
        // 2. Find the menu button WITHIN this post
        // The menu button usually has title="展开" or is an arrow icon
        // Or newer V7: <div class="woo-pop-wrap"> <span class="woo-pop-ctrl"> ...
        // We look for ANY clickable thing that looks like a menu trigger inside the card's header/footer (usually right side)
        
        let menuBtn = await targetPostHandle.$('button[title="展开"]');
        if (!menuBtn) menuBtn = await targetPostHandle.$('.ficon_arrow_down');
        if (!menuBtn) menuBtn = await targetPostHandle.$('.woo-font--angleDown');
        if (!menuBtn) menuBtn = await targetPostHandle.$('i[title="更多"]');
        
        if (!menuBtn) {
            throw new Error('Menu button not found in the target post.');
        }

        await menuBtn.click();
        console.log('[Weibo] Opened menu.');
        
        // Wait for menu animation/render
        await new Promise(r => setTimeout(r, 1000));
        
        // 3. Find "Delete" in the popover
        // The popover is often attached to body, not the post itself.
        // We look for the last opened popover or search global text "删除" that is visible
        
        // Take a debug screenshot of the menu
        await page.screenshot({ path: path.join(__dirname, '../debug_menu_open.png') });

        // Try to click "Delete"
        const deleteClicked = await page.evaluate(async () => {
            // Helper to check visibility
            const isVisible = (elem) => {
                return !!(elem.offsetWidth || elem.offsetHeight || elem.getClientRects().length);
            };

            // Find all elements with text "删除"
            // V7 UI: sometimes it's inside a div with class 'woo-box-flex' inside a 'woo-pop-wrap'
            // We'll search broadly
            const candidates = Array.from(document.querySelectorAll('div, li, span, a'));
            const deleteBtns = candidates.filter(el => 
                el.innerText && el.innerText.trim() === '删除' && isVisible(el)
            );
            
            if (deleteBtns.length > 0) {
                // Usually the last one appearing in DOM is the one in the newly opened layer
                const btn = deleteBtns[deleteBtns.length - 1];
                btn.click();
                return true;
            }
            return false;
        });

        if (!deleteClicked) {
            throw new Error('"Delete" option not found or not clickable.');
        }
        
        console.log('[Weibo] Clicked Delete option.');

        // 4. Confirm Dialog
        await new Promise(r => setTimeout(r, 1000));
        await page.screenshot({ path: path.join(__dirname, '../debug_confirm_dialog.png') });

        const confirmClicked = await page.evaluate(async () => {
            const isVisible = (elem) => {
                return !!(elem.offsetWidth || elem.offsetHeight || elem.getClientRects().length);
            };
            
            // Find "确定" button
            const candidates = Array.from(document.querySelectorAll('button, span, a'));
            const confirmBtns = candidates.filter(el => 
                el.textContent.trim() === '确定' && isVisible(el)
            );

            if (confirmBtns.length > 0) {
                confirmBtns[confirmBtns.length - 1].click();
                return true;
            }
            return false;
        });

        if (confirmClicked) {
            console.log('[Weibo] Confirmed deletion.');
        } else {
            throw new Error('Confirm button not found.');
        }

    } catch (error) {
        console.error('[Weibo] Error:', error);
        // Upload debug screenshot if menu open failed
        if (fs.existsSync(path.join(__dirname, '../debug_menu_open.png'))) {
             const uploadCmd = `node skills/feishu-sender/upload_image.js "${path.join(__dirname, '../debug_menu_open.png')}"`;
             try {
                 const key = execSync(uploadCmd).toString().trim().split('\n').pop();
                 console.log(`Debug Image: ${key}`);
             } catch(e) {}
        }
        throw error;
    } finally {
        await browser.close();
    }
}

// CLI
if (require.main === module) {
    const text = process.argv[2];
    if (!text) {
        console.error('Usage: node delete_post.js "content to find"');
        process.exit(1);
    }
    deletePostByContent(text).catch(err => {
        console.error(err);
        process.exit(1);
    });
}

module.exports = { deletePostByContent };
