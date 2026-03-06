# 3D 模型加载指南

## 概述

Mapv-three 提供三种模型加载方式：
- **SimpleModel**：单体模型，支持地理坐标定位
- **AnimationModel**：动画模型，支持骨骼动画控制
- **LODModel**：LOD 模型，根据相机距离自动切换精度

支持格式：`.glb`（推荐）、`.gltf`

## 基础用法

### SimpleModel

```javascript
const model = engine.add(new mapvthree.SimpleModel({
    url: 'assets/models/building.glb',
    point: [116.404, 39.915, 0],
    scale: [1, 1, 1],
    rotation: [0, 0, 0],
}));

model.addEventListener('loaded', (e) => {
    console.log('模型加载完成:', e.value);
});
```

### AnimationModel

```javascript
const animModel = engine.add(new mapvthree.AnimationModel({
    url: 'assets/models/character.glb',
    point: [116.404, 39.915, 0],
    autoPlay: true,
}));

animModel.play(0);       // 播放第1个动画
animModel.stop(0);       // 停止第1个动画
animModel.playAll();     // 播放所有
animModel.stopAll();     // 停止所有
animModel.setSpeed(2);   // 2倍速
animModel.setLoop(true); // 循环播放
```

### LODModel

```javascript
const lodModel = engine.add(new mapvthree.LODModel({
    hysteresis: 0.1,
    levels: [
        { distance: 100, file: 'models/high.glb' },
        { distance: 500, file: 'models/medium.glb' },
        { distance: 1000, file: 'models/low.glb' },
    ]
}));
```

> LODModel 使用 Three.js 世界坐标，不支持直接设置地理坐标。如需地理定位，请使用 SimpleModel。

## 构造参数

### SimpleModel / AnimationModel

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `url` | string | - | 模型 URL（与 object 二选一） |
| `object` | string/Object3D | - | 模型 URL 或 Object3D 实例 |
| `point` | array | `[0,0,0]` | 地理坐标 `[经度, 纬度, 高度]` |
| `scale` | array/number | `[1,1,1]` | 缩放比例 |
| `rotation` | array | `[0,0,0]` | 旋转弧度 `[roll, pitch, heading]` |
| `autoYUpToZUp` | boolean | `true` | 自动转换 Y-up 为 Z-up |
| `name` | string | `''` | 模型名称 |

**AnimationModel 额外参数：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `autoPlay` | boolean | `false` | 自动播放动画 |

### LODModel

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `hysteresis` | number | `0.1` | 切换缓冲（0-1），防抖动 |
| `levels` | array | `[]` | 层级配置 `[{distance, file, hysteresis?}]` |

## 方法

### SimpleModel

```javascript
model.setTransform({ point: [116.41, 39.92, 100], rotation: [0, 0, Math.PI / 4], scale: 2 });
model.point = [lng, lat, z];
```

### AnimationModel

| 方法 | 参数 | 说明 |
|------|------|------|
| `play(index)` | 动画索引（默认 0） | 播放动画 |
| `stop(index)` | 动画索引 | 停止动画 |
| `playAll()` | - | 播放所有 |
| `stopAll()` | - | 停止所有 |
| `setSpeed(speed, index?)` | 速度，索引（可选） | 设置播放速度 |
| `setLoop(loop, index?)` | 是否循环，索引（可选） | 设置循环模式 |

### LODModel

| 方法 | 返回值 | 说明 |
|------|--------|------|
| `addLevel(file, distance, hysteresis)` | this | 添加层级 |
| `removeLevel(file)` | this | 移除层级 |
| `getCurrentLevel()` | number | 当前层级索引 |
| `getCurrentModel()` | Object3D | 当前显示的模型 |

## 事件

| 事件 | 触发时机 | e.value |
|------|----------|---------|
| `loaded` | 模型加载完成 | 模型实例 |
| `complete` | LODModel 所有层级加载完成 | LODModel 实例 |

## 配合路径追踪

```javascript
const vehicle = engine.add(new mapvthree.SimpleModel({
    url: 'assets/models/car.glb',
    point: [116.404, 39.915, 0]
}));

const tracker = engine.add(new mapvthree.PathTracker());
tracker.track = routeCoordinates;
tracker.object = vehicle;
tracker.start({ duration: 30000, range: 200, pitch: 45 });
```
