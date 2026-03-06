---
name: futu-api
description: |
  富途牛牛API数据获取技能。
  纯数据版本，专注于股票行情数据获取和技术分析。
  触发场景：查询股票行情、分析K线数据、计算技术指标、监控市场变化。
  适用于：港股、美股市场数据分析和量化研究。
---

# 富途API数据技能

## 🎯 概述

基于富途牛牛官方API的纯数据技能，提供股票行情数据获取和技术分析功能。**无交易功能**，专注于数据分析和市场监控。

## 🚀 快速开始

### 安装依赖
```bash
cd /Users/chengling/.openclaw/workspace/skills/futu-api
pip install -r requirements.txt
```

### 前置要求
1. 安装并运行 **FutuOpenD** 应用程序
2. 登录富途账户
3. 确保连接地址：`127.0.0.1:11111`

### 基本使用
```bash
# 查询实时行情
python futu_api.py quote 00700 --market HK

# 获取K线数据
python futu_api.py kline 00700 --market HK --type 5m --count 100

# 计算技术指标
python futu_api.py indicators 00700 --market HK --type day --count 30

# 查看板块列表
python futu_api.py plates --market HK

# 获取逐笔成交
python futu_api.py ticker 00700 --market HK --count 10

# 查看资金流向
python futu_api.py capital 00700 --market HK

# 查看市场状态
python futu_api.py market --market HK

# 查看股票信息
python futu_api.py info 00700 --market HK
```

## 📊 核心功能

### 1. 实时行情查询
```bash
python futu_api.py quote 00700 --market HK
```
**输出示例**：
```
symbol        : 00700
market        : HK
price         : 518.0000
change        : +6.0000
change_percent: +1.17%
volume        : 32,229,030
time          : 16:08:06
```

### 2. K线数据分析
支持多种周期：
- `1m` - 1分钟线
- `5m` - 5分钟线
- `15m` - 15分钟线
- `30m` - 30分钟线
- `60m` - 60分钟线
- `day` - 日线
- `week` - 周线
- `month` - 月线

```bash
# 获取5分钟K线
python futu_api.py kline 00700 --market HK --type 5m --count 20

# JSON格式输出
python futu_api.py kline 00700 --market HK --type day --count 10 --format json
```

### 3. 技术指标计算
```bash
python futu_api.py indicators 00700 --market HK --type day --count 30
```
**计算指标**：
- `ma5`, `ma10`, `ma20` - 移动平均线
- `rsi` - 相对强弱指数
- `bb_upper`, `bb_middle`, `bb_lower` - 布林带
- `current`, `high`, `low` - 价格统计

### 4. 板块数据
```bash
# 查看板块列表
python futu_api.py plates --market HK

# 查看前20个板块
```

### 5. 逐笔成交
```bash
# 获取最近成交
python futu_api.py ticker 00700 --market HK --count 10
```

### 6. 资金流向分析
```bash
# 查看资金流向
python futu_api.py capital 00700 --market HK

# 输出示例：
# 主力净流入: +1.2亿
# 散户净流出: -0.8亿
# 资金情绪: 积极
```

### 7. 市场状态监控
```bash
# 查看市场状态
python futu_api.py market --market HK

# 输出示例：
# 市场状态: 收市
# 是否开市: 否
```

### 8. 股票基础信息
```bash
# 查看股票信息
python futu_api.py info 00700 --market HK

# 输出示例：
# 股票名称: TENCENT
# 每手股数: 100
# 上市日期: 2004-06-16
```

## 📁 文件结构

```
futu-api/
├── futu_api.py          # 主程序 (核心代码)
├── requirements.txt     # 依赖文件
├── SKILL.md            # 技能文档
└── README.md           # 使用说明
```

## 🔧 核心类说明

### `FutuAPI` 类
```python
class FutuAPI:
    def connect(self):              # 连接API
    def get_quote(symbol, market):  # 获取行情
    def get_kline(symbol, market, ktype, count):  # 获取K线
    def get_indicators(kline_data): # 计算技术指标
    def get_plates(market):         # 获取板块
    def get_ticker(symbol, market, count):  # 获取逐笔
```

## 🎯 使用示例

### 简单监控脚本
```python
from futu_api import FutuAPI

api = FutuAPI()
api.connect()

# 获取腾讯行情
quote = api.get_quote('00700', 'HK')
if quote:
    print(f"腾讯: {quote['price']} ({quote['change_percent']:+.2f}%)")

api.disconnect()
```

### 技术分析示例
```python
from futu_api import FutuAPI

api = FutuAPI()
api.connect()

# 获取K线并计算指标
kline = api.get_kline('00700', 'HK', 'day', 30)
indicators = api.get_indicators(kline)

if indicators:
    print(f"MA5: {indicators.get('ma5', 'N/A')}")
    print(f"RSI: {indicators.get('rsi', 'N/A')}")
    
    # RSI超卖/超买判断
    rsi = indicators.get('rsi')
    if rsi:
        if rsi < 30:
            print("🟢 RSI超卖，可能反弹")
        elif rsi > 70:
            print("🔴 RSI超买，可能回调")

api.disconnect()
```

## ⚙️ 配置说明

### 连接配置
默认连接地址：`127.0.0.1:11111`
如需修改，可在代码中调整：
```python
api = FutuAPI(host="127.0.0.1", port=11111)
```

### 环境检查
```bash
# 检查FutuOpenD是否运行
ps aux | grep FutuOpenD

# 检查端口
netstat -an | grep 11111

# 测试连接
telnet 127.0.0.1 11111
```

## 🔒 注意事项

### 数据使用
- ✅ **只读数据**：仅获取行情数据，无交易操作
- ✅ **合规使用**：遵守富途API使用条款
- ✅ **频率限制**：避免高频调用API

### 前置要求
1. **必须安装FutuOpenD**：从富途官网下载
2. **必须登录账户**：在FutuOpenD中登录
3. **保持连接**：FutuOpenD需要保持运行状态

## 🚨 故障排除

### 常见问题

#### 1. 连接失败
```bash
# 检查FutuOpenD是否运行
ps aux | grep FutuOpenD

# 重启FutuOpenD并重新登录
```

#### 2. 数据获取失败
```bash
# 检查股票代码格式
python futu_api.py quote 00700 --market HK

# 检查市场类型
python futu_api.py quote AAPL --market US
```

#### 3. 性能优化
```bash
# 减少数据量
python futu_api.py kline 00700 --count 10

# 增加查询间隔
# 避免连续高频查询
```

## 📚 相关资源

- [富途开放平台](https://openapi.futunn.com/)
- [API文档](https://openapi.futunn.com/doc/)
- [Python SDK](https://github.com/FutunnOpen/futu-api-python-sdk)

---

**版本**: 1.0.0  
**最后更新**: 2026-02-27  
**技能类型**: 纯数据获取  
**适用市场**: 港股、美股