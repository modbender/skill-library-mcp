# SimpleLine 简单线

基础线条渲染组件，相比 Polyline 提供更轻量的 1px 线条渲染。使用 Three.js 的 LineBasicMaterial，性能最优。

## 基础用法

```javascript
const line = engine.add(new mapvthree.SimpleLine({
    color: 'rgba(250, 90, 50, 1)'
}));

const data = mapvthree.GeoJSONDataSource.fromGeoJSON([{
    type: 'Feature',
    geometry: {
        type: 'LineString',
        coordinates: [[116.404, 39.915], [116.405, 39.920]]
    }
}]);
line.dataSource = data;
```

## 构造参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `color` | string | `'#ffffff'` | 线条颜色 |
| `opacity` | number | `1` | 透明度（0-1） |
| `granularity` | number | `0.5` | 线段细分距离（度），仅 3D 模式下生效 |

## 属性修改

SimpleLine 使用属性代理模式：

```javascript
line.color = 'rgb(0, 255, 0)';
```

## 与 Polyline 的区别

| 特性 | SimpleLine | Polyline |
|------|------------|----------|
| 线宽 | 固定 1px | 可配置（像素/米） |
| 渲染方式 | LineBasicMaterial | 屏幕空间/贴地 |
| 性能 | 最优 | 较好 |
| 适用场景 | 大量细线 | 需要线宽控制 |

> WebGL 中 `linewidth` 在大多数浏览器中被限制为 1px。若需要可控线宽，使用 Polyline。
