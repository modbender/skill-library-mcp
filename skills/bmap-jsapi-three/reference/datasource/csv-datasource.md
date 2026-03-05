# CSVDataSource 使用指南

## 概述

CSVDataSource 是 Mapv-three 中处理 CSV 表格数据的专用类。继承自 JSONDataSource，自动解析 CSV 字符串为 JSON 对象数组，适用于从表格软件导出的地理数据。

## 核心特性

- 自动解析 CSV 格式数据
- 支持自定义分隔符
- 自动类型推断（数字转换）
- 继承 JSONDataSource 的所有解析功能

## 静态方法

### fromCSVString()

从 CSV 字符串创建数据源。

```javascript
const data = mapvthree.CSVDataSource.fromCSVString(csvString, options);
```

**参数：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `csvString` | string | - | CSV 格式字符串 |
| `options` | object | `{}` | 配置选项 |

**options 配置：**

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `delimiter` | string | `,` | 字段分隔符 |
| `header` | boolean | `true` | 首行是否为表头 |
| `parseCoordinates` | Function | - | 坐标解析函数 |
| `parseFeature` | Function | - | 特征解析函数 |

**返回值：** `CSVDataSource` 实例

### fromURL()

从 URL 加载 CSV 数据。

```javascript
const data = await mapvthree.CSVDataSource.fromURL('path/to/data.csv', options);
```

**参数：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `url` | string | - | CSV 文件 URL |
| `options` | object | `{}` | 配置选项（同 fromCSVString） |

**返回值：** `Promise<CSVDataSource>`

## 构造参数

继承自 JSONDataSource。

## 基础用法

### 从 CSV 字符串创建

```javascript
const csvString = `lng,lat,name,value
116.39,39.9,北京,100
121.47,31.23,上海,90
113.26,23.13,广州,80`;

const data = mapvthree.CSVDataSource.fromCSVString(csvString, {
    parseCoordinates: (item) => ({
        type: 'Point',
        coordinates: [parseFloat(item.lng), parseFloat(item.lat)]
    })
});
```

### 从 URL 加载

```javascript
const data = await mapvthree.CSVDataSource.fromURL('./data/cities.csv', {
    parseCoordinates: (item) => ({
        type: 'Point',
        coordinates: [parseFloat(item.lng), parseFloat(item.lat)]
    })
});
```

### 使用自定义分隔符

```javascript
const csvString = `lng;lat;name;value
116.39;39.9;北京;100
121.47;31.23;上海;90`;

const data = mapvthree.CSVDataSource.fromCSVString(csvString, {
    delimiter: ';',
    parseCoordinates: (item) => ({
        type: 'Point',
        coordinates: [parseFloat(item.lng), parseFloat(item.lat)]
    })
});
```

### 无表头 CSV

```javascript
const csvString = `116.39,39.9,北京,100
121.47,31.23,上海,90`;

const data = mapvthree.CSVDataSource.fromCSVString(csvString, {
    header: false,
    parseFeature: (item, index) => ({
        type: 'Feature',
        geometry: {
            type: 'Point',
            coordinates: [parseFloat(item.field1), parseFloat(item.field2)]
        },
        properties: {
            name: item.field3,
            value: parseFloat(item.field4)
        }
    })
});
```

## 数据属性映射

```javascript
data.defineAttributes({
    color: (attrs) => {
        const value = attrs.value;
        if (value > 90) return [255, 0, 0];
        if (value > 80) return [255, 128, 0];
        return [0, 255, 0];
    },
    size: (attrs) => attrs.value / 10
});
```

## 实际应用示例

### 城市 POI 数据

```javascript
const csvData = `longitude,latitude,name,type,rating
116.39,39.9,天安门,景点,5
116.40,39.91,故宫,景点,5
116.41,39.92,王府井,商业,4
121.47,31.23,外滩,景点,5
121.48,31.24,南京路,商业,4`;

const data = mapvthree.CSVDataSource.fromCSVString(csvData, {
    parseCoordinates: (item) => ({
        type: 'Point',
        coordinates: [parseFloat(item.longitude), parseFloat(item.latitude)]
    }),
    parseFeature: (item) => ({
        type: 'Feature',
        geometry: {
            type: 'Point',
            coordinates: [parseFloat(item.longitude), parseFloat(item.latitude)]
        },
        properties: {
            name: item.name,
            type: item.type,
            rating: parseFloat(item.rating)
        }
    })
});

data.defineAttributes({
    color: (attrs) => {
        return attrs.type === '景点' ? [255, 0, 0] : [0, 0, 255];
    },
    size: (attrs) => attrs.rating * 3
});

const points = engine.add(new mapvthree.SimplePoint({
    vertexColors: true,
    vertexSizes: true
}));
points.dataSource = data;
```

