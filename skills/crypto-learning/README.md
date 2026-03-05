# Crypto Learning Skill - 加密货币自学系统

## 功能说明

这个 skill 帮助你系统学习加密货币知识，每天早上 9 点自动推送学习内容。

## 学习大纲

### 阶段 1：小白向（30天）
- 什么是加密货币
- 区块链基础
- 钱包和密钥
- 交易所基础
- 安全第一

### 阶段 2：投资向（60天）
- 技术分析基础
- 基本面分析
- DeFi基础
- 风险管理
- 市场周期

### 阶段 3：进阶投资（90天）
- 期权与合约
- 链上数据分析
- 宏观经济影响
- 税务与合规
- 投资心理学

## 使用方法

### 自动学习（推荐）

每天早上 9 点会自动推送学习内容，无需手动操作。

### 手动命令

```bash
# 查看学习进度
python3 /home/hmzo/.openclaw/workspace/skills/crypto-learning/learn.py progress

# 获取今日学习内容
python3 /home/hmzo/.openclaw/workspace/skills/crypto-learning/learn.py today

# 跳过今天
python3 /home/hmzo/.openclaw/workspace/skills/crypto-learning/learn.py skip

# 重置学习计划
python3 /home/hmzo/.openclaw/workspace/skills/crypto-learning/learn.py reset

# 预览下一个主题
python3 /home/hmzo/.openclaw/workspace/skills/crypto-learning/learn.py next
```

## 工作原理

1. **读取进度**：从 `progress.json` 读取当前学习进度
2. **获取内容**：从 `content.json` 获取对应的学习内容
3. **搜索最新资料**：使用 browser 搜索该知识点的最新详细内容
4. **整合呈现**：将基础内容和搜索结果整合后呈现
5. **更新进度**：自动更新学习进度到下一个主题

## 定时任务

已设置每天早上 9 点（新加坡时间）自动推送：
- Cron 表达式：`0 9 * * *`
- 时区：Asia/Singapore

## 文件结构

```
crypto-learning/
├── SKILL.md          # Skill 定义文件
├── README.md         # 本文件
├── content.json      # 学习大纲（所有知识点）
├── progress.json     # 学习进度跟踪
└── learn.py          # 学习脚本
```

## 注意事项

- 每次学习都会通过 browser 搜索最新内容，确保信息的时效性
- 学习进度会自动保存，即使重启也不会丢失
- 可以随时跳过某天的学习
- 可以随时重置学习计划重新开始

## 开始学习

系统已经配置好定时任务，明天早上 9 点会自动推送第一个学习内容！

如果想立即查看当前学习内容，运行：
```bash
python3 /home/hmzo/.openclaw/workspace/skills/crypto-learning/learn.py today
```
