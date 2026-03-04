# DataItem 数据项使用指南

## 概述

DataItem 是 Mapv-three 中表示单个地理数据元素的核心类。每个数据项包含几何信息（坐标）和属性信息，是数据源（DataSource）的基本组成单元。

## 核心特性

- 封装坐标和属性数据
- 自动生成唯一标识
- 支持动态属性修改
- 与 DataSource 无缝集成

## 构造函数

```javascript
const item = new mapvthree.DataItem(
    coordinates,    // 坐标
    properties      // 属性对象
);
```

**参数：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `coordinates` | Array | - | 坐标数组 `[lng, lat]` 或 `[lng, lat, alt]` |
| `properties` | object | `{}` | 属性对象 |

## 公共属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `id` | string | 数据项唯一标识（自动生成） |
| `geometry` | object | 几何信息对象 |
| `geometry.coordinates` | Array | 坐标数组 |
| `geometry.type` | string | 几何类型（如 'Point'） |
| `properties` | object | 原始属性数据 |
| `attributes` | object | 解析后的属性（由 DataSource 处理） |

## 基础用法

### 创建点数据项

```javascript
// 二维坐标
const point = new mapvthree.DataItem(
    [116.39, 39.9],
    { name: '北京', value: 100 }
);

// 三维坐标（带高度）
const point3D = new mapvthree.DataItem(
    [116.39, 39.9, 50],
    { name: '北京', altitude: 50 }
);
```

### 创建线数据项

```javascript
const line = new mapvthree.DataItem(
    [[116.39, 39.9], [116.40, 39.91], [116.41, 39.92]],
    { name: '路线', type: 'highway' }
);
```

### 创建面数据项

```javascript
const polygon = new mapvthree.DataItem(
    [[[116.38, 39.88], [116.42, 39.88], [116.42, 39.92], [116.38, 39.92], [116.38, 39.88]]],
    { name: '区域', area: 1000 }
);
```

### 添加到数据源

```javascript
const data = new mapvthree.DataSource();

// 添加单个
data.add(new mapvthree.DataItem([116.39, 39.9], { name: '北京' }));

// 批量添加
data.add([
    new mapvthree.DataItem([116.39, 39.9], { name: '北京', value: 100 }),
    new mapvthree.DataItem([121.47, 31.23], { name: '上海', value: 90 }),
    new mapvthree.DataItem([113.26, 23.13], { name: '广州', value: 80 })
]);
```

## 数据属性

### 基础属性

```javascript
const item = new mapvthree.DataItem(
    [116.39, 39.9],
    {
        name: '北京',
        value: 100,
        category: 'city',
        visible: true
    }
);

console.log(item.id);              // 自动生成的唯一 ID
console.log(item.properties.name); // '北京'
```

### 嵌套属性

```javascript
const item = new mapvthree.DataItem(
    [116.39, 39.9],
    {
        name: '北京',
        stats: {
            population: 21540000,
            gdp: 36102
        },
        location: {
            district: '东城区',
            address: '长安街1号'
        }
    }
);

// 在属性映射中访问
data.defineAttribute('size', (attrs) => {
    return attrs.stats.population / 1000000;
});
```

### 动态属性

```javascript
const item = new mapvthree.DataItem([116.39, 39.9], {});

// 添加新属性
item.properties.customField = 'value';

// 修改属性
item.properties.value = 200;

// 删除属性
delete item.properties.tempField;
```

## 坐标格式

### Point 坐标

```javascript
// 二维点
new mapvthree.DataItem([116.39, 39.9], {});

// 三维点
new mapvthree.DataItem([116.39, 39.9, 100], {});
```

### MultiPoint 坐标

```javascript
new mapvthree.DataItem([
    [116.39, 39.9],
    [116.40, 39.91],
    [116.41, 39.92]
], {});
```

### LineString 坐标

```javascript
new mapvthree.DataItem([
    [116.39, 39.9],
    [116.40, 39.91],
    [116.41, 39.92]
], {});
```

### Polygon 坐标

```javascript
new mapvthree.DataItem([
    [
        [116.38, 39.88],
        [116.42, 39.88],
        [116.42, 39.92],
        [116.38, 39.92],
        [116.38, 39.88]  // 必须闭合
    ]
], {});
```

## 实际应用示例

### 创建城市数据集

```javascript
const cities = [
    { name: '北京', lng: 116.39, lat: 39.9, pop: 21540000 },
    { name: '上海', lng: 121.47, lat: 31.23, pop: 24870000 },
    { name: '广州', lng: 113.26, lat: 23.13, pop: 18670000 },
    { name: '深圳', lng: 114.05, lat: 22.52, pop: 17560000 }
];

const data = new mapvthree.DataSource();

cities.forEach(city => {
    data.add(new mapvthree.DataItem(
        [city.lng, city.lat],
        {
            name: city.name,
            population: city.pop
        }
    ));
});
```

### 创建轨迹数据

