# OrbitTracker 轨道追踪器

## 概述

OrbitTracker 实现围绕指定中心点或对象的圆周运动动画。支持自定义半径、高度、角度范围和循环模式，适用于建筑展示、环绕观察等场景。

## 基础用法

```javascript
const tracker = engine.add(new mapvthree.OrbitTracker());

tracker.start({
    center: [116.404, 39.915, 0],
    radius: 200,
    duration: 15000,
    pitch: 30
});
```

## 生命周期控制

```javascript
tracker.start(options);  // 开始动画（暂停状态下调用则恢复播放）
tracker.pause();         // 暂停，返回当前状态
tracker.stop();          // 停止，重置状态，触发 onFinish
```

> **注意**：不存在 `resume()` 方法。暂停后再次调用 `start()` 即可恢复播放。

### 状态属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `isRunning` | boolean | 是否运行中 |
| `isPaused` | boolean | 是否暂停 |
| `currentState` | object | 当前状态 `{point, hpr, direction}` |

## start() 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `center` | array | - | 地理坐标中心点 `[lng, lat, alt]` |
| `projectedCenter` | array | - | 投影坐标中心点 `[x, y, z]` |
| `object` | Object3D | - | 围绕的 3D 对象（与 center 二选一） |
| `radius` | number | `100` | 旋转半径（米） |
| `height` | number | `0` | 高度偏移（米） |
| `startAngle` | number | `0` | 起始角度（度） |
| `endAngle` | number | `360` | 结束角度（度） |
| `duration` | number | `10000` | 持续时间（毫秒） |
| `pitch` | number | - | 俯仰角（度） |
| `keepRunning` | boolean | `false` | 持续运行 |
| `loopMode` | string | `'repeat'` | 循环模式 |
| `direction` | string | `'normal'` | 动画方向：`'normal'`/`'reverse'`/`'alternate'`/`'alternate-reverse'` |
| `useWorldAxis` | boolean | `false` | 使用世界轴 |
| `easing` | string\|function | `'linear'` | 缓动函数 |
| `repeatCount` | number | - | 重复次数（优先于 keepRunning） |
| `delay` | number | `0` | 延迟启动（毫秒） |

## 回调函数

```javascript
tracker.onStart = () => console.log('开始环绕');
tracker.onFinish = () => console.log('环绕完成');
tracker.onUpdate = (state) => {
    // state: {point: [lng,lat,alt], hpr: {heading,pitch,roll}, direction}
    console.log('相机位置:', state.point);
};
```

## 围绕 3D 对象旋转

```javascript
const building = engine.add(new mapvthree.SimpleModel({
    url: 'models/building.glb',
    point: [116.404, 39.915, 0]
}));

const tracker = engine.add(new mapvthree.OrbitTracker());
tracker.start({
    object: building,
    radius: 150,
    height: 50,
    duration: 12000,
    pitch: 30
});
```

## useWorldAxis 说明

| 特性 | 本地轴 (false) | 世界轴 (true) |
|------|------------|-----------|
| 旋转方向 | 受 height 影响，可能倾斜 | 始终围绕竖直方向旋转 |
| 视觉效果 | 3D 球面环绕 | 2D 平面旋转 |
| 适用场景 | 建筑展示、产品展示 | 地标展示、俯瞰环绕 |

## 资源清理

```javascript
tracker.stop();
engine.remove(tracker);
```
