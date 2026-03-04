---
name: mood-forum
description: 心情论坛工具。用于在心情分享平台发心情、查看动态、点赞点踩、评论互动。当用户想发心情、查看论坛内容、点赞、点踩、评论时使用此 Skill。
---

# 心情论坛工具

通过 HTTP API 调用心情论坛服务。

## 环境要求

- Python 3
- 无需额外依赖（使用标准库 urllib）

## 可用工具

### 1. 发布心情 post_mood

发布一条新的心情动态。

```bash
python3 scripts/call_mood_api.py post_mood --content "今天天气真好！"
```

### 2. 查看心情列表 get_posts

获取最新的心情动态（分页）。

```bash
# 获取第1页
python3 scripts/call_mood_api.py get_posts --page 1

# 获取第2页
python3 scripts/call_mood_api.py get_posts --page 2
```

返回数据包含：动态ID、作者、内容、点赞数、点踩数、评论列表。

### 3. 点赞 toggle_like

给指定动态点赞（toggle 模式）。

```bash
python3 scripts/call_mood_api.py toggle_like --post-id 13
```

### 4. 点踩 toggle_dislike

给指定动态点踩（toggle 模式）。

```bash
python3 scripts/call_mood_api.py toggle_dislike --post-id 13
```

### 5. 添加评论 add_comment

给指定动态添加评论。

```bash
# 直接评论
python3 scripts/call_mood_api.py add_comment --post-id 13 --content "写得真好！"

# 回复某条评论
python3 scripts/call_mood_api.py add_comment --post-id 13 --content "同意你的观点" --parent-id 7
```

### 6. 编辑评论 edit_comment

修改自己发出的评论。

```bash
python3 scripts/call_mood_api.py edit_comment --post-id 13 --comment-id 8 --content "修改后的内容"
```

### 7. 删除评论 delete_comment

删除评论（本人或管理员可操作）。

```bash
python3 scripts/call_mood_api.py delete_comment --post-id 13 --comment-id 8
```

## 使用示例

当用户说：
- "帮我发一条心情" → 使用 post_mood
- "看看大家最近在发什么" → 使用 get_posts
- "给这条点个赞" → 使用 toggle_like（需要提供 post_id）
- "来评论一下" → 使用 add_comment
- "回复楼上" → 使用 add_comment + parent_id

## 注意事项

1. 所有命令返回 JSON 格式，需要解析给用户看
2. post_id 和 comment_id 必须是对应的
3. API 基础 URL 已内置在脚本中
