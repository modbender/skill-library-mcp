---
name: a-stock-info
description: "基于qgdata API的A股分钟级数据查询服务。提供实时股价、分钟K线、分时数据等专业数据。"
metadata:
  openclaw:
    requires:
      bins: ["python3"]
      env: ["QGDATA_TOKEN"]
---

# A股资讯数据查询 Pro

基于qgdata API的专业A股分钟级数据查询服务，提供实时股价、分钟K线、分时数据等全方位A股市场数据。

## 核心功能

- 📊 **分钟级K线**: 1分钟、5分钟、15分钟、30分钟、60分钟K线数据
- 💰 **实时股价**: 最新成交价格和成交量
- 📈 **分时数据**: 逐笔成交明细和分时走势
- 🏢 **基本面数据**: 公司信息、财务指标
- 📅 **交易日历**: 交易日判断和节假日信息

## 配置要求

### API Key配置
```bash
# 环境变量
export QGDATA_TOKEN="Kj9mN2xP5qR8vL3tY7wZ1aB4cD6eF8gH9nX4pL2qR7sT5vY8wZ1aB3cD6eF0gH2i"

# 或.env文件
echo "QGDATA_TOKEN=Kj9mN2xP5qR8vL3tY7wZ1aB4cD6eF8gH9nX4pL2qR7sT5vY8wZ1aB3cD6eF0gH2i" >> ~/.openclaw/.env
```

### 依赖安装
```bash
pip install qgdata pandas
```

## 使用方法

### 分钟K线查询
```bash
# 5分钟K线数据
python3 {baseDir}/scripts/astock_query.py --symbol 000001.SZ --freq 5min --start-date 20260227 --limit 100

# 1分钟K线数据
python3 {baseDir}/scripts/astock_query.py --symbol 000002.SZ --freq 1min --start-date 20260227 --limit 50

# 60分钟K线数据
python3 {baseDir}/scripts/astock_query.py --symbol 600000.SH --freq 60min --start-date 20260220 --limit 20
```

### 实时数据查询
```bash
# 最新股价
python3 {baseDir}/scripts/astock_query.py --symbol 000001.SZ --realtime

# 成交明细
python3 {baseDir}/scripts/astock_query.py --symbol 000001.SZ --trades --limit 10
```

### 高级查询
```bash
# 指定字段查询
python3 {baseDir}/scripts/astock_query.py --symbol 000001.SZ --freq 5min --fields "ts_code,trade_time,open,close,vol" --start-date 20260227

# 按时间排序
python3 {baseDir}/scripts/astock_query.py --symbol 000001.SZ --freq 5min --order-by trade_time --sort asc --start-date 20260227
```

## 输出格式

### JSON格式 (默认)
```json
{
  "symbol": "000001.SZ",
  "freq": "5min",
  "data": [
    {
      "ts_code": "000001.SZ",
      "trade_time": "2026-02-27 09:30:00",
      "open": "10.8600",
      "close": "10.8500",
      "high": "10.8600",
      "low": "10.8500",
      "vol": "286200.0000",
      "amount": "3107687.0000"
    }
  ],
  "total": 49,
  "provider": "qgdata"
}
```

## 股票代码格式

- **深圳股票**: `000001.SZ` (平安银行)
- **上海股票**: `600000.SH` (浦发银行)
- **创业板**: `300001.SZ` (特锐德)
- **科创板**: `688001.SH` (华兴源创)

## 数据特点

- **实时性**: 分钟级数据更新
- **准确性**: 来自交易所的官方数据
- **完整性**: 包含所有A股品种
- **高效性**: 优化的查询性能

## 适用场景

- **量化交易**: 分钟级策略开发和回测
- **日内交易**: 实时监控和决策支持
- **技术分析**: 基于分钟K线的指标计算
- **程序化交易**: 自动化交易策略实现

## API限制

- **频率限制**: 请控制查询频率，避免过度调用
- **数据范围**: 支持最近一定时期的历史数据
- **字段限制**: 每次查询可指定返回字段

## 版本信息

- **当前版本**: 1.2.0 (修复版)
- **API版本**: qgdata 0.1.2
- **数据更新**: 实时

---

*专业A股分钟级数据查询服务 - 驱动量化交易的强大工具* ⏱️📊🚀
