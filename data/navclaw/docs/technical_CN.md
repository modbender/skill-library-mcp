# NavClaw 技术文档

> 版本 0.1 | 目前支持导航平台：Amap（高德）

## 1. 架构概览

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  config.py  │────▶│  navclaw.py  │◀────│  wrapper.py  │
│  用户配置    │     │  核心引擎     │     │  平台对接     │
└─────────────┘     └──────┬───────┘     └──────────────┘
                           │
                    ┌──────▼───────┐
                    │  Amap API    │
                    │  geocode +   │
                    │  driving v5  │
                    └──────────────┘
```

**数据流**：config.py → PlannerConfig → RoutePlanner.run() → 3 条消息 + 日志文件

## 2. 五阶段流水线

### Phase 1: 🟢 广撒网 (Broad Search)

并发查询多种路线策略，获取尽可能多的候选路线。

- 对 `BASELINES` 中的每个策略调用 Amap 驾车路线 API
- v5 API 每次返回最多 3 条路线，v3 返回 1 条
- 默认 6 种策略 → 约 16 条原始路线

**多样性分析**：基于 `(距离, 时间, 高速里程)` 指纹判断路线唯一性，识别跨策略重复。

### Phase 2: 🟡 精筛选 (Smart Filter)

从 Phase 1 的原始路线中筛选出多样化的种子路线。

1. **去重**：相同指纹的路线只保留时间最短的
2. **相似剔除**：时间差 < `SIMILAR_DUR_THRESHOLD` 且堵长差 < `SIMILAR_RED_THRESHOLD` 的路线视为相似
3. **Top Y 筛选**：保留前 `PHASE2_TOP_Y` 条
4. **非高速保护**：至少保留 `NOHW_PROTECT` 条非高速路线

### Phase 3: 🔴 深加工 (Deep Optimization)

识别种子路线上的拥堵段，生成绕行方案。

#### 拥堵识别

```
TMC 数据 → 过滤（状态 ∈ CONGESTION_STATUSES 且长度 ≥ MIN_RED_LEN）
         → 一次合并（间距 < MERGE_GAP）
         → 二次合并（间距 < BYPASS_MERGE_GAP）
         → 最终拥堵聚合段
```

#### 绕行生成

对每个拥堵聚合段：
1. 在非高速参考路线 (s1) 上取对应区间的 33%/67% 位置点作为途经点
2. 组合不同拥堵段的途经点（单段绕行、多段同时绕行）
3. 用 `BYPASS_STRATEGIES` 中的策略查询含途经点的路线

### Phase 4: 🔄 迭代优化 (Iteration)

对 Phase 3 中最快的绕行方案再做一轮优化。

1. 取绕行方案中时间最短的 `ITER_CANDIDATES` 条
2. 对每条重新识别拥堵段
3. 在原有途经点基础上追加新途经点
4. 重新查询路线

### Phase 5: ⚓ 路线固化 (Route Anchoring)

用途经点"钉住"路线，确保用户打开导航链接时走的是规划好的路。

- 在路线 polyline 上等距取 `ANCHOR_COUNT` 个锚点
- 用这些锚点作为途经点重新查询
- 比较固化前后的时间偏移，保留最优版本

## 3. API 使用

### Geocode (地理编码)

```
GET https://restapi.amap.com/v3/geocode/geo
参数: address, key, city(可选)
```

容错策略：地址含括号时自动尝试 3 种变体（原始 / 去括号保留内容 / 去括号及内容）。

### Driving (驾车路线规划)

```
GET https://restapi.amap.com/v5/direction/driving
参数: origin, destination, strategy, show_fields, key
可选: waypoints（途经点，最多 16 个）
```

v5 API 策略编号 (strategy):

| 编号 | 名称 | 编号 | 名称 |
|------|------|------|------|
| 32 | 默认推荐 | 33 | 躲避拥堵 |
| 34 | 高速优先 | 35 | 不走高速 |
| 36 | 少收费 | 37 | 大路优先 |
| 38 | 速度最快 | 39 | 避堵+高速 |
| 40 | 避堵+不走高速 | 41 | 避堵+少收费 |
| 42 | 少收费+不走高速 | 43 | 避堵+少收费+不走高速 |
| 44 | 避堵+大路 | 45 | 避堵+速度最快 |

v3 API (兼容):

| 编号 | 名称 |
|------|------|
| 0 | 速度优先 |
| 1 | 不走高速 |
| 2 | 费用最少 |
| 3 | 距离最短 |

## 4. 配置参数说明

### 通用参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `API_KEY` | (必填) | Amap Web 服务密钥 |
| `DEFAULT_ORIGIN` | 北京南站 | 默认起点 |
| `DEFAULT_DEST` | 广州南站 | 默认终点 |
| `HOME_KEYWORD` | 家 | 终点简写，等同 DEFAULT_DEST |

### 策略参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `BASELINES` | [32,36,38,39,35,1] | Phase 1 基准策略 |
| `BYPASS_STRATEGIES` | [35,33] | Phase 3 绕行策略 |
| `BASELINE_HW_STRAT` | 39 | 高速基准策略 |

### 拥堵定义

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `CONGESTION_STATUSES` | (拥堵, 严重拥堵) | 算作"堵"的 TMC 状态 |
| `MIN_RED_LEN` | 1000m | 单段最短拥堵长度 |
| `MERGE_GAP` | 3000m | 高速拥堵合并间距 |
| `MERGE_GAP_NOHW` | 1000m | 非高速合并间距 |
| `BYPASS_MERGE_GAP` | 10000m | 二次合并间距 |

### 算法参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `PHASE2_TOP_Y` | 5 | 精筛选保留数 |
| `MAX_ITER` | 1 | 迭代轮数 (0=关闭) |
| `ANCHOR_COUNT` | 10 | 固化锚点数 |
| `API_MAX_WP` | 16 | API 最大途经点数 |

### Mattermost 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `MM_BASEURL` | (空) | Mattermost 服务器 URL |
| `MM_BOT_TOKEN` | (空) | Bot Token |
| `MM_CHANNEL_ID` | (空) | 目标频道 ID |

## 5. 高速免费期

内置 2026-2036 年免费期日历（春节、清明、劳动节、国庆），仅作提示参考。

**实际收费以 API 返回金额为准**，免费期内显示 `¥387(免费期)`，首/末日显示 `¥387(可能免费)`。

免费期定义：
- 春节：除夕 00:00 ~ 初七 24:00（8 天）
- 清明：4月3日 ~ 4月6日
- 劳动节：5月1日 ~ 5月5日
- 国庆：10月1日 ~ 10月7日

## 6. 典型 API 调用量

| 场景 | Phase 1 | Phase 3 | Phase 4 | Phase 5 | 总计 |
|------|---------|---------|---------|---------|------|
| 无拥堵 (如苏州→南京) | ~6 | 0 | 0 | ~7 | ~15 |
| 有拥堵 (如长途有堵) | ~6 | ~12 | ~4 | ~9 | ~35 |
| 严重拥堵 (多段) | ~6 | ~20 | ~6 | ~12 | ~50 |

## 许可证

[Apache License 2.0](LICENSE)
🌐 [NavClaw.com](https://navclaw.com) (Reserved Only for NavClaw GitHub Page 备用链接跳转Github，非商用目的，仅跳转)
Email: nuaa02@gmail.com