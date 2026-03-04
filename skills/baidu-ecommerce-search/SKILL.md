---
name: baidu-ecommerce-search
description: 百度电商搜索，包括cps商品查询、全网比价、榜单、商品参数、品牌品类知识等能力
homepage: https://openai.baidu.com
metadata: {"openclaw":{"emoji":"🛒","slug":"baidu-ecommerce-search","requires":{"bins":["python3"],"env":["BAIDU_EC_SEARCH_TOKEN"]},"primaryEnv":"BAIDU_EC_SEARCH_TOKEN"}}
---

# baidu-ecommerce-search

百度电商搜索，包括商品对比、全网比价、榜单、商品参数、品牌品类知识等能力。

## Setup

### 环境依赖

- Python 3.x（使用标准库 `urllib`、`json`、`os`，无需额外安装依赖）

### 配置步骤

1. 访问：https://openai.baidu.com，并登录百度账号
2. 点击权限申请，勾选你需要的能力，未勾选的能力调用时会失败
3. 设置环境变量
   ```bash
   # 必需：设置 API Token
   export BAIDU_EC_SEARCH_TOKEN="your-token"

   # 可选：设置 API 调用 QPS（每秒请求数），默认为 1
   # 设置为 0 表示无限制，设置为 0.5 表示每 2 秒 1 次请求
   export BAIDU_EC_SEARCH_QPS="1"
   ```

**QPS 配置说明：**
- 默认值：`1`（每秒最多1次请求，避免触发限流）
- `BAIDU_EC_SEARCH_QPS=0`：无限制，但容易触发 `token is limit` 错误
- `BAIDU_EC_SEARCH_QPS=0.5`：每2秒1次请求，更保守的限流策略
- 建议保持默认值 `1`，如需更快的请求速度可适当调高

## 何时使用 (触发条件)

当用户提出以下类型的请求时，应优先使用本技能：

**1. 全维度对比决策助手** 
- "[商品A]和[商品B]对比"
- "[商品A]和[商品B]哪个好？"
- "帮我比较一下[商品A]和[商品B]"
- "选[商品A]还是[商品B]？"

**2.1 品牌知识** 
- "[品牌]是什么品牌？"
- "[品牌]品牌介绍"
- "[品牌]品牌故事"

**2.2 品类知识** 
- "[品类]怎么选？"
- "怎么选[品类]？"
- "[品类]选购指南"
- "[品类]选购攻略"

**2.3 商品参数** 
- "[商品]的参数是什么？"
- "[商品]配置"
- "[商品]规格"

**3.1 品牌榜单** 
- "[品类]品牌榜"
- "[品类]排行榜"
- "什么牌子的[品类]好？"
- "[品类]哪个牌子好？"

**4.1 CPS商品查询** 
- "搜索[商品]"
- "查找[商品]"
- "哪里买[商品]"
- "[商品]推荐"

**5. 全网比价**

**触发时机：** `xxxx价格`、`xxxx比价`

**价格类：**
- "[品类/品牌/SPU/SKU]价格"
- "[品类/品牌/SPU/SKU]多少钱"

**比价类：**
- "[品类/品牌/SPU/SKU]比价"

## Usage

### 1. 全维度对比决策助手

提供 SPU 参数/口碑/价格全方位对比评测，协助用户做最优选择。

```bash
# 对比两个商品
python3 scripts/compare.py "iphone16和iphone15对比"
python3 scripts/compare.py "华为mate60和小米14对比"
```

**返回数据包含：**
- SPU 基本信息（名称、品牌、型号等）
- 参数对比（规格、配置等）
- 口碑对比（用户评价、优缺点）
- 价格对比（各平台价格）
- 综合推荐建议

### 2. 商品百科知识

提供品类选购指南、品牌科普知识、全维度参数库的服务。

#### 2.1 品牌知识

查询单个品牌的相关信息，包括品牌简介、品牌定位、明星产品、品牌荣誉、品牌大事记。

