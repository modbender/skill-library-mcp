# Circle 圆形

用于高效绘制大量圆形标记。Circle 是屏幕空间渲染的实例化组件，支持自定义颜色、大小、边框等属性。

## 基础用法

```javascript
const circle = engine.add(new mapvthree.Circle({
    color: '#f4f27a',
    borderWidth: 20,
    borderColor: '#b73145',
    opacity: 0.8,
    vertexSizes: true
}));

const data = mapvthree.GeoJSONDataSource.fromGeoJSON([{
    type: 'Feature',
    geometry: { type: 'Point', coordinates: [116.404, 39.915] },
    properties: { size: 80 }
}]);
data.defineAttribute('size', 'size');
circle.dataSource = data;
```

## 构造参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `color` | string | `'#ff8000'` | 填充颜色 |
| `size` | number | `100` | 圆形大小 |
| `opacity` | number | `1` | 整体透明度（0-1） |
| `type` | string | `'Default'` | 渲染类型：`'Default'` 或 `'Gradient'` |
| `borderWidth` | number | `1` | 边框宽度（keepSize 为 true 时单位为像素，否则为米） |
| `borderColor` | string | `'#00ff00'` | 边框颜色 |
| `borderOpacity` | number | `1` | 边框透明度（0-1） |
| `fillOpacity` | number | `1` | 填充区域透明度（0-1） |
| `vertexColors` | boolean | `false` | 是否通过数据携带颜色 |
| `vertexSizes` | boolean | `false` | 是否通过数据携带大小 |
| `keepSize` | boolean | - | 是否保持屏幕大小 |
| `radius` | number | - | 半径 |
| `transparent` | boolean | - | 是否启用透明 |

## 数据属性映射

```javascript
const data = mapvthree.GeoJSONDataSource.fromGeoJSON(geojson);
data.defineAttribute('color', 'color');  // 需 vertexColors: true
data.defineAttribute('size', 'size');    // 需 vertexSizes: true
circle.dataSource = data;
```

## 属性修改

Circle 使用属性代理模式，直接赋值即可：

```javascript
circle.color = '#ff0000';
circle.size = 200;
circle.opacity = 0.5;
circle.borderWidth = 5;
circle.borderColor = '#0000ff';
```

## 示例：多级预警区域

```javascript
const circles = engine.add(new mapvthree.Circle({
    color: '#ff0000',
    opacity: 0.3,
    borderWidth: 2,
    borderColor: '#ff0000',
    vertexColors: true,
    vertexSizes: true
}));

const data = mapvthree.GeoJSONDataSource.fromGeoJSON({
    type: 'FeatureCollection',
    features: [
        {
            type: 'Feature',
            geometry: { type: 'Point', coordinates: [116.404, 39.915] },
            properties: { color: '#00ff00', size: 200, level: 'safe' }
        },
        {
            type: 'Feature',
            geometry: { type: 'Point', coordinates: [116.410, 39.920] },
            properties: { color: '#ff0000', size: 400, level: 'danger' }
        }
    ]
});
data.defineAttribute('color', 'color');
data.defineAttribute('size', 'size');
circles.dataSource = data;
```
