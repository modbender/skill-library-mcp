---
name: amap-navigation - 高德地图导航与出行助手
description: 高德地图导航与出行助手。支持路线规划、实时路况、打车估价、POI搜索、距离计算。
---

# amap-navigation - 高德地图导航与出行助手

**版本**: v1.0.0  
**作者**: 玉斧 (wangyuqin2@xiaohongshu.com)  
**类别**: 出行导航  
**区域**: 中国

## 概述

高德地图导航与出行助手。支持路线规划、实时路况、打车估价、POI搜索、距离计算。

## 核心能力

### 1. 多种出行方式对比
- 🚗 驾车导航（实时路况、拥堵预警）
- 🚌 公交路线（最少换乘、最少步行、最快到达）
- 🚶 步行导航
- 🚴 骑行路线
- 🚕 打车估价（滴滴/高德/快车/专车）

### 2. 路线规划
- 智能推荐最优路线
- 多方案对比（时间最短、距离最短、不走高速）
- 实时路况信息
- 红绿灯数量
- 收费站信息

### 3. POI搜索
- 附近美食、酒店、加油站、停车场
- 关键词搜索
- 按距离/评分排序
- 营业时间、价格区间

### 4. 打车估价
- 支持平台：滴滴、高德、快车、专车
- 预估价格、预计时间
- 拼车/独享对比
- 优惠券提示

## 触发场景

当用户询问以下内容时激活：
- "怎么去XX"
- "从A到B路线"
- "导航到XX"
- "打车到XX多少钱"
- "附近有什么XX"
- "最快路线"
- "实时路况"

## 使用方法

### 命令行

#### 路线规划
```bash
# 基础用法
node scripts/navigation.js \
  --from "浙江省杭州市西湖区" \
  --to "浙江省杭州市滨江区阿里巴巴西溪园区" \
  --mode driving

# 公交路线
node scripts/navigation.js \
  --from "北京站" \
  --to "首都机场" \
  --mode transit \
  --prefer "least-time"

# 多方案对比
node scripts/navigation.js \
  --from "上海虹桥火车站" \
  --to "上海浦东机场" \
  --mode driving \
  --alternatives 3
```

#### POI搜索
```bash
# 搜索附近餐厅
node scripts/poi_search.js \
  --keyword "川菜" \
  --location "北京市朝阳区三里屯" \
  --radius 1000

# 搜索加油站
node scripts/poi_search.js \
  --type "加油站" \
  --location "上海市浦东新区陆家嘴" \
  --sort distance
```

#### 打车估价
```bash
# 估算打车费用
node scripts/taxi_estimate.js \
  --from "杭州东站" \
  --to "西湖风景区" \
  --platforms "didi,gaode"
```

### JavaScript API

```javascript
const AMapNavigation = require('./scripts/navigation.js');

// 路线规划
const route = await AMapNavigation.planRoute({
  origin: '116.481028,39.989643',  // 经纬度或地址
  destination: '116.434446,39.90816',
  mode: 'driving',  // driving, transit, walking, bicycling
  strategy: 'fastest'  // fastest, shortest, no-highway
});

// POI搜索
const pois = await AMapNavigation.searchPOI({
  keyword: '星巴克',
  location: '上海市静安区',
  radius: 2000,
  limit: 10
});

// 打车估价
const estimate = await AMapNavigation.estimateTaxi({
  from: '北京南站',
  to: '天安门广场',
  platforms: ['didi', 'gaode']
});
```

## 参数说明

### navigation.js

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `--from` | ✅ | - | 出发地（地址或经纬度） |
| `--to` | ✅ | - | 目的地（地址或经纬度） |
| `--mode` | ❌ | driving | 出行方式：driving/transit/walking/bicycling |
| `--strategy` | ❌ | fastest | 路线偏好：fastest/shortest/no-highway |
| `--alternatives` | ❌ | 1 | 方案数量（1-3） |
| `--avoid` | ❌ | - | 避开拥堵/高速/收费站 |

### poi_search.js

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `--keyword` | ✅ | - | 搜索关键词 |
| `--location` | ✅ | - | 搜索中心点 |
| `--radius` | ❌ | 1000 | 搜索半径（米） |
| `--type` | ❌ | - | POI类型（餐饮/酒店/加油站） |
| `--sort` | ❌ | distance | 排序方式：distance/rating |
| `--limit` | ❌ | 10 | 结果数量 |

### taxi_estimate.js

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `--from` | ✅ | - | 出发地 |
| `--to` | ✅ | - | 目的地 |
| `--platforms` | ❌ | gaode | 平台：gaode/didi/kuaiche/zhuanche |
| `--carpool` | ❌ | false | 是否拼车 |

## 输出格式

