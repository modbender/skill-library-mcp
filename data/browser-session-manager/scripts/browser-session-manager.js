const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

/**
 * Browser Session Manager
 * Applies cookies, localStorage, and sessionStorage from JSON file before visiting a website
 */

async function applySessionData(url, sessionJsonPath, options = {}) {
  const {
    headless = true,
    screenshotPath = null,
    waitTime = 5000,
    actions = []
  } = options;

  // Read session data
  const sessionData = JSON.parse(fs.readFileSync(sessionJsonPath, 'utf8'));
  
  console.log('🌐 启动浏览器...');
  const browser = await chromium.launch({
    headless,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 }
  });

  const page = await context.newPage();

  // Apply cookies if present
  if (sessionData.cookies && sessionData.cookies.length > 0) {
    console.log(`🍪 设置 ${sessionData.cookies.length} 个 cookies...`);
    
    // Group cookies by domain for proper setting
    const cookiesByDomain = {};
    for (const cookie of sessionData.cookies) {
      const domain = cookie.domain || new URL(url).hostname;
      if (!cookiesByDomain[domain]) {
        cookiesByDomain[domain] = [];
      }
      
      // Format cookie for Playwright
      // Convert sameSite values to Playwright-compatible format
      let sameSite = cookie.sameSite;
      if (sameSite === 'unspecified' || sameSite === 'no_restriction') {
        sameSite = undefined;
      } else if (sameSite === 'strict') {
        sameSite = 'Strict';
      } else if (sameSite === 'lax') {
        sameSite = 'Lax';
      } else if (sameSite === 'none') {
        sameSite = 'None';
      }
      
      const formattedCookie = {
        name: cookie.name,
        value: cookie.value,
        domain: cookie.domain,
        path: cookie.path || '/',
        secure: cookie.secure || false,
        httpOnly: cookie.httpOnly || false
      };
      
      if (sameSite) {
        formattedCookie.sameSite = sameSite;
      }
      
      // Handle expiration if present
      if (cookie.expirationDate) {
        formattedCookie.expires = Math.floor(new Date(cookie.expirationDate).getTime() / 1000);
      }
      
      cookiesByDomain[domain].push(formattedCookie);
    }
    
    // Set cookies - need to visit the domain first for some cookies
    for (const [domain, cookies] of Object.entries(cookiesByDomain)) {
      try {
        // Navigate to the domain first to set cookies properly
        const protocol = cookies[0].secure ? 'https' : 'http';
        const cookieUrl = `${protocol}://${domain.replace(/^\./, '')}`;
        await page.goto(cookieUrl, { timeout: 10000 }).catch(() => {});
        await context.addCookies(cookies);
        console.log(`  ✓ 已设置 ${cookies.length} 个 cookies 到 ${domain}`);
      } catch (e) {
        console.error(`  ✗ 设置 cookies 到 ${domain} 失败:`, e.message);
      }
    }
  }

  // Navigate to target URL
  console.log(`🔗 访问目标页面: ${url}`);
  await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });

  // Apply localStorage if present
  if (sessionData.localStorage && Object.keys(sessionData.localStorage).length > 0) {
    console.log(`💾 设置 ${Object.keys(sessionData.localStorage).length} 个 localStorage 项...`);
    await page.evaluate((data) => {
      for (const [key, value] of Object.entries(data)) {
        try {
          localStorage.setItem(key, value);
        } catch (e) {
          console.error(`设置 localStorage[${key}] 失败:`, e);
        }
      }
    }, sessionData.localStorage);
  }

  // Apply sessionStorage if present
  if (sessionData.sessionStorage && Object.keys(sessionData.sessionStorage).length > 0) {
    console.log(`📦 设置 ${Object.keys(sessionData.sessionStorage).length} 个 sessionStorage 项...`);
    await page.evaluate((data) => {
      for (const [key, value] of Object.entries(data)) {
        try {
          sessionStorage.setItem(key, value);
        } catch (e) {
          console.error(`设置 sessionStorage[${key}] 失败:`, e);
        }
      }
    }, sessionData.sessionStorage);
  }

  // Reload page to apply storage changes
  console.log('🔄 刷新页面以应用存储数据...');
  await page.reload({ waitUntil: 'networkidle' });

  // Wait for specified time
  if (waitTime > 0) {
    console.log(`⏱️  等待 ${waitTime}ms...`);
    await page.waitForTimeout(waitTime);
  }

  // Execute custom actions if provided
  for (const action of actions) {
    console.log(`🎬 执行动作: ${action.type}`);
    switch (action.type) {
      case 'click':
        await page.click(action.selector);
        break;
      case 'fill':
        await page.fill(action.selector, action.value);
        break;
      case 'wait':
        await page.waitForTimeout(action.time || 3000);
        break;
      case 'screenshot':
        const ssPath = action.path || '/tmp/screenshot.png';
        await page.screenshot({ path: ssPath, fullPage: action.fullPage || false });
        console.log(`📸 截图已保存: ${ssPath}`);
        break;
    }
  }

  // Take final screenshot if requested
  if (screenshotPath) {
    await page.screenshot({ path: screenshotPath, fullPage: false });
    console.log(`📸 截图已保存: ${screenshotPath}`);
  }

  // Get page info
  const pageInfo = {
    title: await page.title(),
    url: page.url(),
    cookies: await context.cookies(),
    localStorage: await page.evaluate(() => {
      const data = {};
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        data[key] = localStorage.getItem(key);
      }
      return data;
    }),
    sessionStorage: await page.evaluate(() => {
      const data = {};
      for (let i = 0; i < sessionStorage.length; i++) {
        const key = sessionStorage.key(i);
        data[key] = sessionStorage.getItem(key);
      }
      return data;
    })
  };

  await browser.close();
  console.log('✅ 浏览器已关闭');

  return pageInfo;
}

// CLI usage
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.length < 2) {
    console.log('用法: node browser-session-manager.js <url> <session-json-path> [screenshot-path]');
    console.log('');
    console.log('示例:');
    console.log('  node browser-session-manager.js https://example.com/session.json');
    console.log('  node browser-session-manager.js https://example.com/session.json /tmp/screenshot.png');
    process.exit(1);
  }

  const [url, sessionJsonPath, screenshotPath] = args;

  applySessionData(url, sessionJsonPath, { screenshotPath })
    .then(info => {
      console.log('\n📊 页面信息:');
      console.log(`  标题: ${info.title}`);
      console.log(`  URL: ${info.url}`);
      console.log(`  Cookies: ${info.cookies.length} 个`);
      console.log(`  localStorage: ${Object.keys(info.localStorage).length} 项`);
      console.log(`  sessionStorage: ${Object.keys(info.sessionStorage).length} 项`);
    })
    .catch(err => {
      console.error('❌ 错误:', err.message);
      process.exit(1);
    });
}

module.exports = { applySessionData };