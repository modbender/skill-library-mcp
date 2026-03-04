# SimplePoint 简单点

基础点渲染组件，用于高效渲染大量点数据。支持颜色、大小、透明度等属性配置。

## 基础用法

```javascript
const point = engine.add(new mapvthree.SimplePoint({
    color: 'rgba(250, 90, 50, 1)',
    size: 50,
    vertexColors: true,
    vertexSizes: true
}));

const data = mapvthree.GeoJSONDataSource.fromGeoJSON([{
    type: 'Feature',
    geometry: { type: 'Point', coordinates: [116.404, 39.915] },
    properties: { color: '#ff0000', size: 30 }
}]);
data.defineAttribute('color', 'color');
data.defineAttribute('size', 'size');
point.dataSource = data;
```

## 构造参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `color` | string/number | `0xffff00` | 点颜色 |
| `size` | number | `30` | 点大小（像素） |
| `opacity` | number | `1` | 透明度（0-1），需配合 `transparent: true` |
| `transparent` | boolean | `false` | 是否启用透明 |
| `vertexColors` | boolean | `false` | 是否通过数据携带颜色 |
| `vertexSizes` | boolean | `false` | 是否通过数据携带大小 |
| `emissive` | string | - | 自发光颜色 |
| `mapSrc` | string | - | 纹理贴图路径 |

## 数据属性映射

通过 `defineAttribute` 映射数据字段：

```javascript
const data = mapvthree.GeoJSONDataSource.fromGeoJSON(geojson);
data.defineAttribute('color', 'color');  // 需 vertexColors: true
data.defineAttribute('size', 'size');    // 需 vertexSizes: true
point.dataSource = data;
```

## 属性修改

SimplePoint 使用属性代理模式，直接赋值即可：

```javascript
point.color = 'rgba(0, 255, 0, 1)';
point.size = 20;
point.opacity = 0.5;
point.vertexColors = true;
```

## 示例：按数据分色

```javascript
const points = engine.add(new mapvthree.SimplePoint({
    size: 12,
    vertexColors: true,
    vertexSizes: true
}));

const features = data.map(item => ({
    type: 'Feature',
    geometry: { type: 'Point', coordinates: item.coords },
    properties: {
        color: item.value > 80 ? [255, 0, 0] : [0, 255, 0],
        size: 5 + item.value / 10
    }
}));

const ds = mapvthree.GeoJSONDataSource.fromGeoJSON({
    type: 'FeatureCollection',
    features
});
ds.defineAttribute('color', 'color');
ds.defineAttribute('size', 'size');
points.dataSource = ds;
```
