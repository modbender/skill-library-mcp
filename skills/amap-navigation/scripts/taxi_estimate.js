#!/usr/bin/env node

/**
 * 打车费用估算
 * 模拟高德、滴滴等平台的价格估算
 */

const https = require('https');
const { URL } = require('url');

const AMAP_API_KEY = process.env.AMAP_API_KEY || 'demo_key';
const AMAP_BASE_URL = process.env.AMAP_BASE_URL || 'https://restapi.amap.com';

/**
 * 计算两点距离
 */
async function calculateDistance(origin, destination) {
  // 地理编码
  let originLoc = origin;
  let destLoc = destination;
  
  if (!/^\d+\.\d+,\d+\.\d+$/.test(origin)) {
    originLoc = await geocode(origin);
  }
  if (!/^\d+\.\d+,\d+\.\d+$/.test(destination)) {
    destLoc = await geocode(destination);
  }

  const url = new URL('/v3/direction/driving', AMAP_BASE_URL);
  url.searchParams.set('key', AMAP_API_KEY);
  url.searchParams.set('origin', originLoc);
  url.searchParams.set('destination', destLoc);

  return new Promise((resolve, reject) => {
    https.get(url.toString(), (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          if (result.status === '1' && result.route && result.route.paths) {
            const path = result.route.paths[0];
            resolve({
              distance: parseFloat(path.distance),
              duration: parseFloat(path.duration)
            });
          } else {
            reject(new Error('距离计算失败'));
          }
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
 * 估算打车费用
 */
function estimateFare(distance, duration, platform = 'gaode', carpool = false) {
  const km = distance / 1000;
  const minutes = duration / 60;

  // 基础定价模型（仅供参考）
  const pricing = {
    gaode: {
      base: 13,           // 起步价（3公里）
      perKm: 2.6,         // 超出后每公里
      perMin: 0.6,        // 每分钟时长费
      minFee: 0           // 最低消费
    },
    didi: {
      base: 14,
      perKm: 2.9,
      perMin: 0.8,
      minFee: 0
    },
    kuaiche: {
      base: 10,
      perKm: 1.8,
      perMin: 0.4,
      minFee: 0
    },
    zhuanche: {
      base: 18,
      perKm: 3.6,
      perMin: 1.0,
      minFee: 0
    }
  };

  const config = pricing[platform] || pricing.gaode;
  
  let fare = config.base;
  if (km > 3) {
    fare += (km - 3) * config.perKm;
  }
  fare += (minutes * config.perMin);
  
  // 拼车折扣
  if (carpool) {
    fare *= 0.7;
  }

  // 价格区间（±15%）
  const minFare = Math.max(fare * 0.85, config.minFee);
  const maxFare = fare * 1.15;

  return {
    platform: getPlatformName(platform),
    service: carpool ? '拼车' : '快车',
    price: `¥${Math.round(minFare)}-${Math.round(maxFare)}`,
    duration: `${Math.round(minutes)}分钟`,
    distance: `${km.toFixed(1)} km`
  };
}

/**
 * 获取平台名称
 */
function getPlatformName(code) {
  const names = {
    gaode: '高德打车',
    didi: '滴滴出行',
    kuaiche: '快车',
    zhuanche: '专车'
  };
  return names[code] || code;
}

/**
 * 打车估价主函数
 */
async function estimateTaxi(options) {
  const {
    from,
    to,
    platforms = 'gaode',
    carpool = false
  } = options;

  try {
    // 计算距离和时长
    const { distance, duration } = await calculateDistance(from, to);

    // 多平台估价
    const platformList = platforms.split(',');
    const estimates = platformList.map(p => 
      estimateFare(distance, duration, p.trim(), carpool)
    );

    // 找最便宜的
    const cheapest = estimates.reduce((min, curr) => {
      const minPrice = parseFloat(min.price.match(/\d+/)[0]);
      const currPrice = parseFloat(curr.price.match(/\d+/)[0]);
      return currPrice < minPrice ? curr : min;
    });

    return {
      status: 'success',
      estimates,
      recommendation: `推荐使用${cheapest.platform}${cheapest.service}，价格最优`
    };
  } catch (err) {
    return {
      status: 'error',
      message: err.message
    };
  }
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

  if (!options.from || !options.to) {
    console.error('用法: node taxi_estimate.js --from "起点" --to "终点" [选项]');
    console.error('选项:');
    console.error('  --platforms  平台列表，逗号分隔（gaode,didi,kuaiche,zhuanche）');
    console.error('  --carpool    是否拼车（true/false，默认false）');
    process.exit(1);
  }

  try {
    const result = await estimateTaxi({
      from: options.from,
      to: options.to,
      platforms: options.platforms || 'gaode,didi',
      carpool: options.carpool === 'true'
    });

    console.log(JSON.stringify(result, null, 2));
  } catch (err) {
    console.error('错误:', err.message);
    process.exit(1);
  }
}

module.exports = { estimateTaxi };

if (require.main === module) {
  main();
}
