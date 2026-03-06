# fund-advisor 参考文档

## 项目概述

fund-advisor 是一个基金投资咨询与持仓分析工具，整合本地持仓管理功能和 qieman-mcp MCP 服务能力。

## 架构

```
fund-tools/
├── SKILL.md              # Skill定义（AgentSkills协议）
├── CLAUDE.md             # Claude Code 项目指令
├── scripts/              # Skill调用脚本
│   ├── fund-cli.py       # CLI包装脚本
│   └── query_mcp.py      # MCP直查脚本
├── references/           # 参考文档
│   ├── REFERENCE.md      # 本文档
│   ├── mcp-tools.md      # MCP工具文档
│   └── csv-format.md     # CSV格式规范
├── assets/               # 静态资源
└── tools/                # 工程代码
    ├── main.py           # CLI主程序（Click）
    ├── src/
    │   ├── models.py     # 数据模型
    │   ├── database.py   # 数据库操作
    │   ├── csv_importer.py   # CSV导入
    │   ├── mcp_service.py    # MCP服务调用
    │   ├── statistics.py     # 统计分析
    │   └── env_checker.py    # 环境检查
    ├── tests/            # 测试
    ├── data/             # 数据文件
    └── fund_portfolio.db # SQLite数据库
```

## 数据模型

### FundHolding - 用户持仓

| 字段 | 类型 | 说明 |
|------|------|------|
| fund_code | str | 基金代码 |
| fund_name | str | 基金名称 |
| fund_account | str | 基金账户 |
| trade_account | str | 交易账户 |
| holding_shares | float | 持有份额 |
| share_date | date | 份额日期 |
| nav | float | 净值 |
| nav_date | date | 净值日期 |
| asset_value | float | 资产市值 |
| fund_manager | str | 基金管理人 |
| sales_agency | str | 销售机构 |

### FundInfo - 基金信息

| 字段 | 类型 | 说明 |
|------|------|------|
| fund_code | str | 基金代码 |
| fund_name | str | 基金名称 |
| fund_invest_type | str | 投资类型 |
| risk_5_level | int | 风险等级(1-5) |
| nav | float | 单位净值 |
| nav_date | date | 净值日期 |
| net_asset | float | 基金规模(亿) |
| setup_date | date | 成立日期 |
| manager_names | str | 基金经理 |
| stock_ratio | float | 股票占比(%) |
| bond_ratio | float | 债券占比(%) |
| cash_ratio | float | 现金占比(%) |
| one_year_return | float | 近一年收益率(%) |
| setup_day_return | float | 成立来收益率(%) |

### FundHoldingsDetail - 基金持仓详情

| 字段 | 类型 | 说明 |
|------|------|------|
| fund_code | str | 基金代码 |
| report_date | date | 报告日期 |
| stock_invest_ratio | float | 股票投资比例(%) |
| bond_invest_ratio | float | 债券投资比例(%) |
| top_stocks | List[StockHolding] | 十大重仓股 |
| top_bonds | List[BondHolding] | 十大重仓债 |

### StockHolding - 股票持仓

| 字段 | 类型 | 说明 |
|------|------|------|
| stock_code | str | 股票代码 |
| stock_name | str | 股票名称 |
| holding_ratio | float | 持仓比例(%) |
| holding_amount | float | 持仓金额(亿) |

## 数据库

使用 SQLite 数据库，包含三个表：

### fund_holdings 表

存储用户持仓数据，复合主键：`(fund_account, trade_account, fund_code)`

### fund_info 表

存储基金基础信息，主键：`fund_code`

### fund_holdings_detail 表

存储基金持仓详情，主键：`fund_code`

## 环境要求

- Python 3.10+
- mcporter CLI
- qieman-mcp MCP 服务配置