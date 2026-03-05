#!/usr/bin/env node

/**
 * 禅道指标数据导出脚本
 * 
 * 支持导出格式：JSON, CSV, Excel
 */

const fs = require('fs');
const path = require('path');

function parseArgs() {
  const args = process.argv.slice(2);
  const params = {};
  
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--format' && args[i + 1]) {
      params.format = args[++i];
    } else if (args[i] === '--output' && args[i + 1]) {
      params.output = args[++i];
    } else if (args[i] === '--input' && args[i + 1]) {
      params.input = args[++i];
    }
  }
  
  return params;
}

function exportToJson(data, outputPath) {
  fs.writeFileSync(outputPath, JSON.stringify(data, null, 2));
  console.log(`✅ JSON 导出成功：${outputPath}`);
}

function exportToCsv(data, outputPath) {
  if (!data || data.length === 0) {
    console.error('❌ 没有数据可导出');
    return;
  }
  
  const headers = Object.keys(data[0]).join(',');
  const rows = data.map(item => 
    Object.values(item).map(v => `"${v}"`).join(',')
  ).join('\n');
  
  const csv = headers + '\n' + rows;
  fs.writeFileSync(outputPath, csv);
  console.log(`✅ CSV 导出成功：${outputPath}`);
}

async function main() {
  const params = parseArgs();
  const format = params.format || 'json';
  const output = params.output || './output/metrics-export';
  const input = params.input || './output/latest-metrics.json';
  
  console.log('📤 开始导出数据...\n');
  
  try {
    // 读取输入数据
    if (!fs.existsSync(input)) {
      console.error(`❌ 输入文件不存在：${input}`);
      console.log('提示：先运行 analyze-tasks.js 生成数据');
      process.exit(1);
    }
    
    const data = JSON.parse(fs.readFileSync(input, 'utf-8'));
    
    // 确保输出目录存在
    const outputDir = path.dirname(output);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // 导出
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const finalOutput = output.includes('.') ? output : `${output}-${timestamp}.${format}`;
    
    if (format === 'json') {
      exportToJson(data, finalOutput);
    } else if (format === 'csv') {
      exportToCsv(data, finalOutput);
    } else {
      console.error(`❌ 不支持的格式：${format}`);
      console.log('支持的格式：json, csv');
      process.exit(1);
    }
    
  } catch (error) {
    console.error('❌ 导出失败:', error.message);
    process.exit(1);
  }
}

main();
