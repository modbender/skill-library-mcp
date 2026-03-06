# API Guide

各数据源的详细使用方法。

## 1. 港交所官方 API（hkex.py）

```python
from hkipo.hkex import fetch_hkex_active_ipos_sync, get_prospectus_url

# 获取处理中的 IPO（主板+创业板）
ipos = fetch_hkex_active_ipos_sync()

# 获取招股书 PDF 链接
pdf_url = get_prospectus_url(ipo)
```

**返回数据**：IPO 列表、提交日期、状态、招股书文档

## 2. 集思录历史（jisilu.py）

```python
from hkipo.jisilu import fetch_jisilu_history

# 获取最近 100 条历史数据
history = fetch_jisilu_history(limit=100)
```

**字段**（40+）：
- 超购倍数、中签率、首日涨幅、暗盘涨幅
- 保荐人、基石比例、入场费
- 发行价、募资额、市值

## 3. 中签率预测（allotment.py）

```python
from hkipo.allotment import predict_allotment, predict_allotment_table

# 单次预测
result = predict_allotment(
    ipo_data={'offer_price': 10, 'mechanism': 'A'},
    oversub_multiple=300,
    lots=1,
    is_group_a=True
)
# 返回: {"probability": 2.5, "expected_lots": "0-1", "group": "A"}

# 生成多档位表格
table = predict_allotment_table(ipo_data, oversub_multiple=500)
```

### 算法原理（基于公开资料推导）

```
基础中签率 = K × 价格调整因子 / 超购倍数

K_MECHANISM_A = 0.02  (有回拨机制)
K_MECHANISM_B = 1.65  (无回拨机制)
```

## 4. 保荐人表现（etnet.py）

```python
from hkipo.etnet import fetch_sponsor_rankings, get_sponsor_stats

# 获取所有保荐人排名（62 家）
sponsors = fetch_sponsor_rankings()

# 按名称查找（支持别名：中金、高盛、摩根）
stats = get_sponsor_stats("中金")
```

**字段**：
- 保荐数目
- 首日上升率
- 平均首日涨跌
- 最佳/最差表现股票

### 保荐人分析示例

```python
# 用 etnet 获取保荐人整体表现
stats = get_sponsor_stats("华泰")
# → 保荐 50 间，首日上升率 72%，平均涨幅 +39%

# 用 jisilu 获取该保荐人最近项目
history = fetch_jisilu_history(100)
projects = [h for h in history if "华泰" in h.get('underwriter', '')]
```

## 5. 富途暗盘（futu.py）

```python
from hkipo.futu import fetch_futu_listed_ipos

# 获取已上市 IPO（含暗盘涨幅）
ipos = fetch_futu_listed_ipos(limit=20)
```

**字段**：股票代码、名称、上市日期、暗盘涨跌幅、首日涨跌幅

## 6. TradeSmart 入场费（tradesmart.py）

```python
from hkipo.tradesmart import fetch_tradesmart_ipos

# 获取当前招股 IPO 的入场费档位
ipos = fetch_tradesmart_ipos()
```

**字段**：各档位入场金额、最低入场费

## 7. AAStocks 详情（fetcher.py）

通过 CLI 调用：

```bash
python3 cli.py fetch detail <code>
```

**字段**：
- 认购细节（截止日期、定价日、上市日）
- 入场费计算
- 基石投资者列表
- 公开发售股数

## CLI 完整命令

```bash
cd scripts
PYTHONPATH=. python3 cli.py <command>
```

| 命令 | 说明 |
|------|------|
| `overview` | 当前 IPO 快速一览 |
| `fetch detail <code>` | 单只股票详情 |
| `compare <code1> <code2>` | 批量对比 |
| `fetch list` | 招股列表 |
| `fetch calendar` | 按截止日分组 |
| `fetch ah <code>` | A+H 折价率 |
| `fetch history` | AAStocks 历史 |

## 缓存管理

```bash
python3 hkipo/cache.py --list    # 列出缓存
python3 hkipo/cache.py --stats   # 缓存统计
python3 hkipo/cache.py --clear   # 清除缓存
python3 hkipo/cache.py --test    # 测试缓存性能
```

### 缓存策略

| 数据类型 | TTL | 说明 |
|---------|-----|------|
| 保荐人排名 | 7 天 | 变化慢 |
| 已上市历史 | 永久 | 不会变 |
| 活跃 IPO 列表 | 24 小时 | 每日更新 |
| 单只详情 | 24 小时 | 每日更新 |
