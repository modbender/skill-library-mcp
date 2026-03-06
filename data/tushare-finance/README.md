# Tushare Finance Skill

[![Version](https://img.shields.io/badge/version-2.0.6-blue.svg)](https://github.com/StanleyChanH/Tushare-Finance-Skill-for-Claude-Code)
[![License](https://img.shields.io/badge/license-Apache--2.0-green.svg)](LICENSE)
[![ClawHub](https://img.shields.io/badge/ClawHub-Available-purple.svg)](https://clawhub.com)

获取中国金融市场数据的 OpenClaw Skill，支持 **220+ 个 Tushare Pro 接口**。

## ✨ 特性

- 🚀 **开箱即用** - 一键安装，无需复杂配置
- 📊 **全面覆盖** - A股、港股、美股、基金、期货、债券
- 🔧 **多种方式** - Python API、命令行工具、批量导出
- 📈 **实时数据** - 支持股票行情、财务报表、宏观经济
- 🔄 **OpenClaw 集成** - 无缝集成到自动化工作流
- 📖 **完整文档** - 220+ 接口完整索引和使用示例

## 📥 安装

### 方法 1：通过 ClawHub（推荐）

```bash
clawhub install tushare-finance
```

### 方法 2：手动安装

```bash
git clone https://github.com/StanleyChanH/Tushare-Finance-Skill-for-Claude-Code.git
cd Tushare-Finance-Skill-for-Claude-Code
pip install -r requirements.txt
```

## 🔑 配置

### 获取 Tushare Token

1. 访问 [Tushare Pro](https://tushare.pro) 注册账号
2. 在个人中心获取 Token
3. 配置环境变量：

```bash
export TUSHARE_TOKEN="your_token_here"

# 或添加到 ~/.bashrc
echo 'export TUSHARE_TOKEN="your_token_here"' >> ~/.bashrc
source ~/.bashrc
```

## 🚀 快速开始

### Python API

```python
from scripts.api_client import TushareAPI

# 初始化客户端
api = TushareAPI()

# 查询股票日线行情
df = api.get_stock_daily("000001.SZ", "2024-01-01", "2024-12-31")
print(df.head())

# 查询公司基本信息
info = api.get_stock_info("000001.SZ")
print(info)

# 批量查询多只股票
stocks = ["000001.SZ", "000002.SZ", "600000.SH"]
data = api.batch_query(stocks, "2024-01-01", "2024-12-31")
```

### 命令行工具

```bash
# 查询单只股票
python scripts/quick_query.py --stock 000001.SZ --start 2024-01-01 --end 2024-12-31

# 批量查询
python scripts/quick_query.py --file stocks.txt --start 2024-01-01 --output result.csv

# 导出 Excel
python scripts/batch_export.py --stock 000001.SZ --start 2024-01-01 --end 2024-12-31 --format excel
```

## 📊 支持的数据类型

### 股票数据（39 个接口）

| 接口 | 说明 | 示例 |
|------|------|------|
| `daily` | 日线行情 | `api.get_stock_daily()` |
| `stock_basic` | 股票列表 | `api.get_stock_list()` |
| `fina_indicator` | 财务指标 | `api.get_financial_indicator()` |
| `income` | 利润表 | `api.get_income_statement()` |
| `balancesheet` | 资产负债表 | `api.get_balance_sheet()` |

### 指数数据（18 个接口）

| 接口 | 说明 | 示例 |
|------|------|------|
| `index_daily` | 指数日线 | `api.get_index_daily()` |
| `index_weight` | 指数成分 | `api.get_index_weight()` |
| `index_basic` | 指数列表 | `api.get_index_list()` |

### 基金数据（11 个接口）

| 接口 | 说明 | 示例 |
|------|------|------|
| `fund_nav` | 基金净值 | `api.get_fund_nav()` |
| `fund_basic` | 基金列表 | `api.get_fund_list()` |

### 期货数据（16 个接口）

| 接口 | 说明 | 示例 |
|------|------|------|
| `futures_daily` | 期货日线 | `api.get_futures_daily()` |

### 宏观数据（10 个接口）

| 接口 | 说明 | 示例 |
|------|------|------|
| `gdp` | GDP数据 | `api.get_gdp()` |
| `cpi` | CPI数据 | `api.get_cpi()` |
| `pmi` | PMI数据 | `api.get_pmi()` |

### 港股美股（23 个接口）

| 接口 | 说明 | 示例 |
|------|------|------|
| `hk_daily` | 港股日线 | `api.get_hk_daily()` |
| `us_daily` | 美股日线 | `api.get_us_daily()` |

**完整接口列表**：查看 [接口文档索引](reference/README.md)

## 📖 API 文档

### TushareAPI 类

#### `__init__(token=None)`

初始化 API 客户端

**参数**：
- `token` (str, optional): Tushare Token，默认从环境变量读取

#### `get_stock_daily(ts_code, start_date, end_date)`

查询股票日线行情

**参数**：
- `ts_code` (str): 股票代码（如 "000001.SZ"）
- `start_date` (str): 开始日期（如 "2024-01-01"）
- `end_date` (str): 结束日期（如 "2024-12-31"）

**返回**：
- `pd.DataFrame`: 日线数据

**示例**：
```python
df = api.get_stock_daily("000001.SZ", "2024-01-01", "2024-12-31")
```

#### `batch_query(ts_codes, start_date, end_date)`

批量查询多只股票

**参数**：
- `ts_codes` (list): 股票代码列表
- `start_date` (str): 开始日期
- `end_date` (str): 结束日期

**返回**：
- `dict`: {股票代码: DataFrame}

**示例**：
```python
stocks = ["000001.SZ", "000002.SZ", "600000.SH"]
data = api.batch_query(stocks, "2024-01-01", "2024-12-31")
```

**更多 API 请参考**：[docs/api_reference.md](docs/api_reference.md)

## 🔧 使用示例

### 示例 1：股票数据分析

```python
from scripts.api_client import TushareAPI

api = TushareAPI()

# 查询股票数据
df = api.get_stock_daily("000001.SZ", "2024-01-01", "2024-12-31")

# 计算收益率
df['return'] = df['close'].pct_change()
df['cum_return'] = (1 + df['return']).cumprod()

print(df[['trade_date', 'close', 'return', 'cum_return']].tail())
```

### 示例 2：批量导出

```python
from scripts.api_client import TushareAPI

api = TushareAPI()

# 批量查询沪深300成分
stocks = api.get_index_weight("000300.SH", "2024-12-31")
stock_codes = stocks['con_code'].tolist()

# 批量获取数据
for code in stock_codes[:10]:  # 前10只
    df = api.get_stock_daily(code, "2024-01-01", "2024-12-31")
    df.to_csv(f"./data/{code}.csv", index=False)
```

### 示例 3：财务分析

```python
# 查询财务指标
fina = api.get_financial_indicator("000001.SZ", "2024-01-01", "2024-12-31")

# 筛选关键指标
key_metrics = ['roe', 'roa', 'debt_to_assets', 'current_ratio']
print(fina[['ts_code', 'end_date'] + key_metrics].head())
```

**更多示例**：[docs/examples.md](docs/examples.md)

## ⚙️ 配置选项

### 环境变量

```bash
# Tushare Token（必需）
export TUSHARE_TOKEN="your_token_here"

# 数据缓存（可选）
export TUSHARE_CACHE_DIR="~/.tushare_cache"

# 日志级别（可选）
export TUSHARE_LOG_LEVEL="INFO"
```

### 配置文件

编辑 `config/config.yaml`：

```yaml
api:
  # Token（优先级低于环境变量）
  token: "your_token_here"

  # 请求超时（秒）
  timeout: 30

  # 重试次数
  retry: 3

cache:
  # 是否启用缓存
  enabled: true

  # 缓存目录
  dir: ~/.tushare_cache

  # 缓存有效期（秒）
  ttl: 3600

logging:
  # 日志级别
  level: INFO

  # 日志文件
  file: logs/tushare.log
```

## 🧪 测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_api.py

# 查看测试覆盖率
python -m pytest --cov=scripts tests/
```

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

### 开发环境

```bash
git clone https://github.com/StanleyChanH/Tushare-Finance-Skill-for-Claude-Code.git
cd Tushare-Finance-Skill-for-Claude-Code
pip install -r requirements.txt
pip install -r requirements-dev.txt
python -m pytest tests/
```

## 📄 许可证

Apache License 2.0

## 🙏 致谢

- [Tushare Pro](https://tushare.pro) - 提供高质量金融数据 API
- [OpenClaw](https://github.com/openclaw/openclaw) - OpenClaw 框架

## 📚 相关资源

- **GitHub**：https://github.com/StanleyChanH/Tushare-Finance-Skill-for-Claude-Code
- **ClawHub**：https://clawhub.com/skill/tushare-finance
- **Tushare 文档**：https://tushare.pro/document/2
- **OpenClaw 文档**：https://docs.openclaw.ai

## 📊 更新日志

### v2.0.0 (2026-02-14)
- ✨ 添加完整的 Python API 客户端
- ✨ 添加命令行工具
- ✨ 添加批量导出功能
- 📖 完善 API 文档和使用示例
- 🧪 添加自动化测试
- 🔄 配置 GitHub Actions 自动发布

### v1.0.0 (2026-01-10)
- 🎉 初始版本发布
- 📊 支持 220+ Tushare Pro 接口
