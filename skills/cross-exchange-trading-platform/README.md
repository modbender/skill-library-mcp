# Gate CrossEx Skill

Gate.io 跨交易所统一交易接口技能，支持币安、欧易、Gate.io 统一账户交易。

## 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 配置 API 密钥

```bash
export GATE_API_KEY="your_api_key"
export GATE_API_SECRET="your_api_secret"
```

### 3. 使用示例

```python
import os
from gate_crossex import GateCrossExAPI

# 初始化 API 客户端
api = GateCrossExAPI(
    api_key=os.getenv('GATE_API_KEY'),
    api_secret=os.getenv('GATE_API_SECRET')
)

# 查询账户资产
account = api.get_account()
print(f"总资产: {account['total_balance']} USDT")

# 查询 BTC 价格
price = api.get_ticker_price("BINANCE_FUTURE_BTC_USDT")
print(f"BTC 价格: {price}")
```

## 主要功能

- ✅ 跨所账户管理
- ✅ 资产划转
- ✅ 订单管理（下单、撤单、改单）
- ✅ 仓位查询
- ✅ 市场数据查询
- ✅ 闪兑交易

## 支持的交易所

- **BINANCE** - 币安
- **OKX** - 欧易
- **GATE** - Gate.io

## 文档

详细文档请查看 [SKILL.md](./SKILL.md)

## 技术支持

- 官方文档: https://www.gate.com/docs/developers/crossex
- 邮件支持: [mm@gate.com](mailto:mm@gate.com)

## 免责声明

数字货币交易具有高风险，请谨慎投资。

## 许可证

MIT License
