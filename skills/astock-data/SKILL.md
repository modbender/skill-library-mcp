---
name: astock-data
description: "🚀 专业A股量化数据API：1/5/15/30/60分钟实时K线 + 智能数据质量检测。覆盖沪深3000+股票，毫秒级响应，无限量调用。量化交易、算法策略、高频交易的理想数据源。"
metadata:
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
- ⚡ **智能默认**: 不指定日期时自动返回最新数据
- 🔄 **智能排序**: 默认降序返回最近数据
- 📊 **数据质量**: 自动检测数据时效性并给出警告

## 配置要求

### 🔑 API Key配置

#### 免费体验Token（推荐新用户）
技能内置免费体验token，包含一定量的免费调用额度：
```bash
# 自动使用免费体验token（无需配置）
# 系统会优先使用内置的免费token体验功能
```

#### 自定义API Key（专业用户）
如需更高调用频率或专业服务，请配置自己的token：
```bash
# 环境变量
export QGDATA_TOKEN="your_personal_token_here"

# 或.env文件
echo "QGDATA_TOKEN=your_personal_token_here" >> ~/.openclaw/.env
```

#### 📊 免费额度说明
- **体验额度**: 每日1000次API调用（**共享额度，先到先得**）
- **数据覆盖**: 沪深3000+股票全覆盖
- **响应速度**: 毫秒级响应
- **数据质量**: 与付费版本完全一致
- **使用提醒**: 共享额度可能因其他用户使用而提前耗尽
- **智能引导**: 额度不足时自动提供详细升级指南

#### 🚀 升级到个人Token的好处
当免费额度用完时，系统会智能引导您升级：

**为什么需要升级？**
- 🔓 **无限制调用**: 告别每日额度限制
- ⚡ **更高频率**: 支持高频交易策略
- 📊 **完整数据**: 解锁更多专业字段
- 🎯 **独享额度**: 不受其他用户影响
- 💬 **专属支持**: 优先技术服务

**升级流程：**
1. 🖥️ 访问 [https://data.quantgo.ai](https://data.quantgo.ai) 注册
2. 🔐 完成实名认证（大陆用户）
3. 🔑 获取专属API Token
4. ⚙️ 配置到OpenClaw环境

### 依赖安装
```bash
pip install qgdata pandas
```

## 使用方法

### 分钟K线查询

#### 最简单用法（推荐）
```bash
# 获取最近 5 条 60 分钟 K 线（自动获取最新数据）
python3 {baseDir}/scripts/astock_query.py --symbol 000001.SZ --freq 60min --limit 5

# 获取最近 10 条 5 分钟 K 线
python3 {baseDir}/scripts/astock_query.py --symbol 000002.SZ --freq 5min --limit 10
```

#### 高级用法
```bash
# 指定时间范围查询
python3 {baseDir}/scripts/astock_query.py --symbol 000001.SZ --freq 5min --start-date 20260227 --limit 100

# 升序排列（最早的数据在前）
python3 {baseDir}/scripts/astock_query.py --symbol 000001.SZ --freq 5min --sort asc --limit 20

# 指定查询字段
python3 {baseDir}/scripts/astock_query.py --symbol 000001.SZ --freq 5min --fields "ts_code,trade_time,open,close,vol" --limit 10
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
  "start_date": "20260227",
  "data": [
    {
      "ts_code": "000001.SZ",
      "trade_time": "2026-02-27 15:00:00",
      "open": "10.8700",
      "close": "10.9000",
      "high": "10.9000",
      "low": "10.8600",
      "vol": "6305196.0000",
      "amount": "68703336.0000"
    }
  ],
  "total": 3,
  "fields": ["ts_code", "trade_time", "open", "close", "high", "low", "vol", "amount"],
  "date_warning": "null",
  "provider": "qgdata"
}
```

#### date_warning 字段说明
- `"null"` - 数据正常（3天内）
- `"ℹ️ 数据较旧（X天前）"` - 数据较旧但可用（3-10天）
- `"⚠️ 数据很旧（X天前）"` - 数据很旧建议重新查询（超过10天）

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

- **当前版本**: 1.7.0 (智能升级引导版)
- **API版本**: qgdata 0.1.2
- **数据更新**: 实时

## 更新日志

### v1.7.0 (2026-03-02)
- 🚀 **智能升级引导**: 免费额度不足时自动提供完整注册和配置指南
- 🔗 **一键注册链接**: 直接引导至 https://data.quantgo.ai 注册页面
- 💰 **定价透明化**: 展示Starter/Pro/Enterprise三个套餐选择
- 📋 **步骤化指导**: 提供4步注册配置流程
- 🎯 **价值展示**: 详细说明升级后的5大核心优势

### v1.6.0 (2026-03-02)
- ⚠️ **共享额度提醒**: 明确标注每日1000次免费额度为共享使用，先到先得
- 💬 **用户提示**: 使用免费token时显示额度共享提醒
- 🛡️ **透明度提升**: 让用户清楚了解免费额度的限制和特点
- 📊 **使用追踪**: 输出结果中包含token使用状态提示

### v1.5.0 (2026-03-02)
- 🎁 **免费体验**: 内置免费token，每日1000次调用额度
- 📚 **零配置体验**: 新用户无需配置即可体验专业A股数据
- 💡 **智能降级**: 免费额度用尽时自动提示升级
- 🎯 **用户友好**: 清晰标注免费vs付费功能差异

### v1.4.0 (2026-03-02)
- 🚀 大幅优化技能描述：突出量化交易价值、使用emoji增强视觉吸引力

### v1.3.0 (2026-03-02)
- ✨ **智能默认**: 不指定日期时自动返回最新数据
- 🔄 **智能排序**: 默认降序返回最近数据
- 📊 **数据质量检测**: 自动检测数据时效性并给出警告
- ⚡ **简化用法**: 最简单的命令即可获取最新数据

### v1.2.0 (2026-03-02)
- 🐛 修复SKILL.md文件名大小写问题
- ✅ 确保OpenClaw正确识别技能

### v1.1.0 (2026-03-02)
- 🚀 集成qgdata API
- 📈 提供真实的A股分钟级数据查询

---

*专业A股分钟级数据查询服务 - 驱动量化交易的强大工具* ⏱️📊🚀
