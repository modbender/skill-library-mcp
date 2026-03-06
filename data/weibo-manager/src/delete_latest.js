const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const COOKIE_FILE = path.join(__dirname, '../cookies.json');

async function deleteLatestPost() {
    if (!fs.existsSync(COOKIE_FILE)) {
        throw new Error('No cookies found. Please run login first.');
    }
    const cookies = JSON.parse(fs.readFileSync(COOKIE_FILE));
    
    console.log(`[Weibo] Attempting to delete the latest post...`);
    
    const browser = await puppeteer.launch({
        headless: "new",
        executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
    });

    const page = await browser.newPage();
    await page.setCookie(...cookies);
    
    try {
        await page.goto('https://weibo.com/u/5347147372', { waitUntil: 'networkidle2' });
        
        // Wait for feed list
        await page.waitForSelector('.woo-panel-main', { timeout: 10000 });
        
        // Strategy for New UI:
        // 1. Find the "More/Expand" button (title="展开" or icon title="更多")
        // Based on dump: <button title="展开" ...><svg><title>更多</title></svg></button>
        // It is inside <div class="woo-pop-wrap ..."> <span class="woo-pop-ctrl"> ... 
        
        const menuButtonSelector = 'button[title="展开"], svg title:contains("更多")';
        
        // Wait a bit for JS hydration
        await new Promise(r => setTimeout(r, 2000));

        // Find all "Expand" buttons (there might be one per post)
        // We want the first one that corresponds to a user post (not top nav etc)
        // The dump shows it inside `_right_18dhr_156` which is likely the header/footer of the card
        
        const buttons = await page.$$('button[title="展开"]');
        console.log(`[Weibo] Found ${buttons.length} expand buttons.`);
        
        if (buttons.length > 0) {
            const btn = buttons[0]; // First post usually
            await btn.click();
            console.log('[Weibo] Clicked menu button.');
            
            // Wait for popover
            await new Promise(r => setTimeout(r, 1000));
            
            // Find "Delete" option
            // Improve: Dump menu items to debug
            // Broaden search to include list items or divs with specific class structure if text fails
            // Often in React apps, text is nested deep.
            
            // Re-query elements after wait
            let deleteOption = null;
            
            // Try to find ANY element containing "删除"
            const candidates = await page.evaluateHandle(() => {
                const all = Array.from(document.querySelectorAll('body *'));
                return all.filter(el => 
                    el.textContent && 
                    el.textContent.trim() === '删除' && 
                    el.offsetParent !== null && // visible
                    el.childElementCount === 0 // leaf node
                );
            });
            
            const properties = await candidates.getProperties();
            const children = Array.from(properties.values());
            
            if (children.length > 0) {
                deleteOption = children[0]; // Take the first visible "删除"
            }
            
            if (deleteOption) {
                // Ensure it's visible
                await deleteOption.click();
                console.log('[Weibo] Clicked Delete option.');
                
                // Confirm dialog
                await new Promise(r => setTimeout(r, 1000));
                
                let realConfirm = null;
                const dialogButtons = await page.$$('button, a, span');
                for (const btn of dialogButtons) {
                    const text = await page.evaluate(el => el.textContent, btn);
                    if (text && text.trim() === '确定') {
                         const isVisible = await btn.boundingBox();
                         if (isVisible) {
                             realConfirm = btn;
                             break;
                         }
                    }
                }
                
                if (realConfirm) {
                    await realConfirm.click();
                    console.log('[Weibo] Confirmed deletion.');
                } else {
                    console.warn('[Weibo] Confirm button not found.');
                }
                
            } else {
                console.warn('[Weibo] Delete option not found in menu.');
                // Debug: dump menu content
                // await page.screenshot({ path: 'debug_menu.png' });
            }
        } else {
            console.warn('[Weibo] No expand buttons found.');
        }
        
    } catch (error) {
        console.error('[Weibo] Delete Error:', error);
        await page.screenshot({ path: path.join(__dirname, '../debug_delete_v2_fail.png') });
        throw error;
    } finally {
        await browser.close();
    }
}

if (require.main === module) {
    deleteLatestPost().catch(console.error);
}

module.exports = { deleteLatestPost };
