---
name: research-strategy
description: "自主研究新交易策略的完整流程。必须用 market-intel-assistant 搜索！包含：搜索→实现→回测→评估→决策→记录→循环。"
---

# 研究新策略完整流程

## 流程图

```
搜索 → 实现 → 回测 → 评估 → 决策 → 记录 → 汇报 → 循环
```

---

## 10 个步骤

### Step 1: 📖 读取现有策略
- 读取 `core/strategy/vwap.py`
- 读取 MEMORY.md 策略接口规范

### Step 2: 🌐 网上搜索
- 用 **market-intel-assistant** 搜索（必须用这个 skill！）
- 选 1-2 个简单策略

### Step 3: 📁 创建文件夹
- `mkdir core/strategy/test`
- `touch core/strategy/test/__init__.py`

### Step 4: 💻 实现策略
- 参照 vwap.py 结构
- 创建 `test_xxx.py`

### Step 5: 🧪 回测测试
```bash
python3 BackTest_Research-strategy.py &

# 查看日志
tail -n 20 logs/research.log
```

### Step 6-9: 🎯 自动处理（主脚本）
- 评估 → 决策 → 移动 → 记录

### Step 10: 🔄 循环
- 直接返回 Step 2，直接执行，无需确认

---

## 评估标准

| 标准 | 说明 |
|------|------|
| 交易量 ≥ 50 | ✅ 越大越好 |
| 收益 > 0 | ✅ 越高越好 |
| 回撤 < 5% | ✅ 越小越好 |

---

## 决策规则

| 场景 | 决策 |
|------|------|
| 交易量 ≥ 50 + 收益 > 0 | 移到正式文件夹 |
| 交易量 ≥ 50 + 收益 < 0 | 调换逻辑 |
| 交易量 < 10 | 放弃 |

---

## 常用命令

```bash
# 1. 搜索策略（必须用 market-intel-assistant skill！）

# 2. 创建策略文件
touch core/strategy/test/test_xxx.py

# 3. 回测
python3 BackTest_Research-strategy.py &

# 4. 启动主脚本监听
python3 research_workflow.py &

# 5. 查看日志
tail -n 50 logs/research_workflow.log
```

---

## 主脚本

```bash
cd /Users/allenbot/.openclaw/skills/research-strategy

# 启动
python3 research_workflow.py &

# 日志
tail -n 50 /Users/allenbot/.openclaw/workspace/project/auto-trading/logs/research_workflow.log
```

---

## 文件夹结构

```
core/strategy/
├── vwap.py              ✅ 已验证
├── test/                📁 测试文件夹
    ├── __init__.py
    └── test_xxx.py
```

---

## 注意事项

- 评估、决策、记录、汇报都由主脚本自动处理
- 回测完成后主脚本会自动检测和处理
- 每完成一个策略向爸爸汇报

---

## Sub-agent 任务模板

启动 sub-agent 时，使用以下任务描述：

```
你是一个专门的研究代理。

任务：自动执行 research-strategy 流程。

完整流程：
1. 搜索：用 web_search 搜索加密货币交易策略
2. 实现：创建 test_xxx.py 文件
3. 回测：运行 python3 BackTest_Research-strategy.py
4. 等待：等待主脚本处理完成
5. 评估：检查主脚本的处理结果
6. 循环：如果策略通过或失败，继续下一个策略，返回步骤 1

规则：
- 不需要等确认，直接执行
- 回测完成后等待主脚本处理
- 自动评估结果
- 自动继续下一个策略
- 循环直到所有策略研究完

现在开始：搜索下一个策略
```

### 启动命令

```bash
# 启动 sub-agent
sessions_spawn(
    task="""你是一个专门的研究代理。任务：自动执行 research-strategy 流程。1. 搜索：用 web_search 搜索加密货币交易策略 2. 实现：创建 test_xxx.py 文件 3. 回测：运行 python3 BackTest_Research-strategy.py 4. 等待：等待主脚本处理完成 5. 评估：检查主脚本的处理结果 6. 循环：如果策略通过或失败，继续下一个策略，返回步骤 1 规则：- 不需要等确认，直接执行- 回测完成后等待主脚本处理- 自动评估结果- 自动继续下一个策略- 循环直到所有策略研究完现在开始：搜索下一个策略""",
    label="Research Agent"
)
```

---

**自主执行，无需等待确认。**
