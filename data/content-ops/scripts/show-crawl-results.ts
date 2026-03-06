import { db } from '../src/db/index.js';
import { crawlResults } from '../src/db/schema.js';
import { eq, desc } from 'drizzle-orm';

// 查询刚抓取的 AI 内容
const results = await db.select()
  .from(crawlResults)
  .where(eq(crawlResults.taskId, '9252b605-f115-464c-a2bc-3014e84a6016'))
  .orderBy(desc(crawlResults.qualityScore));

console.log('📋 小红书 AI 内容抓取结果 - 待审核\n');
console.log(`共 ${results.length} 条内容\n`);

// 按质量分排序
const sorted = results.sort((a, b) => (b.qualityScore || 0) - (a.qualityScore || 0));

for (let i = 0; i < sorted.length; i++) {
  const r = sorted[i];
  const meta = r.metadata || {};
  
  console.log(`${String(i + 1).padStart(2, '0')}. ${r.title || '无标题'}`);
  console.log(`    👤 作者: ${r.authorName || '未知'}`);
  console.log(`    👍 ${meta.likedCount || 0} | 💾 ${meta.collectedCount || 0} | 💬 ${meta.commentCount || 0}`);
  console.log(`    🔗 ${r.sourceUrl}`);
  console.log(`    ⭐ 质量分: ${r.qualityScore}/10 | 状态: ${r.curationStatus}`);
  console.log(`    🆔 ${r.id}`);
  console.log();
}

console.log('───────────────────────────────────────');
console.log('审核操作:');
console.log('  通过某条:  "确认 1,2,3" 或 "通过 1,2,3"');
console.log('  全部通过:  "全部确认"');
console.log('  拒绝某条:  "不要 2" 或 "拒绝 5"');
console.log('  查看详情:  "详情 1"');
console.log('───────────────────────────────────────');
