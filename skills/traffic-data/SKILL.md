---
name: traffic-data
description: Query traffic data - real-time road conditions, traffic incidents, SCATS intersection data
metadata: {"clawdbot":{"emoji":"🚦","requires":{"bins":["node"],"env":["BAIDU_MAP_KEY","GAODE_MAP_KEY","SCATS_API_KEY"]}}}
---

# Traffic Data Skill

查询交通数据，包括实时路况、交通事件、SCATS路口数据等。

## 环境配置

在 `.env` 文件中添加：

```bash
# 百度地图API（可选）
BAIDU_MAP_KEY=your-baidu-map-api-key

# 高德地图API（可选）
GAODE_MAP_KEY=your-gaode-map-api-key

# SCATS数据API（如果有）
SCATS_API_KEY=your-scats-api-key
```

## 功能

### 1. 实时路况查询
```bash
node skills/traffic-data/road.js <城市> <道路名称>
```

### 2. 交通事件查询
```bash
node skills/traffic-data/incident.js <城市>
```

### 3. SCATS路口数据查询
```bash
node skills/traffic-data/scats.js <路口编号>
```

## 示例

```bash
# 查询广州实时路况
node skills/traffic-data/road.js 广州 广州大道

# 查询广州交通事件
node skills/traffic-data/incident.js 广州

# 查询SCATS路口状态
node skills/traffic-data/scats.js 001
```

## API申请

- 百度地图开放平台：https://lbsyun.baidu.com/
- 高德地图开放平台：https://lbs.amap.com/
