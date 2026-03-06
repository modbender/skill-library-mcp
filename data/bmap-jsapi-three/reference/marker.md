# Marker 标记

DOM 覆盖物标记组件，用于在地图指定位置显示图标。继承自 DOMOverlay，支持拖拽、点击等 DOM 交互。

> 注意：Marker 使用 DOM 渲染，大量标记（>100 个）建议使用 Label、SimplePoint 或 ClusterPoint。

## 基础用法

```javascript
const marker = engine.add(new mapvthree.Marker({
    point: [116.404, 39.915, 0],
    icon: 'assets/icons/marker.png',
    title: '北京',
    width: 32,
    height: 32
}));
```

## 构造参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `point` | array | `[0, 0, 0]` | 位置坐标 `[经度, 纬度, 高度]` |
| `icon` | string | - | 图标 URL |
| `title` | string | - | 标题（鼠标悬停提示） |
| `width` | number | `25` | 宽度（像素） |
| `height` | number | `25` | 高度（像素） |
| `offset` | array | `[0, 0]` | 屏幕偏移 `[x, y]`（像素） |
| `visible` | boolean | `true` | 是否可见 |
| `enableDragging` | boolean | `false` | 是否可拖拽 |
| `className` | string | - | 自定义 CSS 类名 |

## 属性修改

Marker 使用 getter/setter 属性代理：

```javascript
marker.icon = 'assets/icons/active.png';
marker.title = '新标题';
marker.point = [116.41, 39.92, 100];
marker.width = 40;
marker.height = 40;
marker.offset = [0, -10];
marker.visible = false;
marker.enableDragging = true;
```

## 事件

Marker 继承自 DOMOverlay，点击等事件在 `marker.dom` 上监听；拖拽事件在 Marker 实例上监听：

```javascript
// DOM 点击
marker.dom.addEventListener('click', () => {
    engine.flyTo({
        center: marker.point,
        range: 5000
    });
});

// 拖拽事件
marker.addEventListener('dragmove', (e) => {
    console.log('拖拽到:', e.point);
});
```

## 示例：可拖拽标记

```javascript
const marker = engine.add(new mapvthree.Marker({
    point: [116.404, 39.915, 0],
    icon: 'assets/icons/draggable.png',
    enableDragging: true,
    width: 40,
    height: 40
}));

marker.addEventListener('dragmove', (e) => {
    console.log('新位置:', e.point);
});
```

## 资源清理

```javascript
engine.remove(marker);
marker.dispose();
```
