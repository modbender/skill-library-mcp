# JSONDataSource 使用指南

## 概述

JSONDataSource 是 Mapv-three 中处理通用 JSON 格式数据的类。继承自 GeoJSONDataSource，支持自定义坐标字段和解析函数，适用于非标准格式的地理数据。

## 核心特性

- 支持任意结构的 JSON 数据
- 自定义坐标字段映射
- 自定义解析函数
- 适用于 API 返回的非标准格式数据

## 静态方法

### fromJSON()

从 JSON 对象创建数据源。

```javascript
const data = mapvthree.JSONDataSource.fromJSON(jsonArray, options);
```

**参数：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `json` | array | - | JSON 对象数组 |
| `options` | object | `{}` | 配置选项 |

**options 配置：**

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `coordinatesKey` | string | `'coordinates'` | 坐标字段名 |
| `parseCoordinates` | Function | - | 自定义坐标解析函数 |
| `parseFeature` | Function | - | 自定义特征解析函数 |

**返回值：** `JSONDataSource` 实例

### fromURL()

从 URL 加载 JSON 数据。

```javascript
const data = await mapvthree.JSONDataSource.fromURL('path/to/data.json', options);
```

**参数：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `url` | string | - | JSON 文件 URL |
| `options` | object | `{}` | 配置选项（同 fromJSON） |

**返回值：** `Promise<JSONDataSource>`

## 构造参数

继承自 GeoJSONDataSource。

## 基础用法

### 使用 coordinatesKey

```javascript
const jsonData = [
    { lng: 116.39, lat: 39.9, name: '北京', value: 100 },
    { lng: 121.47, lat: 31.23, name: '上海', value: 90 },
    { lng: 113.26, lat: 23.13, name: '广州', value: 80 }
];

const data = mapvthree.JSONDataSource.fromJSON(jsonData, {
    coordinatesKey: 'coordinates'  // 假设数据中有 coordinates 字段
});
```

### 使用 parseCoordinates 函数

```javascript
const jsonData = [
    { longitude: 116.39, latitude: 39.9, name: '北京', value: 100 },
    { longitude: 121.47, latitude: 31.23, name: '上海', value: 90 }
];

const data = mapvthree.JSONDataSource.fromJSON(jsonData, {
    parseCoordinates: (item) => ({
        type: 'Point',
        coordinates: [item.longitude, item.latitude]
    })
});
```

### 使用 parseFeature 函数（完全自定义）

```javascript
const jsonData = [
    { x: 116.39, y: 39.9, title: '北京', score: 100 },
    { x: 121.47, y: 31.23, title: '上海', score: 90 }
];

const data = mapvthree.JSONDataSource.fromJSON(jsonData, {
    parseFeature: (item) => ({
        type: 'Feature',
        geometry: {
            type: 'Point',
            coordinates: [item.x, item.y]
        },
        properties: {
            name: item.title,
            value: item.score
        }
    })
});
```

### 从 URL 加载

```javascript
// 加载本地文件
const data = await mapvthree.JSONDataSource.fromURL('./data/cities.json', {
    parseCoordinates: (item) => ({
        type: 'Point',
        coordinates: [item.lng, item.lat]
    })
});

// 加载 API 数据
const data = await mapvthree.JSONDataSource.fromURL('https://api.example.com/points', {
    parseCoordinates: (item) => ({
        type: 'Point',
        coordinates: [item.location.longitude, item.location.latitude]
    })
});
```

## 数据属性映射

### 基础映射

```javascript
data.defineAttributes({
    color: 'fillColor',
    size: 'sizeField',
    height: (attrs) => attrs.floor * 3
});
```

### 条件映射

```javascript
data.defineAttributes({
    color: (attrs) => {
        if (attrs.value > 100) return [255, 0, 0];
        if (attrs.value > 50) return [255, 128, 0];
        return [0, 255, 0];
    }
});
```

## 实际应用示例

### API 数据可视化

```javascript
// 假设 API 返回的数据格式
// [{ position: { lng: 116.39, lat: 39.9 }, info: { name: '北京', level: 1 } }, ...]

const apiData = await mapvthree.JSONDataSource.fromURL('https://api.example.com/locations', {
    parseCoordinates: (item) => ({
        type: 'Point',
        coordinates: [item.position.lng, item.position.lat]
    }),
    parseFeature: (item) => ({
        type: 'Feature',
        geometry: {
            type: 'Point',
            coordinates: [item.position.lng, item.position.lat]
        },
        properties: {
            name: item.info.name,
            level: item.info.level
        }
    })
});

const points = engine.add(new mapvthree.SimplePoint({
    vertexColors: true,
    vertexSizes: true
}));

apiData.defineAttributes({
    color: (attrs) => {
        return attrs.level === 1 ? [255, 0, 0] :
               attrs.level === 2 ? [255, 128, 0] :
               [0, 255, 0];
    },
    size: (attrs) => (4 - attrs.level) * 5
});

points.dataSource = apiData;
```

### 嵌套数据结构

