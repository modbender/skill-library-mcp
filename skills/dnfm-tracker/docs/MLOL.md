# 掌上英雄联盟 (mlol) JSAPI 文档

## 概述
- 兼容 wgwebbridge.js 和 QTLtools 所有功能
- 新增 HTTP 请求 API
- 新增多账号查询能力
- CDN: `https://mlol-file.qpic.cn/mobile/mlol/js/mlol.js`

## 核心 API

### HTTP 请求
基于 axios 的封装：
```javascript
mlol.http.get(url, config)
mlol.http.post(url, data, config)
```

### 应用操作
```javascript
mlol.openApp({ openScheme, packageName, appDetail })  // 打开App
mlol.downloadApp({ url, packageName })  // 下载App
mlol.getAppVersion({ success, fail })  // 获取版本
mlol.checkAppOrSchemeExist({ uri/packageName, success })  // 检查是否安装
```

### 游戏信息
```javascript
mlol.getGameInfo(gameId)  // 获取游戏信息
// gameId: lgame(英雄联盟手游), jgame(金铲铲), egame(电竞经理)
```

### 分享功能
```javascript
mlol.shareLink({ title, desc, url, ... })  // 分享链接
mlol.shareImage({ imageUrl, ... })  // 分享图片
mlol.showShareMenu({ ... })  // 显示分享菜单
```

### 跳转页面
```javascript
qtpage://rn_page?bundle=taroDemo  // 掌盟内跳转
// 掌盟外跳转通过引导页: https://mlol.qt.qq.com/openmlol.html?intent=qtpage://...
```

### URL 参数
- `exchangeType=1` - 显示切换账号组件
- `zmAccountId=xxx` - 账号信息继承
- `pure_webview=1` - 纯 WebView 模式
- `enableRefreshButton=3` - 显示刷新按钮

## 打开掌盟
- 原生页面: `https://mlol.qt.qq.com/openmlol.html?intent=qtpage://community_post?postId=xxx`
- H5页面: `https://mlol.qt.qq.com/openmlol.html?url=编码后的地址`
- 帖子详情: `https://mlol.qt.qq.com/openmlol.html?postId=UGC_xxx`

## 兼容性问题
- iOS WKWebView 不支持 `window.open()`
- 需要 `pure_webview=1` 解决锚点跳转问题
