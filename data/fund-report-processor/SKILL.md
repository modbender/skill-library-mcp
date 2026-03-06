---
name: fund-report-processor
description: 自动化处理资金日报邮件和数据提取。从邮箱收取资金日报邮件，下载XLSX附件，提取关键财务数据，生成用户指定格式总结并展示趋势图表。🚀v3.1：精简架构版本，Bitwarden集成，完全自动化。⭐标准流程：zero_interaction_runner.py 一键完成所有操作
---

# 资金日报处理器技能 v3.1 - 精简架构版

## 🎯 功能概述

这个技能提供完整的资金日报自动化处理流程，现已实现：
- 🔐 **零交互操作** - 完全自动化凭据管理
- 🚀 **一键运行** - 单个命令完成所有操作  
- 🛡️ **安全集成** - Bitwarden 密码管理
- ⚡ **智能缓存** - 会话复用，提升效率
- 🧹 **精简架构** - v3.1版本清理冗余脚本，专注核心功能

## 🛠️ 核心功能

1. **🚀 零交互处理** (`zero_interaction_runner.py`): 一键完成所有操作
2. **🔐 智能凭据管理** (`fully_automated_bitwarden.py`): 自动从 Bitwarden 获取凭据
3. **📧 邮件收取** (`automated_fund_report_processor_enhanced.py`): 自动连接邮箱下载附件
4. **📊 数据提取** (`extract_enhanced_data.py`): 从XLSX提取50+字段财务数据
5. **📋 总结生成** (`generate_user_format.py`): 严格按用户格式生成报告
6. **📈 图表展示** (`plot_daily_balance.py`): 生成每日结余趋势图表
7. **📦 批量处理** (`batch_process_fund_reports.py`): 支持历史数据批量处理

## 🎯 使用场景

- **🤖 完全自动化**: 定时任务无人值守处理资金日报
- **⚡ 即时处理**: 一键获取最新资金日报分析
- **📊 历史分析**: 批量初始化和分析历史数据
- **📈 趋势监控**: 自动生成和发送资金趋势图表
- **🔒 安全管理**: 集中化凭据管理，避免硬编码密码

## 关键数据字段

- **昨日结余**: 前一日的资金余额
- **本日结余**: 当日的资金余额  
- **资金流入合计**: 当日总资金流入金额
- **资金流出合计**: 当日总资金流出金额
- **投资理财**: 理财账户金额和占比
- **USDT资产**: 泰达币数字货币资产
- **交易明细**: 前5大交易对手方和金额

## 配置要求

### 邮箱配置
需要在脚本中配置以下邮箱参数：
- `EMAIL`: 邮箱地址 (例如: your_email@example.com)
## 🚀 快速开始

### 零交互模式 (推荐)
```bash
# 一键运行 - 完全自动化，无需任何用户输入
python3 zero_interaction_runner.py
```

### Bitwarden 凭据管理
```bash
# 仅加载凭据到环境变量
python3 fully_automated_bitwarden.py

# 然后运行主处理脚本
python3 automated_fund_report_processor_enhanced.py
```

### 传统模式 (手动配置)
```bash
# 设置环境变量
export FUND_EMAIL="your_email@example.com"
export FUND_PASSWORD="your_password"

# 运行主处理脚本
python3 automated_fund_report_processor_enhanced.py
```

## ⚙️ 配置方式

### 🔐 Bitwarden 自动化 (推荐)
系统会自动从 Bitwarden 获取凭据，无需手动配置：
- 自动解锁 Bitwarden vault
- 智能会话管理和缓存
- 跨会话持久化凭据
- 详见 `ZERO_INTERACTION_GUIDE.md`

### 📧 手动环境变量 (备选)
```bash
export FUND_EMAIL="your_email@example.com"
export FUND_PASSWORD="your_password" 
export IMAP_SERVER="imap.exmail.qq.com"  # 可选
export IMAP_PORT="993"  # 可选
```

## 📋 脚本架构 - v3.1精简版

### 🚀 **一键运行器 (1个)**

#### `zero_interaction_runner.py` ⭐推荐入口⭐
- **功能**: 零交互完全自动化运行器
- **特点**: 自动凭据管理 + 完整处理流程 + 图表展示
- **输出**: 完整的资金日报分析和图表

### 🔐 **Bitwarden 集成 (1个)**

#### `fully_automated_bitwarden.py` ⭐核心组件⭐
- **功能**: 完全自动化 Bitwarden 凭据管理器
- **特点**: 
  - 使用永久记忆中的主密码自动解锁
  - 智能会话文件管理
  - 零用户交互凭据获取
