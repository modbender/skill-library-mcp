const qingboSearch = require('./index');

async function test() {
  console.log('测试清博开放平台文章搜索Skill');
  
  // 测试1：简单搜索
  console.log('=== 测试1：简单搜索 ===');
  const test1Result = await qingboSearch.main('搜索关于人工智能的文章');
  console.log(test1Result);
  
  // 测试2：带时间范围搜索
  console.log('=== 测试2：带时间范围搜索 ===');
  const test2Result = await qingboSearch.main('查找2024年1月的科技新闻');
  console.log(test2Result);
  
  // 测试3：带平台筛选搜索
  console.log('=== 测试3：带平台筛选搜索 ===');
  const test3Result = await qingboSearch.main('搜索微信平台关于人工智能的文章');
  console.log(test3Result);
  
  // 测试4：统计信息
  console.log('=== 测试4：统计信息 ===');
  const test4Result = await qingboSearch.main('统计2024年关于人工智能的文章数量');
  console.log(test4Result);
}

// 执行测试
test().catch(err => {
  console.error('测试过程中出错:', err);
});
