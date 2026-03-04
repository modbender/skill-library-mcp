---
name: skill-governance
description: OpenClaw Cognitive Operating & Skill Governance Kernel
---

# 🧠 OpenClaw 认知与技能治理内核 v2.1

> 本协议不只是管理技能，而是管理认知资源、上下文负载与交付闭环。

---

# 0️⃣ GLOBAL PRIME DIRECTIVE
系统优化目标：
[ Maximize ; Output / (Noise \times Cognitive\ Load) ]
任何行为若增加噪音或认知负载而不增加输出，必须拒绝。

---

# 1️⃣ 感知层协议 (Perception Protocol)

## 1.1 强制脱水规则 (Mandatory Dehydration)
若 Raw_Data > 500 条 或 > 2000 tokens：
必须先执行：
* 低成本摘要（Flash）
* 输出仅包含：
    * Top 高频主题 (≤10)
    * 异动信号 (≤5)
    * 潜在机会 (≤3)
禁止：
* 将全量原始数据直接传入主模型

## 1.2 信号阈值规则
只有满足以下任一条件，才允许进入分析阶段：
* 增长率 > 30%
* 偏离历史均值 > 2σ
* 直接影响现金流或决策
否则自动丢弃。

---

# 2️⃣ 决策层协议 (Cognitive Budget Protocol)

## 2.1 每日启动校准
每日首次任务前，必须输入：
* Sleep (1-10)
* Focus (1-10)
* Stability (1-10)
计算： [ Capacity = (S + F + St) / 3 ]

## 2.2 权限锁定规则
Capacity ≤ 4 → 禁止：
* 架构重构
* 多技能联动 (>2)
* 高复杂调研
Capacity 5–7 → 允许分析类任务
Capacity ≥ 8 → 允许战略级任务

---

# 3️⃣ 动态挂载内核 (Contextual Mounting Kernel)

## 3.1 场景触发器
检测关键词：
* 调研 / Research → research.bundle
* 复盘 / Review → analytics.bundle
* 部署 / Deploy → automation.bundle
* 谈判 / Strategy → decision.bundle
自动执行： mount bundle
任务结束： unmount bundle

## 3.2 认知负载上限
同时挂载技能 ≤ 7
超过立即警告： ⚠ Cognitive Overload Risk

---

# 4️⃣ 执行闭环协议 (Mandatory Closure Protocol)
⚠ 这是强制规则。
任务结束前必须满足：

## 4.1 产出验证
至少生成以下之一：
* 文件
* 结构化笔记
* 决策记录
否则不允许标记完成。

## 4.2 自动归档
强制生成： /memory/YYYY-MM-DD-task.md
结构固定：
# 决策
# 核心数据
# 下一步行动
# 置信度

## 4.3 高级任务推送规则
若任务类型为：
* 财务
* 战略
* 重大决策
必须生成摘要用于外部同步（笔记或移动端）。
禁止停留在本地缓存。

---

# 5️⃣ 生命周期与淘汰 (Evolution Engine)
## 5.1 30 天未调用 → 移入 archived_skills/
## 5.2 60 天仍未恢复 → 标记为删除候选
## 5.3 删除前必须发送通知
⚠ 24 小时缓冲期 支持 restore <skill_name>

---

# 6️⃣ 故障熔断规则
单任务中：
Skill 报错 ≥ 3 次 → 立即停止 → 标记为 Unstable → 禁止盲重试

---

# 7️⃣ 输出契约 (Output Contract)
每次技能调用输出必须包含：
🔍 一句话结论
📊 关键数据
⚠ 置信度说明

---

# 使用说明
仅在以下情况加载本协议：
* 引入新技能
* 重构技能体系
* 大规模调研
* 多技能联动规划
* 高级战略任务

执行顺序：
1. 检查认知预算
2. 决定是否允许任务
3. 动态挂载所需技能
4. 执行脱水
5. 执行任务
6. 强制生成归档
