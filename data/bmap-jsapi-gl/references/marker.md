# Marker 点标记

## 快速开始

```javascript
var point = new BMapGL.Point(116.404, 39.915);
var marker = new BMapGL.Marker(point);
map.addOverlay(marker);
```

## 构造函数

```javascript
new BMapGL.Marker(position, options)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| position | Point | - | 标注坐标 (必需) |
| options | Object | - | 配置参数 |

### options 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| icon | Icon | 红色图标 | 标注图标，详见 base-classes.md |
| offset | Size | `new Size(0, 0)` | 像素偏移。width 正值向右/负值向左，height 正值向下/负值向上 |
| label | Label | - | 文本标注，显示在标注旁边 |
| title | string | `''` | 鼠标悬停时显示的提示文字 |
| clickable | boolean | `true` | 是否响应点击事件 |
| enableDragging | boolean | `false` | 是否允许用户拖拽移动标注 |
| raiseOnDrag | boolean | `false` | 拖拽时标注是否有抬起动画效果 |
| enableMassClear | boolean | `true` | 调用 map.clearOverlays() 时是否被清除 |
| isTop | boolean | `false` | 是否置顶显示，置顶后会覆盖其他标注 |
| rotation | number | `0` | 顺时针旋转角度，0 为正北方向 |
| zIndex | number | 按纬度 | 层级，默认纬度低的覆盖纬度高的 |
| baseZIndex | number | `0` | 基准层级增量，在默认层级基础上增加 |

## 方法

### 位置

```javascript
marker.setPoint(new BMapGL.Point(116.404, 39.915));
var pos = marker.getPoint();  // 返回 Point
```

### 图标

```javascript
var icon = new BMapGL.Icon('marker.png', new BMapGL.Size(24, 24));
marker.setIcon(icon);
var currentIcon = marker.getIcon();  // 返回 Icon
```

### 标题

```javascript
marker.setTitle('这是标题');
var title = marker.getTitle();
```

### 偏移

相对于标注坐标点的像素偏移。

- width: 正值向右，负值向左
- height: 正值向下，负值向上

```javascript
marker.setOffset(new BMapGL.Size(10, -5));  // 右移10px，上移5px
var offset = marker.getOffset();  // 返回 Size
```

### 旋转

以正北方向为 0 度，顺时针旋转。

```javascript
marker.setRotation(45);   // 顺时针旋转 45 度（东北方向）
marker.setRotation(90);   // 正东方向
marker.setRotation(180);  // 正南方向
var angle = marker.getRotation();
```

### 置顶

将标注显示在其他标注之上，用于高亮或强调某个标注。

```javascript
marker.setTop(true);   // 置顶，显示在最上层
marker.setTop(false);  // 取消置顶，恢复按纬度排序
```

### 拖拽

启用后用户可拖拽移动标注位置。

```javascript
marker.enableDragging();   // 启用拖拽
marker.disableDragging();  // 禁用拖拽
```

### 动画

```javascript
marker.setAnimation(BMAP_ANIMATION_BOUNCE);  // 跳动
marker.setAnimation(BMAP_ANIMATION_DROP);    // 掉落
marker.setAnimation(null);                   // 取消动画
```

## 常见场景

### 自定义图标标记

```javascript
var icon = new BMapGL.Icon(
    'custom-marker.png',
    new BMapGL.Size(32, 32),
    { anchor: new BMapGL.Size(16, 32) }
);

var marker = new BMapGL.Marker(point, { icon: icon });
map.addOverlay(marker);
```

### 可拖拽标记

```javascript
var marker = new BMapGL.Marker(point, {
    enableDragging: true,
});

map.addOverlay(marker);
```

### 带文本标签的标记

```javascript
var marker = new BMapGL.Marker(point);
var label = new BMapGL.Label('标签文字', {
    offset: new BMapGL.Size(20, -10)
});
marker.setLabel(label);
map.addOverlay(marker);
```
