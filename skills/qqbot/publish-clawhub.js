const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false }); // 设为 true 可无头运行
  const context = await browser.newContext();
  const page = await context.newPage();

  // 登录 ClawHub (如果已登录会跳过)
  await page.goto('https://clawhub.com');
  
  // 等待用户登录
  console.log('请在浏览器中登录 ClawHub...');
  await page.waitForSelector('a[href*="publish"], button:has-text("Publish")', { timeout: 60000 });
  
  // 点击 Publish
  console.log('点击 Publish...');
  await page.click('a[href*="publish"], button:has-text("Publish")');
  
  // 等待上传界面
  await page.waitForSelector('input[type="file"]', { timeout: 30000 });
  
  // 上传文件
  console.log('上传文件...');
  const filePath = process.env.HOME + '/Desktop/qqbot-v1.0.0.zip';
  await page.setInputFiles('input[type="file"]', filePath);
  
  // 填写表单
  console.log('填写表单...');
  await page.fill('input[name="name"], input[placeholder*="name"]', 'qqbot');
  await page.fill('input[name="version"], input[placeholder*="version"]', '1.0.0');
  await page.fill('textarea[name="description"], textarea[placeholder*="description"]', 
    'QQ 官方机器人配置指南，包含完整部署流程和常见问题解决方案\n\n一键配置 QQ 官方机器人，支持私聊、群聊、频道消息。\n\n功能特点:\n✅ WebSocket 实时连接\n✅ 支持私聊、群聊、频道消息\n✅ 内置 AI 处理器接口\n✅ 完整的故障排除指南\n✅ 自动 IP 白名单监控脚本\n\n安装命令: openclaw skill install qqbot');
  
  await page.fill('input[name="author"], input[placeholder*="author"]', '小皮');
  
  // 选择许可证
  await page.selectOption('select[name="license"]', 'MIT');
  
  // 添加标签
  const tags = ['qq', 'bot', 'im', '机器人', 'qq-bot'];
  for (const tag of tags) {
    await page.fill('input[placeholder*="tag"], input[name*="tag"]', tag);
    await page.keyboard.press('Enter');
  }
  
  // 选择分类
  await page.selectOption('select[name="category"]', 'IM');
  
  console.log('表单填写完成，准备提交...');
  console.log('请检查信息是否正确，然后点击 Submit');
  
  // 等待提交按钮可点击
  await page.waitForSelector('button[type="submit"], button:has-text("Submit")', { timeout: 10000 });
  
  console.log('脚本执行完成！请在浏览器中点击 Submit 提交。');
  
  // 保持浏览器打开，等待用户手动提交
  // await browser.close(); // 不关闭，让用户确认提交
})();
