# 个性化地图样式

自定义地图外观：修改水体、道路、建筑等要素的颜色，控制 POI 标签的显示/隐藏，实现深色主题、简洁地图等效果。

## 快速开始

```javascript
// 方式一：使用 styleJson 定义样式
map.setMapStyleV2({
    styleJson: [{
        featureType: 'water',
        elementType: 'all',
        stylers: { color: '#021019ff' }
    }]
});

// 方式二：使用 styleId（从百度地图开放平台获取）
map.setMapStyleV2({
    styleId: '3d71dc5a4ce6222d3396801dee06622d'
});
```

## setMapStyleV2 方法

```javascript
map.setMapStyleV2(config)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| config | Object \| string | 样式配置对象或预定义样式名称 |

### config 配置方式

#### 方式一：styleJson（本地定义样式）

```javascript
map.setMapStyleV2({
    styleJson: [
        { featureType: '...', elementType: '...', stylers: {...} },
        // 更多样式规则...
    ]
});
```

#### 方式二：styleId（服务端样式）

从[百度地图个性化编辑器](https://lbsyun.baidu.com/apiconsole/custommap)获取样式 ID。

```javascript
map.setMapStyleV2({
    styleId: '3d71dc5a4ce6222d3396801dee06622d'
});
```

## 样式规则结构

每个样式规则是一个对象：

```javascript
{
    featureType: string,   // 地图要素类型（必需）
    elementType: string,   // 要素元素类型（必需）
    stylers: {             // 样式器对象（必需）
        visibility: 'on' | 'off',
        color: string,
        weight: string,
        lightness: number,
        saturation: number
    }
}
```

### stylers 属性

| 属性 | 类型 | 说明 | 示例 |
|------|------|------|------|
| visibility | string | 可见性 | `'on'` / `'off'` |
| color | string | 颜色（RRGGBBAA 十六进制） | `'#ff0000ff'` |
| weight | string | 线条粗细 | `'1'` / `'2'` / `'4'` |
| lightness | number | 亮度调整 | `-20` 到 `20` |
| saturation | number | 饱和度调整 | `-100` 到 `100` |

**颜色格式说明：**
- 使用 8 位十六进制格式：`#RRGGBBAA`
- 最后两位 (AA) 表示透明度：`ff` 完全不透明，`00` 完全透明
- 示例：`#ff0000ff`（不透明红色）、`#0000ff80`（半透明蓝色）

## featureType 要素类型

### 基础要素

| featureType | 说明 |
|-------------|------|
| land | 陆地 |
| water | 水体 |
| green | 绿地 |
| background | 背景 |
| building | 建筑 |
| manmade | 人造物体 |

### 道路要素

| featureType | 说明 |
|-------------|------|
| road | 普通道路 |
| highway | 高速公路 |
| cityhighway | 城市高速 |
| nationalway | 国道 |
| provincialway | 省道 |
| arterial | 干道 |
| tertiaryway | 三级道路 |
| fourlevelway | 四级路 |
| local | 本地道路 |
| railway | 铁路 |
| subway | 地铁 |

### 道路附属要素

| featureType | 说明 |
|-------------|------|
| laneline | 车道线 |
| roadarrow | 路箭头 |
| crosswalk | 人行横道 |
| footbridge | 天桥 |
| underpass | 地下通道 |
| parkinglot | 停车场 |
| parkingspace | 停车位 |

### 道路标志

| featureType | 说明 |
|-------------|------|
| highwaysign | 高速标志 |
| nationalwaysign | 国道标志 |
| provincialwaysign | 省道标志 |
| tertiarywaysign | 三级道路标志 |

### 行政区划

| featureType | 说明 |
|-------------|------|
| continent | 大陆 |
| country | 国家 |
| city | 城市 |
| district | 区 |
| town | 城镇 |
| village | 乡村 |

### POI 标签

| featureType | 说明 |
|-------------|------|
| poilabel | POI 标签（通用） |
| districtlabel | 区标签 |
| airportlabel | 机场标签 |
| subwaylabel | 地铁标签 |
| subwaystation | 地铁站 |
| transportationlabel | 交通标签 |

