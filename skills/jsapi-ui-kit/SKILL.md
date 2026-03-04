---
name: jsapi-ui-kit
description: 百度地图 JavaScript API ui-kit 组件库开发指南。提供地点自动补全（PlaceAutocomplete）、地点检索（PlaceSearch）和地点详情（PlaceDetail）组件的使用参考。当用户需要：(1) 实现地点搜索输入框自动补全、(2) 在百度地图上实现地点搜索功能、(3) 展示 POI 详情信息、(4) 了解 @baidumap/jsapi-ui-kit 的 API 用法、(5) 处理组件事件回调时使用此 skill。
---

# 百度地图 jsapi-ui-kit

轻量级百度地图 UI 组件库，提供地点自动补全、地点检索和详情展示能力。

## 什么时候使用

- 希望快速集成标准化的地图 UI 组件，无需从零开发
- 需要在地图应用中添加搜索输入框自动补全功能
- 需要在地图应用中添加地点搜索功能
- 需要展示 POI 详情信息（名称、地址、电话等）

## 文档导航

- **[快速开始](references/getting-started.md)** - 安装、引入方式、基础示例
- **[PlaceAutocomplete 地点自动补全](references/place-autocomplete.md)** - 搜索输入框实时建议
- **[PlaceSearch 地点检索](references/place-search.md)** - 关键字/周边/范围检索
- **[PlaceDetail 地点详情](references/place-detail.md)** - POI 详情展示

## 如何使用

根据用户问题查询文档导航，参考详细文档内容和API设计： 
```
references/getting-started.md
```
每个参考文件包含：

- 功能简要说明
- 完整代码示例及解释
- API 参数说明和注意事项

## 注意事项

- 必须先加载百度地图 JS API（BMap 或 BMapGL）
