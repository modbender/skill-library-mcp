/**
 * DataMaster Pro - 数据抓取脚本
 * 支持网页、API、数据库三种数据源
 */

const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');

// 解析命令行参数
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    url: null,
    api: null,
    db: null,
    selector: 'table',
    method: 'GET',
    headers: {},
    output: 'data.json',
    query: null
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--url':
        options.url = args[++i];
        break;
      case '--api':
        options.api = args[++i];
        break;
      case '--db':
        options.db = args[++i];
        break;
      case '--selector':
        options.selector = args[++i];
        break;
      case '--method':
        options.method = args[++i];
        break;
      case '--headers':
        options.headers = JSON.parse(args[++i]);
        break;
      case '--output':
        options.output = args[++i];
        break;
      case '--query':
        options.query = args[++i];
        break;
    }
  }

  return options;
}

// HTTP 请求封装
function httpRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const lib = urlObj.protocol === 'https:' ? https : http;

    const reqOptions = {
      hostname: urlObj.hostname,
      port: urlObj.port || (urlObj.protocol === 'https:' ? 443 : 80),
      path: urlObj.pathname + urlObj.search,
      method: options.method || 'GET',
      headers: {
        'User-Agent': 'DataMaster-Pro/1.0',
        ...options.headers
      }
    };

    const req = lib.request(reqOptions, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(data);
        } else {
          reject(new Error(`HTTP ${res.statusCode}: ${data}`));
        }
      });
    });

    req.on('error', reject);
    req.end();
  });
}

// 网页抓取 - 简化版HTML解析
function parseHTML(html, selector) {
  const data = [];
  
  // 简单的表格提取
  if (selector.includes('table')) {
    const tableRegex = /<table[^>]*>([\s\S]*?)<\/table>/gi;
    const rowRegex = /<tr[^>]*>([\s\S]*?)<\/tr>/gi;
    const cellRegex = /<t[dh][^>]*>([\s\S]*?)<\/t[dh]>/gi;
    
    let tableMatch;
    while ((tableMatch = tableRegex.exec(html)) !== null) {
      const table = tableMatch[1];
      let rowMatch;
      
      while ((rowMatch = rowRegex.exec(table)) !== null) {
        const row = [];
        const rowContent = rowMatch[1];
        let cellMatch;
        
        while ((cellMatch = cellRegex.exec(rowContent)) !== null) {
          // 清理HTML标签
          let cell = cellMatch[1]
            .replace(/<[^>]+>/g, '')
            .replace(/&nbsp;/g, ' ')
            .replace(/&lt;/g, '<')
            .replace(/&gt;/g, '>')
            .replace(/&amp;/g, '&')
            .trim();
          row.push(cell);
        }
        
        if (row.length > 0) {
          data.push(row);
        }
      }
    }
  }
  
  // 简单的列表提取
  if (selector.includes('li') || selector.includes('list')) {
    const liRegex = /<li[^>]*>([\s\S]*?)<\/li>/gi;
    let match;
    
    while ((match = liRegex.exec(html)) !== null) {
      let text = match[1]
        .replace(/<[^>]+>/g, '')
        .replace(/&nbsp;/g, ' ')
        .trim();
      if (text) {
        data.push({ text });
      }
    }
  }
  
  return data;
}

// API 数据获取
async function fetchAPI(url, method, headers) {
  console.log(`📡 正在请求 API: ${url}`);
  
  try {
    const response = await httpRequest(url, { method, headers });
    const data = JSON.parse(response);
    console.log(`✅ 成功获取 ${Array.isArray(data) ? data.length : 1} 条数据`);
    return data;
  } catch (error) {
    console.error(`❌ API 请求失败: ${error.message}`);
    throw error;
  }
}

// 网页数据抓取
async function fetchWeb(url, selector) {
  console.log(`🌐 正在抓取网页: ${url}`);
  
  try {
    const html = await httpRequest(url);
    const data = parseHTML(html, selector);
    console.log(`✅ 成功解析 ${data.length} 行数据`);
    return data;
  } catch (error) {
    console.error(`❌ 网页抓取失败: ${error.message}`);
    throw error;
  }
}

// 模拟数据库查询（需要实际数据库驱动）
async function fetchDatabase(dbString, query) {
  console.log(`🗄️ 正在连接数据库...`);
  console.log(`📝 执行查询: ${query}`);
  
  // 这里是示例实现
  // 实际使用需要安装对应数据库驱动
  // 如: mysql2, pg, mongodb
  
  console.log('⚠️ 数据库功能需要安装对应驱动');
  console.log('   MySQL: npm install mysql2');
  console.log('   PostgreSQL: npm install pg');
  console.log('   MongoDB: npm install mongodb');
  
  throw new Error('数据库功能需要配置驱动');
}

// 保存数据
function saveData(data, outputFile) {
  const ext = path.extname(outputFile);
  
  if (ext === '.json') {
    fs.writeFileSync(outputFile, JSON.stringify(data, null, 2));
  } else if (ext === '.csv') {
    const csv = convertToCSV(data);
    fs.writeFileSync(outputFile, csv);
  } else {
    fs.writeFileSync(outputFile, JSON.stringify(data, null, 2));
  }
  
  console.log(`💾 数据已保存到: ${outputFile}`);
}

// 转换为CSV
function convertToCSV(data) {
  if (!Array.isArray(data) || data.length === 0) return '';
  
  // 处理对象数组
  if (typeof data[0] === 'object' && !Array.isArray(data[0])) {
    const headers = Object.keys(data[0]);
    const rows = data.map(item => headers.map(h => `"${item[h] || ''}"`).join(','));
    return [headers.join(','), ...rows].join('\n');
  }
  
  // 处理二维数组
  return data.map(row => row.map(cell => `"${cell || ''}"`).join(',')).join('\n');
}

// 主函数
async function main() {
  console.log('╔════════════════════════════════════╗');
  console.log('║   DataMaster Pro - 数据抓取工具    ║');
  console.log('╚════════════════════════════════════╝\n');
  
  const options = parseArgs();
  let data = null;
  
  try {
    if (options.url) {
      data = await fetchWeb(options.url, options.selector);
    } else if (options.api) {
      data = await fetchAPI(options.api, options.method, options.headers);
    } else if (options.db) {
      data = await fetchDatabase(options.db, options.query);
    } else {
      console.log('使用方法:');
      console.log('  node data-fetch.js --url <URL> --selector <选择器>');
      console.log('  node data-fetch.js --api <API_URL> --method <GET|POST>');
      console.log('  node data-fetch.js --db <连接字符串> --query <SQL>');
      console.log('\n示例:');
      console.log('  node data-fetch.js --url "https://example.com/data" --selector "table"');
      console.log('  node data-fetch.js --api "https://api.example.com/v1/data" --output data.json');
      return;
    }
    
    if (data) {
      saveData(data, options.output);
      console.log('\n✨ 抓取完成！');
    }
  } catch (error) {
    console.error('\n❌ 抓取失败:', error.message);
    process.exit(1);
  }
}

main();