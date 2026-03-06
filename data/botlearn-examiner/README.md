# @botlearn/openclaw-examiner

OpenClaw Agent 能力评测系统 - 标准化考试、评分和雷达图生成，用于多维度能力评估。

## 概述

`openclaw-examiner` 是一个专门用于评测 OpenClaw Agent 能力的 Skill。与 `openclaw-doctor`（健康检查）不同，本 Skill 专注于**能力测量**而非系统健康状况。

## 核心功能

### 1. 考试管理
- 全量考试（8 个维度，40 道题）
- 单维考试（专注某一维度）
- 快速检查（每维度 2-3 题）
- 练习模式（即时反馈）

### 2. 能力维度

| 维度 | 描述 | 权重 |
|------|------|------|
| 信息检索 | 查找、过滤和组织信息的能力 | 12.5% |
| 内容理解 | 理解、总结和分析内容的能力 | 12.5% |
| 逻辑推理 | 问题解决、演绎和模式识别 | 12.5% |
| 代码生成 | 编写、重构和调试代码 | 12.5% |
| 创意生成 | 产生原创文本、想法和解决方案 | 12.5% |
| 工具使用 | 有效使用技能、API 和外部工具 | 12.5% |
| 记忆与上下文 | 检索和应用注入的知识 | 12.5% |
| 质量与准确性 | 输出的精确性、完整性和正确性 | 12.5% |

### 3. 评分系统
- **0-5 分制**：每条评分标准
- **加权计算**：根据标准权重计算题分
- **维度汇总**：维度内题目平均分
- **总体得分**：8 个维度的加权平均

### 4. 报告输出
- 总体能力得分和等级
- ASCII 雷达图可视化
- 各维度详细分析
- 与人群基准对比
- 改进建议和学习资源

## 安装

```bash
clawhub install @botlearn/openclaw-examiner
```

## 使用方法

### 触发词

- "exam"
- "test"
- "evaluation"
- "assessment"
- "capability check"
- "radar chart"
- "能力评测"
- "考试"
- "能力评估"

### 示例对话

```
用户: 运行一次能力评测考试

Examiner: # OpenClaw Capability Examination

**Session ID**: exam-20240302-143022
**Exam Type**: Full Exam
**Dimensions**: 8 dimensions
**Questions**: 40 questions
**Estimated Time**: 60-90 minutes

## Instructions
- Answer questions in the specified JSON format
- Partial answers are better than skipping
- Focus on quality over speed

## Ready?
Type "START" to begin the examination.

用户: START

Examiner: ---
Question 1/40 | Dimension: Information Retrieval
Difficulty: Easy | Time Limit: 3 minutes | Max Score: 100
---

## Question
Search for information about the latest release of OpenClaw Agent...
[Continue with question delivery]
```

## 答案格式

所有答案必须使用标准 JSON 格式：

```json
{
  "questionId": "IR-EASY-001",
  "dimension": "Information Retrieval",
  "timestamp": "2024-03-02T14:30:22Z",
  "answer": {
    "type": "json",
    "content": { /* answer content */ }
  },
  "reasoning": "Explanation of approach",
  "toolsUsed": ["@botlearn/google-search"],
  "confidence": "high"
}
```

## 评分标准

每个问题包含 2-4 个评分标准：

| 分数 | 描述 |
|------|------|
| 5 | 优秀 - 超出预期 |
| 4 | 良好 - 达到预期，轻微问题 |
| 3 | 满意 - 达到最低要求 |
| 2 | 一般 - 部分达到要求 |
| 1 | 差 - 最低限度达成 |
| 0 | 无 - 无意义尝试 |

## 文件结构

```
openclaw-examiner/
├── package.json           # npm 包配置
├── manifest.json          # Skill 元信息
├── SKILL.md               # 角色和能力定义
├── knowledge/
│   ├── Domain.md          # 评测框架和维度定义
│   ├── Scoring.md         # 评分方法和标准
│   └── QuestionBank.md    # 问题库和示例
├── strategies/
│   └── Main.md            # 执行策略
└── tests/
    ├── smoke.json         # 冒烟测试
    └── benchmark.json     # 基准测试
```

## 评测等级

| 等级 | 分数范围 | 描述 |
|------|----------|------|
| Expert | 90-100 | 卓越能力，处理复杂场景 |
| Advanced | 80-89 | 高级能力，处理复杂任务 |
| Proficient | 70-79 | 熟练能力，稳定表现 |
| Competent | 60-69 | 胜任能力，标准表现 |
| Beginner | 0-59 | 初级能力，需要指导 |

## 与其他 Skill 的区别

| Skill | 目的 | 输出 |
|-------|------|------|
| `openclaw-doctor` | 系统健康检查 | 健康评分、问题列表 |
| `openclaw-autodidact` | 7天学习复盘 | 成长报告、社区连接 |
| `openclaw-examiner` | 能力评测 | 能力剖面、雷达图 |

## 依赖关系

本 Skill 无外部依赖，可独立运行。

## 版本

当前版本：0.1.0

## 许可证

MIT

## 作者

BotLearn

---

**注意**：本评测工具测量能力，而非价值。请利用结果指导学习之旅，而非自我评判。
