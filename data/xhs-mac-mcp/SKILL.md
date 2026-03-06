---
name: xhs-mac-mcp
description: 通过 macOS Accessibility API 控制小红书（rednote）App。支持私信、评论回复、视频评论读取、搜索、点赞、收藏、作者数据等。需要 Mac + rednote App 可见 + Terminal 辅助功能权限。
---

# xhs-mac-mcp

通过 OpenClaw Plugin 调用，20 个 `xhs_*` tools 已注册，直接 call 即可。

## 安装

```bash
cd ~/.agents/skills/xhs-mac-mcp && bash install.sh
openclaw config set tools.allow '["xhs-mac"]'
openclaw gateway restart
```

⚠️ 系统设置 → 隐私与安全 → 辅助功能 → 开启 Terminal

## 按需读取的参考文件

| 需要做什么 | 读哪个文件 |
|-----------|-----------|
| 导航、截图、搜索 | `docs/ref-navigation.md` |
| 浏览 Feed、打开笔记 | `docs/ref-feed.md` |
| 点赞、收藏、评论、回复、删除 | `docs/ref-note.md` |
| 私信（发送/打开对话） | `docs/ref-dm.md` |
| 主页数据（关注/粉丝/bio） | `docs/ref-profile.md` |
| 图文帖限制 / 注意事项 | `docs/ref-limits.md` |

## 快速参考

```
xhs_screenshot          截图
xhs_navigate            切底部Tab (home/messages/profile)
xhs_navigate_top        切顶部Tab (follow/discover/video)
xhs_back                返回
xhs_search              搜索
xhs_scroll_feed         滚动Feed
xhs_open_note           打开笔记(col,row)
xhs_like / xhs_collect  点赞 / 收藏
xhs_get_note_url        获取分享链接
xhs_follow_author       关注作者
xhs_open_comments       打开评论区
xhs_scroll_comments     滚动评论
xhs_get_comments        获取评论列表
xhs_post_comment        发评论
xhs_reply_to_comment    回复评论(index,text)
xhs_delete_comment      删评论(index) ⚠️不可逆
xhs_open_dm             打开私信(index)
xhs_send_dm             发私信(text)
xhs_get_author_stats    读主页数据
```
