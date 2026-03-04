# 快速开始

## 安装

```bash
npm install @baidumap/jsapi-ui-kit
```

## 引入方式

### ESM 模块

```javascript
import { PlaceSearch, PlaceDetail } from '@baidumap/jsapi-ui-kit';
import '@baidumap/jsapi-ui-kit/dist/css/jsapi-ui-kit.css';
```

### CDN 引入

```html
<link rel="stylesheet" href="https://unpkg.com/@baidumap/jsapi-ui-kit/dist/css/jsapi-ui-kit.css">
<script src="https://unpkg.com/@baidumap/jsapi-ui-kit/dist/jsapi-ui-kit.iife.js"></script>
```

CDN 方式下通过全局变量 `BMapUIKit` 访问组件。

## 前置依赖

使用前需先加载百度地图 JS API：

```html
<script src="https://api.map.baidu.com/api?v=1.0&type=webgl&ak=YOUR_AK"></script>
```

## 基础示例

```javascript
// 1. 初始化地图
const map = new BMapGL.Map('map-container');
map.centerAndZoom(new BMapGL.Point(116.404, 39.915), 12);

// 2. 创建检索组件
const search = new BMapUIKit.PlaceSearch('#search-panel', { map });

// 3. 监听事件
search.on('select', (poi) => {
  console.log('选中:', poi.title);
});

// 4. 执行检索
search.search('餐厅');
```

