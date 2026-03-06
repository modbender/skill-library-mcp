import { metasoSearch, metasoChat } from './metaso-api.js';

async function test() {
  console.log('=== 快速测试 ===');
  console.log('');
  
  try {
    console.log('1. 测试搜索功能...');
    const searchResult = await metasoSearch('人工智能', 2, 'document', true, false, true);
    console.log('✅ 搜索结果:');
    console.log(`   完整响应: ${JSON.stringify(searchResult, null, 2)}`);
    
    console.log('');
    console.log('2. 测试聊天功能...');
    const chatResult = await metasoChat([{ role: 'user', content: '什么是机器学习？' }], 'fast', 'webpage', 'simple', false, true);
    console.log('✅ 回答:');
    console.log(`   完整响应: ${JSON.stringify(chatResult, null, 2)}`);
    
    console.log('');
    console.log('=== 测试完成 ===');
  } catch (error) {
    console.error('❌ 测试失败:', error.message);
    console.error('详细错误:', error);
  }
}

test();
