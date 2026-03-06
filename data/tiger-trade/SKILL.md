---
name: tiger-trade
description: Execute US and HK stock trades via Tiger Brokers API. Use when user wants to buy or sell stocks, manage investment portfolio, place orders for US ETFs or HK stocks, or check account balance. Requires tiger-config.json with tiger_id account and private_key_pk8.
---

# Tiger Trade

Execute trades via Tiger Brokers API.

## Setup

Create config file at `~/.tiger-config.json`:
```json
{
  "tiger_id": "your_tiger_id",
  "account": "your_account",
  "private_key_pk8": "your_private_key"
}
```

## Check HK Stock Prices

Use Tiger Broker website to get current prices:

```
https://www.itiger.com/hant/stock/02800
```

Replace the stock code (02800) with any HK stock:

| Code | Name |
|------|------|
| 02800 | 盈富基金 (Tracker Fund) |
| 00700 | 腾讯 (Tencent) |
| 09988 | 阿里巴巴 (Alibaba) |
| 03690 | 美团 (Meituan) |
| 01810 | 小米 (Xiaomi) |
| 00981 | 中芯国际 (SMIC) |
| 00005 | 汇丰 (HSBC) |
| 02318 | 中国平安 (Ping An) |
| 02269 | 药明生物 (WuXi Biologics) |
| 01928 | 金沙中国 (Sands China) |

## Quick Trade

```python
import json
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.trade.trade_client import TradeClient
from tigeropen.trade.request.model import PlaceModifyOrderParams
from tigeropen.common.consts import OrderType

with open('~/.tiger-config.json', 'r') as f:
    config = json.load(f)

client_config = TigerOpenClientConfig()
client_config.tiger_id = config['tiger_id']
client_config.account = config['account']
client_config.private_key = config['private_key_pk8']
client_config.sandbox = False

client = TradeClient(client_config)

# Place HK stock order
contracts = client.get_contracts(['02800'])
if contracts:
    order_params = PlaceModifyOrderParams()
    order_params.account = config['account']
    order_params.contract = contracts[0]
    order_params.action = 'BUY'
    order_params.order_type = OrderType.LMT.value
    order_params.limit_price = 26.80  # Get from itiger.com
    order_params.quantity = 10000
    
    result = client.place_order(order_params)
    print(result)
```

## Order Types

- `LMT` = Limit order
- `MKT` = Market order

## Actions

- `BUY` - 买入
- `SELL` - 卖出
