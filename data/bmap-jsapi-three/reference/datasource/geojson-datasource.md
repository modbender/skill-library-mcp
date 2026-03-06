# GeoJSONDataSource 使用指南

## 概述

GeoJSONDataSource 是 Mapv-three 中处理标准 GeoJSON 格式数据的专用类。继承自 DataSource，提供 GeoJSON 格式的解析和转换功能，是处理地理可视化数据的首选方式。

## 核心特性

- 支持标准 GeoJSON FeatureCollection 格式
- 支持所有 GeoJSON 几何类型（Point、LineString、Polygon 等）
- 静态工厂方法简化创建流程
- 自动解析 coordinates 和 properties

## 支持的几何类型

| 几何类型 | 说明 | 坐标格式 |
|----------|------|----------|
| `Point` | 点 | `[lng, lat]` 或 `[lng, lat, alt]` |
| `MultiPoint` | 多点 | `[[lng, lat], ...]` |
| `LineString` | 线 | `[[lng, lat], ...]` |
| `MultiLineString` | 多线 | `[[[lng, lat], ...], ...]` |
| `Polygon` | 多边形 | `[[[lng, lat], ...]]`（必须闭合） |
| `MultiPolygon` | 多多边形 | `[[[[lng, lat], ...]], ...]` |

## 静态方法

### fromGeoJSON()

从 GeoJSON 对象创建数据源。

```javascript
const data = mapvthree.GeoJSONDataSource.fromGeoJSON(geojsonObject);
```

**参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `geojson` | object | GeoJSON 对象（Feature 或 FeatureCollection） |

**返回值：** `GeoJSONDataSource` 实例

### fromURL()

从 URL 加载 GeoJSON 数据。

```javascript
const data = await mapvthree.GeoJSONDataSource.fromURL('path/to/data.geojson');
```

**参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `url` | string | GeoJSON 文件 URL |
| `options` | object | 可选的 fetch 选项 |

**返回值：** `Promise<GeoJSONDataSource>`

## 构造参数

继承自 DataSource，无额外构造参数。

```javascript
const data = new mapvthree.GeoJSONDataSource({
    id: 'my-geojson-datasource'
});
```

## 基础用法

### 从 GeoJSON 对象创建

```javascript
// 单个 Feature
const pointData = mapvthree.GeoJSONDataSource.fromGeoJSON({
    type: 'Feature',
    geometry: {
        type: 'Point',
        coordinates: [116.39, 39.9]
    },
    properties: {
        name: '北京',
        value: 100
    }
});

// FeatureCollection
const collectionData = mapvthree.GeoJSONDataSource.fromGeoJSON({
    type: 'FeatureCollection',
    features: [
        {
            type: 'Feature',
            geometry: { type: 'Point', coordinates: [116.39, 39.9] },
            properties: { name: '北京', value: 100 }
        },
        {
            type: 'Feature',
            geometry: { type: 'Point', coordinates: [121.47, 31.23] },
            properties: { name: '上海', value: 90 }
        }
    ]
});
```

### 从 URL 加载

```javascript
// 异步加载
const data = await mapvthree.GeoJSONDataSource.fromURL('./data/cities.geojson');

// 带选项的加载
const data = await mapvthree.GeoJSONDataSource.fromURL('./data/cities.geojson', {
    method: 'GET',
    headers: {
        'Authorization': 'Bearer token'
    }
});
```

### 绑定到可视化组件

```javascript
// 点数据
const points = engine.add(new mapvthree.SimplePoint({
    vertexColors: true,
    vertexSizes: true
}));
points.dataSource = pointData;

// 线数据
const lines = engine.add(new mapvthree.SimpleLine({
    color: '#ff0000'
}));
lines.dataSource = lineData;

// 面数据
const polygons = engine.add(new mapvthree.Polygon({
    color: '#00ff00',
    opacity: 0.6
}));
polygons.dataSource = polygonData;
```

## 数据属性映射

### 基础映射

