#!/usr/bin/env node
/**
 * Playwright Stealth Scraper
 * 適用：有 Cloudflare 或反爬保護的網站
 * 速度：中等（5-10 秒）
 * 反爬能力：中（隱藏自動化、真實 UA）
 * 
 * Usage: node playwright-stealth.js <URL>
 * 
 * 環境變數：
 * - HEADLESS=false        顯示瀏覽器
 * - WAIT_TIME=10000       等待時間（毫秒）
 * - SCREENSHOT_PATH=...   截圖路徑
 * - SAVE_HTML=true        儲存 HTML
 * - USER_AGENT=...        自訂 User-Agent
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const url = process.argv[2];
const waitTime = parseInt(process.env.WAIT_TIME || '5000');
const headless = process.env.HEADLESS !== 'false';
const screenshotPath = process.env.SCREENSHOT_PATH || `./screenshot-${Date.now()}.png`;
const saveHtml = process.env.SAVE_HTML === 'true';

// 預設 User-Agent（iPhone）
const defaultUA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1';
const userAgent = process.env.USER_AGENT || defaultUA;

if (!url) {
    console.error('❌ 請提供 URL');
    console.error('用法: node playwright-stealth.js <URL>');
    process.exit(1);
}

(async () => {
    console.log('🕷️  啟動 Playwright Stealth 爬蟲...');
    console.log(`🔒 反爬模式: ${headless ? '無頭' : '有頭'}`);
    const startTime = Date.now();
    
    const browser = await chromium.launch({
        headless: headless,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-blink-features=AutomationControlled',
            '--disable-features=IsolateOrigins,site-per-process',
        ],
    });
    
    const context = await browser.newContext({
        userAgent: userAgent,
        locale: 'zh-HK',
        viewport: { width: 375, height: 812 }, // iPhone size
        extraHTTPHeaders: {
            'Accept-Language': 'zh-HK,zh-TW;q=0.9,zh;q=0.8,en;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        },
    });
    
    // 隱藏自動化特徵
    await context.addInitScript(() => {
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false,
        });
        
        window.chrome = { runtime: {} };
        
        // Mock permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
    });
    
    const page = await context.newPage();
    
    console.log(`📱 導航到: ${url}`);
    try {
        const response = await page.goto(url, {
            waitUntil: 'domcontentloaded',
            timeout: 30000,
        });
        
        console.log(`📡 HTTP Status: ${response.status()}`);
        
        if (response.status() === 403) {
            console.log('⚠️  收到 403，但繼續嘗試...');
        }
        
    } catch (error) {
        console.error(`❌ 導航失敗: ${error.message}`);
    }
    
    console.log(`⏳ 等待 ${waitTime}ms 讓內容載入...`);
    await page.waitForTimeout(waitTime);
    
    // 檢查 Cloudflare
    const cloudflare = await page.evaluate(() => {
        return document.body.innerText.includes('Checking your browser') ||
               document.body.innerText.includes('Just a moment') ||
               document.querySelector('iframe[src*="challenges.cloudflare.com"]') !== null;
    });
    
    if (cloudflare) {
        console.log('🛡️  偵測到 Cloudflare 挑戰，等待額外 10 秒...');
        await page.waitForTimeout(10000);
    }
    
    // 擷取資訊
    const result = await page.evaluate(() => {
        return {
            title: document.title,
            url: window.location.href,
            htmlLength: document.documentElement.outerHTML.length,
            contentPreview: document.body.innerText.substring(0, 1000),
        };
    });
    
    result.cloudflare = cloudflare;
    
    // 截圖
    try {
        await page.screenshot({ path: screenshotPath, fullPage: false, timeout: 10000 });
        console.log(`📸 截圖已儲存: ${screenshotPath}`);
        result.screenshot = screenshotPath;
    } catch (error) {
        console.log(`⚠️  截圖失敗: ${error.message}`);
        result.screenshot = null;
    }
    
    // 儲存 HTML（如果需要）
    if (saveHtml) {
        const htmlPath = screenshotPath.replace(/\.[^.]+$/, '.html');
        const html = await page.content();
        fs.writeFileSync(htmlPath, html);
        console.log(`📄 HTML 已儲存: ${htmlPath}`);
        result.htmlFile = htmlPath;
    }
    
    // 嘗試提取結構化資料（依網站調整）
    const customData = await page.evaluate(() => {
        // 範例：提取所有連結
        const links = Array.from(document.querySelectorAll('a[href*="tid="]'))
            .slice(0, 10)
            .map(a => ({
                text: a.innerText.trim().substring(0, 100),
                href: a.href,
            }));
        
        return { links };
    });
    
    result.data = customData;
    
    const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
    result.elapsedSeconds = elapsed;
    
    console.log('\n✅ 爬取完成！');
    console.log(JSON.stringify(result, null, 2));
    
    await browser.close();
})();
