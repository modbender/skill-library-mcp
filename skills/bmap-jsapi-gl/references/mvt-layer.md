# MVTLayer 矢量瓦片图层

加载 MVT/PBF 格式的矢量瓦片，支持样式表达式、特征交互、状态管理。

## 快速开始

```javascript
var mvtLayer = new BMapGL.MVTLayer({
    gridModel: BMapGL.MVTLayer.GridModel.GOOGLEWEB,
    tileUrlTemplate: 'http://server/tiles/[z]/[x]/[y].pbf',
    transform: { source: 'GCJ02' },
    idProperty: 'adcode',
    style: {
        'boundary': {
            type: 'polygon',
            painter: {
                fillColor: '#ff8b1a',
                fillOpacity: 0.6,
                strokeColor: '#0000ff',
                strokeWeight: 2
            }
        }
    }
});
map.addTileLayer(mvtLayer);
```

## 构造函数

```javascript
new BMapGL.MVTLayer(options)
```

### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| tileUrlTemplate | string | - | 瓦片 URL 模板，支持 `[x]`、`[y]`、`[z]` 占位符 |
| layers | Array\<string\> | - | 需要加载的图层名称数组，不指定则加载全部 |
| idProperty | string | - | 要素唯一标识属性名，状态管理依赖此属性 |
| style | Object | - | 图层样式配置对象 |
| minZoom | number | 3 | 最小缩放级别 |
| maxZoom | number | 23 | 最大缩放级别 |
| gridModel | number | 0 | 瓦片网格模型：0=百度网格，1=谷歌网格 |
| transform | Object | - | 坐标转换：`source` 源坐标系（GCJ02/EPSG3857/WGS84），`target` 目标坐标系（默认 BD09MC） |
| extent | Array | - | 显示范围 [minX, minY, maxX, maxY] |
| extentCRSIsWGS84 | boolean | false | extent 是否为 WGS84 坐标 |

## 样式配置

### 结构

```javascript
style: {
    '图层名称': {
        type: 'point' | 'polyline' | 'polygon',
        visible: true,
        minZoom: 9,
        maxZoom: 16,
        painter: { /* 样式属性 */ }
    }
}
```

## 方法

```javascript
// 样式
mvtLayer.setStyle(styleObject);

// 层级
mvtLayer.setZIndex(10);
mvtLayer.setZIndexTop();

// 特征选择
var features = mvtLayer.pickFeatures(point, pixel);
var result = mvtLayer.intersectFeatures(polygon.toGeoJSON());

// 状态管理（状态名自定义，需与样式表达式中的 feature-state 对应）
mvtLayer.updateState(features, { hover: true }, false);   // 悬停高亮
mvtLayer.updateState(features, { picked: true }, false);  // 点击选中
mvtLayer.clearState();
```

## 事件

| 事件 | 说明 | 回调参数 |
|------|------|----------|
| onclick | 点击 | e.value(Entity数组), e.point, e.pixel |
| onmousemove | 鼠标移动 | 同上 |
| onmouseout | 鼠标移出 | 同上 |
| ontilesloadend | 瓦片加载完成 | - |

```javascript
mvtLayer.addEventListener('onclick', function(e) {
    console.log('点击要素:', e.value);
});
```

## 常见场景

### 交互高亮

```javascript

mvtLayer.addEventListener('onmousemove', function(e) {
    mvtLayer.clearState();
    if (e.value && e.value.length > 0) {
        mvtLayer.updateState(e.value, { hover: true }, false);
    }
});

mvtLayer.addEventListener('onmouseout', function(e) {
    mvtLayer.clearState();
});
```

## 注意事项

1. MVT 瓦片通常使用谷歌网格，需设置 `gridModel: BMapGL.MVTLayer.GridModel.GOOGLEWEB`
2. 加载高德等瓦片需配置 `transform: { source: 'GCJ02' }`
3. 状态管理依赖 `idProperty`，需指定要素唯一标识属性
4. 移除图层使用 `map.removeTileLayer(mvtLayer)`
