# Label 标签

批量标签组件，支持纯图标、纯文本、图标+文本三种模式。使用 SDF 文字渲染，适合大量标签的高性能渲染。

## 类型

| 类型 | 值 | 说明 |
|------|-----|------|
| 纯图标 | `'icon'` | 仅显示图标 |
| 纯文本 | `'text'` | 仅显示文本 |
| 图标+文本 | `'icontext'` | 同时显示图标和文本 |

## 基础用法

### 纯文本标签

```javascript
const textLabel = engine.add(new mapvthree.Label({
    type: 'text',
    textSize: 16,
    textFillStyle: 'rgb(255, 8, 8)',
    textStrokeStyle: 'rgba(0, 0, 0, 1)',
    textStrokeWidth: 2,
}));

const data = mapvthree.GeoJSONDataSource.fromGeoJSON([{
    type: 'Feature',
    geometry: { type: 'Point', coordinates: [116.404, 39.915] },
    properties: { text: '北京市' }
}]);
data.defineAttribute('text', 'text');
textLabel.dataSource = data;
```

### 图标+文本组合

```javascript
const comboLabel = engine.add(new mapvthree.Label({
    type: 'icontext',
    vertexIcons: true,
    textSize: 16,
    iconWidth: 40,
    iconHeight: 40,
    padding: [2, 2],
}));

const data = mapvthree.GeoJSONDataSource.fromGeoJSON([{
    type: 'Feature',
    geometry: { type: 'Point', coordinates: [116.404, 39.915] },
    properties: { icon: 'assets/icons/marker.png', text: '地点名称' }
}]);
data.defineAttributes({
    icon: 'icon',
    text: 'text'
});
comboLabel.dataSource = data;
```

## 构造参数

### 基础参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `type` | string | `'icon'` | `'icon'` / `'text'` / `'icontext'` |
| `flat` | boolean | `false` | 贴地渲染 |
| `vertexIcons` | boolean | `false` | 数据中携带 icon URL |
| `opacity` | number | `1` | 透明度 |
| `keepSize` | boolean | - | 保持固定屏幕大小 |
| `depthTest` | boolean | - | 深度测试 |

### 文字样式参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `textSize` | number | `16` | 文字大小（像素） |
| `textFamily` | string | `'sans-serif'` | 字体 |
| `textWeight` | string | `'400'` | 字重 |
| `textFillStyle` | string/array | `[255,255,255,1]` | 文字颜色 |
| `textStrokeStyle` | string/array | `[0,0,0,1]` | 描边颜色 |
| `textStrokeWidth` | number | `0` | 描边宽度 |
| `textAnchor` | string | `'center'` | 锚点位置 |
| `textAlign` | string | `'center'` | 对齐方式（`'left'`/`'center'`/`'right'`） |
| `textOffset` | array | `[0, 0]` | 文字偏移（像素） |
| `maxWidth` | number | - | 最大宽度（触发换行） |

**textAnchor 可选值：** `'center'`、`'left'`、`'right'`、`'top'`、`'bottom'`、`'top-left'`、`'top-right'`、`'bottom-left'`、`'bottom-right'`

### 图标样式参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `iconWidth` | number | `40` | 图标宽度 |
| `iconHeight` | number | `40` | 图标高度 |
| `mapSrc` | string | - | 默认图标 URL |
| `useIconScale` | boolean | `false` | 使用图标原始宽高比 |

### 布局参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `padding` | array | `[2, 2]` | 图标与文字间距 `[x, y]` |
| `textPadding` | array | `[0, 2]` | 文字内边距 |
| `offset` | array | `[0, 0]` | 坐标偏移 |
| `pixelOffset` | array | `[0, 0]` | 像素偏移 |
| `rotateZ` | number | `0` | 旋转角度（弧度） |

### 淡入淡出参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enableFade` | boolean | `false` | 启用淡入淡出（数据需包含 id） |
| `fadeDuration` | number | - | 动画时长（毫秒） |

## 数据级样式覆盖

每个数据项可携带独立样式属性，覆盖全局设置：

```javascript
const data = mapvthree.GeoJSONDataSource.fromGeoJSON([{
    type: 'Feature',
    geometry: { type: 'Point', coordinates: [116.404, 39.915] },
    properties: {
        text: '自定义样式',
        textSize: 20,
        textFillStyle: [255, 0, 0, 1],
        icon: 'assets/icon.png',
        iconSize: [50, 50],
        rotateZ: 0.78,
    }
}]);

data.defineAttributes({
    text: 'text',
    textSize: 'textSize',
    textFillStyle: 'textFillStyle',
    icon: 'icon',
    iconSize: 'iconSize',
    rotateZ: 'rotateZ',
});
```

支持的数据级属性：`text`、`textSize`、`textFillStyle`、`textStrokeStyle`、`textStrokeWidth`、`textAnchor`、`textOffset`、`textWeight`、`textFamily`、`icon`、`iconSize`、`iconOpacity`、`offset`、`rotateZ`、`maxWidth`

## 碰撞检测

```javascript
// 添加到碰撞检测系统
engine.rendering.collision.add(label, {
    margin: [5, 5]
}, 'poi-labels');

// 移除
engine.rendering.collision.remove(label);
```

## 事件交互

```javascript
label.addEventListener('click', (e) => {
    console.log('数据索引:', e.entity.index);
    console.log('原始数据:', e.entity.value);
});
```
