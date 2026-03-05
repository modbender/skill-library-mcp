# Content Ops - 精细化工序设计

## 一、语料生产（多Agent协作）

### 工序总览

```
用户需求
    │
    ▼
┌─────────────────┐
│  Master Agent   │
│  (主控)         │
└────────┬────────┘
         │
         ├────▶ 拆分Query（扩展同义词/相关词）
         │
         ├────▶ 创建Sub-Agent 1 ──▶ 搜索Query 1 ──▶ 评估帖子质量
         │                                         │
         ├────▶ 创建Sub-Agent 2 ──▶ 搜索Query 2 ──▶ 评估帖子质量
         │                                         │
         └────▶ 创建Sub-Agent N ──▶ 搜索Query N ──▶ 评估帖子质量
                                                       │
                                                       ▼
                                            ┌─────────────────┐
                                            │  质量评估Agent  │
                                            │  - 数据好？      │
                                            │  - 观点好？      │
                                            │  - 时效高？      │
                                            └────────┬────────┘
                                                     │
                                     ┌───────────────┼───────────────┐
                                     │               │               │
                                     ▼               ▼               ▼
                                  质量高          质量中          质量低
                                     │               │               │
                                     ▼               ▼               ▼
                                  点进去看      翻1-3页再找       放弃
                                     │
                                     ▼
                            ┌─────────────────┐
                            │  详情抓取Agent  │
                            │  - 标题          │
                            │  - 正文          │
                            │  - 图片URL       │
                            │  - 互动数据      │
                            └────────┬────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │  去重评估Agent  │
                            │  - 和已有语料对比│
                            │  - 观点是否重复  │
                            │  - 相似度检测    │
                            └────────┬────────┘
                                     │
                         ┌───────────┴───────────┐
                         │                       │
                         ▼                       ▼
                      不重复                    重复
                         │                       │
                         ▼                       ▼
                      加入候选列表              标记为重复
                         │                       │
                         └───────────┬───────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │  Master Agent   │
                            │  汇总所有候选   │
                            └────────┬────────┘
                                     │
                                     ▼
                              输出总List给用户
                              (包含质量评分、
                               推荐理由)
```

### 详细工序

#### 步骤1: Master Agent - 任务拆分

**输入**: 用户主题（如"春季穿搭"）

**输出**: Query列表

**Prompt示例**:
```
主题：春季穿搭

请扩展以下搜索维度：
1. 核心词：春季穿搭
2. 场景词：通勤穿搭、约会穿搭、出游穿搭
3. 风格词：简约风、日系风、韩系风
4. 单品词：风衣搭配、牛仔裤穿搭、小白鞋搭配
5. 热门标签：OOTD、每日穿搭、春日穿搭

输出格式：JSON数组，每个query一个对象
```

#### 步骤2: Sub-Agent - 搜索与初筛（每个Query一个Agent）

**Agent配置**:
- **名称**: `Search-Evaluator-{query}`
- **模型**: Claude Opus（需要理解内容和评估质量）
- **工具**: 浏览器自动化（Playwright）

**工序**:
```
1. 访问小红书搜索页
2. 输入query搜索
3. 获取前20条结果
4. 对每条结果评估：
   ├─ 数据指标：点赞>1000？收藏>500？评论>100？
   ├─ 内容质量：图片是否清晰？排版是否专业？
   ├─ 时效性：发布时间是否在7天内？
   └─ 独特观点：是否有新颖的穿搭思路？

5. 评分规则：
   - 高质量（8-10分）：数据好+观点新颖+时效高
   - 中质量（5-7分）：数据中等+观点一般
   - 低质量（<5分）：放弃

6. 如果前20条高质量<3条：
   └─ 翻页到第2-3页继续找

7. 对高质量帖子：
   └─ 点击进入详情页
   └─ 抓取完整内容

8. 返回候选列表（含URL、评分、推荐理由）
```

**输出格式**:
```json
{
  "query": "春季穿搭",
  "results": [
    {
      "url": "https://xiaohongshu.com/...",
      "title": "春日简约穿搭",
      "score": 9,
      "reason": "点赞1.2w，风衣搭配思路新颖",
      "engagement": { "likes": 12000, "saves": 5000 },
      "publish_time": "2024-01-10",
      "status": "待去重评估"
    }
  ]
}
```

