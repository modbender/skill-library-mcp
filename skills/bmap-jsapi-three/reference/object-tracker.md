# ObjectTracker 对象追踪器

## 概述

ObjectTracker 实时跟踪 3D 对象、向量或坐标点的位置变化。适用于跟随移动目标、锁定视角、实时监控等场景。

## 基础用法

```javascript
const vehicle = engine.add(new mapvthree.SimpleModel({
    url: 'models/car.glb',
    point: [116.404, 39.915, 0]
}));

const tracker = engine.add(new mapvthree.ObjectTracker());

tracker.track(vehicle, {
    range: 100,
    pitch: 60,
    lock: true
});
```

## 生命周期控制

```javascript
tracker.track(target, options);  // 开始追踪
tracker.pause();                 // 暂停
tracker.stop();                  // 停止，触发 onFinish
```

> **注意**：不存在 `resume()` 方法。暂停后再次调用 `start()` 即可恢复播放。

### 状态属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `isRunning` | boolean | 是否运行中 |
| `isPaused` | boolean | 是否暂停 |
| `currentState` | object | 当前状态 `{point, hpr, direction}` |

## track() 参数

### target

| 类型 | 说明 |
|------|------|
| Object3D | Three.js 3D 对象 |
| Vector3 | 三维向量 |
| array | 坐标数组 `[x, y, z]` |

### options

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `lock` | boolean | `true` | 是否锁定视角 |
| `range` | number | - | 观察距离（米） |
| `radius` | number | - | 观察距离（米），与 `range` 同义 |
| `pitch` | number | `0` | 俯仰角（度） |
| `heading` | number | `0` | 方位角（度） |
| `height` | number | - | 高度偏移（米） |
| `extraDir` | number | - | 额外方向修正角度（度） |
| `duration` | number | `0` | 过渡持续时间（毫秒），0 表示持续追踪 |
| `easing` | string\|function | `'linear'` | 缓动函数 |

## 回调函数

```javascript
tracker.onStart = () => console.log('开始追踪');
tracker.onFinish = () => console.log('追踪完成');
tracker.onUpdate = (state) => {
    console.log('目标位置:', state.point);
};

// 帧追踪回调（ObjectTracker 特有）
tracker.onTrackFrame = (lastState, currentState) => {
    // lastState: 上一帧状态（首帧为 null）
    // currentState: {point: [lng,lat,alt], hpr: {heading,pitch,roll}}
};
```

## 多目标切换

```javascript
const targets = [car1, car2, car3];
let currentIndex = 0;

function switchTarget(index) {
    tracker.track(targets[index], {
        range: 80,
        pitch: 50,
        lock: true,
        duration: 1500,
        easing: 'ease-in-out'
    });
    currentIndex = index;
}

switchTarget(0);
```

## 资源清理

```javascript
tracker.stop();
engine.remove(tracker);
```
