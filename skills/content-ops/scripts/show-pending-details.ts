import { db } from '../src/db/index.js';
import { crawlResults } from '../src/db/schema.js';
import { eq, desc, and } from 'drizzle-orm';
import fs from 'fs';
import { randomUUID } from 'crypto';

/**
 * 生成待人工补充详情的链接列表
 */
async function generatePendingDetailList() {
  // 获取已审核但没有正文内容的高质量笔记
  const results = await db.select()
    .from(crawlResults)
    .where(
      and(
        eq(crawlResults.taskId, '9252b605-f115-464c-a2bc-3014e84a6016'),
        eq(crawlResults.curationStatus, 'approved'),
        eq(crawlResults.isAvailable, true)
      )
    )
    .orderBy(desc(crawlResults.qualityScore));
  
  // 筛选出内容为空或较短的
  const pendingItems = results.filter(r => {
    const content = r.content || '';
    // 如果 content 只是元数据（少于100字），认为需要补充
    return content.length < 100;
  });
  
  console.log('📋 需要补充详情的笔记列表\n');
  console.log('='.repeat(80));
  
  const output = [];
  
  for (let i = 0; i < pendingItems.length; i++) {
    const item = pendingItems[i];
    const meta = item.metadata || {};
    
    console.log(`\n【${i + 1}】${item.title || '无标题'}`);
    console.log(`   作者: ${item.authorName || '未知'}`);
    console.log(`   质量分: ${item.qualityScore}/10 | 类型: ${item.contentType || 'unknown'}`);
    console.log(`   👍 ${meta.likedCount || 0} | 💾 ${meta.collectedCount || 0} | 💬 ${meta.commentCount || 0}`);
    console.log(`   🔗 ${item.sourceUrl}`);
    console.log(`   🆔 ${item.id}`);
    console.log(`   当前内容长度: ${(item.content || '').length} 字符`);
    
    output.push({
      index: i + 1,
      id: item.id,
      title: item.title,
      author: item.authorName,
      url: item.sourceUrl,
      qualityScore: item.qualityScore,
      type: item.contentType,
      currentContentLength: (item.content || '').length
    });
  }
  
  console.log('\n' + '='.repeat(80));
  console.log(`\n📊 总计: ${pendingItems.length} 条笔记需要补充详情`);
  
  // 保存到文件
  const outputPath = '/tmp/pending_details.json';
  fs.writeFileSync(outputPath, JSON.stringify({
    generatedAt: new Date().toISOString(),
    total: pendingItems.length,
    items: output
  }, null, 2));
  
  console.log(`💾 已保存到: ${outputPath}`);
  
  console.log('\n📝 补充格式:');
  console.log('   详情 【序号】');
  console.log('   [粘贴正文内容]');
  console.log('   ---');
  
  console.log('\n示例:');
  console.log('   详情 1');
  console.log('   这是第一篇笔记的完整正文内容...');
  console.log('   ---');
  
  return pendingItems;
}

generatePendingDetailList();
