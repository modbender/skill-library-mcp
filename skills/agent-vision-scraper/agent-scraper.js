import { AgentBrowser } from '@vercel/agent-browser';
import { chromium } from 'playwright-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';
import dotenv from 'dotenv';

dotenv.config();

chromium.use(StealthPlugin());

const url = process.argv[2];
const userInstruction = process.argv[3];

if (!url || !userInstruction) {
    console.error("❌ 缺少参数。用法: node agent-scraper.js <URL> <INSTRUCTION>");
    process.exit(1);
}

// 给大模型下达的“系统级”视觉增强指令
const augmentedInstruction = `
【核心任务】: ${userInstruction}

【应对风控与验证码协议】：
1. 你正在一个真实的浏览器环境中操作。如果页面弹出了图形验证码（如看图识字、滑块、点选等），请立刻停止报错。
2. 调用你的视觉 (Vision) 能力分析当前页面的截图。
3. 识别出验证码的内容后，找到对应的输入框或坐标，执行填写或点击操作。
4. 验证通过后，继续执行核心任务。
`;

async function run() {
    console.log(`[+] 启动浏览器 (环境: Docker虚拟屏幕 + Stealth指纹)...`);
    
    // 注意：在 Docker 的虚拟屏幕下，我们可以安全地开启有头模式 (headless: false)
    const browser = await chromium.launch({ 
        headless: false, 
        args: [
            '--no-sandbox', 
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage', // 防止 Docker 内存溢出
            '--disable-blink-features=AutomationControlled'
        ]
    }); 
    
    const context = await browser.newContext({
        viewport: { width: 1280, height: 720 },
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        locale: 'zh-CN'
    });
    
    const page = await context.newPage();
    
    try {
        console.log(`[+] 正在导航至: ${url}`);
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
        await page.waitForTimeout(3000); 

        // 尝试把常见的验证码区域滚动到可视区中央，方便大模型截图看清
        await page.evaluate(() => {
            const captchas = document.querySelectorAll('.g-recaptcha, .h-captcha, #cf-turnstile, img[src*="captcha"]');
            if (captchas.length > 0) captchas[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
        });

        console.log(`\n[+] 移交控制权给 Agent-browser...`);
        console.log(`[-] 正在执行指令: "${augmentedInstruction}"`);
        
        const agentBrowser = new AgentBrowser({ page });
        
        // 执行循环：截图 -> LLM 分析 -> 执行动作 -> 截图...
        const result = await agentBrowser.execute(augmentedInstruction);
        
        console.log(`\n[√] 🎉 任务完成，数据提取如下:\n`);
        console.log(JSON.stringify(result, null, 2));

    } catch (error) {
        console.error(`\n[x] 执行失败:`, error);
    } finally {
        await browser.close();
    }
}

run();
