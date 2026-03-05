# Simple Mode - 快速修复

适用于问题修复、代码重构、代码审查。

> **核心原则**: 通过状态文件跟踪进度，不依赖会话历史，节省 token。

---

## ⚠️ 重要约束

```
❌ 禁止行为:
- 完成一个修复后输出"总结报告"然后停止
- 中途询问"是否继续"
- 完成主要修复后忽略后续验证步骤

✅ 正确行为:
- 完成修复后，检查是否还有 pending 任务
- 如有 pending 任务，继续执行下一个
- 完成所有修复和验证后才能结束
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
    --input "用户问题描述" --format context > $PROJECT_ROOT/.opencode/.knowledge-context.md
  读取 $PROJECT_ROOT/.opencode/.knowledge-context.md 获取相关历史经验
  > 利用历史经验，快速定位类似问题

步骤1: 状态恢复与问题分析
  使用 `sequential-thinking` 工具进行深度分析
  ├─ 存在 $PROJECT_ROOT/.opencode/progress.txt → 读取当前进度和"下一步"
  │   └─ 存在 $PROJECT_ROOT/.opencode/feature_list.json → 读取任务列表
  └─ 不存在 → 根据用户描述在 $PROJECT_ROOT/.opencode/ 创建新任务

步骤2: 问题理解（修复前必须）
  ├─ 复现问题 - 确认能稳定复现
  ├─ 分析根因 - 定位问题源头
  └─ 制定方案 - 选择最小化修改

步骤3: 修复循环 [WHILE 有 pending 任务]
  3.1 确定当前任务
      ├─ 从 progress.txt 的"下一步"继续
      └─ 或从 feature_list.json 选择第一个 pending 任务
  
  3.2 更新状态为 in_progress
      ├─ 更新 progress.txt 的"当前任务"
      └─ 修改 feature_list.json 中对应任务的 status（如有）
  
  3.3 执行修复
      ├─ 最小化修改代码
      ├─ 运行测试验证
      └─ 确认无回归
  
  3.4 修复完成，更新状态
      ├─ 更新 progress.txt: 移动到"本次完成"
      ├─ 记录"问题根因"和"关键发现"
      ├─ 修改 feature_list.json: status → completed（如有）
      └─ git commit
  
  3.5 健康检查（主进程协调点）
      ├─ 检查是否还有 pending 任务
      ├─ 如有 → 回到 3.1
      └─ 如无 → 退出循环

步骤4: 结果验证（主进程协调点）
  ├─ 确认所有修复任务完成
  ├─ 运行完整测试确认无回归
  └─ 输出修复摘要

步骤5: 知识归纳
  按照 ./evolution-check.md 执行进化检查
```

---

## 何时创建 feature_list.json

| 场景 | 是否创建 |
|------|----------|
| 涉及多个文件 | ✅ |
| 修复范围较大 | ✅ |
| 根因不明确需多步排查 | ✅ |
| 预计需要多个会话完成 | ✅ |
| 单文件简单修复 | ❌ |

---

## 任务拆解原则

```
❌ 模糊: "修复登录失败"

✅ 清晰:
  1. 复现问题 - 记录错误日志和请求参数
  2. 检查前端请求 - 确认请求格式正确
  3. 检查后端响应 - 查看具体错误信息
  4. 定位失败点 - 确定是哪个环节出错
  5. 修复代码 - 最小化改动
  6. 验证修复 - 确认问题解决且无回归
```

---

## 验证方法

| 类型 | 方法 | 时机 |
|------|------|------|
| 编译 | 运行构建命令 | 每次修改后 |
| 单测 | 运行相关测试 | 修复完成后 |
| 功能 | curl/手动测试 | 验证修复 |
| 回归 | 运行完整测试 | 最终验证 |

---

## 错误处理

```
修复失败 → 分析原因 → 尝试方案（最多3次）
├─ 成功 → 继续执行，记录到 progress.txt "问题根因"
└─ 连续失败 → 回退 + 记录详情 + 标记 blocked + 报告用户
```

---

## 状态文件说明

| 文件 | 用途 | 创建时机 |
|------|------|----------|
| `$PROJECT_ROOT/.opencode/progress.txt` | 当前修复进度 | 必须创建 |
| `$PROJECT_ROOT/.opencode/feature_list.json` | 任务清单 | 复杂修复时创建 |


### progress.txt 模板（修复专用）

```
# Progress Log - 修复记录
# 最后更新: 2024-01-01 10:00

## 当前任务
- [ ] 修复登录接口 500 错误

## 本次完成
- [x] 定位问题：数据库连接池耗尽
- [x] 修复：增加连接池大小 10 → 50
- [x] 验证：登录接口恢复正常

## 下一步（如有后续）
1. 添加连接池监控日志
2. 设置连接池告警阈值

## 问题根因
- 现象：登录接口随机 500 错误
- 根因：高并发下数据库连接池耗尽
- 方案：增加连接池大小，添加重试机制

## 关键发现
- 连接泄漏来自未关闭的事务
- 需要添加 finally 块确保连接释放
```

---

## 必须提取经验的场景

| 场景 | 提取 |
|------|------|
| 修复失败2次后成功 | ✅ |
| 发现隐蔽的 bug 根因 | ✅ |
| 环境特定的 workaround | ✅ |
| 用户明确要求记住 | ✅ |
| 简单一行代码修改 | ❌ |
