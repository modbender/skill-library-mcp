# Popup 弹出窗口

## 概述

Popup 是弹出窗口组件，继承自 DOMOverlay。默认尺寸 250x130px，通过 CSS 自定义样式。

## 基础用法

```javascript
const popup = engine.add(new mapvthree.Popup({
    point: [116.404, 39.915, 0]
}));

popup.title = '信息标题';
popup.content = '<div>弹窗内容</div>';
popup.visible = true;
```

## 构造参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `point` | array | `[0, 0, 0]` | 位置坐标 `[经度, 纬度, 高度]` |
| `offset` | array | `[0, 0]` | 屏幕偏移 `[x, y]` |
| `visible` | boolean | `true` | 是否可见 |
| `className` | string | - | 自定义 CSS 类名 |
| `enableDragging` | boolean | `false` | 是否可拖拽 |
| `stopPropagation` | boolean | `false` | 阻止事件传播 |

## 属性（getter/setter）

### title

标题内容（支持 string 或 HTMLElement）。

```javascript
popup.title = '新标题';
popup.title = '<div style="color: red;">自定义标题</div>';
```

### content

弹窗内容（支持 string 或 HTMLElement）。

```javascript
popup.content = '<p>详细信息</p>';

// 带交互元素
const el = document.createElement('div');
el.innerHTML = '<button id="btn">确认</button>';
el.querySelector('#btn').addEventListener('click', () => popup.visible = false);
popup.content = el;
```

### 其他属性

```javascript
popup.point = [116.41, 39.92, 100];
popup.visible = true;
popup.offset = [0, -20];
popup.stopPropagation = true;
```

## 事件

| 事件 | 说明 |
|------|------|
| `close` | 用户点击关闭按钮时触发 |

```javascript
popup.addEventListener('close', (e) => {
    console.log('弹窗已关闭');
});
```

> `popup.visible = false` 不会触发 `close` 事件。

## 点击标记显示弹窗

```javascript
const marker = engine.add(new mapvthree.Marker({
    point: [116.404, 39.915, 0],
    width: 32,
    height: 32
}));

const popup = engine.add(new mapvthree.Popup({
    point: [116.404, 39.915, 50],
    visible: false
}));

popup.title = '地点信息';
popup.content = '<p>详细内容</p>';

marker.dom.addEventListener('click', () => popup.visible = true);
```

## CSS 自定义

```css
.custom-popup .frame {
    width: 300px !important;
    height: 200px !important;
    background: #f5f5f5 !important;
}

.custom-popup .title {
    background: #4a90e2;
    color: white;
    padding: 10px;
}

.custom-popup .content {
    padding: 12px;
    max-height: 150px;
    overflow-y: auto;
}
```

## 资源清理

```javascript
engine.remove(popup);
popup.dispose();
```
