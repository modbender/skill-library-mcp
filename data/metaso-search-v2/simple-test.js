import { metasoSearch, metasoReadPage, metasoChat } from './metaso-api.js';

async function test() {
  console.log('=== 简单功能测试 ===');
  console.log('');
  
  try {
    console.log('1. 测试搜索功能（所有参数明确指定）...');
    const searchResult = await metasoSearch(
      '人工智能', 
      2, 
      'document', 
      true, 
      false, 
      true
    );
    console.log('✅ 搜索结果:');
    console.log(`   找到 ${searchResult.total} 个结果`);
    if (searchResult.data) {
      searchResult.data.slice(0, 2).forEach((item, index) => {
        console.log(`   ${index + 1}. ${item.title}`);
      });
    }
    
    console.log('');
    console.log('2. 测试网页读取功能...');
    const readResult = await metasoReadPage('https://example.com', 'json');
    console.log('✅ 网页读取结果:');
    console.log(`   标题: ${readResult.title}`);
    
    console.log('');
    console.log('3. 测试聊天功能...');
    const chatResult = await metasoChat(
      [{ role: 'user', content: '什么是机器学习？' }], 
      'fast', 
      'webpage', 
      'simple', 
      false, 
      true
    );
    console.log('✅ 聊天功能响应:');
    console.log(`   响应类型: ${typeof chatResult}`);
    console.log(`   完整响应: ${JSON.stringify(chatResult, null, 2)}`);
    
    console.log('');
    console.log('=== 测试完成 ===');
  } catch (error) {
    console.error('❌ 测试失败:', error.message);
    console.error('详细错误:', error);
  }
}

test();
