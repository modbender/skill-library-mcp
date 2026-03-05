# PathTracker 路径追踪器

## 概述

PathTracker 沿预设路径驱动相机或对象动画，支持多种路径数据格式、视图模式和轨迹插值。适用于车辆轨迹回放、路线漫游等场景。

## 基础用法

```javascript
const tracker = engine.add(new mapvthree.PathTracker());

tracker.track = [
    [116.368264, 39.176959, 38],
    [116.370264, 39.178959, 40],
    [116.372264, 39.180959, 42],
];

tracker.start({
    duration: 10000,
    pitch: 60,
    range: 100
});
```

## 属性

### 路径配置

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `track` | array\|object | `[]` | 路径数据，支持坐标数组或 GeoJSON |
| `object` | Object3D | - | 跟踪的 3D 对象（可选） |
| `pointHandle` | string | `'line'` | 路径插值方式：`'line'`(直线)/`'curve'`(平滑曲线) |
| `interpolateDirectThreshold` | number | `10` | 直接过渡阈值（米） |
| `interpolateDirectThresholdPercent` | number | `0.4` | 插值百分比（路径总长的比例） |

### 状态属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `isRunning` | boolean | 是否运行中 |
| `isPaused` | boolean | 是否暂停 |
| `currentState` | object | 当前状态 `{point, hpr, direction}` |

## 生命周期控制

```javascript
tracker.start(options);  // 开始动画（暂停状态下调用则恢复播放）
tracker.pause();         // 暂停，返回当前状态
tracker.stop();          // 停止，重置状态，触发 onFinish
```

> **注意**：不存在 `resume()` 方法。暂停后再次调用 `start()` 即可恢复播放。

### start() 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `duration` | number | `1000` | 持续时间（毫秒） |
| `viewMode` | string | `'follow'` | 视图模式 |
| `heading` | number | `0` | 方位角（度） |
| `pitch` | number | `60` | 俯仰角（度） |
| `range` | number | `100` | 观察距离（米） |
| `easing` | string\|function | `'linear'` | 缓动函数 |
| `repeatCount` | number | - | 重复次数（优先于 keepRunning） |
| `delay` | number | `0` | 延迟启动（毫秒） |
| `keepRunning` | boolean | `false` | 持续运行 |
| `direction` | string | `'normal'` | 动画方向：`'normal'`/`'reverse'`/`'alternate'`/`'alternate-reverse'` |
| `loopMode` | string | `'repeat'` | 循环模式 |

### 视图模式 (ViewMode)

| 值 | 说明 |
|-----|------|
| `'follow'` | 相机跟随但不锁定方向 |
| `'lock'` | 相机锁定路径切线方向 |
| `'unlock'` | 相机不跟随 |
| `'keyFrame'` | 使用关键帧数据 |
| `'activeFrame'` | 支持速度控制的帧模式 |

## 回调函数

```javascript
tracker.onStart = () => console.log('开始');
tracker.onFinish = () => console.log('结束');
tracker.onUpdate = (state) => {
    // state: {point: [lng,lat,alt], hpr: {heading,pitch,roll}, direction}
    console.log('位置:', state.point);
};
```

## 路径数据格式

```javascript
// 坐标数组
tracker.track = [[lng1, lat1, alt1], [lng2, lat2, alt2]];

// GeoJSON
tracker.track = {
    type: 'Feature',
    geometry: { type: 'LineString', coordinates: [...] }
};

// 关键帧格式（viewMode: 'keyFrame'）
tracker.track = [
    { x: 116.368, y: 39.177, z: 38, pitch: 0, yaw: 0, time: 0 }
];

// 活跃帧格式（viewMode: 'activeFrame'，支持 speed）
tracker.track = [
    { x: 116.368, y: 39.177, z: 38, pitch: 0, speed: 50 }
];
```

## 让模型沿路径移动

```javascript
const vehicle = engine.add(new mapvthree.SimpleModel({ url: 'car.glb' }));

const tracker = engine.add(new mapvthree.PathTracker());
tracker.track = routeCoordinates;
tracker.object = vehicle;

tracker.start({ duration: 30000, range: 200, pitch: 45, viewMode: 'lock' });
```

## 轨迹插值

```javascript
tracker.pointHandle = 'curve';                         // 平滑曲线插值
tracker.interpolateDirectThreshold = 10;               // 插值直接阈值（默认 10）
tracker.interpolateDirectThresholdPercent = 0.4;       // 插值百分比（默认 0.4）
```

## 资源清理

```javascript
tracker.stop();
engine.remove(tracker);
```
