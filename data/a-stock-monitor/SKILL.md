---
name: a-stock-monitor
description: A股量化监控系统 - 7维度市场情绪评分、智能选股引擎（短线5策略+中长线7策略）、实时价格监控、涨跌幅排行榜。支持全市场5000+股票数据采集与分析，多指标共振评分，精确买卖点计算，动态止损止盈。每日自动推荐短线3-5只、中长线5-10只优质股票。包含Web界面、自动化Cron任务、历史数据回溯。适用于A股量化交易、技术分析、选股决策。
author: James Mei
contact:
  email: meijinmeng@126.com
  blog: https://www.cnblogs.com/Jame-mei
metadata:
  openclaw:
    requires:
      bins: ["python3"]
      packages: ["akshare", "flask", "ccxt"]
---

# A股量化选股和监控系统

一个完整的A股量化选股、实时监控与市场情绪分析系统。

**作者**: James Mei  
**邮箱**: meijinmeng@126.com  
**博客**: https://www.cnblogs.com/Jame-mei  
**版本**: 1.1.2  
**许可证**: MIT

## 🆕 v1.1.2 更新 (2026-02-24)

### 核心优化
- ⚡ **性能提升6-10倍**：交易时间使用新浪财经（0.1秒 vs 1.5秒）
- 🔧 **修复关键Bug**：全市场数据更新、选股功能
- 📊 **数据完整性**：从8只提升到5748只（98.9%）
- 🎯 **智能切换**：交易时间新浪优先，盘后akshare稳定

### 技术改进
- 双数据源架构（新浪+akshare）
- 自动判断交易时间
- 超时保护和降级机制
- 完整的向后兼容

详见：[CHANGELOG.md](references/CHANGELOG.md)

---

## 核心功能

### 1. 市场情绪评分 (7维度)
基于全市场5000+只A股的综合情绪评分（0-100分）：
- 涨跌家数比 (20%)
- 平均涨幅 (20%)
- 涨停/跌停比 (15%)
- 强势股占比 (15%)
- 成交活跃度 (10%)
- 波动率 (10%)
- 趋势强度 (10%)

### 2. 智能选股引擎

#### 短线选股 (1-5天)
**5大策略**，每日推荐3-5只短线机会股：
- **RSI短线** - 超短线RSI策略，适合T+0或快速进出
- **MACD短线** - MACD金叉死叉，短期趋势跟踪
- **KDJ短线** - KDJ超买超卖，适合日内波段
- **布林突破** - 布林带突破，捕捉短期波动
- **放量突破** - 量价齐升，短期强势股

**多指标共振评分体系** (满分100分)：
- RSI信号 (20分)
- KDJ信号 (20分)
- MACD信号 (15分)
- 布林带信号 (15分)
- 量价异动 (15分)
- 资金流向 (15分)

**精确买卖点**：
- 动态止损止盈（基于ATR）
- 买入价、止损价、止盈价自动计算
- 预期收益率、风险收益比

#### 中长线选股 (20-180天)
**7大策略**，每日推荐5-10只优质股票：
- **MA趋势** - 均线多头排列，趋势跟踪 (20-60天)
- **MACD趋势** - MACD趋势确认，中期持有 (15-30天)
- **价值成长** - 长期价值投资 (60-180天)
- **突破回踩** - 突破后回踩买入 (10-30天)
- **底部反转** - RSI+MACD双确认 (15-30天)
- **趋势加速** - 均线多头+放量 (10-20天)
- **强势股回调** - 强势股回调低吸 (5-15天)

**综合评分维度**：
- 技术指标 (40%) - MA/MACD/RSI/KDJ等
- 资金流向 (30%) - 主力资金净流入
- 市场热度 (15%) - 换手率、振幅
- 风险评估 (15%) - 波动率、回撤

**持仓建议**：
- 建议仓位（根据评分）
- 预期收益率
- 风险等级
- 持仓周期

#### 选股配置
- 自动过滤创业板(3开头)和科创板(688开头)
- 支持自定义监控股票池（watchlist.json）
- 每日自动推荐，飞书/企业微信告警

### 3. 实时价格监控
- 交易时间：每5秒更新价格
- 非交易时间：显示历史数据
- 自动判断交易时段（9:15-11:30, 13:00-15:00）

### 4. 涨跌幅排行榜
- 实时涨幅榜（Top 5）
- 实时跌幅榜（Top 5）
- 支持点击查看详情

### 5. Web可视化界面
- 市场情绪仪表盘
- 监控股票卡片展示
- 统计数据汇总
- 响应式设计

## 使用方式

### 快速开始

1. **安装依赖**
```bash
pip3 install akshare flask ccxt
```

2. **配置监控股票**
编辑 `web_app.py`，修改 `WATCHED_STOCKS` 列表：
```python
WATCHED_STOCKS = [
    '600900',  # 长江电力
    '601985',  # 中国核电
    # 添加更多股票代码...
]
```

3. **启动Web服务**
```bash
cd scripts/
python3 web_app.py
```
访问 `http://localhost:5000`

### 自动化运行

**设置Cron任务**（交易时间每5分钟更新）：
```bash
openclaw cron add --name "A股全市场数据更新" \
  --schedule "*/5 9-15 * * 1-5" \
  --tz "Asia/Shanghai" \
  --payload '{"kind":"systemEvent","text":"cd <skill-path>/scripts && python3 smart_market_updater.py"}'
```

