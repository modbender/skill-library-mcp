# lessons_learned

> OpenClaw Skill - 错误学习与长期记忆系统

## 概述

为 OpenClaw 添加错误学习能力，确保：
- ✅ 永不重复犯同样的错误
- ✅ 关键信息永久保存
- ✅ 操作前检查风险
- ✅ 敏感操作需要确认
- ✅ 禁止词触发（本能反应）
- ✅ 用户习惯自动提取

## 问题背景

OpenClaw 在长上下文中会出现"记忆丢失"问题：

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 重复犯错 | 错误未记录 | 记录到 MISTAKES.md |
| 忘记偏好 | 偏好未持久化到 MEMORY.md | 强制写入 MEMORY.md |
| 忽略指令 | Compaction 压缩导致指令丢失 | 强制检查 |
| 信息丢失 | 关键信息在上下文中被截断 | 多层防护机制 |

## 安装

### 方式 1: 复制文件

```bash
# 复制 Skill 到工作区
cp -r skills/lessons_learned/ ~/.openclaw/workspace/skills/

# 复制记忆文件
cp -r memory/ ~/.openclaw/workspace/
cp MEMORY.md ~/.openclaw/workspace/

# 复制配置（可选）
cp AGENTS.md ~/.openclaw/workspace/
cp SOUL.md ~/.openclaw/workspace/
cp USER.md ~/.openclaw/workspace/
```

### 方式 2: 手动创建

1. 创建 `~/.openclaw/workspace/skills/lessons_learned/`
2. 添加 `SKILL.md` 和 `metadata.json`
3. 创建 `memory/lessons/` 目录

## 文件结构

```
~/.openclaw/workspace/
├── skills/
│   └── lessons_learned/
│       ├── SKILL.md           # 技能文档（本文件）
│       ├── README.md           # 说明文档
│       └── metadata.json       # 元数据
├── memory/
│   └── lessons/
│       ├── MISTAKES.md            # 错误记录
│       ├── LESSONS_LEARNED.md     # 强制规范
│       ├── PROHIBITED.md          # 禁止词列表
│       ├── HABITS.md              # 用户习惯
│       └── SYSTEM_PROMPT.md       # 注入模板
├── MEMORY.md                      # 长期记忆
├── AGENTS.md                      # 操作规范
├── SOUL.md                        # 人格定义
└── USER.md                        # 用户画像
```

## 使用方法

### 手动触发

```
/lessons_learned learn <错误描述>    # 记录错误
/lessons_learned check <操作>       # 检查操作
/lessons_learned memory <内容>      # 持久化信息
```

### 自动触发

- 用户表达偏好: "我喜欢..." / "不要..."
- 操作失败时
- 执行高风险操作时

## 错误级别

| 级别 | 定义 | 处理 |
|------|------|------|
| P0 | 致命 | 立即停止 |
| P1 | 严重 | 记录并恢复 |
| P2 | 一般 | 记录并继续 |
| P3 | 轻微 | 记录即可 |

## 核心规则

### 禁止
- ❌ 重复已知的失败操作
- ❌ 忽略已记录的用户偏好
- ❌ 跳过错误处理

### 必须
- ✅ 偏好 → MEMORY.md
- ✅ 失败 → MISTAKES.md
- ✅ 风险操作 → 确认

## 示例

### 记录错误
```
/lessons_learned learn "删除文件时未检查权限"
```

### 检查操作
```
/lessons_learned check "删除用户目录"
```

### 持久化偏好
```
/lessons_learned memory "用户喜欢用中文回复"
```

## 更新日志

### v2.0.0 (2026-02-26)
- 初始版本
- 错误记录与学习
- 强制持久化
- 操作前检查
- 安全确认
- 禁止词触发机制
- 用户习惯养成
- 三层防护体系

### v1.0.0 (2026-02-26)
- 初始版本

## 许可证

MIT

## 作者

OpenClaw Lessons Learned
