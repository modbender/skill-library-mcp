# Convertor 坐标转换

用于将其他坐标系（GPS、高德、谷歌等）转换为百度坐标系。

## 快速开始

```javascript
var convertor = new BMapGL.Convertor();
var points = [new BMapGL.Point(116.32715863448607, 39.990912172420714)];

convertor.translate(points, COORDINATES_WGS84, COORDINATES_BD09, function(data) {
    if (data.status === 0) {
        map.addOverlay(new BMapGL.Marker(data.points[0]));
    }
});
```

## 构造函数

```javascript
new BMapGL.Convertor()
```

无参数。

## 方法

### translate

将坐标从源坐标系转换为目标坐标系。

```javascript
convertor.translate(points, from, to, callback)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| points | Array\<Point\> | - | 待转换的坐标数组 |
| from | number | 1 | 源坐标系类型 |
| to | number | 5 | 目标坐标系类型（仅支持 5 或 6） |
| callback | function | - | 转换完成回调 |

**回调参数：**

```javascript
callback(data)
```

| 属性 | 类型 | 说明 |
|------|------|------|
| status | number | 状态码，0 表示成功 |
| points | Array\<Point\> | 转换后的坐标数组（成功时） |

## 坐标系常量

| 常量 | 值 | 说明 |
|------|-----|------|
| COORDINATES_WGS84 | 1 | GPS 坐标 |
| COORDINATES_WGS84_MC | 2 | GPS 米制坐标 |
| COORDINATES_GCJ02 | 3 | 高德、谷歌、腾讯坐标（火星坐标系） |
| COORDINATES_GCJ02_MC | 4 | GCJ02 米制坐标 |
| COORDINATES_BD09 | 5 | 百度经纬度坐标 |
| COORDINATES_BD09_MC | 6 | 百度米制坐标 |
| COORDINATES_MAPBAR | 7 | Mapbar 坐标 |
| COORDINATES_51 | 8 | 51 地图坐标 |

**限制：** 目标坐标系（to）仅支持 `COORDINATES_BD09`(5) 和 `COORDINATES_BD09_MC`(6)。

## 示例

### 批量转换

```javascript
var points = [
    new BMapGL.Point(116.397428, 39.90923),
    new BMapGL.Point(116.407428, 39.91923),
    new BMapGL.Point(116.417428, 39.92923)
];

var convertor = new BMapGL.Convertor();
convertor.translate(points, COORDINATES_GCJ02, COORDINATES_BD09, function(data) {
    if (data.status === 0) {
        data.points.forEach(function(point, index) {
            map.addOverlay(new BMapGL.Marker(point));
        });
    }
});
```

## 注意事项

1. 百度地图使用 BD09 坐标系，直接使用 GPS 或其他地图坐标会产生偏移
2. 转换为异步操作，结果通过回调返回
3. 转换失败时 `data.status` 非 0，`data.points` 不存在
4. 常量定义在全局 `window` 对象上，可直接使用
