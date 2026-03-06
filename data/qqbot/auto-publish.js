const { chromium } = require('playwright');

(async () => {
  console.log('🚀 启动 ClawHub 自动发布...\n');
  
  const browser = await chromium.launch({ 
    headless: false,  // 显示浏览器窗口
    slowMo: 100       // 减慢操作以便观察
  });
  
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // 1. 访问 ClawHub
    console.log('1️⃣  访问 ClawHub...');
    await page.goto('https://clawhub.com', { timeout: 30000 });
    
    // 2. 检查登录状态
    console.log('2️⃣  检查登录状态...');
    const publishButton = await page.locator('a[href*="publish"], button:has-text("Publish"), a:has-text("Publish")').first();
    
    if (await publishButton.isVisible().catch(() => false)) {
      console.log('   ✅ 已登录');
    } else {
      console.log('   ⏳ 请手动登录 ClawHub...');
      await page.waitForSelector('a[href*="publish"], button:has-text("Publish")', { timeout: 120000 });
    }
    
    // 3. 点击 Publish
    console.log('3️⃣  点击 Publish...');
    await publishButton.click();
    await page.waitForLoadState('networkidle');
    
    // 4. 上传文件
    console.log('4️⃣  上传 skill 包...');
    const fileInput = await page.locator('input[type="file"]').first();
    await fileInput.setInputFiles(process.env.HOME + '/Desktop/qqbot-v1.0.0.zip');
    console.log('   ✅ 文件已选择');
    
    // 等待上传完成
    await page.waitForTimeout(2000);
    
    // 5. 填写表单
    console.log('5️⃣  填写表单信息...');
    
    // 名称
    await page.fill('input[name="name"], input[placeholder*="name" i]', 'qqbot');
    console.log('   ✅ 名称: qqbot');
    
    // 版本
    await page.fill('input[name="version"], input[placeholder*="version" i]', '1.0.0');
    console.log('   ✅ 版本: 1.0.0');
    
    // 描述
    const description = `QQ 官方机器人配置指南，包含完整部署流程和常见问题解决方案

一键配置 QQ 官方机器人，支持私聊、群聊、频道消息。

功能特点:
✅ WebSocket 实时连接
✅ 支持私聊、群聊、频道消息
✅ 内置 AI 处理器接口
✅ 完整的故障排除指南
✅ 自动 IP 白名单监控脚本

安装命令: openclaw skill install qqbot`;
    await page.fill('textarea[name="description"], textarea[placeholder*="description" i]', description);
    console.log('   ✅ 描述已填写');
    
    // 作者
    await page.fill('input[name="author"], input[placeholder*="author" i]', '小皮');
    console.log('   ✅ 作者: 小皮');
    
    // 6. 选择许可证和分类
    console.log('6️⃣  选择许可证和分类...');
    
    // 尝试选择 MIT 许可证
    try {
      await page.selectOption('select[name="license"]', 'MIT');
      console.log('   ✅ 许可证: MIT');
    } catch (e) {
      console.log('   ⚠️  许可证选择失败，可能需要手动选择');
    }
    
    // 尝试选择分类
    try {
      await page.selectOption('select[name="category"]', { label: 'IM' });
      console.log('   ✅ 分类: IM');
    } catch (e) {
      console.log('   ⚠️  分类选择失败，可能需要手动选择');
    }
    
    // 7. 添加标签
    console.log('7️⃣  添加标签...');
    const tags = ['qq', 'bot', 'im', '机器人'];
    for (const tag of tags) {
      try {
        const tagInput = await page.locator('input[placeholder*="tag" i], input[name*="tag"]').first();
        await tagInput.fill(tag);
        await tagInput.press('Enter');
        console.log(`   ✅ 标签: ${tag}`);
      } catch (e) {
        console.log(`   ⚠️  标签 ${tag} 添加失败`);
      }
    }
    
    console.log('\n✅ 表单填写完成！');
    console.log('⏳ 请检查信息是否正确，然后手动点击 Submit 按钮');
    console.log('📝 浏览器将保持打开，等待您确认提交...\n');
    
    // 保持浏览器打开
    await new Promise(() => {});  // 无限等待
    
  } catch (error) {
    console.error('\n❌ 错误:', error.message);
    console.log('\n⚠️  请手动完成发布');
    await browser.close();
    process.exit(1);
  }
})();
