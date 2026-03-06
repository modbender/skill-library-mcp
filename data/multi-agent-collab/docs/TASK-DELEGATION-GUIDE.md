# 任务委派指南 - 用对模型省大钱

> **原则**：简单任务给 Flash（$0.15/1M），复杂任务给 Sonnet（$3/1M）

---

## 💡 可以交给 Gemini Flash 的任务

### 📂 文档整理类
- "用 Flash 归档 CHANGELOG 中 2 周前的内容"
- "用 Flash 清理 TASK.md 中完成的任务"
- "用 Flash 整理 memory/ 文件夹，按月归档"
- "用 Flash 检查所有 .md 文件大小，列出超过 2k tokens 的"

### 🔍 分析汇总类
- "用 Flash 总结今天的 CHANGELOG"
- "用 Flash 统计 TASK.md 中有多少待办/完成任务"
- "用 Flash 生成本周工作周报"
- "用 Flash 检查 git status，列出未提交的文件"

### 🔄 格式转换类
- "用 Flash 将这个 YAML 转成 Markdown 表格"
- "用 Flash 批量重命名文件（加日期前缀）"
- "用 Flash 提取所有 TODO 注释到一个文件"

### ✅ 状态检查类
- "用 Flash 检查所有链接是否有效"
- "用 Flash 验证 YAML 语法"
- "用 Flash 检查是否有重复的任务 ID"

---

## 🎯 命令格式

```
"用 Flash [任务描述]"
"让 Gemini Flash [任务描述]"
"Flash: [任务描述]"
```

我会自动用 `sessions_spawn` 调用 Gemini Flash agent。

---

## 💰 成本对比（单个任务）

| 任务 | Sonnet | Flash | 节省 |
|------|--------|-------|------|
| 归档 CHANGELOG | $0.014 | $0.0003 | **98%** |
| 生成周报 | $0.05 | $0.001 | **98%** |
| 格式转换 | $0.02 | $0.0004 | **98%** |

**每天委派 5 个任务 → 年省 $18+** 🎉

---

## 🚫 不要交给 Flash 的任务

- 复杂代码重构
- 架构设计讨论
- 创意写作
- 深度问题诊断
- 需要上下文推理的任务

这些用 Sonnet 或 Opus！

---

**记住：便宜的模型做重复劳动，贵的模型做创意思考！** 🧠