替换 `<skill-path>` 为技能安装路径。

### 手动执行

```bash
# 更新全市场数据
python3 scripts/update_all_market_data.py

# 计算市场情绪
python3 scripts/market_sentiment.py

# 智能更新（仅交易时间）
python3 scripts/smart_market_updater.py

# 检查交易时间
python3 scripts/is_trading_time.py

# 短线选股（每日推荐3-5只）
python3 scripts/short_term_selector.py

# 中长线选股（每日推荐5-10只）
python3 scripts/long_term_selector.py

# 增强版中长线选股
python3 scripts/enhanced_long_term_selector.py
```

## 目录结构

```
scripts/
├── web_app.py                      # Flask Web服务
├── stock_cache_db.py               # SQLite数据缓存
├── stock_async_fetcher.py          # 异步数据获取
├── market_sentiment.py             # 市场情绪计算
├── is_trading_time.py              # 交易时间判断
├── smart_market_updater.py         # 智能更新器
├── update_all_market_data.py       # 全市场数据更新
├── short_term_selector.py          # 短线选股引擎
├── long_term_selector.py           # 中长线选股引擎
├── enhanced_long_term_selector.py  # 增强版中长线选股
├── strategy_config.py              # 策略配置文件
└── templates/
    └── index.html                  # Web前端页面
```

## API端点

### GET /api/market/sentiment
返回全市场情绪评分

**响应示例**:
```json
{
  "score": 57,
  "level": "偏乐观",
  "emoji": "🟢",
  "description": "市场偏强，情绪稳定",
  "stats": {
    "total": 5000,
    "gainers": 2460,
    "losers": 2534,
    "limit_up": 15,
    "limit_down": 3
  }
}
```

### GET /api/stocks
返回所有监控股票数据

### GET /api/stocks/realtime
返回监控股票实时价格（轻量级）

### GET /api/stock/<code>
返回单只股票详情

## 配置说明

### 交易时间配置
默认交易时间：周一至周五 9:15-15:00

修改 `is_trading_time.py`：
```python
TRADING_HOURS = {
    'morning': (9, 15, 11, 30),    # 9:15-11:30
    'afternoon': (13, 0, 15, 0),   # 13:00-15:00
}
```

### 数据缓存配置
SQLite数据库：`stock_cache.db`
默认缓存时间：30分钟

修改 `stock_cache_db.py`：
```python
MAX_AGE_MINUTES = 30  # 缓存有效期
```

### 监控股票配置
编辑 `web_app.py` 中的 `WATCHED_STOCKS` 列表

### 市场情绪阈值
修改 `market_sentiment.py`：
```python
# 情绪等级阈值
LEVELS = [
    (80, 100, '极度乐观', '🔴'),
    (65, 79, '乐观', '🟠'),
    (55, 64, '偏乐观', '🟢'),
    # ...
]
```

## 数据来源

- **akshare**: 获取A股实时行情、全市场数据
- **本地缓存**: SQLite数据库存储历史数据

## 性能优化

1. **分级更新**
   - 实时价格: 5秒（仅价格+涨跌）
   - 完整数据: 30秒（含技术指标）
   - 后端更新: 5分钟（全市场数据）

2. **智能缓存**
   - 交易时间: 5分钟缓存
   - 非交易时间: 显示历史数据

3. **异步获取**
   - 使用异步方式获取全市场数据
   - 避免阻塞主线程

## 故障排查

### 问题1: 数据全为null
**原因**: 非交易时间，akshare返回空数据
**解决**: 等待交易时间，或导入演示数据

### 问题2: Web界面一直转圈
**原因**: 数据库无有效数据
**解决**: 运行 `python3 update_all_market_data.py`

### 问题3: Cron任务不执行
**原因**: 时区配置错误
**解决**: 确保时区设置为 `Asia/Shanghai`

### 问题4: 端口被占用
**原因**: Flask默认端口5000冲突
**解决**: 修改 `web_app.py` 中的端口号

## 扩展开发

### 添加新的监控指标
编辑 `market_sentiment.py`，添加新的评分维度：

```python
def calculate_sentiment(stocks):
    # 添加新维度
    new_dimension_score = calculate_new_dimension(stocks)
    
    # 调整权重
    score = (
        gain_ratio_score * 0.18 +      # 降低原有权重
        # ...
        new_dimension_score * 0.10      # 新维度10%
    )
```

### 自定义告警规则
创建新的告警脚本：

```python
def check_custom_alert():
    cache = StockCache()
    stocks = cache.get_all_stocks()
    
    # 自定义告警逻辑
    alerts = []
    for stock in stocks:
        if stock['change_pct'] > 5:
            alerts.append(stock)
    
    if alerts:
        send_alert(alerts)
```

## 技术栈

- **后端**: Python 3.9+, Flask
- **数据**: akshare, SQLite
- **前端**: jQuery, Bootstrap
- **自动化**: OpenClaw Cron

## 许可证

MIT License

## 联系作者

- **邮箱**: meijinmeng@126.com
- **博客**: https://www.cnblogs.com/Jame-mei

欢迎反馈问题、建议和改进意见！

## 致谢

- akshare 提供A股数据接口
- OpenClaw 提供自动化调度能力
