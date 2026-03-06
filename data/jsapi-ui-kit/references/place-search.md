# PlaceSearch 地点检索组件

## 构造函数

```typescript
new PlaceSearch(container: string | HTMLElement, options: PlaceSearchOptions)
```

**参数**:

| 参数      | 类型                    | 必填 | 说明                  |
| --------- | ----------------------- | ---- | --------------------- |
| container | `string \| HTMLElement` | 是   | 容器元素或 CSS 选择器 |
| options   | `PlaceSearchOptions`    | 是   | 配置选项              |

**PlaceSearchOptions**:

```typescript
interface PlaceSearchOptions {
    map: BMap.Map | BMapGL.Map; // 地图实例（必填）
    theme?: string; // 主题名称，默认 'default'
    pageCapacity?: number; // 每页结果条数，默认 10
    pageNum?: number; // 页码，默认 0
    display?: PlaceSearchDisplayOptions;
}

interface PlaceSearchDisplayOptions {
    title?: boolean; // 显示标题
    address?: boolean; // 显示地址
    type?: boolean; // 显示类型
    phone?: boolean; // 显示电话
    rating?: boolean; // 显示评分
    openingHours?: boolean; // 显示营业时间
}
```

---

## 方法

### search(keyword, option?)

关键字检索。

```typescript
search(keyword: string, option?: { city?: string }): Promise<void>
```

**参数**:

| 参数        | 类型     | 必填 | 说明             |
| ----------- | -------- | ---- | ---------------- |
| keyword     | `string` | 是   | 检索关键字       |
| option.city | `string` | 否   | 城市名称（预留） |

**示例**:

```javascript
await search.search('餐厅');
await search.search('咖啡', {city: '北京'});
```

---

### searchNearby(keyword, center, radius?)

周边检索。

```typescript
searchNearby(
  keyword: string,
  center: BMap.Point | BMapGL.Point,
  radius?: number
): Promise<void>
```

**参数**:

| 参数    | 类型     | 必填 | 说明                  |
| ------- | -------- | ---- | --------------------- |
| keyword | `string` | 是   | 检索关键字            |
| center  | `Point`  | 是   | 圆心坐标              |
| radius  | `number` | 否   | 半径（米），默认 2000 |

**示例**:

```javascript
const center = new BMapGL.Point(116.404, 39.915);
await search.searchNearby('酒店', center, 1000);
```

---

### searchInBounds(keyword, bounds)

范围检索。

```typescript
searchInBounds(
  keyword: string,
  bounds: { sw: BMapGL.Point, ne: BMapGL.Point }
): Promise<void>
```

**参数**:

| 参数      | 类型     | 必填 | 说明       |
| --------- | -------- | ---- | ---------- |
| keyword   | `string` | 是   | 检索关键字 |
| bounds    | `object` | 是   | 矩形范围   |
| bounds.sw | `Point`  | 是   | 西南角坐标 |
| bounds.ne | `Point`  | 是   | 东北角坐标 |

**示例**:

```javascript
await search.searchInBounds('商场', {
    sw: new BMapGL.Point(116.3, 39.8),
    ne: new BMapGL.Point(116.5, 40.0),
});
```

---

### destroy()

销毁组件，清理 DOM 和事件。

```typescript
destroy(): void
```

---

## 事件

### load

检索完成时触发。

```typescript
search.on('load', (list: PlaceSearchEventPoi[]) => {
    console.log('检索结果:', list);
});
```

### select

用户点击列表项时触发。

```typescript
search.on('select', (poi: PlaceSearchEventPoi) => {
    console.log('选中:', poi.title, poi.point);
});
```

---

## 类型定义

### PlaceSearchEventPoi

事件回调参数类型。

```typescript
interface PlaceSearchEventPoi {
    title: string; // 名称
    address: string; // 地址
    uid?: string; // POI 唯一标识
    point?: BMapGL.Point; // 坐标
    tel?: string; // 电话
}
```

---

## 使用示例

### 基础用法

```javascript
import {PlaceSearch} from '@baidumap/jsapi-ui-kit';

const map = new BMapGL.Map('map');
map.centerAndZoom(new BMapGL.Point(116.404, 39.915), 12);

const search = new PlaceSearch('#search-panel', {map});

search.on('load', (list) => {
    console.log(`共 ${list.length} 条结果`);
});

search.on('select', (poi) => {
    map.centerAndZoom(poi.point, 16);
});

search.search('美食');
```

### 配置显示字段

```javascript
const search = new PlaceSearch('#panel', {
    map,
    pageCapacity: 5,
    display: {
        title: true,
        address: true,
        phone: true,
        rating: false,
        openingHours: false,
    },
});
```

### 周边检索联动

```javascript
// 点击地图时，在点击位置周边检索
map.addEventListener('click', (e) => {
    search.searchNearby('餐厅', e.latlng, 500);
});
```
