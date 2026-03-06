# Heatmap 热力图使用指南

## 概述

Heatmap 将大量点数据以热力形式可视化，通过颜色渐变展示数据密度分布。支持 2D（Heatmap）和 3D（Heatmap3D）模式。

## 基础用法

```javascript
const heatmap = engine.add(new mapvthree.Heatmap({
    radius: 100,
    opacity: 0.8,
    gradient: {
        0: 'rgba(0,0,255,1)',
        0.3: 'rgba(0,255,0,1)',
        0.6: 'rgba(255,255,0,1)',
        1: 'rgba(255,0,0,1)'
    }
}));

heatmap.dataSource = mapvthree.GeoJSONDataSource.fromGeoJSON({
    type: 'FeatureCollection',
    features: [
        {
            type: 'Feature',
            geometry: { type: 'Point', coordinates: [116.404, 39.915] },
            properties: { value: 100 }
        }
    ]
});
```

## Heatmap 构造参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `gradient` | object | `{0:'rgba(0,0,255,1)', 0.3:'rgba(0,255,0,1)', 0.6:'rgba(255,255,0,1)', 1:'rgba(255,0,0,1)'}` | 颜色梯度映射 |
| `opacity` | number | `1` | 透明度 (0-1) |
| `minValue` | number | `0` | 最小值映射 |
| `maxValue` | number | `1` | 最大值映射 |
| `radius` | number | `100` | 影响半径 |
| `keepSize` | boolean | `false` | 是否保持像素大小（true 为像素单位，false 为米单位） |
| `attenuateMValueFactor` | number | `0` | 径向渐变衰减速度因子 |

## Heatmap3D 构造参数

Heatmap3D 继承 Heatmap 的所有参数，额外支持：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `height` | number | `50` | 拉伸高度（米） |
| `segments` | number | `16` | 柱体分段数 |

## 数据格式

```javascript
// 标准 GeoJSON
{
    type: 'FeatureCollection',
    features: [{
        type: 'Feature',
        geometry: { type: 'Point', coordinates: [116.404, 39.915] },
        properties: { value: 100 }
    }]
}
```

## 示例：人口密度热力图

```javascript
const heatmap = engine.add(new mapvthree.Heatmap({
    radius: 80,
    opacity: 0.8,
    maxValue: 100,
    gradient: {
        0: '#2c3e50',
        0.3: '#3498db',
        0.5: '#2ecc71',
        0.7: '#f1c40f',
        1: '#e74c3c'
    }
}));

heatmap.dataSource = mapvthree.GeoJSONDataSource.fromGeoJSON({
    type: 'FeatureCollection',
    features: generatePopulationData()
});
```

## 示例：3D 热力图

```javascript
const heatmap3d = engine.add(new mapvthree.Heatmap3D({
    radius: 50,
    height: 200,
    opacity: 0.8,
    segments: 8,
    gradient: {
        0: '#0088fe',
        0.5: '#00c6fb',
        1: '#ff0080'
    }
}));

heatmap3d.dataSource = await mapvthree.GeoJSONDataSource.fromURL('buildings.geojson');
```
