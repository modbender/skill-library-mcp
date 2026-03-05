# 基础类

## Point 坐标点

表示地理坐标点（经纬度）。

### 构造函数

```javascript
new BMapGL.Point(lng, lat)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| lng | number | 经度 |
| lat | number | 纬度 |

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| lng | number | 经度 |
| lat | number | 纬度 |

### 方法

| 方法 | 返回值 | 说明 |
|------|--------|------|
| `equals(other)` | boolean | 判断两个坐标点是否相等 |

### 示例

```javascript
// 创建坐标点（BD09 经纬度坐标系）
var point = new BMapGL.Point(116.404, 39.915);

// 获取坐标值
console.log(point.lng);  // 116.404
console.log(point.lat);  // 39.915

// 比较两个点
var point2 = new BMapGL.Point(116.404, 39.915);
console.log(point.equals(point2));  // true
```

### 坐标系说明

百度地图 API 使用 **BD09** 坐标系（百度坐标系）。如果数据是其他坐标系（如 WGS84、GCJ02），需要先进行坐标转换。

## Bounds 地理范围

表示地理矩形区域。

### 构造函数

```javascript
new BMapGL.Bounds(sw, ne)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| sw | Point | 西南角坐标 |
| ne | Point | 东北角坐标 |

### 方法

| 方法 | 返回值 | 说明 |
|------|--------|------|
| `getSouthWest()` | Point | 获取西南角坐标 |
| `getNorthEast()` | Point | 获取东北角坐标 |
| `getCenter()` | Point | 获取中心点坐标 |
| `containsPoint(point)` | boolean | 判断点是否在范围内 |
| `extend(point)` | void | 扩展范围以包含指定点 |

### 示例

```javascript
// 创建地理范围
var sw = new BMapGL.Point(116.3, 39.8);
var ne = new BMapGL.Point(116.5, 40.0);
var bounds = new BMapGL.Bounds(sw, ne);

// 获取中心点
var center = bounds.getCenter();

// 判断点是否在范围内
var point = new BMapGL.Point(116.4, 39.9);
console.log(bounds.containsPoint(point));  // true

// 获取当前地图视野范围
var mapBounds = map.getBounds();
```

## Size 尺寸

表示像素尺寸。

### 构造函数

```javascript
new BMapGL.Size(width, height)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| width | number | 宽度（像素） |
| height | number | 高度（像素） |

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| width | number | 宽度 |
| height | number | 高度 |

### 示例

```javascript
// 创建尺寸
var size = new BMapGL.Size(100, 80);

// 获取地图容器尺寸
var containerSize = map.getContainerSize();
console.log(containerSize.width, containerSize.height);
```

## Pixel 像素坐标

表示像素坐标点。

### 构造函数

```javascript
new BMapGL.Pixel(x, y)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| x | number | X 坐标（像素） |
| y | number | Y 坐标（像素） |

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| x | number | X 坐标 |
| y | number | Y 坐标 |

### 示例

```javascript
// 在事件对象中获取像素坐标
map.addEventListener('click', function(e) {
    console.log('像素坐标:', e.pixel.x, e.pixel.y);
    console.log('经纬度:', e.latlng.lng, e.latlng.lat);
});

// 像素坐标与经纬度转换
var point = map.pixelToPoint(new BMapGL.Pixel(100, 100));
var pixel = map.pointToPixel(new BMapGL.Point(116.404, 39.915));
```

## Icon 图标

表示标注覆盖物所使用的图标。

### 构造函数

```javascript
new BMapGL.Icon(image, size, options)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| image | string/Canvas/Image | - | 图片 URL 或 DOM |
| size | Size | - | 显示尺寸 |
| options.anchor | Size | 图标中心 | 定位点偏移 |
| options.imageOffset | Size | `new Size(0, 0)` | 图片偏移 (雪碧图) |
| options.imageSize | Size | 原始尺寸 | 图片尺寸 (2x 图需设置) |

### 方法

| 方法 | 说明 |
|------|------|
| `setImageUrl(url)` | 设置图片 URL |
| `setSize(size)` | 设置显示尺寸 |
| `setAnchor(anchor)` | 设置定位点偏移 |
| `setImageOffset(offset)` | 设置图片偏移 |
| `setImageSize(size)` | 设置图片尺寸 |

### 示例

```javascript
// 基础用法
var icon = new BMapGL.Icon(
    'marker.png',
    new BMapGL.Size(24, 32),
    { anchor: new BMapGL.Size(12, 32) }  // 底部中心为定位点
);

// 雪碧图
var icon = new BMapGL.Icon(
    'sprites.png',
    new BMapGL.Size(24, 24),
    {
        anchor: new BMapGL.Size(12, 24),
        imageOffset: new BMapGL.Size(-48, 0)  // 第三个图标
    }
);

// 用于 Marker
var marker = new BMapGL.Marker(point, { icon: icon });
```