### 路径轨迹数据

```javascript
const csvData = `id,sequence,lng,lat,speed
vehicle1,1,116.39,39.9,60
vehicle1,2,116.40,39.91,55
vehicle1,3,116.41,39.92,50
vehicle2,1,121.47,31.23,70
vehicle2,2,121.48,31.24,65`;

const data = mapvthree.CSVDataSource.fromCSVString(csvData, {
    parseFeature: (item) => ({
        type: 'Feature',
        geometry: {
            type: 'Point',
            coordinates: [parseFloat(item.lng), parseFloat(item.lat)]
        },
        properties: {
            id: item.id,
            sequence: parseInt(item.sequence),
            speed: parseFloat(item.speed)
        }
    })
});

data.defineAttributes({
    color: (attrs) => {
        return attrs.speed > 60 ? [255, 0, 0] :
               attrs.speed > 40 ? [255, 255, 0] :
               [0, 255, 0];
    }
});
```

### 区域边界数据

```javascript
const csvData = `areaId,coordinates,fillColor,density
zone1,"116.38,39.88;116.42,39.88;116.42,39.92;116.38,39.92;116.38,39.88","#ff0000",5000
zone2,"121.46,31.22;121.50,31.22;121.50,31.26;121.46,31.26;121.46,31.22","#00ff00",3000`;

const data = mapvthree.CSVDataSource.fromCSVString(csvData, {
    parseFeature: (item) => {
        const coords = item.coordinates.split(';').map(p => {
            const [lng, lat] = p.split(',');
            return [parseFloat(lng), parseFloat(lat)];
        });

        return {
            type: 'Feature',
            geometry: {
                type: 'Polygon',
                coordinates: [coords]
            },
            properties: {
                id: item.areaId,
                fillColor: item.fillColor,
                density: parseFloat(item.density)
            }
        };
    }
});
```

### 多属性统计数据

```javascript
const csvData = `city,population,area,gdp,avgIncome
北京,21540000,16410,36102,75023
上海,24870000,6340,43214,79627
广州,18670000,7434,28231,68304
深圳,17560000,1997,32387,70847`;

const data = mapvthree.CSVDataSource.fromCSVString(csvData, {
    parseCoordinates: (item, index) => {
        // 需要另外提供城市坐标映射
        const cityCoords = {
            '北京': [116.39, 39.9],
            '上海': [121.47, 31.23],
            '广州': [113.26, 23.13],
            '深圳': [114.05, 22.52]
        };
        return {
            type: 'Point',
            coordinates: cityCoords[item.city] || [0, 0]
        };
    },
    parseFeature: (item) => {
        const cityCoords = {
            '北京': [116.39, 39.9],
            '上海': [121.47, 31.23],
            '广州': [113.26, 23.13],
            '深圳': [114.05, 22.52]
        };
        return {
            type: 'Feature',
            geometry: {
                type: 'Point',
                coordinates: cityCoords[item.city] || [0, 0]
            },
            properties: {
                city: item.city,
                population: parseInt(item.population),
                area: parseInt(item.area),
                gdp: parseInt(item.gdp),
                avgIncome: parseInt(item.avgIncome)
            }
        };
    }
});

data.defineAttributes({
    size: (attrs) => Math.sqrt(attrs.population) / 100,
    color: (attrs) => {
        const income = attrs.avgIncome;
        if (income > 75000) return [255, 0, 0];
        if (income > 70000) return [255, 128, 0];
        return [0, 255, 0];
    }
});
```

## 高级功能

### 动态 CSV 加载

