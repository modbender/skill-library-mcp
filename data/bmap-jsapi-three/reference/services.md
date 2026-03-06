# LBS 服务参考

MapV-Three 提供地理编码、地点搜索、路线规划等 LBS 服务，支持百度地图和天地图数据源。

## 1. 地理编码（Geocoder）

```javascript
const geocoder = new mapvthree.services.Geocoder({
    apiSource: mapvthree.services.API_SOURCE_BAIDU
});
```

| 方法 | 参数 | 说明 |
|------|------|------|
| `getPoint(address, callback, city)` | address: string, callback: Function, city?: string | 地址转坐标 |
| `getLocation(point, callback, opts)` | point: [lng, lat], callback: Function | 坐标转地址 |

回调格式：`result.point` ([lng, lat])、`result.address` (string)

---

## 2. 本地搜索（LocalSearch）

```javascript
const localSearch = new mapvthree.services.LocalSearch({
    apiSource: mapvthree.services.API_SOURCE_BAIDU,
    pageCapacity: 10,
    pageNum: 0,
    renderOptions: {
        engine: engine,
        autoViewport: true,
        enableRender: true,
    }
});
```

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `search(keyword, options)` | keyword: string | Promise\<Object\> | 搜索 POI |
| `setPageCapacity(capacity)` | capacity: number | void | 设置每页结果数 |
| `setPageNum(pageNum)` | pageNum: number | void | 设置页码 |
| `getResults()` | - | Object | 获取最后搜索结果 |
| `clearResults()` | - | void | 清除结果和标记 |

搜索结果：`result.pois[]` 包含 `name, point, province, city, area, address, uid`

---

## 3. 自动完成（AutoComplete）

仅支持百度地图 API。

```javascript
const autoComplete = new mapvthree.services.AutoComplete({
    input: 'searchInput',
    types: ['ALL'],
    maxResults: 10,
    debounceTime: 200,
    onSearchComplete: (results) => { /* ... */ },
    onError: (error) => { /* ... */ }
});
```

| 方法 | 参数 | 说明 |
|------|------|------|
| `search(keyword)` | keyword: string | 执行搜索 |
| `setTypes(types)` | types: string[] | 设置搜索类型 |
| `getResults()` | - | 获取建议结果 |

---

## 4. 行政区划边界（Boundary）

```javascript
const boundary = new mapvthree.services.Boundary({
    apiSource: mapvthree.services.API_SOURCE_BAIDU
});

boundary.get('北京市', (result) => {
    result.boundaries; // [[[lng, lat], ...], ...]
});
```

---

## 5. 行政区划图层（DistrictLayer）

```javascript
const district = new mapvthree.services.DistrictLayer({
    name: '(山东省)',
    kind: 0,  // 0=省级, 1=市级, 2=区县级
    apiSource: mapvthree.services.API_SOURCE_BAIDU,
    renderOptions: {
        engine: engine,
        fillColor: '#618bf8',
        fillOpacity: 0.6,
        autoViewport: true,
    }
});

district.renderMap();   // 手动渲染
district.clearMap();    // 清除图层
```

---

## 6. 驾车路线规划（DrivingRoute）

```javascript
const drivingRoute = new mapvthree.services.DrivingRoute({
    apiSource: mapvthree.services.API_SOURCE_BAIDU,
    renderOptions: { engine: engine, autoViewport: true }
});

const result = await drivingRoute.search(
    new THREE.Vector3(116.404, 39.915, 0),
    new THREE.Vector3(116.414, 39.925, 0),
    { waypoints: [new THREE.Vector3(116.409, 39.920, 0)] }
);
// result.routes[0].distance (米), result.routes[0].duration (秒)
```

---

## 7. 骑行路线规划（RidingRoute）

仅支持百度地图。

```javascript
const ridingRoute = new mapvthree.services.RidingRoute({
    renderOptions: { engine: engine, autoViewport: true }
});
await ridingRoute.search(start, end);
```

---

## 8. 步行路线规划（WalkingRoute）

仅支持百度地图。

```javascript
const walkingRoute = new mapvthree.services.WalkingRoute({
    renderOptions: { engine: engine, autoViewport: true }
});
await walkingRoute.search(start, end);
```

---

## 9. 公交路线规划（TransitRoute）

```javascript
const transitRoute = new mapvthree.services.TransitRoute({
    apiSource: mapvthree.services.API_SOURCE_BAIDU,
    renderOptions: { engine: engine, autoViewport: true }
});

const result = await transitRoute.search(start, end);
// result.routes[].steps[].instruction, result.routes[].steps[].stations[]
```

---

## 代码示例

### 地址转坐标并跳转

```javascript
const geocoder = new mapvthree.services.Geocoder({
    apiSource: mapvthree.services.API_SOURCE_BAIDU,
});

geocoder.getPoint('北京市朝阳区建国路1号', (result) => {
    if (result && result.point) {
        engine.map.setCenter(result.point);
        engine.map.setRange(500);
    }
}, '北京市');
```

### 搜索周边 POI

```javascript
const localSearch = new mapvthree.services.LocalSearch({
    apiSource: mapvthree.services.API_SOURCE_BAIDU,
    pageCapacity: 20,
    renderOptions: { engine: engine, autoViewport: true, enableRender: true }
});

const result = await localSearch.search('餐厅');
result.pois.forEach(poi => console.log(poi.name, poi.point));
```

### 多数据源切换

```javascript
// 配置全局默认数据源
mapvthree.services.setApiSource(mapvthree.services.API_SOURCE_BAIDU);

// 之后创建的服务使用全局配置
const geocoder = new mapvthree.services.Geocoder();
```

## 数据源支持情况

| 服务 | 百度地图 | 天地图 |
|------|:------:|:------:|
| Geocoder | Yes | Yes |
| LocalSearch | Yes | Yes |
| Boundary | Yes | Yes |
| DistrictLayer | Yes | Yes |
| DrivingRoute | Yes | Yes |
| TransitRoute | Yes | Yes |
| AutoComplete | Yes | - |
| RidingRoute | Yes | - |
| WalkingRoute | Yes | - |
