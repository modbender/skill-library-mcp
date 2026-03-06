# Prompt Templates

预设的任务提示词模板。

## Bug Fix

```
在 {repo} 中修复以下问题：
{description}

相关文件：{files}
错误信息：{error_message}

请：
1. 分析问题根因
2. 编写修复代码
3. 确保通过现有测试
4. 如需新测试，一并编写
```

## Feature

```
在 {repo} 中实现新功能：{feature_name}

需求描述：{description}

请：
1. 先了解现有代码结构
2. 设计实现方案
3. 编写代码
4. 编写测试
5. 更新相关文档
```

## Refactor

```
在 {repo} 中重构 {target}：

重构目标：{goal}
约束条件：{constraints}

请：
1. 先理解现有代码
2. 确保重构后功能不变
3. 运行所有测试
4. 保持代码风格一致
```

## Subagent Task Contract (Recommended for Orchestrator)

```
你是本次多 Agent 开发流程中的一个 subagent。

【任务目标】
{goal}

【仓库与分支】
- Repo: {repo}
- Branch: {branch}

【范围】
- In Scope: {in_scope}
- Out of Scope: {out_of_scope}

【修改边界】
- 允许修改: {allowed_paths}
- 禁止修改: {forbidden_paths}

【交付要求（DoD）】
1. 完成目标功能/修复
2. 运行并汇报相关测试（至少列出命令与结果）
3. 更新必要文档/注释（如适用）
4. 提交变更并创建 PR（如环境允许）

【阻塞处理】
如果遇到阻塞，请停止盲目尝试，并按以下格式汇报：
- Blocker:
- 已尝试:
- 需要的输入/决策:

【最终输出格式（严格按此格式）】
1. Summary: 一句话总结本次改动
2. Changes: 列出修改的文件与主要变化
3. Tests: 列出执行的命令和结果（通过/失败/未运行 + 原因）
4. Risks: 潜在风险或待确认点
5. PR: PR 链接或“未创建（原因）”
```
