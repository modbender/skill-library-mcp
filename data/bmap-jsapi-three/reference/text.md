# Text 文本

3D 文本标签组件，基于 Canvas 绘制后映射为纹理贴片，用于在地图上显示文字标注。

## 基础用法

```javascript
const text = engine.add(new mapvthree.Text({
    fontSize: 16,
    fillStyle: '#ff0000',
    strokeStyle: '#ffffff',
    lineWidth: 2,
    padding: [4, 4]
}));

const data = mapvthree.GeoJSONDataSource.fromGeoJSON([{
    type: 'Feature',
    geometry: { type: 'Point', coordinates: [116.404, 39.915] },
    properties: { text: '北京市' }
}]);
data.defineAttribute('text', 'text');
text.dataSource = data;
```

## 构造参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `fontSize` | number | `16` | 字号大小（像素） |
| `fontFamily` | string | `'Microsoft Yahei'` | 字体 |
| `fillStyle` | string | `'#ff0'` | 文本填充颜色 |
| `strokeStyle` | string | - | 描边颜色 |
| `lineWidth` | number | - | 描边宽度 |
| `padding` | array | `[2, 2]` | 文本方块内边距 `[x, y]` |
| `keepSize` | boolean | `false` | 是否保持固定屏幕大小 |
| `flat` | boolean | - | 贴地渲染 |
| `opacity` | number | `1` | 透明度 |
| `backgroundColor` | string | - | 背景颜色 |
| `emissive` | string | - | 自发光颜色 |

## 数据属性映射

```javascript
const data = mapvthree.GeoJSONDataSource.fromGeoJSON(geojson);
data.defineAttribute('text', 'label');
data.defineAttribute('fillStyle', (attrs) => {
    if (attrs.type === 'city') return '#ff0000';
    return '#ffffff';
});
text.dataSource = data;
```

支持 `vertexStyles` 模式时，每个数据项可携带独立的 `fontSize`、`fontWeight`、`fillStyle`、`strokeStyle`、`lineWidth` 属性。

## 属性修改

Text 使用 getter/setter 属性代理：

```javascript
text.fontSize = 24;
text.fontFamily = 'Arial';
text.fillStyle = '#ff0000';
text.strokeStyle = '#000000';
text.lineWidth = 3;
text.padding = [6, 6];
text.opacity = 0.8;
```

## 示例：城市标注

```javascript
const cityLabels = engine.add(new mapvthree.Text({
    fontSize: 18,
    fillStyle: '#ffffff',
    strokeStyle: '#000000',
    lineWidth: 2,
    padding: [6, 6],
    keepSize: true
}));

const data = mapvthree.GeoJSONDataSource.fromGeoJSON({
    type: 'FeatureCollection',
    features: [
        {
            type: 'Feature',
            geometry: { type: 'Point', coordinates: [116.404, 39.915] },
            properties: { text: '北京', level: 1 }
        }
    ]
});
data.defineAttribute('text', 'text');
data.defineAttribute('fontSize', (attrs) => attrs.level === 1 ? 20 : 14);
cityLabels.dataSource = data;
```

> 多行文本：使用 `\\` 分隔符换行，如 `'第一行\\第二行'`。

## 资源清理

```javascript
engine.remove(text);
text.dispose();
```
