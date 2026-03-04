# 灵感发现 — 完整执行指南

## 一、搜索策略

### 搜索关键词模板

将 `{年份}` 和 `{月份}` 替换为当前日期。

#### Product Hunt

**使用脚本**：运行 `scripts/producthunt_trending.py`，通过官方 API v2 获取热门产品，结果自动保存为纯文本到 `tmp/ph_results.txt`。

> Token 从工作目录的 `.env.idea2mvp` 文件自动读取（也支持环境变量）。如未配置，需先询问用户是否愿意配置（见下方搜索执行策略）。

**执行流程**：
1. 直接运行脚本（脚本自动从 `.env.idea2mvp` 读取 Token，无需手动 export）
```bash
python3 scripts/producthunt_trending.py
python3 scripts/producthunt_trending.py --days 7 --limit 20
python3 scripts/producthunt_trending.py --topic productivity --days 3
```
2. **用户不想配置 Token 时**（`.env.idea2mvp` 中 `SKIP_PH_API=true`）：使用 `web_search` 搜索 PH 相关信息
  - `"Product Hunt" best new tools {月份} {年份}`
  - `"Product Hunt" trending productivity tools {年份}`
  - `site:producthunt.com top products this week`

> Token 配置方式：在工作目录创建 `.env.idea2mvp`，写入 `PRODUCTHUNT_TOKEN=your_token`
> Token 获取：https://www.producthunt.com/v2/oauth/applications → 创建应用 → Developer Token

**常用 topic**：`productivity`、`developer-tools`、`artificial-intelligence`、`design-tools`、`marketing`、`fintech`、`education`

#### 中文社区

**小红书**：运行 `scripts/xiaohongshu_search.py` 搜索笔记，结果自动保存到 `tmp/xhs_results.txt`。

脚本使用 Playwright 控制浏览器，模拟真人操作：打开首页 → 搜索框输入关键词 → 逐个点击笔记卡片进入详情页 → 提取正文、标签、互动数据等完整信息 → 关闭详情返回列表。全程加入随机延迟、鼠标移动、渐进滚动等反爬策略。

> ⚠️ **登录要求**：首次运行时会弹出浏览器，用户需扫码登录一次，之后自动复用登录状态。
> 依赖：`pip3 install playwright && python3 -m playwright install chromium`

**执行流程**：

1. **Playwright 自动搜索**（推荐，需用户同意使用 Playwright）：
   ```bash
   python3 scripts/xiaohongshu_search.py --keyword "效率工具推荐"
   python3 scripts/xiaohongshu_search.py --keyword "AI工具推荐" --sort popularity_descending
   python3 scripts/xiaohongshu_search.py --keyword "宝藏app推荐" --limit 5
   ```
   首次运行需扫码登录，后续自动复用。脚本逐个点入笔记详情页，提取完整正文内容和互动数据。

2. **从 JSON 解析**（离线模式，已有数据时）：
   ```bash
   python3 scripts/xiaohongshu_search.py --input tmp/xhs_response.json
   ```

3. **用户不想使用 Playwright 时**：在 `.env.idea2mvp` 中设置 `SKIP_XHS_PLAYWRIGHT=true`，后续直接跳过小红书搜索（小红书未开放公网搜索，搜索引擎无法抓取其内容，`web_search` 搜不到有效结果）。

**推荐关键词**：`效率工具推荐`、`好用的小众app`、`独立开发者 产品推荐`、`宝藏app推荐`、`AI工具推荐`

**V2EX**（✅ 免费公开 API，无需认证）：运行 `scripts/v2ex_topics.py`，从产品相关节点（分享创造、分享发现）获取话题，自动过滤出工具/产品/独立开发相关内容，结果保存到 `tmp/v2ex_results.txt`。

```bash
python3 scripts/v2ex_topics.py                          # 默认从 分享创造 + 分享发现 节点获取，自动过滤工具相关话题
python3 scripts/v2ex_topics.py --nodes create share macos  # 指定多个节点
python3 scripts/v2ex_topics.py --filter "AI工具"          # 自定义关键词过滤
python3 scripts/v2ex_topics.py --no-filter                 # 不过滤，返回节点下所有话题
python3 scripts/v2ex_topics.py --pages 2                   # 每个节点获取 2 页（约 40 条/节点）
```

