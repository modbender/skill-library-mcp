# Step 6: 成品生产

## 目标
5 个 SubAgent 分 3 轮并行生产，每角度产出 X 推文 + 小红书笔记 + 公众号文章三平台成品。

## 前置条件
- Step 5 已完成
- `runs/<slug>/angles.json` 已生成
- `runs/<slug>/posts_detail.json` 可用

## 调度策略

### 并行调度：5 SubAgent × 3 轮（2+2+1）

```
轮次 1：SubAgent A（角度 1-2）  ║  SubAgent B（角度 3-4）
轮次 2：SubAgent C（角度 5-6）  ║  SubAgent D（角度 7-8）
轮次 3：SubAgent E（角度 9-10）
```

每个 SubAgent 处理 2 个角度，每角度产出 3 篇内容。

### 为什么分轮而非一次性并行？

- 控制并发数，避免超出 SubAgent 并行限制
- 每轮结束后检查结果完整性
- 出错时只需重试单个 SubAgent

## 执行步骤

### 6.1 准备 SubAgent 输入

主 Agent 为每个 SubAgent 构建独立输入：

```json
{
  "topic": "Cursor IDE",
  "angles": [
    {
      "id": 1,
      "angle": "为什么资深开发者正在从 VS Code 转向 Cursor",
      "article_type": "热点解读",
      "brief": "VS Code 老用户迁移 Cursor 的真实原因"
    },
    {
      "id": 2,
      "angle": "Cursor vs GitHub Copilot：AI 编程助手终极对决",
      "article_type": "对比分析",
      "brief": "两大 AI 编程工具全方位横评"
    }
  ],
  "source_posts": [
    {
      "title": "帖子标题",
      "url": "https://...",
      "key_points": "从帖子中提炼的 3-5 个关键点"
    }
  ]
}
```

> **注意**：只传递与该 SubAgent 角度相关的帖子摘要，而非全部帖子详情。

### 6.2 SubAgent Prompt 模板

```
你是一个多平台内容创作专家。请根据以下角度和素材，产出三平台成品内容。

## 创作任务

主题：{topic}

### 角度 {angle.id}：{angle.angle}
- 文章类型：{angle.article_type}
- 核心观点：{angle.brief}

### 参考素材
{source_posts}

## 产出要求

请严格按以下格式输出，每个角度产出 3 篇内容：

### 角度 {id} 成品

#### X 推文
（参考 X 推文模板规范）

#### 小红书笔记
（参考小红书笔记模板规范）

#### 公众号文章
（参考公众号文章模板规范）

---

## 模板规范

### X 推文规范
- 总长 ≤ 280 字符（中文约 140 字）
- 第一句必须是 Hook（提问/数据/反常识）
- 包含 2-3 个话题标签
- 结尾引导互动

### 小红书笔记规范
- 标题：带 emoji 的吸睛标题（≤ 20 字）
- 正文：分点阐述，每点一个 emoji 开头
- 300-500 字
- 结尾 3-5 个标签

### 公众号文章规范
- 标题：不超过 30 字
- 摘要：一句话概括（≤ 54 字）
- 正文：800-1500 字
- 结构：引言 → 正文（3-5 段）→ 总结 → 引导关注
- 每段有小标题
```

### 6.3 执行三轮调度

**轮次 1**：并行启动 SubAgent A 和 B
```
SubAgent A → runs/<slug>/pieces/angle-01.md、angle-02.md
SubAgent B → runs/<slug>/pieces/angle-03.md、angle-04.md
```

**轮次 2**：并行启动 SubAgent C 和 D
```
SubAgent C → runs/<slug>/pieces/angle-05.md、angle-06.md
SubAgent D → runs/<slug>/pieces/angle-07.md、angle-08.md
```

**轮次 3**：启动 SubAgent E
```
SubAgent E → runs/<slug>/pieces/angle-09.md、angle-10.md
```

### 6.4 结果检查

每轮结束后，主 Agent 检查（**不读内容，只检查文件存在性**）：

```bash
ls runs/<slug>/pieces/angle-*.md | wc -l
```

如有缺失文件，重试对应 SubAgent。

### 6.5 更新 progress.json

Step 6 标记为 `completed`，`current_step` 设为 `7`。

## piece 文件格式

每个 `angle-{n}.md` 包含：

```markdown
# 角度 {n}：{角度描述}

**文章类型**：{类型}

---

## X 推文

{推文内容}

---

## 小红书笔记

{笔记内容}

---

## 公众号文章

{文章内容}
```

## 上下文保护

> ⚠️ **主 Agent 严禁读取 piece 文件内容**。
> 主 Agent 只通过文件存在性检查确认 SubAgent 是否完成。
> piece 文件内容将由 Step 7 的 Python 脚本确定性合并。

## 下一步

→ [Step 7: 合并输出](step-7-merge.md)
