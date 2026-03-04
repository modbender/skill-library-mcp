# Polyline 折线

支持普通折线和贴地折线两种渲染模式，通过 `flat` 参数控制。普通模式为屏幕空间线，贴地模式为 XY 平面拉伸线。

## 基础用法

```javascript
// 普通折线（屏幕空间）
const polyline = engine.add(new mapvthree.Polyline({
    flat: false,
    color: 0xff0000,
    lineWidth: 4
}));

const data = mapvthree.GeoJSONDataSource.fromGeoJSON([{
    type: 'Feature',
    geometry: {
        type: 'LineString',
        coordinates: [[116.404, 39.915], [116.405, 39.920], [116.406, 39.918]]
    }
}]);
polyline.dataSource = data;
```

```javascript
// 贴地折线（XY平面拉伸）
const fatLine = engine.add(new mapvthree.Polyline({
    flat: true,
    color: 0x00ff00,
    lineWidth: 5
}));
fatLine.dataSource = data;
```

## 两种模式对比

| 特性 | 普通模式 (flat: false) | 贴地模式 (flat: true) |
|------|----------------------|---------------------|
| 渲染方式 | 屏幕空间线条 | XY 平面拉伸宽线 |
| 适用场景 | 道路、轨迹、边界线 | 地面标线、管线、河流 |

## 构造参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `flat` | boolean | `false` | 是否贴地模式 |
| `color` | string/number | `'#00ffff'` | 线条颜色 |
| `lineWidth` | number | `4` | 线条宽度 |
| `height` | number | - | 线条高度 |
| `opacity` | number | `1` | 透明度（0-1） |
| `alphaTest` | number | `0` | 透明度测试阈值 |
| `vertexColors` | boolean | - | 是否使用顶点颜色 |
| `emissive` | string | - | 自发光颜色 |
| `map` | string | - | 纹理贴图路径 |
| `isCurve` | boolean | `false` | 是否自动生成贝塞尔曲线 |

### 虚线参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `dashed` | boolean | `false` | 是否渲染虚线 |
| `dashArray` | number | `20` | 每段虚线（实心+空心）的长度 |
| `dashOffset` | number | `0` | 虚线起始偏移 |
| `dashRatio` | number | `0.5` | 实心部分占每段长度的比例 |

## 样式配置

### 虚线

```javascript
const dashedLine = engine.add(new mapvthree.Polyline({
    lineWidth: 4,
    color: '#ffff00',
    dashed: true,
    dashArray: 20,
    dashRatio: 0.5,
    dashOffset: 0
}));
```

### 贝塞尔曲线

```javascript
const curveLine = engine.add(new mapvthree.Polyline({
    lineWidth: 4,
    color: '#ff00ff',
    isCurve: true
}));
```

## 虚线流动动画

通过持续修改 `dashOffset` 实现流动效果：

```javascript
const line = engine.add(new mapvthree.Polyline({
    lineWidth: 4,
    dashed: true,
    dashArray: 20,
    dashRatio: 0.5
}));

let offset = 0;
function animate() {
    offset += 0.5;
    line.dashOffset = offset;
    requestAnimationFrame(animate);
}
animate();
```

## 属性修改

Polyline 使用属性代理模式：

```javascript
polyline.color = '#ff0000';
polyline.lineWidth = 6;
polyline.opacity = 0.8;
polyline.dashOffset = 10;
```

## 数据属性映射

```javascript
data.defineAttribute('color', 'strokeColor');  // 需 vertexColors: true
```