可用节点：`create`（分享创造）、`share`（分享发现）、`macos`、`chrome`、`programmer`（程序员）、`app`（App 推荐）。

> ⚠️ `web_search` 的 `site:v2ex.com` 实测无效，务必使用脚本 API。

**少数派**（✅ 免费公开 API，无需认证）：运行 `scripts/sspai_search.py`，通过少数派搜索 API 获取文章，自动按点赞数排序并去重，结果保存到 `tmp/sspai_results.txt`。还支持通过文章 ID 获取完整正文内容（详情保存到 `tmp/sspai_detail.txt`）。

```bash
# 搜索文章列表
python3 scripts/sspai_search.py                                # 默认搜索: 效率工具、独立开发、小工具推荐
python3 scripts/sspai_search.py --keyword "效率工具"            # 单关键词搜索
python3 scripts/sspai_search.py --keywords "AI工具" "独立开发"  # 多关键词搜索
python3 scripts/sspai_search.py --keyword "效率工具" --limit 10 # 限制输出数量

# 获取文章完整正文（传入搜索结果中的文章 ID）
python3 scripts/sspai_search.py --detail 60079                 # 单篇文章详情
python3 scripts/sspai_search.py --detail 60079 73051 55239     # 多篇文章详情
```

**推荐用法**：先用关键词搜索获取文章列表 → 从中挑选与产品/工具相关的文章 → 用 `--detail` 获取完整正文深入了解。

#### Indie Hackers

**Indie Hackers**（✅ 免费 Algolia 搜索 API，无需认证）：运行 `scripts/indiehackers_search.py`，通过 Indie Hackers 内置的 Algolia 搜索 API 获取独立开发者产品信息，自动按月收入排序并去重，结果保存到 `tmp/ih_results.txt`。

```bash
python3 scripts/indiehackers_search.py                                    # 默认搜索: productivity tool, AI tool, developer tool, side project
python3 scripts/indiehackers_search.py --keyword "AI tool"                # 单关键词搜索
python3 scripts/indiehackers_search.py --keywords "newsletter" "SaaS"     # 多关键词搜索
python3 scripts/indiehackers_search.py --keyword "productivity" --limit 10 # 限制输出数量
python3 scripts/indiehackers_search.py --keyword "AI" --min-revenue 100   # 只看月收入 >= $100 的产品
```

每个产品包含：名称、tagline、描述、月收入、领域标签、商业模式、融资方式、平台、网站链接等。

#### 其他独立开发者社区
- `DecoHack 独立产品周刊`
- `独立开发者产品 工具 推荐 {年份}`

#### GitHub Trending

**使用脚本**：运行 `scripts/github_trending.py`，结果自动保存到 `tmp/github_results.txt`。

```bash
python3 scripts/github_trending.py
python3 scripts/github_trending.py --days 7 --min-stars 100
python3 scripts/github_trending.py --lang python --topic cli
python3 scripts/github_trending.py --days 90 --lang typescript --min-stars 200
```

无需 Token，如需更高速率可在 `.env.idea2mvp` 中配置 `GITHUB_TOKEN`。

**备用 web_search**（API 不可用时）：
- `GitHub trending tool CLI utility {月份} {年份}`
- `GitHub trending productivity developer tool`

#### 通用搜索
- `实用小工具 {年份}`
- `效率工具推荐 独立开发 {年份}`
- `best indie apps {年份}`
- `best CLI tools developers {年份}`

### 搜索执行策略

> 所有脚本都会自动将结果保存为纯文本到 `tmp/` 目录，可通过 `read_file` 读取纯文本结果，节省 token。

**第零步：确认用户搜索偏好**

在执行搜索前，先读取 `.env.idea2mvp` 检查是否已有偏好配置。如果以下配置项**不存在**，则向用户确认：

1. **Product Hunt**：是否已配置 `PRODUCTHUNT_TOKEN`？如未配置，询问用户是否愿意配置 Token 以使用 API 搜索。
   - 用户愿意 → 引导配置 Token，使用脚本搜索
   - 用户不愿意 → 在 `.env.idea2mvp` 中写入 `SKIP_PH_API=true`，后续跳过脚本，改用 `web_search` 搜索 Product Hunt 信息

