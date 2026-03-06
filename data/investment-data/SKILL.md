---
name: investment-data
description: 获取高质量 A 股投资数据，基于 investment_data 项目。支持日终价格、涨跌停数据、指数数据等。每日更新，多数据源交叉验证。触发词：股票数据、A股数据、金融数据、量化数据、历史行情。
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["python3", "wget", "tar"] },
        "install":
          [
            {
              "id": "python-deps",
              "kind": "pip",
              "packages": ["pandas", "numpy", "requests"],
              "label": "Install Python dependencies"
            }
          ]
      }
  }
---

# A 股投资数据获取 Skill

基于 [investment_data](https://github.com/chenditc/investment_data) 项目，提供高质量 A 股投资数据。

## 🎯 核心功能

1. **数据下载** - 自动下载最新数据集
2. **数据查询** - 查询股票历史数据
3. **数据更新** - 每日自动更新
4. **多格式支持** - Qlib、CSV、JSON

## 📊 数据类型

- **日终价格** - 开高低收、成交量、成交额
- **涨跌停数据** - 涨跌停价格、涨跌停状态
- **指数数据** - 主要指数价格和权重
- **复权数据** - 前复权、后复权价格

## 🚀 快速开始

### 1. 下载最新数据

```bash
python scripts/download_data.py --latest
```

### 2. 查询股票数据

```python
from scripts.data_client import InvestmentData

# 初始化客户端
client = InvestmentData()

# 查询单只股票
df = client.get_stock_data("000001.SZ", start_date="2024-01-01", end_date="2024-12-31")

# 查询指数成分
weights = client.get_index_weights("000300.SH")

# 查询涨跌停
limits = client.get_limit_data("000001.SZ", date="2024-12-01")
```

### 3. 批量查询

```bash
python scripts/query_batch.py --stocks "000001.SZ,000002.SZ" --start 2024-01-01 --end 2024-12-31 --output csv
```

## 📖 详细文档

- [数据字段说明](references/fields.md)
- [API 参考](references/api.md)
- [使用示例](examples/)
- [常见问题](docs/faq.md)

## 🔧 配置

### 环境变量

```bash
# 数据存储路径（可选）
export INVESTMENT_DATA_DIR=~/.qlib/qlib_data/cn_data

# Tushare Token（可选，用于实时更新）
export TUSHARE_TOKEN=your_token_here
```

### 配置文件

编辑 `config/config.yaml`：

```yaml
data:
  # 数据存储路径
  data_dir: ~/.qlib/qlib_data/cn_data
  
  # 自动更新
  auto_update: true
  update_time: "09:00"
  
  # 数据源优先级
  sources:
    - final
    - ts
    - ak
    - yahoo

query:
  # 默认输出格式
  output_format: csv
  
  # 日期格式
  date_format: "%Y-%m-%d"
```

## 📝 使用示例

### Python API

```python
from scripts.data_client import InvestmentData

client = InvestmentData()

# 查询股票日 K 线
df = client.get_stock_daily("000001.SZ", "2024-01-01", "2024-12-31")
print(df.head())

# 查询指数数据
index_df = client.get_index_daily("000300.SH", "2024-01-01", "2024-12-31")

# 查询股票列表
stocks = client.get_stock_list(date="2024-12-31")

# 查询退市股票
delisted = client.get_delisted_stocks()
```

### 命令行

```bash
# 查询单只股票
python scripts/query.py --stock 000001.SZ --start 2024-01-01 --end 2024-12-31

# 批量查询
python scripts/query_batch.py --file stocks.txt --start 2024-01-01 --output json

# 更新数据
python scripts/update_data.py --daily

# 导出数据
python scripts/export.py --stock 000001.SZ --format excel
```

## 🔄 自动化

### 定时更新

使用 OpenClaw cron 自动更新：

```yaml
# 每天早上 9:00 更新数据
schedule:
  cron: "0 9 * * *"
  task: "python scripts/update_data.py --daily"
```

### 批量处理

```bash
# 批量导出多只股票
python scripts/batch_export.py --stocks stocks.txt --output ./data/
```

## ⚠️ 注意事项

1. **数据延迟**：每日更新，T+1 数据
2. **存储空间**：需要约 5GB 存储空间
3. **网络要求**：需要访问 GitHub 和 DoltHub
4. **Tushare Token**：实时更新需要 token

## 📊 数据质量

- ✅ **多源验证**：交叉验证多个数据源
- ✅ **完整性好**：包含退市公司数据
- ✅ **修正错误**：自动修正数据异常
- ✅ **每日更新**：自动化 CI/CD 流程

## 📚 相关资源

- **GitHub**：https://github.com/chenditc/investment_data
- **DoltHub**：https://www.dolthub.com/repositories/chenditc/investment_data
- **原始文档**：https://github.com/chenditc/investment_data/blob/master/docs/README-ch.md

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

## 📄 许可证

Apache 2.0
