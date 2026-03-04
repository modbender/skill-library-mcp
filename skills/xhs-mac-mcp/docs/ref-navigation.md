# 导航 & 截图

## xhs_screenshot
截取当前界面截图。无参数。

## xhs_navigate
切换底部 Tab。
- `tab`: `home`(首页) | `messages`(消息) | `profile`(我)

## xhs_navigate_top
切换顶部 Tab（需在首页）。
- `tab`: `follow`(关注) | `discover`(发现) | `video`(视频)

## xhs_back
返回上一页。无参数。

## xhs_search
搜索关键词，跳转搜索结果页。
- `keyword`: 搜索词（string，必填）

## 使用顺序示例
```
xhs_navigate(tab="home")
→ xhs_navigate_top(tab="discover")
→ xhs_search(keyword="AI论文")
→ xhs_screenshot()  # 确认结果
```