```javascript
data.defineAttributes({
    // 直接映射字段名
    color: 'fillColor',
    size: 'sizeField',

    // 函数映射
    height: (attrs) => attrs.floor * 3,
    opacity: (attrs) => attrs.value / 100
});
```

### 条件颜色映射

```javascript
data.defineAttributes({
    color: (attrs) => {
        const value = attrs.value;
        if (value > 100) return [255, 0, 0];      // 红色
        if (value > 50) return [255, 128, 0];    // 橙色
        return [0, 255, 0];                      // 绿色
    }
});
```

### 复杂逻辑映射

```javascript
data.defineAttributes({
    color: (attrs) => {
        switch (attrs.type) {
            case 'important': return [255, 0, 0];
            case 'normal': return [0, 255, 0];
            case 'warning': return [255, 255, 0];
            default: return [128, 128, 128];
        }
    },
    size: (attrs) => {
        return Math.max(5, Math.min(50, attrs.value / 2));
    }
});
```

## 实际应用示例

### 城市点位可视化

```javascript
const cities = await mapvthree.GeoJSONDataSource.fromURL('./data/cities.geojson');

cities.defineAttributes({
    color: (attrs) => {
        const pop = attrs.population;
        if (pop > 10000000) return [255, 0, 0];
        if (pop > 5000000) return [255, 128, 0];
        return [0, 255, 0];
    },
    size: (attrs) => Math.sqrt(attrs.population) / 100
});

const points = engine.add(new mapvthree.SimplePoint({
    vertexColors: true,
    vertexSizes: true
}));
points.dataSource = cities;
```

### 区域多边形填充

```javascript
const districts = await mapvthree.GeoJSONDataSource.fromURL('./data/districts.geojson');

districts.defineAttributes({
    color: (attrs) => {
        return attrs.density > 5000 ? [255, 0, 0, 200] :
               attrs.density > 2000 ? [255, 128, 0, 200] :
               [0, 255, 0, 200];
    },
    height: (attrs) => attrs.avgFloor * 3
});

const polygons = engine.add(new mapvthree.Polygon({
    vertexColors: true,
    extrude: true,
    vertexHeights: true
}));
polygons.dataSource = districts;
```

### 路径线绘制

```javascript
const routes = await mapvthree.GeoJSONDataSource.fromURL('./data/routes.geojson');

routes.defineAttributes({
    color: (attrs) => {
        return attrs.congestion === 'high' ? [255, 0, 0] :
               attrs.congestion === 'medium' ? [255, 255, 0] :
               [0, 255, 0];
    }
});

const lines = engine.add(new mapvthree.SimpleLine({
    vertexColors: true
}));
lines.dataSource = routes;
```

### 多类型几何数据

```javascript
const mixedData = mapvthree.GeoJSONDataSource.fromGeoJSON({
    type: 'FeatureCollection',
    features: [
        {
            type: 'Feature',
            geometry: { type: 'Point', coordinates: [116.39, 39.9] },
            properties: { type: 'poi', name: '地标' }
        },
        {
            type: 'Feature',
            geometry: {
                type: 'LineString',
                coordinates: [[116.39, 39.9], [116.40, 39.91]]
            },
            properties: { type: 'road', name: '道路' }
        },
        {
            type: 'Feature',
            geometry: {
                type: 'Polygon',
                coordinates: [[[116.38, 39.88], [116.42, 39.88], [116.42, 39.92], [116.38, 39.92], [116.38, 39.88]]]
            },
            properties: { type: 'area', name: '区域' }
        }
    ]
});

// 分别创建图层
const points = engine.add(new mapvthree.SimplePoint());
const lines = engine.add(new mapvthree.SimpleLine());
const polygons = engine.add(new mapvthree.Polygon());

// 使用过滤器绑定不同类型
points.dataSource = mixedData;
points.dataSource.setFilter((item) => item.geometry.type === 'Point');

lines.dataSource = mixedData;
lines.dataSource.setFilter((item) => item.geometry.type === 'LineString');

polygons.dataSource = mixedData;
polygons.dataSource.setFilter((item) => item.geometry.type === 'Polygon');
```

## 高级功能

### 动态更新 GeoJSON 数据

