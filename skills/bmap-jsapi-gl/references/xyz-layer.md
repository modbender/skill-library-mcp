# XYZLayer 第三方图层

加载第三方标准瓦片图层，支持 XYZ、TMS、WMS、WMTS 等格式。

## 快速开始

```javascript
// XYZ 标准瓦片
var layer = new BMapGL.XYZLayer({
    tileUrlTemplate: 'http://c.tile.opencyclemap.org/cycle/[z]/[x]/[y].png'
});
map.addTileLayer(layer);

// TMS 标准（Y 坐标反向）
var tmsLayer = new BMapGL.XYZLayer({
    tms: true,
    tileUrlTemplate: 'http://tiles.example.com/[z]/[x]/[y].png'
});
map.addTileLayer(tmsLayer);
```

## 构造函数

```javascript
new BMapGL.XYZLayer(options)
```

### 基础参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| tileUrlTemplate | string | - | 瓦片 URL 模板，支持占位符 |
| opacity | number | 1 | 透明度（0-1） |
| minZoom | number | 0 | 最小缩放级别 |
| maxZoom | number | 23 | 最大缩放级别 |
| tms | boolean | false | 是否使用 TMS 标准（Y 坐标反向） |
| zIndex | number | - | 图层堆叠顺序 |

### 坐标转换参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| transform | object | - | 坐标转换配置 |
| transform.source | string | 'EPSG3857' | 源坐标系：'EPSG3857'/'GCJ02'/'BD09MC' |
| transform.target | string | 'BD09MC' | 目标坐标系 |
| extent | array | - | 显示范围 [minX, minY, maxX, maxY] |
| extentCRSIsWGS84 | boolean | false | extent 是否为 WGS84 坐标 |

## URL 占位符

| 占位符 | 说明 |
|--------|------|
| `[x]` | 瓦片列号 |
| `[y]` | 瓦片行号 |
| `[z]` | 缩放级别 |
| `[b]` | 边界框 BBOX（用于 WMS） |
| `[w]` | 瓦片宽度 |
| `[h]` | 瓦片高度 |
| `{a,b,c}` | 服务器负载均衡，随机选择 |


## 常见场景

### XYZ 标准瓦片

```javascript
var layer = new BMapGL.XYZLayer({
    tileUrlTemplate: 'https://tile.openstreetmap.org/[z]/[x]/[y].png',
    minZoom: 3,
    maxZoom: 18
});
map.addTileLayer(layer);
```

### TMS 标准瓦片

```javascript
var layer = new BMapGL.XYZLayer({
    tms: true,
    tileUrlTemplate: 'http://tiles.example.com/[z]/[x]/[y].png'
});
map.addTileLayer(layer);
```

### WMS 服务

```javascript
var layer = new BMapGL.XYZLayer({
    tileUrlTemplate: 'https://ahocevar.com/geoserver/wms?' +
        'SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&' +
        'LAYERS=topp:states&STYLES=&FORMAT=image/png&' +
        'TRANSPARENT=true&SRS=EPSG:3857&' +
        'WIDTH=256&HEIGHT=256&BBOX=[b]'
});
map.addTileLayer(layer);
```

### WMTS 服务

```javascript
var layer = new BMapGL.XYZLayer({
    tileUrlTemplate: 'https://mrdata.usgs.gov/mapcache/wmts?' +
        'Service=WMTS&Request=GetTile&Version=1.0.0&' +
        'layer=sgmc2&style=default&Format=image/png&' +
        'tilematrixset=GoogleMapsCompatible&' +
        'TileMatrix=[z]&TileCol=[x]&TileRow=[y]'
});
map.addTileLayer(layer);
```

### 限定显示范围

```javascript
var layer = new BMapGL.XYZLayer({
    tileUrlTemplate: 'http://tiles.example.com/[z]/[x]/[y].png',
    extent: [115.5, 39.5, 117.5, 40.5],
    extentCRSIsWGS84: true
});
map.addTileLayer(layer);
```


## 注意事项

1. WMS 服务使用 `[b]` 占位符传递 BBOX 参数
2. TMS 与 XYZ 的区别在于 Y 坐标方向，设置 `tms: true` 自动处理
3. 移除图层使用 `map.removeTileLayer(layer)`
