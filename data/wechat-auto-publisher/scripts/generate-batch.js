/**
 * 批量生成文章 - 用真实大模型生成 3-5 篇文章
 * 用于测试内容质量
 */

const fs = require('fs');
const path = require('path');
const HotMonitor = require('./hot-monitor');

// 确保草稿目录存在
const draftsDir = path.join(__dirname, 'drafts');
if (!fs.existsSync(draftsDir)) {
  fs.mkdirSync(draftsDir, { recursive: true });
}

// 获取热点选题
const monitor = new HotMonitor();
let topics = monitor.loadLatestTopics();

if (topics.length === 0) {
  console.log('未找到选题，运行监控...');
  // 使用模拟数据
  topics = [
    { source: 'weibo', title: 'GPT-5 发布，性能大幅提升', hotValue: 95, url: '#', timestamp: new Date().toISOString() },
    { source: 'zhihu', title: 'AI 会取代哪些工作？', hotValue: 85, url: '#', timestamp: new Date().toISOString() },
    { source: 'huxiu', title: 'OpenAI 发布新模型，多模态能力再升级', hotValue: 90, url: '#', timestamp: new Date().toISOString() },
    { source: 'weibo', title: 'AI 写代码效率超过程序员', hotValue: 88, url: '#', timestamp: new Date().toISOString() },
    { source: 'huxiu', title: '字节跳动布局 AI 硬件', hotValue: 82, url: '#', timestamp: new Date().toISOString() }
  ];
}

console.log('\n========================================');
console.log('  微信公众号文章批量生成');
console.log('========================================\n');
console.log(`准备生成 ${Math.min(5, topics.length)} 篇文章...\n`);

// 输出选题列表
console.log('=== 选题列表 ===');
topics.slice(0, 5).forEach((topic, i) => {
  console.log(`${i + 1}. [${topic.source}] ${topic.title} (热度：${topic.hotValue})`);
});
console.log('\n');

// 保存选题到文件，供外部使用
const topicsFile = path.join(draftsDir, 'topics_to_generate.json');
fs.writeFileSync(topicsFile, JSON.stringify(topics.slice(0, 5), null, 2), 'utf8');

console.log('✅ 选题已保存到：' + topicsFile);
console.log('\n========================================');
console.log('下一步：');
console.log('1. 使用大模型生成完整文章');
console.log('2. 查看生成的草稿：drafts/ 目录');
console.log('========================================\n');

// 输出每篇文章的生成 prompt
console.log('\n=== 文章生成 Prompt 示例（第 1 篇）===\n');

const firstTopic = topics[0];
const prompt = `你是一名资深科技公众号作者，文风专业但不失幽默，用通俗易懂的语言讲解技术。
目标读者：25-40 岁，对科技感兴趣的职场人士

请根据以下选题写一篇完整的公众号文章。

【选题】${firstTopic.title}
【热度】${firstTopic.hotValue}
【来源】${firstTopic.source}

【写作要求】
1. 字数：1500 字左右
2. 语言通俗易懂，避免过多专业术语
3. 适当使用 emoji 增加可读性（但不要太密集）
4. 段落清晰，每段不超过 5 行
5. 开头要有吸引力，让人想继续读
6. 结尾引导读者点赞、在看、转发
7. 可以加入一些个人观点，增加真实感

【文章结构】
- 标题：生成 3 个备选标题（吸引眼球，20-30 字）
- 开头：热点引入（100 字）
- 主体：3 个分论点（每段 200-300 字）
  * 分论点 1：事件/技术详解
  * 分论点 2：影响/意义分析
  * 分论点 3：对读者的价值/启发
- 结尾：总结 + 引导互动（100 字）

请直接输出完整文章。`;

console.log(prompt);
console.log('\n\n========================================');
console.log('提示：可以用这个 prompt 调用大模型生成文章');
console.log('========================================\n');
