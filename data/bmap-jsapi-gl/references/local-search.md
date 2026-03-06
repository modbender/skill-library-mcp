# LocalSearch 本地检索

用于 POI 检索，支持普通检索、范围检索和周边检索。

## 快速开始

```javascript
var local = new BMapGL.LocalSearch(map, {
    renderOptions: { map: map, autoViewport: true },
    onSearchComplete: function(results) {
        if (local.getStatus() === BMAP_STATUS_SUCCESS) {
            for (var i = 0; i < results.getCurrentNumPois(); i++) {
                console.log(results.getPoi(i).title);
            }
        }
    }
});
local.search('餐厅');
```

## 构造函数

```javascript
new BMapGL.LocalSearch(location, options)
```

### location 参数

| 类型 | 说明 |
|------|------|
| Map | 地图实例，以当前视野为检索范围 |
| Point | 坐标点，以所在城市为范围 |
| String | 城市名称，如 `"北京市"` |
| Number | 城市代码（如北京 131、上海 289） |

### options 配置

通用配置（renderOptions、回调函数、language）参见 [route-common.md](./route-common.md)。

**LocalSearch 专有配置：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| pageCapacity | number | `10` | 每页结果数（1-100） |
| pageNum | number | `0` | 初始页码 |

**renderOptions 扩展：**

| 参数 | 类型 | 说明 |
|------|------|------|
| selectFirstResult | boolean | 是否自动选中第一个结果 |

## 检索方法

### 普通检索

```javascript
local.search(keyword)
```

在构造函数指定的区域内检索，支持多关键字（最多 10 个）。

```javascript
// 单关键字
local.search('银行');

// 多关键字
local.search(['银行', '酒店']);
```

### 范围检索

```javascript
local.searchInBounds(keyword, bounds)
```

在指定矩形范围内检索。

```javascript
var bounds = new BMapGL.Bounds(
    new BMapGL.Point(116.30, 39.85),
    new BMapGL.Point(116.50, 39.95)
);
local.searchInBounds('餐厅', bounds);
```

### 周边检索

```javascript
local.searchNearby(keyword, center, radius)
```

以指定点为圆心、指定半径范围内检索。

```javascript
var center = new BMapGL.Point(116.404, 39.915);
local.searchNearby('超市', center, 1000);  // 半径 1000 米
```

## 实例方法

| 方法 | 说明 |
|------|------|
| getResults() | 获取结果（多关键字返回数组） |
| getStatus() | 获取状态码 |
| clearResults() | 清除结果 |
| gotoPage(num) | 跳转到指定页 |
| setPageCapacity(num) / getPageCapacity() | 设置/获取每页结果数 |
| setPageNum(num) / getPageNum() | 设置/获取页码 |
| setLocation(loc) | 设置检索区域 |
| enableAutoViewport() / disableAutoViewport() | 启用/禁用自动调整视野 |
| enableFirstResultSelection() / disableFirstResultSelection() | 启用/禁用自动选中首个结果 |

## LocalResult 结果对象

### 方法

| 方法 | 返回值 | 说明 |
|------|--------|------|
| getPoi(index) | Object | 获取第 index 个 POI（坐标已转换） |
| getNumPois() | number | 结果总数 |
| getCurrentNumPois() | number | 当前页结果数 |
| getNumPages() | number | 总页数 |
| getPageIndex() | number | 当前页索引 |
| getCenter() | Point | 获取周边检索中心点（坐标已转换） |
| getBounds() | Bounds | 获取范围检索的范围（坐标已转换） |
| getCityList() | Array | 获取城市列表（跨城检索时） |

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| keyword | string | 检索关键字 |
| city | string | 结果所在城市 |
| province | string | 结果所在省份 |
| center | Point | 周边检索的中心点（原始坐标） |
| radius | number | 周边检索的半径 |
| bounds | Bounds | 范围检索的范围（原始坐标） |
| viewport | Bounds | 地图最佳视野 |
| moreResultsUrl | string | 更多结果 URL |
| suggestions | Array | 搜索建议列表 |

## POI 对象

| 属性 | 类型 | 说明 |
|------|------|------|
| title | string | 名称 |
| uid | string | 唯一标识 |
| point | Point | 坐标 |
| address | string | 地址 |
| city | string | 城市 |
| province | string | 省份 |
| phoneNumber | string | 电话 |
| url | string | POI 详情页 URL |
| detailUrl | string | 百度地图详情页 URL |
| type | number | 类型，见下方常量 |
| isAccurate | boolean | 是否精确定位 |
| marker | Marker | 对应的地图标注（设置 renderOptions.map 后有效） |

### POI 类型常量

| 常量 | 值 | 说明 |
|------|-----|------|
| BMAP_POI_TYPE_NORMAL | 0 | 普通 POI |
| BMAP_POI_TYPE_BUSSTOP | 1 | 公交站 |
| BMAP_POI_TYPE_SUBSTOP | 2 | 地铁站 |

## 状态常量

参见 [constants.md](./constants.md)。

## 注意事项

1. 多关键字最多 10 个，结果返回 LocalResult 数组
2. 周边检索半径最大 100000 米，默认 2000 米
3. 状态码为 `BMAP_STATUS_CITY_LIST` 时需通过 `getCityList()` 选择城市后重新检索
4. **坐标转换**：使用 `getPoi()`、`getCenter()`、`getBounds()` 方法获取的坐标会自动转换为当前地图坐标系；直接访问 `center`、`bounds` 属性则是原始 BD09 坐标