#### 步骤3: Sub-Agent - 去重评估

**Agent配置**:
- **名称**: `Deduplication-Checker`
- **输入**: 候选内容 + 已有语料库

**工序**:
```
1. 提取候选内容的核心观点（总结3个关键点）
2. 和已有语料库对比：
   ├─ 标题相似度（编辑距离）
   ├─ 内容语义相似度（embedding对比）
   ├─ 核心观点重复度
   └─ 图片相似度（感知hash）

3. 判断规则：
   - 如果核心观点重合度>70%：标记为重复
   - 如果只有图片相似但观点不同：保留
   - 如果角度不同（如一个讲搭配，一个讲颜色）：保留

4. 输出：去重后的候选列表
```

#### 步骤4: Master Agent - 汇总输出

**工序**:
```
1. 收集所有Sub-Agent的结果
2. 按质量分排序
3. 去重（同query可能抓相似内容）
4. 生成总List：
   ├─ 高质量语料（8-10分）：推荐立即使用
   ├─ 中质量语料（5-7分）：备选
   └─ 低质量/重复：已过滤

5. 输出给用户：
   ├─ 表格：链接、标题、评分、推荐理由
   ├─ 统计：共找到X条，高质量Y条
   └─ 建议：哪些适合今天的发布计划
```

**输出示例**:
```markdown
# 语料抓取结果 - 春季穿搭

## 统计
- 搜索Query：5个
- 候选帖子：25条
- 高质量（8-10分）：8条 ✅
- 中质量（5-7分）：10条
- 重复/低质量：7条 ❌

## 高质量语料推荐

| 排名 | 标题 | 评分 | 推荐理由 | 链接 |
|------|------|------|----------|------|
| 1 | 春日风衣3种穿法 | 9.5 | 点赞2w，搭配思路实用 | [查看] |
| 2 | 小个子春季穿搭 | 9.0 | 针对性强，评论区互动高 | [查看] |
| ... | ... | ... | ... | ... |

## 建议
- 推荐语料1改编为Reddit帖子（实用向）
- 推荐语料2适合Pinterest（图文向）
```

---

## 二、内容生成（选题→样稿→确认）

### 工序总览

```
可用语料库
    │
    ▼
┌─────────────────┐
│  选题推荐Agent  │
│  - 分析语料主题 │
│  - 匹配账号定位 │
│  - 推荐选题方向 │
└────────┬────────┘
         │
         ▼
    选题方向List
    （3-5个方向）
         │
         ▼
    用户确认选题
         │
         ▼
┌─────────────────┐
│  样稿生成Agent  │
│  - 文案生成      │
│  - 图片生成/选择 │
│  - 排版设计      │
└────────┬────────┘
         │
         ▼
    样稿（文案+配图）
         │
         ▼
    用户确认样稿
    （通过/修改/拒绝）
         │
    ┌────┴────┐
    │         │
    ▼         ▼
  通过      修改
    │         │
    ▼         ▼
沟通发布计划  重新生成
    │
    ▼
创建发布任务
```

### 详细工序

#### 步骤1: 选题推荐

**输入**: 可用语料库 + 账号运营策略

**Agent配置**:
- **名称**: `Topic-Recommender`
- **模型**: Claude Opus

**工序**:
```
1. 分析语料库主题分布：
   ├─ 统计各主题数量
   ├─ 识别热门话题
   └─ 发现趋势

2. 匹配账号定位：
   ├─ 读取 target_accounts.positioning
   ├─ 过滤符合定位的语料
   └─ 排除不相关主题

3. 结合平台特性：
   ├─ Reddit：讨论型、问题型内容表现好
   ├─ Pinterest：视觉型、教程型内容表现好
   └─ Discord：社区型、互动型内容表现好

4. 生成选题建议（3-5个）：
   ├─ 选题标题
   ├─ 推荐理由（为什么适合）
   ├─ 目标受众
   ├─ 预计表现（基于语料数据）
   └─ 参考语料链接
```

