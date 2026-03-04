---
name: tencent-map
description: 腾讯地图Web服务API集成，用于地点搜索、路线规划、逆地理编码等功能
author: OpenClaw Community
version: 1.0.0
homepage: https://lbs.qq.com/dev/console/application/
metadata: {"clawdbot":{"emoji":"🗺️","requires":{"bins":["curl","python3"],"env":["TENCENT_MAP_KEY"]},"primaryEnv":"TENCENT_MAP_KEY"}}
---

# 腾讯地图API技能

集成腾讯地图Web服务API，提供地点搜索、路线规划、逆地理编码等功能。

## 设置

1. 在[腾讯位置服务控制台](https://lbs.qq.com/dev/console/application/)申请密钥
2. 设置环境变量：
   ```bash
   export TENCENT_MAP_KEY="YOUR_TENCENT_MAP_KEY"
   ```

## 功能

### 1. 地点搜索 (search)
搜索指定关键词的地点信息

```bash
# 基础搜索
bash {baseDir}/scripts/tencent_map.sh search "花店" "广州"

# 带分页搜索
bash {baseDir}/scripts/tencent_map.sh search "花店" "广州" 1 20

# 指定区域搜索
bash {baseDir}/scripts/tencent_map.sh search "花店" "广州天河区"
```

### 2. 逆地理编码 (reverse_geocode)
根据经纬度获取详细地址信息

```bash
bash {baseDir}/scripts/tencent_map.sh reverse_geocode 23.129405 113.264287
```

### 3. 地理编码 (geocode)
根据地址获取经纬度坐标

```bash
bash {baseDir}/scripts/tencent_map.sh geocode "广州市天河区珠江新城"
```

### 4. 路线规划 (route)
计算两点间的路线信息

```bash
bash {baseDir}/scripts/tencent_map.sh route "起点地址" "终点地址" "driving|walking|transit"
```

### 5. 周边搜索 (around)
搜索指定坐标周围的POI

```bash
bash {baseDir}/scripts/tencent_map.sh around 23.129405 113.264287 "花店" 3000
```

## 参数

- **search**: `keyword`, `region`, `page_index`, `page_size`
- **reverse_geocode**: `latitude`, `longitude`
- **geocode**: `address`
- **route**: `from`, `to`, `mode`
- **around**: `latitude`, `longitude`, `keyword`, `radius`

## 返回格式

所有命令均返回标准化的JSON格式，包含状态、结果和错误信息。

## 限制

- 每日调用次数限制根据腾讯地图API套餐而定
- 搜索结果最多返回20条/页
- 需要有效的腾讯地图API密钥