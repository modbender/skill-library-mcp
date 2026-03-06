#!/usr/bin/env node

/**
 * Alpha Vantage API 客户端
 * 支持股票、外汇、加密货币数据查询
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

const CONFIG_FILE = path.join(__dirname, 'config.json');

// 默认配置
let config = {
  apiKey: 'demo'
};

// 加载配置
function loadConfig() {
  try {
    if (fs.existsSync(CONFIG_FILE)) {
      const data = fs.readFileSync(CONFIG_FILE, 'utf8');
      config = { ...config, ...JSON.parse(data) };
    }
  } catch (e) {
    // 使用默认配置
  }
}

// 保存配置
function saveConfig() {
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
}

/**
 * HTTP GET 请求
 */
function httpGet(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(new Error(`JSON 解析失败：${e.message}`));
        }
      });
    }).on('error', reject);
  });
}

/**
 * 格式化数字
 */
function formatNumber(num, decimals = 2) {
  if (num === undefined || num === null || num === '') return null;
  const n = parseFloat(num);
  return isNaN(n) ? null : Math.round(n * Math.pow(10, decimals)) / Math.pow(10, decimals);
}

/**
 * 查询股票实时报价
 */
async function getQuote(symbol) {
  const url = `https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=${symbol}&apikey=${config.apiKey}`;
  const data = await httpGet(url);
  
  if (data['Error Message']) {
    throw new Error(data['Error Message']);
  }
  if (data['Note']) {
    throw new Error(`API 限流: ${data['Note']}`);
  }
  if (data['Information']) {
    throw new Error(data['Information']);
  }
  
  const quote = data['Global Quote'];
  if (!quote || Object.keys(quote).length === 0) {
    throw new Error(`未找到股票 ${symbol} 的数据`);
  }
  
  return {
    symbol: quote['01. symbol'],
    name: symbol,
    price: formatNumber(quote['05. price'], 2),
    open: formatNumber(quote['02. open'], 2),
    high: formatNumber(quote['03. high'], 2),
    low: formatNumber(quote['04. low'], 2),
    volume: parseInt(quote['06. volume']),
    change: formatNumber(quote['09. change'], 2),
    changePercent: formatNumber(quote['10. change percent']?.replace('%', ''), 2),
    timestamp: new Date().toISOString(),
  };
}

/**
 * 获取历史 K 线数据
 */
async function getTimeSeries(symbol, outputSize = 'compact') {
  const url = `https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=${symbol}&outputsize=${outputSize}&apikey=${config.apiKey}`;
  const data = await httpGet(url);
  
  if (data['Error Message']) {
    throw new Error(data['Error Message']);
  }
  if (data['Note']) {
    throw new Error(`API 限流: ${data['Note']}`);
  }
  
  const timeSeries = data['Time Series (Daily)'];
  if (!timeSeries) {
    throw new Error(`未找到股票 ${symbol} 的数据`);
  }
  
  const dates = Object.keys(timeSeries).slice(0, 30);
  const klines = dates.map(date => {
    const d = timeSeries[date];
    return {
      date: date,
      open: formatNumber(d['1. open'], 2),
      high: formatNumber(d['2. high'], 2),
      low: formatNumber(d['3. low'], 2),
      close: formatNumber(d['4. close'], 2),
      volume: parseInt(d['5. volume']),
    };
  });
  
  return {
    symbol: symbol,
    type: 'daily',
    count: klines.length,
    data: klines,
  };
}

/**
 * 获取周 K 线
 */
async function getWeekly(symbol) {
  const url = `https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol=${symbol}&apikey=${config.apiKey}`;
  const data = await httpGet(url);
  
  if (data['Error Message']) {
    throw new Error(data['Error Message']);
  }
  if (data['Note']) {
    throw new Error(`API 限流: ${data['Note']}`);
  }
  
  const timeSeries = data['Weekly Time Series'];
  if (!timeSeries) {
    throw new Error(`未找到股票 ${symbol} 的数据`);
  }
  
  const dates = Object.keys(timeSeries).slice(0, 30);
  const klines = dates.map(date => {
    const d = timeSeries[date];
    return {
      date: date,
      open: formatNumber(d['1. open'], 2),
      high: formatNumber(d['2. high'], 2),
      low: formatNumber(d['3. low'], 2),
      close: formatNumber(d['4. close'], 2),
      volume: parseInt(d['5. volume']),
    };
  });
  
  return {
    symbol: symbol,
    type: 'weekly',
    count: klines.length,
    data: klines,
  };
}

/**
 * 获取月 K 线
 */
async function getMonthly(symbol) {
  const url = `https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol=${symbol}&apikey=${config.apiKey}`;
  const data = await httpGet(url);
  
  if (data['Error Message']) {
    throw new Error(data['Error Message']);
  }
  if (data['Note']) {
    throw new Error(`API 限流: ${data['Note']}`);
  }
  
  const timeSeries = data['Monthly Time Series'];
  if (!timeSeries) {
    throw new Error(`未找到股票 ${symbol} 的数据`);
  }
  
  const dates = Object.keys(timeSeries).slice(0, 30);
  const klines = dates.map(date => {
    const d = timeSeries[date];
    return {
      date: date,
      open: formatNumber(d['1. open'], 2),
      high: formatNumber(d['2. high'], 2),
      low: formatNumber(d['3. low'], 2),
      close: formatNumber(d['4. close'], 2),
      volume: parseInt(d['5. volume']),
    };
  });
  
  return {
    symbol: symbol,
    type: 'monthly',
    count: klines.length,
    data: klines,
  };
}

