#!/usr/bin/env node
/**
 * WebFetch MD - OpenClaw 工具入口
 * 用于被 OpenClaw 直接调用
 * 
 * 用法: node webfetch-md-tool.js --url <URL>
 */

const { fetchAsMarkdown } = require('./index.js');

async function main() {
  const args = process.argv.slice(2);
  const urlIndex = args.indexOf('--url');
  
  if (urlIndex === -1 || !args[urlIndex + 1]) {
    console.error(JSON.stringify({ error: 'Missing --url parameter' }));
    process.exit(1);
  }
  
  const url = args[urlIndex + 1];
  
  try {
    const result = await fetchAsMarkdown(url);
    
    if (result.success) {
      // 输出 JSON 格式供 OpenClaw 解析
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
    }
  } catch (error) {
    console.log(JSON.stringify({
      success: false,
      error: error.message
    }));
  }
}

main();
