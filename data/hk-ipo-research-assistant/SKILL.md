---
name: hk-ipo-research-assistant
description: |
  港股 IPO 打新研究助手。抓取实时数据（孖展、基石、评级、暗盘、A+H折价、中签率），供 AI 分析判断。
  触发词：港股打新、新股分析、IPO、孖展、保荐人、暗盘、中签率、基石投资者。
  不适用：A 股打新、美股 IPO、基金申购。
---

# 港股打新研究助手

> **数据来自第三方公开网站，不构成投资建议。**

## 安装依赖

首次使用前安装 Python 依赖：

```bash
cd <skill_dir>
pip install -r scripts/requirements.txt
```

需要 Python 3.10+。

## 调用方式

所有命令通过 Python 调用：

```bash
cd <skill_dir>
python3 scripts/hkipo.py <命令> [参数]
```

以下文档中的命令（如 `overview`、`analyze 02692`）都省略了前缀，实际调用时加上 `python3 scripts/hkipo.py`。

## 快速开始

```bash
cd <skill_dir>

# 当前招股一览
python3 scripts/hkipo.py overview

# 一键分析（聚合多维度数据）
python3 scripts/hkipo.py analyze 02692

# 单只股票分项查询
python3 scripts/hkipo.py aipo ipo-brief 02692        # 基本信息
python3 scripts/hkipo.py aipo margin-detail 02692    # 孖展明细
python3 scripts/hkipo.py aipo cornerstone 02692      # 基石投资者
python3 scripts/hkipo.py aipo rating-detail 02692    # 机构评级
```

## 完整命令清单

### 概览类
| 命令 | 说明 |
|------|------|
| `overview` | 当前招股 IPO 一览（格式化输出） |
| `calendar` | 资金日历，按截止日期分组 |
| `analyze <代码>` | **一键分析**（聚合基本面+孖展+基石+评级+保荐人历史） |
| `profile` | **用户画像 + 当前 IPO 数据**（读取用户画像，输出当前 IPO 数据供 AI 分析） |

### AiPO 数据（主力数据源）
| 命令 | 说明 |
|------|------|
| `aipo margin-list` | 孖展列表（当前招股） |
| `aipo margin-detail <代码>` | 单只孖展明细（13+券商） |
| `aipo rating-list` | 新股评级列表 |
| `aipo rating-detail <代码>` | 单只评级明细（各机构打分） |
| `aipo ipo-brief <代码>` | IPO 基本信息（保荐人、发行价、市值、PE） |
| `aipo cornerstone <代码>` | 基石投资者（名单、金额、锁定期、解禁日） |
| `aipo placing <代码>` | 配售结果 |

### 暗盘数据
| 命令 | 说明 |
|------|------|
| `aipo grey-list` | 暗盘历史列表 |
| `aipo grey-today` | 今日暗盘 |
| `aipo grey-trades <代码> --date YYYY-MM-DD` | 暗盘成交明细 |
| `aipo grey-prices <代码> --date YYYY-MM-DD` | 暗盘分价表 |
| `aipo grey-placing <代码>` | 暗盘配售详情 |
| `aipo allotment` | 中签结果列表 |
| `aipo scroll` | 市场滚动消息 |

### 排名统计
| 命令 | 说明 |
|------|------|
| `aipo bookrunner-rank --start-date --end-date` | 账簿管理人排名 |
| `aipo broker-rank --start-date --end-date` | 券商参与度排名 |
| `aipo stableprice-rank --start-date --end-date` | 稳价人排名 |
| `aipo summary --year 2025` | 年度 IPO 统计 |
| `aipo performance --year 2025` | 年度表现统计 |
| `aipo by-office --year 2025` | 按注册地统计 |

### 历史数据（集思录）
| 命令 | 说明 |
|------|------|
| `jisilu list` | 历史 IPO 列表（表格） |
| `jisilu list --json` | 历史 IPO 列表（JSON） |
| `jisilu list --sponsor XX` | 按保荐人筛选 |
| `jisilu detail <代码>` | 单只历史详情 |

### 估值计算
| 命令 | 说明 |
|------|------|
| `ah compare <代码> --price <发行价> --name <名称>` | A+H 折价计算 |

### 中签率预测
| 命令 | 说明 |
|------|------|
| `odds --oversub <倍数> --price <价格>` | 中签率表格（甲/乙组各档） |
| `allotment --oversub <倍数> --price <价格>` | 单次中签率预测 |

### 其他数据源
| 命令 | 说明 |
|------|------|
| `hkex active` | 港交所活跃申请（含招股书链接） |
| `tradesmart list` | TradeSmart 数据 |
| `futu list` | 富途历史数据 |

### 市场情绪判断
| 命令 | 说明 |
|------|------|
| `hsi` | 恒生指数当日表现（大盘情绪） |
| `sponsor` | 保荐人历史排名（胜率、平均首日表现） |
| `sentiment sponsor-search --name <名称>` | 查特定保荐人战绩 |
| `etnet list` | 保荐人排名（经济通数据，备用） |
| `etnet search --name <名称>` | 查保荐人（经济通数据） |

结合以下数据综合判断：
- **大盘情绪**：HSI 涨跌反映整体风险偏好
- **保荐人战绩**：胜率 >80% 的保荐人历史表现更好
- **孖展金额**：>50亿热门，>100亿爆款
- **数据源 Fallback**：AASTOCKS 挂了自动切换 etnet

## 输出格式

- **默认 JSON**：`aipo`、`jisilu --json`、`ah compare`
- **格式化文本**：`overview`、`calendar`、`odds`、`jisilu list`
- **加 `--format table`**：aipo 命令可切换表格输出

## 分析要点

详见 `references/analysis-guide.md`，核心：
- **市场热度**：孖展 >50亿 热门，>100亿 爆款
- **基石投资者**：数量 + 质量 + 锁定期
- **保荐人**：用 `jisilu list --sponsor` 查历史战绩
- **估值**：PE 对比同行，A+H折价 >30% 有安全边际
- **中签率**：
  1. 从 `margin-detail` 获取 `oversubscription_forecast`（预测超购倍数）
  2. 用 `./hkipo odds --oversub <倍数> --price <发行价>` 生成表格
  3. 把表格给用户，让用户根据本金自己决定打几手

## 用户画像

**使用 `profile` 命令**：
1. 运行 `./hkipo profile`
2. 如果没有配置，输出会告诉你需要问用户哪些问题
3. 问用户：本金、风险偏好、是否用孖展、券商
4. 把答案写入 `scripts/config/user-profile.yaml`
5. 再次运行 `profile` 获取数据

**配置文件** (`scripts/config/user-profile.yaml`)：
```yaml
capital: 22000           # 港币
risk: conservative       # conservative/balanced/aggressive
margin: never            # never/cautious/active
broker: longbridge
```

## 详细参考

- `references/analysis-guide.md` — 分析框架详解
- `references/ipo-mechanism.md` — 机制详解（回拨、红鞋、绿鞋）
- `references/aipo-api.md` — AiPO API 完整文档