```bash
# 查询品牌信息
python3 scripts/knowledge.py brand "华为"
python3 scripts/knowledge.py brand "ysl"
```

**返回数据包含：**
- 品牌简介
- 品牌定位
- 明星产品
- 品牌荣誉
- 品牌大事记

#### 2.2 品类知识

查询某个品类的选购知识，如选购要点、选购建议、避坑指南等。

```bash
# 查询品类选购知识
python3 scripts/knowledge.py entity "无人机怎么选"
python3 scripts/knowledge.py entity "怎么选笔记本电脑"
```

**返回数据包含：**
- 选购要点
- 选购建议
- 避坑指南

#### 2.3 商品参数

查询单个 SPU 的参数信息，包括 SPU 名称、图片、价格、参数列表及 AI 解读。

```bash
# 查询商品参数
python3 scripts/knowledge.py param "iphone16"
python3 scripts/knowledge.py param "小米14"
```

**返回数据包含：**
- SPU 名称
- SPU 图片
- 价格
- 参数列表
- 参数 AI 解读

### 3. 实时品牌天梯榜单

基于综合搜索热度、全网声量及销量，提供客观权威的品牌排行推荐服务。

#### 3.1 品牌榜单

查询某个分类下的品牌排行榜信息。

```bash
# 查询品牌榜单
python3 scripts/ranking.py brand "手机品牌榜"
python3 scripts/ranking.py brand "冰箱品牌榜"
```

**返回数据包含：**
- 品牌排名
- 品牌名称
- 推荐理由
- 对应品牌的热门商品

#### 3.2 单品榜

查询某品牌某品类下的单品排行榜信息。

```bash
# 查询单品榜
python3 scripts/ranking.py product "苹果手机排行榜"
python3 scripts/ranking.py product "华为冰箱排行榜"
```

**返回数据包含：**
- 商品排名
- 商品名称
- 商品价格
- 推荐理由

### 4. 全网 CPS 商品

通过商品关键词，获取全网 CPS 商品链接及热卖商品信息。

```bash
# 查询商品
python3 scripts/cps.py "iphone16"
python3 scripts/cps.py "机械键盘"
```

**返回数据包含：**
- 商品名称
- 商品图片
- 商品价格
- 购买链接（使用 `url` 字段）
- 销量信息
- 优惠信息

### 5. 全网比价

**xxxx价格：返回对应层级的价格**
- 品类/品牌 → spu列表价格
- SPU → spu价格 + 各sku价格
- SKU → 各平台商品价格

**xxxx比价：查询到对应sku的商品价格**
- 品类/品牌 → spu列表→第一个spu→第一个sku→商品价格，spu列表query需要修改为xxx价格
- SPU → spu列表→对应spu→第一个sku→商品价格，spu列表query需要修改为xxx价格
- SKU → spu列表→对应spu→对应sku→商品价格，spu列表query需要修改为xxx价格

#### API 层级关系

```
query → spu列表 → spuID → sku列表 → skuID → 商品价格
```

---

#### 5.1 SPU 比价

基于用户 query 返回匹配的 SPU 列表，包含 SPUID、名称、价格等信息。

**触发场景：** 用户询问 "[品类]价格"、"[品牌]价格"

```bash
# 品类价格
python3 scripts/bijia.py spu "手机价格"
python3 scripts/bijia.py spu "冰箱价格"

# 品牌价格
python3 scripts/bijia.py spu "华为价格"
python3 scripts/bijia.py spu "小米价格"
```

**返回数据包含：**
- SPU ID（可用于后续SKU比价）
- SPU 名称
- SPU 图片
- 价格区间
- 品牌
- 相关 SKU 信息

---

#### 5.2 SKU 比价

基于 SPUID 查询该 SPU 下所有 SKU 列表及价格。

**调用流程：** 首先使用 SPU比价能力获取品牌下所有 SPU，然后基于返回结果中的 SPUID 调用 SKU比价。

