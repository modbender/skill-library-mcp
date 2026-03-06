# 标记点类型

MapV Three 提供多种标记点类型，适应不同的可视化场景。

## 类型对比

| 类型 | 渲染方式 | 适用场景 |
|------|----------|----------|
| SimplePoint | WebGL 实例化 | 大量简单圆点 |
| Circle | WebGL 屏幕空间 | 范围标注 |
| Icon | WebGL 纹理贴片 | 图标标记、POI |
| BallonPoint | WebGL 实例化 | 气泡样式数据点 |
| DOMPoint | DOM 叠加 | 自定义 HTML 交互 |
| EffectModelPoint | WebGL 3D 模型 | 模型+动画标记 |
| Label | WebGL SDF 文本 | 批量文本/图标标签 |
| ClusterPoint | WebGL 聚合 | 大量同类点聚合 |

---

## Icon - 图标标记

WebGL 渲染的图标点组件，支持自定义图片、固定像素大小、贴地、跳动动画等。

### 基础用法

```javascript
const icon = engine.add(new mapvthree.Icon({
    mapSrc: 'assets/icons/marker.png',
    width: 32,
    height: 32,
    keepSize: true,
    vertexIcons: true
}));

const data = mapvthree.GeoJSONDataSource.fromGeoJSON(pointData);
data.defineAttribute('icon', 'icon');
icon.dataSource = data;
```

### Icon 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `mapSrc` | string | - | 图标图片 URL |
| `vertexIcons` | boolean | `false` | 数据中携带 icon URL |
| `vertexColors` | boolean | `false` | 数据中携带颜色 |
| `width` | number | `12` | 宽度（像素） |
| `height` | number | `12` | 高度（像素） |
| `offset` | array | `[0, 0]` | 偏移 `[x, y]`（像素） |
| `opacity` | number | `1` | 透明度 |
| `keepSize` | boolean | `true` | 保持固定像素大小 |
| `flat` | boolean | `false` | 贴地显示 |
| `color` | string | - | 图标颜色 |
| `rotateZ` | number | `0` | 旋转角度（弧度），仅 flat 模式 |
| `animationJump` | boolean | `false` | 跳动动画 |
| `jumpHeight` | number | `20` | 跳动高度 |
| `jumpSpeed` | number | `1` | 跳动速度 |

### 数据属性映射

```javascript
data.defineAttribute('icon', 'icon');       // 需 vertexIcons: true
data.defineAttribute('iconSize', 'size');   // [width, height]
data.defineAttribute('offset', 'offset');
```

---

## BallonPoint - 气泡点

实例化渲染的气泡样式点组件，适用于数据可视化中的标记。

### 基础用法

```javascript
const ballon = engine.add(new mapvthree.BallonPoint({
    color: 0xff0000,
    size: 20,
    height: 100,
    iconSrc: 'car'
}));

ballon.dataSource = mapvthree.GeoJSONDataSource.fromGeoJSON(pointData);
```

### BallonPoint 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `iconSrc` | string | `'car'` | 气泡图标源 |
| `color` | number/string | - | 气泡颜色 |
| `size` | number | - | 气泡大小 |
| `size3` | array | - | 三维大小 `[x, y, z]` |
| `height` | number | - | 气泡高度 |
| `opacity` | number | - | 透明度 |
| `dashed` | boolean | - | 虚线样式 |

### 属性修改

BallonPoint 使用属性代理模式：

```javascript
ballon.color = 0x00ff00;
ballon.size = 30;
ballon.height = 200;
```

---

## DOMPoint - DOM 元素点

在地图上叠加自定义 DOM 元素，通过 `renderItem` 回调函数自定义每个点的 HTML 内容。

### 基础用法

```javascript
const domPoint = engine.add(new mapvthree.DOMPoint({
    offset: [-50, -50]
}));

// 自定义渲染函数
domPoint.renderItem = (value) => {
    const node = document.createElement('div');
    node.className = 'custom-point';
    node.innerHTML = `
        <div class="title">${value.attributes.name}</div>
        <div class="content">${value.attributes.description}</div>
    `;
    return node;
};

domPoint.dataSource = mapvthree.GeoJSONDataSource.fromGeoJSON([{
    type: 'Feature',
    geometry: { type: 'Point', coordinates: [116.404, 39.915] },
    properties: { name: '位置1', description: '描述信息' }
}]);
```

### DOMPoint 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `offset` | array | `[0, 0]` | 偏移 `[x, y]`（像素） |

### renderItem 回调

通过覆盖 `renderItem` 方法自定义 DOM 内容。参数为数据源中的数据项对象，返回 HTMLElement。

---

## EffectModelPoint - 模型特效点

加载 3D 模型作为点标记，支持旋转和跳跃动画。默认加载内置钻石模型。

> 动画效果需要设置 `rendering.enableAnimationLoop = true`。

### 基础用法

```javascript
const modelPoint = engine.add(new mapvthree.EffectModelPoint({
    normalize: true,
    rotateToZUp: true,
    keepSize: true,
    animationRotate: true,
    animationJump: true,
    animationJumpHeight: 100
}));

// 设置自定义模型（可选，默认使用内置钻石模型）
// modelPoint.model = gltfScene;
modelPoint.size = 30;

modelPoint.dataSource = mapvthree.GeoJSONDataSource.fromGeoJSON(pointData);
```

### EffectModelPoint 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `normalize` | boolean | `true` | 归一化模型大小 |
| `rotateToZUp` | boolean | `true` | 将模型调整至 Z 轴朝上 |
| `keepSize` | boolean | `true` | 保持固定大小 |
| `size` | number | `1` | 模型大小 |
| `size3` | array | `[1, 1, 1]` | 三维大小 `[x, y, z]` |
| `height` | number | `0` | 高度偏移 |
| `animationRotate` | boolean | `false` | 旋转动画 |
| `animationRotatePeriod` | number | `3000` | 旋转周期（毫秒） |
| `animationJump` | boolean | `false` | 跳跃动画 |
| `animationJumpPeriod` | number | `3000` | 跳跃周期（毫秒） |
| `animationJumpHeight` | number | `30` | 跳跃高度 |
| `vertexColors` | boolean | `false` | 数据中携带颜色 |
| `vertexSizes` | boolean | `false` | 数据中携带大小 |

### 设置自定义模型

```javascript
// 通过 GLTFLoader 加载
const gltf = await mapvthree.GLTFLoader.load('assets/models/marker.glb');
modelPoint.model = gltf.scene;
```
