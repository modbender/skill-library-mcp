# 资金日报处理器

自动化处理资金日报邮件和数据提取的工具集。从邮箱收取资金日报邮件，下载XLSX附件，提取关键财务数据（昨日结余、本日结余、资金流入合计、资金流出合计），并保存为CSV格式。支持单次处理、批量历史数据处理和可视化图表生成。

## ✨ 更新记录

### v2.0 - 增强版 (2026-02-21)
- 🆕 **完全自动化处理** - `automated_fund_report_processor_enhanced.py`
- 🔄 **自动去重合并** - 智能处理重复数据
- 📧 **批量邮件下载** - `download_all_fund_reports.py`
- 📊 **批量数据处理** - `batch_process_fund_reports.py`
- 📈 **完整历史数据支持** - 支持处理23天历史数据
- 🎯 **智能数据清理** - 自动去重和数据验证

### v3.1 - 精简架构版 (2026-02-23)
- 🧹 **代码精简** - 移除冗余脚本，优化架构
- 📊 **图表展示优化** - 使用内置工具直接展示图表
- 🔄 **统一凭据管理** - 仅保留完全自动化版本
- ⚡ **性能提升** - 减少依赖，提高执行效率

## 🛠️ 使用方法

### 🚀 快速开始 (推荐 - 零交互)
```bash
# 一键运行 - 完全自动化，无需任何用户输入
python3 zero_interaction_runner.py
```
**说明**: 自动从 Bitwarden 获取凭据，下载最新资金日报，提取数据，无需任何手动操作。

### 🔐 Bitwarden 自动化
```bash
# 仅加载凭据到环境变量
python3 fully_automated_bitwarden.py

# 然后运行任何需要凭据的脚本
python3 automated_fund_report_processor_enhanced.py
```

### ⚙️ 传统方式 (手动配置)
```bash
# 设置环境变量
export FUND_EMAIL="your_email@example.com"
export FUND_PASSWORD="your_password"

# 完全自动化处理
python3 automated_fund_report_processor_enhanced.py
```

## 📋 核心功能

### 1. 数据处理流水线
```bash
# 数据提取
python3 extract_enhanced_data.py input.xlsx

# 格式生成
python3 generate_user_format.py data.csv

# 图表生成
python3 plot_daily_balance.py fund_key_data_clean_history.csv
```

### 2. 批量历史数据
```bash
# 下载所有历史邮件
python3 download_all_fund_reports.py

# 批量处理文件
python3 batch_process_fund_reports.py fund_attachments/

# 生成趋势图表
python3 plot_daily_balance.py fund_key_data_clean_history.csv
```

### 3. 完全自动化流程
```bash
# 完全自动化凭据管理
python3 fully_automated_bitwarden.py

# 一键运行器 (推荐)
python3 zero_interaction_runner.py
```

## 📊 输出文件

- `fund_key_data_latest.csv` - 最新单日数据
- `fund_key_data_clean_history.csv` - 完整历史数据（去重）
- `daily_balance_chart.png` - 资金趋势图表

## 🔧 配置

### Bitwarden 凭据管理 (推荐)
系统会自动从 Bitwarden 获取凭据，无需手动配置。详见 `ZERO_INTERACTION_GUIDE.md`。

### 手动环境变量 (备选)
```bash
export FUND_EMAIL="your_email@example.com"
export FUND_PASSWORD="your_password"
```
- `IMAP_PORT`: IMAP端口

### 依赖安装
```bash
pip3 install -r requirements.txt
pip3 install matplotlib  # 用于图表生成
```

## 📈 数据字段

- `date`: 报告日期 (YYYY.MM.DD)
- `yesterday_balance`: 昨日结余
- `today_balance`: 本日结余
- `total_inflow`: 资金流入合计
- `total_outflow`: 资金流出合计

## 🎯 技能集成

此项目已集成为OpenClaw技能，可通过自然语言调用：
- "处理最新的资金日报"
- "生成资金趋势图表" 
- "分析近期资金流动"

## 🔒 数据安全

- 敏感财务数据已配置在.gitignore中
- 仅代码和示例文件提交到版本控制
- 支持私有仓库部署

## 📄 许可证

私有项目 - 仅限内部使用