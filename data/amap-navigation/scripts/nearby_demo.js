#!/usr/bin/env node
/**
 * 高德地图附近搜索脚本 - 演示版本
 */

// 模拟POI数据
const MOCK_POIS = {
  '上海外滩_咖啡': [
    {
      name: '星巴克(外滩店)',
      type: '咖啡馆',
      distance: 200,
      rating: 4.6,
      reviews: 523,
      hours: '07:00-22:00',
      address: '上海市黄浦区中山东一路18号',
      phone: '021-63393999'
    },
    {
      name: '太平洋咖啡',
      type: '咖啡馆',
      distance: 350,
      rating: 4.5,
      reviews: 312,
      hours: '08:00-21:00',
      address: '上海市黄浦区南京东路299号',
      phone: '021-63232888'
    },
    {
      name: 'Manner Coffee',
      type: '咖啡馆',
      distance: 450,
      rating: 4.7,
      reviews: 891,
      hours: '08:00-20:00',
      address: '上海市黄浦区四川中路123号',
      phone: null
    },
    {
      name: 'Peet\'s Coffee',
      type: '咖啡馆',
      distance: 580,
      rating: 4.4,
      reviews: 267,
      hours: '09:00-21:00',
      address: '上海市黄浦区南京东路168号',
      phone: '021-63217777'
    },
    {
      name: 'COSTA COFFEE',
      type: '咖啡馆',
      distance: 720,
      rating: 4.3,
      reviews: 189,
      hours: '08:00-22:00',
      address: '上海市黄浦区福州路88号',
      phone: '021-63456789'
    }
  ],
  '上海虹桥_加油站': [
    {
      name: '中国石化加油站',
      type: '加油站',
      distance: 800,
      rating: 4.2,
      reviews: 145,
      hours: '24小时',
      address: '上海市闵行区虹桥路1234号',
      phone: '021-64191234',
      services: ['92#', '95#', '98#', '柴油', '便利店']
    },
    {
      name: '中国石油加油站',
      type: '加油站',
      distance: 1200,
      rating: 4.1,
      reviews: 98,
      hours: '24小时',
      address: '上海市长宁区延安西路2000号',
      phone: '021-62339988',
      services: ['92#', '95#', '98#', '充电桩']
    },
    {
      name: '壳牌加油站',
      type: '加油站',
      distance: 1500,
      rating: 4.5,
      reviews: 203,
      hours: '24小时',
      address: '上海市闵行区沪闵路3000号',
      phone: '021-64888888',
      services: ['95#', '98#', 'V-Power', '便利店', '洗车']
    }
  ]
};

/**
 * 解析参数
 */
function parseArgs() {
  const args = process.argv.slice(2);
  const params = {
    location: null,
    keyword: null,
    type: null,
    radius: 1000,
    limit: 10
  };

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--location') params.location = args[++i];
    else if (args[i] === '--keyword') params.keyword = args[++i];
    else if (args[i] === '--type') params.type = args[++i];
    else if (args[i] === '--radius') params.radius = parseInt(args[++i]);
    else if (args[i] === '--limit') params.limit = parseInt(args[++i]);
  }

  if (!params.location || (!params.keyword && !params.type)) {
    console.error('❌ 错误：必须指定 --location 和 (--keyword 或 --type)');
    process.exit(1);
  }

  return params;
}

/**
 * 获取POI数据
 */
function getPOIs(location, keyword) {
  const key = `${location}_${keyword}`;
  return MOCK_POIS[key] || [];
}

/**
 * 格式化距离
 */
function formatDistance(meters) {
  if (meters < 1000) {
    return `${meters}m`;
  }
  return `${(meters / 1000).toFixed(1)}km`;
}

/**
 * 格式化步行时间
 */
function formatWalkTime(meters) {
  const minutes = Math.ceil(meters / 80);  // 按80米/分钟
  return `约${minutes}分钟`;
}

/**
 * 打印POI列表
 */
function printPOIs(pois, params) {
  const radiusKm = params.radius / 1000;
  console.log(`\n📍 附近的${params.keyword || params.type} (${params.location}周边 ${radiusKm}km)\n`);

  if (pois.length === 0) {
    console.log('❌ 未找到相关地点（演示版本仅支持部分查询）');
    console.log('💡 支持查询：');
    console.log('   - 上海外滩 + 咖啡');
    console.log('   - 上海虹桥 + 加油站\n');
    return;
  }

  pois.slice(0, params.limit).forEach((poi, i) => {
    const star = i === 0 ? '⭐ ' : '';
    console.log(`${i + 1}. ${star}${poi.name} - ${formatDistance(poi.distance)}`);
    console.log(`   ├─ 评分：${poi.rating}/5.0 (${poi.reviews}条评价)`);
    console.log(`   ├─ 营业：${poi.hours}`);
    console.log(`   ├─ 地址：${poi.address}`);
    
    if (poi.phone) {
      console.log(`   ├─ 电话：${poi.phone}`);
    }
    
    if (poi.services) {
      console.log(`   └─ 服务：${poi.services.join('、')}`);
    } else {
      console.log(`   └─ 步行：${formatWalkTime(poi.distance)}`);
    }
    
    console.log('');
  });

  // 推荐最近的
  const nearest = pois[0];
  console.log(`💡 步行最近：${nearest.name}，${formatWalkTime(nearest.distance)}`);
  
  // 推荐评分最高的
  const bestRated = pois.reduce((best, current) => 
    current.rating > best.rating ? current : best
  );
  if (bestRated !== nearest) {
    console.log(`💡 评分最高：${bestRated.name}，${bestRated.rating}/5.0`);
  }

  console.log('');
}

/**
 * 主函数
 */
function main() {
  const params = parseArgs();
  const pois = getPOIs(params.location, params.keyword || params.type);
  printPOIs(pois, params);
  
  console.log('📝 注意：这是演示版本，实际数据请使用高德地图APP');
  console.log('🔗 高德地图：https://www.amap.com\n');
}

main();
