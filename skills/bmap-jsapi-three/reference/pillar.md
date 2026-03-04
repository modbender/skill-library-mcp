# Pillar 柱体

柱状体组件，支持柱形（pillar）和锥形（cone）两种形状。常用于数据柱状图、建筑物标记等场景。

## 基础用法

```javascript
// 创建柱形
const pillar = engine.add(new mapvthree.Pillar({
    shape: 'pillar',
    color: 0xff0000,
    height: 100,
    radius: 10
}));

// 创建锥形
const cone = engine.add(new mapvthree.Pillar({
    shape: 'cone',
    color: 0x00ff00,
    height: 80,
    radius: 15
}));

const data = mapvthree.GeoJSONDataSource.fromGeoJSON([{
    type: 'Feature',
    geometry: { type: 'Point', coordinates: [116.404, 39.915] },
    properties: {}
}]);
pillar.dataSource = data;
```

## 构造参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `shape` | string | `'pillar'` | 形状类型：`'pillar'`（柱形）或 `'cone'`（锥形） |
| `color` | string/array | `[80, 20, 170, 0.8]` | 颜色 |
| `opacity` | number | `1` | 透明度（0-1） |
| `height` | number | `1` | 柱体高度 |
| `radius` | number | `6` | 柱体半径 |
| `radialSegments` | number | `4` | 径向分段数（影响圆滑度） |
| `heightSegments` | number | `1` | 高度分段数 |
| `openEnded` | boolean | `true` | 是否开放顶底 |
| `vertexHeights` | boolean | `false` | 是否通过数据携带高度 |
| `vertexSizes` | boolean | `false` | 是否通过数据携带大小 |
| `gradient` | object | - | 颜色渐变配置 |
| `colorMode` | string | - | 颜色模式：`'gradient'`（渐变）或 `'band'`（分带） |
| `heatmap` | boolean | `true` | 是否开启热力模式 |

## 数据驱动高度

```javascript
const pillars = engine.add(new mapvthree.Pillar({
    shape: 'pillar',
    radius: 10,
    height: 1,
    color: '#4a90e2',
    vertexHeights: true
}));

const data = mapvthree.GeoJSONDataSource.fromGeoJSON({
    type: 'FeatureCollection',
    features: [
        {
            type: 'Feature',
            geometry: { type: 'Point', coordinates: [116.404, 39.915] },
            properties: { height: 150 }
        },
        {
            type: 'Feature',
            geometry: { type: 'Point', coordinates: [116.405, 39.916] },
            properties: { height: 200 }
        }
    ]
});
data.defineAttribute('height', 'height');
pillars.dataSource = data;
```

## 属性修改

Pillar 使用属性代理模式：

```javascript
pillar.opacity = 0.8;
pillar.height = 200;
```
