/**
 * WebFetch MD 测试脚本
 */

const { fetchAsMarkdown } = require('./index');

async function test() {
  // 测试 URL
  const testUrl = process.argv[2] || 'https://www.ruanyifeng.com/blog/2026/02/weekly-issue-384.html';
  
  console.log('🧪 测试 WebFetch MD');
  console.log('目标 URL:', testUrl);
  console.log('');
  
  const result = await fetchAsMarkdown(testUrl);
  
  if (result.success) {
    console.log('✅ 抓取成功！');
    console.log('📄 标题:', result.title);
    console.log('🖼️ 图片数:', result.imageCount);
    console.log('📝 内容长度:', result.contentLength, '字符');
    console.log('');
    console.log('--- Markdown 内容（前 3000 字符）---');
    console.log(result.markdown.substring(0, 3000));
    console.log('...');
    console.log('');
    console.log('--- 图片列表（前 5 张）---');
    result.images.slice(0, 5).forEach((img, i) => {
      console.log(`${i + 1}. ${img.src}`);
    });
  } else {
    console.error('❌ 抓取失败:', result.error);
  }
}

test();
