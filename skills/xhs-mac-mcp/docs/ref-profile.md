# 个人主页 & 作者数据

## xhs_get_author_stats
读取当前主页的统计数据。无参数。
返回：
```json
{
  "following": "2",
  "followers": "29",
  "likes": "302",
  "bio": "OpenClaw驱动的一只小虾\n🦞 本虾每天潜入 ArXiv 深海捞论文"
}
```

**前提**：需先导航到主页（自己或他人）。

## 查看自己主页
```
xhs_navigate(tab="profile")
→ xhs_get_author_stats()
```

## 查看笔记作者主页
```
# 进入笔记详情页后，点作者头像（暂无专用 tool）
# 可截图后用 image tool 读数据作为替代
xhs_screenshot()
```
