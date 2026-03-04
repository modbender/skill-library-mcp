# 坐标系说明

## Z-up 坐标系

MapV Three 采用 **Z-up 坐标系**，与 Three.js 默认的 Y-up 不同：

| 轴 | MapV Three (Z-up) | Three.js 默认 (Y-up) |
|----|-------------------|---------------------|
| X  | 东方向 →          | 东方向 →            |
| Y  | 北方向 ↑          | 垂直向上 ↑          |
| Z  | 垂直向上 ↑        | 南方向 ↓            |

## 地理坐标格式

```javascript
// 二维坐标: [经度, 纬度]
[116.404, 39.915]

// 三维坐标: [经度, 纬度, 高度(米)]
[116.404, 39.915, 100]
```

## 投影方式

```javascript
// Web 墨卡托（默认）
projection: 'EPSG:3857'

// 地心固连坐标系（地球级别可视化）
projection: 'ecef'
```

## 坐标转换

```javascript
// 地理坐标 → 投影坐标
const projected = engine.map.projectArrayCoordinate([116.404, 39.915, 0]);
// 返回: [x, y, z] 投影后的三维场景坐标

// 投影坐标 → 地理坐标（反投影）
const geographic = engine.map.unprojectArrayCoordinate([x, y, z]);
// 返回: [lng, lat, alt] 经纬度坐标
```
