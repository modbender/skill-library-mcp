const { chromium } = require('playwright-core');
const fs = require('fs');

async function verify(sessionFile, url, searchString) {
    if (!fs.existsSync(sessionFile)) {
        console.error('Session file not found');
        return false;
    }

    const sessionData = JSON.parse(fs.readFileSync(sessionFile, 'utf8'));
    
    // Sandbox is ALWAYS enabled for security.
    const browser = await chromium.launch({
        executablePath: '/usr/bin/chromium-browser',
        headless: true,
        args: [
            '--no-first-run',
            '--no-zygote'
        ]
    });
    
    const context = await browser.newContext();
    await context.addCookies(sessionData.cookies);
    
    const page = await context.newPage();
    await page.goto(url);
    await page.waitForTimeout(3000);
    
    const content = await page.content();
    const success = content.toLowerCase().includes(searchString.toLowerCase());
    
    await browser.close();
    return success;
}

if (require.main === module) {
    const args = process.argv.slice(2);
    const file = args[0];
    const url = args[1];
    const str = args[2];
    verify(file, url, str).then(res => {
        console.log(res ? 'SUCCESS' : 'FAILURE');
        process.exit(res ? 0 : 1);
    });
}