**输出示例**:
```markdown
# 选题推荐 - Reddit账号: MyBrandUS

## 推荐选题（基于今日语料库）

### 选项1: "小个子女生春季风衣穿搭指南"
- **类型**: 教程型
- **推荐理由**: 
  - 语料中有2篇高赞内容（点赞>1w）
  - r/femalefashionadvice 社区近期讨论度高
  - 针对性强，容易引发共鸣
- **目标受众**: 小个子女性
- **参考语料**: [链接1] [链接2]

### 选项2: "春日约会穿搭：温柔风vs酷飒风"
- **类型**: 对比型/讨论型
- **推荐理由**:
  - 对比形式适合Reddit投票互动
  - 评论区容易引发讨论
- **目标受众**: 年轻女性
- **参考语料**: [链接3]

### 选项3: "一周通勤穿搭不重样"
- **类型**: 合集型
- **推荐理由**:
  - 信息密度高，收藏率通常较高
  - 适合做成图文帖子
- **目标受众**: 职场女性

请回复数字（1/2/3）确认选题，或描述你的修改意见
```

#### 步骤2: 样稿生成

**输入**: 用户确认的选题 + 参考语料

**Agent配置**:
- **名称**: `Content-Generator`
- **工具**: 
  - OpenAI DALL-E（图片生成）
  - 浏览器（抓取参考图片）

**工序**:
```
1. 文案生成
   ├─ 分析参考语料的核心观点
   ├─ 翻译/改编为英文（Reddit）
   ├─ 生成标题（吸引力优化）
   ├─ 生成正文结构：
   │   ├─ Hook（开头吸引人）
   │   ├─ 主体内容（分点论述）
   │   └─ CTA（引导互动）
   └─ 添加表情符号、格式优化

2. 图片准备
   ├─ 方案A：从语料下载原图（需处理版权）
   ├─ 方案B：用DALL-E生成新图
   │   └─ Prompt: "Spring outfit ideas, minimalist style, 
   │              female model, natural lighting, ..."
   └─ 方案C：混合（参考语料构图，生成新图）

3. 排版设计
   ├─ Reddit: Markdown格式，段落清晰
   ├─ Pinterest: 竖版图片+简洁描述
   └─ Discord: 适合频道的格式

4. 生成3个版本供选择
   ├─ 版本A：偏教程型（干货多）
   ├─ 版本B：偏讨论型（引发互动）
   └─ 版本C：偏故事型（个人经历）
```

**输出示例**:
```markdown
# 样稿 - "小个子女生春季风衣穿搭指南"

## 版本A：教程型

### 标题
[Tip] How to Style Trench Coats for Petite Women: 3 Proven Looks

### 正文
Hey r/femalefashionadvice!

As a 5'2" gal who's struggled with oversized trenches, I want to share 
3 styling tricks that actually work for us petite women...

[详细内容...]

### 配图
- 主图：小个子女生穿风衣全身照（DALL-E生成）
- 图2：3种搭配对比图
- 图3：细节展示（腰带位置）

### 标签
#fashion #petitefashion #springoutfits #styletips

---

请确认：
- [ ] 这个版本可以，直接发布
- [ ] 需要修改（请描述）
- [ ] 看看其他版本
```

#### 步骤3: 用户确认

**工序**:
```
1. 展示样稿（文案+配图预览）
2. 等待用户反馈：
   ├─ "确认" → 进入发布计划沟通
   ├─ "修改：xxx" → 重新生成
   └─ "拒绝" → 回到选题阶段

3. 修改循环（最多3轮）
```

#### 步骤4: 发布计划沟通

**确认样稿后**:
```
1. 确认发布平台：
   ├─ Reddit: 选择subreddit
   ├─ Pinterest: 选择board
   └─ Discord: 选择频道

2. 确认发布时间：
   ├─ 立即发布
   ├─ 定时发布（选择时间）
   └─ 加入队列（按策略自动安排）

3. 确认发布频率：
   ├─ 单条发布
   └─ 系列发布（如"一周穿搭"分7天发）

4. 创建发布任务（publish_tasks）
```

---

## 三、内容发布（平台适配）

### 平台发布方案对比

| 平台 | API方案 | 浏览器自动化 | 推荐 |
|------|---------|-------------|------|
| **Reddit** | PRAW（需OAuth） | Playwright模拟 | **浏览器** |
| **Pinterest** | 官方API（需商业申请） | Playwright模拟 | **浏览器** |
| **Discord** | Webhook（最简单） | 不需要 | **Webhook** |

### 方案选择

