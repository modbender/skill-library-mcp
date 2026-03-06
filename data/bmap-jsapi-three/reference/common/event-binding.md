# 事件绑定通用模式

## 图层事件

```javascript
layer.addEventListener('click', (e) => {
    console.log('点击了要素', e.entity);
});

layer.addEventListener('mouseenter', (e) => {});
layer.addEventListener('mouseleave', (e) => {});
```

## 地图事件

```javascript
engine.map.addEventListener('click', (e) => {});
engine.map.addEventListener('dblclick', (e) => {});
```

## 组件事件

部分组件使用 `addEventListener`：

```javascript
editor.addEventListener('created', () => {});
editor.addEventListener('update', () => {});
label.addEventListener('click', (e) => {});
```

## 支持的事件类型

| 事件 | 说明 |
|------|------|
| click | 点击 |
| dblclick | 双击 |
| rightclick | 右键点击 |
| rightdblclick | 右键双击 |
| mouseenter | 鼠标进入 |
| mouseleave | 鼠标离开 |
| mousemove | 鼠标移动 |
| pointerdown | 指针按下 |
| pointerup | 指针抬起 |

## 回调参数

| 属性 | 类型 | 说明 |
|------|------|------|
| e.point | Vector3 | 经纬度坐标 |
| e.position | Vector3 | 三维场景坐标 |
| e.pixel | Array | 像素坐标 |
| e.event | Event | 原始浏览器事件 |
| e.object | Object3D | 触发事件的物体 |
| e.entity | Object | 触发事件的具体实例 |
| e.target | Object3D | 目标物体 |
| e.currentTarget | Object3D | 当前事件处理的物体 |
| e.intersection | Object | 光线与物体的相交信息 |
