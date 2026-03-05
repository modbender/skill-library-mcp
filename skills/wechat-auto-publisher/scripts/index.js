/**
 * 微信公众号全自动发布系统
 * 主入口
 */

const HotMonitor = require('./hot-monitor');
const ArticleGenerator = require('./article-generator');
const config = require('./config');

console.log(`
╔═══════════════════════════════════════════════════╗
║     微信公众号全自动发布系统 v1.0                  ║
║     从选题 → 写作 → 发布 全流程自动化               ║
╚═══════════════════════════════════════════════════╝

当前配置:
- 赛道：AI/科技资讯
- 模型：${config.llm.model}
- 自动发布：${config.publish.autoPublish ? '开启' : '关闭（仅生成草稿）'}
- 发布时间：${config.publish.publishTime}
- 每日篇数：${config.publish.postsPerDay}

===============================================
`);

/**
 * 完整流程：监控 → 选题 → 写作 → 发布
 */
async function runFullCycle() {
  console.log('\n🚀 开始完整发布流程...\n');
  
  // 步骤 1：热点监控
  const monitor = new HotMonitor();
  const topics = await monitor.monitor();
  
  if (topics.length === 0) {
    console.log('❌ 没有找到合适的选题，退出');
    return;
  }
  
  // 步骤 2：文章生成
  const generator = new ArticleGenerator();
  const draftCount = config.publish.postsPerDay;
  
  console.log(`\n📝 准备生成 ${draftCount} 篇文章...\n`);
  const drafts = await generator.generateFromMonitor(draftCount);
  
  // 步骤 3：发布（如果开启自动发布）
  if (config.publish.autoPublish) {
    console.log('\n📤 开始自动发布...');
    // TODO: 实现发布逻辑
    console.log('发布功能待实现...');
  } else {
    console.log('\n💡 自动发布已关闭，草稿已保存到 drafts/ 目录');
    console.log('请人工审核后发布');
  }
  
  // 步骤 4：输出报告
  console.log('\n========== 执行报告 ==========');
  console.log(`监控到热点：${topics.length} 个`);
  console.log(`生成草稿：${drafts.length} 篇`);
  console.log('草稿位置：' + path.join(__dirname, 'drafts/'));
  console.log('=============================\n');
  
  return { topics, drafts };
}

/**
 * 仅监控热点
 */
async function runMonitor() {
  const monitor = new HotMonitor();
  return await monitor.monitor();
}

/**
 * 仅生成文章（使用已有选题）
 */
async function runGenerate(limit = 1) {
  const generator = new ArticleGenerator();
  return await generator.generateFromMonitor(limit);
}

// 命令行参数处理
const args = process.argv.slice(2);
const command = args[0];

switch (command) {
  case 'monitor':
    console.log('📊 运行热点监控...\n');
    runMonitor().then(topics => {
      console.log(`\n✅ 监控完成，找到 ${topics.length} 个相关选题`);
    });
    break;
    
  case 'generate':
    console.log('✍️  生成文章...\n');
    const limit = parseInt(args[1]) || 1;
    runGenerate(limit).then(drafts => {
      console.log(`\n✅ 生成了 ${drafts.length} 篇草稿`);
    });
    break;
    
  case 'full':
  default:
    runFullCycle().then(result => {
      console.log('✅ 完整流程执行完毕');
    });
    break;
}

// 辅助函数
const path = require('path');
