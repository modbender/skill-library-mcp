const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
require('dotenv').config();

const COOKIE_FILE = path.join(__dirname, '../cookies.json');
const TARGET_CHAT_ID = process.argv[2]; 

(async () => {
    if (!fs.existsSync(COOKIE_FILE)) {
        console.error('No cookies found. Please run login first.');
        process.exit(1);
    }

    const cookies = JSON.parse(fs.readFileSync(COOKIE_FILE));
    
    console.log('[Weibo] Launching browser to post...');
    const browser = await puppeteer.launch({
        headless: "new",
        executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
    });

    const page = await browser.newPage();
    await page.setCookie(...cookies);
    
    try {
        await page.goto('https://weibo.com', { waitUntil: 'networkidle2' });
        
        // Check if logged in by looking for user avatar or specific element
        const loggedInSelector = 'a[href*="/u/"]'; // Usually profile link
        try {
            await page.waitForSelector(loggedInSelector, { timeout: 5000 });
            console.log('[Weibo] Login verified.');
        } catch (e) {
            console.error('[Weibo] Login check failed. Cookies might be invalid or guest mode.');
            // Take screenshot for debug
            await page.screenshot({ path: path.join(__dirname, '../debug_login_fail.png') });
             // Upload to Feishu
            const uploadCmd = `node skills/feishu-sender/upload_image.js "${path.join(__dirname, '../debug_login_fail.png')}"`;
            const rawOutput = execSync(uploadCmd).toString();
            const imageKey = rawOutput.split('\n')
                .map(line => line.trim())
                .filter(line => line.startsWith('img_'))
                .pop();
            
            const msg = JSON.stringify({
                zh_cn: {
                    title: "登录验证失败 ❌",
                    content: [[{ tag: "text", text: "虽然保存了Cookie，但似乎未登录成功。请看截图：" }],
                              [{ tag: "img", image_key: imageKey }]]
                }
            });
            execSync(`node skills/feishu-sender/send_post.js "${TARGET_CHAT_ID}" '${msg}'`);
            
            throw new Error('Login verification failed');
        }

        // Try to post text
        // Selector for input box: textarea.Form_input_3o77k (dynamic class names are common in Weibo V6)
        // Better: look for "What's new" placeholder or similar
        // Actually, let's just dump the page title and verify user name first.
        const title = await page.title();
        console.log(`[Weibo] Page title: ${title}`);
        
        // Post content
        // This is tricky with dynamic classes.
        // Try to find the main input area.
        // Usually: div[contenteditable="true"] inside the main feed publisher
        
        // Let's just confirm login for now.
        const msg = JSON.stringify({
            zh_cn: {
                title: "微博登录验证成功 ✅",
                content: [[{ tag: "text", text: `成功进入微博首页！标题：${title}` }]]
            }
        });
        execSync(`node skills/feishu-sender/send_post.js "${TARGET_CHAT_ID}" '${msg}'`);

    } catch (error) {
        console.error('[Weibo] Error:', error);
    } finally {
        await browser.close();
    }
})();
