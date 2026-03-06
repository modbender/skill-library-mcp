# InfoWindow 信息窗口

信息窗口用于在地图上显示详细信息，通常配合 Marker 使用。地图上同时只能打开一个信息窗口。

## 快速开始

```javascript
var infoWindow = new BMapGL.InfoWindow('这是内容', {
    width: 250,
    height: 100,
    title: '标题'
});

var point = new BMapGL.Point(116.404, 39.915);
map.openInfoWindow(infoWindow, point);
```

## 构造函数

```javascript
new BMapGL.InfoWindow(content, options)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| content | string \| HTMLElement | 信息窗口内容，支持 HTML 片段或 DOM 元素 |
| options | Object | 配置参数 |

### options 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| width | number | `0` | 宽度（220-730px），0 表示自适应 |
| height | number | `0` | 高度（60-650px），0 表示自适应 |
| maxWidth | number | `600` | 最大化时的宽度（220-730px） |
| title | string | `''` | 标题，支持 HTML 片段 |
| offset | Size | `new Size(0, 0)` | 底部尖角相对于锚点的像素偏移 |
| enableMaximize | boolean | `false` | 是否显示最大化按钮 |
| enableAutoPan | boolean | `true` | 是否自动平移地图使窗口完全可见 |
| enableCloseOnClick | boolean | `true` | 点击地图时是否关闭窗口 |
| maxContent | string | `''` | 最大化时显示的内容 |
| margin | Array | `[10, 10, 40, 10]` | 与地图边界的边距 [上, 右, 下, 左] |

## 方法

### 内容

```javascript
infoWindow.setContent('<div>新内容</div>');
infoWindow.setContent(document.getElementById('content'));  // DOM 元素
var content = infoWindow.getContent();

infoWindow.setTitle('新标题');
var title = infoWindow.getTitle();

infoWindow.setMaxContent('<div>最大化内容</div>');  // 需启用 enableMaximize
```

### 尺寸

```javascript
infoWindow.setWidth(300);     // 220-730px，0 为自适应
infoWindow.setHeight(200);    // 60-650px，0 为自适应
infoWindow.setMaxWidth(500);  // 最大化时的宽度
```

### 显示控制

```javascript
// 打开 - 通过 map 或 marker
map.openInfoWindow(infoWindow, point);
marker.openInfoWindow(infoWindow);

// 关闭
infoWindow.close();
map.closeInfoWindow();
marker.closeInfoWindow();

// 状态查询
var isOpen = infoWindow.isOpen();

// 重绘（内容变化后调用）
infoWindow.redraw();
```

### 最大化

```javascript
infoWindow.enableMaximize();   // 显示最大化按钮
infoWindow.disableMaximize();  // 隐藏最大化按钮
infoWindow.maximize();         // 最大化
infoWindow.restore();          // 还原
```

### 自动平移

打开窗口时自动平移地图，确保窗口完全可见。

```javascript
infoWindow.enableAutoPan();   // 启用
infoWindow.disableAutoPan();  // 禁用
```

### 点击关闭

```javascript
infoWindow.enableCloseOnClick();   // 点击地图关闭窗口
infoWindow.disableCloseOnClick();  // 禁用
```
## 事件

```javascript
infoWindow.addEventListener('open', function(e) {
    console.log('窗口打开', e.point);
});

infoWindow.addEventListener('close', function(e) {
    console.log('窗口关闭', e.point);
});

infoWindow.addEventListener('clickclose', function() {
    console.log('点击关闭按钮');
});

infoWindow.addEventListener('maximize', function() {
    console.log('窗口最大化');
});

infoWindow.addEventListener('restore', function() {
    console.log('窗口还原');
});
```


## 常见场景

### 带最大化功能

```javascript
var infoWindow = new BMapGL.InfoWindow('简要内容', {
    width: 250,
    height: 100,
    title: '详情',
    enableMaximize: true,
    maxWidth: 500,
    maxContent: '<div>这里是更详细的内容...</div>'
});

map.openInfoWindow(infoWindow, point);
```

### 阻止关闭

通过 `onClosing` 回调返回 `false` 可阻止窗口关闭。

```javascript
var infoWindow = new BMapGL.InfoWindow('内容', {
    width: 200,
    onClosing: function() {
        if (!confirm('确定关闭？')) {
            return false;  // 阻止关闭
        }
        return true;
    }
});
```


## 注意事项

1. **单例限制**：地图上同时只能打开一个信息窗口，打开新窗口会自动关闭之前的
2. **尺寸范围**：宽度 220-730px，高度 60-650px，超出范围会被限制
3. **内存管理**：不再使用的信息窗口应调用 `dispose()` 释放资源
