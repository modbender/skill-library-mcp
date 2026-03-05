# 地图事件

## 事件绑定方式

### addEventListener

```javascript
map.addEventListener('click', function(e) {
    console.log(e.point);
});
```

### on（简写）

```javascript
map.on('click', function(e) {
    // 处理逻辑
});
```

### 移除监听

```javascript
// 指定处理函数移除
map.off('click', handler);
map.removeEventListener('click', handler);

// 移除所有该类型事件
map.off('click');
```

## 交互事件

### 通用交互事件

以下事件在 PC 端和 H5 端均可使用，推荐优先使用：

| 事件名 | 触发时机 | PC 端来源 | H5 端来源 |
|--------|--------|----------|----------|
| click | 单击 | 原生 click | touchend 模拟派发 |
| dblclick | 双击 | 原生 dblclick | 两次 touchend 模拟 |

```javascript
// 推荐：使用通用事件，自动适配 PC 和 H5
map.on('click', function(e) {
    console.log('点击位置:', e.point.lng, e.point.lat);
});
```

### PC 专有事件

以下事件仅在 PC 端（鼠标操作）可用：

| 事件名 | 触发时机 | 说明 |
|--------|--------|------|
| rightclick | 右键单击 | 通过 contextmenu 事件触发 |
| rightdblclick | 右键双击 | |
| mousedown | 鼠标按下 | |
| mouseup | 鼠标释放 | |
| mousemove | 鼠标移动 | 仅空闲状态时触发 |
| mouseout | 鼠标离开地图区域 | |

```javascript
// 右键菜单示例（仅 PC）
map.on('rightclick', function(e) {
    showContextMenu(e.pixel.x, e.pixel.y);
});

// 鼠标悬停效果（仅 PC）
map.on('mousemove', function(e) {
    highlightFeatureAt(e.point);
});
```

### H5 专有事件

以下事件仅在 H5 端（触摸操作）可用：

| 事件名 | 触发时机 | 说明 |
|--------|--------|------|
| touchstart | 触摸开始 | 支持多点触摸 |
| touchmove | 触摸移动 | 高频事件，注意性能 |
| touchend | 触摸结束 | 会同时派发 click 事件 |

#### 触摸事件对象特有属性

| 属性 | 类型 | 说明 |
|------|------|------|
| touchesCount | number | 当前触点总数 |
| targetTouchesCount | number | 目标元素上的触点数 |
| changedTouchesCount | number | 改变的触点数 |
| secondTouchInfo | Object | 第二个触点信息（多点触摸时） |

```javascript
// 检测多点触摸（仅 H5）
map.on('touchstart', function(e) {
    console.log('触点数:', e.touchesCount);
    if (e.touchesCount > 1) {
        console.log('第二触点:', e.secondTouchInfo);
    }
});
```

### 跨平台开发建议

```javascript
// ✓ 推荐：优先使用通用事件
map.on('click', handleClick);
map.on('dblclick', handleDblClick);

// ✓ 按需添加平台特定功能
if (!isMobile()) {
    map.on('mousemove', handleHover);
    map.on('rightclick', handleRightClick);
}

// ✗ 避免：同时监听 click 和 touchend 处理相同逻辑
// 会导致 H5 端触发两次
```

## 手势操作

### 双指操作触发的事件

双指手势操作会触发常规的视图变化事件：

| 手势操作 | 触发的事件 | 说明 |
|---------|-----------|------|
| 双指缩放 | zoomstart → zooming → zoomend | 通过 `map.getZoom()` 获取当前级别 |
| 双指旋转 | heading_changed | 通过 `map.getHeading()` 获取当前朝向 |
| 双指上下滑动 | tilt_changed | 通过 `map.getTilt()` 获取当前倾斜角 |

### 监听双指操作示例

