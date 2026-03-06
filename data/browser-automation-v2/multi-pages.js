#!/usr/bin/env node

/**
 * 多页面自动化：批量打开、截图、抓取标题（自动清理）- v2
 * 用法: node multi-pages.js "https://example1.com" "https://example2.com" ...
 */

const BrowserManager = require('./browser-manager.v2');

const urls = process.argv.slice(2);

if (urls.length === 0) {
  console.error('❌ 请提供至少一个URL');
  console.log('用法: node multi-pages.js "https://a.com" "https://b.com"');
  process.exit(1);
}

async function main() {
  const browser = new BrowserManager();
  
  try {
    console.log(`🌐 批量处理 ${urls.length} 个页面`);
    await browser.start();
    
    for (let i = 0; i < urls.length; i++) {
      const url = urls[i];
      console.log(`\n[${i + 1}/${urls.length}] 处理: ${url}`);
      
      await browser.open(url);
      await browser.waitForLoadState('domcontentloaded', 8000); // 智能等待
      
      // 截图
      const screenshotPath = await browser.screenshot();
      console.log('   📸 截图:', screenshotPath);
      
      // 提取标题
      try {
        const titleRes = await browser.runCommand(
          `openclaw browser --browser-profile ${browser.profile} evaluate --fn "document.title"`
        );
        if (titleRes && titleRes.stdout) {
          console.log('   📄 标题:', titleRes.stdout.trim());
        }
      } catch (e) {
        browser.logger.warn('无法获取标题', { url, error: e.message });
      }
      
      // 关闭当前标签页
      await browser.closeTab();
    }
    
    await browser.cleanup();
    console.log('\n✅ 全部完成！');
    
  } catch (e) {
    browser.logger.error('批量处理失败', { error: e.message });
    await browser.cleanup();
    process.exit(1);
  }
}

main();
