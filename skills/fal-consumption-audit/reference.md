# 数据模型参考

## 表关系总览

```
ts_fal_account          1:N    ts_fal_tasks          (通过 api_key 字段关联)
ts_fal_tasks            N:1    ts_users              (通过 user_id 字段关联)
ts_users                1:N    ts_points_detail      (通过 user_id 字段关联)
ts_users                1:N    ts_financial_transactions (通过 user_id 字段关联)
```

## 表结构

### ts_fal_account (FalAccount)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键 |
| name | CharField(100) | 账号名称 |
| api_key | CharField(150) | fal API 密钥（唯一，关联 FalTasks） |
| balance | Float | 当前余额 (USD) |
| use_cnt | Int | 使用次数 |
| error_cnt | Int | 错误次数 |
| status | Int | 1=正常 0=禁用 |
| remark | Text | 备注 |

### ts_fal_tasks (FalTasks)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键 |
| user_id | Int (indexed) | 发起任务的用户ID |
| task_id | CharField(100) | 系统内部任务ID（唯一） |
| online_task_id | CharField(100) | fal 平台返回的任务ID |
| app_name | CharField(150) | fal 模型名称，如 `fal-ai/flux/schnell` |
| api_key | CharField(150) | 使用的 fal API 密钥 |
| task_type | CharField(100) | 任务类型 |
| status | CharField(100) | 任务状态 |
| money | Int | 向用户收取的金额（系统积分，单位：分） |
| cost_money | Float | fal 实际成本 |
| is_refund | Int | 是否退款 0=否 1=是 |
| input_params | Text | 输入参数 (JSON) |
| output_params | Text | 输出结果 (JSON) |
| created_at | DateTime | 创建时间 |
| completed_at | DateTime | 完成时间 |

### ts_points_detail (PointsDetail)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键 |
| user_id | Int | 用户ID |
| points | Int | 积分变动（正=增加，负=减少） |
| order_id | CharField(255) | 关联订单号 |
| title | CharField(255) | 交易说明 |
| source_type | CharField(50) | recharge/consume/gift/refund |
| balance_before | Int | 交易前余额 |
| balance_after | Int | 交易后余额 |
| created_at | DateTime | 创建时间 |

### ts_financial_transactions (FinancialTransactions)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键 |
| user_id | Int | 用户ID |
| money | Int | 交易金额（分，正=收入，负=支出） |
| order_id | CharField(255) | 订单ID |
| title | CharField(255) | 交易标题 |
| deployment_uuid | CharField(255) | 部署UUID |
| time | DateTime | 时间戳 |
| transaction_type | Int | 0=充值/退款 1=消耗 3=智能体收益 |
| pay_type | Int | 支付类型 |
| is_cash | Int | 0=否 1=是 |

## ORM Model 导入路径

```python
from app.models.storyboard import FalAccount, FalTasks
from app.models.computeHub import PointsDetail, FinancialTransactions
from app.models.user import User
```

## fal Usage API

```
GET https://api.fal.ai/v1/models/usage
Authorization: Key {api_key}

Query params:
  expand=time_series&expand=auth_method&expand=summary
  timeframe=day
  start=2026-02-01T00:00:00Z
  end=2026-02-06T23:59:59Z

Response 关键字段:
  summary[].endpoint_id    - 模型名（如 fal-ai/sora-2/image-to-video）
  summary[].quantity       - 请求数
  summary[].unit_price     - 单价 (USD)
  summary[].cost           - 总消耗 (USD)
  summary[].auth_method    - 认证方式（区分 key）
```

## 已有可复用代码

| 函数 | 位置 | 说明 |
|------|------|------|
| `query_fal_usage()` | `app/coze/fal_balance.py` | 查询 fal 官方用量 |
| `print_usage_report()` | `app/coze/fal_balance.py` | 打印单账号用量报告 |
| `get_user_total_money()` | `app/api/computeHub.py` | 获取用户总余额 |
| `deduct_user_money_by_id()` | `app/api/computeHub.py` | 扣费函数 |
