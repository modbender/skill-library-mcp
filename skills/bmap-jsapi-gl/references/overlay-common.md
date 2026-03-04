# 覆盖物通用操作

## 添加覆盖物

```javascript
// 创建覆盖物
var marker = new BMapGL.Marker(new BMapGL.Point(116.404, 39.915));

// 添加到地图
map.addOverlay(marker);
```

### map.addOverlay(overlay)

| 参数 | 类型 | 说明 |
|------|------|------|
| overlay | Overlay | 覆盖物实例 |

## 移除覆盖物

### 移除单个

```javascript
map.removeOverlay(marker);
```

### 移除全部

```javascript
map.clearOverlays();
```

> 设置 `enableMassClear: false` 的覆盖物不会被 clearOverlays 清除

### 获取所有覆盖物

```javascript
var overlays = map.getOverlays();
```

## 覆盖物通用方法

| 方法 | 说明 |
|------|------|
| `show()` | 显示覆盖物 |
| `hide()` | 隐藏覆盖物 |
| `isVisible()` | 返回是否可见 |
| `getMap()` | 获取所在地图实例 |

```javascript
marker.hide();           // 隐藏
marker.show();           // 显示
marker.isVisible();      // true
marker.getMap();         // 返回 map 实例
```

## enableMassClear 属性

控制覆盖物是否会被 `clearOverlays()` 清除。

| 值 | 默认 | 说明 |
|------|------|------|
| `true` | 是 | 调用 clearOverlays 时会被清除 |
| `false` | - | 调用 clearOverlays 时保留 |

```javascript
// 创建时设置
var marker = new BMapGL.Marker(point, {
  enableMassClear: false
});

// 或通过方法设置
marker.disableMassClear();  // 禁止批量清除
marker.enableMassClear();   // 允许批量清除
```

## 事件

覆盖物事件详见 [overlay-events.md](./overlay-events.md)。
