# Polyline 折线

## 快速开始

```javascript
var points = [
    new BMapGL.Point(116.399, 39.910),
    new BMapGL.Point(116.405, 39.920),
    new BMapGL.Point(116.420, 39.915)
];
var polyline = new BMapGL.Polyline(points, {
    strokeColor: '#3366FF',
    strokeWeight: 3
});
map.addOverlay(polyline);
```

## 构造函数

```javascript
new BMapGL.Polyline(path, options)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| path | Array\<Point\> | - | 折线坐标点数组 (必需) |
| options | Object | - | 配置参数 |

### options 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| strokeColor | string | `'#000'` | 线颜色，支持 '#xxxxxx'、'red'、'rgb(?,?,?)' |
| strokeWeight | number | `2` | 线宽度，单位像素 |
| strokeOpacity | number | `1` | 线透明度，取值范围 0-1 |
| strokeStyle | string | `'solid'` | 线样式：'solid'(实线)、'dashed'(虚线)、'dotted'(点线) |
| dashArray | Array\<number\> | `null` | 虚线样式，如 `[8, 4]` 表示实线8像素，间隙4像素 |
| strokeLineCap | string | `'round'` | 线端点形状：'round'(圆形)、'butt'(直角)、'square'(方角) |
| strokeLineJoin | string | `'round'` | 线连接形状：'round'(圆形)、'miter'(尖角)、'bevel'(倒角) |
| strokeTexture | Object | - | 线纹理配置，格式：`{url: string, width?: number, height?: number}`，width/height 默认 16 |
| enableMassClear | boolean | `true` | 调用 map.clearOverlays() 时是否被清除 |
| enableEditing | boolean | `false` | 是否开启可编辑模式 |
| enableParse | boolean | `true` | 是否进行抽稀优化，点数较多时建议开启 |
| geodesic | boolean | `false` | 是否使用大圆线（地球曲面最短路径） |
| linkRight | boolean | `false` | 跨 180 度经线时是否走右侧 |
| clip | boolean | `true` | 是否进行视口剪裁优化 |
| mouseOverTolerance | number | `5` | 触发 mouseover 事件的鼠标距离线的像素阈值 |
| texture | string\|HTMLCanvasElement | `null` | 填充纹理，可以是图片 URL 或 Canvas 元素 |
| textureSize | Array\<number\> | `null` | 纹理尺寸，格式：`[width, height]` |
| textureZoomWithMap | boolean | `false` | 纹理是否随地图缩放而变化 |
| textureRepeat | boolean | `true` | 纹理是否重复填充 |
| getParseTolerance | function | `null` | 自定义抽稀因子函数，参数为 (zoom, coordType) |
| getParseCacheIndex | function | `null` | 自定义抽稀缓存索引函数，参数为 (zoom) |
| zIndex | number | `0` | 层级 |

## 方法

### 坐标

```javascript
// 设置折线坐标
polyline.setPath([
    new BMapGL.Point(116.399, 39.910),
    new BMapGL.Point(116.420, 39.920)
]);

// 获取折线坐标
var path = polyline.getPath();  // 返回 Array<Point>

// 设置某个点的位置
polyline.setPositionAt(1, new BMapGL.Point(116.410, 39.918));
```

### 线条样式

```javascript
// 颜色
polyline.setStrokeColor('#FF0000');
var color = polyline.getStrokeColor();

// 宽度
polyline.setStrokeWeight(5);
var weight = polyline.getStrokeWeight();

// 透明度
polyline.setStrokeOpacity(0.8);
var opacity = polyline.getStrokeOpacity();

// 线型
polyline.setStrokeStyle('dashed');
var style = polyline.getStrokeStyle();

// 端点形状
polyline.setStrokeLineCap('square');
var cap = polyline.getStrokeLineCap();

// 连接形状
polyline.setStrokeLineJoin('miter');
var join = polyline.getStrokeLineJoin();
```

### 几何信息

```javascript
// 获取折线的地理范围
var bounds = polyline.getBounds();  // 返回 Bounds

// 获取折线长度 （墨卡托单位）
var length = polyline.getLength();
```

### 编辑

```javascript
polyline.enableEditing();   // 开启编辑模式
polyline.disableEditing();  // 关闭编辑模式
```

### 批量配置

```javascript
polyline.setOptions({
    strokeColor: '#00FF00',
    strokeWeight: 4,
    strokeOpacity: 0.9
});
```

## 常见场景

### 虚线样式

```javascript
var polyline = new BMapGL.Polyline(points, {
    strokeStyle: 'dashed',
    dashArray: [10, 5]  // 实线10像素，间隙5像素
});

map.addOverlay(polyline);
```

### 可编辑折线

```javascript
var polyline = new BMapGL.Polyline(points, {
    enableEditing: true
});

map.addOverlay(polyline);

// 监听编辑完成事件
polyline.addEventListener('lineupdate', function(e) {
    console.log('折线已更新:', e.overlay.getPath());
});
```

