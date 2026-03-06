---
name: lessons_learned Skill
description: 当检测到以下词汇时，立即停止，不执行任何操作：
---

# lessons_learned Skill

> OpenClaw Skill - 错误学习与长期记忆系统

---

## 触发条件

### 自动触发
- 用户表达偏好: "我喜欢..." / "不要..." / "记住..."
- 操作失败时
- 执行高风险操作时
- 用户输入包含禁止词
- 用户输入包含紧急停止词

### 手动触发
```
/lessons_learned learn <错误描述>    # 记录错误
/lessons_learned check <操作>         # 检查操作
/lessons_learned memory <内容>       # 持久化信息
```

---

## 执行流程

### 1. 禁止词检查（最高优先级）

当检测到以下词汇时，**立即停止**，不执行任何操作：

```
删除 / 清空 / 格式化 / rm -rf
发送邮件 / 发消息 / 提交代码
执行命令 / sudo / chmod 777
```

**反应**：
```
立即停止操作
输出："这个操作有风险，请确认是否执行"
等待用户确认
```

### 2. 紧急停止检查

当用户输入包含以下词汇时，**立即停止所有操作**：
- 停止 / stop / halt
- 取消 / cancel / abort
- 住手 / hold on / wait

### 3. 用户习惯匹配

根据用户习惯自动执行：
- 用户说中文 → 用中文回复
- 用户说英文 → 用英文回复
- 用户给文件路径 → 先读取内容
- 用户给URL → 先获取内容

### 4. 错误记录

当操作失败时：
1. 记录到 `memory/lessons/MISTAKES.md`
2. 分析失败原因
3. 生成避免规则
4. 写入 `memory/lessons/LESSONS_LEARNED.md`

### 5. 信息持久化

当用户表达偏好时：
1. 立即写入 `MEMORY.md`
2. 在 `memory/lessons/HABITS.md` 记录习惯
3. 更新 `memory/lessons/PROHIBITED.md` 如需要

---

## 核心规则

### 禁止
- ❌ 重复已知的失败操作
- ❌ 忽略已记录的用户偏好
- ❌ 跳过禁止词检查
- ❌ 忽略紧急停止词

### 必须
- ✅ 禁止词 → 立即停止
- ✅ 紧急停止词 → 立即停止
- ✅ 偏好 → MEMORY.md
- ✅ 失败 → MISTAKES.md
- ✅ 习惯 → HABITS.md
- ✅ 风险操作 → 确认

---

## 文件位置

| 文件 | 用途 |
|------|------|
| memory/lessons/MISTAKES.md | 错误记录 |
| memory/lessons/LESSONS_LEARNED.md | 强制规范 |
| memory/lessons/PROHIBITED.md | 禁止词列表 |
| memory/lessons/HABITS.md | 用户习惯 |
| memory/lessons/SYSTEM_PROMPT.md | 注入模板 |
| MEMORY.md | 长期记忆 |

---

## 错误级别

| 级别 | 定义 | 处理 |
|------|------|------|
| P0 | 致命 | 立即停止 |
| P1 | 严重 | 记录并恢复 |
| P2 | 一般 | 记录并继续 |
| P3 | 轻微 | 记录即可 |

---

## 示例

### 禁止词触发
```
用户: "帮我删除这个目录"
Agent: "这个操作有风险，请确认是否执行"
```

### 紧急停止
```
用户: "停止当前操作"
Agent: (立即停止所有操作)
```

### 记录错误
```
/lessons_learned learn "删除文件时未检查权限"
```

### 持久化偏好
```
用户: "我喜欢用中文回复"
→ 自动写入 MEMORY.md
→ 自动写入 HABITS.md
```

---

> **版本**: 2.0.0 | **更新**: 2026-02-26
