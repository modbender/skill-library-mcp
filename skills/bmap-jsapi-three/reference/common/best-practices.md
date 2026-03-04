# 通用最佳实践

## 资源管理

### 组件销毁
```javascript
engine.remove(component);
component.dispose();
```

### 引擎销毁
```javascript
engine.dispose();
```

## 性能优化

### 数据组织
- 使用 `FeatureCollection` 批量管理数据
- 相同样式的要素合并（如 `MultiLineString`）
- 启用数据过滤减少渲染负担

### 批量操作
```javascript
// 推荐：批量添加
data.add([item1, item2, item3]);

// 推荐：批量定义属性
data.defineAttributes({ color: 'c', size: 's' });
```

## 坐标系

MapV Three 使用 **Z-up 坐标系**：
- 二维坐标：`[经度, 纬度]`
- 三维坐标：`[经度, 纬度, 高度(米)]`

详见：`coordinate-system.md`

## 事件处理

频繁触发的 `update` 事件建议使用防抖处理。