**统一方案**: 浏览器自动化（Playwright）
- 优点：一套代码适配所有平台
- 优点：无需申请API权限
- 优点：可处理复杂的登录态
- 缺点：速度稍慢（但内容发布不需要实时）

### 发布工序

```
发布任务队列
    │
    ▼
┌─────────────────┐
│  登录检查Agent  │
│  - 检查账号登录态│
│  - 如需重新登录  │
│  - 触发登录流程  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  平台适配Agent  │
│  - 根据平台选择  │
│    发布方式      │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
 Discord   Reddit/
 Webhook   Pinterest
    │       浏览器自动化
    │         │
    │    ┌────┴────┐
    │    │         │
    │    ▼         ▼
    │  读取DOM   多模态
    │  定位元素  辅助定位
    │    │         │
    └────┴────┬────┘
              │
              ▼
         执行发布
              │
              ▼
         验证发布成功
              │
              ▼
         记录发布链接
```

#### Reddit/Pinterest 浏览器自动化

**工序**:
```
1. 启动浏览器（Playwright）
2. 加载账号Cookies（从source_accounts.session_data）
3. 访问发布页面
4. 填写内容：
   ├─ 标题输入框
   ├─ 正文输入框（Markdown）
   ├─ 上传图片
   ├─ 选择社区/board
   └─ 添加标签
5. 预览检查（截图给用户确认）
6. 点击发布
7. 等待发布完成
8. 抓取发布后的URL
9. 截图保存发布结果
```

**DOM定位策略**:
```python
# 方案1: 基于选择器（稳定优先）
title_input = page.locator('input[placeholder*="title" i]')

# 方案2: 基于文本（鲁棒性优先）
post_button = page.get_by_text('Post', exact=False)

# 方案3: 多模态辅助（备选）
# 当选择器失效时，用视觉模型识别按钮位置
```

#### Discord Webhook

**最简单**:
```python
import requests

webhook_url = "https://discord.com/api/webhooks/..."

payload = {
    "content": "春日穿搭分享",
    "embeds": [{
        "title": "小个子女生春季风衣穿搭",
        "description": "...",
        "image": {"url": "https://..."}
    }]
}

requests.post(webhook_url, json=payload)
```

---

## 四、Agent协作架构

### Master-Agent 调度关系

```
Master Agent (主控)
    │
    ├──▶ Sub-Agent: Query-Expander (拆分query)
    │
    ├──▶ Sub-Agent: Search-Evaluator-1 (搜索+评估)
    ├──▶ Sub-Agent: Search-Evaluator-2
    ├──▶ Sub-Agent: Search-Evaluator-N
    │
    ├──▶ Sub-Agent: Deduplication-Checker (去重)
    │
    ├──▶ Sub-Agent: Topic-Recommender (选题)
    │
    ├──▶ Sub-Agent: Content-Generator (生成样稿)
    │
    └──▶ Sub-Agent: Publisher (发布)

每个Sub-Agent返回结构化结果
Master Agent负责协调和决策
```

### 通信协议

```typescript
// Sub-Agent 返回格式
interface SubAgentResult {
  agentId: string;
  status: 'success' | 'partial' | 'failed';
  data: any;
  summary: string;  // 给Master的摘要
  nextAction?: string;  // 建议下一步
}

// 示例：Search-Evaluator返回
{
  agentId: 'search-evaluator-spring-outfit',
  status: 'success',
  data: {
    query: '春季穿搭',
    results: [...],
    highQualityCount: 5
  },
  summary: '找到5条高质量语料，2条中质量',
  nextAction: 'proceed_to_deduplication'
}
```

---

## 五、数据流转更新

### 新增字段

**crawl_results表新增**:
```sql
-- 抓取来源追踪
sub_agent_id: string;  // 哪个sub-agent抓的
query_path: string;    // 第几页找到的这个结果
quality_factors: json; // 评分明细 {data_score, view_score, timeliness_score}
duplication_check: json; // 去重结果 {is_duplicate, similarity_to, reason}
```

**publish_tasks表新增**:
```sql
-- 样稿生成追踪
topic_options: json;   // 给用户看的选题列表
selected_topic: string; // 用户确认的选题
draft_versions: json;   // 多版本样稿
user_feedback: json;    // 用户修改意见历史
```

---

这个设计是否更符合你的预期？