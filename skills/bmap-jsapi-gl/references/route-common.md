# 路径规划通用配置

本文档包含驾车、步行、骑行、公交四种路径规划的公共配置、方法和数据结构。

## 通用构造参数

所有路径规划类（DrivingRoute、WalkingRoute、RidingRoute、TransitRoute）都接受以下通用配置：

```javascript
new BMapGL.XxxRoute(location, {
    renderOptions: { ... },
    onSearchComplete: function(results, statusCode) { },
    onMarkersSet: function(pois) { },
    onPolylinesSet: function(routes) { },
    onInfoHtmlSet: function(poi, html) { },
    onResultsHtmlSet: function(html) { },
    language: BMAPGL_LANGUAGE_ZH
});
```

### location 参数

| 类型 | 说明 | 示例 |
|------|------|------|
| Map | 地图实例 | `map` |
| Point | 坐标点 | `new BMapGL.Point(116, 39)` |
| String | 城市名称 | `'北京市'` |
| Number | 城市代码 | `131` |

### renderOptions 渲染配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| map | Map | - | 用于展示结果的地图实例 |
| panel | HTMLElement | - | 结果列表的容器 DOM 元素 |
| autoViewport | boolean | `true` | 搜索完成后是否自动调整地图视野 |
| viewportOptions | Object | `{}` | 视野调整选项 |
| highlightMode | number | `1` | 展现策略：`BMAP_HIGHLIGHT_STEP`(1) 突出关键点，`BMAP_HIGHLIGHT_ROUTE`(2) 突出路段。**仅驾车/步行/骑行支持，公交不支持** |
| enableDragging | boolean | `false` | 是否启用路线拖拽功能（仅驾车支持） |

### 回调函数

| 参数 | 回调参数 | 说明 |
|------|----------|------|
| onSearchComplete | `(results, statusCode)` | 搜索完成时触发 |
| onMarkersSet | `(pois)` | 标注添加完成时触发 |
| onPolylinesSet | `(routes)` | 路线折线绑定完成时触发 |
| onInfoHtmlSet | `(poi, html)` | 标注信息窗口 HTML 创建完成时触发 |
| onResultsHtmlSet | `(html)` | 结果列表 HTML 创建完成时触发 |

**回调参数说明：**

| 参数 | 类型 | 说明 |
|------|------|------|
| results | RouteResult | 路线规划结果对象，包含起终点信息和路线方案 |
| statusCode | number | 搜索状态码，参见状态常量 |
| pois | Array\<LocalResultPoi\> | 起点、终点、途经点的 POI 数组 |
| routes | Array\<Route\> | 路线段数组 |
| poi | LocalResultPoi | 当前标注对应的 POI 对象 |
| html | string | 生成的 HTML 字符串 |

### 语言设置

| 常量 | 说明 |
|------|------|
| BMAPGL_LANGUAGE_ZH | 中文（默认） |
| BMAPGL_LANGUAGE_EN | 英文 |

## 通用方法

### 搜索相关

```javascript
// 发起路线规划搜索
route.search(start, end);

// 获取搜索状态
var status = route.getStatus();

// 获取搜索结果
var results = route.getResults();

// 清除上一次检索结果
route.clearResults();
```

**start/end 参数支持的类型：**

| 类型 | 说明 | 示例 |
|------|------|------|
| String | 地址/地名 | `'北京西站'` |
| Point | 坐标点 | `new BMapGL.Point(116.404, 39.915)` |
| LocalResultPoi | POI 对象 | 搜索返回的 POI 结果 |

> **⚠️ 重要**：start 和 end 必须使用**相同类型**。例如都用 String 或都用 Point，不能混用


## 通用数据结构

### RouteResult 搜索结果

通过 `onSearchComplete` 回调或 `route.getResults()` 获取：

```javascript
onSearchComplete: function(results) {
    var plan = results.getPlan(0);  // 获取 RoutePlan
}
```

| 方法 | 返回值 | 说明 |
|------|--------|------|
| getStart() | LocalResultPoi | 获取起点信息 |
| getEnd() | LocalResultPoi | 获取终点信息 |
| getStartStatus() | number | 获取起点状态 |
| getEndStatus() | number | 获取终点状态 |
| getNumPlans() | number | 获取路线方案数量 |
| getPlan(index) | RoutePlan | 获取第 index 个路线方案 |

### RoutePlan 路线方案

通过 `results.getPlan(index)` 获取：

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| getRoute(index) | number | Route | 获取第 index 个路线段 |
| getNumRoutes() | - | number | 获取路线段数量 |
| getDistance(format) | boolean | string/number | 获取总距离，format=false 返回米数，默认返回格式化字符串如"5.2公里" |
| getDuration(format) | boolean | string/number | 获取总耗时，format=false 返回秒数，默认返回格式化字符串 |
| getDragPois() | - | Array | 获取拖拽点信息数组 |

### Route 路线段

通过 `plan.getRoute(index)` 获取：

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| getStep(index) | number | Step | 获取第 index 个关键步骤 |
| getNumSteps() | - | number | 获取关键步骤数量 |
| getDistance(format) | boolean | string/number | 获取路线段距离 |
| getIndex() | - | number | 获取路线段索引 |
| getPolyline() | - | Polyline | 获取路线对应的折线覆盖物 |
| getPath() | - | Array\<Point\> | 获取路线坐标点数组 |
| getRouteType() | - | number | 获取路线类型 |
| getPlanIndex() | - | number | 获取所属方案的索引 |

### Step 关键步骤

通过 `route.getStep(index)` 获取：

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| getPosition() | - | Point | 获取关键点坐标 |
| getIndex() | - | number | 获取步骤索引 |
| getDescription(includeHtml) | boolean | string | 获取步骤描述，includeHtml=false 返回纯文本 |
| getDistance(format) | boolean | string/number | 获取到下一步骤的距离 |
| getRouteIndex() | - | number | 获取所属路线段的索引 |
| getPlanIndex() | - | number | 获取所属方案的索引 |

### LocalResultPoi 起终点信息

```javascript
{
    title: String,   // POI 名称/地址
    point: Point,    // 坐标点
    city: String,    // 所在城市
    uid: String,     // POI 唯一标识
    url: String,     // POI 详情页链接
    marker: Marker   // 关联的地图标注（onMarkersSet 回调中可用）
}
```

## 状态常量

### 搜索状态

参见 [constants.md](./constants.md) 中的搜索状态常量。

### 起终点状态

| 常量 | 值 | 说明 |
|------|-----|------|
| BMAP_ROUTE_STATUS_NORMAL | 0 | 正常，位置明确 |
| BMAP_ROUTE_STATUS_EMPTY | 1 | 无结果 |
| BMAP_ROUTE_STATUS_ADDRESS | 2 | 位置不确定，需用户选择 |

### 路线类型

| 常量 | 值 | 说明 |
|------|-----|------|
| BMAP_ROUTE_TYPE_WALKING | 2 | 步行路线 |
| BMAP_ROUTE_TYPE_DRIVING | 3 | 驾车路线 |
| BMAP_ROUTE_TYPE_RIDING | 6 | 骑行路线 |

