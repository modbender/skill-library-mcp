---
name: memory-on-demand
description: "按需记忆检索。当用户询问历史相关问题时，自动搜索 memory 和 QMD 获取相关信息。"
argument-hint: "自动记忆检索"
---

# Memory On Demand - 按需记忆检索

## 触发条件

当用户问题包含以下关键词时自动触发：
- "之前"、"以前"、"上次"
- "历史"、"记录"
- "那次"、"那次"
- "还记得吗"
- "我之前"
- "之前我们"
- "那时候"

## 执行流程

### 1. 判断是否需要检索
检查用户问题是否与历史记录相关。

### 2. 选择检索方式

**首选：QMD 搜索**（更快、更准确）
```bash
qmd search "关键词" --limit 5
```

**备选：Memory 搜索**
```bash
# 搜索 memory 文件
grep -r "关键词" ~/.openclaw/workspace/memory/

# 或使用 memory_search
```

### 3. 返回结果
将搜索结果整理后返回给用户。

## 使用示例

用户问："之前那次健身训练的记录是什么？"

自动执行：
1. 检测到"之前"关键词
2. 执行 `qmd search "健身 训练"`
3. 返回相关记录

## 优势

- **按需加载**：只在需要时搜索，不浪费 context
- **自动触发**：无需手动指定
- **多源检索**：QMD + Memory 双保险

## 配置

- QMD 索引：已配置 workspace + butler + researcher + sessions
- Memory 文件：自动读取 memory/*.md

---
*自动记忆检索 skill*