```javascript
let data = await mapvthree.CSVDataSource.fromURL('./data/realtime.csv', {
    parseCoordinates: (item) => ({
        type: 'Point',
        coordinates: [parseFloat(item.lng), parseFloat(item.lat)]
    })
});

const points = engine.add(new mapvthree.SimplePoint());
points.dataSource = data;

// 定时刷新
setInterval(async () => {
    const updated = await mapvthree.CSVDataSource.fromURL('./data/realtime.csv', {
        parseCoordinates: (item) => ({
            type: 'Point',
            coordinates: [parseFloat(item.lng), parseFloat(item.lat)]
        })
    });
    data.setData(updated.data);
}, 10000);
```

### 数据验证与过滤

```javascript
const csvData = `lng,lat,name,value
116.39,39.9,北京,100
invalid,39.91,无效位置,50
116.41,,无效纬度,30`;

const data = mapvthree.CSVDataSource.fromCSVString(csvData, {
    parseCoordinates: (item) => {
        const lng = parseFloat(item.lng);
        const lat = parseFloat(item.lat);

        // 验证坐标有效性
        if (isNaN(lng) || isNaN(lat)) {
            console.warn('无效坐标:', item);
            return null;
        }

        return {
            type: 'Point',
            coordinates: [lng, lat]
        };
    }
});

// 过滤掉解析失败的数据
data.setFilter((dataItem) => dataItem.geometry !== null);
```

### 编码处理

```javascript
// 处理中文 CSV 文件
const data = await mapvthree.CSVDataSource.fromURL('./data/cities.csv', {
    // 从 URL 加载时会自动处理常见编码
    // 如果遇到乱码，可先使用 fetch 手动处理
    parseCoordinates: (item) => ({
        type: 'Point',
        coordinates: [parseFloat(item.lng), parseFloat(item.lat)]
    })
});

// 或者手动处理编码
const response = await fetch('./data/cities.csv');
const csvText = await response.text();
const data = mapvthree.CSVDataSource.fromCSVString(csvText, {
    parseCoordinates: (item) => ({
        type: 'Point',
        coordinates: [parseFloat(item.lng), parseFloat(item.lat)]
    })
});
```

## 注意事项

1. **坐标格式**
   - 参考 [DataSource 坐标系统](../datasource.md#坐标系统) 了解坐标格式规范
   - 坐标必须转换为数字类型：`[parseFloat(lng), parseFloat(lat)]`

2. **坐标类型转换**
   - CSV 解析后所有字段都是字符串
   - 数字字段需要使用 `parseFloat()` 或 `parseInt()` 转换

2. **表头处理**
   - 默认第一行是表头，会被用作字段名
   - 设置 `header: false` 时，字段名为 `field1`, `field2` 等

3. **分隔符**
   - 默认使用逗号分隔
   - 使用 `delimiter` 选项指定其他分隔符

4. **特殊字符**
   - 字段包含逗号时应使用引号包裹
   - 字段包含引号时应使用双引号转义

5. **性能优化**
   - 大 CSV 文件建议分批加载
   - 考虑在服务端预处理为 JSON

6. **编码问题**
   - 确保 CSV 文件使用 UTF-8 编码
   - GBK 编码可能导致中文乱码

## 常见问题

**Q: 所有坐标都是 0？**
- 确保使用 `parseFloat()` 转换坐标
- 检查 CSV 中的分隔符是否正确

**Q: 中文显示乱码？**
- 确保 CSV 文件保存为 UTF-8 编码
- 使用文本编辑器转换编码后再加载

**Q: 如何处理 Excel 导出的 CSV？**
```javascript
// Excel 导出的 CSV 可能使用分号分隔
const data = mapvthree.CSVDataSource.fromCSVString(csvString, {
    delimiter: ';',
    parseCoordinates: (item) => ({
        type: 'Point',
        coordinates: [parseFloat(item.lng), parseFloat(item.lat)]
    })
});
```

**Q: 如何跳过无效数据行？**
```javascript
parseCoordinates: (item) => {
    const lng = parseFloat(item.lng);
    const lat = parseFloat(item.lat);
    if (isNaN(lng) || isNaN(lat)) {
        return null;  // 返回 null 跳过该行
    }
    return { type: 'Point', coordinates: [lng, lat] };
}
```

**Q: 如何处理带引号的字段？**
- 标准 CSV 格式：字段含逗号时用双引号包裹
- 字段含双引号时用两个双引号转义：`"他说""你好"""`
