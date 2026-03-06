# 地图初始化

## 引入资源

### 在线引入

```html
<script src="//api.map.baidu.com/api?v=1.0&type=webgl&ak=您的密钥"></script>
```

## 基础初始化

### HTML 结构

```html
<div id="map_container" style="width: 100%; height: 100%;"></div>
```

### JavaScript 初始化

```javascript
// 创建地图实例
var map = new BMapGL.Map('map_container');

// 设置中心点和缩放级别（必须调用）
map.centerAndZoom(new BMapGL.Point(116.404, 39.915), 12);

// 交互
map.enableScrollWheelZoom();
```

### centerAndZoom 方法

```javascript
map.centerAndZoom(center, zoom, options)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| center | Point \| string | 中心点坐标或城市名称（如 "北京"） |
| zoom | number | 缩放级别（3-21，支持浮点数） |
| options | Object | 可选配置 |

## 配置选项

### 构造函数配置

```javascript
var map = new BMapGL.Map('container', {
    minZoom: 5,
    maxZoom: 18,
    forceRenderType: 'webgl',
    showControls: false,
    enableIconClick: false,
    fixCenterWhenResize: true,
    displayOptions: {
        poi: true,
        building: true
    }
});
```

### 完整配置选项

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| minZoom | number | 3 | 最小缩放级别 |
| maxZoom | number | 21 | 最大缩放级别 |
| forceRenderType | string | '' | 强制渲染类型：'webgl' / 'canvas' / 'dom' |
| showControls | boolean | false | 是否显示默认控件 |
| enableIconClick | boolean | false | 是否启用底图 POI 点击 |
| fixCenterWhenResize | boolean | false | 窗口大小变化时是否固定中心点 |
| fixCenterWhenPinch | boolean | false | 双指缩放时是否固定中心点 |
| enableAutoResize | boolean | true | 是否自动调整地图尺寸 |
| enableDragging | boolean | true | 是否允许拖拽 |
| enableRotate | boolean | true | 是否允许旋转 |
| enableTilt | boolean | true | 是否允许倾斜 |
| enableKeyboard | boolean | false | 是否启用键盘控制 |
| enableDblclickZoom | boolean | true | 是否启用双击缩放 |
| enableWheelZoom | boolean | false | 是否启用滚轮缩放 |
| enablePinchZoom | boolean | true | 是否启用双指缩放 |
| zoomCenter | Point | null | 指定缩放中心点 |
| style | string \| Object | 'default' | 地图样式 |
| displayOptions | Object | - | 显示选项配置 |

### displayOptions 子选项

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| poi | boolean | true | 是否显示 POI 点 |
| poiText | boolean | true | 是否显示 POI 文字 |
| poiIcon | boolean | true | 是否显示 POI 图标 |
| overlay | boolean | true | 是否显示覆盖物 |
| building | boolean | true | 是否显示 3D 建筑 |
| indoor | boolean | false | 是否显示室内图 |
| street | boolean | true | 是否显示街道 |
| layer | boolean | true | 是否显示图层 |
| skyColors | Array | null | 天空渐变颜色，格式：`[地面颜色, 天空颜色]` |

**skyColors 配置示例：**

```javascript
// 天空渐变：从地面到天空的颜色过渡
displayOptions: {
    skyColors: [
        'rgba(226, 237, 248, 0)',   // 地面颜色
        'rgba(186, 211, 252, 1)'    // 天空颜色
    ]
}
```

### 动态修改配置

```javascript
map.setOptions({
    displayOptions: { poi: false, building: false }
});

map.setDisplayOptions({ poi: true, overlay: true });
```

## 视图控制方法

### 基础方法

| 方法 | 说明 |
|------|------|
| `setCenter(point, options)` | 设置中心点 |
| `getCenter()` | 获取中心点（返回 Point） |
| `setZoom(zoom, options)` | 设置缩放级别 |
| `getZoom()` | 获取当前缩放级别 |
| `setHeading(heading, options)` | 设置旋转角度（0-360） |
| `getHeading()` | 获取旋转角度（-180 到 180） |
| `setTilt(tilt, options)` | 设置倾斜角度（0-87） |
| `getTilt()` | 获取倾斜角度 |
| `getBounds()` | 获取当前视野范围（返回 Bounds） |
| `getContainerSize()` | 获取容器尺寸（返回 Size） |
| `resize()` | 强制调整地图尺寸 |

### 动画与回调配置

视图控制方法的 `options` 参数支持以下配置：

| 选项 | 类型 | 适用方法 | 说明 |
|------|------|----------|------|
| noAnimation | boolean | 全部 | 是否禁用动画 |
| callback | function | 全部 | 动画完成后的回调函数 |
| zoomCenter | Point | setZoom | 指定缩放中心点 |

```javascript
// 禁用动画
map.setCenter(point, { noAnimation: true });

// 带回调
map.setZoom(15, { callback: function() { console.log('完成'); } });

// 指定缩放中心（仅 setZoom）
map.setZoom(18, { zoomCenter: new BMapGL.Point(116.404, 39.915) });
```

### 飞行动画

```javascript
map.flyTo(new BMapGL.Point(116.404, 39.915), 18, {
    heading: 90,
    tilt: 60,
    duration: 1200,
    callback: function() { console.log('飞行完成'); }
});
```

### 平移动画

```javascript
map.panTo(new BMapGL.Point(116.404, 39.915), { noAnimation: false });
```

## 交互控制方法

| 启用方法 | 禁用方法 | 说明 |
|---------|---------|------|
| `enableDragging()` | `disableDragging()` | 地图拖拽 |
| `enableInertialDragging()` | `disableInertialDragging()` | 惯性拖拽 |
| `enableScrollWheelZoom()` | `disableScrollWheelZoom()` | 滚轮缩放 |
| `enableContinuousZoom()` | `disableContinuousZoom()` | 连续缩放 |
| `enableDoubleClickZoom()` | `disableDoubleClickZoom()` | 双击缩放 |
| `enableKeyboard()` | `disableKeyboard()` | 键盘控制 |
| `enablePinchToZoom()` | `disablePinchToZoom()` | 双指缩放 |
| `enableRotateGestures()` | `disableRotateGestures()` | 手势旋转 |
| `enableTiltGestures()` | `disableTiltGestures()` | 手势倾斜 |
| `enableTilt()` | `disableTilt()` | 倾斜功能 |
| `enableRotate()` | `disableRotate()` | 旋转功能 |
| `enableAutoResize()` | `disableAutoResize()` | 自动调整尺寸 |

## 销毁地图

```javascript
map.destroy();
```


**注意：** 必须调用 `destroy()` 释放内存，销毁后不可再使用该实例。

## 完整示例

### 基础地图

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>地图初始化示例</title>
    <style>
        html, body { width: 100%; height: 100%; margin: 0; padding: 0; }
        #map_container { width: 100%; height: 100%; }
    </style>
    <script src="//api.map.baidu.com/api?v=1.0&type=webgl&ak=您的密钥"></script>
</head>
<body>
    <div id="map_container"></div>
    <script>
        var map = new BMapGL.Map('map_container', { enableIconClick: false });
        map.centerAndZoom(new BMapGL.Point(116.404, 39.915), 15);
        map.enableScrollWheelZoom();
    </script>
</body>
</html>
```
