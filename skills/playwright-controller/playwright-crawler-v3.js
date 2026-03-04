const { chromium } = require('playwright');

/**
 * 使用 Playwright 获取网页内容并截图
 * @param {string} url - 网页URL
 * @param {Object} options - 配置选项
 * @param {boolean} options.headless - 是否无头模式，默认true
 * @param {number} options.timeout - 超时时间，默认60000ms
 * @param {string} options.screenshotDir - 截图保存目录，默认当前目录
 * @returns {Promise<{ content: string, screenshotPath: string }>}
 */
async function fetchWithPlaywright(url, options = {}) {
  const {
    headless = false, // 有头模式，可以看到浏览器
    timeout = 60000,
    screenshotDir = './screenshots'
  } = options;

  // 确保截图目录存在
  const fs = require('fs');
  if (!fs.existsSync(screenshotDir)) {
    fs.mkdirSync(screenshotDir, { recursive: true });
  }

  const timestamp = Date.now();
  const browser = await chromium.launch({
    headless: false, // 有头模式
    slowMo: 0
  });

  const context = await browser.newContext({
    // 移动端 User-Agent
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    // 移动端视口尺寸（375x800）
    viewport: { width: 375, height: 800 },
    locale: 'zh-CN',
    // 开启移动设备模拟
    isMobile: true
  });

  const page = await context.newPage();

  console.log('⏳ 1. 不设置任何拦截规则，让所有资源正常加载（包括图片、CSS、字体）');
  console.log('⏳ 2. 模拟移动端浏览（375x667）');
  console.log('⏳ 3. 访问网页: ' + url);

  try {
    // 访问页面 - 等待网络空闲
    await page.goto(url, {
      waitUntil: 'networkidle',
      timeout: timeout
    });

    console.log('✅ 页面加载完成');

    // 等待页面完全渲染
    await page.waitForTimeout(2000);

    // 获取页面标题
    const title = await page.title();
    console.log(`📄 页面标题: ${title}`);

    // 生成截图文件名
    const urlParts = url.replace(/^https?:\/\//, '').replace(/[^a-zA-Z0-9]/g, '_');
    const screenshotFilename = `${timestamp}_${urlParts}.png`;
    const screenshotPath = `${screenshotDir}/${screenshotFilename}`;

    // 截取全屏截图
    console.log('📸 3. 截取全屏截图: ' + screenshotPath);
    await page.screenshot({
      path: screenshotPath,
      fullPage: true,
      type: 'png'
    });

    console.log('✅ 截图完成');

    // 获取完整文本内容
    console.log('📝 4. 获取页面文本内容');

    const content = await page.evaluate(() => {
      // 移除不需要的元素
      const elementsToRemove = document.querySelectorAll('script, style, noscript, iframe, nav, footer, header, .ad, .advertisement, .banner');
      elementsToRemove.forEach(el => el.remove());

      // 获取文本内容
      return document.body.innerText;
    });

    console.log(`✅ 文本内容长度: ${content.length} 字符`);

    await browser.close();

    return {
      content,
      screenshotPath,
      title,
      timestamp
    };

  } catch (error) {
    console.error('❌ 获取失败:', error.message);

    // 失败时也截图，保存当前状态
    try {
      const urlParts = url.replace(/^https?:\/\//, '').replace(/[^a-zA-Z0-9]/g, '_');
      const screenshotFilename = `${timestamp}_${urlParts}_error.png`;
      const screenshotPath = `${screenshotDir}/${screenshotFilename}`;

      await page.screenshot({
        path: screenshotPath,
        fullPage: true,
        type: 'png'
      });

      console.log(`📸 错误截图已保存: ${screenshotPath}`);
    } catch (e) {
      console.error('截图失败:', e.message);
    }

    await browser.close();
    throw error;
  }
}

/**
 * 获取网页特定元素并截图
 * @param {string} url - 网页URL
 * @param {string} selector - CSS 选择器
 * @param {Object} options - 配置选项
 * @returns {Promise<{ content: string, screenshotPath: string }>}
 */
async function fetchElementAndScreenshot(url, selector, options = {}) {
  const {
    headless = false, // 有头模式
    timeout = 60000,
    screenshotDir = './screenshots'
  } = options;

  const fs = require('fs');
  if (!fs.existsSync(screenshotDir)) {
    fs.mkdirSync(screenshotDir, { recursive: true });
  }

  const timestamp = Date.now();
  const browser = await chromium.launch({
    headless: false, // 有头模式
    slowMo: 0
  });

  const context = await browser.newContext({
    // 移动端 User-Agent
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    // 移动端视口尺寸（375x800）
    viewport: { width: 375, height: 800 },
    locale: 'zh-CN',
    // 开启移动设备模拟
    isMobile: true
  });

  const page = await context.newPage();

  console.log('⏳ 1. 不设置任何拦截规则，让所有资源正常加载（包括图片、CSS、字体）');
  console.log('⏳ 2. 模拟移动端浏览（375x667）');
  console.log('⏳ 3. 访问网页: ' + url);

  try {
    await page.goto(url, {
      waitUntil: 'networkidle',
      timeout: timeout
    });

    console.log('✅ 页面加载完成');

    await page.waitForTimeout(2000);

    const title = await page.title();
    console.log(`📄 页面标题: ${title}`);

    // 查找元素
    console.log(`⏳ 3. 查找元素: ${selector}`);

    const element = await page.$(selector);
    if (!element) {
      throw new Error(`未找到元素: ${selector}`);
    }

    console.log('✅ 找到元素');

    // 截取元素截图
    const urlParts = url.replace(/^https?:\/\//, '').replace(/[^a-zA-Z0-9]/g, '_');
    const elementFilename = `${timestamp}_${urlParts}_element.png`;
    const screenshotPath = `${screenshotDir}/${elementFilename}`;

    console.log(`📸 4. 截取元素截图: ${screenshotPath}`);

    await element.screenshot({
      path: screenshotPath,
      type: 'png'
    });

    console.log('✅ 截图完成');

    // 获取元素文本内容
    console.log(`📝 5. 获取元素文本`);

    const content = await element.evaluate(el => el.innerText);

    console.log(`✅ 元素文本长度: ${content.length} 字符`);

    await browser.close();

    return {
      content,
      screenshotPath,
      title,
      timestamp
    };

  } catch (error) {
    console.error('❌ 获取失败:', error.message);

    try {
      const urlParts = url.replace(/^https?:\/\//, '').replace(/[^a-zA-Z0-9]/g, '_');
      const elementFilename = `${timestamp}_${urlParts}_element_error.png`;
      const screenshotPath = `${screenshotDir}/${elementFilename}`;

      await element.screenshot({
        path: screenshotPath,
        type: 'png'
      });

      console.log(`📸 错误截图已保存: ${screenshotPath}`);
    } catch (e) {
      console.error('截图失败:', e.message);
    }

    await browser.close();
    throw error;
  }
}

module.exports = {
  fetchWithPlaywright,
  fetchElementAndScreenshot
};
