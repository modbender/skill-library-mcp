# EffectPoint 特效点

用于创建带动画效果的点标记，支持扇形雷达、气泡、波纹、呼吸、雷达扫描等特效类型。

> 注意：动画效果需要在引擎初始化时设置 `rendering.enableAnimationLoop = true`。

## 基础用法

```javascript
// 创建扇形雷达特效
const effectPoint = engine.add(new mapvthree.EffectPoint({
    type: 'Fan',
    color: 0xff0000,
    size: 50
}));

// 设置数据源
const data = mapvthree.GeoJSONDataSource.fromGeoJSON([{
    type: 'Feature',
    geometry: { type: 'Point', coordinates: [116.404, 39.915] },
    properties: {}
}]);
effectPoint.dataSource = data;
```

## 构造参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `type` | string | - | 特效类型，见下表 |
| `color` | string/number | - | 颜色，支持十六进制数值或颜色字符串 |
| `size` | number | - | 尺寸 |
| `duration` | number | - | 动画间隔时长 |
| `keepSize` | boolean | - | 是否保持屏幕大小 |
| `vertexColors` | boolean | `false` | 是否通过数据携带颜色 |
| `vertexSizes` | boolean | `false` | 是否通过数据携带尺寸 |
| `segmentAngle` | number | - | 雷达扇形弧度值，仅 `type: 'Radar'` 时有效 |
| `sideColor` | string | - | 最外圈底色，仅 `type: 'RadarLayered'` 时有效 |
| `opacity` | number | `1` | 透明度 |

### 特效类型 (type)

| 类型 | 说明 |
|------|------|
| `'Fan'` | 扇形雷达 |
| `'Bubble'` | 气泡上浮 |
| `'Wave'` | 水波纹扩散 |
| `'Breath'` | 呼吸缩放 |
| `'Radar'` | 雷达扫描（可配合 `segmentAngle`） |
| `'RadarLayered'` | 分层雷达（可配合 `sideColor`） |
| `'RadarSpread'` | 雷达扩散 |

## 示例：批量特效点

```javascript
const effectLayer = engine.add(new mapvthree.EffectPoint({
    type: 'Wave',
    color: 0x00ffff,
    size: 40,
    vertexColors: true,
    vertexSizes: true
}));

const data = mapvthree.GeoJSONDataSource.fromGeoJSON([
    {
        type: 'Feature',
        geometry: { type: 'Point', coordinates: [116.404, 39.915] },
        properties: { color: '#ff0000', size: 60 }
    },
    {
        type: 'Feature',
        geometry: { type: 'Point', coordinates: [116.410, 39.920] },
        properties: { color: '#00ff00', size: 40 }
    }
]);
data.defineAttribute('color', 'color');
data.defineAttribute('size', 'size');
effectLayer.dataSource = data;
```

## 示例：雷达扫描

```javascript
const radar = engine.add(new mapvthree.EffectPoint({
    type: 'Radar',
    color: 0x00ff00,
    size: 80,
    segmentAngle: Math.PI / 3  // 60度扇形
}));

radar.dataSource = mapvthree.GeoJSONDataSource.fromGeoJSON([{
    type: 'Feature',
    geometry: { type: 'Point', coordinates: [116.404, 39.915] },
    properties: {}
}]);
```

## 属性修改

EffectPoint 使用属性代理模式，直接赋值即可修改：

```javascript
effectPoint.color = 0xff00ff;
effectPoint.size = 100;
effectPoint.opacity = 0.5;
```
