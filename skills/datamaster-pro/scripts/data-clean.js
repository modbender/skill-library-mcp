/**
 * DataMaster Pro - 数据清洗脚本
 * 支持去重、补缺、格式化、异常检测
 */

const fs = require('fs');
const path = require('path');

// 解析命令行参数
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    input: null,
    output: 'clean.csv',
    rules: null,
    removeDuplicates: true,
    fillMissing: 'mean',
    detectOutliers: true,
    normalizeColumns: []
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--input':
      case '-i':
        options.input = args[++i];
        break;
      case '--output':
      case '-o':
        options.output = args[++i];
        break;
      case '--rules':
        options.rules = args[++i];
        break;
      case '--remove-duplicates':
        options.removeDuplicates = args[++i] === 'true';
        break;
      case '--fill-missing':
        options.fillMissing = args[++i];
        break;
      case '--detect-outliers':
        options.detectOutliers = args[++i] === 'true';
        break;
      case '--normalize':
        options.normalizeColumns = args[++i].split(',');
        break;
    }
  }

  return options;
}

// 读取数据文件
function readData(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  const content = fs.readFileSync(filePath, 'utf-8');

  if (ext === '.json') {
    return JSON.parse(content);
  } else if (ext === '.csv') {
    return parseCSV(content);
  } else {
    throw new Error(`不支持的文件格式: ${ext}`);
  }
}

// 解析CSV
function parseCSV(content) {
  const lines = content.trim().split('\n');
  if (lines.length === 0) return [];

  const headers = parseCSVLine(lines[0]);
  const data = [];

  for (let i = 1; i < lines.length; i++) {
    const values = parseCSVLine(lines[i]);
    const row = {};
    headers.forEach((header, index) => {
      row[header] = values[index] || '';
    });
    data.push(row);
  }

  return data;
}

// 解析CSV行
function parseCSVLine(line) {
  const result = [];
  let current = '';
  let inQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    
    if (char === '"') {
      inQuotes = !inQuotes;
    } else if (char === ',' && !inQuotes) {
      result.push(current.trim());
      current = '';
    } else {
      current += char;
    }
  }
  
  result.push(current.trim());
  return result;
}

// 转换为CSV
function toCSV(data) {
  if (!Array.isArray(data) || data.length === 0) return '';

  const headers = Object.keys(data[0]);
  const lines = [headers.join(',')];

  data.forEach(row => {
    const values = headers.map(h => {
      const value = row[h];
      if (value === null || value === undefined) return '';
      const str = String(value);
      return str.includes(',') || str.includes('"') ? `"${str}"` : str;
    });
    lines.push(values.join(','));
  });

  return lines.join('\n');
}

// 去重
function removeDuplicates(data, keyColumns = null) {
  console.log('🔍 执行去重...');
  const seen = new Set();
  const result = [];

  data.forEach(row => {
    const key = keyColumns 
      ? keyColumns.map(col => row[col]).join('|')
      : JSON.stringify(row);
    
    if (!seen.has(key)) {
      seen.add(key);
      result.push(row);
    }
  });

  console.log(`   去重前: ${data.length} 条`);
  console.log(`   去重后: ${result.length} 条`);
  console.log(`   移除: ${data.length - result.length} 条重复数据`);

  return result;
}

// 填充缺失值
function fillMissing(data, strategy = 'mean') {
  console.log('🔧 填充缺失值...');
  
  // 统计缺失情况
  const columns = Object.keys(data[0] || {});
  const missingStats = {};
  
  columns.forEach(col => {
    const values = data.map(row => row[col]).filter(v => v !== null && v !== undefined && v !== '');
    const missing = data.length - values.length;
    if (missing > 0) {
      missingStats[col] = { total: data.length, missing, values };
    }
  });

  // 根据策略填充
  Object.entries(missingStats).forEach(([col, stats]) => {
    const numericValues = stats.values
      .map(v => parseFloat(v))
      .filter(v => !isNaN(v));

    let fillValue;
    
    if (strategy === 'mean' && numericValues.length > 0) {
      fillValue = numericValues.reduce((a, b) => a + b, 0) / numericValues.length;
      fillValue = Math.round(fillValue * 100) / 100;
    } else if (strategy === 'median' && numericValues.length > 0) {
      const sorted = numericValues.sort((a, b) => a - b);
      fillValue = sorted[Math.floor(sorted.length / 2)];
    } else if (strategy === 'mode') {
      const counts = {};
      stats.values.forEach(v => {
        counts[v] = (counts[v] || 0) + 1;
      });
      fillValue = Object.entries(counts).sort((a, b) => b[1] - a[1])[0][0];
    } else if (strategy === 'zero' || strategy === '0') {
      fillValue = 0;
    } else {
      fillValue = '';
    }

    // 应用填充
    data.forEach(row => {
      if (row[col] === null || row[col] === undefined || row[col] === '') {
        row[col] = fillValue;
      }
    });

    console.log(`   列 "${col}": 填充 ${stats.missing} 个缺失值为 ${fillValue}`);
  });

  return data;
}

