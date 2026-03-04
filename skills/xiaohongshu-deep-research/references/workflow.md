# 详细工作流

## 初始化

```bash
mkdir -p ~/xiaohongshu-research/{keyword}_{YYYYMMDD_HHmm}/{raw,analysis}
```

## 关键词扩展

```
输入: "露营"
→ 露营、露营装备推荐、露营好物、新手露营攻略
```

## 搜索 API

```bash
curl -s -X POST "http://localhost:18060/api/v1/feeds/search" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "露营"}'
```

返回字段：
- `id` — 帖子 ID（用于生成链接）
- `noteCard.displayTitle` — 标题
- `noteCard.user.nickname` — 作者
- `noteCard.interactInfo.*` — 点赞/收藏/评论数

## 帖子链接

```
https://www.xiaohongshu.com/explore/{id}
```

## 数据处理

```bash
# 合并多个搜索结果，去重，按点赞排序
jq -s '
  [.[].data.feeds[] | select(.modelType == "note")] | 
  unique_by(.id) |
  sort_by(-(.noteCard.interactInfo.likedCount | tonumber))
' search_*.json > posts.json
```

## 报告模板

```markdown
# {主题} 小红书研究

> {日期} · 关键词: {keywords} · {N} 篇帖子

---

## 📱 速览

{用 2-3 段话总结发现，像给朋友发消息一样写。有观点，有态度，不要官腔。}

**值得看的几篇：**
• [{标题1}](https://www.xiaohongshu.com/explore/{id1})
• [{标题2}](https://www.xiaohongshu.com/explore/{id2})
• [{标题3}](https://www.xiaohongshu.com/explore/{id3})

---

## 数据

{N} 篇帖子 · {total_likes} 赞 · {total_collects} 收藏

## Top 10

1. **{标题}** @{作者}
   {likes}👍 {collects}📁 · [看看](https://www.xiaohongshu.com/explore/{id})

2. ...

## 发现

{用自然语言写 3-5 个洞察，不要用 bullet points 堆砌}

## 建议

{如果用户要去/要买/要做什么，给出具体建议}

---

数据: `~/xiaohongshu-research/{keyword}_{date}/raw/posts.json`
```

## 写作指南

### 速览部分（可直接转发）

写法示例：

❌ 不要这样写：
> 经过对20篇小红书帖子的分析，我们发现波士顿美食话题具有较高的用户关注度。头部内容主要集中在龙虾、中餐等品类。

✅ 这样写：
> 刷了一圈小红书，波士顿吃的还挺多的。龙虾当然是必吃，但意外发现羊杂汤特别火——可能华人都馋这口。有个博主吃了100家店做了个系列，挺靠谱的可以参考。

### 正文部分

- 直接说结论，不要铺垫
- 数字要有意义（"1489 赞"比"高互动"具体）
- 链接要能点

## 限制

- 帖子正文内容无法获取
- 评论无法获取
- 数据来自搜索结果元数据
