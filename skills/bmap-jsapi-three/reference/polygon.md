# Polygon 多边形

填充多边形组件，支持 2D 平面、3D 拉伸和贴地渲染。

## 基础用法

```javascript
const polygon = engine.add(new mapvthree.Polygon({
    color: '#ff0000',
    opacity: 0.8
}));

polygon.dataSource = mapvthree.GeoJSONDataSource.fromGeoJSON([{
    type: 'Feature',
    geometry: {
        type: 'Polygon',
        coordinates: [[
            [116.404, 39.915], [116.405, 39.915],
            [116.405, 39.916], [116.404, 39.916],
            [116.404, 39.915]  // 必须闭合
        ]]
    }
}]);
```

## 3D 拉伸

```javascript
const building = engine.add(new mapvthree.Polygon({
    extrude: true,
    extrudeValue: 100,
    color: '#4488ff'
}));

// 带起始高度：从50米开始向上拉伸100米（顶部150米）
const floatingBuilding = engine.add(new mapvthree.Polygon({
    extrude: true,
    extrudeValue: 100,
    zOffset: 50,
    color: '#4488ff'
}));
```

## 贴地渲染

```javascript
const groundPolygon = engine.add(new mapvthree.Polygon({
    isGroundPrimitive: true,
    color: 'rgba(255, 0, 0, 0.5)'
}));
```

## 构造参数

### 基础参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `color` | string | `'#ffffff'` | 填充颜色 |
| `opacity` | number | `1` | 透明度 |
| `emissive` | string | `'#000000'` | 自发光颜色 |
| `vertexColors` | boolean | `false` | 使用顶点颜色 |
| `transparent` | boolean | `false` | 启用透明效果 |
| `depthWrite` | boolean | `true` | 深度写入 |
| `renderOrder` | number | `0` | 渲染顺序 |

### 拉伸参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `extrude` | boolean | `false` | 是否拉伸 |
| `extrudeValue` | number | `100` | 拉伸高度（米） |
| `enableBottomFace` | boolean | `true` | 是否封闭底面 |
| `vertexHeights` | boolean | `false` | 从数据中读取高度 |

### 高度与纹理

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `zOffset` | number | `0` | 高度抬升（米） |
| `normalOffset` | number | `0` | 沿法线方向抬升 |
| `mapSrc` | string | `''` | 纹理贴图路径 |
| `mapScale` | number | `1` | 纹理缩放 |

### 贴地与 AO

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `isGroundPrimitive` | boolean | `false` | 贴地渲染 |
| `isDynamic` | boolean | `false` | 支持动态更新（贴地时） |
| `useAO` | boolean | `false` | 环境光遮蔽 |
| `concaveIntensity` | number | `0.2` | 凹面强度 |
| `heightIntensity` | number | `0.4` | 高度强度 |
| `excludeElements` | array | `[]` | 贴地时排除的 3D 元素 |

## 数据属性映射

```javascript
const data = mapvthree.GeoJSONDataSource.fromGeoJSON(geojson);
data.defineAttribute('color', 'fillColor');          // 需 vertexColors: true
data.defineAttribute('height', 'building_height');   // 需 vertexHeights: true
polygon.dataSource = data;
```

## 属性修改

Polygon 使用属性代理模式：

```javascript
polygon.color = '#ff0000';
polygon.opacity = 0.5;
polygon.extrude = true;
polygon.extrudeValue = 200;
polygon.zOffset = 50;
```

## 示例：城市建筑

```javascript
const buildings = engine.add(new mapvthree.Polygon({
    extrude: true,
    vertexColors: true,
    enableBottomFace: false
}));

const data = await mapvthree.GeoJSONDataSource.fromURL('buildings.geojson');
data.defineAttribute('color', (attrs) => {
    switch (attrs.type) {
        case 'residential': return [200, 200, 200];
        case 'commercial': return [100, 150, 255];
        default: return [180, 180, 180];
    }
});
data.defineAttribute('height', 'building_height');
buildings.dataSource = data;
```

## 带洞多边形

GeoJSON 标准格式：第一个环为外环，后续环为洞。

```javascript
const polygonWithHole = {
    type: 'Feature',
    geometry: {
        type: 'Polygon',
        coordinates: [
            [[116.404, 39.915], [116.405, 39.915], [116.405, 39.916], [116.404, 39.916], [116.404, 39.915]],
            [[116.4042, 39.9152], [116.4048, 39.9152], [116.4048, 39.9158], [116.4042, 39.9158], [116.4042, 39.9152]]
        ]
    }
};
```

## 资源清理

```javascript
engine.remove(polygon);
polygon.dispose();
```
