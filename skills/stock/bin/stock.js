#!/usr/bin/env node

/**
 * Stock Query Tool
 * 查询A股、港股实时行情 (使用新浪接口)
 */

const https = require('https');

function fetchStockData(symbol) {
  return new Promise((resolve, reject) => {
    let code = symbol;
    
    if (/^\d{6}$/.test(symbol)) {
      // A股: 6开头上海，0/3开头深圳
      code = symbol.startsWith('6') ? `sh${symbol}` : `sz${symbol}`;
    } else if (/^\d{5}$/.test(symbol)) {
      // 港股
      code = `hk${symbol}`;
    } else {
      reject(new Error('暂只支持A股(6位数字)和港股(5位数字)'));
      return;
    }

    const url = `https://hq.sinajs.cn/list=${code}`;
    const timeout = setTimeout(() => reject(new Error('请求超时')), 10000);
    
    const req = https.get(url, { headers: { 'Referer': 'https://finance.sina.com.cn' } }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        clearTimeout(timeout);
        try {
          const result = parseStockData(data, symbol, code);
          resolve(result);
        } catch (e) {
          reject(e);
        }
      });
    });
    
    req.on('error', (e) => {
      clearTimeout(timeout);
      reject(e);
    });
  });
}

function parseStockData(data, symbol, code) {
  const match = data.match(/="(.+)"/);
  if (!match) {
    throw new Error('未找到股票数据');
  }
  
  const fields = match[1].split(',');
  
  if (code.startsWith('hk')) {
    // 港股: 0代码,1名称,2开盘,3当前,4最高,5最低,6昨收,...
    const current = parseFloat(fields[3]) || 0;
    const prev = parseFloat(fields[6]) || 0;
    return {
      symbol: symbol,
      name: fields[1] || '',
      price: current,
      change: current - prev,
      changePercent: prev > 0 ? ((current - prev) / prev * 100) : 0,
      open: parseFloat(fields[2]) || 0,
      high: parseFloat(fields[4]) || 0,
      low: parseFloat(fields[5]) || 0,
      prevClose: prev,
      volume: fields[9] || '0',
      market: '港股'
    };
  } else {
    // A股: 0名称,1当前,2涨跌,3涨跌幅,4最高,5最低,6开盘,7昨收,8成交量,9成交额,10换手
    return {
      symbol: symbol,
      name: fields[0] || '',
      price: parseFloat(fields[1]) || 0,
      change: parseFloat(fields[2]) || 0,
      changePercent: parseFloat(fields[3]) || 0,
      open: parseFloat(fields[6]) || 0,
      high: parseFloat(fields[4]) || 0,
      low: parseFloat(fields[5]) || 0,
      prevClose: parseFloat(fields[7]) || 0,
      volume: parseInt(fields[8]) || 0,
      amount: fields[9] || '0',
      turnover: fields[10] || '0',
      market: symbol.startsWith('6') ? '上海' : '深圳'
    };
  }
}

function formatOutput(stock) {
  const sign = stock.change >= 0 ? '+' : '';
  let vol = stock.volume;
  if (typeof vol === 'number') {
    if (vol >= 100000000) {
      vol = (vol / 100000000).toFixed(2) + '亿';
    } else if (vol >= 10000) {
      vol = (vol / 10000).toFixed(2) + '万';
    }
  }
  
  return `
📈 ${stock.name} (${stock.symbol})
━━━━━━━━━━━━━━━━
💰 价格: ${stock.price.toFixed(2)}
📊 涨跌: ${sign}${stock.change.toFixed(2)} (${sign}${stock.changePercent.toFixed(2)}%)
🏷️ 开盘: ${stock.open}
📈 最高: ${stock.high}
📉 最低: ${stock.low}
🔊 成交量: ${vol}
${stock.amount ? `💵 成交额: ${stock.amount}` : ''}
${stock.turnover ? `🔄 换手率: ${stock.turnover}` : ''}
🌍 市场: ${stock.market}
`.trim();
}

async function main() {
  const symbol = process.argv[2];
  
  if (!symbol) {
    console.log('Usage: stock <symbol>');
    console.log('Examples:');
    console.log('  stock 600519  # A股-贵州茅台');
    console.log('  stock 000001  # A股-平安银行');
    console.log('  stock 00700   # 港股-腾讯');
    process.exit(1);
  }

  try {
    const data = await fetchStockData(symbol);
    console.log(formatOutput(data));
  } catch (e) {
    console.error(`Error: ${e.message}`);
    process.exit(1);
  }
}

main();
