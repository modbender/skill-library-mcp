# PlaceAutocomplete 地点自动补全组件

## 构造函数

```typescript
new PlaceAutocomplete(container: string | HTMLElement, options: PlaceAutocompleteOptions)
```

**参数**:

| 参数      | 类型                    | 必填 | 说明                  |
| --------- | ----------------------- | ---- | --------------------- |
| container | `string \| HTMLElement` | 是   | 容器元素或 CSS 选择器 |
| options   | `PlaceAutocompleteOptions` | 是   | 配置选项           |

**PlaceAutocompleteOptions**:

```typescript
interface PlaceAutocompleteOptions {
    map: BMap.Map | BMapGL.Map; // 地图实例（必填）
    placeholder?: string; // 输入框占位符，默认 '搜索地点'
    debounce?: number; // 防抖延迟（毫秒），默认 300
    location?: string; // 检索城市，默认使用地图中心所在城市
    citylimit?: boolean; // 是否严格限制在指定城市内，默认 false
    types?: string; // 结果类型过滤，默认 'all'
    minLength?: number; // 触发检索的最小字符数，默认 1
    showSuggestion?: boolean; // 是否显示下拉建议列表，默认 true
    suggestionCount?: number; // 建议列表最大条数，默认移动端 6 条，PC 端 10 条
}
```

---

## 方法

### search(keyword)

手动触发检索。

```typescript
search(keyword: string): void
```

**参数**:

| 参数    | 类型     | 必填 | 说明       |
| ------- | -------- | ---- | ---------- |
| keyword | `string` | 是   | 检索关键字 |

**示例**:

```javascript
autocomplete.search('百度大厦');
```

---

### setInputValue(value)

设置输入框的值（不触发检索）。

```typescript
setInputValue(value: string): void
```

**参数**:

| 参数  | 类型     | 必填 | 说明     |
| ----- | -------- | ---- | -------- |
| value | `string` | 是   | 输入值   |

**示例**:

```javascript
autocomplete.setInputValue('百度大厦');
```

---

### getInputValue()

获取输入框当前值。

```typescript
getInputValue(): string
```

**返回值**: 当前输入框的值

**示例**:

```javascript
const value = autocomplete.getInputValue();
console.log('当前输入:', value);
```

---

### setLocation(location)

设置检索城市。

```typescript
setLocation(location: string): void
```

**参数**:

| 参数     | 类型     | 必填 | 说明                           |
| -------- | -------- | ---- | ------------------------------ |
| location | `string` | 是   | 城市名称（如 '北京'、'上海'） |

**示例**:

```javascript
autocomplete.setLocation('北京');
```

---

### setCitylimit(citylimit)

设置是否严格限制在指定城市内搜索。

```typescript
setCitylimit(citylimit: boolean): void
```

**参数**:

| 参数      | 类型      | 必填 | 说明         |
| --------- | --------- | ---- | ------------ |
| citylimit | `boolean` | 是   | 是否限制城市 |

**示例**:

```javascript
autocomplete.setCitylimit(true);
```

---

### setTypes(types)

设置结果类型过滤。

```typescript
setTypes(types: string): void
```

**参数**:

| 参数  | 类型     | 必填 | 说明                        |
| ----- | -------- | ---- | --------------------------- |
| types | `string` | 是   | 类型过滤（如 'all'、'bus'） |

**示例**:

```javascript
autocomplete.setTypes('bus');
```

---

### show()

显示下拉列表。

```typescript
show(): void
```

---

### hide()

隐藏下拉列表。

```typescript
hide(): void
```

---

### destroy()

销毁组件，清理 DOM 和事件。

```typescript
destroy(): void
```

---

## 事件

### suggest

实时搜索建议更新时触发。

```typescript
autocomplete.on('suggest', (suggestions: PlaceAutocompleteEventSuggestion[]) => {
    console.log('搜索建议:', suggestions);
});
```

**回调参数**: `PlaceAutocompleteEventSuggestion[]` - 建议列表

---

### select

用户选中某个建议时触发。

```typescript
autocomplete.on('select', (suggestion: PlaceAutocompleteEventSuggestion) => {
    console.log('选中:', suggestion);

    // 通常在 select 事件中触发 PlaceSearch 检索
    if (suggestion.point) {
        search.searchNearby(suggestion.name, suggestion.point, 1000);
    } else {
        search.search(suggestion.name);
    }
});
```

**回调参数**: `PlaceAutocompleteEventSuggestion` - 选中的建议项

**典型使用场景**:
- 将选中的地点传递给 `PlaceSearch` 组件进行详细检索
- 在地图上添加标记
- 更新地图中心点

---

### highlight

用户通过键盘上下键切换高亮项时触发。

```typescript
autocomplete.on('highlight', (event: { from: HighlightItem | null, to: HighlightItem }) => {
    console.log('高亮切换:', event);
});
```

**回调参数**: 包含 `from`（上一个高亮项）和 `to`（当前高亮项）的对象

---

## 类型定义

### PlaceAutocompleteEventSuggestion

事件回调参数类型。

```typescript
interface PlaceAutocompleteEventSuggestion {
    province: string; // 省份
    city: string; // 城市
    district: string; // 区县
    name: string; // POI 名称（如"京酱肉丝"、"百度大厦"）
    street: string; // @deprecated 使用 name 字段代替，为兼容旧版保留
    business: string; // 商圈
    address: string; // 地址
    tag?: string; // 标签
    point?: BMapGL.Point; // 坐标（部分建议可能没有坐标）
    uid?: string; // POI 唯一标识
}
```

### HighlightItem

高亮切换事件数据。

