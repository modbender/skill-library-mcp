# iOS 端 TypeScript 格式示例脚本

## 示例：发送消息脚本

```typescript
import { agentFromWebDriverAgent } from '@midscene/ios';
import "dotenv/config"; // read environment variables from .env file

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

// 主函数，包含简化的错误处理
async function messageSendTest() {
  let agent;
  
  try {
    console.log('🚀 开始初始化 Midscene agent...');
    // 👀 init Midscene agent
    agent = await agentFromWebDriverAgent({
      aiActionContext:
        '如果出现任何位置、权限、用户协议等弹窗，请点击"同意"。如果出现登录页面，请将其关闭。',
    });
    console.log('✅ Midscene agent 初始化成功');

    //PackageName="com.newjdme"  #Appstore and TF
    //PackageName = 'com.testjdme'  #Jenkins

    await agent.launch('com.testjdme');
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

    console.log('\n=== 第二步：输入搜索内容 ===');
    
    // 👀 在搜索框中输入用户名
    await agent.aiInput('左上角的搜索框', {
      value: "zhencuicui"
    });
    console.log('✅ 已在搜索框中输入用户名: zhencuicui');
    await sleep(5000);

    console.log('\n=== 第四步：进入聊天页面 ===');

    // 👀 点击搜索结果中的目标用户
    await agent.aiTap('甄翠翠');
    console.log('✅ 已点击搜索结果中的甄翠翠用户，进入聊天页面');
    await sleep(2000);

    console.log('\n=== 第五步：发送消息 ===');

    // 👀 在输入框中输入测试消息内容
    await agent.aiTap('消息输入框');
    await agent.aiInput("消息输入框", {
      value: "AI自动化测试"
    });
    console.log('✅ 已在消息输入框中输入: AI自动化测试');
    await sleep(1000);

    // 👀 点击发送按钮发送消息
    await agent.aiTap('发送按钮');
    console.log('✅ 已点击发送按钮');
    await sleep(2000);

    console.log('\n=== 第六步：验证消息发送结果 ===');
    
    // 👀 验证消息发送成功
    await agent.aiAssert('消息"AI自动化测试"已发送成功');
    console.log('✅ 验证成功：消息已发送并在聊天记录中可见');

    // 👀 返回上一页
    await agent.aiTap('返回按钮');
    console.log('✅ 已返回上一页');
    await sleep(1000);

    // 👀 再次返回到主页面
    await agent.aiTap('返回按钮');
    console.log('✅ 已返回主页面');
    await sleep(1000);

    console.log('🎉 京东ME消息发送流程测试完成！');

  } catch (error) {
    console.error('❌ 消息发送测试过程中发生错误:', error);
    
    throw error; // 重新抛出原始错误
  } 
}

// 运行测试
messageSendTest()
  .then(() => {
    console.log('✅ 消息发送测试完成');
    process.exit(0);
  })
  .catch((error) => {
    console.error('💥 消息发送测试失败:', error);
    process.exit(1);
  });
```

## 支持的 iOS 操作（TypeScript）

| 方法 | TypeScript 语法 | 说明 |
|------|----------------|------|
| 启动应用 | `await agent.launch('BundleID')` | 启动应用 |
| 点击 | `await agent.aiTap('按钮文本')` | 点击元素 |
| 输入 | `await agent.aiInput('内容', { locate: '输入框' })` | 输入文本 |
| 操作 | `await agent.aiAction('操作描述')` | AI 操作 |
| 断言 | `await agent.aiAssert('验证条件')` | 断言验证 |
| 查询 | `await agent.aiQuery('查询内容')` | 查询信息 |
| 布尔判断 | `await agent.aiBoolean('判断条件')` | 布尔判断 |
| 返回 | `await agent.aiAction('Back')` | 返回上一页 |
| 等待 | `await sleep(毫秒数)` | 等待指定时间 |