**示例：**
```bash
# 1. 先用品牌名SPU比价获取SPUID
python3 scripts/bijia.py spu "华为价格"

# 2. 基于返回的SPUID查询该SPU下的所有SKU
python3 scripts/bijia.py sku_list "shv2_09bff5cedd0cc952c7cbaf05e08ae972"
```

**完整调用（SPU名称价格场景）：**
```bash
# 例如用户询问 "Mate 60价格"
# Step 1: 使用品牌名"华为"获取所有SPU
# Step 2: 从结果中找到"Mate 60"对应的SPUID
# Step 3: 基于SPUID调用SKU比价
```

**返回数据包含：**
- SKU ID（可用于后续SKU商品比价）
- SKU 名称
- 规格参数（颜色、存储等）
- 价格信息
- SPU 信息

---

#### 5.3 SKU 商品比价

基于 SKUID 查询该 SKU 下所有商品在不同渠道、不同平台的价格。

**调用流程：** 首先使用 SPU比价获取品牌下所有 SPU，然后基于 SPUID 获取 SKU列表，最后基于 SKUID 调用 SKU商品比价。

**示例：**
```bash
# 1. 先用品牌名SPU比价获取SPUID
python3 scripts/bijia.py spu "华为价格"

# 2. 基于SPUID获取SKU列表及SKUID
python3 scripts/bijia.py sku_list "shv2_09bff5cedd0cc952c7cbaf05e08ae972"

# 3. 基于SKUID查询各平台价格
python3 scripts/bijia.py sku_goods "shv2_62a16fd98771e0ed3aee0f2a6b40dbb9"
```

**完整调用（SKU名称价格场景）：**
```bash
# 例如用户询问 "Mate 60 Pro 12GB+256GB价格"
# Step 1: 使用品牌名"华为"获取所有SPU
# Step 2: 从结果中找到"Mate 60 Pro"对应的SPUID
# Step 3: 基于SPUID获取SKU列表，找到"12GB+256GB"对应的SKUID
# Step 4: 基于SKUID调用SKU商品比价
```

**返回数据包含：**
- 商品名称
- 商品价格
- 购买链接（使用 `cps_url` 字段，当 `cps_url` 有值时作为购买链接展示，当 `cps_url` 为空时则不展示购买链接）
- 平台信息（淘宝、京东、拼多多等）
- 店铺信息
- 优惠信息

## 错误处理

脚本返回的错误信息（`errmsg`字段）及处理措施：

| 错误信息 | 说明 | 处理措施 |
|----------|------|----------|
| `token is limit` | API调用频率限流 | 等待1秒后重试 |
| `path错误` / `请求地址错误` | API请求地址不正确 | 检查脚本路径和调用参数 |
| `token权限不足` | Token未申请对应权限 | 访问 https://openai.baidu.com 申请所需能力 |
| `非法path` | 当前功能暂未支持 | 该路径/API尚未开放，请更换查询方式 |
| `token is nil` | Token未配置 | 检查token |
| `token is invalid` | Token错误 | 检查token |

## 注意事项

1. 确保 `BAIDU_EC_SEARCH_TOKEN` 环境变量已正确设置
2. API 调用有频率限制，脚本已内置 QPS 控制避免触发限流
   - 默认 QPS=1（每秒最多1次请求）
   - 可通过 `BAIDU_EC_SEARCH_QPS` 环境变量调整
3. 部分能力需要单独申请权限，未申请会返回 `token权限不足`
4. Python 脚本使用标准库，无需额外安装依赖
5. 返回的商品链接中可能有 `|` 等特殊字符，在以markdown形式展现链接时需要注意转义
6. 当获取到和用户意图匹配的购买链接时，应优先以markdown的链接格式提供购买链接，而不是直接返回链接文本。
7. 应优先使用接口返回的购买链接，而不是自行推测购买链接