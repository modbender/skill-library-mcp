# Stock Analysis Skill

A股市场数据分析技能，支持实时行情获取、板块筛选、股票推荐和自动定时分析。

## 功能特性

- ✅ 实时行情分析（akshare 数据源）
- ✅ 个性化股票推荐（基于用户偏好）
- ✅ 板块筛选和热点分析
- ✅ 早盘报告生成
- ✅ 定时自动分析
- ✅ 事件驱动 + 中短线策略

## 安装

```bash
pip install akshare pandas
```

## 快速开始

### 实时分析
```bash
python ~/.openclaw/skills/stock-analysis/scripts/quick_analysis.py
```

### 股票推荐
```bash
python ~/.openclaw/skills/stock-analysis/scripts/stock_recommend.py
```

### 早盘报告
```bash
python ~/.openclaw/skills/stock-analysis/scripts/morning_report.py
```

## 用户偏好

默认投资偏好：
- **关注板块**: 科技股、白酒、航天、半导体、芯片、航空
- **风险偏好**: 中等
- **投资风格**: 事件驱动、中短线
- **筛选条件**: 量比>1.5, 涨幅0-7%

## 脚本列表

| 脚本 | 用途 |
|------|------|
| `quick_analysis.py` | 快速实时分析 |
| `stock_recommend.py` | 股票推荐分析 |
| `morning_report.py` | 早盘报告生成 |
| `cron_stock_analysis.py` | 定时任务专用 |
| `final_analysis.py` | 完整分析 |

## 定时分析设置

```bash
openclaw cron add \
  --name "A股数据分析-每小时" \
  --cron "0 * * * *" \
  --tz "Asia/Shanghai" \
  --agent main \
  --message "现在是A股数据分析时间，请执行 stock-analysis 技能的定时分析脚本。" \
  --session isolated
```

## 使用示例

### 1. 实时行情分析
```
用户: 分析一下今天的行情
AI: 运行 quick_analysis.py，输出板块热点和推荐标的
```

### 2. 股票推荐
```
用户: 推荐几只科技股
AI: 运行 stock_recommend.py，输出符合条件的技术股
```

### 3. 早盘报告
```
用户: 生成早盘报告
AI: 运行 morning_report.py，输出开盘前分析
```

## 技术说明

- **数据源**: akshare (东方财富)
- **覆盖范围**: 全部 A 股
- **更新频率**: 实时
- **交易时间**: 9:30-15:00 (交易日)

## 限制

- 仅在交易日有实时数据
- 数据可能有 1-5 分钟延迟
- 需要 Python 3.8+

## 故障排查

### akshare 连接失败
```bash
pip install --upgrade akshare
```

### 编码错误
脚本已优化使用 UTF-8 编码，如仍有问题请检查终端编码设置。

## 扩展开发

编辑脚本中的 `preferences` 可自定义投资偏好：

```python
preferences = {
    'sectors': ['科技', '白酒', '航天'],  # 修改关注板块
    'risk': '中等',                        # 风险偏好
    'style': '事件驱动、中短线'            # 投资风格
}
```

## 版本历史

- **v1.0** (2026-02-16): 初始版本
  - 实时行情分析
  - 股票推荐
  - 定时分析
  - 早盘报告

## 许可

MIT License

## 支持

如有问题或建议，请查看 SKILL.md 或联系开发者。
