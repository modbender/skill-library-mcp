#!/usr/bin/env node

/**
 * 高德地图路线规划
 * 支持驾车、公交、步行、骑行多种出行方式
 */

const https = require('https');
const { URL } = require('url');

// 配置
const AMAP_API_KEY = process.env.AMAP_API_KEY || 'demo_key';
const AMAP_BASE_URL = process.env.AMAP_BASE_URL || 'https://restapi.amap.com';

// 出行方式映射
const MODE_MAP = {
  driving: 'driving',      // 驾车
  transit: 'transit',      // 公交
  walking: 'walking',      // 步行
  bicycling: 'bicycling'   // 骑行
};

// 策略映射
const STRATEGY_MAP = {
  fastest: 0,        // 速度优先
  shortest: 1,       // 距离优先
  'no-highway': 3,   // 不走高速
  'avoid-toll': 4,   // 避开收费站
  'no-highway-no-toll': 5  // 不走高速且避开收费站
};

/**
 * 地理编码：地址转经纬度
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
 * 路线规划
 */
async function planRoute(options) {
  const {
    origin,
    destination,
    mode = 'driving',
    strategy = 'fastest',
    alternatives = 1
  } = options;

  // 如果是地址，先转经纬度
  let originLoc = origin;
  let destLoc = destination;
  
  if (!/^\d+\.\d+,\d+\.\d+$/.test(origin)) {
    originLoc = await geocode(origin);
  }
  if (!/^\d+\.\d+,\d+\.\d+$/.test(destination)) {
    destLoc = await geocode(destination);
  }

  // 构建API请求
  const endpoint = mode === 'transit' 
    ? '/v3/direction/transit/integrated'
    : `/v3/direction/${mode}`;
  
  const url = new URL(endpoint, AMAP_BASE_URL);
  url.searchParams.set('key', AMAP_API_KEY);
  url.searchParams.set('origin', originLoc);
  url.searchParams.set('destination', destLoc);
  
  if (mode === 'driving') {
    url.searchParams.set('strategy', STRATEGY_MAP[strategy] || 0);
    url.searchParams.set('extensions', 'all');
  }

  return new Promise((resolve, reject) => {
    https.get(url.toString(), (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          resolve(formatRouteResult(result, mode));
        } catch (err) {
          reject(err);
        }
      });
    }).on('error', reject);
  });
}

/**
 * 格式化路线结果
 */
function formatRouteResult(apiResult, mode) {
  if (apiResult.status !== '1') {
    return {
      status: 'error',
      code: apiResult.infocode,
      message: '路线规划失败'
    };
  }

  const routes = [];
  
  if (mode === 'driving') {
    const route = apiResult.route;
    if (route && route.paths) {
      route.paths.forEach((path, idx) => {
        routes.push({
          name: `方案${idx + 1}${idx === 0 ? '（推荐）' : ''}`,
          distance: formatDistance(path.distance),
          duration: formatDuration(path.duration),
          traffic: getTrafficLevel(path.traffic_lights),
          toll: path.tolls ? `${path.tolls}元` : '0元',
          strategy: path.strategy || '综合最优',
          steps: path.steps ? path.steps.map(s => s.instruction) : []
        });
      });
    }
  } else if (mode === 'transit') {
    const route = apiResult.route;
    if (route && route.transits) {
      route.transits.forEach((transit, idx) => {
        routes.push({
          name: `方案${idx + 1}`,
          distance: formatDistance(transit.distance),
          duration: formatDuration(transit.duration),
          cost: transit.cost ? `${transit.cost}元` : '未知',
          segments: transit.segments ? transit.segments.length : 0,
          walking_distance: formatDistance(transit.walking_distance)
        });
      });
    }
  } else {
    // 步行/骑行
    const route = apiResult.route;
    if (route && route.paths) {
      const path = route.paths[0];
      routes.push({
        name: `${mode === 'walking' ? '步行' : '骑行'}路线`,
        distance: formatDistance(path.distance),
        duration: formatDuration(path.duration),
        steps: path.steps ? path.steps.map(s => s.instruction) : []
      });
    }
  }

  return {
    status: 'success',
    mode,
    routes,
    recommendation: routes.length > 0 
      ? `建议选择${routes[0].name}，预计${routes[0].duration}到达`
      : '未找到可用路线'
  };
}

/**
 * 格式化距离
 */
function formatDistance(meters) {
  const m = parseFloat(meters);
  if (m >= 1000) {
    return `${(m / 1000).toFixed(1)} km`;
  }
  return `${Math.round(m)} 米`;
}

/**
 * 格式化时长
 */
function formatDuration(seconds) {
  const s = parseInt(seconds);
  const hours = Math.floor(s / 3600);
  const minutes = Math.floor((s % 3600) / 60);
  
  if (hours > 0) {
    return `${hours}小时${minutes}分钟`;
  }
  return `${minutes}分钟`;
}

/**
 * 获取路况等级
 */
function getTrafficLevel(lights) {
  if (!lights) return '畅通';
  const count = parseInt(lights);
  if (count < 5) return '畅通';
  if (count < 10) return '轻微拥堵';
  return '拥堵';
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
    console.error('用法: node navigation.js --from "起点" --to "终点" [选项]');
    console.error('选项:');
    console.error('  --mode      出行方式: driving|transit|walking|bicycling (默认: driving)');
    console.error('  --strategy  路线策略: fastest|shortest|no-highway (默认: fastest)');
    console.error('  --alternatives  方案数量: 1-3 (默认: 1)');
    process.exit(1);
  }

  try {
    const result = await planRoute({
      origin: options.from,
      destination: options.to,
      mode: options.mode || 'driving',
      strategy: options.strategy || 'fastest',
      alternatives: parseInt(options.alternatives) || 1
    });

    console.log(JSON.stringify(result, null, 2));
  } catch (err) {
    console.error('错误:', err.message);
    process.exit(1);
  }
}

// 导出API
module.exports = {
  geocode,
  planRoute
};

// 命令行运行
if (require.main === module) {
  main();
}
