# 笔记互动（点赞 / 收藏 / 评论 / 私信）

> 所有操作需先用 xhs_open_note 进入笔记详情页。

## 基础互动

### xhs_like
点赞当前笔记。无参数。

### xhs_collect
收藏当前笔记。无参数。

### xhs_get_note_url
获取当前笔记的分享链接（xhslink.com 短链）。无参数。返回 URL 字符串。

### xhs_follow_author
关注当前笔记的作者。无参数。

## 评论区

### xhs_open_comments
打开评论区。
- 视频帖：弹出侧边评论层，完整可用
- 图文帖：只聚焦输入框，评论列表 AX 读不到（见 ref-limits.md）

### xhs_scroll_comments
滚动评论区。
- `times`: 滚动次数（默认 3）
- 视频帖完全可用；图文帖受限

### xhs_get_comments
获取评论列表。无参数。返回：
```json
[{"index": 0, "author": "用户名", "cx": 1450, "cy": 368}, ...]
```
- **视频帖可靠**，图文帖 AX 暴露有限

### xhs_post_comment
发送评论。
- `text`: 评论内容（string，必填）

### xhs_reply_to_comment
回复某条评论。
- `index`: 评论序号（来自 get_comments 的 index 字段）
- `text`: 回复内容（string，必填）

### xhs_delete_comment
删除评论（**只能删自己发的，不可逆**）。
- `index`: 评论序号（来自 get_comments）

## 评论操作标准流程
```
xhs_open_comments()
→ xhs_get_comments()           # 拿到评论列表和 index
→ xhs_reply_to_comment(index=0, text="回复内容")
# 或
→ xhs_delete_comment(index=0)  # 确认是自己的评论再删
```
