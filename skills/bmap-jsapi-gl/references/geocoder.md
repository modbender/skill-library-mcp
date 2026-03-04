# Geocoder 地理编码

用于地址与坐标的相互转换：正地理编码（地址 → 坐标）和逆地理编码（坐标 → 地址）。

## 快速开始

```javascript
var myGeo = new BMapGL.Geocoder();

// 正地理编码：地址 → 坐标
myGeo.getPoint('北京市海淀区上地十街10号', function(point) {
    if (point) {
        map.centerAndZoom(point, 16);
        map.addOverlay(new BMapGL.Marker(point));
    }
}, '北京市');

// 逆地理编码：坐标 → 地址
myGeo.getLocation(new BMapGL.Point(116.404, 39.915), function(result) {
    if (result) {
        console.log(result.address);
    }
});
```

## 构造函数

```javascript
new BMapGL.Geocoder(options)
```

## 方法

### getPoint 正地理编码

将地址解析为坐标。

```javascript
geocoder.getPoint(address, callback, city)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| address | string | 地址字符串 |
| callback | function | 回调函数 |
| city | string | 城市名称，可选，默认全国范围检索 |

**回调参数：**

```javascript
callback(point, detailInfo)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| point | Point \| null | 解析成功返回坐标，失败返回 null |
| detailInfo | object | 详细信息对象 |

**detailInfo 结构：**

| 属性 | 类型 | 说明 |
|------|------|------|
| city | string | 城市名称 |
| citycode | string | 城市代码 |
| address | string | 规范化后的地址 |
| precise | number | 精确性：0=精确，1=前向匹配 |
| confidence | number | 置信度（0-100） |
| level | string | 地址级别：地址、街道、地区、城市、省份、国家 |

### getLocation 逆地理编码

将坐标解析为地址。

```javascript
geocoder.getLocation(point, callback, options)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| point | Point | 坐标点 |
| callback | function | 回调函数，参数为 GeocoderResult 或 null |
| options | object | 可选配置 |

**options 配置：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| poiRadius | number | 100 | 周边 POI 搜索半径（米） |
| numPois | number | 10 | 返回的 POI 个数 |

## GeocoderResult 结果对象

逆地理编码返回的结果对象。

| 属性 | 类型 | 说明 |
|------|------|------|
| point | Point | 查询点坐标 |
| address | string | 完整地址描述 |
| addressComponents | object | 地址组成部分 |
| surroundingPois | Array | 周边 POI 数组 |
| business | string | 商业区信息 |

**addressComponents 结构：**

| 属性 | 类型 | 说明 |
|------|------|------|
| province | string | 省份 |
| city | string | 城市 |
| district | string | 区县 |
| street | string | 街道名称 |
| streetNumber | string | 街道号码 |

**surroundingPois 数组元素：**

| 属性 | 类型 | 说明 |
|------|------|------|
| title | string | POI 名称 |
| uid | string | POI 唯一标识 |
| point | Point | POI 坐标 |
| address | string | POI 地址 |
| city | string | POI 所在城市 |
| phoneNumber | string | 电话 |
| postcode | string | 邮编 |
| type | number | POI 类型（BMAP_POI_TYPE_NORMAL） |
| tags | Array | 分类标签数组 |

## 语言常量

Geocoder 仅支持中英文，其他语言会回退为中文。

| 常量 | 值 | 说明 |
|------|-----|------|
| BMAPGL_LANGUAGE_ZH | 'zh' | 中文（简体）**默认** |
| BMAPGL_LANGUAGE_EN | 'en' | 英语 |

## 状态常量

参见 [constants.md](./constants.md)。

## 注意事项

1. 正地理编码指定 city 参数可提高解析准确性和速度
2. 逆地理编码的 poiRadius 过大会影响响应速度
3. 解析失败时 callback 的 point 参数为 null
4. 返回坐标为 BD09 坐标系
