# 影像瓦片提供者

用于加载卫星影像、航拍图像等栅格底图。通过 MapView 使用：

```javascript
const mapView = engine.add(new mapvthree.MapView({
    imageryProvider: new mapvthree.BingImageryTileProvider({
        style: mapvthree.mapViewConstants.BING_MAP_STYLE_AERIAL
    })
}));

// 切换提供者
mapView.imageryProvider = new mapvthree.OSMImageryTileProvider();
```

## 提供者对比

| 提供者 | 投影 | 缩放级别 | 覆盖范围 | 费用 |
|-------|------|---------|---------|------|
| BingImageryTileProvider | Web墨卡托、地理 | 1-18 | 全球 | 免费 |
| Baidu09ImageryTileProvider | Web墨卡托 | 3-19 | 全球（国内优） | 需AK |
| TiandituImageryTileProvider | Web墨卡托、地理 | 0-18 | 全球（国内优） | 需TK |
| OSMImageryTileProvider | Web墨卡托、地理 | 1-18 | 全球 | 免费 |
| StadiaImageryTileProvider | Web墨卡托、地理 | 1-18 | 全球 | 免费 |

## 内置提供者

### BingImageryTileProvider

```javascript
const provider = new mapvthree.BingImageryTileProvider({
    style: mapvthree.mapViewConstants.BING_MAP_STYLE_AERIAL
});

// 支持的样式常量（mapvthree.mapViewConstants）：
// BING_MAP_STYLE_AERIAL - 卫星图（无标签）
// BING_MAP_STYLE_AERIAL_WITH_LABELS - 卫星图（含标签）
// BING_MAP_STYLE_ROAD - 路况图

// 动态切换
provider.style = mapvthree.mapViewConstants.BING_MAP_STYLE_ROAD;
```

### Baidu09ImageryTileProvider

```javascript
const provider = new mapvthree.Baidu09ImageryTileProvider({
    ak: 'your_baidu_ak',
    type: 'satellite'  // 'satellite' 或 'normal'
});
```

### TiandituImageryTileProvider

```javascript
mapvthree.TiandituConfig.tk = 'your_token';
const provider = new mapvthree.TiandituImageryTileProvider();
```

### OSMImageryTileProvider

```javascript
const provider = new mapvthree.OSMImageryTileProvider();
```

### StadiaImageryTileProvider

```javascript
const provider = new mapvthree.StadiaImageryTileProvider({
    style: mapvthree.mapViewConstants.STADIA_MAP_STYLE_STAMEN_WATERCOLOR
});

// 支持的样式（mapvthree.mapViewConstants）：
// STADIA_MAP_STYLE_STAMEN_WATERCOLOR - 水彩风格
// STADIA_MAP_STYLE_STAMEN_TONER - 简笔风格
// STADIA_MAP_STYLE_ALIDADE_SMOOTH - 光滑风格
// STADIA_MAP_STYLE_ALIDADE_SMOOTH_DARK - 暗色风格
// STADIA_MAP_STYLE_OUTDOORS - 户外风格
```

## API 参数表

### 通用参数

| 参数 | 类型 | 说明 | 默认值 |
|-----|------|------|--------|
| `projection` | string | 投影方式 | PROJECTION_WEB_MERCATOR |

### BingImageryTileProvider

| 参数 | 类型 | 说明 | 默认值 |
|-----|------|------|--------|
| `style` | string | 地图样式 | BING_MAP_STYLE_AERIAL |

### Baidu09ImageryTileProvider

| 参数 | 类型 | 说明 | 默认值 |
|-----|------|------|--------|
| `ak` | string | 百度地图 API Key | BaiduMapConfig.ak |
| `type` | string | 'satellite' 或 'normal' | 'normal' |

### TiandituImageryTileProvider

| 参数 | 类型 | 说明 | 默认值 |
|-----|------|------|--------|
| `tk` | string | 天地图访问令牌 | TiandituConfig.tk |

### StadiaImageryTileProvider

| 参数 | 类型 | 说明 | 默认值 |
|-----|------|------|--------|
| `style` | string | 地图样式 | STADIA_MAP_STYLE_STAMEN_WATERCOLOR |

## 示例：动态切换影像提供者

```javascript
// ... engine initialized (see initialization.md)

const mapView = engine.add(new mapvthree.MapView({
    imageryProvider: new mapvthree.BingImageryTileProvider()
}));

const providers = {
    bing: new mapvthree.BingImageryTileProvider(),
    osm: new mapvthree.OSMImageryTileProvider(),
    baidu: new mapvthree.Baidu09ImageryTileProvider({ ak: 'your_ak', type: 'satellite' })
};

function switchProvider(name) {
    if (providers[name]) {
        mapView.imageryProvider = providers[name];
    }
}
```

## 示例：卫星图 + 矢量地图叠加

```javascript
// ... engine initialized

const mapView = engine.add(new mapvthree.MapView({
    imageryProvider: new mapvthree.OSMImageryTileProvider(),
    vectorTileProvider: new mapvthree.BaiduVectorTileProvider({ ak: 'your_ak' })
}));
```
