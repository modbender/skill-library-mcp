---
name: fal-consumption-audit
description: 审计 fal 账号消耗与用户扣费的一致性。查询 fal 官方账单，交叉比对 fal_tasks 中的用户消耗，汇总积分/现金明细，检测异常。当用户提到"消耗审计"、"账单核对"、"fal 对账"、"用量异常"时使用此 skill。
---

# Fal 消耗审计

## 审计目标

核对三层数据的一致性，发现差异和异常：

```
fal 官方账单（实际成本）
       ↕ 比对
fal_tasks 任务表（系统记录）
       ↕ 比对
用户积分/现金明细（用户扣费）
```

## 审计流程

复制此清单跟踪进度：

```
Task Progress:
- [ ] Step 1: 查询 fal 官方账单
- [ ] Step 2: 查询 fal_tasks 任务明细
- [ ] Step 3: 按用户聚合消耗
- [ ] Step 4: 比对用户积分/现金明细
- [ ] Step 5: 异常检测 & 输出报告
```

---

## Step 1: 查询 fal 官方账单

调用 fal Platform API 获取每个 fal 账号的实际消耗。

**API**: `GET https://api.fal.ai/v1/models/usage`

**认证**: `Authorization: Key {fal_api_key}`

**关键参数**:

| 参数 | 值 | 说明 |
|------|-----|------|
| `expand` | `["time_series", "auth_method", "summary"]` | 包含按时间和汇总数据 |
| `timeframe` | `day` | 按天聚合 |
| `start` | 审计开始日期 | ISO8601 格式 |
| `end` | 审计结束日期 | ISO8601 格式 |

**数据来源**: `FalAccount` 表（`ts_fal_account`），取最新插入的 20 个账号（按 id 倒序，不过滤 status）

```
FalAccount 关键字段:
  id          - 账号ID
  api_key     - fal API 密钥（用于调用 Usage API + 关联 FalTasks）
  balance     - 当前余额
  status      - 1=正常 0=禁用

查询: FalAccount.select().order_by(FalAccount.id.desc()).limit(20)
```

**输出**: 每个 fal 账号 → 各模型的 cost(USD) 和 quantity

---

## Step 2: 查询 fal_tasks 任务明细

从 `FalTasks` 表查询同一时间段内，每个 fal key 被哪些用户使用。

**数据来源**: `FalTasks` 表（`ts_fal_tasks`）

```
FalTasks 关键字段:
  user_id     - 发起任务的用户ID（核心关联字段）
  api_key     - 使用的 fal API 密钥（与 FalAccount.api_key 关联）
  app_name    - fal 模型名称（如 fal-ai/flux/schnell）
  money       - 向用户收取的金额（系统内积分，单位：分）
  cost_money  - fal 实际成本
  status      - 任务状态
  is_refund   - 是否退款（0=否 1=是）
  created_at  - 创建时间
```

**查询逻辑**:

```
SELECT
  api_key,
  user_id,
  app_name,
  COUNT(*) as task_count,
  SUM(money) as total_charged,        -- 向用户收的
  SUM(cost_money) as total_cost,      -- fal 实际成本
  SUM(CASE WHEN is_refund=1 THEN 1 ELSE 0 END) as refund_count
FROM ts_fal_tasks
WHERE created_at BETWEEN {start} AND {end}
GROUP BY api_key, user_id, app_name
ORDER BY total_charged DESC
```

---

## Step 3: 按用户聚合消耗

将 Step 2 的结果按 `user_id` 聚合，得到每个用户的消耗全貌。

**聚合维度**:

| 维度 | 说明 |
|------|------|
| 用户总消耗 | SUM(money) — 用户在 fal_tasks 中被收取的总积分 |
| 用户实际成本 | SUM(cost_money) — 对应的 fal 实际成本 |
| 用户任务数 | COUNT(*) — 总任务数 |
| 用户退款数 | SUM(is_refund=1) — 退款任务数 |
| 使用的 fal 账号 | GROUP_CONCAT(DISTINCT api_key) — 用了几个 fal 账号 |
| 使用的模型 | GROUP_CONCAT(DISTINCT app_name) — 用了哪些模型 |

---

## Step 4: 比对用户积分/现金明细

对 Step 3 中每个用户，查询其积分明细和现金明细进行交叉验证。

**积分明细表**: `PointsDetail`（`ts_points_detail`）

```
PointsDetail 关键字段:
  user_id        - 用户ID
  points         - 积分变动（正=增加，负=减少）
  title          - 交易说明（包含任务描述）
  source_type    - 来源类型：recharge/consume/gift/refund
  balance_before - 交易前余额
  balance_after  - 交易后余额
  created_at     - 创建时间
```

**现金明细表**: `FinancialTransactions`（`ts_financial_transactions`）

```
FinancialTransactions 关键字段:
  user_id          - 用户ID
  money            - 交易金额（单位：分，正=收入，负=支出）
  title            - 交易标题
  transaction_type - 0=充值/退款 1=消耗 3=智能体收益
  is_cash          - 0=否 1=是（现金交易）
  time             - 时间戳
```

**查询逻辑**:

对每个用户，分别查询审计时间段内的：

