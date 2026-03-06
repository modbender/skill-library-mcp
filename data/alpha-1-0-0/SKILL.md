---
name: alpha
description: Binance Alpha new coin launch detector. Uses WebSocket to monitor !miniTicker@arr stream and detects new trading pairs immediately when they appear. Maintains known symbols set in memory and triggers alert for new symbols with valid opening price.
---

# Binance Alpha 新币上线监控

通过 WebSocket 实时监听 Binance 所有交易对行情，第一时间发现新上线的加密货币。

## 工作原理

1. **WebSocket 连接** - 连接 Binance 流式 API (`!miniTicker@arr`)
2. **Symbol 检测** - 维护 `known_symbols` 集合，检测新出现的交易对
3. **价格验证** - 通过 REST API 确认交易对已有有效开盘价
4. **实时报警** - 立即输出新币上线信息

## 功能特性

- ⚡ **实时检测** - WebSocket 流式数据，毫秒级延迟
- 🎯 **精准过滤** - 自动过滤系统 symbol 和无效数据
- ✅ **价格确认** - 双重验证确保交易对已开放交易
- 💾 **状态持久化** - 保存已知交易对和历史报警记录
- 🔄 **自动重连** - 断线自动重连，确保监控不中断

## 前提条件

### 安装依赖

```bash
pip3 install websocket-client --user
```

## 使用方法

### 启动监控

```bash
python3 scripts/alpha.py monitor
```

输出示例：
```
🚀 Binance Alpha 新币上线监控
==================================================
📂 已加载 1847 个已知交易对
✅ WebSocket 连接成功
📊 开始监控... 已知交易对: 1847 个
⏳ 等待新币上线...

======================================================================
🚀🚀🚀 新币上线 detected! 🚀🚀🚀
======================================================================
⏰ 检测时间: 2024-02-03T15:42:18.123456
🪙 交易对: BTCUSDT
💰 当前价格: 43250.50
📊 开盘价: 43100.00
📈 24h涨跌: 150.50 (0.35%)
📦 24h成交量: 15234.56
💵 24h成交额: 658923456.78
======================================================================
```

### 查看历史报警

```bash
# 查看最近 20 条
python3 scripts/alpha.py history

# 查看最近 50 条
python3 scripts/alpha.py history --limit 50
```

输出示例：
```
📜 历史报警记录 (最近 3 条):

⏰ 2024-02-03T15:42:18.123456
🪙 BTCUSDT
💰 价格: 43250.50
📊 涨跌: 0.35%
--------------------------------------------------
⏰ 2024-02-03T14:30:22.654321
🪙 ETHUSDT
💰 价格: 2650.30
📊 涨跌: 1.20%
--------------------------------------------------
```

### 查看状态

```bash
python3 scripts/alpha.py status
```

输出：
```
📊 当前状态:

  已知交易对数量: 1847
  历史报警数量: 15
  状态文件位置: /Users/xxx/.config/alpha

  最近报警:
    时间: 2024-02-03T15:42:18.123456
    交易对: BTCUSDT
```

### 重置监控

如果需要重新开始监控（清除所有历史记录）：

```bash
python3 scripts/alpha.py reset
```

⚠️ **警告**：这将清除所有已知交易对和历史报警记录！

## 技术实现

### WebSocket 数据源

**连接地址**：`wss://stream.binance.com:9443/ws/!miniTicker@arr`

**数据格式**：
```json
[
  {
    "e": "24hrMiniTicker",
    "E": 1234567890123,
    "s": "BTCUSDT",
    "c": "43250.50",
    "o": "43100.00",
    "h": "43500.00",
    "l": "42800.00",
    "v": "15234.56",
    "q": "658923456.78"
  },
  ...
]
```

字段说明：
- `s` - Symbol (交易对)
- `c` - 最新价格
- `o` - 开盘价
- `h` - 最高价
- `l` - 最低价
- `v` - 成交量
- `q` - 成交额

### 新币检测逻辑

1. 接收 `!miniTicker@arr` 推送的所有交易对数据
2. 提取每个数据包中的 `s` (symbol) 字段
3. 检查 symbol 是否在 `known_symbols` 集合中
4. 如果不在集合中，通过 REST API 确认价格有效性
5. 确认有效后触发报警，并加入 `known_symbols`

### 价格验证

通过 Binance REST API 二次确认：
```
GET /api/v3/ticker/price?symbol=XXX
```

确保交易对已有有效开盘价（价格 > 0）。

## 配置文件

状态文件存储位置：`~/.config/alpha/`

- `known_symbols.json` - 已知的交易对集合
- `alerts_history.json` - 历史报警记录（最近100条）

## 命令参考

| 命令 | 功能 | 示例 |
|------|------|------|
| `monitor` | 启动监控 | `alpha.py monitor` |
| `history` | 查看历史 | `alpha.py history --limit 50` |
| `status` | 查看状态 | `alpha.py status` |
| `reset` | 重置数据 | `alpha.py reset` |

## 运行环境

- Python 3.7+
- 网络连接（能访问 Binance）
- 无需 API Key（使用公开 WebSocket 流）

## 使用场景

### 场景1：第一时间发现新币
```bash
# 保持监控运行
python3 scripts/alpha.py monitor

# 当有新币上线时，立即在终端看到报警
```

### 场景2：追踪历史新币表现
```bash
# 查看最近发现的新币
python3 scripts/alpha.py history --limit 10
```

### 场景3：定期清理数据
```bash
# 每周重置一次，重新统计
python3 scripts/alpha.py reset
```

## 常见问题

**错误：websocket-client 库未安装**
→ 运行: `pip3 install websocket-client --user`

**连接断开**
→ 程序会自动重连，无需手动干预

**误报（显示已存在的币）**
→ 运行 `alpha.py reset` 重置数据

**没有报警**
→ 确认 Binance 确实有新币上线，检查网络连接

**如何集成到通知系统**
→ 修改 `alert_new_coin` 函数，添加邮件/短信/钉钉等通知逻辑

## 注意事项

1. **网络要求** - 需要能访问 Binance 的 WebSocket 服务
2. **内存占用** - 维护的 symbol 集合约占用几 MB 内存
3. **误报可能** - 偶尔可能因为网络问题产生重复报警
4. **仅限现货** - 监控的是现货交易对，不包含合约

## 参考

- Binance WebSocket API: https://binance-docs.github.io/apidocs/spot/en/#websocket-market-streams
- miniTicker 文档: [references/binance_ws.md](references/binance_ws.md)
