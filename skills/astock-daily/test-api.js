#!/usr/bin/env node
/**
 * 测试股票 API
 */

const https = require('https');
const http = require('http');

function httpGet(url) {
  return new Promise((resolve, reject) => {
    const client = url.startsWith('https') ? https : http;
    client.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'http://quote.eastmoney.com/',
      }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        console.log('HTTP 状态码:', res.statusCode);
        console.log('响应头:', JSON.stringify(res.headers));
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          resolve(data);
        }
      });
    }).on('error', reject);
  });
}

async function test() {
  // 尝试多个 API
  const apis = [
    // 东方财富 API (HTTPS)
    'https://push2.eastmoney.com/api/qt/clist/get?' +
      'pn=1&pz=10&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&' +
      'fltt=2&invt=2&wbp2u=|0|0|0|web&' +
      'fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&' +
      'fields=f12,f14,f2,f3,f5,f6,f115,f162',
    
    // 新浪财经 API
    'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=1&num=10&sort=symbol&asc=1&node=hs_a&symbol=&_s_r_a=page',
  ];
  
  for (const apiUrl of apis) {
    console.log('\n========================================');
    console.log('请求 URL:', apiUrl.slice(0, 100) + '...');
    
    try {
      const data = await httpGet(apiUrl);
      console.log('返回数据类型:', typeof data);
      if (typeof data === 'string') {
        console.log('返回数据 (前 500 字符):', data.slice(0, 500));
      } else {
        console.log('返回数据:', JSON.stringify(data, null, 2).slice(0, 1000));
      }
    } catch (error) {
      console.error('错误:', error.message);
    }
  }
}

test();
