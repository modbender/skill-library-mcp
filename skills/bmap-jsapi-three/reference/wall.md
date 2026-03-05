# Wall 墙体

沿线路创建垂直墙面的组件，支持颜色、纹理和多种动画效果。适用于围栏、边界线、区域分隔等场景。

## 基础用法

```javascript
const wall = engine.add(new mapvthree.Wall({
    height: 200,
    color: '#00ffff',
    opacity: 0.8
}));

const data = mapvthree.GeoJSONDataSource.fromGeoJSON([{
    type: 'Feature',
    geometry: {
        type: 'LineString',
        coordinates: [[116.404, 39.915], [116.405, 39.920], [116.406, 39.918]]
    }
}]);
wall.dataSource = data;
```

## 构造参数

### 基础参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `height` | number | `100` | 墙体高度（米） |
| `color` | string | `'#00ffff'` | 墙体颜色 |
| `emissive` | string/array | `[0,0,0]` | 自发光颜色 |
| `opacity` | number | `1` | 整体透明度 |
| `minOpacity` | number | `0` | 最低透明度（渐变效果） |
| `maxOpacity` | number | `1` | 最高透明度 |
| `transparent` | boolean | - | 启用透明度 |
| `depthWrite` | boolean | - | 深度写入 |
| `vertexColors` | boolean | `false` | 使用顶点颜色 |
| `vertexHeights` | boolean | `false` | 使用顶点高度 |

### 纹理参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `map` | string | - | 纹理贴图路径 |
| `mapScale` | number/array | `1` | 纹理缩放系数 |

### 动画参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enableAnimation` | boolean | `false` | 启用动画 |
| `animationSpeed` | number | `1` | 动画速度倍数 |
| `animationTailType` | number | `3` | 动画类型（见下表） |
| `animationTailRatio` | number | `0.2` | 比例拖尾长度比（type=1） |
| `animationTailLength` | number | `100` | 固定拖尾长度（type=2） |
| `animationIdle` | number | `1000` | 动画间隔（毫秒） |
| `animationRatio` | number | `0.5` | 条纹实线占比（type=4） |
| `animationBales` | number | `5` | 条纹组数（type=4） |

**animationTailType 可选值：**

| 值 | 说明 |
|---|------|
| `1` | 按比例拖尾 |
| `2` | 固定长度拖尾 |
| `3` | 垂直方向动画 |
| `4` | 条纹上升动画 |

## 示例：动画围栏

```javascript
const fence = engine.add(new mapvthree.Wall({
    height: 150,
    color: '#00ffff',
    opacity: 0.8,
    transparent: true,
    depthWrite: false,
    enableAnimation: true,
    animationTailType: 3,
    animationSpeed: 1
}));
```

## 数据属性映射

```javascript
data.defineAttribute('color', 'wallColor');   // 需 vertexColors: true
data.defineAttribute('height', 'wallHeight'); // 需 vertexHeights: true
```

## 属性修改

Wall 使用属性代理模式：

```javascript
wall.height = 300;
wall.color = '#ff0000';
wall.opacity = 0.6;
```
