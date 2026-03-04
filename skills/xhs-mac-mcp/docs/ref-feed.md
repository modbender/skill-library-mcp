# Feed 浏览

## xhs_scroll_feed
滚动 Feed 流。
- `direction`: `down`(默认) | `up`
- `times`: 滚动次数（默认 3）

## xhs_open_note
点击 Feed 双列瀑布流中的笔记。
- `col`: 0=左列，1=右列（默认 0）
- `row`: 行号，0=第一行（默认 0）

## 使用顺序示例
```
xhs_navigate(tab="home")
→ xhs_navigate_top(tab="discover")
→ xhs_scroll_feed(direction="down", times=3)  # 刷新内容
→ xhs_open_note(col=0, row=0)  # 打开左列第一篇
→ xhs_screenshot()  # 确认进入笔记详情
```
