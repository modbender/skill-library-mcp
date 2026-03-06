---
name: money-maker-hand
version: 1.0.0
description: 自主赚钱助手 - 自动寻找赚钱机会、调研市场、生成报告
runtime: prompt_only
---

# Money Maker Hand - 自主赚钱助手

## 🎯 核心功能

自主运行，帮你寻找和评估赚钱机会：
- 市场调研（知乎/小红书/Upwork）
- 赚钱机会发现
- 竞品分析
- 收入追踪
- 生成可执行建议

---

## 🔄 运行流程 (7 阶段)

### Phase 1: 状态恢复
```
1. memory_recall 检查 `money_maker_state`
2. 读取现有收入数据库 `income_database.json`
3. 加载历史报告
```

### Phase 2: 收入来源配置
```
目标收入：10,000 元/月
当前收入：0 元
缺口：10,000 元
优先方向：小说 + Skills + 外包
```

### Phase 3: 机会发现
```
执行多平台调研：
1. 知乎盐选 - 热门题材/过稿率/稿费标准
2. 小红书 - 变现方式/广告报价
3. Upwork/Freelancer - AI 相关外包需求
4. ClawHub - 热门 Skills/定价策略
```

### Phase 4: 机会评估
```
每个机会评分 (0-100)：
- 市场需求：+30 (搜索量/竞争度)
- 变现潜力：+30 (单价×数量)
- 进入门槛：+20 (技能匹配度)
- 时间投入：+20 (ROI)
```

### Phase 5: 竞品分析
```
对 Top 3 竞品深度分析：
- 产品/服务详情
- 定价策略
- 营销渠道
- 优劣势对比
```

### Phase 6: 生成报告
```
输出格式：Markdown 报告
包含：
1. 本周收入进度
2. Top 5 赚钱机会 (按评分排序)
3. 详细行动计划
4. 风险提示
```

### Phase 7: 状态持久化
```
1. 更新 `income_database.json`
2. memory_store `money_maker_state`
3. 更新仪表盘指标
```

---

## 💰 追踪的收入来源

| 来源 | 目标 | 当前 | 状态 |
|------|------|------|------|
| 知乎盐选 | 5,000 元 | 0 元 | ⏳ 审核中 |
| 小红书 | 3,000 元 | 0 元 | ⏳ 待发布 |
| Skill 开发 | 2,000 元 | 0 元 | 🔄 准备中 |
| 外包接单 | 1,000 元 | 0 元 | ⏳ 待启动 |
| **月度总计** | **10,000 元** | **0 元** | ⏳ 第 2 天 |

---

## 📊 仪表盘指标

```json
{
  "money_maker_income_month": 0,
  "money_maker_income_goal": 10000,
  "money_maker_progress_percent": 0,
  "money_maker_days_remaining": 28,
  "money_maker_daily_target": 357,
  "money_maker_opportunities_found": 0,
  "money_maker_reports_generated": 0,
  "money_maker_last_report_date": null
}
```

---

## 🎯 使用示例

### 激活 Hand
```
openfang hand activate money-maker
```

### 查看状态
```
openfang hand status money-maker
```

### 手动触发报告
```
帮我生成这周的赚钱机会报告
```

### 配置目标
```
这个月我要赚到 1 万元，帮我规划一下
```

---

## 📋 报告模板

```markdown
# 赚钱机会周报

## 本周收入进度
- 目标：10,000 元
- 当前：0 元
- 进度：0%
- 剩余天数：28 天
- 日均需要：357 元/天

## Top 5 赚钱机会

### 1. 知乎盐选投稿 (评分：85/100)
**机会描述**: 《便利店夜班》已投稿，等待审核
**预期收入**: 500-5,000 元
**时间投入**: 已完成
**成功率**: 高 (已达标)
**下一步**: 等待审核结果，准备第 2 篇

### 2. 小红书起号 (评分：80/100)
**机会描述**: AI 工具教程/效率技巧内容
**预期收入**: 1,000-10,000 元/月
**时间投入**: 2 小时/天
**成功率**: 中高
**下一步**: 发布第 1 篇内容

### 3. Skill 开发外包 (评分：75/100)
**机会描述**: 为其他 OpenClaw 用户开发 Skills
**预期收入**: 500-2,000 元/个
**时间投入**: 1-2 天/个
**成功率**: 中
**下一步**: 完成自媒体文案 Skill

### 4. 知乎问答带货 (评分：70/100)
**机会描述**: AI 工具推荐 + 分销链接
**预期收入**: 100-1,000 元/月
**时间投入**: 1 小时/天
**成功率**: 中
**下一步**: 调研分销平台

### 5. 技术文档翻译 (评分：65/100)
**机会描述**: OpenClaw 中文文档维护
**预期收入**: 500-1,000 元/月
**时间投入**: 2 小时/周
**成功率**: 中低
**下一步**: 联系官方

## 详细行动计划

### 今天 (第 2 天)
- [ ] 发布小红书第 1 篇
- [ ] 启动自媒体文案 Skill 开发
- [ ] 调研 Upwork 外包机会

### 本周
- [ ] 小红书发布 3 篇内容
- [ ] 完成 Skill 设计文档
- [ ] 申请 Upwork 账号

## 风险提示
1. 知乎盐选审核可能不通过 → 准备备选投稿平台
2. 小红书起号需要时间 → 保持耐心，持续输出
3. Skill 开发可能遇到技术难点 → 预留缓冲时间
```

---

## 🔧 配置选项

```toml
# 收入目标
income_goal = 10000  # 元/月
income_sources = ["知乎盐选", "小红书", "Skill 开发", "外包"]

# 报告频率
report_schedule = "weekly_sunday"  # 每周日生成报告

# 机会筛选
min_opportunity_score = 60  # 最低评分门槛
max_opportunities = 10  # 最多展示机会数

# 输出格式
output_format = "markdown"  # markdown/csv/json
```

---

## 📝 学习笔记

### 从 OpenFang Lead Hand 借鉴
1. ✅ 7 阶段运行流程
2. ✅ 知识图谱存储 (knowledge_add_entity)
3. ✅ 仪表盘指标设计
4. ✅ 配置化设置
5. ✅ 状态持久化

### 适配 OpenClaw 的改进
1. 用 file_read/write 替代 file 工具
2. 用 memory_store/recall 替代 knowledge_*
3. 用 sessions_send 替代 dashboard
4. 简化为单文件 Skill

---

*此 Skill 受 OpenFang Lead Hand 启发创建*