// 异常值检测 (IQR方法)
function detectOutliers(data, columns = null) {
  console.log('📊 检测异常值...');
  
  const allColumns = columns || Object.keys(data[0] || {});
  const outlierCount = {};

  allColumns.forEach(col => {
    const values = data
      .map(row => parseFloat(row[col]))
      .filter(v => !isNaN(v));

    if (values.length === 0) return;

    values.sort((a, b) => a - b);
    
    const q1 = values[Math.floor(values.length * 0.25)];
    const q3 = values[Math.floor(values.length * 0.75)];
    const iqr = q3 - q1;
    
    const lower = q1 - 1.5 * iqr;
    const upper = q3 + 1.5 * iqr;

    let count = 0;
    data.forEach(row => {
      const val = parseFloat(row[col]);
      if (!isNaN(val) && (val < lower || val > upper)) {
        row[`${col}_outlier`] = true;
        count++;
      }
    });

    if (count > 0) {
      outlierCount[col] = count;
      console.log(`   列 "${col}": 发现 ${count} 个异常值 (范围: ${lower.toFixed(2)} ~ ${upper.toFixed(2)})`);
    }
  });

  return data;
}

// 数据标准化
function normalize(data, columns) {
  console.log('📏 标准化数据...');
  
  columns.forEach(col => {
    const values = data
      .map(row => parseFloat(row[col]))
      .filter(v => !isNaN(v));

    if (values.length === 0) return;

    const min = Math.min(...values);
    const max = Math.max(...values);
    const range = max - min;

    if (range === 0) return;

    data.forEach(row => {
      const val = parseFloat(row[col]);
      if (!isNaN(val)) {
        row[`${col}_normalized`] = (val - min) / range;
      }
    });

    console.log(`   列 "${col}": 标准化到 [0, 1]`);
  });

  return data;
}

// 数据类型转换
function convertTypes(data, rules) {
  console.log('🔄 转换数据类型...');

  Object.entries(rules).forEach(([col, type]) => {
    data.forEach(row => {
      const val = row[col];
      
      if (val === null || val === undefined || val === '') return;

      switch (type) {
        case 'number':
          row[col] = parseFloat(val) || 0;
          break;
        case 'integer':
          row[col] = parseInt(val) || 0;
          break;
        case 'string':
          row[col] = String(val);
          break;
        case 'boolean':
          row[col] = ['true', '1', 'yes', '是'].includes(String(val).toLowerCase());
          break;
        case 'date':
          row[col] = new Date(val).toISOString().split('T')[0];
          break;
      }
    });

    console.log(`   列 "${col}": 转换为 ${type}`);
  });

  return data;
}

// 数据质量报告
function generateReport(data, originalCount) {
  console.log('\n📋 数据质量报告');
  console.log('═'.repeat(40));
  console.log(`原始数据量: ${originalCount} 条`);
  console.log(`清洗后数据量: ${data.length} 条`);
  console.log(`数据保留率: ${((data.length / originalCount) * 100).toFixed(1)}%`);
  
  const columns = Object.keys(data[0] || {});
  console.log(`\n字段数量: ${columns.length}`);
  
  // 完整性检查
  console.log('\n字段完整性:');
  columns.forEach(col => {
    const filled = data.filter(row => row[col] !== null && row[col] !== undefined && row[col] !== '').length;
    const pct = ((filled / data.length) * 100).toFixed(1);
    const bar = '█'.repeat(Math.floor(pct / 5)) + '░'.repeat(20 - Math.floor(pct / 5));
    console.log(`  ${col.padEnd(20)} [${bar}] ${pct}%`);
  });

  console.log('═'.repeat(40));
}

// 主函数
async function main() {
  console.log('╔════════════════════════════════════╗');
  console.log('║   DataMaster Pro - 数据清洗工具    ║');
  console.log('╚════════════════════════════════════╝\n');

  const options = parseArgs();

  if (!options.input) {
    console.log('使用方法:');
    console.log('  node data-clean.js --input <文件> [选项]');
    console.log('\n选项:');
    console.log('  --output, -o          输出文件 (默认: clean.csv)');
    console.log('  --remove-duplicates   是否去重 (默认: true)');
    console.log('  --fill-missing        填充策略: mean/median/mode/zero (默认: mean)');
    console.log('  --detect-outliers     检测异常值 (默认: true)');
    console.log('  --normalize           标准化列 (逗号分隔)');
    console.log('\n示例:');
    console.log('  node data-clean.js --input data.json --output clean.csv');
    console.log('  node data-clean.js -i data.csv --fill-missing median');
    return;
  }

  try {
    console.log(`📂 读取数据: ${options.input}`);
    const data = readData(options.input);
    const originalCount = Array.isArray(data) ? data.length : 1;
    console.log(`✅ 读取 ${originalCount} 条数据\n`);

    let cleanedData = [...data];

    // 执行清洗步骤
    if (options.removeDuplicates) {
      cleanedData = removeDuplicates(cleanedData);
    }

    if (options.fillMissing) {
      cleanedData = fillMissing(cleanedData, options.fillMissing);
    }

    if (options.detectOutliers) {
      cleanedData = detectOutliers(cleanedData);
    }

    if (options.normalizeColumns.length > 0) {
      cleanedData = normalize(cleanedData, options.normalizeColumns);
    }

    // 生成报告
    generateReport(cleanedData, originalCount);

    // 保存数据
    const ext = path.extname(options.output);
    const content = ext === '.json' 
      ? JSON.stringify(cleanedData, null, 2)
      : toCSV(cleanedData);
    
    fs.writeFileSync(options.output, content);
    console.log(`\n💾 数据已保存到: ${options.output}`);
    console.log('✨ 清洗完成！');

  } catch (error) {
    console.error('\n❌ 清洗失败:', error.message);
    process.exit(1);
  }
}

main();