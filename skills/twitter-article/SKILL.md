# Twitter Article Skill

Notion 文章一键同步到 Twitter/X Article（Premium+ 长文，图文混排）。

## 快速使用

```bash
# 环境变量（必须）
export AUTH_TOKEN="<twitter auth_token cookie>"
export CT0="<twitter ct0 cookie>"
export HTTPS_PROXY="http://127.0.0.1:7897"

# Notion 文章 → Twitter 草稿（一条命令搞定）
node twitter-article.js notion-to-article --notion-key <key> --page-id <id>

# 或者分步操作
node twitter-article.js upload-media --file image.png        # 上传图片
node twitter-article.js create --title "标题" --file a.md     # 创建含内容的草稿
node twitter-article.js update-content --id <id> --file a.md  # 更新已有草稿内容
node twitter-article.js update-cover --id <id> --media-id <m> # 设封面
node twitter-article.js publish --id <id>                     # 发布
```

## 命令一览

| 命令 | 说明 |
|------|------|
| `list` | 列出所有草稿 |
| `create-draft --title "xxx"` | 创建空草稿 |
| `create --title "xxx" --file a.md` | 创建并写入内容 |
| `update-content --id <id> --file a.md` | 更新内容（.md 或 .json） |
| `update-title --id <id> --title "xxx"` | 更新标题 |
| `update-cover --id <id> --media-id <mid>` | 设封面 |
| `upload-media --file image.png` | 上传图片 → media_id |
| `get --id <id>` | 查看文章详情 |
| `publish --id <id>` | 发布 |
| `delete --id <id>` | 删除 |

## 前提条件

- Twitter Premium+ 账号（Article 功能需要）
- Cookies 认证：`AUTH_TOKEN` + `CT0`（从浏览器获取）
- 代理：`HTTPS_PROXY`（国内需要）

## 内容格式（核心）

Twitter Article 使用修改版 Draft.js 格式。发送用 **snake_case**，返回用 camelCase。

### Block

```json
{
  "data": {},
  "text": "段落文字",
  "key": "a1b2c",
  "type": "unstyled",
  "entity_ranges": [],
  "inline_style_ranges": []
}
```

支持的 type：`unstyled` `header-one` `header-two` `blockquote` `unordered-list-item` `ordered-list-item` `atomic`

**不支持**：`header-three` `header-four` `code-block`（服务端 500）

### 内嵌图片

Atomic block + MEDIA entity：

```json
// entity_map 条目
{
  "key": "0",
  "value": {
    "type": "MEDIA",
    "mutability": "Immutable",
    "data": {
      "entity_key": "<uuid-v4>",
      "media_items": [{
        "local_media_id": 1,
        "media_category": "DraftTweetImage",
        "media_id": "<media_id_string>"
      }]
    }
  }
}

// 对应的 atomic block
{
  "data": {},
  "text": " ",
  "key": "xxx",
  "type": "atomic",
  "entity_ranges": [{"key": 0, "offset": 0, "length": 1}],
  "inline_style_ranges": []
}
```

## API 变量名速查

| Mutation | 文章ID变量名 | 其他关键变量 |
|----------|-------------|-------------|
| DraftCreate | (无) | content_state, title, plaintext, word_count |
| UpdateContent | `article_entity` | content_state, plaintext, word_count |
| UpdateTitle | `articleEntityId` | title |
| UpdateCoverMedia | `articleEntityId` | coverMedia: {media_id, media_category} |
| Delete/Publish | `articleEntityId` | (无) |

⚠️ UpdateContent 用 `article_entity`，其他用 `articleEntityId`！

## ⚠️ 关键注意事项

1. **media_id 必须用字符串** — JS Number 对 19 位数字丢精度，用 `media_id_string`
2. **第一个 # 标题自动跳过** — 作为 title 参数传递，不重复写入正文
3. **h3/h4 → h2** — Twitter 不支持三级以下标题
4. **code → blockquote** — code-block 类型会报错
5. **QueryID 可能变** — Twitter 前端更新后需要重新抓取
6. **封面图格式** — `coverMedia: {media_id, media_category: "DraftTweetImage"}`，不是平铺的 media_id

## 文件结构

```
skills/twitter-article/
├── SKILL.md              # 本文档
└── twitter-article.js    # CLI 工具（所有功能）
```