/**
 * 查询外汇汇率
 */
async function getForex(from, to) {
  const url = `https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=${from}&to_currency=${to}&apikey=${config.apiKey}`;
  const data = await httpGet(url);
  
  if (data['Error Message']) {
    throw new Error(data['Error Message']);
  }
  if (data['Note']) {
    throw new Error(`API 限流: ${data['Note']}`);
  }
  
  const rate = data['Realtime Currency Exchange Rate'];
  if (!rate) {
    throw new Error(`未找到 ${from}/${to} 的汇率数据`);
  }
  
  return {
    from: rate['1. From_Currency Code'],
    to: rate['3. To_Currency Code'],
    rate: formatNumber(rate['5. Exchange Rate'], 6),
    timestamp: rate['6. Last Refreshed'],
  };
}

/**
 * 查询加密货币
 */
async function getCrypto(from, to) {
  const url = `https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=${from}&to_currency=${to}&apikey=${config.apiKey}`;
  const data = await httpGet(url);
  
  if (data['Error Message']) {
    throw new Error(data['Error Message']);
  }
  if (data['Note']) {
    throw new Error(`API 限流: ${data['Note']}`);
  }
  
  const rate = data['Realtime Currency Exchange Rate'];
  if (!rate) {
    throw new Error(`未找到 ${from}/${to} 的数据`);
  }
  
  return {
    from: rate['1. From_Currency Code'],
    fromName: rate['2. From_Currency Name'],
    to: rate['3. To_Currency Code'],
    toName: rate['4. To_Currency Name'],
    rate: formatNumber(rate['5. Exchange Rate'], 8),
    timestamp: rate['6. Last Refreshed'],
  };
}

/**
 * 主函数
 */
async function main() {
  loadConfig();
  
  const args = process.argv.slice(2);
  const command = args[0];
  
  if (!command || command === 'help') {
    console.log(`
Alpha Vantage 金融数据 API

用法：
  node alpha.js <command> [options]

命令:
  quote <symbol>       查询股票实时报价
  daily <symbol>      获取日K线数据
  weekly <symbol>     获取周K线数据
  monthly <symbol>    获取月K线数据
  forex <from>/<to>   查询外汇汇率
  crypto <from>/<to>  查询加密货币汇率
  apikey <key>        设置 API key

示例:
  node alpha.js quote AAPL              # 苹果股票
  node alpha.js daily AAPL              # 日K线
  node alpha.js forex USD/JPY           # 美元兑日元
  node alpha.js crypto BTC/USD         # 比特币
  node alpha.js apikey YOUR_API_KEY     # 设置 API key

注意: 默认使用 demo key，有严格限流。建议申请免费 API key:
  https://www.alphavantage.co/support/#api-key
`);
    process.exit(0);
  }
  
  try {
    let result;
    
    switch (command) {
      case 'apikey':
        if (!args[1]) {
          console.error('请提供 API key');
          process.exit(1);
        }
        config.apiKey = args[1];
        saveConfig();
        console.log(`API key 已设置为: ${args[1]}`);
        process.exit(0);
        
      case 'quote':
        if (!args[1]) {
          console.error('请提供股票代码');
          process.exit(1);
        }
        result = await getQuote(args[1].toUpperCase());
        break;
        
      case 'daily':
        if (!args[1]) {
          console.error('请提供股票代码');
          process.exit(1);
        }
        result = await getTimeSeries(args[1].toUpperCase(), 'compact');
        break;
        
      case 'weekly':
        if (!args[1]) {
          console.error('请提供股票代码');
          process.exit(1);
        }
        result = await getWeekly(args[1].toUpperCase());
        break;
        
      case 'monthly':
        if (!args[1]) {
          console.error('请提供股票代码');
          process.exit(1);
        }
        result = await getMonthly(args[1].toUpperCase());
        break;
        
      case 'forex':
        if (!args[1]) {
          console.error('请提供货币对，如 USD/JPY');
          process.exit(1);
        }
        const [forexFrom, forexTo] = args[1].split('/');
        if (!forexFrom || !forexTo) {
          console.error('格式错误，请使用 USD/JPY 格式');
          process.exit(1);
        }
        result = await getForex(forexFrom.toUpperCase(), forexTo.toUpperCase());
        break;
        
      case 'crypto':
        if (!args[1]) {
          console.error('请提供货币对，如 BTC/USD');
          process.exit(1);
        }
        const [cryptoFrom, cryptoTo] = args[1].split('/');
        if (!cryptoFrom || !cryptoTo) {
          console.error('格式错误，请使用 BTC/USD 格式');
          process.exit(1);
        }
        result = await getCrypto(cryptoFrom.toUpperCase(), cryptoTo.toUpperCase());
        break;
        
      default:
        console.error(`未知命令: ${command}`);
        console.error('使用 "node alpha.js help" 查看帮助');
        process.exit(1);
    }
    
    console.log(JSON.stringify(result, null, 2));
    
  } catch (error) {
    if (error.message.includes('demo') || error.message.includes('demo purposes')) {
      console.error('错误: demo API key 已被限制。请申请免费的 API key:');
      console.error('  https://www.alphavantage.co/support/#api-key');
      console.error('');
      console.error('申请后设置: node alpha.js apikey YOUR_API_KEY');
    } else {
      console.error(`错误: ${error.message}`);
    }
    process.exit(1);
  }
}

// 运行主函数
if (require.main === module) {
  main();
}

module.exports = {
  getQuote,
  getTimeSeries,
  getWeekly,
  getMonthly,
  getForex,
  getCrypto,
};