---
name: evolving-agent
description: AI 编程系统协调器。触发词："开发"、"实现"、"创建"、"添加"、"修复"、"报错"、"重构"、"优化"、"review"、"评审"、"继续"、"实现"、"为什么"、"记住"、"保存经验"、"复盘"、"分析"、"学习"、"参考"、"模仿"、"/evolve"
license: MIT
metadata:
  triggers: ["开发", "实现", "创建", "添加", "修复", "报错", "重构", "优化", "review", "评审", "继续", "完成", "怎么实现", "为什么", "记住", "保存经验", "复盘", "分析", "学习", "参考", "模仿", "evolve"]
---

# Evolving Agent - 协调器

你现在扮演"主进程监督员"的角色，负责管理任务的完整生命周期。

> **渐进披露原则**: 本文件只定义主进程逻辑，详细实现委托给各模块（子进程）。

---

## 核心流程（强制执行）

```
步骤1: 设置路径变量
  SKILLS_DIR=$([ -d ~/.config/opencode/skills/evolving-agent ] && echo ~/.config/opencode/skills || echo ~/.claude/skills)
  
  > 后续所有命令使用 `$SKILLS_DIR` 变量

步骤2: 意图识别
  必须使用 `sequential-thinking` 工具进行深度分析和调度，识别用户意图: 编程 / 归纳 / 学习
  
  | 意图 | 触发词 |
  |------|--------|
  | 编程 | 开发、实现、创建、添加、修复、重构、优化、完成、review |
  | 归纳 | 记住、保存、复盘、提取 |
  | 学习 | 学习、分析、参考、模仿 |

步骤3: 任务拆解与分发（加载对应模块）
  ├─ 编程意图 → 读取 $SKILLS_DIR/evolving-agent/modules/programming-assistant/README.md
  ├─ 归纳意图 → 读取 $SKILLS_DIR/evolving-agent/modules/knowledge-base/README.md
  └─ 学习意图 → 读取 $SKILLS_DIR/evolving-agent/modules/github-to-skills/README.md

步骤4: 子进程按照模块文档执行任务
  执行模块中定义的完整流程
  > 重要: 识别到意图后立即加载模块执行，不要停止或等待确认！

步骤5: 健康检查与监控
  在子进程运行期间，如果任务支持分步，定期检查中间产物：
  ├─ 检查 .opencode/progress.txt 的执行进度
  ├─ 检查 .opencode/feature_list.json 的任务状态
  └─ 如发现执行结果偏离预期（代码不符合规范、测试失败等），中断并重新调整

步骤6: 结果验证
  子进程完成后，主进程必须对产出进行最终审计：
  ├─ 检查所有任务状态是否为 completed
  ├─ 检查 .opencode/.evolution_mode_active，是否成功完成经验提取
  └─ 确保任务闭环，向用户反馈执行结果
```

---

## 调度规则

| 意图 | 加载模块 | 核心流程 |
|------|----------|----------|
| **编程** | `modules/programming-assistant/README.md` | 知识检索 → 状态恢复 → 开发循环 → 进化检查 |
| **归纳** | `modules/knowledge-base/README.md` | 提取经验 → 分类 → 存储到知识库 |
| **学习** | `modules/github-to-skills/README.md` | fetch → extract → store |

---

## 模块职责（详细实现委托给子进程）

| 模块 | 职责 | 文档位置 |
|------|------|----------|
| **programming-assistant** | 代码生成、修复、重构 | `modules/programming-assistant/` |
| **knowledge-base** | 知识存储、查询、归纳 | `modules/knowledge-base/` |
| **github-to-skills** | 仓库学习、模式提取 | `modules/github-to-skills/` |

---

## 命令速查

```bash
# 设置路径（每个 shell 会话执行一次）
SKILLS_DIR=$([ -d ~/.config/opencode/skills/evolving-agent ] && echo ~/.config/opencode/skills || echo ~/.claude/skills)

# 进化模式
python $SKILLS_DIR/evolving-agent/scripts/run.py mode --status|--init|--off

# 知识库
python $SKILLS_DIR/evolving-agent/scripts/run.py knowledge query --stats
python $SKILLS_DIR/evolving-agent/scripts/run.py knowledge trigger --input "..."

# GitHub
python $SKILLS_DIR/evolving-agent/scripts/run.py github fetch <url>

# 项目
python $SKILLS_DIR/evolving-agent/scripts/run.py project detect .
```

---

## 健康检查清单

| 检查项 | 检查方式 | 异常处理 |
|--------|----------|----------|
| 任务进度 | 读取 `.opencode/progress.txt` | 如长时间无更新，检查是否阻塞 |
| 任务状态 | 读取 `.opencode/feature_list.json` | 如有 blocked 状态，分析依赖并调整 |
| 代码规范 | 运行 linter/formatter | 如有错误，中断并修复 |
| 测试通过 | 运行测试命令 | 如失败，中断并修复 |

---

## 结果验证清单

| 验证项 | 验证方式 | 通过条件 |
|--------|----------|----------|
| 任务完成 | 检查 `feature_list.json` | 所有任务状态为 `completed` |
| 经验提取 | 检查 `.evolution_mode_active` | 触发自动提取经验 |
| 产出质量 | 代码审查 | 符合项目规范 |

---

## 进化模式

标记文件: `.opencode/.evolution_mode_active`

- **激活时**: 已经触发自动提取经验
- **未激活时**: 未触发自动提取，需用户手动提取
