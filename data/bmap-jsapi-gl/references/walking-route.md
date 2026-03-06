# WalkingRoute 步行路线规划

用于规划两点之间的步行路线。

## 快速开始

```javascript
var walking = new BMapGL.WalkingRoute(map, {
    renderOptions: { map: map, autoViewport: true },
    onSearchComplete: function(results) {
        if (walking.getStatus() === BMAP_STATUS_SUCCESS) {
            var plan = results.getPlan(0);
            console.log('距离：' + plan.getDistance());
            console.log('耗时：' + plan.getDuration());
        }
    }
});

walking.search('王府井', '天安门');
```

## 构造函数

```javascript
new BMapGL.WalkingRoute(location, options)
```

步行使用通用配置，详见 [route-common.md](./route-common.md)。

## 注意事项

1. 不支持途经点（仅驾车支持）
2. 不支持路线拖拽（仅驾车支持）
3. `getRouteType()` 返回 `BMAP_ROUTE_TYPE_WALKING`（2）
