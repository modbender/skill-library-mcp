# CustomOverlay 自定义覆盖物

用于在地图上添加自定义 HTML DOM 元素的覆盖物，可以实现信息卡片、自定义标注等复杂展示效果。

## 快速开始

```javascript
// 定义 DOM 创建函数
function createDOM() {
    var div = document.createElement('div');
    div.style.cssText = 'background:#fff; padding:10px; border-radius:4px;';
    div.innerHTML = '<h4>故宫博物院</h4><p>建于1420年</p>';
    return div;
}

// 创建自定义覆盖物
var customOverlay = new BMapGL.CustomOverlay(createDOM, {
    point: new BMapGL.Point(116.403, 39.924)
});

map.addOverlay(customOverlay);
```

## 构造函数

```javascript
new BMapGL.CustomOverlay(createDom, options)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| createDom | Function | 创建 DOM 的回调函数，返回 HTMLElement (必需) |
| options | Object | 配置参数 |

### createDom 函数

创建 DOM 元素的回调函数。函数内部 `this` 指向覆盖物实例，可通过 `this.properties` 访问自定义属性。

```javascript
function createDOM() {
    var div = document.createElement('div');
    // 访问自定义属性
    div.textContent = this.properties.title;
    return div;
}
```

### options 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| point | Point | - | 覆盖物坐标位置 (必需) |
| offsetX | number | `0` | X 轴像素偏移量，正值向右 |
| offsetY | number | `0` | Y 轴像素偏移量，正值向下 |
| anchors | Array | `[0.5, 1]` | 锚点，范围 [0,1]，[0,0] 为左上角，[0.5,1] 为底部居中 |
| minZoom | number | `3` | 最小显示缩放级别 |
| maxZoom | number | `21` | 最大显示缩放级别 |
| zIndex | number | `0` | CSS z-index 层级 |
| visible | boolean | `true` | 初始是否可见 |
| enableMassClear | boolean | `true` | 调用 map.clearOverlays() 时是否被清除 |
| enableDraggingMap | boolean | `false` | 在覆盖物上是否允许拖拽地图 |
| properties | Object | `{}` | 自定义属性，可在 createDom 中通过 this.properties 访问 |
| fixBottom | boolean | `false` | 是否固定在 DOM 底部对齐 |

### 高级选项

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| useTranslate | boolean | `false` | 使用 CSS translate3d 定位，性能更好 |
| nextTick | boolean | `false` | 异步渲染，解决 div 自适应宽度问题 |
| rotationInit | number | `0` | 初始旋转角度（度） |
| rotationFlip | boolean | `false` | 旋转时是否允许翻转 |
| autoFollowHeadingChanged | boolean | `false` | 是否跟随地图旋转自动调整角度 |
| synUpdate | boolean | `false` | 是否同步更新（监听地图 ondraw 事件） |

## 方法

### 位置

```javascript
customOverlay.setPoint(new BMapGL.Point(116.404, 39.915));
var pos = customOverlay.getPoint();  // 返回 Point
```

### 属性

获取或更新自定义属性。`setProperties` 采用**增量合并**方式（Object.assign），新属性会与原有属性合并，而非整体替换。更新后会触发 DOM 重建。

```javascript
// 获取属性
var props = customOverlay.getProperties();

// 更新属性（增量合并，会重新调用 createDom）
customOverlay.setProperties({
    title: '新标题',
    content: '新内容'
});
// 原有的其他属性（如 imgSrc）会保留
```

### 旋转

```javascript
customOverlay.setRotation(45);  // 设置旋转角度
var angle = customOverlay.getRotation();  // 获取当前角度
```

## 事件

支持的事件类型：`click`、`mouseover`、`mouseout`

```javascript
customOverlay.addEventListener('click', function(e) {
    console.log('点击位置:', e.latLng);  // 地理坐标
    console.log('像素位置:', e.pixel);   // 屏幕像素坐标
});
```

## 常见场景

### 信息卡片

```javascript
function createInfoCard() {
    var div = document.createElement('div');
    div.className = 'info-card';
    div.innerHTML = `
        <img src="${this.properties.imgSrc}" />
        <h4>${this.properties.title}</h4>
        <p>${this.properties.desc}</p>
    `;
    return div;
}

var infoCard = new BMapGL.CustomOverlay(createInfoCard, {
    point: new BMapGL.Point(116.403, 39.924),
    offsetY: -10,
    properties: {
        title: '故宫博物院',
        desc: '中国明清两代的皇家宫殿',
        imgSrc: 'gugong.jpg'
    }
});

map.addOverlay(infoCard);
```
