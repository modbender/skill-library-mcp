# PlaceDetail 地点详情组件

## 构造函数

```typescript
new PlaceDetail(container: string | HTMLElement, options: PlaceDetailOptions)
```

**参数**:

| 参数      | 类型                    | 必填 | 说明                  |
| --------- | ----------------------- | ---- | --------------------- |
| container | `string \| HTMLElement` | 是   | 容器元素或 CSS 选择器 |
| options   | `PlaceDetailOptions`    | 是   | 配置选项              |

**PlaceDetailOptions**:

```typescript
interface PlaceDetailOptions {
    map: BMap.Map | BMapGL.Map; // 地图实例（必填）
    theme?: string; // 主题名称，默认 'default'
    layout?: 'default' | 'compact'; // 布局模式，默认 'default'
    display?: PlaceDetailDisplayOptions;
}

interface PlaceDetailDisplayOptions {
    image?: boolean; // 显示图片
    title?: boolean; // 显示标题
    type?: boolean; // 显示类型
    address?: boolean; // 显示地址
    phone?: boolean; // 显示电话
    rating?: boolean; // 显示评分
    openingHours?: boolean; // 显示营业时间
    website?: boolean; // 显示网址
}
```

**布局模式**:

| 值          | 说明                       |
| ----------- | -------------------------- |
| `'default'` | 详细竖向布局，适合侧边栏   |
| `'compact'` | 紧凑横向布局，适合底部面板 |

---

## 方法

### setPlace(uidOrPoi)

加载并展示地点详情。

```typescript
setPlace(uidOrPoi: string | LocalResultPoiType): void
```

**参数**:

| 参数     | 类型                 | 必填 | 说明        |
| -------- | -------------------- | ---- | ----------- |
| uidOrPoi | `string`             | 是   | POI 的 UID  |
| uidOrPoi | `LocalResultPoiType` | 是   | 或 POI 对象 |

**示例**:

```javascript
// 通过 UID 加载（会发起网络请求）
detail.setPlace('abc123uid');

// 通过 POI 对象直接展示（无网络请求）
detail.setPlace({
    name: '天安门',
    address: '北京市东城区',
    point: {lng: 116.404, lat: 39.915},
    tel: '010-12345678',
});
```

---

### clear()

清空详情面板，显示空状态。

```typescript
clear(): void
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

详情加载完成时触发。

```typescript
detail.on('load', (data: PlaceDetailEventData) => {
    console.log('详情:', data.title, data.address);
});
```

---

## 类型定义

### PlaceDetailEventData

事件回调参数类型。

```typescript
interface PlaceDetailEventData {
    title: string; // 名称
    address: string; // 地址
    uid?: string; // POI 唯一标识
    point?: {lng: number; lat: number}; // 坐标
    tel?: string; // 电话
}
```

### LocalResultPoiType

传入 `setPlace()` 的 POI 对象类型（来自 BMap API）。

```typescript
// 参考 BMap.LocalResultPoi
interface LocalResultPoiType {
    name?: string;
    title?: string;
    addr?: string;
    address?: string;
    uid?: string;
    point?: {lng: number; lat: number};
    tel?: string;
    // ... 其他字段
}
```

---

## 使用示例

### 基础用法

```javascript
import {PlaceDetail} from '@baidumap/jsapi-ui-kit';

const map = new BMapGL.Map('map');
map.centerAndZoom(new BMapGL.Point(116.404, 39.915), 12);

const detail = new PlaceDetail('#detail-panel', {map});

detail.on('load', (data) => {
    console.log('加载完成:', data.title);
});

// 加载详情
detail.setPlace('poi_uid_string');
```

### 配置显示字段

```javascript
const detail = new PlaceDetail('#panel', {
    map,
    layout: 'compact',
    display: {
        image: true,
        title: true,
        address: true,
        phone: true,
        rating: false,
        website: false,
    },
});
```

### 与 PlaceSearch 联动

```javascript
import {PlaceSearch, PlaceDetail} from '@baidumap/jsapi-ui-kit';

const search = new PlaceSearch('#search', {map});
const detail = new PlaceDetail('#detail', {map});

// 点击搜索结果时展示详情
search.on('select', (poi) => {
    if (poi.uid) {
        detail.setPlace(poi.uid);
    } else {
        // 没有 UID 时直接展示已有信息
        detail.setPlace(poi);
    }
});
```

### 动态切换布局

```javascript
// 根据屏幕宽度选择布局
const layout = window.innerWidth < 768 ? 'compact' : 'default';
const detail = new PlaceDetail('#panel', {map, layout});
```