```typescript
interface HighlightItem {
    index: number; // 高亮项在列表中的索引
    value: PlaceAutocompleteEventSuggestion; // 高亮项数据
}
```

---

## 使用示例

### 基础用法

```javascript
import BMapUIKit from '@baidumap/jsapi-ui-kit';

const map = new BMapGL.Map('map');
map.centerAndZoom(new BMapGL.Point(116.404, 39.915), 14);

// 创建自动补全组件
const autocomplete = new BMapUIKit.PlaceAutocomplete('#autocomplete-container', {
    map,
    placeholder: '搜索地点',
    location: '北京',
    citylimit: false,
});

// 监听建议更新
autocomplete.on('suggest', suggestions => {
    console.log('搜索建议:', suggestions);
});

// 监听用户选中
autocomplete.on('select', suggestion => {
    console.log('选中:', suggestion);
});
```

---

### 与 PlaceSearch 联动

```javascript
import BMapUIKit from '@baidumap/jsapi-ui-kit';

const map = new BMapGL.Map('map');
map.centerAndZoom(new BMapGL.Point(116.404, 39.915), 14);

// 自动补全组件
const autocomplete = new BMapUIKit.PlaceAutocomplete('#autocomplete-container', {
    map,
    placeholder: '搜索地点',
    debounce: 300,
    location: '北京',
});

// 搜索结果展示组件
const search = new BMapUIKit.PlaceSearch('#search-results', {
    map,
    pageCapacity: 10,
});

// 详情展示组件
const detail = new BMapUIKit.PlaceDetail('#detail-panel', {
    map,
});

// 选中建议后触发搜索
autocomplete.on('select', suggestion => {
    if (!suggestion) return;

    // 构建搜索关键词
    const keyword = suggestion.name || suggestion.address || autocomplete.getInputValue();

    if (suggestion.point) {
        // 如果有坐标，使用周边搜索
        search.searchNearby(keyword, suggestion.point, 1000);
    } else {
        // 否则使用关键词搜索
        search.search(keyword);
    }
});

// 搜索结果选中后展示详情
search.on('select', poi => {
    if (poi && poi.uid) {
        detail.setPlace(poi.uid);
    }
});
```

---

### 动态切换城市

```javascript
const autocomplete = new BMapUIKit.PlaceAutocomplete('#autocomplete-container', {
    map,
    location: '北京',
    citylimit: false,
});

// 切换搜索城市
document.getElementById('city-select').addEventListener('change', (e) => {
    const city = e.target.value;
    autocomplete.setLocation(city);

    // 同步移动地图到对应城市
    const cityCenters = {
        '北京': [116.404, 39.915],
        '上海': [121.473, 31.230],
        '广州': [113.264, 23.129],
    };
    const coords = cityCenters[city];
    if (coords) {
        map.centerAndZoom(new BMapGL.Point(coords[0], coords[1]), 14);
    }
});

// 切换城市限制
document.getElementById('citylimit-check').addEventListener('change', (e) => {
    autocomplete.setCitylimit(e.target.checked);
});
```

---

### 键盘导航支持

PlaceAutocomplete 组件内置了完整的键盘导航支持：

- **↓ (ArrowDown)**: 向下选择建议项
- **↑ (ArrowUp)**: 向上选择建议项
- **Enter**: 确认选中当前高亮的建议项
- **Escape**: 关闭下拉列表

```javascript
autocomplete.on('highlight', ({ from, to }) => {
    console.log(`高亮从 ${from?.index} 切换到 ${to.index}`);
    console.log('当前高亮项:', to.value.name);
});

autocomplete.on('select', suggestion => {
    console.log('用户确认选中:', suggestion.name);
});
```

---

## 完整示例 HTML

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>PlaceAutocomplete 示例</title>
  <style>
    #map { width: 100%; height: 500px; }
    #autocomplete-container { width: 300px; margin: 20px; }
  </style>
</head>
<body>
  <div id="autocomplete-container"></div>
  <div id="map"></div>

  <script src="https://api.map.baidu.com/api?v=1.0&type=webgl&ak=YOUR_AK"></script>
  <script type="module">
    import BMapUIKit from '@baidumap/jsapi-ui-kit';

    const map = new BMapGL.Map('map');
    map.centerAndZoom(new BMapGL.Point(116.404, 39.915), 14);
    map.enableScrollWheelZoom(true);

    const autocomplete = new BMapUIKit.PlaceAutocomplete('#autocomplete-container', {
        map,
        placeholder: '搜索地点',
        location: '北京',
    });

    autocomplete.on('select', suggestion => {
        console.log('选中:', suggestion);
        if (suggestion.point) {
            map.centerAndZoom(suggestion.point, 16);
            const marker = new BMapGL.Marker(suggestion.point);
            map.addOverlay(marker);
        }
    });
  </script>
</body>
</html>
```

---

## 注意事项

1. **必须先加载百度地图 API**: 确保在使用组件前已加载 BMap 或 BMapGL
2. **防抖优化**: 默认 300ms 防抖延迟，避免频繁请求。可通过 `debounce` 参数调整
3. **移动端适配**: 组件会自动检测设备类型，移动端建议列表默认显示 6 条，PC 端 10 条
4. **城市设置**:
   - `location` 为空时，使用地图中心所在城市
   - `citylimit: true` 时，严格限制在指定城市内搜索
5. **坐标可用性**: 并非所有建议都包含坐标（`point`），使用前需判断
6. **与 PlaceSearch 联动**: 选中建议后通常需要触发 PlaceSearch 进行详细检索
7. **内存管理**: 组件销毁时会自动清理所有事件监听器和 DOM 元素
