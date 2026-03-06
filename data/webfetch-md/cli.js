#!/usr/bin/env node
/**
 * WebFetch MD CLI - 命令行工具
 * 输出 JSON 格式供下游处理
 */

const { fetchAsMarkdown } = require('./index');

async function main() {
  const args = process.argv.slice(2);
  const urlIndex = args.indexOf('--url');
  
  // 支持 --url 参数或直接传 URL
  let url;
  if (urlIndex !== -1 && args[urlIndex + 1]) {
    url = args[urlIndex + 1];
  } else if (args[0] && !args[0].startsWith('-')) {
    url = args[0];
  }
  
  if (!url) {
    console.log(JSON.stringify({ 
      error: '缺少 URL 参数',
      usage: 'npx webfetch-md <url> 或 npx webfetch-md --url <url>'
    }));
    process.exit(1);
  }
  
  try {
    const result = await fetchAsMarkdown(url);
    
    if (result.success) {
      // 输出 JSON 格式供下游处理
      console.log(JSON.stringify({
        success: true,
        title: result.title,
        markdown: result.markdown,
        images: result.images,
        imageCount: result.imageCount,
        contentLength: result.contentLength
      }));
    } else {
      console.log(JSON.stringify({
        success: false,
        error: result.error
      }));
      process.exit(1);
    }
  } catch (error) {
    console.log(JSON.stringify({
      success: false,
      error: error.message
    }));
    process.exit(1);
  }
}

main();
