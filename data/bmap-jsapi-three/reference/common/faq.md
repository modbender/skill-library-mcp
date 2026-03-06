# 常见问题解答

## 通用显示问题

### 组件没有显示？

**检查清单：**
1. 确认 `dataSource` 已正确设置
2. 检查坐标是否在当前地图视野范围内
3. 确认参数设置合理（如 `opacity` 不为0，`height` 不为0）
4. 查看控制台是否有错误信息

### 数据更新后视图没有刷新？

**解决方案：**
- 使用数据源的更新方法：`setAttributeValues()`, `setCoordinates()`
- 数据源修改后会自动触发更新
- 如果仍不刷新，尝试重新设置 `dataSource`

## 坐标系问题

**MapV Three 使用 Z-up 坐标系**，坐标格式为 `[经度, 纬度]` 或 `[经度, 纬度, 高度]`。

详见：`coordinate-system.md`

## 资源管理

### 如何正确销毁组件？

```javascript
// 标准销毁流程
engine.remove(component);
component.dispose();
```

## 天空和天气系统

### 如何选择合适的天空类型？

- **EmptySky**：需要最小性能开销或完全自定义天空时使用
- **DefaultSky**：简单渐变天空，性能最好，适合移动端
- **StaticSky**：需要预设天气和时间效果的预烘焙纹理
- **DynamicSky**：需要动态大气、云层和实时反射的高端效果

### 天空效果不对？

**问题：天空看不到，或效果很暗**
- 检查是否添加了天空对象：`engine.add(new mapvthree.DynamicSky())`
- 确认 `affectWorld` 属性为 `true`（影响环境反射）
- 检查光照强度参数是否过小：`sky.sunLightIntensity`, `sky.skyLightIntensity`

**问题：云层不显示**
- 确认 `enableCloudsPass: true`
- 检查 `cloudsCoverage` 是否大于0（默认0.55）
- DynamicWeather 切换天气时确保使用支持的天气值

**问题：时间变化无效**
- 更新时间应使用：`engine.clock.currentTime = new Date(...)`
- 注意时间值范围是0-86400秒（一天）

### Popup 内容不显示？

- 确认 `popup.visible = true`
- 检查内容是否为空：`popup.title` 和 `popup.content`
- 验证 CSS 尺寸没有设置为0或超出容器范围

### DOMOverlay 鼠标事件不生效？

- 检查 `pointer-events` CSS 属性：不能为 `none`
- 确认 `stopPropagation` 设置正确
- 验证 DOM 元素不被其他覆盖物遮挡

## 性能优化

### 大数据量卡顿？

- 使用聚合/过滤减少渲染数量
- 启用碰撞检测（如Label组件）
- 调整更新频率参数
- 降低细节层级（如LOD）

### 天空系统卡顿？

- 降低 DynamicSky 的 `cloudMarchSteps`（默认16，可设为8-12）
- 禁用 `enableCloudsPass` 或 `enableAtmospherePass`
- 在移动设备上使用 DefaultSky 而非 DynamicSky
