# DataSource 数据源

## 概述

DataSource 是管理地理数据的核心抽象类。负责数据格式转换、属性映射和数据操作。

## 数据源类型

| 类型 | 说明 | 适用场景 |
|------|------|----------|
| **DataSource** | 基础抽象类 | 动态生成、实时更新 |
| **GeoJSONDataSource** | GeoJSON 格式（推荐） | 大多数地理可视化 |
| **JSONDataSource** | 通用 JSON 格式 | 非标准格式数据 |
| **CSVDataSource** | CSV 表格数据 | 点数据、表格导入 |

## 构造参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `id` | string | 自动生成时间戳 | 数据源唯一标识 |
| `attributes` | object | `{}` | 属性映射配置 |
| `coordType` | string | - | 坐标类型（用于坐标转换） |

## 公共属性

| 属性 | 类型 | 只读 | 说明 |
|------|------|------|------|
| `data` | object | 是 | 解析后的 buffer 格式数据 |
| `userData` | object[] | 是 | 解析后的 array 格式数据 |
| `size` | number | 是 | 数据项数量 |
| `dataItems` | DataItem[] | 是 | 所有数据项数组 |
| `objects` | Array | 否 | 连接的可视化对象 |
| `needsUpdate` | boolean | 否 | 是否需要更新 |

## 公共方法

### 数据加载

```javascript
await data.load('https://example.com/data.geojson');
```

### 属性映射

```javascript
// 设置单个 attribute
data.defineAttribute('color', 'fillColor');

// 批量设置（推荐）
data.defineAttributes({
    color: 'fillColor',
    size: (attrs) => attrs.value / 10
});

// 移除
data.undefineAttribute('color');
data.undefineAllAttributes();
```

### 数据操作

```javascript
// 添加
data.add(new mapvthree.DataItem([116.39, 39.9], { name: '北京' }));
data.add([item1, item2, item3]);  // 批量添加

// 移除
data.remove('featureId');
data.remove(['id1', 'id2']);

// 设置属性值
data.setAttributeValue('featureId', 'color', [255, 0, 0]);
data.setAttributeValues('featureId', { color: [255, 0, 0], size: 20 });

// 设置坐标
data.setCoordinates('featureId', [116.40, 39.91]);

// 获取
const item = data.get(0);
const dataItem = data.getDataItem(0);
```

### 数据管理

```javascript
data.exportToGeoJSON();
data.clear();
data.setFilter((dataItem, index) => dataItem.attributes.visible === true);
data.setData(newData);
data.dispose();
```

## 事件

| 事件 | 参数 | 说明 |
|------|------|------|
| `afterAdd` | `{ dataItems }` | 数据添加后触发 |
| `afterRemove` | `{ dataItems }` | 数据移除后触发 |

## DataItem 数据项

```javascript
const item = new mapvthree.DataItem(
    [116.39, 39.9],           // 坐标
    { name: '北京', value: 100 }  // 属性
);
```

| 属性 | 类型 | 说明 |
|------|------|------|
| `id` | string | 唯一标识 |
| `geometry` | object | 几何信息 |
| `properties` | object | 原始属性 |
| `attributes` | object | 解析后的属性 |

## 基础示例

```javascript
const data = new mapvthree.DataSource();

data.add([
    new mapvthree.DataItem([116.39, 39.9], { name: '北京', value: 100 }),
    new mapvthree.DataItem([121.47, 31.23], { name: '上海', value: 90 }),
]);

const points = engine.add(new mapvthree.SimplePoint({ vertexColors: true }));
points.dataSource = data;

data.defineAttributes({
    color: (attrs) => attrs.value > 90 ? [255, 0, 0] : [0, 255, 0],
    size: (attrs) => attrs.value / 10
});
```

## 实时数据更新

```javascript
const data = new mapvthree.DataSource();

// 定时更新位置
setInterval(async () => {
    const positions = await fetch('/api/positions').then(r => r.json());
    positions.forEach(pos => {
        data.setCoordinates(pos.id, [pos.lng, pos.lat]);
    });
}, 1000);
```

## 数据过滤

```javascript
data.setFilter((dataItem) => dataItem.attributes.value > 50);
data.setFilter(null);  // 清除过滤
```

## 资源清理

```javascript
data.clear();
data.dispose();
```
