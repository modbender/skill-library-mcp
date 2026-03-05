# 地形瓦片提供者

用于加载高程数据，将平面地图转换为 3D 地形。通过 MapView 使用：

```javascript
const mapView = engine.add(new mapvthree.MapView({
    terrainProvider: new mapvthree.CesiumTerrainTileProvider({
        accessToken: 'your_cesium_access_token'
    })
}));
```

## 提供者对比

| 提供者 | 数据源 | 分辨率 | 覆盖范围 | 成本 |
|-------|-------|--------|---------|------|
| CesiumTerrainTileProvider | Cesium ion | ~30m | 全球 | 付费（有免费额度） |
| PlaneTerrainTileProvider | 生成平面 | N/A | 全球 | 免费 |

## CesiumTerrainTileProvider

```javascript
// 使用 Cesium ion 默认地形
const provider = new mapvthree.CesiumTerrainTileProvider({
    accessToken: 'your_cesium_access_token'
});

// 全局配置 token
mapvthree.CesiumConfig.accessToken = 'your_cesium_access_token';
const provider = new mapvthree.CesiumTerrainTileProvider();

// 自定义地形服务器
const provider = new mapvthree.CesiumTerrainTileProvider({
    url: 'https://your-terrain-server/terrain-data'
});

// 高级配置（请求顶点法线以获更好光照）
const provider = new mapvthree.CesiumTerrainTileProvider({
    accessToken: 'your_token',
    requestVertexNormals: true
});
```

## PlaneTerrainTileProvider

```javascript
const provider = new mapvthree.PlaneTerrainTileProvider();
// 适用于不需要真实地形的场景，或作为初始化占位
```

## API 参数表

### CesiumTerrainTileProvider

| 参数 | 类型 | 说明 | 默认值 |
|-----|------|------|--------|
| `accessToken` | string | Cesium ion 访问令牌 | CesiumConfig.accessToken |
| `url` | string | 自定义地形服务 URL | Cesium 官方 URL |
| `requestVertexNormals` | boolean | 是否请求顶点法线 | true |

### PlaneTerrainTileProvider

无特殊参数。

## 示例：地形与影像叠加

```javascript
// ... engine initialized (see initialization.md)

const mapView = engine.add(new mapvthree.MapView({
    imageryProvider: new mapvthree.Baidu09ImageryTileProvider({
        ak: 'your_ak', type: 'satellite'
    }),
    terrainProvider: new mapvthree.CesiumTerrainTileProvider({
        accessToken: 'your_cesium_access_token'
    })
}));
```

## 示例：先用平面地形快速初始化，再异步加载真实地形

```javascript
// ... engine initialized

const mapView = engine.add(new mapvthree.MapView({
    terrainProvider: new mapvthree.PlaneTerrainTileProvider()
}));

// 异步切换到真实地形
mapView.terrainProvider = new mapvthree.CesiumTerrainTileProvider({
    accessToken: 'your_access_token'
});
```

## 示例：自定义地形服务

```javascript
// ... engine initialized

const mapView = engine.add(new mapvthree.MapView({
    terrainProvider: new mapvthree.CesiumTerrainTileProvider({
        url: 'https://terrain-server.example.com/assets/123/v1.0'
    })
}));
```
