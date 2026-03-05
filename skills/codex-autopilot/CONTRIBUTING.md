# 贡献指南

感谢你对 AI WorkFlow Skill 的关注！我们欢迎任何形式的贡献。

---

## 报告问题

如果你发现了 bug 或有改进建议，请：

1. 先搜索是否已有相关 Issue
2. 如果没有，创建新 Issue，包含以下信息：
   - 问题描述
   - 复现步骤
   - 期望行为
   - 实际行为
   - 环境信息

---

## 功能建议

如果你有新功能的想法：

1. 创建 Issue，标题以 `[Feature]` 开头
2. 描述清楚：
   - 你想要什么功能
   - 为什么需要这个功能
   - 可能的实现方式

---

## 提交代码

### 1. Fork 仓库

点击右上角的 Fork 按钮

### 2. 克隆到本地

```bash
git clone https://github.com/你的用户名/AIWorkFlowSkill.git
cd AIWorkFlowSkill
```

### 3. 创建分支

```bash
git checkout -b feature/your-feature-name
```

### 4. 修改代码

请遵循现有的代码风格和格式

### 5. 提交更改

```bash
git add .
git commit -m "feat: 添加 xxx 功能"
```

提交信息格式：
- `feat`: 新功能
- `fix`: 修复
- `docs`: 文档更新
- `style`: 格式调整
- `refactor`: 重构

### 6. 推送并创建 PR

```bash
git push origin feature/your-feature-name
```

然后在 GitHub 上创建 Pull Request

---

## Skill 编写规范

如果你要添加或修改 Skill，请遵循以下规范：

### 文件结构

```
skill-name/
└── SKILL.md
```

### SKILL.md 格式

```markdown
---
name: Skill 名称
description: Skill 描述
version: 1.0.0
updated: YYYY-MM-DD
---

# Skill 名称

> 一句话介绍

## 速查表
[快速参考内容]

## 关联 Skill
[与其他 Skill 的关系]

## 使用场景
[触发条件]

## 主要内容
[Skill 的核心内容]

## 下一步
[完成后的下一步]
```

### 规范要求

1. **版本号**：使用语义化版本 (SemVer)
2. **速查表**：每个 Skill 都要有速查表
3. **关联说明**：明确与其他 Skill 的关系
4. **使用场景**：列出触发 Skill 的常见语句
5. **中文优先**：内容以中文为主
6. **纯文本标记**：使用 `[OK]`/`[X]`/`[!]` 替代emoji，提高兼容性

---

## 代码审查

所有 PR 都会经过审查，我们会关注：

- 是否符合项目规范
- 是否有清晰的文档
- 是否有潜在问题

---

## 行为准则

- 尊重他人
- 建设性沟通
- 共同学习

---

感谢你的贡献！
