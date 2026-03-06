# RidingRoute 骑行路线规划

用于规划两点之间的骑行路线。

## 快速开始

```javascript
var riding = new BMapGL.RidingRoute(map, {
    renderOptions: { map: map, autoViewport: true },
});

riding.search('朝阳公园', '奥林匹克公园');
```

## 构造函数

```javascript
new BMapGL.RidingRoute(location, options)
```

骑行使用通用配置，详见 [route-common.md](./route-common.md)。

## 注意事项

1. 不支持途经点（仅驾车支持）
2. 不支持路线拖拽（仅驾车支持）
3. `getRouteType()` 返回 `BMAP_ROUTE_TYPE_RIDING`（6）
