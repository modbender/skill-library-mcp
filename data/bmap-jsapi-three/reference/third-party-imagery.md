# 第三方图层接入 - WMS/WMTS/XYZ

支持接入 OGC 标准（WMS、WMTS）和 XYZ 瓦片格式的第三方地图服务。通过 MapView 使用：

```javascript
const mapView = engine.add(new mapvthree.MapView({
    imageryProvider: new mapvthree.WMSImageryTileProvider({
        url: 'https://your-geoserver:8080/geoserver/wms',
        params: {
            LAYERS: 'workspace:layername',
            SRS: 'EPSG:3857'
        }
    })
}));
```

## API 参数表

### WMSImageryTileProvider

| 参数 | 类型 | 说明 | 默认值 | 必填 |
|-----|------|------|--------|------|
| `url` | string | WMS 服务 URL | - | 是 |
| `params` | object | WMS 参数对象 | {} | 否 |
| `params.LAYERS` | string | 图层名称，多个用逗号分隔 | - | 是 |
| `params.VERSION` | string | WMS 版本 | 1.3.0 | 否 |
| `params.SRS/CRS` | string | 坐标参考系统 | EPSG:3857 | 否 |
| `params.TRANSPARENT` | boolean | 是否透明 | true | 否 |
| `params.STYLES` | string | 样式参数 | '' | 否 |
| `params.FORMAT` | string | 输出格式 | image/png | 否 |
| `serverType` | string | 服务器类型(geoserver/mapserver/qgis) | - | 否 |
| `hidpi` | boolean | 高 DPI 支持 | false | 否 |

### WMTSImageryTileProvider

| 参数 | 类型 | 说明 | 默认值 | 必填 |
|-----|------|------|--------|------|
| `url` | string | WMTS 服务 URL | - | 是 |
| `params` | object | WMTS 参数对象 | {} | 否 |
| `params.LAYER` | string | 图层标识符 | - | 是 |
| `params.TILEMATRIXSET` | string | 瓦片矩阵集合 | EPSG:3857 | 否 |
| `params.VERSION` | string | WMTS 版本 | 1.0.0 | 否 |
| `params.STYLE` | string | 样式标识符 | default | 否 |
| `params.FORMAT` | string | 输出格式 | image/png | 否 |
| `matrixIds` | array | 自定义矩阵 ID 映射 | - | 否 |
| `requestEncoding` | string | 请求方式（KVP 或 REST） | KVP | 否 |

### XYZImageryTileProvider

| 参数 | 类型 | 说明 | 默认值 | 必填 |
|-----|------|------|--------|------|
| `url` | string | 瓦片 URL 模板 | - | 是 |
| `projection` | string | 投影方式 | PROJECTION_WEB_MERCATOR | 否 |
| `maxLevel` | number | 最大缩放级别 | 18 | 否 |

## XYZ URL 模板占位符

| 占位符 | 说明 |
|-------|------|
| `{z}` | 缩放级别 |
| `{x}` | 瓦片 X 坐标 |
| `{y}` | 瓦片 Y 坐标（谷歌/OSM 规范） |
| `{-y}` | 瓦片 Y 坐标（TMS 规范，反向） |

## 示例：GeoServer WMS

```javascript
// ... engine initialized (see initialization.md)

const mapView = engine.add(new mapvthree.MapView({
    imageryProvider: new mapvthree.WMSImageryTileProvider({
        url: 'http://localhost:8080/geoserver/wms',
        params: {
            LAYERS: 'test:roads,test:buildings',
            SRS: 'EPSG:3857',
            FORMAT: 'image/png',
            TRANSPARENT: true
        },
        serverType: 'geoserver'
    })
}));
```

## 示例：WMTS 服务

```javascript
// ... engine initialized

const mapView = engine.add(new mapvthree.MapView({
    imageryProvider: new mapvthree.WMTSImageryTileProvider({
        url: 'http://localhost:8080/geoserver/gwc/service/wmts',
        params: {
            LAYER: 'test:roads',
            TILEMATRIXSET: 'EPSG:3857',
            FORMAT: 'image/png'
        }
    })
}));

// WMTS REST 风格
const wmtsRest = new mapvthree.WMTSImageryTileProvider({
    url: 'https://server/wmts/{layer}/{style}/{tilematrixset}/{tilematrix}/{tilerow}/{tilecol}.png',
    params: {
        LAYER: 'your-layer',
        STYLE: 'default',
        TILEMATRIXSET: 'EPSG:3857'
    },
    requestEncoding: 'REST'
});
```

## 示例：XYZ 瓦片

```javascript
// ... engine initialized

// 通用 XYZ
const mapView = engine.add(new mapvthree.MapView({
    imageryProvider: new mapvthree.XYZImageryTileProvider({
        url: 'https://tile-server.example.com/data/{z}/{x}/{y}.png'
    })
}));

// ArcGIS Online
new mapvthree.XYZImageryTileProvider({
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
});

// CartoDB
new mapvthree.XYZImageryTileProvider({
    url: 'https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png'
});
```

## 示例：动态切换图层

```javascript
// ... engine initialized

const mapView = engine.add(new mapvthree.MapView({
    imageryProvider: new mapvthree.WMSImageryTileProvider({
        url: 'http://localhost:8080/geoserver/wms',
        params: { LAYERS: 'test:satellite' }
    })
}));

// 切换图层
mapView.imageryProvider = new mapvthree.WMSImageryTileProvider({
    url: 'http://localhost:8080/geoserver/wms',
    params: { LAYERS: 'test:roads' }
});
```
