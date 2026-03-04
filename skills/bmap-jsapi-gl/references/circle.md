# Circle 圆形

## 快速开始

```javascript
var center = new BMapGL.Point(116.404, 39.915);
var circle = new BMapGL.Circle(center, 1000, {
    strokeColor: '#3366FF',
    strokeWeight: 2,
    fillColor: '#3366FF',
    fillOpacity: 0.3
});
map.addOverlay(circle);
```

## 构造函数

```javascript
new BMapGL.Circle(center, radius, options)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| center | Point | - | 圆心坐标 (必需) |
| radius | number | - | 半径，单位：米 (必需) |
| options | Object | - | 配置参数 |

### options 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| strokeColor | string | `'#000'` | 边框颜色，支持 '#xxxxxx'、'red'、'rgb(?,?,?)' |
| strokeWeight | number | `2` | 边框宽度，单位像素 |
| strokeOpacity | number | `1` | 边框透明度，取值范围 0-1 |
| strokeStyle | string | `'solid'` | 边框样式：'solid'(实线)、'dashed'(虚线)、'dotted'(点线) |
| fillColor | string | `'#fff'` | 填充颜色 |
| fillOpacity | number | `0.6` | 填充透明度，取值范围 0-1 |
| enableMassClear | boolean | `true` | 调用 map.clearOverlays() 时是否被清除 |
| enableEditing | boolean | `false` | 是否开启可编辑模式 |
| zIndex | number | `0` | 层级 |

## 方法

### 中心点

```javascript
// 设置圆心
circle.setCenter(new BMapGL.Point(116.410, 39.920));

// 获取圆心
var center = circle.getCenter();  // 返回 Point
```

### 半径

```javascript
// 设置半径（单位：米）
circle.setRadius(2000);

// 获取半径
var radius = circle.getRadius();  // 返回 number
```

### 边框样式

```javascript
// 颜色
circle.setStrokeColor('#FF0000');
var color = circle.getStrokeColor();

// 宽度
circle.setStrokeWeight(3);
var weight = circle.getStrokeWeight();

// 透明度
circle.setStrokeOpacity(0.8);
var opacity = circle.getStrokeOpacity();

// 线型
circle.setStrokeStyle('dashed');
var style = circle.getStrokeStyle();
```

### 填充样式

```javascript
// 填充颜色
circle.setFillColor('#00FF00');
var fillColor = circle.getFillColor();

// 填充透明度
circle.setFillOpacity(0.5);
var fillOpacity = circle.getFillOpacity();
```

### 几何信息

```javascript
// 获取圆形的地理范围（外接矩形）
var bounds = circle.getBounds();  // 返回 Bounds

// 获取近似圆周长（墨卡托单位，非实际距离），返回的是近似圆的多边形边界点连线长度，不是数学圆周长 2πr
var length = circle.getLength();

// 获取近似圆的边界路径点
var path = circle.getPath();  // 返回 Array<Point>，约40个点
```

### 显示隐藏

```javascript
circle.show();   // 显示
circle.hide();   // 隐藏
```

### 编辑

编辑模式下有两个控制点：
- 中心点：拖拽移动圆形
- 圆周点：拖拽改变半径

```javascript
circle.enableEditing();   // 开启编辑模式
circle.disableEditing();  // 关闭编辑模式
```

### 批量配置

```javascript
circle.setOptions({
    strokeColor: '#FF6600',
    fillColor: '#FF6600',
    fillOpacity: 0.4
});
```

## 常见场景

### 可编辑圆形

```javascript
var circle = new BMapGL.Circle(center, 1000, {
    enableEditing: true
});

map.addOverlay(circle);

// 监听编辑完成事件
circle.addEventListener('lineupdate', function(e) {
    var overlay = e.overlay;
    console.log('新圆心:', overlay.getCenter());
    console.log('新半径:', overlay.getRadius(), '米');
});
```

