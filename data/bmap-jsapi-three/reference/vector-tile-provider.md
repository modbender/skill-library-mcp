# 矢量瓦片提供者

用于加载矢量地图数据（道路、建筑、水体等），支持样式自定义和交互查询。通过 MapView 使用：

```javascript
const mapView = engine.add(new mapvthree.MapView({
    vectorTileProvider: new mapvthree.BaiduVectorTileProvider({ ak: 'your_ak' })
}));
```

## 提供者对比

| 提供者 | 特点 | 样式系统 | 适用场景 |
|-------|------|---------|---------|
| BaiduVectorTileProvider | 国内覆盖优，POI 丰富 | 百度自有 | 国内应用、3D 建筑 |
| MapboxVectorTileProvider | 样式丰富，GL 规范 | Mapbox GL v8 | 国际应用、复杂样式 |
| GeoJSONVectorTileProvider | 灵活自定义 | 自定义 | 业务数据展示 |
| BaiduTrafficTileProvider | 实时交通数据 | 内置 | 交通导航 |

## 内置提供者

### BaiduVectorTileProvider

```javascript
// 基础使用
const provider = new mapvthree.BaiduVectorTileProvider({
    ak: 'your_baidu_ak'
});

// 离线模式
const offlineProvider = new mapvthree.BaiduVectorTileProvider({
    isOffline: true,
    url: 'http://local-server:8080',
    projection: mapvthree.PROJECTION_WEB_MERCATOR
});

// 个性化样式
const customProvider = new mapvthree.BaiduVectorTileProvider({
    ak: 'your_baidu_ak',
    styleId: 'your_style_id'
});

// 显示选项
const provider = new mapvthree.BaiduVectorTileProvider({
    ak: 'your_baidu_ak',
    displayOptions: {
        base: true,      // 基础面
        link: true,      // 道路网络
        building: true,  // 3D 建筑
        poi: true,       // POI 标签
        flat: false      // 平面模式
    }
});
```

### MapboxVectorTileProvider

```javascript
// 官方样式
const provider = new mapvthree.MapboxVectorTileProvider({
    style: 'mapbox://styles/mapbox/streets-v11',
    accessToken: 'your_mapbox_access_token'
});

// 支持的官方样式：
// mapbox://styles/mapbox/streets-v11
// mapbox://styles/mapbox/outdoors-v12
// mapbox://styles/mapbox/light-v11
// mapbox://styles/mapbox/dark-v11
// mapbox://styles/mapbox/satellite-v9

// 自定义样式对象（Mapbox GL Style Specification v8）
const provider = new mapvthree.MapboxVectorTileProvider({
    style: {
        version: 8,
        sources: { /* ... */ },
        layers: [ /* ... */ ]
    },
    accessToken: 'your_token'
});
```

### GeoJSONVectorTileProvider

```javascript
const provider = new mapvthree.GeoJSONVectorTileProvider({
    data: geoJsonData,
    projection: mapvthree.PROJECTION_WEB_MERCATOR,
    minZoom: 0,
    maxZoom: 16,
    tolerance: 3,
    styleOptions: {
        color: '#ff0000',
        opacity: 0.8
    }
});
```

### BaiduTrafficTileProvider

```javascript
const provider = new mapvthree.BaiduTrafficTileProvider({
    ak: 'your_baidu_ak'
});
```

## API 参数表

### BaiduVectorTileProvider

| 参数 | 类型 | 说明 | 默认值 |
|-----|------|------|--------|
| `ak` | string | 百度地图 API Key | BaiduMapConfig.ak |
| `isOffline` | boolean | 离线模式 | false |
| `url` | string | 离线服务器地址 | - |
| `staticUrl` | string | 离线静态资源地址 | - |
| `styleId` | string | 个性化样式 ID | - |
| `styleJson` | string | 个性化样式 JSON | - |
| `displayOptions.base` | boolean | 显示基础面 | true |
| `displayOptions.link` | boolean | 显示道路网络 | true |
| `displayOptions.building` | boolean | 显示 3D 建筑 | true |
| `displayOptions.poi` | boolean | 显示 POI 标签 | true |
| `displayOptions.flat` | boolean | 平面模式 | false |

### MapboxVectorTileProvider

| 参数 | 类型 | 说明 | 默认值 |
|-----|------|------|--------|
| `style` | string\|object | 样式 URL 或样式对象 | mapbox://styles/mapbox/streets-v11 |
| `accessToken` | string | Mapbox 访问令牌 | MapboxConfig.accessToken |

### GeoJSONVectorTileProvider

| 参数 | 类型 | 说明 | 默认值 |
|-----|------|------|--------|
| `data` | object | GeoJSON 数据 | - (必填) |
| `projection` | string | 投影方式 | PROJECTION_WEB_MERCATOR |
| `minZoom` | number | 最小缩放级别 | 0 |
| `maxZoom` | number | 最大缩放级别 | 16 |
| `tolerance` | number | 化简精度（米） | 3 |

## 示例：百度矢量地图 + 个性化风格

```javascript
// ... engine initialized (see initialization.md)

const mapView = engine.add(new mapvthree.MapView({
    vectorTileProvider: new mapvthree.BaiduVectorTileProvider({
        ak: 'your_baidu_ak',
        styleId: 'your_style_id',
        displayOptions: {
            base: true,
            link: true,
            building: true,
            poi: true
        }
    })
}));

// 动态切换样式
await mapView.vectorTileProvider.setMapStyle({ styleId: 'another_style_id' });
```

## 示例：卫星图 + 矢量叠加

```javascript
// ... engine initialized

const mapView = engine.add(new mapvthree.MapView({
    imageryProvider: new mapvthree.Baidu09ImageryTileProvider({
        ak: 'your_ak', type: 'satellite'
    }),
    vectorTileProvider: new mapvthree.BaiduVectorTileProvider({
        ak: 'your_ak',
        displayOptions: { base: false, link: true, building: false, poi: true }
    })
}));
```
