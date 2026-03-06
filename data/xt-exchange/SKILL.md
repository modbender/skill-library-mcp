---
name: xt-exchange
description: XT.COM exchange CLI — spot & futures trading via progressive conversation. Market data, balance, orders, transfer, and withdrawal.
version: 1.0.0
emoji: 📈
homepage: https://github.com/realm520/xt-exchange-plugin
metadata:
  openclaw:
    requires:
      bins:
        - python3
      env:
        - XT_ACCESS_KEY
        - XT_SECRET_KEY
    primaryEnv: XT_ACCESS_KEY
install:
  - kind: brew
    formula: python@3
    bins: [python3]
---

# XT Exchange Skill

当用户调用 `/xt-exchange` 时，遵循以下渐进式披露流程。

## 脚本路径

```bash
PYTHON="python3"
SPOT="SKILL_PATH/scripts/xt_spot.py"
FUTURES="SKILL_PATH/scripts/xt_futures.py"
```

> `SKILL_PATH` 由 OpenClaw 自动注入为 skill 安装目录路径。

## 认证方式

脚本优先读取以下凭证（按优先级）：

1. **环境变量**（推荐）：`XT_ACCESS_KEY` + `XT_SECRET_KEY`
2. **本地文件**：`~/.xt-exchange/credentials.json`

在执行需要认证的操作前，先检查凭证是否存在：

```bash
# 检查环境变量
echo $XT_ACCESS_KEY

# 或检查本地文件
cat ~/.xt-exchange/credentials.json 2>/dev/null
```

若两者均未设置，引导用户：

> 「需要 API Key 才能进行账户操作。请在 XT.COM 的 API 管理页面创建 Key，设置环境变量 XT_ACCESS_KEY 和 XT_SECRET_KEY，或将其保存到 ~/.xt-exchange/credentials.json。」

## 安装 Python 依赖

首次使用前，确保 `requests` 已安装：

```bash
pip3 install requests -q
```

## 启动规则

调用后**不要展示功能菜单**，直接问：

> 「现货还是合约？」

## 渐进式问答流程（最多 2 轮追问）

### 第一轮：现货 or 合约

用户选择后进入第二轮，或用户已给出足够信息则直接执行。

### 第二轮：具体操作

**现货**：行情 / 余额 / 下单 / 撤单 / 划转 / 提币 / 历史订单
**合约**：行情 / 账户权益 / 持仓 / 开仓 / 平仓 / 撤单 / 历史委托

### 追问必要参数

- 行情类：交易对（如 `btc_usdt`）
- 下单/开仓：交易对、数量、价格（市价不需要价格）
- 余额/账户：直接执行

**超过 2 轮追问就执行**，不再继续问。

## 安全规则

下单 / 撤单 / 划转 / 开仓 / 平仓 **执行前必须**：
1. 展示完整参数（symbol、方向、价格、数量）
2. 等待用户确认（「确认」「yes」「对」等）
3. 收到确认后才执行

**提币额外规则**（不可逆操作，需二次确认）：
1. 展示：币种、链名、数量、手续费、预计到账量、**完整目标地址**
2. 明确提示「提币不可撤销」
3. 等待用户确认后才执行
4. 若用户只说了地址但未指定链，先查询支持的链及最小提币量，再由用户选择：
   ```bash
   $PYTHON $SPOT symbol <currency>
   ```

## 输出规则

- **价格**：加粗
- **余额**：只显示非零余额
- **订单列表**：表格格式
- **不粘贴原始 JSON**，除非用户要求

## 命令参考

```bash
PYTHON="python3"
SPOT="SKILL_PATH/scripts/xt_spot.py"
FUTURES="SKILL_PATH/scripts/xt_futures.py"

# ── 现货行情（无需 Key）──
$PYTHON $SPOT ticker btc_usdt
$PYTHON $SPOT ticker_24h btc_usdt
$PYTHON $SPOT depth btc_usdt --limit 10
$PYTHON $SPOT klines btc_usdt --interval 1h --limit 24
$PYTHON $SPOT symbol btc_usdt

# ── 现货账户（需要 Key）──
$PYTHON $SPOT balance
$PYTHON $SPOT balance usdt
$PYTHON $SPOT orders
$PYTHON $SPOT history --limit 20

# ── 现货下单（确认后执行）──
$PYTHON $SPOT buy btc_usdt --price 50000 --qty 0.001
$PYTHON $SPOT sell btc_usdt --price 60000 --qty 0.001
$PYTHON $SPOT buy btc_usdt --market --quote_qty 100
$PYTHON $SPOT cancel --id 123456789
$PYTHON $SPOT cancel_all
# 账户类型：SPOT / LEVER / FUTURES_U（USDT本位合约）/ FUTURES_C（币本位合约）/ FINANCE
$PYTHON $SPOT transfer --from SPOT --to LEVER --currency usdt --amount 100
$PYTHON $SPOT transfer --from FUTURES_U --to SPOT --currency usdt --amount 10
# 提币
$PYTHON $SPOT withdraw --currency pol --chain "Polygon POS" --amount 200 --address 0xABC...
$PYTHON $SPOT withdraw --currency usdt --chain "Ethereum" --amount 50 --address 0xABC...

# ── 合约行情（无需 Key）──
$PYTHON $FUTURES ticker btc_usdt
$PYTHON $FUTURES depth btc_usdt
$PYTHON $FUTURES funding_rate btc_usdt
$PYTHON $FUTURES klines btc_usdt --interval 1h

# ── 合约账户（需要 Key）──
$PYTHON $FUTURES account
$PYTHON $FUTURES positions
$PYTHON $FUTURES orders

# ── 合约开平仓（确认后执行）──
# qty 单位为"张"（整数），contractSize 因品种而异
$PYTHON $FUTURES open_long btc_usdt --qty 1 --price 50000
$PYTHON $FUTURES open_short btc_usdt --qty 1 --market
$PYTHON $FUTURES close_long btc_usdt --qty 1
$PYTHON $FUTURES cancel --id 123456789
$PYTHON $FUTURES history
```
