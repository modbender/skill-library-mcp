const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
require('dotenv').config();

// Config
const COOKIE_FILE = path.join(__dirname, '../cookies.json');
const LOGIN_URL = 'https://weibo.com/login.php';
const TARGET_CHAT_ID = process.argv[2]; // Passed from caller

(async () => {
    console.log('[Weibo] Launching browser...');
    const browser = await puppeteer.launch({
        headless: "new", // Headless mode
        executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });

    try {
        console.log('[Weibo] Navigating to login page...');
        await page.goto(LOGIN_URL, { waitUntil: 'networkidle2' });

        // Wait for QR code container (adjust selector as needed)
        const qrSelector = '.qrcode-img img'; 
        try {
            await page.waitForSelector(qrSelector, { timeout: 10000 });
        } catch (e) {
            console.log('[Weibo] QR Code selector not found immediately, trying general page screenshot.');
        }
        
        // Take screenshot of QR code area or full page
        const screenshotPath = path.join(__dirname, '../qrcode.png');
        try {
            const element = await page.$(qrSelector);
            if (element) {
                await element.screenshot({ path: screenshotPath });
            } else {
                await page.screenshot({ path: screenshotPath });
            }
        } catch (e) {
            await page.screenshot({ path: screenshotPath });
        }
        
        console.log(`[Weibo] QR Code saved to ${screenshotPath}`);

        // Upload to Feishu
        const uploadCmd = `node skills/feishu-sender/upload_image.js "${screenshotPath}"`;
        const rawOutput = execSync(uploadCmd).toString();
        // Extract image key (it looks like img_v2_... or similar, usually the last line)
        const imageKey = rawOutput.split('\n')
            .map(line => line.trim())
            .filter(line => line.startsWith('img_'))
            .pop();

        console.log(`[Weibo] Image uploaded, key: ${imageKey}`);

        if (!imageKey) {
            console.error(`[Weibo] Upload output: ${rawOutput}`);
            throw new Error(`Failed to extract image key from upload output.`);
        }

        // Send to Feishu
        const msg = JSON.stringify({
            zh_cn: {
                title: "请扫码登录微博 📱",
                content: [
                    [{ tag: "text", text: "检测到登录失效，请使用微博APP扫码登录：" }],
                    [{ tag: "img", image_key: imageKey }],
                    [{ tag: "text", text: "扫码后请等待约 10-20 秒，我会自动保存登录状态。" }]
                ]
            }
        });
        
        // Use send_post logic directly or via exec
        // Since we are inside node, we can just call the script or reuse logic if modular
        // But for now, exec is safest to avoid context issues
        const sendCmd = `node skills/feishu-sender/send_post.js "${TARGET_CHAT_ID}" '${msg}'`;
        execSync(sendCmd);

        // Poll for login success
        console.log('[Weibo] Waiting for login...');
        const maxRetries = 60; // 60 * 2s = 2 minutes
        let loggedIn = false;

        for (let i = 0; i < maxRetries; i++) {
            if (page.url().includes('weibo.com') && !page.url().includes('login.php')) {
                // Check if actually logged in (e.g. user avatar present or specific cookie)
                const cookies = await page.cookies();
                const subCookie = cookies.find(c => c.name === 'SUB'); // Weibo's main auth cookie
                
                if (subCookie) {
                    console.log('[Weibo] Login detected! Saving cookies...');
                    fs.writeFileSync(COOKIE_FILE, JSON.stringify(cookies, null, 2));
                    loggedIn = true;
                    break;
                }
            }
            await new Promise(r => setTimeout(r, 2000));
        }

        if (loggedIn) {
            const successMsg = JSON.stringify({
                zh_cn: {
                    title: "登录成功！🎉",
                    content: [[{ tag: "text", text: "Cookie 已保存。现在可以使用微博技能了！" }]]
                }
            });
            execSync(`node skills/feishu-sender/send_post.js "${TARGET_CHAT_ID}" '${successMsg}'`);
        } else {
            const failMsg = JSON.stringify({
                zh_cn: {
                    title: "登录超时 ❌",
                    content: [[{ tag: "text", text: "等待扫码超时，请重新触发指令。" }]]
                }
            });
            execSync(`node skills/feishu-sender/send_post.js "${TARGET_CHAT_ID}" '${failMsg}'`);
        }

    } catch (error) {
        console.error('[Weibo] Error:', error);
    } finally {
        await browser.close();
    }
})();