### 路线规划
```json
{
  "status": "success",
  "mode": "driving",
  "routes": [
    {
      "name": "方案1（推荐）",
      "distance": "15.2 km",
      "duration": "28分钟",
      "traffic": "畅通",
      "toll": "0元",
      "strategy": "时间最短",
      "steps": [
        "从起点出发，沿XX路向北行驶500米",
        "右转进入XX路，行驶2.3公里"
      ]
    }
  ],
  "recommendation": "建议选择方案1，预计28分钟到达，当前路况畅通"
}
```

### POI搜索
```json
{
  "status": "success",
  "total": 15,
  "pois": [
    {
      "name": "星巴克（静安店）",
      "address": "上海市静安区XX路123号",
      "distance": "350米",
      "rating": 4.5,
      "phone": "021-12345678",
      "hours": "08:00-22:00",
      "price": "¥30-50/人"
    }
  ]
}
```

### 打车估价
```json
{
  "status": "success",
  "estimates": [
    {
      "platform": "高德打车",
      "service": "快车",
      "price": "¥25-30",
      "duration": "18分钟",
      "distance": "8.5 km"
    },
    {
      "platform": "滴滴出行",
      "service": "快车",
      "price": "¥28-33",
      "duration": "20分钟",
      "distance": "8.5 km"
    }
  ],
  "recommendation": "推荐使用高德打车快车，价格最优"
}
```

## 配置要求

### 环境变量

在工作区根目录 `.env` 文件中配置：

```bash
# 高德地图 API Key（必需）
AMAP_API_KEY=your_api_key_here

# 可选配置
AMAP_API_SECRET=your_secret_here  # 部分API需要
AMAP_BASE_URL=https://restapi.amap.com  # 默认值
```

### 获取 API Key

1. 访问 [高德开放平台](https://lbs.amap.com/)
2. 注册/登录账号
3. 进入"应用管理" → "我的应用"
4. 创建应用，选择"Web服务"
5. 复制 API Key 到 `.env` 文件

**免费额度：**
- 每日调用量：30万次
- QPS限制：3000次/秒
- 个人开发者可申请更高额度

## 错误处理

```javascript
// 地址解析失败
{
  "status": "error",
  "code": "GEOCODE_FAILED",
  "message": "无法解析地址：XX路XX号"
}

// API Key 无效
{
  "status": "error",
  "code": "INVALID_API_KEY",
  "message": "请在 .env 文件中配置有效的 AMAP_API_KEY"
}

// 无可用路线
{
  "status": "error",
  "code": "NO_ROUTE",
  "message": "未找到从A到B的可行路线"
}
```

## 实际应用场景

### 场景1：智能通勤助手
```bash
# 用户："从家到公司最快路线"
node scripts/navigation.js \
  --from "北京市朝阳区XX小区" \
  --to "北京市海淀区中关村软件园" \
  --mode driving \
  --strategy fastest \
  --alternatives 3

# 输出：
# - 方案1：三环-四环路线，28分钟，轻微拥堵
# - 方案2：走五环绕行，35分钟，畅通
# - 建议：选择方案1，虽有拥堵但仍最快
```

### 场景2：附近美食推荐
```bash
# 用户："附近有什么好吃的川菜馆"
node scripts/poi_search.js \
  --keyword "川菜" \
  --location "当前位置" \
  --radius 2000 \
  --sort rating \
  --limit 5

# 输出：
# 1. 巴蜀风味（4.8星，500米）
# 2. 蜀香阁（4.6星，800米）
# 3. 川渝人家（4.5星，1.2公里）
```

### 场景3：打车价格对比
```bash
# 用户："从机场到酒店打车多少钱"
node scripts/taxi_estimate.js \
  --from "首都机场T3航站楼" \
  --to "北京朝阳区XX酒店" \
  --platforms "didi,gaode"

# 输出：
# 高德打车：¥85-95，50分钟
# 滴滴出行：¥88-98，52分钟
# 建议：高德打车略便宜，预计50分钟到达
```

## 技术实现

### 核心依赖
- Node.js 内置 `https` 模块（API调用）
- 高德地图 Web服务 API v7.0

### API端点
- 路线规划：`/v5/direction/{mode}`
- 地理编码：`/v3/geocode/geo`
- POI搜索：`/v5/place/text`
- 距离计算：`/v5/direction/distance`

## 注意事项

1. **API Key 安全**
   - 不要在代码中硬编码 API Key
   - 使用环境变量或配置文件
   - 定期更换 Key

2. **调用频率**
   - 注意 QPS 限制
   - 使用缓存减少重复调用
   - 批量请求时添加延迟

3. **坐标系统**
   - 高德使用 GCJ-02（火星坐标系）
   - GPS坐标需转换

4. **隐私保护**
   - 不记录用户位置历史
   - 敏感地址脱敏处理

## 输出物

路线方案 + 时间距离 + 实时路况 + 出行建议

## 下一步

- [ ] 集成实时路况拥堵指数
- [ ] 支持途经点规划
- [ ] 添加停车场推荐
- [ ] 地铁路线优化

## 许可证

MIT License

---

**ClawHub 生态贡献**  
填补中国本土化出行服务空白
