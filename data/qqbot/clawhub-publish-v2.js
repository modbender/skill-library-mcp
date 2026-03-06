const { chromium } = require('playwright');
const path = require('path');
const os = require('os');

(async () => {
  console.log('🚀 启动 ClawHub 自动发布...\n');
  
  const browser = await chromium.launch({
    headless: false,
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
  });
  
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // 1. 访问 ClawHub
    console.log('1️⃣  访问 ClawHub...');
    await page.goto('https://clawhub.com/publish', { waitUntil: 'networkidle', timeout: 60000 });
    console.log('   ✅ 页面加载完成');
    
    // 等待更长时间确保登录完成
    console.log('   ⏳ 等待登录状态稳定...');
    await page.waitForTimeout(8000);
    
    // 2. 等待表单加载
    console.log('2️⃣  等待表单...');
    await page.waitForSelector('input[name="name"], input[placeholder*="name"]', { timeout: 60000 });
    console.log('   ✅ 表单已就绪');
    
    // 3. 填写基本信息（先不上传文件）
    console.log('3️⃣  填写表单...');
    
    await page.fill('input[name="name"]', 'qqbot');
    console.log('   ✅ 名称');
    
    await page.fill('input[name="version"]', '1.0.0');
    console.log('   ✅ 版本');
    
    const description = `QQ 官方机器人配置指南

功能特点:
✅ WebSocket 实时连接
✅ 支持私聊、群聊、频道消息
✅ 内置 AI 处理器接口
✅ 完整的故障排除指南

安装: openclaw skill install qqbot`;
    
    await page.fill('textarea[name="description"]', description);
    console.log('   ✅ 描述');
    
    await page.fill('input[name="author"]', '小皮');
    console.log('   ✅ 作者');
    
    // 4. 尝试选择许可证和分类
    try {
      await page.selectOption('select[name="license"]', 'MIT');
      console.log('   ✅ 许可证');
    } catch (e) {}
    
    try {
      await page.selectOption('select[name="category"]', 'IM');
      console.log('   ✅ 分类');
    } catch (e) {}
    
    // 5. 添加标签
    console.log('4️⃣  添加标签...');
    const tagInput = await page.locator('input[placeholder*="tag"]').first();
    if (tagInput) {
      for (const tag of ['qq', 'bot', 'im', '机器人']) {
        await tagInput.fill(tag);
        await tagInput.press('Enter');
        await page.waitForTimeout(500);
      }
      console.log('   ✅ 标签');
    }
    
    // 6. 上传文件
    console.log('5️⃣  上传文件...');
    const filePath = path.join(os.homedir(), 'Desktop', 'qqbot-v1.0.0.zip');
    
    // 查找文件输入框
    const fileInputs = await page.locator('input[type="file"]').all();
    if (fileInputs.length > 0) {
      await fileInputs[0].setInputFiles(filePath);
      console.log('   ✅ 文件上传成功');
      await page.waitForTimeout(3000);
    } else {
      console.log('   ⚠️  未找到文件上传框，请手动上传');
    }
    
    console.log('\n✅ 表单填写完成！');
    console.log('📝 请检查信息并点击 Submit\n');
    
    // 保持打开
    await new Promise(() => {});
    
  } catch (error) {
    console.error('\n❌ 错误:', error.message);
    await page.screenshot({ path: '/tmp/clawhub-error-v2.png', fullPage: true });
    console.log('📸 截图: /tmp/clawhub-error-v2.png');
    await browser.close();
  }
})();