2. **小红书**：询问用户是否愿意使用 Playwright 控制浏览器登录并搜索小红书（需扫码登录、安装 Playwright 依赖）。**提醒用户：自动化操作存在被平台检测到反爬而封号的风险，请用户自行评估后决定。**
   - 用户愿意 → 使用 `scripts/xiaohongshu_search.py` 搜索
   - 用户不愿意 → 在 `.env.idea2mvp` 中写入 `SKIP_XHS_PLAYWRIGHT=true`，后续直接跳过小红书搜索（小红书未开放公网搜索，搜索引擎无法抓取其内容）

> 偏好一旦写入 `.env.idea2mvp`，后续搜索自动跳过确认步骤，直接按偏好执行。用户可随时手动修改 `.env.idea2mvp` 中的配置来调整偏好。

**第一轮（并行 5-6 个搜索）**：
1. Product Hunt 精选产品（`scripts/producthunt_trending.py`，或 `web_search` 如设置了 `SKIP_PH_API=true`） → `tmp/ph_results.txt`
2. V2EX 热门/最新话题（`scripts/v2ex_topics.py`） → `tmp/v2ex_results.txt`
3. GitHub 工具项目（`scripts/github_trending.py`） → `tmp/github_results.txt`
4. 小红书热门工具推荐（`scripts/xiaohongshu_search.py`，如设置了 `SKIP_XHS_PLAYWRIGHT=true` 则跳过） → `tmp/xhs_results.txt`
5. 少数派（`scripts/sspai_search.py`）→ `tmp/sspai_results.txt`
6. Indie Hackers（`scripts/indiehackers_search.py`）→ `tmp/ih_results.txt`
7. 其他独立开发者社区/英文社区（`web_search`）

**第二轮（根据第一轮结果补充，并行 2-3 个搜索）**：
- 针对第一轮发现的有趣方向深入搜索
- 搜索特定工具的详细信息、定价、用户评价

## 二、筛选标准

### 纳入标准（全部满足）
1. **解决具体痛点**：工具有明确的使用场景
2. **小团队或个人作品**：优先 10 人以下团队
3. **C 端可用**：普通用户能直接下载/使用
4. **近期活跃**：近 6 个月内有更新

### 排除标准（命中任一即排除）
1. 平台型产品（Notion、Figma、Slack 等）
2. 框架和库（React、Next.js 等）
3. 基础设施（数据库、云服务等）
4. AI 大模型平台（ChatGPT、Claude 等，但使用 AI 的小工具可纳入）
5. 纯 B 端 SaaS

### GitHub Trending 特别注意
- 仅筛选工具类、效率类小项目
- 个人开发者项目优先
- Trending 中多为框架类时减少此来源占比
- 最多选取 3 个项目

## 三、Idea 扩展思维框架

### 痛点提炼

对每个发现的工具，回答：
1. 用户之前怎么做的？（手动？忍受？凑合？）
2. 工具把什么从"麻烦"变成了"简单"？
3. 痛点的频率和强度？

| 痛点类型 | 描述 | 示例 |
|---------|------|------|
| 效率痛点 | 手动操作耗时，可自动化 | 文件格式批量转换 |
| 信息痛点 | 信息分散、难找、难整理 | 跨平台书签管理 |
| 决策痛点 | 选择太多、不知如何选 | 穿搭搭配推荐 |
| 沟通痛点 | 表达或传递信息困难 | 屏幕录制转 GIF |
| 习惯痛点 | 想养成好习惯但难以坚持 | 专注计时器 |
| 成本痛点 | 现有方案太贵或太重 | 轻量级替代大型软件 |

### 模式识别

**技术模式**：
- AI + X、自动化替代手动、本地化/离线化、一键化/极简化

**市场模式**：
- 大产品的"拆解"、免费替代付费、跨平台统一、垂直深耕

**用户行为模式**：
- 碎片化使用、创作者工具、个人数据主权

### 空白发现

