import { db } from '../src/db/index.js';
import { crawlResults } from '../src/db/schema.js';
import { eq, desc } from 'drizzle-orm';

const results = await db.select()
  .from(crawlResults)
  .where(eq(crawlResults.taskId, '9252b605-f115-464c-a2bc-3014e84a6016'))
  .orderBy(desc(crawlResults.qualityScore));

console.log('📋 完整内容数据（含正文）\n');
console.log('='.repeat(60));

for (let i = 0; i < results.length; i++) {
  const r = results[i];
  const contentPreview = (r.content || '').slice(0, 100);
  
  console.log(`\n${String(i + 1).padStart(2, '0')}. ${r.title || '无标题'}`);
  console.log(`    作者: ${r.authorName || '未知'}`);
  console.log(`    正文: ${contentPreview}${(r.content || '').length > 100 ? '...' : ''}`);
  console.log(`    字数: ${(r.content || '').length}`);
  console.log(`    图片: ${(r.mediaUrls || []).length} 张`);
  console.log(`    质量分: ${r.qualityScore}/10`);
}

console.log('\n' + '='.repeat(60));
console.log(`\n总计: ${results.length} 条内容已入库`);
console.log('可用于 redesign 发布到目标平台');