```javascript
const nestedData = [
    {
        location: {
            coordinates: { longitude: 116.39, latitude: 39.9 }
        },
        attributes: {
            basic: { name: '北京', type: 'city' },
            stats: { population: 21540000, gdp: 36102 }
        }
    }
];

const data = mapvthree.JSONDataSource.fromJSON(nestedData, {
    parseFeature: (item) => ({
        type: 'Feature',
        geometry: {
            type: 'Point',
            coordinates: [
                item.location.coordinates.longitude,
                item.location.coordinates.latitude
            ]
        },
        properties: {
            name: item.attributes.basic.name,
            type: item.attributes.basic.type,
            population: item.attributes.stats.population,
            gdp: item.attributes.stats.gdp
        }
    })
});
```

### 线数据解析

```javascript
const lineData = [
    {
        pathId: 'route-1',
        points: [
            { lng: 116.39, lat: 39.9 },
            { lng: 116.40, lat: 39.91 },
            { lng: 116.41, lat: 39.92 }
        ],
        color: '#ff0000',
        width: 5
    }
];

const data = mapvthree.JSONDataSource.fromJSON(lineData, {
    parseFeature: (item) => ({
        type: 'Feature',
        geometry: {
            type: 'LineString',
            coordinates: item.points.map(p => [p.lng, p.lat])
        },
        properties: {
            id: item.pathId,
            color: item.color,
            width: item.width
        }
    })
});
```

### 面数据解析

```javascript
const areaData = [
    {
        areaId: 'zone-1',
        boundary: [
            { x: 116.38, y: 39.88 },
            { x: 116.42, y: 39.88 },
            { x: 116.42, y: 39.92 },
            { x: 116.38, y: 39.92 },
            { x: 116.38, y: 39.88 }  // 闭合
        ],
        fill: 'rgba(255, 0, 0, 0.5)'
    }
];

const data = mapvthree.JSONDataSource.fromJSON(areaData, {
    parseFeature: (item) => ({
        type: 'Feature',
        geometry: {
            type: 'Polygon',
            coordinates: [item.boundary.map(p => [p.x, p.y])]
        },
        properties: {
            id: item.areaId,
            fill: item.fill
        }
    })
});
```

## 高级功能

### 结合 TypeScript 类型

```typescript
interface ApiLocation {
    position: { longitude: number; latitude: number };
    info: { name: string; level: number };
}

const data = mapvthree.JSONDataSource.fromJSON<ApiLocation>(apiData, {
    parseFeature: (item: ApiLocation) => ({
        type: 'Feature',
        geometry: {
            type: 'Point',
            coordinates: [item.position.longitude, item.position.latitude]
        },
        properties: {
            name: item.info.name,
            level: item.info.level
        }
    })
});
```

### 动态数据更新

```javascript
let data = await mapvthree.JSONDataSource.fromURL('./data/realtime.json', {
    parseCoordinates: (item) => ({
        type: 'Point',
        coordinates: [item.lng, item.lat]
    })
});

const points = engine.add(new mapvthree.SimplePoint());
points.dataSource = data;

// 定时更新
setInterval(async () => {
    const updated = await mapvthree.JSONDataSource.fromURL('./data/realtime.json', {
        parseCoordinates: (item) => ({
            type: 'Point',
            coordinates: [item.lng, item.lat]
        })
    });
    data.setData(updated.data);
}, 5000);
```

### 错误处理

```javascript
try {
    const data = await mapvthree.JSONDataSource.fromURL('./data/invalid.json', {
        parseCoordinates: (item) => {
            // 验证数据
            if (!item.lng || !item.lat) {
                console.warn('无效的坐标:', item);
                return null;
            }
            return {
                type: 'Point',
                coordinates: [item.lng, item.lat]
            };
        }
    });
} catch (error) {
    console.error('数据加载失败:', error);
}
```

## 注意事项

1. **坐标格式**
   - 参考 [DataSource 坐标系统](../datasource.md#坐标系统) 了解坐标格式规范
   - 解析函数返回的 coordinates 必须是 `[lng, lat]` 或 `[lng, lat, alt]` 格式
   - 坐标值必须是数字类型

2. **parseCoordinates vs parseFeature**
   - `parseCoordinates`：仅处理坐标，properties 自动从原始数据复制
   - `parseFeature`：完全控制 Feature 结构，包括 properties

3. **性能优化**
   - `parseFeature` 函数中避免复杂计算
   - 大数据集考虑使用 `parseCoordinates` 而非 `parseFeature`

4. **数据验证**
   - 在解析函数中验证数据有效性
   - 返回 `null` 可跳过无效数据

5. **类型转换**
   - 字符串坐标需要转换：`parseFloat(item.lng)`
   - 日期字符串需要解析：`new Date(item.time)`

## 常见问题

**Q: 数据没有显示？**
- 检查解析函数返回的坐标格式
- 确认坐标值范围是否正确
- 验证数据已成功绑定到图层

**Q: 如何处理缺失的字段？**
```javascript
parseFeature: (item) => ({
    type: 'Feature',
    geometry: { ... },
    properties: {
        name: item.name || '未命名',
        value: item.value ?? 0
    }
})
```

**Q: 如何解析嵌套的坐标数组？**
```javascript
parseCoordinates: (item) => ({
    type: 'LineString',
    coordinates: item.path.map(p => [p.lng, p.lat])
})
```

**Q: 从 URL 加载时如何传递请求头？**
```javascript
const data = await mapvthree.JSONDataSource.fromURL('https://api.example.com/data', {}, {
    headers: {
        'Authorization': 'Bearer token',
        'Accept': 'application/json'
    }
});
```
