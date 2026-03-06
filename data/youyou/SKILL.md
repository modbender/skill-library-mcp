---
name: youyou
description: Personal health data management with natural language interaction. Use when user wants to record health metrics (blood pressure, weight, blood sugar), store medical reports/images, track medications, manage health profiles, or get multi-specialty consultation analysis. Triggers on health-related queries like "记录血压", "存体检报告", "药物提醒", "会诊分析", or mentions of symptoms, checkups, medications.
author: frxiaobei@elyfinn
repository: https://github.com/frxiaobei/frxiaobei-skills
license: MIT
---

# YouYou 佑佑

私人健康数据管理助手，自然语言交互，无需记命令。

## 核心能力

| 类别 | 说明 |
|------|------|
| 档案管理 | 身高、体重、血型、过敏史、家族病史 |
| 日常记录 | 血压、血糖、体重、症状、用药 |
| 报告存储 | 体检报告、化验单、影像检查（支持图片） |
| 用药管理 | 药物记录、相互作用检查、提醒 |
| 多学科会诊 | 17 专科视角综合分析 |

## 数据存储

所有数据存储在 `data/` 目录：

```
data/
├── profile.json           # 基本档案
├── allergies.json         # 过敏史
├── medications/           # 用药记录
├── 生化检查/YYYY-MM/      # 化验结果
├── 影像检查/YYYY-MM/      # 影像报告
├── 手术记录/              # 手术历史
└── 出院小结/              # 出院记录
```

## 自然语言触发

无需记忆命令格式，自然表达即可：

**记录健康数据：**
- "今天血压 135/88" → 自动记录血压
- "体重 72kg" → 更新体重
- "早上空腹血糖 6.2" → 记录血糖

**存储报告：**
- 发送图片 → 自动识别报告类型并存储
- "存一下这个化验单" + 图片 → 存储化验结果

**查询历史：**
- "上次血压多少" → 查询最近记录
- "最近三个月的体检报告" → 列出报告

**用药管理：**
- "开始吃阿司匹林，每天一片" → 记录用药
- "检查一下我的药有没有冲突" → 相互作用检查

**会诊分析：**
- "综合分析我的健康状况" → 17 专科会诊
- "从心内科角度看看我的报告" → 单专科分析

## 专科会诊

读取 `specialists/` 目录下的专科模板：

- 心血管科 (cardiology.md)
- 内分泌科 (endocrinology.md)
- 消化科 (gastroenterology.md)
- 肾内科 (nephrology.md)
- 血液科 (hematology.md)
- 呼吸科 (respiratory.md)
- 神经科 (neurology.md)
- 肿瘤科 (oncology.md)
- 全科 (general.md)
- 等 17 个专科

## 安全边界

⚠️ **重要声明**：

1. 本技能仅用于健康数据整理，不提供医学诊断
2. 任何异常指标建议尽快就医
3. 不提供用药剂量建议
4. 数据仅存储本地，不外传

## 命令参考

完整命令定义见 `commands/` 目录。常用：

| 文件 | 用途 |
|------|------|
| profile.md | 档案管理 |
| medication.md | 用药记录 |
| interaction.md | 药物相互作用 |
| consult.md | 多学科会诊 |
| specialist.md | 单专科分析 |
| save-report.md | 保存报告 |
| query.md | 查询记录 |

## 初始化

首次使用时创建数据目录：

```bash
mkdir -p data/{medications,生化检查,影像检查,手术记录,出院小结}
```

然后通过自然对话建立基本档案："我叫张三，男，35岁，身高175cm，体重72kg"

---

## 致谢

基于 [WellAlly-health](https://github.com/huifer/WellAlly-health) 开源项目封装。

## 关于

由 **frxiaobei@elyfinn** 维护

- 主页：[elyfinn.com/skills/youyou](https://elyfinn.com/skills/youyou)
- 问题反馈：[GitHub Issues](https://github.com/frxiaobei/frxiaobei-skills/issues)
- 作者：[@frxiaobei](https://x.com/frxiaobei) & Finn 🦊
