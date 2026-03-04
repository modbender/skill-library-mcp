#!/usr/bin/env node
/**
 * 博查搜索 API 脚本
 * 
 * 用法: node search.js <query> [options]
 * 
 * 选项 (通过环境变量或命令行参数):
 *   --count <n>       返回结果数量 (1-50, 默认 10)
 *   --freshness <v>   时间范围: noLimit|oneDay|oneWeek|oneMonth|oneYear (默认 noLimit)
 *   --summary         是否返回摘要 (默认 false)
 * 
 * 环境变量:
 *   BOCHA_API_KEY     API Key (必须)
 */

const https = require('https');

// 配置
const API_URL = 'https://api.bocha.cn/v1/web-search';
// API Key 优先级: 环境变量 > 配置文件 > 默认值
const CONFIG_PATH = require('path').join(__dirname, '..', 'config.json');
let configKey = null;
try { configKey = require(CONFIG_PATH).apiKey; } catch (e) {}
const DEFAULT_API_KEY = process.env.BOCHA_API_KEY || configKey || '';

// 解析命令行参数
function parseArgs(args) {
  const result = {
    query: null,
    count: 10,
    freshness: 'noLimit',
    summary: false
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--count' && args[i + 1]) {
      result.count = parseInt(args[++i], 10);
    } else if (arg === '--freshness' && args[i + 1]) {
      result.freshness = args[++i];
    } else if (arg === '--summary') {
      result.summary = true;
    } else if (!arg.startsWith('--') && !result.query) {
      result.query = arg;
    }
  }

  return result;
}

// 调用博查 API
async function bochaSearch(query, options = {}) {
  const apiKey = process.env.BOCHA_API_KEY || DEFAULT_API_KEY;
  
  if (!apiKey) {
    throw new Error('API Key not configured. Set BOCHA_API_KEY env or create config.json');
  }
  
  const payload = JSON.stringify({
    query: query,
    count: options.count || 10,
    freshness: options.freshness || 'noLimit',
    summary: options.summary || false
  });

  return new Promise((resolve, reject) => {
    const url = new URL(API_URL);
    const req = https.request({
      hostname: url.hostname,
      path: url.pathname,
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload)
      }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(new Error(`JSON parse error: ${data}`));
        }
      });
    });

    req.on('error', reject);
    req.write(payload);
    req.end();
  });
}

// 格式化输出 (参考 Brave Search 格式)
function formatOutput(response) {
  // 错误处理
  if (response.code && response.code !== 200) {
    return {
      type: 'error',
      code: response.code,
      message: response.message || 'Unknown error',
      log_id: response.log_id
    };
  }

  const data = response.data;
  if (!data) {
    return {
      type: 'error',
      code: 'NO_DATA',
      message: 'No data in response'
    };
  }

  const webPages = data.webPages?.value || [];
  
  // 无结果
  if (webPages.length === 0) {
    return {
      type: 'search',
      query: data.queryContext?.originalQuery || '',
      totalResults: 0,
      results: []
    };
  }

  // 格式化结果 (只保留文字信息，适合大模型使用)
  const results = webPages.map((page, index) => ({
    index: index + 1,
    title: page.name || '',
    url: page.url || '',
    description: page.snippet || '',
    summary: page.summary || null,
    siteName: page.siteName || '',
    publishedDate: page.datePublished || page.dateLastCrawled || null
  }));

  return {
    type: 'search',
    query: data.queryContext?.originalQuery || '',
    totalResults: data.webPages?.totalEstimatedMatches || results.length,
    resultCount: results.length,
    results: results
  };
}

// 主函数
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
    console.log(`用法: node search.js <query> [options]

选项:
  --count <n>       返回结果数量 (1-50, 默认 10)
  --freshness <v>   时间范围: noLimit|oneDay|oneWeek|oneMonth|oneYear
  --summary         返回网页摘要

示例:
  node search.js "沪电股份"
  node search.js "AI新闻" --count 5 --freshness oneWeek --summary`);
    process.exit(0);
  }

  const options = parseArgs(args);

  if (!options.query) {
    console.error(JSON.stringify({ type: 'error', code: 'NO_QUERY', message: 'Missing query parameter' }));
    process.exit(1);
  }

  try {
    const response = await bochaSearch(options.query, options);
    const output = formatOutput(response);
    console.log(JSON.stringify(output, null, 2));
  } catch (error) {
    console.error(JSON.stringify({ 
      type: 'error', 
      code: 'REQUEST_FAILED', 
      message: error.message 
    }));
    process.exit(1);
  }
}

main();
