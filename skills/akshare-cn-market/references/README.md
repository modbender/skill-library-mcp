# AKShare 参考资料

- 官方文档: https://akshare.akfamily.xyz/
- GitHub: https://github.com/akfamily/akshare
- 数据来源: 东方财富、新浪财经、同花顺、国家统计局等公开数据源

## 已验证接口（akshare v1.18.x）

| 接口 | 说明 | 数据源 |
|------|------|--------|
| `stock_zh_a_hist` | A股个股历史K线 | 东方财富 |
| `stock_zh_index_daily` | 大盘指数K线 | 新浪财经 |
| `stock_financial_abstract_ths` | 个股财务摘要 | 同花顺 |
| `macro_china_gdp` | GDP季度数据 | 国家统计局 |
| `macro_china_cpi` | CPI月度数据 | 国家统计局 |
| `macro_china_pmi` | PMI月度数据 | 统计局/财新 |
| `macro_china_money_supply` | M0/M1/M2货币供应 | 央行 |
| `bond_zh_us_rate` | 中美国债收益率 | 东方财富 |

## 注意

- `stock_zh_a_spot_em`（全市场实时行情）依赖东方财富推送服务器，在部分网络环境（如带代理的 sandbox）下可能超时
- 宏观数据和新浪源指数在大多数网络环境下均可正常访问
