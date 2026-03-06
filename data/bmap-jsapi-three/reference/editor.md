# Editor 编辑器

## 概述

Editor 是地图编辑器组件，提供要素绘制、编辑功能。支持多边形、线、点、圆、矩形等几何类型。

## 绘制类型

```javascript
mapvthree.Editor.DrawerType = {
    POLYGON: 'polygon',
    LINE: 'line',
    POINT: 'point',
    CIRCLE: 'circle',
    RECTANGLE: 'rectangle'
}
```

## 基本用法

```javascript
const editor = engine.add(new mapvthree.Editor({
    type: mapvthree.Editor.DrawerType.POLYGON,
    enableMidpointHandles: true,
    singleMode: false
}));

editor.setStyle({
    fillColor: '#ff0000',
    fillOpacity: 0.5,
    strokeColor: '#ffffff',
    strokeWidth: 2
});

editor.start({ continuous: false });
```

## 构造参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `type` | string | `'polygon'` | 默认绘制类型 |
| `enableMidpointHandles` | boolean | `false` | 启用中点标记 |
| `singleMode` | boolean | `false` | 单要素模式 |
| `showLabel` | boolean | `false` | 显示测量标签 |
| `continuousDrawing` | boolean | `false` | 连续绘制模式 |
| `renderOptions` | object | - | 渲染选项 |

## 样式配置

| 属性 | 类型 | 说明 | 适用类型 |
|------|------|------|----------|
| `fillColor` | string | 填充颜色 | polygon, circle, rectangle, point |
| `fillOpacity` | number | 填充透明度 (0-1) | polygon, circle, rectangle, point |
| `strokeColor` | string | 边框颜色 | 全部 |
| `strokeWidth` | number | 边框宽度（像素） | 全部 |
| `strokeOpacity` | number | 边框透明度 (0-1) | 全部 |
| `pointRadius` | number | 点半径 | point |

```javascript
// 为特定类型设置样式
editor.setStyle({ strokeColor: '#00ff00', strokeWidth: 3 }, mapvthree.Editor.DrawerType.LINE);

// 获取样式
const style = editor.getStyle(mapvthree.Editor.DrawerType.POLYGON);

// 更新要素样式（合并）
editor.updateFeatureStyle('feature-id', { fillColor: '#00ff00' });

// 替换要素样式
editor.updateFeatureStyle('feature-id', { fillColor: '#0000ff' }, true);
```

## 编辑功能

```javascript
// 编辑所有要素
editor.enableEdit();

// 编辑指定 ID 的要素
editor.enableEdit('feature-id');

// 使用过滤函数
editor.enableEdit((feature) => feature.geometry.type === 'Polygon');

// 关闭编辑
editor.disableEdit();
```

## 键盘快捷键

| 快捷键 | 功能 | 适用场景 |
|--------|------|----------|
| **Delete** | 删除选中顶点 | 编辑模式 |
| **Escape** | 取消当前绘制或编辑 | 绘制/编辑中 |
| **右键点击** | 撤销上一步操作 | 绘制模式 |

## 数据管理

```javascript
// 导出所有数据（GeoJSON）
const allData = editor.exportData();

// 导出特定类型
const polygonData = editor.exportData(mapvthree.Editor.DrawerType.POLYGON);

// 导入数据
editor.importData(geojson, { clear: true, fitBounds: true });

// 删除
editor.delete();                              // 删除所有
editor.delete(mapvthree.Editor.DrawerType.POLYGON);  // 删除特定类型
editor.deleteById('feature-id');              // 根据 ID 删除
editor.deleteById(['feature-1', 'feature-2']);

// 显示/隐藏
editor.show();
editor.hide(mapvthree.Editor.DrawerType.LINE);
```

## 状态查询

| 属性 | 类型 | 说明 |
|------|------|------|
| `isDrawing` | boolean | 是否正在绘制 |
| `isEditing` | boolean | 是否正在编辑 |

## 事件

| 事件 | 参数 | 说明 |
|------|------|------|
| `start` | `{drawerType, options}` | 开始绘制 |
| `created` | `{feature}` | 要素创建完成 |
| `update` | `{feature}` | 要素更新 |
| `delete` | - | 要素删除 |
| `featureClick` | `{featureId}` | 点击要素 |

```javascript
editor.addEventListener('created', (e) => console.log('要素创建:', e.feature));
editor.addEventListener('featureClick', (e) => editor.enableEdit(e.featureId));
```

## 完整示例

```javascript
const engine = new mapvthree.Engine(document.getElementById('map'), {
    map: { center: [116.516, 39.799], range: 500 }
});

const editor = engine.add(new mapvthree.Editor({
    type: mapvthree.Editor.DrawerType.POLYGON,
    enableMidpointHandles: true
}));

editor.setStyle({
    fillColor: '#ff0000',
    fillOpacity: 0.5,
    strokeColor: '#ffffff',
    strokeWidth: 2
});

editor.addEventListener('created', () => {
    console.log('当前数据:', JSON.stringify(editor.exportData(), null, 2));
});

editor.addEventListener('featureClick', (e) => editor.enableEdit(e.featureId));

editor.start({ continuous: false });
```

## 资源清理

```javascript
editor.delete();
engine.remove(editor);
```