```javascript
// 监听缩放变化
map.on('zoomend', function() {
    console.log('当前缩放级别:', map.getZoom());
});

// 监听地图朝向变化
map.on('heading_changed', function() {
    console.log('当前朝向:', map.getHeading());
});

// 监听倾斜角变化
map.on('tilt_changed', function() {
    console.log('当前倾斜角:', map.getTilt());
});
```

### 手势相关配置

可通过以下方法控制手势行为：

```javascript
map.enablePinchToZoom();      // 启用双指缩放
map.disablePinchToZoom();     // 禁用双指缩放
map.enableRotateGestures();   // 启用旋转手势
map.disableRotateGestures();  // 禁用旋转手势
map.enableTilt();             // 启用倾斜
map.disableTilt();            // 禁用倾斜
```

## 视图变化事件

> 以下事件均为**通用事件**，PC 端和 H5 端都会触发。

### 拖拽事件

| 事件名 | 触发时机 | PC 端触发方式 | H5 端触发方式 |
|--------|--------|-------------|--------------|
| dragstart | 拖拽开始 | 鼠标拖拽 | 手指拖拽 |
| dragging | 拖拽中（连续触发） | 鼠标拖拽 | 手指拖拽 |
| dragend | 拖拽结束 | 鼠标拖拽 | 手指拖拽 |

### 移动事件

| 事件名 | 触发时机 | 说明 |
|--------|--------|------|
| movestart | 移动开始 | 拖拽、flyTo、panTo、setCenter 等均会触发 |
| moving | 移动中（连续触发） | 包含惯性滚动过程 |
| moveend | 移动结束 | |

### 缩放事件

| 事件名 | 触发时机 | PC 端触发方式 | H5 端触发方式 |
|--------|--------|-------------|--------------|
| zoomstart | 缩放开始 | 滚轮/双击/API | 双指缩放/双击/API |
| zooming | 缩放中（连续触发） | 滚轮/双击/API | 双指缩放/双击/API |
| zoomend | 缩放结束 | 滚轮/双击/API | 双指缩放/双击/API |
| zoomexceeded | 缩放超出范围 | 超出 minZoom/maxZoom 时触发 | |

## 生命周期事件

> 以下事件均为**通用事件**，与交互方式无关，PC 端和 H5 端都会触发。

| 事件名 | 触发时机 | 说明 |
|--------|--------|------|
| load | 地图加载完成 | 地图初始化完成时触发 |
| tilesloaded | 瓦片加载完成 | 适合做地图加载完成判断 |
| resize | 容器尺寸变化 | 窗口或容器尺寸改变时触发 |
| center_changed | 中心点改变 | 任何导致中心点变化的操作都会触发 |
| zoom_changed | 缩放级别改变 | 任何导致缩放级别变化的操作都会触发 |
| heading_changed | 地图朝向改变 | 旋转地图时触发 |
| tilt_changed | 地图倾斜角改变 | 倾斜地图时触发 |
| maptypechange | 地图类型切换 | 如切换到地球模式 |
| idle | 地图进入空闲状态 | 所有操作完成后触发 |
| destroy | 地图销毁 | 调用 destroy() 后触发 |

## 事件对象属性

### 通用属性

| 属性 | 类型 | 说明 |
|------|------|------|
| type | string | 事件类型 |
| target | Map | 事件源（地图实例） |
| timeStamp | number | 事件时间戳 |
| domEvent | Event | 原始 DOM 事件 |

### 鼠标/触摸事件属性

| 属性 | 类型 | 说明 |
|------|------|------|
| point | Point | 地理坐标（经纬度） |
| pixel | Pixel | 像素坐标（相对于地图左上角） |
| offsetPos | Object | 相对于地图容器的坐标 |
| clientPos | Object | 相对于浏览器窗口的坐标 |
| overlay | Overlay | 点击的覆盖物（如有） |

```javascript
map.on('click', function(e) {
    console.log('事件类型:', e.type);
    console.log('经纬度:', e.point.lng, e.point.lat);
    console.log('像素坐标:', e.pixel.x, e.pixel.y);
});
```