/**
 * 测试脚本
 * 快速验证系统是否正常工作
 */

const HotMonitor = require('./hot-monitor');
const ArticleGenerator = require('./article-generator');

async function test() {
  console.log('\n🧪 开始测试微信公众号自动发布系统\n');
  console.log('=' .repeat(50));
  
  // 测试 1：热点监控
  console.log('\n【测试 1】热点监控模块');
  console.log('-' .repeat(50));
  
  const monitor = new HotMonitor();
  const topics = await monitor.monitor();
  
  console.log(`\n✅ 热点监控测试通过，获取到 ${topics.length} 个选题`);
  
  if (topics.length > 0) {
    console.log('\n前 3 个选题：');
    topics.slice(0, 3).forEach((t, i) => {
      console.log(`  ${i + 1}. [${t.source}] ${t.title} (热度：${t.hotValue})`);
    });
  }
  
  // 测试 2：文章生成
  console.log('\n\n【测试 2】文章生成模块');
  console.log('-' .repeat(50));
  
  if (topics.length > 0) {
    const generator = new ArticleGenerator();
    const draft = await generator.generate(topics[0]);
    
    console.log(`\n✅ 文章生成测试通过`);
    console.log(`标题：${draft.title}`);
    console.log(`草稿文件：${draft.fileName}`);
    console.log(`正文字数：${draft.content.length} 字`);
  } else {
    console.log('⚠️  没有选题，跳过文章生成测试');
  }
  
  // 总结
  console.log('\n' + '='.repeat(50));
  console.log('🎉 所有测试完成！');
  console.log('=' .repeat(50));
  console.log('\n下一步：');
  console.log('1. 查看生成的草稿：drafts/ 目录');
  console.log('2. 运行完整流程：node index.js');
  console.log('3. 配置公众号 API：编辑 config.js');
  console.log('');
}

test().catch(err => {
  console.error('❌ 测试失败:', err);
  process.exit(1);
});
