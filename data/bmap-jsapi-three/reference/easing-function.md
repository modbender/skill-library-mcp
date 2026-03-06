# EasingFunction 缓动函数

## 概述

EasingFunction 提供三个预定义的缓动函数常量，用于 Tracker 动画中控制时间值映射。

## 导出的缓动函数

| 常量 | 说明 | 公式 |
|------|------|------|
| `EasingFunction.LINEAR` | 线性（匀速） | `t => t` |
| `EasingFunction.QUINTIC_IN_OUT` | 五次缓入缓出 | 五次多项式对称缓动 |
| `EasingFunction.CUBIC_OUT` | 三次缓出 | `(--t) * t * t + 1` |

## 基础用法

```javascript
// 直接引用常量作为缓动函数
tracker.start({
    duration: 5000,
    easing: mapvthree.EasingFunction.CUBIC_OUT
});

// 所有缓动函数接收 t(0-1)，返回缓动后的值(0-1)
const value = mapvthree.EasingFunction.LINEAR(0.5);        // 0.5
const value2 = mapvthree.EasingFunction.CUBIC_OUT(0.5);    // 0.875
```

## TrackerAbstract 内置缓动字符串

TrackerAbstract 的 `start()` 方法另外支持以下字符串形式的缓动：

| 字符串 | 说明 | 公式 |
|--------|------|------|
| `'linear'` | 线性 | `t => t` |
| `'ease-in'` | 缓入（二次） | `t => t * t` |
| `'ease-out'` | 缓出 | `t => t * (2 - t)` |
| `'ease-in-out'` | 缓入缓出 | 分段二次函数 |

```javascript
// 使用字符串形式
tracker.start({
    duration: 5000,
    easing: 'ease-in-out'
});

// 使用自定义函数
tracker.start({
    duration: 5000,
    easing: (t) => t * t * t  // 自定义三次方缓动
});
```

## 自定义缓动函数

```javascript
// 缓动函数签名：接收 0-1 的时间值，返回 0-1 的缓动值
function customEasing(t) {
    return t * t * (3 - 2 * t);  // smoothstep
}

tracker.start({
    duration: 3000,
    easing: customEasing
});
```
