# DOMOverlay DOM 覆盖物

## 概述

DOMOverlay 将 HTML 元素与地理坐标绑定，支持拖拽和交互事件。是 Marker 和 Popup 的基类。

## 基础用法

```javascript
const overlay = engine.add(new mapvthree.DOMOverlay({
    dom: document.getElementById('popup'),
    point: [116.404, 39.915, 100],
    offset: [0, -50]
}));
```

### 动态创建

```javascript
const div = document.createElement('div');
div.innerHTML = '<div class="content">自定义内容</div>';

const overlay = engine.add(new mapvthree.DOMOverlay({
    dom: div,
    point: [116.404, 39.915, 0]
}));
```

## 构造参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `dom` | HTMLElement\|string | - | DOM 元素或元素 ID |
| `point` | array | `[0, 0, 0]` | 位置坐标 `[经度, 纬度, 高度]` |
| `offset` | array | `[0, 0]` | 屏幕偏移 `[x, y]`（像素） |
| `visible` | boolean | `true` | 是否可见 |
| `enableDragging` | boolean | `false` | 是否可拖拽 |
| `className` | string | - | 自定义 CSS 类名 |
| `stopPropagation` | boolean | `false` | 阻止事件传播到地图 |

## 属性（getter/setter）

```javascript
overlay.point = [116.41, 39.92, 100];
overlay.offset = [10, -20];  // x正值向右, y正值向下
overlay.visible = true;
overlay.enableDragging = true;
overlay.stopPropagation = true;
```

## 方法

### getBounds()

获取 DOM 元素的屏幕边界（像素）。

```javascript
const bounds = overlay.getBounds();
// { left, top, right, bottom }
```

### dispose()

```javascript
engine.remove(overlay);
overlay.dispose();
```

## 事件

| 事件 | 参数 | 说明 |
|------|------|------|
| `dragmove` | `{target, point}` | 拖拽移动时触发 |

> DOMOverlay 本身不提供 click 等事件，应直接在 DOM 元素上监听。

```javascript
// DOM 元素事件
overlay.dom.addEventListener('click', () => console.log('点击了覆盖物'));

// 拖拽事件
overlay.addEventListener('dragmove', (e) => console.log('拖拽到:', e.point));
```

## 可拖拽覆盖物

```javascript
const draggableDiv = document.createElement('div');
draggableDiv.style.cssText = 'background: rgba(0,150,255,0.9); color: white; padding: 8px; cursor: move;';
draggableDiv.textContent = '拖拽我';

const overlay = engine.add(new mapvthree.DOMOverlay({
    dom: draggableDiv,
    point: [116.404, 39.915, 0],
    enableDragging: true
}));

overlay.addEventListener('dragmove', (e) => console.log('位置:', e.point));
```

## 跟随移动对象

```javascript
const label = document.createElement('div');
label.textContent = '车辆 A001';

const overlay = engine.add(new mapvthree.DOMOverlay({
    dom: label,
    point: [116.404, 39.915, 0]
}));

// 定时更新位置
setInterval(() => {
    overlay.point = [newLng, newLat, 0];
}, 1000);
```