- **输出**: 自动设置环境变量 `FUND_EMAIL`、`FUND_PASSWORD`

### 📧 **数据处理流水线 (4个)**

#### `automated_fund_report_processor_enhanced.py` ⭐主处理器⭐
- **功能**: 增强版自动化处理器，集成 Bitwarden 支持
- **特点**: 
  - 自动尝试从 Bitwarden 加载凭据
  - 完整邮件处理和数据提取流程
  - 自动去重和历史数据合并

#### `extract_enhanced_data.py` ⭐深度分析⭐
- **功能**: 增强数据提取器 - 从4字段扩展到50+字段
- **特点**:
  - 提取13个银行账户详细信息
  - 分析交易明细和对手方
  - 收支分类统计和外币资产监控
  - 投资理财占比分析
- **输出**: `fund_enhanced_data.json` - 结构化JSON数据

#### `generate_user_format.py` ⭐总结生成器⭐
- **功能**: 按用户指定格式生成资金日报总结
- **特点**:
  - emoji标记的重要交易明细
  - 核心财务指标、理财占比、USDT资产
  - 收入构成分析和趋势总结
- **输出**: 格式化总结报告

#### `plot_daily_balance.py`
- **功能**: 生成每日结余趋势图表
- **输出**: `daily_balance_chart.png` - 高质量PNG图表

### 🔄 **批量处理工具 (2个)**

#### `download_all_fund_reports.py`
- **功能**: 批量下载历史资金日报邮件
- **输出**: XLSX文件保存到 `fund_attachments/` 文件夹

#### `batch_process_fund_reports.py`  
- **功能**: 批量处理XLSX文件
- **输出**: 历史数据保存到 `fund_key_data_history.csv`

### 🛠️ **部署工具 (1个)**

#### `install.sh`
- **功能**: 自动安装所有Python依赖
- **用途**: 首次部署时运行

## 数据文件结构

### 📁 核心数据文件位置
技能工作目录：`/opt/homebrew/lib/node_modules/openclaw/skills/fund-report-processor/`

#### 📊 CSV数据文件
- `fund_key_data_latest.csv` - **最新单日数据**（每次运行时更新）
- `fund_key_data_clean_history.csv` - **完整历史数据**（自动去重，推荐使用）
- `fund_key_data_history.csv` - **原始历史数据**（未去重，批量处理生成）

#### 🚀 增强数据文件
- `fund_enhanced_data.json` - **增强分析数据**(50+字段，JSON格式)

#### 📈 图表文件
- `daily_balance_chart.png` - **资金趋势图表**（基于历史数据生成）

#### 📁 附件文件夹
- `fund_attachments/` - **XLSX附件存储目录**
  - 包含所有下载的资金日报Excel文件
  - 文件名格式：`资金日报-YYYY.MM.DD_时间戳.xlsx`

### 🔍 快速定位数据
新会话中可以直接访问：
```bash
# 查看最新数据
cat /opt/homebrew/lib/node_modules/openclaw/skills/fund-report-processor/fund_key_data_latest.csv

# 查看完整历史数据
cat /opt/homebrew/lib/node_modules/openclaw/skills/fund-report-processor/fund_key_data_clean_history.csv

# 查看增强分析数据
cat /opt/homebrew/lib/node_modules/openclaw/skills/fund-report-processor/fund_enhanced_data.json
```

## 📊 输出文件

- `fund_key_data_latest.csv` - 最新单日数据
- `fund_key_data_clean_history.csv` - 完整历史数据（去重）
- `fund_enhanced_data.json` - 增强分析数据（50+字段）
- `daily_balance_chart.png` - 资金趋势图表
- `fund_attachments/` - XLSX附件存储目录

## 📋 依赖库

- `pandas`: 数据处理和CSV操作
- `openpyxl`: Excel文件读取
- `matplotlib`: 图表生成
- `imaplib`: 邮件协议支持

## 🔗 相关文档

- `README.md` - 项目说明和快速开始
- `ZERO_INTERACTION_GUIDE.md` - 完全自动化使用指南
- `CLEANUP_LOG.md` - v3.0版本清理记录

## 📝 关键数据字段

- **昨日结余**: 前一日资金余额
- **本日结余**: 当日资金余额  
- **资金流入合计**: 当日总流入金额
- **资金流出合计**: 当日总流出金额
- **投资理财**: 理财账户金额和占比
- **USDT资产**: 数字货币资产
- **交易明细**: 重要交易对手方和金额

---

**🚀 资金日报处理器 v3.1 - 精简架构版，让财务分析变得轻松简单！**
