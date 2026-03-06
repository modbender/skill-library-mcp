# Full Mode - 完整开发

适用于新建项目和功能开发。

> **核心原则**: 通过状态文件跟踪进度，不依赖会话历史，节省 token。

---

## ⚠️ 重要约束

```
❌ 禁止行为:
- 完成一个任务后输出"总结报告"然后停止
- 看到 review/文档任务后停止执行
- 完成高优先级任务后等待用户确认
- 中途询问"是否继续"

✅ 正确行为:
- 完成任务后，立即检查 feature_list.json 是否还有 pending 任务
- 如有 pending 任务，继续执行下一个
- 只有所有任务状态都是 completed 时，才输出最终总结
- 循环执行直到没有 pending 任务
```

---

## 核心流程

```
步骤0: 环境准备（必须执行）
  # 设置路径变量
  SKILLS_DIR=$([ -d ~/.config/opencode/skills/evolving-agent ] && echo ~/.config/opencode/skills || echo ~/.claude/skills)
  
  # 获取项目根目录（避免在 submodule 中创建 .opencode）
  PROJECT_ROOT=$(git rev-parse --show-toplevel)
  
  # 知识检索
  python $SKILLS_DIR/evolving-agent/scripts/run.py knowledge trigger \
    --input "用户输入描述" --format context > $PROJECT_ROOT/.opencode/.knowledge-context.md
  读取 $PROJECT_ROOT/.opencode/.knowledge-context.md 获取相关历史经验

步骤1: 状态恢复与任务分析
  使用 `sequential-thinking` 工具进行深度分析
  ├─ 存在 $PROJECT_ROOT/.opencode/feature_list.json → 读取任务列表，恢复上下文
  │   └─ 存在 $PROJECT_ROOT/.opencode/progress.txt → 读取当前进度和"下一步"
  └─ 不存在 → 执行初始化（步骤2）

步骤2: 任务拆解与初始化（仅首次）
  使用 `sequential-thinking` 生成 todos
  ├─ 在项目根目录创建 $PROJECT_ROOT/.opencode/feature_list.json（模板: ../template/feature_list.json）
  ├─ 将 todos 写入 feature_list.json
  └─ 选取第一个 pending 任务，写入 $PROJECT_ROOT/.opencode/progress.txt（模板: ../template/progress.txt）
  
  ⚠️ 注意：.opencode 必须在 $PROJECT_ROOT 下，不是当前目录！

步骤3: 编程循环 [WHILE 有 pending 任务]
  3.1 确定当前任务
      ├─ 从 progress.txt 的"下一步"继续
      └─ 或从 feature_list.json 选择第一个 pending 任务
  
  3.2 更新状态为 in_progress
      ├─ 修改 feature_list.json 中对应任务的 status
      └─ 更新 progress.txt 的"当前任务"
  
  3.3 执行开发
      ├─ 编写代码
      ├─ 编写单元测试
      └─ 运行测试验证
  
  3.4 测试通过，更新状态
      ├─ 修改 feature_list.json: status → completed
      ├─ 更新 progress.txt: 移动到"本次完成"
      └─ 记录"遇到的问题"和"关键决策"
  
  3.5 健康检查（主进程协调点）
      ├─ 检查是否还有 pending 任务
      ├─ 如有 → 回到 3.1
      └─ 如无 → 退出循环

步骤4: 结果验证（主进程协调点）
  ├─ 确认所有任务状态为 completed
  └─ 输出最终执行摘要

步骤5: 知识归纳
  按照 ./evolution-check.md 执行进化检查
```

---

## 任务拆解原则

每个任务必须满足：
- **< 30分钟**可完成
- **可独立测试**验证
- **单一职责**，专注一个问题
- **按依赖顺序**排列

---

## 错误处理

```
错误发生 → 分析原因 → 尝试方案（最多3次）
├─ 成功 → 继续执行，记录到 progress.txt "遇到的问题"
└─ 连续失败 → 回退 + 记录详情 + 标记 blocked + 报告用户
```

---

## 状态文件说明

| 文件 | 用途 | 模板 |
|------|------|------|
| `$PROJECT_ROOT/.opencode/feature_list.json` | 任务清单和状态 | `../template/feature_list.json` |
| `$PROJECT_ROOT/.opencode/progress.txt` | 当前任务进度 | `../template/progress.txt` |

> **注意**: `progress.txt` 只保存当前任务详情，历史任务查看 `feature_list.json`
