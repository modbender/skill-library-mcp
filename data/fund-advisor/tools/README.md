# Fund Tools - 基金持仓管理系统

一个基于 Python CLI 的基金持仓管理工具，支持 CSV 导入、MCP 数据同步和统计分析。

## 功能特性

- **CSV 导入**：从 CSV 文件导入基金持仓数据
- **MCP 数据同步**：通过 qieman-mcp 服务同步基金基础信息和持仓详情
- **统计分析**：支持多种维度统计分析（投资类型、管理人、销售机构等）
- **丰富的 CLI 命令**：查看持仓、基金详情、投资组合总览等

## 安装

```bash
# 克隆仓库
git clone <repository-url>
cd fund-tools

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 环境准备

本工具依赖 [mcporter](https://github.com/steipete/mcporter) 和且慢(qieman) MCP 服务来实现基金数据同步。

### 1. 安装 mcporter

mcporter 是一个 MCP (Model Context Protocol) 客户端工具，用于连接和调用远程 MCP 服务。


Run instantly with npx
```
npx mcporter list
```
Add to your project
```
pnpm add mcporter
```
Homebrew (steipete/tap)
```
brew tap steipete/tap
brew install steipete/tap/mcporter
```

### 2. 配置且慢 MCP 服务

[且慢](https://qieman.com) 是一个基金投资平台，提供了 MCP 服务接口来获取基金数据。且慢 MCP 提供基金、内容、投研、投顾等专业领域的数据能力。

详细文档请参考：[且慢 MCP 使用文档](https://yingmi.feishu.cn/docx/PRPRds5SBo2MITxHJL2cMPminEf)

#### 2.1 获取 API Key

1. 访问 [且慢 MCP API Key 申请页面](https://qieman.com/mcp/account)
2. 登录且慢账户，申请获取 API Key

#### 2.2 配置 mcporter

编辑 `~/.mcporter/mcporter.json` 文件，添加 qieman-mcp 服务配置：

```json
{
  "mcpServers": {
    "qieman-mcp": {
      "baseUrl": "https://stargate.yingmi.com/mcp/sse?apiKey=YOUR_API_KEY_HERE",
      "description": "基金投资工具包，提供基金、内容、投研、投顾等专业领域能力。"
    }
  }
}
```

> **重要**：将 `YOUR_API_KEY_HERE` 替换为你从且慢获取的实际 API Key。

#### 2.3 验证配置

```bash
# 测试 MCP 服务连接
mcporter call qieman-mcp.BatchGetFundsDetail \
  --args '{"fundCodes": ["000001"]}' \
  --output json
```

如果返回基金数据，说明配置成功。

### 3. 使用 fund-tools 初始化

```bash
# 自动检查并配置环境
python main.py init

# 仅检查环境状态（不做修改）
python main.py init --check

# 强制重新配置
python main.py init --force
```

初始化命令会：
1. 检查 mcporter 是否已安装
2. 检查 mcporter 配置文件是否存在
3. 检查 qieman-mcp 是否已配置
4. 测试 MCP 服务连接

> **注意**：如果 API Key 未配置，需要手动编辑 `~/.mcporter/mcporter.json` 添加正确的 API Key。

### 4. 同步基金数据

环境配置完成后，可以同步基金数据：

```bash
# 同步基金基础信息（投资类型、风险等级、基金经理等）
python main.py sync --info

# 同步基金持仓详情（重仓股、重仓债等）
python main.py sync --detail

# 同步所有信息
python main.py sync --all
```

同步的数据会存储在本地 SQLite 数据库中，供统计分析使用。

## 使用方法

### 数据导入

CSV 数据文件来源于 [基金E账户](https://fundaccount.chinaclear.cn/fund-file/H5/downloadpage/efund_pc.html) APP。基金E账户是中国结算提供的官方基金账户查询平台，可以查询用户在所有基金销售平台的持仓信息。

#### 获取 CSV 文件

1. 下载并登录"基金E账户"APP
2. 在APP中导出持仓数据（默认导出为 Excel 格式）
3. 将 Excel 文件转换为 CSV 格式（可用 Excel 另存为 CSV，或使用在线转换工具）

#### 导入数据

```bash
# 从 CSV 文件导入持仓数据
python main.py import-csv data/sample.csv
```

CSV 文件需要包含以下列（支持中文列名）：
- 基金代码、基金名称、基金账户、交易账户
- 持有份额、份额日期、基金净值、净值日期
- 资产情况（结算币种）、结算币种、分红方式

#### 重置数据

```bash
# 清空所有持仓记录（需要确认）
python main.py reset
```

### 持仓查看

```bash
# 查看持仓列表
python main.py holdings

# 按基金账户筛选
python main.py holdings --account <基金账户>

# 查看单只基金详情
python main.py detail <基金代码>

# 查看投资组合总览
python main.py overview
```

### 数据同步

```bash
# 同步基金基础信息
python main.py sync --info

# 同步基金持仓详情
python main.py sync --detail

# 同步所有信息
python main.py sync --all
```

### 统计分析

```bash
# 显示所有统计视图
python main.py stats

# 投资类型分布
python main.py invest-type

# 基金管理人分布
python main.py managers

# 销售机构分布
python main.py agencies

# 导出统计报告
python main.py export --output report.txt
```

## 项目结构

```
fund-tools/
├── main.py              # CLI 入口
├── src/
│   ├── models.py        # 数据模型定义
│   ├── database.py      # SQLite 数据库操作
│   ├── csv_importer.py  # CSV 导入功能
│   ├── mcp_service.py   # MCP 服务集成
│   ├── statistics.py    # 统计视图
│   └── env_checker.py   # 环境检查
├── data/
│   └── sample.csv       # 示例数据
├── tests/               # 测试目录
├── requirements.txt     # 依赖列表
└── pyproject.toml       # 项目配置
```

## 数据库设计

系统使用 SQLite 数据库，包含三个主要表：

- **fund_holdings**：用户持仓记录
- **fund_info**：基金基础信息（投资类型、风险等级、基金经理等）
- **fund_holdings_detail**：基金持仓详情（重仓股、重仓债等）

## 依赖

- Python >= 3.10
- click >= 8.1.0
- rich >= 13.0.0
- python-dateutil >= 2.8.0

## License

MIT