```javascript
const trajectory = [
    { lng: 116.39, lat: 39.9, speed: 60, time: '10:00' },
    { lng: 116.40, lat: 39.91, speed: 55, time: '10:05' },
    { lng: 116.41, lat: 39.92, speed: 50, time: '10:10' }
];

const data = new mapvthree.DataSource();

// 创建整条轨迹
data.add(new mapvthree.DataItem(
    trajectory.map(p => [p.lng, p.lat]),
    {
        vehicleId: 'vehicle-1',
        startTime: trajectory[0].time,
        endTime: trajectory[trajectory.length - 1].time
    }
));
```

### 创建带孔多边形

```javascript
const outerRing = [
    [116.38, 39.88],
    [116.42, 39.88],
    [116.42, 39.92],
    [116.38, 39.92],
    [116.38, 39.88]
];

const innerRing = [
    [116.39, 39.89],
    [116.41, 39.89],
    [116.41, 39.91],
    [116.39, 39.91],
    [116.39, 39.89]
];

const data = new mapvthree.DataSource();

data.add(new mapvthree.DataItem(
    [outerRing, innerRing],  // 外环和内环
    {
        name: '带孔区域',
        area: 1000
    }
));
```

### 实时更新数据项

```javascript
const data = new mapvthree.DataSource();

const vehicle = new mapvthree.DataItem(
    [116.39, 39.9],
    { id: 'vehicle-1', status: 'moving' }
);

data.add(vehicle);

// 更新位置
data.setCoordinates(vehicle.id, [116.40, 39.91]);

// 更新属性
data.setAttributeValues(vehicle.id, { status: 'stopped' });
```

### 自定义 ID

```javascript
const item = new mapvthree.DataItem([116.39, 39.9], {});

// 设置自定义 ID
item.id = 'custom-id-123';

// 使用自定义 ID 进行操作
data.setAttributeValues('custom-id-123', { value: 200 });
```

## 高级功能

### 属性计算

```javascript
class ComputedDataItem extends mapvthree.DataItem {
    constructor(coordinates, properties) {
        super(coordinates, properties);
        this._computed = null;
    }

    get computedValue() {
        if (!this._computed) {
            this._computed = this.properties.baseValue * 2;
        }
        return this._computed;
    }
}

const item = new ComputedDataItem([116.39, 39.9], { baseValue: 100 });
console.log(item.computedValue);  // 200
```

### 数据验证

```javascript
function validateDataItem(item) {
    const coords = item.geometry.coordinates;

    // 验证坐标
    if (!Array.isArray(coords) || coords.length < 2) {
        console.error('无效的坐标:', item.id);
        return false;
    }

    const [lng, lat] = coords;
    if (lng < -180 || lng > 180 || lat < -90 || lat > 90) {
        console.error('坐标超出范围:', item.id);
        return false;
    }

    return true;
}

const item = new mapvthree.DataItem([116.39, 39.9], {});
if (validateDataItem(item)) {
    data.add(item);
}
```

### 数据序列化

```javascript
const item = new mapvthree.DataItem([116.39, 39.9], {
    name: '北京',
    value: 100
});

// 转换为 GeoJSON Feature
const feature = {
    type: 'Feature',
    id: item.id,
    geometry: item.geometry,
    properties: item.properties
};

console.log(JSON.stringify(feature));
```

## 注意事项

1. **坐标格式**
   - 必须是数组格式
   - Point: `[lng, lat]` 或 `[lng, lat, alt]`
   - LineString: `[[lng, lat], ...]`
   - Polygon: `[[[lng, lat], ...]]`

2. **唯一性**
   - 每个数据项自动生成唯一 ID
   - 可以手动设置自定义 ID
   - 更新和删除操作依赖 ID

3. **属性访问**
   - 原始属性通过 `properties` 访问
   - 解析后的属性通过 `attributes` 访问
   - `attributes` 由 DataSource 的属性映射生成

4. **内存管理**
   - 大量数据项时注意内存使用
   - 不再需要时从 DataSource 移除
   - 使用 `clear()` 清空整个数据源

5. **坐标闭合**
   - Polygon 坐标必须闭合（首尾相同）
   - 外环通常逆时针，内环顺时针

## 常见问题

**Q: 如何获取数据项的坐标？**
```javascript
const item = data.getDataItem(0);
const coords = item.geometry.coordinates;
```

**Q: 如何修改数据项的属性？**
```javascript
// 直接修改
item.properties.value = 200;

// 通过 DataSource 修改（推荐）
data.setAttributeValues(item.id, { value: 200 });
```

**Q: 如何复制数据项？**
```javascript
const item = data.getDataItem(0);
const copy = new mapvthree.DataItem(
    [...item.geometry.coordinates],  // 深拷贝坐标
    { ...item.properties }           // 深拷贝属性
);
```

**Q: 数据项 ID 是如何生成的？**
- 自动生成，通常是 UUID 或时间戳
- 可以手动设置：`item.id = 'custom-id'`
- ID 在数据源内必须唯一
