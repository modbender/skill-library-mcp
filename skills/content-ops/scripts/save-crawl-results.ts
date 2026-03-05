import { db, mutations, queries } from '../src/db/index.js';
import { randomUUID } from 'crypto';
import fs from 'fs';

// 读取抓取结果
const crawlResult = JSON.parse(fs.readFileSync('/tmp/xhs_ai_crawled.json', 'utf8'));

// 任务和账号信息
const taskId = '9252b605-f115-464c-a2bc-3014e84a6016';
const sourceAccountId = '08705bf4-86a2-4a3d-a865-37e206bbc65b';

// 批量插入抓取结果
const results = [];
for (const note of crawlResult.notes) {
  // 计算质量分 (基于点赞数)
  let qualityScore = 5;
  if (note.liked_count > 50000) qualityScore = 10;
  else if (note.liked_count > 20000) qualityScore = 9;
  else if (note.liked_count > 10000) qualityScore = 8;
  else if (note.liked_count > 5000) qualityScore = 7;
  else if (note.liked_count > 2000) qualityScore = 6;
  
  // 内容类型: video 或 normal
  const contentType = (note as any).type === 'video' ? 'video' : 
                      (note as any).type === 'normal' ? 'image' : 'mixed';
  
  const result = await mutations.batchInsertCrawlResults([{
    id: randomUUID(),
    taskId: taskId,
    sourceAccountId: sourceAccountId,
    platform: 'xiaohongshu',
    sourceUrl: `https://www.xiaohongshu.com/explore/${note.id}`,
    sourceId: note.id,
    authorName: note.user,
    title: note.title,
    content: `作者: ${note.user} | 点赞: ${note.liked_count} | 收藏: ${note.collected_count} | 评论: ${note.comment_count}`,
    contentType: contentType,
    mediaUrls: note.cover_url ? [note.cover_url] : [],
    metadata: {
      noteId: note.id,
      xsecToken: note.xsec_token,
      coverUrl: note.cover_url,
      likedCount: note.liked_count,
      collectedCount: note.collected_count,
      commentCount: note.comment_count
    },
    qualityScore: qualityScore,
    curationStatus: 'pending',
    isAvailable: false
  }]);
  
  results.push(result[0]);
}

console.log(`✅ 已录入 ${results.length} 条抓取结果到数据库`);
console.log('\n📊 内容质量分布:');
const scores = results.reduce((acc, r) => {
  acc[r.qualityScore] = (acc[r.qualityScore] || 0) + 1;
  return acc;
}, {});
for (const [score, count] of Object.entries(scores).sort((a, b) => b[0] - a[0])) {
  console.log(`   ${score}分: ${count}条`);
}

console.log('\n📝 高质量内容预览:');
for (const r of results.filter(r => r.qualityScore >= 8).slice(0, 5)) {
  console.log(`   ${r.title?.slice(0, 40) || '无标题'}`);
  console.log(`      质量分: ${r.qualityScore} | ID: ${r.id.slice(0, 8)}...`);
}
