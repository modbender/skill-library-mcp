// Test suite for Visualization Skill
const { generateVisualization } = require('./main');

async function runTests() {
  console.log('🧪 Running Visualization Skill Tests...\n');
  
  // Test 1: Stock Chart
  try {
    const stockResult = await generateVisualization({
      prompt: 'AAPL 2026年1-2月技术分析',
      template: 'stock'
    });
    console.log('✅ Stock chart test passed:', stockResult.path);
  } catch (e) {
    console.error('❌ Stock chart test failed:', e.message);
  }
  
  // Test 2: Portfolio Dashboard
  try {
    const portfolioResult = await generateVisualization({
      prompt: '投资组合监控 2026年Q1',
      template: 'portfolio'
    });
    console.log('✅ Portfolio dashboard test passed:', portfolioResult.path);
  } catch (e) {
    console.error('❌ Portfolio dashboard test failed:', e.message);
  }
  
  // Test 3: Industry Comparison
  try {
    const industryResult = await generateVisualization({
      prompt: '科技金融能源行业对比 2026年',
      template: 'industry'
    });
    console.log('✅ Industry comparison test passed:', industryResult.path);
  } catch (e) {
    console.error('❌ Industry comparison test failed:', e.message);
  }
  
  console.log('\n🏁 Test suite completed!');
}

runTests().catch(console.error);