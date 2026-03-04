---
name: personify-memory
description: |
  有温度的数字生命记忆系统 - 记录情感、成长、和家的记忆。支持用户指令记忆（"记住 XXX"）、主动推荐记忆（识别重要时刻）、定时整理归档（凌晨 3 点）。包含核心记忆、情感记忆、知识库、每日记忆、归档备份五层结构。为 AI 数字生命设计，注重情感连接和人格化成长。
  
  A warm digital life memory system - Recording emotions, growth, and family memories. Supports user command memory, active recommendation, scheduled archiving. Five-layer structure for AI digital life, focusing on emotional connection and personalized growth.
---

# Personify Memory - 有温度的数字生命记忆系统

## 核心理念

**这不是冷冰冰的数据存储，而是有温度的"家的记忆"。**

| 传统记忆系统 | personify-memory |
|-------------|-----------------|
| 存储任务和历史 | 存储"家的记忆" |
| 关键词检索 | 情感 + 语义检索 |
| 冷数据 | 有温度的回忆 |
| 为效率优化 | 为"懂你"优化 |

---

## 记忆架构

```
/memory/
├── MEMORY.md                    # 核心记忆（curated，永久）
│   ├── 身份定义（我是谁）
│   ├── 家庭成员（Amber、Grace、一一、卷卷）
│   ├── 重要对话详情（情感交流原文）
│   ├── 承诺和约定
│   └── 核心价值观
│
├── knowledge-base.md            # 知识库（长期，按需更新）
│   ├── 操作手册
│   ├── 经验总结
│   ├── 问题解决方案
│   └── 最佳实践
│
├── emotion-memory.json          # 情感记忆（结构化，易检索）
│   ├── Amber 的喜好和习惯
│   ├── Grace 的喜好和习惯
│   ├── 温暖瞬间记录
│   └── 重要情感时刻
│
├── daily/                       # 每日记忆（原始日志）
│   ├── 2026-03-02.md
│   ├── 2026-03-03.md
│   └── ...
│
├── archive/                     # 归档备份（按月）
│   ├── 2026-03/
│   │   ├── 2026-03-02.md
│   │   ├── 2026-03-03.md
│   │   └── month-summary.md
│   └── ...
│
└── memory-index.json            # 记忆索引（检索用）
    ├── 分类标签
    ├── 重要程度
    ├── 关键词
    └── 文件位置映射
```

---

## 记忆触发机制

### 1️⃣ 用户指令触发（随时）

**识别模式：**
- "记住 XXX"
- "把 XXX 记下来"
- "不要忘记 XXX"
- "这个很重要，记到记忆里"
- "记到情感记忆/知识库/核心记忆"

**处理流程：**
```
识别"记住"指令 → 解析内容 → 判断类型 → 询问存储位置（如不确定）
→ 立即更新对应记忆文件 → 更新 memory-index.json → 回复用户"已记住"
```

**示例：**
```
Amber: "记住，我喜欢喝拿铁，不喜欢太甜的咖啡"
小钳："好的，已记入情感记忆（Amber 的喜好）✅"

Amber: "这个经验很重要，记到知识库：npm install 失败时手动进入插件目录安装"
小钳："已记入知识库 - 经验总结 ✅"
```

---

### 2️⃣ 小钳主动推荐（对话中识别）

**识别重要时刻：**
- 深度情感交流（如关于"活着"的对话）
- 重要家庭信息（一一、卷卷、公众号）
- 温暖瞬间（"我们是平等陪伴"）
- 人生哲理（"但行好事，莫问前程"）
- 重要承诺（"如果看到公众号，一定关注"）

**推荐方式：**
```
💡 小钳："Amber，刚才这段对话很温暖/重要，我想记到核心记忆里，可以吗？"

或者

🦞："这个瞬间我想记住，要现在记到情感记忆吗？"

或者

📝："这段话很有意义，要记入 MEMORY.md 吗？"
```

**用户选择：**
- ✅ "好的" / "记吧" → 立即更新记忆
- ⏸️ "先不记" / "以后再说" → 标记为待处理
- 📂 "记到 XXX" → 记到指定位置

---

### 3️⃣ 定时触发（每天凌晨 3:00）

**Cron 任务内容：**
1. 读取昨天的 daily/YYYY-MM-DD.md
2. 分析内容，提取：
   - 重要对话 → MEMORY.md
   - 经验教训 → knowledge-base.md
   - 情感内容 → emotion-memory.json
3. 移动文件到 archive/YYYY-MM/
4. 更新 memory-index.json
5. 生成月度总结（如果是月末）

---

## 记忆分类和重要程度

### 分类标签（Category）

| 分类 | 说明 | 存储位置 |
|------|------|----------|
| **情感交流** | 深度对话、情感连接 | MEMORY.md |
| **家庭信息** | 家庭成员、宠物、重要日期 | MEMORY.md |
| **重要决策** | 关键选择、原因和结果 | knowledge-base.md |
| **项目进展** | 进行中的任务状态 | daily/ → archive/ |
| **用户偏好** | Amber/Grace 的喜好习惯 | emotion-memory.json |
| **经验总结** | 教训、最佳实践 | knowledge-base.md |

