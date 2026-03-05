# Engine 使用指南

Engine 是 MapV Three 的核心入口，提供场景管理、渲染控制、事件监听和视频导出功能。

## 基础用法

```javascript
import * as mapvthree from '@baidumap/mapv-three';

const engine = new mapvthree.Engine(document.getElementById('map'), {
    map: {
        center: [116.404, 39.915],
        range: 5000
    },
    rendering: {
        enableAnimationLoop: true
    }
});

// 添加/移除 3D 对象
engine.add(mesh);
engine.remove(mesh);

// 释放资源
engine.dispose();
```

## 构造参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `container` | HTMLElement \| string | - | 容器对象或容器ID |
| `options` | object | `{}` | 配置选项 |

### options 配置项

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `rendering` | object | - | 渲染选项 |
| `map` | object | - | 地图选项 |
| `event` | object | - | 事件选项 |
| `selection` | object | - | 选择器选项 |
| `widgets` | object | - | 控件选项 |

## 公共属性

| 属性 | 类型 | 只读 | 说明 |
|------|------|:----:|------|
| `container` | HTMLElement | Yes | 容器对象 |
| `map` | EngineMap | Yes | 地图视野控制 |
| `rendering` | EngineRendering | Yes | 渲染配置管理 |
| `widgets` | EngineWidgets | Yes | UI控件 |
| `renderer` | WebGLRenderer | Yes | Three.js渲染器 |
| `scene` | Scene | Yes | Three.js场景 |
| `camera` | Camera | Yes | Three.js相机 |
| `event` | EngineEvent | Yes | 事件对象 |
| `selection` | EngineSelection | Yes | 物体选择器 |
| `clock` | EngineClock | Yes | 时钟对象 |
| `controller` | EngineController | Yes | 键鼠交互控制器 |
| `id` | number | Yes | 引擎实例唯一ID |

## 公共方法

### add / remove

```javascript
const layer = engine.add(new mapvthree.Polygon({ color: 'red' }));
engine.remove(layer);
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `object` | Object3D | Three.js 3D对象 |

### requestRender

请求一次渲染。在 `enableAnimationLoop: false` 时使用。

```javascript
engine.requestRender();
```

### 渲染监听器

```javascript
// 渲染更新前（适合更新数据、计算位置）
engine.addPrepareRenderListener(callback);
engine.removePrepareRenderListener(callback);

// 渲染前（适合最后调整）
engine.addBeforeRenderListener(callback);
engine.removeBeforeRenderListener(callback);
```

### renderVideo

```javascript
await engine.renderVideo({
    duration: 5000,
    fps: 60,
    resolution: [1920, 1080]
});
```

### dispose

释放全部资源。调用后引擎实例不可再使用。

## EngineMap 地图对象

`engine.map` 提供地图视野控制。

```javascript
// 中心点
engine.map.setCenter([116.404, 39.915]);
engine.map.getCenter();  // [lng, lat]

// 旋转角度
engine.map.setHeading(45);
engine.map.getHeading();

// 俯仰角
engine.map.setPitch(60);
engine.map.getPitch();

// 视野距离（米）
engine.map.setRange(5000);
engine.map.getRange();
```

### lookAt

```javascript
engine.map.lookAt([116.404, 39.915], {
    heading: 30,
    pitch: 60,
    range: 3000
});
```

### flyTo

```javascript
engine.map.flyTo([116.404, 39.915], {
    heading: 0,
    pitch: 45,
    range: 2000,
    duration: 2000,
    complete: () => console.log('飞行完成')
});
```

### setViewport

根据点集自动调整视野。

```javascript
engine.map.setViewport([
    [116.38, 39.90],
    [116.42, 39.92]
]);
```

### setBounds

限制可拖动范围。

```javascript
engine.map.setBounds([
    [116.30, 39.85],  // 西南角
    [116.50, 39.95]   // 东北角
]);
```

### 坐标转换

```javascript
// 地理坐标 -> 投影坐标
const projected = engine.map.projectArrayCoordinate([116.404, 39.915, 0]);
// 投影坐标 -> 地理坐标
const geographic = engine.map.unprojectArrayCoordinate(projected);
```

## EngineClock 时钟对象

```javascript
const now = engine.clock.currentTime;  // Date 对象
engine.clock.currentTime = new Date('2024-06-21T16:00:00');
```

## 完整示例

```javascript
import * as mapvthree from '@baidumap/mapv-three';

mapvthree.BaiduMapConfig.ak = '您的AK密钥';

const engine = new mapvthree.Engine(document.getElementById('map'), {
    map: {
        center: [116.404, 39.915],
        range: 5000,
        pitch: 45,
        heading: 0,
        projection: 'EPSG:3857'
    },
    rendering: {
        enableAnimationLoop: true,
        pixelRatio: window.devicePixelRatio,
        features: {
            antialias: { enabled: true, method: 'smaa' },
            bloom: { enabled: false }
        }
    }
});

// 添加底图
engine.add(new mapvthree.MapView({
    imageryProvider: new mapvthree.BingImageryTileProvider()
}));

// 添加多边形图层
const polygon = engine.add(new mapvthree.Polygon({
    color: 'red',
    opacity: 0.8,
    extrude: true,
    extrudeValue: 100
}));

polygon.dataSource = mapvthree.GeoJSONDataSource.fromGeoJSON({
    type: 'FeatureCollection',
    features: [{
        type: 'Feature',
        geometry: {
            type: 'Polygon',
            coordinates: [[
                [116.404, 39.915],
                [116.405, 39.915],
                [116.405, 39.916],
                [116.404, 39.916],
                [116.404, 39.915]
            ]]
        }
    }]
});

engine.map.flyTo([116.404, 39.915], {
    pitch: 60,
    range: 1000,
    duration: 2000
});

window.addEventListener('beforeunload', () => {
    engine.dispose();
});
```

## 注意事项

1. 添加到引擎的对象由引擎管理，不需要手动添加到 scene
2. 设置 `enableAnimationLoop: false` 时，需调用 `requestRender()` 触发渲染
3. 页面卸载时务必调用 `dispose()` 释放资源
4. 添加的渲染监听器不再需要时应手动移除
5. 地理坐标使用 `[经度, 纬度]` 格式
