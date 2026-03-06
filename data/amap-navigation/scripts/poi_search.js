#!/usr/bin/env node

/**
 * 高德地图 POI 搜索
 * 支持关键词搜索、附近搜索、类型筛选
 */

const https = require('https');
const { URL } = require('url');

const AMAP_API_KEY = process.env.AMAP_API_KEY || 'demo_key';
const AMAP_BASE_URL = process.env.AMAP_BASE_URL || 'https://restapi.amap.com';

/**
 * POI 类型映射
 */
const POI_TYPES = {
  '餐饮': '050000',
  '酒店': '100000',
  '购物': '060000',
  '加油站': '010300',
  '停车场': '150900',
  '医院': '090100',
  '银行': '160100',
  '超市': '061000'
};

/**
 * POI 搜索
 */
async function searchPOI(options) {
  const {
    keyword,
    location,
    radius = 1000,
    type,
    sort = 'distance',
    limit = 10
  } = options;

  // 地理编码
  let centerLoc = location;
  if (!/^\d+\.\d+,\d+\.\d+$/.test(location)) {
    centerLoc = await geocode(location);
  }

  const url = new URL('/v5/place/around', AMAP_BASE_URL);
  url.searchParams.set('key', AMAP_API_KEY);
  url.searchParams.set('keywords', keyword || '');
  url.searchParams.set('location', centerLoc);
  url.searchParams.set('radius', radius);
  
  if (type && POI_TYPES[type]) {
    url.searchParams.set('types', POI_TYPES[type]);
  }
  
  url.searchParams.set('sortrule', sort === 'rating' ? 'weight' : 'distance');
  url.searchParams.set('page_size', Math.min(limit, 25));

  return new Promise((resolve, reject) => {
    https.get(url.toString(), (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          resolve(formatPOIResult(result));
        } catch (err) {
          reject(err);
        }
      });
    }).on('error', reject);
  });
}

/**
 * 地理编码
 */
async function geocode(address) {
  const url = new URL('/v3/geocode/geo', AMAP_BASE_URL);
  url.searchParams.set('key', AMAP_API_KEY);
  url.searchParams.set('address', address);

  return new Promise((resolve, reject) => {
    https.get(url.toString(), (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          if (result.status === '1' && result.geocodes && result.geocodes.length > 0) {
            resolve(result.geocodes[0].location);
          } else {
            reject(new Error(`地理编码失败: ${address}`));
          }
        } catch (err) {
          reject(err);
        }
      });
    }).on('error', reject);
  });
}

/**
 * 格式化POI结果
 */
function formatPOIResult(apiResult) {
  if (apiResult.status !== '1') {
    return {
      status: 'error',
      code: apiResult.infocode,
      message: 'POI搜索失败'
    };
  }

  const pois = [];
  if (apiResult.pois) {
    apiResult.pois.forEach(poi => {
      pois.push({
        name: poi.name,
        address: poi.address || poi.pname + poi.cityname + poi.adname,
        distance: poi.distance ? `${poi.distance}米` : '未知',
        type: poi.type,
        phone: poi.tel || '无',
        rating: parseFloat(poi.biz_ext?.rating || '0') || '暂无评分',
        location: poi.location
      });
    });
  }

  return {
    status: 'success',
    total: parseInt(apiResult.count) || 0,
    pois
  };
}

/**
 * 命令行接口
 */
async function main() {
  const args = process.argv.slice(2);
  const options = {};
  
  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].replace('--', '');
    const value = args[i + 1];
    options[key] = value;
  }

  if (!options.keyword || !options.location) {
    console.error('用法: node poi_search.js --keyword "关键词" --location "位置" [选项]');
    console.error('选项:');
    console.error('  --radius   搜索半径（米，默认1000）');
    console.error('  --type     POI类型（餐饮|酒店|加油站|停车场）');
    console.error('  --sort     排序方式（distance|rating，默认distance）');
    console.error('  --limit    结果数量（默认10）');
    process.exit(1);
  }

  try {
    const result = await searchPOI({
      keyword: options.keyword,
      location: options.location,
      radius: parseInt(options.radius) || 1000,
      type: options.type,
      sort: options.sort || 'distance',
      limit: parseInt(options.limit) || 10
    });

    console.log(JSON.stringify(result, null, 2));
  } catch (err) {
    console.error('错误:', err.message);
    process.exit(1);
  }
}

module.exports = { searchPOI };

if (require.main === module) {
  main();
}