```javascript
// 初始加载
let data = await mapvthree.GeoJSONDataSource.fromURL('./data/realtime.geojson');

const points = engine.add(new mapvthree.SimplePoint({
    vertexColors: true
}));
points.dataSource = data;

// 定时更新
setInterval(async () => {
    const updatedData = await mapvthree.GeoJSONDataSource.fromURL('./data/realtime.geojson');
    data.setData(updatedData.data);
}, 5000);
```

### 结合 Popup 显示信息

```javascript
const data = await mapvthree.GeoJSONDataSource.fromURL('./data/pois.geojson');

const points = engine.add(new mapvthree.SimplePoint({
    size: 10,
    color: '#ff0000'
}));
points.dataSource = data;

// 点击显示 Popup
points.addEventListener('click', (e) => {
    const dataItem = data.getDataItem(e.index);
    const props = dataItem.properties;

    const popup = new mapvthree.Popup({
        point: dataItem.geometry.coordinates,
        title: props.name,
        content: `地址: ${props.address}<br>类型: ${props.type}`
    });

    engine.add(popup);
});
```

### 数据导出

```javascript
const data = await mapvthree.GeoJSONDataSource.fromURL('./data/original.geojson');

// 修改数据
data.setAttributeValues('feature-1', { value: 200 });

// 导出修改后的数据
const modifiedGeoJSON = data.exportToGeoJSON();
console.log(JSON.stringify(modifiedGeoJSON, null, 2));

// 或保存为文件
const blob = new Blob([JSON.stringify(modifiedGeoJSON)], { type: 'application/json' });
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'modified-data.geojson';
a.click();
```

## 注意事项

1. **坐标格式**
   - 参考 [DataSource 坐标系统](../datasource.md#坐标系统) 了解坐标格式规范
   - GeoJSON 格式遵循 RFC 7946，坐标为 [lng, lat] 或 [lng, lat, alt]
   - Polygon 坐标必须闭合（首尾坐标相同）

2. **多边形坐标系**
   - Polygon 坐标数组必须是三维嵌套：`[[[lng, lat], ...]]`
   - MultiPolygon 是四维嵌套：`[[[[lng, lat], ...]], ...]`
   - 右手定则：外环逆时针，内环顺时针

3. **性能优化**
   - 大数据集考虑使用 `setFilter` 过滤
   - 复杂的属性映射函数会影响性能
   - 使用 `fromURL` 时考虑服务端数据压缩

4. **数据唯一性**
   - GeoJSON Feature 的 `id` 字段会被用作数据项 ID
   - 没有 `id` 时会自动生成

5. **投影转换**
   - 默认使用 EPSG:4326 (WGS84)
   - 如需其他投影，使用 `setCoordinates` 方法指定

## 常见问题

**Q: Polygon 没有显示？**
- 检查坐标是否闭合（首尾相同）
- 检查坐标数组嵌套层级（Polygon 是三层）
- 确认坐标范围是否在视野内

**Q: 属性映射返回的颜色不正确？**
- 颜色数组格式：`[R, G, B]` 或 `[R, G, B, A]`
- 值范围 0-255，不是 0-1
- 确保 `vertexColors: true` 已启用

**Q: 如何处理带孔洞的多边形？**
```javascript
{
    type: 'Polygon',
    coordinates: [
        // 外环（逆时针）
        [[116.38, 39.88], [116.42, 39.88], [116.42, 39.92], [116.38, 39.92], [116.38, 39.88]],
        // 内环/孔洞（顺时针）
        [[116.39, 39.89], [116.41, 39.89], [116.41, 39.91], [116.39, 39.91], [116.39, 39.89]]
    ]
}
```

**Q: 如何合并多个 GeoJSON 文件？**
```javascript
const geojson1 = await fetch('./data1.geojson').then(r => r.json());
const geojson2 = await fetch('./data2.geojson').then(r => r.json());

const merged = {
    type: 'FeatureCollection',
    features: [...geojson1.features, ...geojson2.features]
};

const data = mapvthree.GeoJSONDataSource.fromGeoJSON(merged);
```