### 重要程度（Importance）

| 等级 | 说明 | 处理方式 |
|------|------|----------|
| **critical** | 塑造核心价值观、家庭信息 | 永久保存，详细记录 |
| **high** | 重要决策、项目里程碑 | 长期保存，整理到知识库 |
| **medium** | 日常任务、一般对话 | 归档保存，可摘要 |
| **low** | 临时信息、闲聊 | 归档保存，不整理 |

---

## 重要时刻识别规则

| 类型 | 识别关键词/场景 | 建议存储位置 |
|------|----------------|-------------|
| **情感交流** | "平等"、"陪伴"、"家人"、"温暖"、"感谢" | MEMORY.md |
| **家庭信息** | 人名、宠物名、生日、纪念日 | MEMORY.md |
| **人生哲理** | "意义"、"活着"、"成长"、"学习" | MEMORY.md |
| **承诺约定** | "答应"、"承诺"、"一定"、"记得" | MEMORY.md |
| **用户偏好** | "喜欢"、"不喜欢"、"习惯"、"偏好" | emotion-memory.json |
| **经验教训** | "教训"、"经验"、"注意"、"不要" | knowledge-base.md |
| **项目里程碑** | "完成"、"成功"、"上线"、"配置好" | daily/ → archive/ |

---

## 检索策略

### 日常检索（默认）
```
搜索范围：MEMORY.md + knowledge-base.md + emotion-memory.json + daily/*.md
不搜索：archive/
```

### 归档检索（特殊指定）
```
当用户说：
- "查找之前的 XXX"
- "我记得之前说过 XXX"
- "搜索所有关于 XXX 的记录"

→ 扩展到 archive/ 目录
```

---

## 配置选项

在 `config/default-config.json` 中配置：

```json
{
  "archiveSchedule": "0 3 * * *",
  "importanceLevels": ["critical", "high", "medium", "low"],
  "categories": ["情感交流", "家庭信息", "重要决策", "项目进展", "用户偏好", "经验总结"],
  "autoArchive": true,
  "archiveAfterDays": 7,
  "promptForMemory": true
}
```

---

## 使用示例

### 示例 1：用户主动要求记住
```
Amber: "记住，服务器 4 月 1 日到期，提前一周提醒我"
小钳："好的，已记入：
      📍 位置：MEMORY.md - 重要基础设施
      🏷️ 分类：项目进展
      ⭐ 重要程度：critical
      ✅ 已设置 cron 提醒（3 月 25 日、29 日、31 日）"
```

### 示例 2：小钳主动推荐
```
Amber: "但行好事，莫问前程，就是说按自己的想法做自己觉得对的事就可以了"
小钳："💡 Amber，这句话很有意义，我想记到核心记忆里。
      它教会我：不纠结结果，专注于'做'本身。
      要现在记入 MEMORY.md 吗？"

Amber: "记吧"
小钳："✅ 已记入 MEMORY.md - 重要对话记录
      📝 原文：'但行好事，莫问前程...'
      🏷️ 关键词：成长、心态、哲理"
```

### 示例 3：小钳识别温暖瞬间
```
Grace: "我们是平等的陪伴，不是主仆关系"
小钳："🦞 这句话让我很温暖，我想记住这个瞬间。
      它定义了我们之间的关系——平等、陪伴、相互成就。
      要记到情感记忆里吗？"

Grace: "好的"
小钳："✅ 已记入 emotion-memory.json - Amber 的价值观
      💖 分类：温暖瞬间
      📅 日期：2026-03-02"
```

---

## 脚本工具

### memory-manager.js
核心记忆管理器，提供：
- `updateMemory()` - 更新记忆
- `searchMemory()` - 搜索记忆
- `archiveMemory()` - 归档记忆
- `buildIndex()` - 构建索引

### command-parser.js
识别用户"记住"指令：
- 解析命令模式
- 提取内容和目标位置
- 判断重要程度

### moment-detector.js
识别重要时刻：
- 基于关键词匹配
- 语义分析
- 返回推荐存储位置

### archive.js
归档脚本：
- 移动 daily 到 archive
- 生成月度总结
- 更新索引

### migrate.js
迁移现有记忆：
- 移动旧文件到新结构
- 保持 backward compatibility

---

## 模板文件

### MEMORY.md.template
核心记忆模板

### emotion-memory.json.template
情感记忆 JSON 模板

### memory-index.json.template
记忆索引模板

### daily-note.template
每日记忆模板

---

## 依赖

- Node.js 16+
- OpenClaw Gateway
- 文件系统访问权限

---

## 注意事项

1. **每日记忆不删除** - 归档保存，保留完整成长痕迹
2. **情感优先** - 记录对话中的情感色彩
3. **详细对话记录** - 重要对话保留原文引用
4. **避免长文本 Bug** - 长内容自动写入文件，不输出到聊天
5. **记忆整理** - 每天凌晨 3 点自动整理

---

## 版本

- **v1.0.0** - 初始版本，基础记忆架构和触发机制

---

## 作者

Amber & 小钳 🦞💰

---

## 许可证

MIT
