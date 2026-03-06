# Polygon 多边形

## 快速开始

```javascript
var points = [
    new BMapGL.Point(116.395, 39.910),
    new BMapGL.Point(116.415, 39.910),
    new BMapGL.Point(116.415, 39.930),
    new BMapGL.Point(116.395, 39.930)
];
var polygon = new BMapGL.Polygon(points, {
    strokeColor: '#3366FF',
    strokeWeight: 2,
    fillColor: '#3366FF',
    fillOpacity: 0.3
});
map.addOverlay(polygon);
```

## 构造函数

```javascript
new BMapGL.Polygon(path, options)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| path | Array\<Point\> \| Array\<Array\<Point\>\> | - | 多边形坐标点数组 (必需) |
| options | Object | - | 配置参数 |

**path 参数说明：**
- 简单多边形：`[Point1, Point2, Point3, ...]`
- 带孔多边形：`[[外环点...], [孔1点...], [孔2点...]]`

### options 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| strokeColor | string | `'#000'` | 边框颜色，支持 '#xxxxxx'、'red'、'rgb(?,?,?)' |
| strokeWeight | number | `2` | 边框宽度，单位像素 |
| strokeOpacity | number | `1` | 边框透明度，取值范围 0-1 |
| strokeStyle | string | `'solid'` | 边框样式：'solid'(实线)、'dashed'(虚线)、'dotted'(点线) |
| dashArray | Array\<number\> | `null` | 虚线样式，如 `[8, 4]` |
| strokeLineCap | string | `'round'` | 线端点形状：'round'(圆形)、'butt'(直角)、'square'(方角) |
| strokeLineJoin | string | `'round'` | 线连接形状：'round'(圆形)、'miter'(尖角)、'bevel'(倒角) |
| fillColor | string | `'#fff'` | 填充颜色 |
| fillOpacity | number | `0.6` | 填充透明度，取值范围 0-1 |
| enableMassClear | boolean | `true` | 调用 map.clearOverlays() 时是否被清除 |
| enableEditing | boolean | `false` | 是否开启可编辑模式 |
| geodesic | boolean | `false` | 是否使用大圆线 |
| zIndex | number | `0` | 层级 |
| enableParse | boolean | `true` | 是否启用点简化（Douglas-Peucker 算法），大数据量时可提升渲染性能 |
| clip | boolean | `true` | 是否启用视口裁剪，仅渲染可视区域内的部分 |
| texture | Canvas\|Image | `null` | 自定义纹理填充，可实现图案、斜线、图片填充等效果 |
| textureSize | Array\<number\> | `null` | 纹理尺寸 `[width, height]`，需配合 texture 使用 |
| textureZoomWithMap | boolean | `false` | 纹理是否随地图缩放变化，false 时图案保持固定比例 |
| textureRepeat | boolean | `true` | 纹理是否重复填充，false 时使用边缘拉伸(CLAMP_TO_EDGE) |

## 方法

### 坐标

```javascript
// 设置多边形坐标
polygon.setPath(path);

// 获取多边形坐标
var path = polygon.getPath();  // 返回 Array<Point> 或 Array<Array<Point>>

// 设置某个顶点的位置（简单多边形）
polygon.setPositionAt(0, new BMapGL.Point(116.388, 39.903));

// 设置某个顶点的位置（带孔多边形）
// setPositionAt(index, point, deep) - deep 指定环索引：0=外环, 1=第一个孔, 2=第二个孔...
polygon.setPositionAt(0, new BMapGL.Point(116.388, 39.903), 0);  // 修改外环第一个点
polygon.setPositionAt(2, new BMapGL.Point(116.405, 39.920), 1);  // 修改第一个孔的第三个点
```

### 边框样式

```javascript
// 颜色
polygon.setStrokeColor('#FF0000');
var color = polygon.getStrokeColor();

// 宽度
polygon.setStrokeWeight(3);
var weight = polygon.getStrokeWeight();

// 透明度
polygon.setStrokeOpacity(0.8);
var opacity = polygon.getStrokeOpacity();

// 线型
polygon.setStrokeStyle('dashed');
var style = polygon.getStrokeStyle();

// 端点形状
polygon.setStrokeLineCap('square');
var cap = polygon.getStrokeLineCap();

// 连接形状
polygon.setStrokeLineJoin('miter');
var join = polygon.getStrokeLineJoin();
```

### 填充样式

```javascript
// 填充颜色
polygon.setFillColor('#00FF00');
var fillColor = polygon.getFillColor();

// 填充透明度
polygon.setFillOpacity(0.5);
var fillOpacity = polygon.getFillOpacity();
```

### 几何信息

```javascript
// 获取多边形的地理范围
var bounds = polygon.getBounds();  // 返回 Bounds

// 获取多边形周长（墨卡托单位）
var length = polygon.getLength();
```

### 编辑

```javascript
polygon.enableEditing();   // 开启编辑模式
polygon.disableEditing();  // 关闭编辑模式
```

### 批量配置

```javascript
polygon.setOptions({
    strokeColor: '#FF6600',
    fillColor: '#FF6600',
    fillOpacity: 0.4
});
```


## 常见场景

### 带孔多边形

绘制中间有空洞的多边形。

```javascript
// 外环（顺时针）
var outer = path1;
// 内环/孔（逆时针）
var hole = path2;

var polygon = new BMapGL.Polygon([outer, hole], {
});

map.addOverlay(polygon);
```

### 可编辑多边形

```javascript
var polygon = new BMapGL.Polygon(points, {
    enableEditing: true
});

map.addOverlay(polygon);
// 监听编辑完成事件
polygon.addEventListener('lineupdate', function(e) {
    console.log('多边形已更新:', e.overlay.getPath());
});
```


### 大数据量优化

处理大量坐标点时，可利用点简化提升性能。

```javascript
// 大量坐标点（如行政区划边界）
var largePathData = [...];  // 数千个坐标点

var polygon = new BMapGL.Polygon(largePathData, {
    enableParse: true,  // 启用点简化（默认开启）
    clip: true          // 启用视口裁剪（默认开启）
});

map.addOverlay(polygon);
```

