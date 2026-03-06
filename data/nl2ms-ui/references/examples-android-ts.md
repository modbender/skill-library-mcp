# Android 端 TypeScript 格式示例脚本

## 示例：发送消息脚本

```typescript
import { AndroidAgent, AndroidDevice, getConnectedDevices } from '@midscene/android';
import "dotenv/config"; // read environment variables from .env file

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

Promise.resolve(
  (async () => {
    console.log('🚀 启动京东ME消息发送流程自动化测试...');
    
    // 获取连接的设备
    const devices = await getConnectedDevices();
    if (devices.length === 0) {
      throw new Error('未找到连接的Android设备');
    }
    
    const page = new AndroidDevice(devices[0].udid);
    console.log(`📱 使用设备: ${devices[0].udid}`);

    // 初始化 Midscene agent，设置中文上下文
    const agent = new AndroidAgent(page, {
      aiActionContext: '处理弹窗和权限请求。如果出现位置权限、用户协议等弹窗，点击同意。如果出现登录页面，请关闭它。',
    });

    try {
      // 👀 连接设备并启动京东ME应用
      await page.connect();
      console.log('设备连接成功');
      
      await page.launch('com.jd.oa');
      console.log('启动京东ME应用');
      
      await sleep(3000); // 等待应用启动

      console.log('\n=== 第一步：搜索用户并进入聊天 ===');
      
      // 👀 点击底部的消息tab
      await agent.aiTap('消息');
      console.log('✅ 已点击底部消息tab');
      await sleep(2000);

      // 👀 点击顶部搜索框
      await agent.aiTap('搜索框');
      console.log('✅ 已点击顶部搜索框');
      await sleep(1000);

      // 👀 在搜索框中输入用户名
      await agent.aiInput('zhencuicui', '搜索框');
      console.log('✅ 已在搜索框中输入用户名: zhencuicui');
      await sleep(3000);

      // 👀 验证搜索结果包含目标用户
      await agent.aiAssert('搜索结果中显示甄翠翠');
      console.log('✅ 验证成功：搜索结果包含甄翠翠');

      console.log('\n=== 第二步：发送消息 ===');

      // 👀 点击搜索结果中的目标用户
      await agent.aiTap('甄翠翠');
      console.log('✅ 已点击搜索结果中的甄翠翠用户，进入聊天页面');
      await sleep(2000);

      // 👀 点击消息输入框获得焦点
      await agent.aiAction('点击消息输入框');
      console.log('✅ 已点击消息输入框，获得输入焦点');
      await sleep(1000);

      // 👀 在输入框中输入测试消息内容
      await agent.aiInput('AI自动化测试', '消息输入框');
      console.log('✅ 已在消息输入框中输入: AI自动化测试');
      await sleep(1000);

      // 👀 点击发送按钮发送消息
      await agent.aiAction('点击发送按钮');
      console.log('✅ 已点击发送按钮');
      await sleep(2000);

      // 👀 验证消息发送成功
      await agent.aiAssert('消息"AI自动化测试"已发送成功');
      console.log('✅ 验证成功：消息已发送并在聊天记录中可见');

      // 👀 返回上一页
      await agent.aiAction('AndroidBackButton');
      console.log('已返回上一页');
      await sleep(1000);

      // 👀 再次返回到主页面
      await agent.aiAction('AndroidBackButton');
      console.log('已返回主页面');

      console.log('\n🎉 京东ME消息发送流程测试完成！');

    } catch (error) {
      console.error('❌ 测试过程中发生错误:', error);
      throw error;
    }
  })()
);

```

## 支持的 Android 操作（TypeScript）

| 操作 | TypeScript 语法 | 说明 |
|------|----------------|------|
| 点击 | `await agent.aiTap('按钮文本')` | 点击指定文本的元素 |
| 输入 | `await agent.aiInput('内容', '输入框定位')` | 在指定输入框输入内容 |
| 操作 | `await agent.aiAction('操作描述')` | AI 驱动的复杂操作 |
| 断言 | `await agent.aiAssert('验证条件')` | 验证页面状态 |
| 查询 | `await agent.aiQuery('查询内容')` | 提取页面信息 |
| 启动应用 | `await device.launch('包名')` | 启动指定应用 |
| 返回 | `await agent.aiAction('AndroidBackButton')` | 触发系统返回键 |
| 等待 | `await sleep(毫秒数)` | 等待指定时间 |
