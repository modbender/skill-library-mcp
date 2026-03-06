# Measure 测量工具

## 概述

Measure 继承自 Editor，提供距离测量、面积测量、点坐标测量功能。默认显示测量标签，支持连续测量和自定义标签样式。

## 测量类型

通过 `mapvthree.Measure.MeasureType` 访问：

| 类型 | 枚举值 | 说明 |
|------|--------|------|
| 距离测量 | `Measure.MeasureType.DISTANCE` | 测量线条长度 |
| 面积测量 | `Measure.MeasureType.AREA` | 测量多边形面积 |
| 点测量 | `Measure.MeasureType.POINT` | 测量点坐标 |

## 基本用法

```javascript
const measure = engine.add(new mapvthree.Measure({
    type: mapvthree.Measure.MeasureType.DISTANCE
}));

measure.start();
measure.stop();
```

## 构造参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `type` | MeasureType | `DISTANCE` | 测量类型 |
| `enableMidpointHandles` | boolean | `true` | 显示中点控制点 |
| `renderOptions` | object | 见下方 | 渲染选项 |

**renderOptions 默认值：**
```javascript
{ depthTest: false, transparent: true, renderOrder: 100 }
```

> Measure 内部自动设置 `showLabel: true` 和 `singleMode: true`。

## 距离测量

```javascript
const measure = engine.add(new mapvthree.Measure({
    type: mapvthree.Measure.MeasureType.DISTANCE
}));

measure.setStyle({ strokeColor: '#ffff00', strokeWidth: 3 });

measure.setDistanceFormatter((distance) => {
    return distance < 1000
        ? `${distance.toFixed(1)} 米`
        : `${(distance / 1000).toFixed(2)} 公里`;
});

measure.start();
```

## 面积测量

```javascript
const areaMeasure = engine.add(new mapvthree.Measure({
    type: mapvthree.Measure.MeasureType.AREA
}));

areaMeasure.setStyle({
    fillColor: '#52c41a',
    fillOpacity: 0.3,
    strokeColor: '#52c41a',
    strokeWidth: 2
});

areaMeasure.setAreaFormatter((area) => {
    return area < 10000
        ? `${area.toFixed(1)} 平方米`
        : `${(area / 10000).toFixed(2)} 公顷`;
});

areaMeasure.start();
```

## 点坐标测量

```javascript
const pointMeasure = engine.add(new mapvthree.Measure({
    type: mapvthree.Measure.MeasureType.POINT
}));

pointMeasure.setPointFormatter((point) => {
    return `经度: ${point[0].toFixed(6)}\n纬度: ${point[1].toFixed(6)}`;
});

pointMeasure.start();
```

## 切换测量类型

```javascript
measure.setType(mapvthree.Measure.MeasureType.AREA);
```

## 获取与清除结果

```javascript
// 获取所有测量结果
const all = measure.getMeasurements();

// 获取特定类型结果
const distances = measure.getMeasurementsByType(mapvthree.Measure.MeasureType.DISTANCE);

// 清除所有
measure.clear();

// 清除特定类型
measure.clearByType(mapvthree.Measure.MeasureType.DISTANCE);
```

## 自定义标签渲染

```javascript
measure.setLabelRenderer((value) => {
    const div = document.createElement('div');
    div.innerText = value.attributes.text;
    div.style.cssText = `
        background: rgba(0,0,0,0.8);
        color: #fff;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
    `;

    if (value.attributes.isMain) {
        div.style.fontWeight = 'bold';
        div.style.fontSize = '14px';
    }

    return div;
});
```

**value.attributes 属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `text` | string | 标签显示文本 |
| `type` | string | 测量类型 |
| `isMain` | boolean | 是否为主标签（总计值） |
| `isSegment` | boolean | 是否为分段标签 |
| `value` | number | 原始数值 |
| `index` | number | 标签序号 |
| `position` | number[] | 标签位置坐标 |

## 编辑测量结果

```javascript
measure.enableEdit();
measure.enableEdit('feature-id');
measure.disableEdit();
```

## 事件

```javascript
measure.addEventListener('created', (e) => console.log('测量完成'));
measure.addEventListener('start', () => console.log('开始测量'));
measure.addEventListener('update', (e) => console.log('当前值:', e));
```

## 只读属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `isDrawing` | boolean | 是否正在绘制 |
| `isEditing` | boolean | 是否正在编辑 |
| `measureType` | string | 当前测量类型 |

## 静态方法

```javascript
// 计算两点间距离
const distance = mapvthree.Measure.getLength(
    [116.404, 39.915, 0],
    [116.405, 39.916, 0],
    'spatial'  // 'vertical'|'horizontal'|'spatial'
);

// 计算路径分段距离
const segments = mapvthree.Measure.getSegementLength([
    [116.404, 39.915, 0],
    [116.405, 39.916, 0],
    [116.406, 39.917, 0]
]);

// 平面投影面积
const area = mapvthree.Measure.getArea(polygonCoords);

// 球面面积
const spaceArea = mapvthree.Measure.getSpaceArea(polygonCoords);
```

## 资源清理

```javascript
measure.clear();
engine.remove(measure);
```
