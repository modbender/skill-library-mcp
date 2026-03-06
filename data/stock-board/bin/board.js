#!/usr/bin/env node

/**
 * Stock Board Screening Tool
 * 股票打板筛选 - 筛选涨停板及强势股
 */

const https = require('https');

function fetchStockList(type = 'zt') {
  return new Promise((resolve, reject) => {
    let url;
    
    // type: zt=涨停, strong=强势, cy=创业板, kc=科创板
    switch (type) {
      case 'strong':
        // 涨幅>=7%, 使用沪深涨幅榜
        url = 'https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=50&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f1,f2,f3,f4,f12,f13,f14';
        break;
      case 'cy':
        // 创业板涨停 >=19.9%
        url = 'https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=100&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:1+t:23&fields=f1,f2,f3,f4,f12,f13,f14';
        break;
      case 'kc':
        // 科创板涨停 >=19.9%
        url = 'https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=100&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:1+t:2&fields=f1,f2,f3,f4,f12,f13,f14';
        break;
      case 'zt':
      default:
        // 沪深涨停板 >=9.9%
        url = 'https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=200&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f1,f2,f3,f4,f12,f13,f14';
        break;
    }

    const timeout = setTimeout(() => reject(new Error('请求超时')), 15000);
    
    const req = https.get(url, { 
      headers: { 
        'Referer': 'https://finance.eastmoney.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      } 
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        clearTimeout(timeout);
        try {
          const result = parseData(data, type);
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

function parseData(data, type) {
  const json = JSON.parse(data);
  if (!json.data || !json.data.diff) {
    return [];
  }
  
  const stocks = json.data.diff.map(item => ({
    code: item.f12,
    name: item.f14,
    price: item.f2,
    change: item.f4,
    percent: item.f3
  })).filter(s => s.price > 0 && s.percent > 0);
  
  // 根据类型过滤
  if (type === 'zt') {
    return stocks.filter(s => s.percent >= 9.9);
  } else if (type === 'strong') {
    return stocks.filter(s => s.percent >= 7);
  } else if (type === 'cy' || type === 'kc') {
    return stocks.filter(s => s.percent >= 19.9);
  }
  
  return stocks.slice(0, 50);
}

function formatOutput(stocks, type) {
  if (stocks.length === 0) {
    return '暂无数据';
  }
  
  let title = '';
  switch (type) {
    case 'zt': title = '📈 涨停板股票'; break;
    case 'strong': title = '🔥 强势股 (≥7%)'; break;
    case 'cy': title = '📈 创业板涨停'; break;
    case 'kc': title = '📈 科创板涨停'; break;
    default: title = '📈 涨停板股票';
  }
  
  let text = `${title} (${stocks.length}只)\n━━━━━━━━━━━━━━━━\n`;
  
  stocks.slice(0, 20).forEach((s, i) => {
    const sign = s.percent >= 0 ? '+' : '';
    text += `${i+1}. ${s.name} ${s.price} ${sign}${s.percent}%\n`;
  });
  
  if (stocks.length > 20) {
    text += `\n...还有 ${stocks.length - 20} 只`;
  }
  
  return text;
}

async function main() {
  const type = process.argv[2] || 'zt';
  
  const validTypes = ['zt', 'strong', 'cy', 'kc'];
  if (!validTypes.includes(type)) {
    console.log('Usage: board [zt|strong|cy|kc]');
    console.log('  zt      - 涨停板 (默认)');
    console.log('  strong  - 强势股 (≥7%)');
    console.log('  cy      - 创业板涨停');
    console.log('  kc      - 科创板涨停');
    process.exit(1);
  }

  try {
    const data = await fetchStockList(type);
    console.log(formatOutput(data, type));
  } catch (e) {
    console.error(`Error: ${e.message}`);
    process.exit(1);
  }
}

main();
