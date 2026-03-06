# 已知限制（必读）

## 图文帖评论区：AX 硬限制

**现象**：图文帖评论文字完全读不到。
**根因**：小红书图文帖使用自绘渲染（Metal/Canvas），AX API 无法获取文字内容。
- `AXNumberOfCharacters = 0`，`AXValue = kAXErrorNoValue`
- 尝试过：AXValue / AXSelectedText / AXCustomContent / AXVisibleText / AS 全遍历 → 全部空

**视频帖无此限制**：open_comments 弹出侧边层，get_comments 完整返回用户名 + 坐标。

**图文帖替代方案**：`xhs_screenshot()` + image tool 分析截图文字。

## App 可见性要求

- rednote App 必须**在屏幕上可见**（不能最小化）
- 屏幕**不能锁定**（锁屏后鼠标事件全部失效）
- 可以在后台（其他窗口在前面），不需要在最前面
- 长时间运行建议：`caffeinate -di &`

## search() 注意事项

从非首页状态（如笔记详情页）调用 search，App 可能还停在当前页。
标准做法：先 `xhs_navigate(tab="home")`，再 `xhs_navigate_top(tab="discover")`，再 search。