- **相邻空白法**：同类用户还有什么需求？上下游有什么痛点？其他场景是否也有需求？
- **组合创新法**：两个工具的核心能力组合能否产生新价值？
- **反向思考法**：工具解决了"做了某事后的痛点"，"不做某事的痛点"是否也可解决？

### Idea 输出规范

每个 Idea 需包含：
- **Idea 名称**：简洁有力
- **核心场景**：2-3 句话描述真实使用场景
- **目标用户群体**：具体到人群画像
- **差异化切入点**：和现有工具相比的独特之处
- **灵感来源**：基于哪个工具的分析得出
- **潜在商业模式**：订阅/买断/免费增值，注明预期定价
- **难度评估**：⭐~⭐⭐⭐⭐⭐

## 四、报告输出模板

**生成报告前**：先通过 `read_file` 加载 `tmp/` 目录下的搜索结果文件，作为归纳总结的参考素材：

- `tmp/ph_results.txt` — Product Hunt 热门产品
- `tmp/v2ex_results.txt` — V2EX 产品/工具话题
- `tmp/github_results.txt` — GitHub 热门项目
- `tmp/xhs_results.txt` — 小红书笔记
- `tmp/sspai_results.txt` — 少数派文章
- `tmp/sspai_detail.txt` — 少数派文章详情（如有）
- `tmp/ih_results.txt` — Indie Hackers 产品

> 只加载实际存在的文件。基于这些原始数据进行筛选、交叉比对和归纳，确保报告中的推荐和洞察有据可依。

```markdown
## 🛠️ 工具探索报告 - {当前日期}

### 📱 实用 App & 小工具推荐（Top 5-8）

#### 🔧 工具名称（附访问链接）
> 一句话定位

- **解决的痛点**：2-3 句话
- **核心功能**：① [功能1] ② [功能2] ③ [功能3]
- **适合人群**：[目标用户]
- **平台**：iOS / Android / Web / 桌面 / CLI / 浏览器插件
- **价格**：免费 / 买断 / 订阅
- **信息来源**：Product Hunt / GitHub / 少数派 / 小红书

---

### 📦 GitHub 工具类小项目（Top 3，仅限工具类）

#### ⭐ 项目名称（GitHub 链接）
> 一句话定位

- **使用场景**：2 句话
- **目标用户**：[用户画像]
- ⭐ Star 数：[数量]
- **技术栈**：[主要技术]

---

### 💡 产品 Ideas & 拓展方向（Top 5）

#### 💡 Idea [序号]：[Idea 名称]

- **核心场景**：[2-3 句话]
- **目标用户群体**：[人群画像]
- **差异化切入点**：[独特之处]
- **灵感来源**：[基于哪个工具]
- **潜在商业模式**：[定价]
- **难度评估**：[⭐~⭐⭐⭐⭐⭐]

---

### 📌 今日洞察

1. **[趋势名称]**：[2-3 句话]
2. **[趋势名称]**：[2-3 句话]
3. **[趋势名称]**：[2-3 句话]

---

### 🔗 下一步

如果以上任何 Idea 让你感兴趣，我们可以深入聊聊，然后我帮你生成一份**灵感确认文档**，作为后续想法验证的起点。
```

## 五、灵感确认文档

阶段一沟通完成后，询问用户是否生成灵感确认文档。此文档记录沟通中的关键信息，作为阶段二的输入上下文。

**文件名**：`idea-brief.md`，保存至项目工作目录。

**模板**：

```markdown
# 灵感确认文档

> 生成日期：[日期]

## 选定方向

### Idea 名称
[名称]

### 一句话描述
[描述]

### 核心场景
[2-3 句话]

### 目标用户
[用户画像]

## 用户背景与偏好

### 产品偏好
[用户在沟通中表达的倾向，如：偏好 C 端/B 端、偏好轻量工具/平台型、偏好买断/订阅等]

### 相关经验
[用户提到的行业经验、技术背景、个人优势]

### 资源条件
[可投入的时间、预算、团队情况等]

## 关键问题与顾虑

- [用户提出的问题 1]
- [用户提出的问题 2]
- ...

## 讨论中的新想法

[沟通过程中产生的调整、补充或新方向]

## 待验证事项

[进入阶段二需要重点验证的问题清单]
```
