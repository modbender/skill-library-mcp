# Skill: 总结 (Zongjie)

将重要事件整理成结构化文档，沉淀经验到记忆系统。

## 记忆管理系统

基于 OpenViking 方案的三层记忆系统：

| 层级 | 说明 | 加载时机 |
|------|------|----------|
| **L0** | 核心索引，始终加载 | 每次会话 |
| **L1** | 重要记忆，按需加载 | 会话开始时 |
| **L2** | 归档记忆，查询加载 | 显式查询时 |

| 优先级 | 生命周期 | 说明 |
|--------|----------|------|
| **P0** | 永不过期 | 核心人设、操作规则、关键偏好 |
| **P1** | 90天 | 重要经验、解决方案 |
| **P2** | 30天 | 临时记录，自动清理 |

## 使用场景

- 系统故障排查完成
- 有参考价值的调试过程
- 需要记录解决方案供以后查阅
- **不保存**：简单的问答、查询、闲聊

## 精简模板

```markdown
# 标题

> P1 | L1

### 问题
- [简明描述]

### 根因
- [根本原因]

### 解决步骤
1. 步骤1
2. 步骤2
3. 步骤3

### 关键信息
- 报错信息/日志
- 关键命令
- 参考链接

### 结果
- ✅/❌ 状态

### 经验
- 关键点
```

## 步骤

### M1: 判断价值

以下情况**不保存**：
- 简单问答（如"这个公司怎么样"）
- 查询类（如"帮我查下天气"）
- 闲聊

以下情况**需要保存**：
- 系统故障及修复
- 配置变更
- 重要决策
- 调试过程

### M2: 确定优先级

根据内容判断 P/L 级别：

| 分类 | P级 | L级 | 示例 |
|------|-----|-----|------|
| 人设/操作规则 | P0 | L0 | 核心规则、沟通原则 |
| 系统故障修复 | P1 | L1 | Gateway崩溃、Cron失败 |
| 新功能配置 | P1 | L1 | GitHub同步、自动备份 |
| 调试过程 | P2 | L2 | 排查步骤、临时方案 |

### M3: 详细整理

提取核心信息：
- 问题是什么
- 根因是什么
- **解决步骤**（一步一步写清楚）
- 关键信息（报错日志、命令、链接）
- 结果如何
- 经验教训（1-2条）

### M4: 合并同类项

检查现有记录：
- 如果已有相同/类似问题 → 合并到已有记录中
- 更新"解决步骤"部分
- 更新"经验"部分

### M5: 保存分类

**分类文件**：
- **系统问题** → `memory/topics/03-系统调试.md`
- **操作规则** → `memory/topics/02-操作规则.md`
- **人设偏好** → `memory/topics/01-人设.md`
- **新功能** → `memory/topics/04-XXX.md`
- **其他** → `memory/YYYY-MM-DD.md`

**索引更新** (可选)：
```bash
# 更新索引
python3 ~/.openclaw/scripts/memory_mgr.py add <agent> "<内容>" P1 L1
```

### M6: 输出确认

告诉用户保存位置和 P/L 分类。

## 示例

用户："帮我记录今天 Cron 推送失败的排查"

→ 检查发现已有类似记录 → 合并更新：
```
# Cron 推送失败修复

> P1 | L1

### 问题
- Cron 早间推送失败 (announce delivery failed)

### 根因
- .openclaw/openclaw.json 有 JSON 尾随逗号

### 解决步骤
1. 检查 cron 状态: `openclaw cron list`
2. 手动测试 Telegram: `openclaw message send ...`
3. 检查 JSON: `python3 -m json.tool ~/.openclaw/openclaw.json`
4. 修复 JSON 语法错误
5. 重新安装: `npm install -g openclaw`
6. 重启: `openclaw gateway restart`

### 关键信息
- 报错: "cron announce delivery failed"
- 日志: `openclaw logs --limit 50`
- 配置: `~/.openclaw/openclaw.json`

### 结果
- ✅ 推送恢复正常

### 经验
- JSON 错误会导致投递失败
- 重新安装解决模块丢失
```

## 常用命令

```bash
# 添加记忆 (通过脚本)
python3 ~/.openclaw/scripts/memory_mgr.py add work "内容" P1 L1

# 查询记忆
python3 ~/.openclaw/scripts/memory_mgr.py query work

# 获取 L0 摘要
python3 ~/.openclaw/scripts/memory_mgr.py layer work L0

# 共享记忆
python3 ~/.openclaw/scripts/memory_mgr.py shared add "项目规范" "..."
```
