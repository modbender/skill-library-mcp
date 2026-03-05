# TransitRoute 公交路线规划

用于规划两点之间的公交出行路线，支持市内公交和跨城公交（火车、飞机、大巴）。

## 快速开始

```javascript
var transit = new BMapGL.TransitRoute(map, {
    policy: BMAP_TRANSIT_POLICY_LEAST_TRANSFER,
    renderOptions: { map: map, autoViewport: true },
    onSearchComplete: function(results) {
        if (transit.getStatus() === BMAP_STATUS_SUCCESS) {
            var plan = results.getPlan(0);
            console.log('线路：' + plan.getLinesTitle());
            console.log('耗时：' + plan.getDuration());
        }
    }
});

var start = new BMapGL.Point(116.31, 40.06);
var end = new BMapGL.Point(116.50, 39.89);
transit.search(start, end);
```

## 构造函数

```javascript
new BMapGL.TransitRoute(location, options)
```

公交使用通用配置，详见 [route-common.md](./route-common.md)。

### 公交专有配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| policy | number | `0` | 市内公交策略 |
| intercityPolicy | number | `0` | 跨城公交策略 |
| transitTypePolicy | number | `0` | 跨城交通方式策略 |
| pageCapacity | number | `100` | 返回方案数（1-100） |

## 公交专有方法

| 方法 | 说明 |
|------|------|
| setPolicy(policy) | 设置市内公交策略 |
| setIntercityPolicy(policy) | 设置跨城公交策略 |
| setTransitTypePolicy(policy) | 设置跨城交通方式策略 |
| setPageCapacity(num) | 设置返回方案数 |

## 策略枚举

### 市内公交策略

| 常量 | 值 | 说明 |
|------|-----|------|
| BMAP_TRANSIT_POLICY_RECOMMEND | 0 | 推荐方案 |
| BMAP_TRANSIT_POLICY_LEAST_TRANSFER | 1 | 最少换乘 |
| BMAP_TRANSIT_POLICY_LEAST_WALKING | 2 | 最少步行 |
| BMAP_TRANSIT_POLICY_AVOID_SUBWAYS | 3 | 不乘地铁 |
| BMAP_TRANSIT_POLICY_LEAST_TIME | 4 | 最少时间 |
| BMAP_TRANSIT_POLICY_FIRST_SUBWAYS | 5 | 地铁优先 |

### 跨城策略

| 常量 | 值 | 说明 |
|------|-----|------|
| BMAP_INTERCITY_POLICY_LEAST_TIME | 0 | 时间短 |
| BMAP_INTERCITY_POLICY_EARLY_START | 1 | 出发早 |
| BMAP_INTERCITY_POLICY_CHEAP_PRICE | 2 | 价格低 |

### 跨城交通方式策略

| 常量 | 值 | 说明 |
|------|-----|------|
| BMAP_TRANSIT_TYPE_POLICY_TRAIN | 0 | 火车优先 |
| BMAP_TRANSIT_TYPE_POLICY_AIRPLANE | 1 | 飞机优先 |
| BMAP_TRANSIT_TYPE_POLICY_COACH | 2 | 大巴优先 |

## TransitRoutePlan 公交方案

通过 `results.getPlan(index)` 获取：

```javascript
onSearchComplete: function(results) {
    var plan = results.getPlan(0);  // 获取第一个方案
    console.log(plan.getLinesTitle());
}
```

| 方法 | 返回值 | 说明 |
|------|--------|------|
| getNumTotal() | number | 所有交通段数量（步行+公交） |
| getTotal(index) | Line \| Route | 获取第 index 个交通段 |
| getTotalType(index) | number | 获取第 index 段的类型 |
| getNumLines() | number | 公交线路数量 |
| getLine(index) | Line | 获取第 index 条公交线路 |
| getNumRoutes() | number | 步行路线数量 |
| getRoute(index) | Route | 获取第 index 条步行路线 |
| getDistance(format) | string \| number | 总距离 |
| getDuration(format) | string \| number | 总耗时 |
| getWalkDistance() | string | 步行总距离（格式化） |
| getLinesTitle() | string | 线路标题（格式：'线路1 → 线路2'） |
| getDescription(includeHtml) | string | 方案描述 |

### 交通段类型

| 常量 | 值 | 说明 |
|------|-----|------|
| BMAP_TRANSIT_PLAN_TYPE_ROUTE | 0 | 步行路段 |
| BMAP_TRANSIT_PLAN_TYPE_LINE | 1 | 公交/线路路段 |

## Line 公交线路

通过 `plan.getLine(index)` 或 `plan.getTotal(index)` 获取：

```javascript
var line = plan.getLine(0);  // 获取第一条公交线路
console.log(line.getTitle());
console.log('经过站数：' + line.getNumViaStops());
```

| 方法 | 返回值 | 说明 |
|------|--------|------|
| getTitle() | string | 线路名称 |
| getDistance(format) | string \| number | 线路距离 |
| getNumViaStops() | number | 经过的中间站点数 |
| getGetOnStop() | Object | 上车站 {title, point} |
| getGetOffStop() | Object | 下车站 {title, point} |
| getPathIn() | Array | 线路坐标点数组 |
| getPolyline() | Polyline | 线路折线覆盖物 |

**`line.type` 属性** - 线路类型：

| 常量 | 值 | 说明 |
|------|-----|------|
| BMAP_LINE_TYPE_BUS | 0 | 公交 |
| BMAP_LINE_TYPE_SUBWAY | 1 | 地铁 |
| BMAP_LINE_TYPE_FERRY | 2 | 渡轮 |
| BMAP_LINE_TYPE_TRAIN | 3 | 火车 |
| BMAP_LINE_TYPE_AIRPLANE | 4 | 飞机 |
| BMAP_LINE_TYPE_COACH | 5 | 大巴 |

## 出行方案类型

通过 `results.getTransitType()` 获取：

| 常量 | 值 | 说明 |
|------|-----|------|
| BMAP_TRANSIT_TYPE_IN_CITY | 0 | 市内换乘 |
| BMAP_TRANSIT_TYPE_CROSS_CITY | 1 | 跨城换乘 |

## 回调函数差异

公交回调与其他路线不同：

```javascript
onMarkersSet: function(pois, transPois) {
    // pois: 起终点 POI 数组
    // transPois: 换乘点 POI 数组
}

onPolylinesSet: function(lines, routes) {
    // lines: 公交线路数组
    // routes: 步行路线数组
}
```

## 注意事项

1. **不支持 String 类型**：start/end 只能使用 Point 或 LocalResultPoi，不支持地址字符串
2. **不支持 highlightMode**：公交路线不支持展现策略配置
3. **不支持途经点**：公交路线不支持 waypoints
4. **不支持路线拖拽**：公交路线不支持 enableDragging
5. **自动判断市内/跨城**：系统自动识别并应用对应策略
