# DrivingRoute 驾车路线规划

用于规划两点之间的驾车路线，支持途经点、多种策略选择和路况信息显示。

## 快速开始

```javascript
var driving = new BMapGL.DrivingRoute(map, {
    policy: BMAP_DRIVING_POLICY_AVOID_CONGESTION,
    renderOptions: { map: map, autoViewport: true },
    onSearchComplete: function(results) {
        if (driving.getStatus() === BMAP_STATUS_SUCCESS) {
            var plan = results.getPlan(0);
            console.log('距离：' + plan.getDistance());
            console.log('耗时：' + plan.getDuration());
        }
    }
});

var start = new BMapGL.Point(116.33, 39.90);
var end = new BMapGL.Point(116.61, 40.08);
driving.search(start, end);
```

## 构造函数

```javascript
new BMapGL.DrivingRoute(location, options)
```

驾车继承使用通用配置，详见 [route-common.md](./route-common.md)。

### 驾车专有配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| policy | number | `0` | 驾车策略，详见下方策略枚举 |
| alternatives | number | `0` | 返回的备选路线数量 |
| enableTraffic | boolean | `false` | 是否启用路况信息 |

### renderOptions 扩展配置

| 参数 | 类型 | 说明 |
|------|------|------|
| enableDragging | boolean | 是否启用路线拖拽功能 |
| lineLayerStyle.strokeTextureUrl | string | 线纹理 URL |
| lineLayerStyle.lineLayerColor.color | string | 线颜色（十六进制） |
| lineLayerStyle.lineLayerColor.opacity | number | 线透明度（0-1） |

## 驾车策略枚举

| 常量 | 值 | 说明 |
|------|-----|------|
| BMAP_DRIVING_POLICY_DEFAULT | 0 | 默认策略 |
| BMAP_DRIVING_POLICY_DESTANCE | 2 | 最短距离 |
| BMAP_DRIVING_POLICY_AVOID_HIGHWAYS | 3 | 避开高速 |
| BMAP_DRIVING_POLICY_FIRST_HIGHWAYS | 4 | 优先高速 |
| BMAP_DRIVING_POLICY_AVOID_CONGESTION | 5 | 避开拥堵 |
| BMAP_DRIVING_POLICY_AVOID_PAY | 6 | 避开收费 |
| BMAP_DRIVING_POLICY_HIGHWAYS_AVOID_CONGESTION | 7 | 高速优先 + 避开拥堵 |
| BMAP_DRIVING_POLICY_AVOID_HIGHWAYS_CONGESTION | 8 | 避开高速 + 避开拥堵 |
| BMAP_DRIVING_POLICY_AVOID_CONGESTION_PAY | 9 | 避开拥堵 + 避开收费 |
| BMAP_DRIVING_POLICY_AVOID_HIGHWAYS_CONGESTION_PAY | 10 | 避开高速 + 避开拥堵 + 避开收费 |
| BMAP_DRIVING_POLICY_AVOID_HIGHWAYS_PAY | 11 | 避开高速 + 避开收费 |

## 途经点搜索

驾车路线支持设置最多 10 个途经点：

```javascript
driving.search(start, end, {
    waypoints: [
        new BMapGL.Point(116.42, 39.92),
        new BMapGL.Point(116.45, 39.91)
    ]
});
```

## 路况状态常量

| 常量 | 值 | 说明 |
|------|-----|------|
| BMAP_TRAFFICE_STATUS_NONE | 0 | 无路况信息 |
| BMAP_TRAFFICE_STATUS_NORMAL | 1 | 畅通 |
| BMAP_TRAFFICE_STATUS_SLOW | 2 | 缓行 |
| BMAP_TRAFFICE_STATUS_JAM | 3 | 拥堵 |

## 注意事项

1. **不支持 String 类型**：start/end 只能使用 Point 或 LocalResultPoi，不支持地址字符串
2. **途经点**：仅驾车支持，最多 10 个
3. **路线拖拽**：仅驾车支持 `enableDragging`
4. `getRouteType()` 返回 `BMAP_ROUTE_TYPE_DRIVING`（3）
5. **收费信息**：`getToll()`、`getTollDistance()` 仅 TruckRoute（货车）支持，普通驾车不支持