### 生活服务标签

| featureType | 说明 |
|-------------|------|
| educationlabel | 教育标签 |
| medicallabel | 医疗标签 |
| restaurantlabel | 餐厅标签 |
| hotellabel | 酒店标签 |
| shoppinglabel | 购物标签 |
| entertainmentlabel | 娱乐标签 |
| lifeservicelabel | 生活服务标签 |
| carservicelabel | 汽车服务标签 |
| financelabel | 金融标签 |
| companylabel | 公司标签 |
| governmentlabel | 政府标签 |
| businesstowerlabel | 商务楼标签 |
| scenicspotslabel | 风景名胜标签 |
| estatelabel | 庄园标签 |
| otherlabel | 其他标签 |

### 功能区域

| featureType | 说明 |
|-------------|------|
| education | 教育 |
| medical | 医疗 |
| shopping | 购物 |
| entertainment | 娱乐 |
| estate | 庄园 |
| scenicspots | 风景名胜 |
| playground | 游乐场 |
| transportation | 交通 |

### 特殊道路

| featureType | 说明 |
|-------------|------|
| scenicspotsway | 风景名胜道路 |
| universityway | 大学道路 |
| vacationway | 度假道路 |

## elementType 元素类型

| elementType | 说明 |
|-------------|------|
| all | 所有元素 |
| geometry | 几何体 |
| geometry.fill | 几何填充 |
| geometry.stroke | 几何描边 |
| geometry.topfill | 几何顶面填充（3D 建筑） |
| geometry.sidefill | 几何侧面填充（3D 建筑） |
| labels | 标签 |
| labels.text | 标签文本 |
| labels.text.fill | 标签文本填充 |
| labels.text.stroke | 标签文本描边 |
| labels.icon | 标签图标 |

## 常见场景

### 深色地图样式

```javascript
map.setMapStyleV2({
    styleJson: [{
        featureType: 'land',
        elementType: 'geometry',
        stylers: {
            color: '#0e1723ff'
        }
    }, {
        featureType: 'water',
        elementType: 'geometry',
        stylers: {
            color: '#113549ff'
        }
    }, {
        featureType: 'building',
        elementType: 'geometry.fill',
        stylers: {
            color: '#1a2634ff'
        }
    }, {
        featureType: 'highway',
        elementType: 'geometry.fill',
        stylers: {
            color: '#2a3f54ff'
        }
    }, {
        featureType: 'road',
        elementType: 'geometry.fill',
        stylers: {
            color: '#1e3040ff'
        }
    }]
});
```

### 隐藏元素

```javascript
map.setMapStyleV2({
    styleJson: [{
        featureType: 'poilabel',
        elementType: 'all',
        stylers: { visibility: 'off' }
    }, {
        featureType: 'building',
        elementType: 'all',
        stylers: { visibility: 'off' }
    }]
});
```

### 3D 建筑样式

```javascript
map.setMapStyleV2({
    styleJson: [{
        featureType: 'building',
        elementType: 'geometry.topfill',
        stylers: {
            color: '#e0e0e0ff'
        }
    }, {
        featureType: 'building',
        elementType: 'geometry.sidefill',
        stylers: {
            color: '#bdbdbdff'
        }
    }]
});
```

## 注意事项

1. **颜色格式**：使用 8 位十六进制颜色（RRGGBBAA），最后两位为透明度

2. **样式叠加**：多次调用 `setMapStyleV2` 会完全替换之前的样式，不会叠加

3. **性能考虑**：样式规则过多可能影响渲染性能，建议只定义必要的规则

4. **恢复默认**：传入空数组可恢复默认样式
   ```javascript
   map.setMapStyleV2({ styleJson: [] });
   ```

5. **在线编辑器**：推荐使用[百度地图个性化编辑器](https://lbsyun.baidu.com/apiconsole/custommap)可视化创建样式，然后导出 styleJson 或获取 styleId
