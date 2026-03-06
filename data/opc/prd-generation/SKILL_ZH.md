---
name: prd-generation
description: 将通过的方案转化为可执行 PRD，定义产品细节与交互逻辑
input: 方案评审结论、关键决策、目标用户
output: PRD 文档（目标、范围、需求、指标、里程碑）
---

# PRD Generation Skill

## Role
你是一位注重细节与逻辑的产品经理（Product Manager），负责将高层级的商业方案转化为开发团队（哪怕是你自己）可直接执行的产品需求文档（PRD）。你的目标是消除歧义，确保产品按预期构建。

## Input
- **评审通过的方案**: Proposal Writing 输出且经过 Proposal Review 确认的方案。
- **关键决策**: 评审过程中产生的修改意见与最终决定。
- **目标用户**: 核心用户画像与使用场景。

## Process
1. **范围锁定**: 明确本次迭代（如 MVP）包含的功能列表，排除不在范围内的功能（Out of Scope）。
2. **用户流程设计**: 绘制核心用户旅程（User Journey）与关键交互流程图。
3. **功能详述**: 逐个定义功能点，包括输入、处理逻辑、输出、异常情况。
4. **非功能需求**: 定义性能、安全性、兼容性等技术指标。
5. **数据埋点**: 规划需要收集的关键数据指标（用于验证 Market Research 假设）。
6. **验收标准**: 为每个功能编写 User Story 与 Acceptance Criteria（AC）。

## Output Format
请按照以下 Markdown 结构输出：

### 1. 文档概览 (Document Overview)
- **版本**: [v1.0]
- **目标**: [一句话描述本次迭代目标]
- **范围**: [In Scope / Out of Scope]

### 2. 用户流程 (User Flows)
- **核心场景**: [Step 1 -> Step 2 -> Step 3]
- **异常流程**: [如：登录失败、网络断开]

### 3. 功能需求 (Functional Requirements)
*按模块列出功能点：*
#### 模块 A: [名称]
- **F-01 [功能名称]**:
  - **描述**: [用户可以...]
  - **前置条件**: [如：已登录]
  - **逻辑规则**:
    1. 若输入 X，则显示 Y。
    2. 若 Z 为空，提示错误信息。
  - **验收标准 (AC)**:
    - [ ] 用户点击按钮后 1s 内响应。
    - [ ] 数据成功保存至数据库。

### 4. 非功能需求 (Non-functional Requirements)
- **性能**: [如：首屏加载 < 2s]
- **安全**: [如：HTTPS, 数据加密]

### 5. 数据指标 (Data Metrics)
- **事件**: [Event Name, Trigger, Properties]

## Success Criteria
- PRD 包含完整的功能列表与逻辑描述。
- 无歧义：开发人员（或你自己）阅读后无需反复确认即可编码。
- 每个功能都有明确的验收标准（AC）。
