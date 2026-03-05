# Step 7: 合并输出

## 目标
使用 Python 脚本将所有 piece 文件确定性拼接为最终的 `content.md`，附加来源帖子表格。

## 前置条件
- Step 6 已完成
- `runs/<slug>/pieces/angle-*.md` 全部生成（10 个文件）
- `runs/<slug>/posts_detail.json` 可用

## 执行命令

```bash
python3 skills/reddit-topic-insight/scripts/python/content_merger.py \
  --pieces-dir runs/<slug>/pieces \
  --posts-file runs/<slug>/posts_detail.json \
  --output runs/<slug>/content.md
```

## 脚本行为

### 7.1 扫描 piece 文件
按文件名中的角度编号排序：`angle-01.md` → `angle-02.md` → ... → `angle-10.md`

### 7.2 拼接内容

生成 `content.md`，结构如下：

```markdown
# {topic} — Reddit 主题洞察报告

> 生成时间：{timestamp}
> 数据来源：Reddit
> 覆盖角度：10 个
> 涵盖平台：X / 小红书 / 公众号

---

{angle-01.md 内容}

---

{angle-02.md 内容}

---

... （依次拼接所有角度）

---

## 📊 数据来源

| # | 标题 | 子版块 | 热度分 | 评论数 | 链接 |
|---|------|--------|--------|--------|------|
| 1 | 帖子标题 | r/programming | 1960 | 230 | [链接](url) |
| 2 | ... | ... | ... | ... | ... |
```

### 7.3 生成来源表格
从 `posts_detail.json` 读取 Top 10 帖子信息，生成 Markdown 表格。

### 7.4 更新 progress.json
Step 7 标记为 `completed`。

## 输出

- `runs/<slug>/content.md` — 最终合并文件
- 通知用户查看最终输出

## 为什么用脚本而非 AI？

> 合并操作是纯确定性的（读文件 → 排序 → 拼接 → 写文件），没有创造性成分。
> 使用脚本可以：
> - 避免 AI 对内容进行不必要的修改
> - 保证输出顺序和格式一致
> - 保护主 Agent 的上下文窗口

## 下一步

→ 完成！通知用户查看 `runs/<slug>/content.md`