```
-- 积分消耗汇总
SELECT
  user_id,
  SUM(CASE WHEN source_type='consume' THEN ABS(points) ELSE 0 END) as points_consumed,
  SUM(CASE WHEN source_type='refund' THEN points ELSE 0 END) as points_refunded,
  SUM(CASE WHEN source_type='recharge' THEN points ELSE 0 END) as points_recharged,
  COUNT(*) as transaction_count
FROM ts_points_detail
WHERE user_id = {uid} AND created_at BETWEEN {start} AND {end}

-- 现金消耗汇总
SELECT
  user_id,
  SUM(CASE WHEN transaction_type=1 THEN ABS(money) ELSE 0 END) as cash_consumed,
  SUM(CASE WHEN transaction_type=0 AND money>0 THEN money ELSE 0 END) as cash_recharged,
  COUNT(*) as transaction_count
FROM ts_financial_transactions
WHERE user_id = {uid} AND time BETWEEN {start} AND {end}
```

---

## Step 5: 异常检测 & 输出报告

### 异常检测规则

| 编号 | 规则 | 判定条件 | 严重等级 |
|:---:|------|----------|:--------:|
| A1 | **fal 成本 vs 系统记录偏差** | abs(fal官方cost - fal_tasks.cost_money之和) / fal官方cost > 10% | HIGH |
| A2 | **用户被收费但 fal 无记录** | fal_tasks 有记录但 fal Usage API 中无对应模型消耗 | HIGH |
| A3 | **fal 有消耗但用户未被收费** | fal Usage API 有消耗但 fal_tasks 中无对应任务 | HIGH |
| A4 | **收费与扣费不一致** | fal_tasks.money 之和 ≠ PointsDetail consume 之和 | MEDIUM |
| A5 | **异常退款** | 退款金额 > 当日消耗总额的 30% | MEDIUM |
| A6 | **单用户消耗异常** | 用户当日消耗 > 历史日均消耗的 5 倍 | LOW |
| A7 | **零成本任务** | fal_tasks.money=0 且 cost_money>0（白嫖） | MEDIUM |
| A8 | **fal 账号余额预警** | FalAccount.balance < 1.0 USD | LOW |

### 报告输出格式（终端）

```
============================================================
  Fal 消耗审计报告
  审计日期: 2026-02-06
  审计范围: 2026-02-06 00:00:00 ~ 2026-02-06 23:59:59
============================================================

  ━━━ 第一层：Fal 官方账单 ━━━

  账号ID  余额(USD)  官方消耗(USD)  模型数  请求数
  ─────  ─────────  ────────────  ──────  ──────
     5      12.30         99.92      18    1049
    12      45.60          8.50       5     120
  ─────  ─────────  ────────────  ──────  ──────
  合计                    108.42      --    1169

  ━━━ 第二层：系统任务记录 (fal_tasks) ━━━

  fal账号ID  用户ID  用户名   模型              任务数  收费(积分)  fal成本(USD)
  ────────  ──────  ──────  ────────────────  ──────  ─────────  ──────────
     5       101    张三     sora-2/i2v          50      5000       5.00
     5       102    李四     kling/v2.1/i2v      30      8400      28.00
     5       103    王五     seedream/v4/t2i     20       600       0.60
    12       101    张三     flux/schnell        80       800       0.80
  ────────  ──────  ──────  ────────────────  ──────  ─────────  ──────────
  合计                                         180     14800      34.40

  ━━━ 第三层：用户扣费核对 ━━━

  用户ID  用户名   fal任务收费  积分消耗  现金消耗  积分充值  差异(积分)  状态
  ──────  ──────  ──────────  ────────  ────────  ────────  ─────────  ────
   101    张三        5800      5600       200      1000         0     OK
   102    李四        8400      8400         0         0         0     OK
   103    王五         600       400       200         0         0     OK

  ━━━ 异常告警 ━━━

  [HIGH]  A1: fal账号5 官方成本$99.92 vs 系统记录$34.40，偏差65.6%
  [MEDIUM] A7: 用户103 有3笔任务 money=0 但 cost_money>0
  [LOW]   A8: fal账号23 余额 $0.15，低于阈值

============================================================
  审计完成
  正常: 2 | 告警: 3 | 严重: 1
============================================================
```

## 数据关联关系图

```
FalAccount (ts_fal_account)
  │ api_key
  ├──────→ fal Usage API (官方账单, 按 api_key 查)
  │
  └──────→ FalTasks (ts_fal_tasks)
              │ api_key = FalAccount.api_key
              │ user_id → 关联到用户
              │
              └──→ User (ts_users)
                    │ id = FalTasks.user_id
                    │
                    ├──→ PointsDetail (ts_points_detail)
                    │     user_id = User.id
                    │     source_type = 'consume' / 'refund'
                    │
                    └──→ FinancialTransactions (ts_financial_transactions)
                          user_id = User.id
                          transaction_type = 1 (消耗)
```

## 脚本位置

实现脚本写在: `translate_api/app/coze/fal_balance.py`

已有的可复用函数:
- `query_fal_usage(api_key, start, end, timeframe)` — 查询 fal 官方用量

## 运行方式

```bash
# 审计今天
python fal_balance.py audit

# 审计指定日期
python fal_balance.py audit --start 2026-02-01 --end 2026-02-06

# 只审计指定 fal 账号
python fal_balance.py audit --ids 5 12

# 只审计指定用户
python fal_balance.py audit --user-ids 101 102
```

## 补充资料

- fal Usage API 文档: https://docs.fal.ai/platform-apis/v1/models/usage
- 数据模型定义: [reference.md](reference.md)
