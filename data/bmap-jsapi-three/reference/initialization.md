# MapV Three 初始化指南

## 安装

```bash
npm install @baidumap/mapv-three three
```

## 静态资源配置

### Webpack

```javascript
const CopyWebpackPlugin = require('copy-webpack-plugin');

module.exports = {
    plugins: [
        new CopyWebpackPlugin({
            patterns: [
                {from: 'node_modules/@baidumap/mapv-three/dist/assets', to: 'mapvthree/assets'},
            ],
        }),
    ]
};
```

### Vite

```javascript
import copy from 'rollup-plugin-copy';

export default {
    plugins: [
        copy({
            targets: [
                {src: 'node_modules/@baidumap/mapv-three/dist/assets', dest: 'public/mapvthree'},
            ],
            hook: 'buildStart',
        }),
    ]
};
```

### 全局变量

```html
<script>
    window.MAPV_BASE_URL = 'mapvthree/';
</script>
```

## 基础初始化

```javascript
import * as mapvthree from '@baidumap/mapv-three';

// 配置百度地图 AK（可选，使用百度底图时需要）
mapvthree.BaiduMapConfig.ak = '您的AK密钥';

// 创建引擎
const engine = new mapvthree.Engine(document.getElementById('map'), {
    map: {
        center: [116.404, 39.915],
        range: 5000
    },
    rendering: {
        enableAnimationLoop: true
    }
});

// 添加底图
engine.add(new mapvthree.MapView({
    imageryProvider: new mapvthree.BingImageryTileProvider()
}));
```

## 构造函数完整配置

```javascript
new mapvthree.Engine(container, {
    map: {
        center: [116.404, 39.915],   // 初始中心点 [经度, 纬度]
        heading: 0,                   // 旋转角度（0-360）
        pitch: 45,                    // 俯仰角（0-90）
        range: 5000,                  // 视野距离（米）
        projection: 'EPSG:3857',      // 投影：'EPSG:3857' 或 'ecef'
        is3DControl: true             // 3D 控制器（默认 true，设 false 禁用）
    },
    rendering: {
        enableAnimationLoop: true,    // 启用动画循环
        pixelRatio: window.devicePixelRatio,
        features: {
            antialias: { enabled: true, method: 'smaa' },   // 'smaa'|'fxaa'
            ao: { enabled: false, strength: 1.0 },          // 环境光遮蔽
            reflection: { enabled: false, strength: 0.5 },  // 反射
            depthPicking: { enabled: true },                 // 深度拾取
            colorAdjustment: { enabled: false, brightness: 1.0, contrast: 1.0, saturation: 1.0 },
            hdr: { enabled: false },                         // HDR 渲染
            bloom: { enabled: false, strength: 0.1, threshold: 0.5, radius: 0.5 },
            shadow: { enabled: false }
        }
    },
    controller: {
        enabled: true,
        enableRotate: true,
        enableZoom: true,
        enablePan: true,
        enableTilt: true,
        minimumZoomDistance: 1,
        maximumZoomDistance: Infinity,
        enableFixCenter: false,
        enableTerrainCollision: true,
        inertiaTranslate: true,
        maximumMovementRatio: 1.0,
        bounceAnimationTime: 300
    }
});
```

## 视野控制

```javascript
// 中心点
engine.map.setCenter([116.404, 39.915]);
engine.map.getCenter();

// 旋转/俯仰/距离
engine.map.setHeading(45);
engine.map.setPitch(60);
engine.map.setRange(5000);

// 综合设置
engine.map.lookAt([116.404, 39.915], { heading: 30, pitch: 60, range: 3000 });

// 动画飞行
engine.map.flyTo([116.404, 39.915], {
    heading: 0, pitch: 45, range: 2000,
    duration: 2000,
    complete: () => console.log('飞行完成')
});

// 根据点集自动调整视野
engine.map.setViewport([[116.38, 39.90], [116.42, 39.92]]);

// 边界限制
engine.map.setBounds([[116.30, 39.85], [116.50, 39.95]]);
engine.map.setMinRange(100);
engine.map.setMaxRange(50000);
```

## 添加图层

```javascript
// 可视化图层
const polygon = engine.add(new mapvthree.Polygon({
    color: 'red',
    extrude: true,
    extrudeValue: 100
}));
polygon.dataSource = await mapvthree.GeoJSONDataSource.fromURL('data.geojson');

// Three.js 对象
const position = engine.map.projectArrayCoordinate([116.404, 39.915, 0]);
const mesh = new THREE.Mesh(
    new THREE.BoxGeometry(10, 10, 10),
    new THREE.MeshStandardMaterial({ color: 0xff0000 })
);
mesh.position.set(...position);
engine.add(mesh);

engine.remove(polygon);
```

## 事件绑定

```javascript
polygon.addEventListener('click', (e) => {
    console.log('点击了多边形', e.entity);
});

engine.map.addEventListener('click', (e) => {
    console.log('点击了地图', e.point);
});
```

## 坐标转换

```javascript
const projected = engine.map.projectArrayCoordinate([116.404, 39.915, 0]);
const geographic = engine.map.unprojectArrayCoordinate(projected);
```

## 底图提供者

```javascript
new mapvthree.BingImageryTileProvider()                            // Bing 卫星图
new mapvthree.OSMImageryTileProvider()                             // OpenStreetMap
new mapvthree.TiandituImageryTileProvider()                        // 天地图（需 TiandituConfig.tk）
new mapvthree.XYZImageryTileProvider({ url: '.../{z}/{x}/{y}.png' })
new mapvthree.WMSImageryTileProvider({ url: '...', layers: '...' })
new mapvthree.WMTSImageryTileProvider({ url: '...', layer: '...', style: 'default', tileMatrixSetID: 'EPSG:3857' })
```

通过 MapView 使用：
```javascript
const mapView = engine.add(new mapvthree.MapView({
    imageryProvider: new mapvthree.BingImageryTileProvider()
}));
// 切换底图：mapView.imageryProvider = newProvider;
```

## 百度地图适配器

兼容百度地图 JSAPI GL 的 API：

```javascript
import * as BMapGL from '@baidumap/mapv-three/adapters/bmap';

const map = new BMapGL.Map('map');
map.centerAndZoom(new BMapGL.Point(116.404, 39.915), 15);

const marker = new BMapGL.Marker(new BMapGL.Point(116.404, 39.915));
map.addOverlay(marker);
```

## 销毁

```javascript
engine.dispose();
// 销毁后引擎不可再使用
```
