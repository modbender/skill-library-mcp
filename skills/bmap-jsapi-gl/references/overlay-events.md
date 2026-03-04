# 覆盖物事件

## 事件监听

```javascript
overlay.addEventListener('eventName', function(e) {
    console.log(e.latLng);
});

overlay.removeEventListener('eventName', handler);
```

## 通用事件

所有覆盖物（Marker、Polyline、Polygon、Circle 等）都支持以下事件：

| 事件 | 触发时机 |
|------|----------|
| click | 鼠标点击覆盖物 |
| dblclick | 鼠标双击覆盖物 |
| rightclick | 鼠标右键点击覆盖物 |
| mouseover | 鼠标移入覆盖物区域 |
| mouseout | 鼠标移出覆盖物区域 |
| mousedown | 鼠标在覆盖物上按下 |
| mouseup | 鼠标在覆盖物上抬起 |
| remove | 覆盖物被移除（调用 removeOverlay） |

```javascript
marker.addEventListener('click', function(e) {
    console.log('点击坐标:', e.latLng.lng, e.latLng.lat);
    console.log('像素坐标:', e.pixel.x, e.pixel.y);
});

polyline.addEventListener('mouseover', function(e) {
    this.setStrokeColor('red');
});

polyline.addEventListener('mouseout', function(e) {
    this.setStrokeColor('blue');
});
```

## Marker 拖拽事件

仅当 `enableDragging: true` 时触发：

| 事件 | 触发时机 |
|------|----------|
| dragstart | 开始拖拽（鼠标按下并开始移动） |
| dragging | 拖拽过程中（持续触发） |
| dragend | 拖拽结束（鼠标释放） |

```javascript
var marker = new BMapGL.Marker(point, { enableDragging: true });

marker.addEventListener('dragstart', function(e) {
    console.log('开始拖拽');
});

marker.addEventListener('dragging', function(e) {
    console.log('拖拽中:', e.latLng.lng, e.latLng.lat);
});

marker.addEventListener('dragend', function(e) {
    console.log('拖拽结束，新位置:', e.latLng.lng, e.latLng.lat);
});
```

## 矢量图形事件

Polyline、Polygon、Circle 等矢量覆盖物支持：

| 事件 | 触发时机 |
|------|----------|
| lineupdate | 图形数据更新（setPath、setCenter、setRadius 等） |

```javascript
polyline.addEventListener('lineupdate', function(e) {
    console.log('路径已更新');
});

circle.addEventListener('lineupdate', function(e) {
    console.log('圆形已更新');
});
```

## 事件对象属性

事件回调函数的参数 `e` 包含以下属性：

| 属性 | 类型 | 说明 |
|------|------|------|
| type | string | 事件类型名称 |
| target | Overlay | 触发事件的覆盖物实例 |
| latLng | Point | 事件发生位置的经纬度坐标（BD09，推荐使用） |
| point | Point | 事件发生位置的内部坐标（墨卡托） |
| pixel | Pixel | 事件发生位置的像素坐标 |

```javascript
marker.addEventListener('click', function(e) {
    console.log('事件类型:', e.type);
    console.log('覆盖物:', e.target);
    console.log('经纬度:', e.latLng.lng, e.latLng.lat);
    console.log('像素:', e.pixel.x, e.pixel.y);
});
```
