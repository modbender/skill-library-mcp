---
name: tushare
description: tushare是一个财经数据接口包，拥有丰富的数据内容，如股票、基金、期货、数字货币等行情数据，公司财务、基金经理等基本面数据。该模块通过标准化API方式统一了数据资产的对外服务方式，以帮助有需要的技术用户更实时、简洁、轻量的使用相关数据。
---

# Tushare

## 概述

tushare是一个财经数据接口包，拥有丰富的数据内容，如股票、基金、期货、数字货币等行情数据，公司财务、基金经理等基本面数据。该模块通过标准化API方式统一了数据资产的对外服务方式，以帮助有需要的技术用户更实时、简洁、轻量的使用相关数据。

## 快速上手
- Tushare官网注册，获取token，并配置环境变量。 [注册地址](https://tushare.pro/register)
- 初始化python运行换环境，并安装tushare依赖包。*pip install tushare*
- 查询Tushare接口文档，[接口文档](https://tushare.pro/document/2)
- 获取数据， python代码示例-查询正常上市交易的股票列表
```python
import tushare as ts

# 设置token
ts.set_token('<your_token>')

# 初始化pro接口实例
pro = ts.pro_api()


# 查询数据接口（*股票列表*），获取上市交易的股票列表
data = pro.stock_basic(list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
print(df)
```

## 示例脚本

- [股票数据获取示例](scripts/stock_data_example.py)
- [基金数据获取示例](scripts/fund_data_example.py)


## 安装和使用文档

- [安装tushare](references/安装tushare.md)， 在线文档：https://tushare.pro/document/1?doc_id=29
- [使用tushare](references/使用tushare.md)， 在线文档：https://tushare.pro/document/1?doc_id=7

## 数据接口文档
- [完整接口文档](references/目录索引.md)
- [在线接口地址](https://tushare.pro/document/2)

### 接口文档统计

| 接口分类 | 接口数量 |
| ---- | ---- |
| ETF专题 | 7 |
| 债券专题 | 15 |
| 公募基金 | 8 |
| 另类数据 | 2 |
| 外汇数据 | 2 |
| 宏观经济 | 22 |
| 指数专题 | 16 |
| 期权数据 | 3 |
| 期货数据 | 14 |
| 港股数据 | 11 |
| 现货数据 | 2 |
| 美股数据 | 9 |
| 股票数据 | 107 |
| 财富管理 | 2 |
| 大模型语料专题数据 | 5 |
| **总计** | **225** |

- 
