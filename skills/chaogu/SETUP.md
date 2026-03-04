# Stock Analysis Skill - 安装完成

## ✅ 技能已成功创建！

### 📁 技能结构

```
~/.openclaw/skills/stock-analysis/
├── SKILL.md              # 技能说明文档（AI 决策指南）
├── README.md             # 用户使用手册
├── config.json           # 配置文件
├── install.py            # 安装脚本
├── start.bat             # 快速启动脚本（Windows）
└── scripts/             # 脚本目录
    ├── quick_analysis.py      # 快速实时分析
    ├── stock_recommend.py     # 股票推荐分析
    ├── morning_report.py     # 早盘报告生成
    ├── cron_stock_analysis.py # 定时任务专用
    ├── final_analysis.py      # 完整分析
    ├── recommend.py          # 推荐筛选
    ├── recommend2.py         # 推荐筛选（放宽条件）
    ├── recommend3.py         # 推荐筛选（按名称搜索）
    ├── test_akshare.py       # akshare 测试
    ├── check_columns.py      # 检查数据列
    ├── check_sectors.py      # 检查板块分类
    ├── simple_analysis.py    # 简化分析
    ├── analyze.py           # 分析脚本
    └── quick_check.py       # 快速检查
```

---

## 🚀 快速开始

### 方法1：运行安装脚本（推荐）

```bash
python ~/.openclaw/skills/stock-analysis/install.py
```

### 方法2：直接运行脚本

```bash
# 实时分析
python ~/.openclaw/skills/stock-analysis/scripts/quick_analysis.py

# 股票推荐
python ~/.openclaw/skills/stock-analysis/scripts/stock_recommend.py

# 早盘报告
python ~/.openclaw/skills/stock-analysis/scripts/morning_report.py
```

### 方法3：使用启动脚本（Windows）

```bash
start.bat
```

---

## 📊 功能概览

| 功能 | 脚本 | 说明 |
|------|------|------|
| **实时行情分析** | `quick_analysis.py` | 快速获取市场数据 |
| **股票推荐** | `stock_recommend.py` | 基于偏好推荐 |
| **早盘报告** | `morning_report.py` | 开盘前分析 |
| **定时分析** | `cron_stock_analysis.py` | 自动定时分析 |
| **完整分析** | `final_analysis.py` | 全部指标 |

---

## ⚙️ 用户配置

默认投资偏好存储在 `config.json`：

```json
{
  "user_preferences": {
    "investment": {
      "sectors": ["科技", "白酒", "航天", "半导体", "芯片", "航空"],
      "risk_level": "中等",
      "style": "事件驱动、中短线",
      "filter_conditions": {
        "volume_ratio_min": 1.5,
        "change_percent_min": 0,
        "change_percent_max": 7
      }
    }
  }
}
```

**修改配置**：直接编辑 `config.json` 文件

---

## 📋 主要功能详解

### 1. 实时行情分析

**脚本**: `quick_analysis.py`

**功能**:
- 获取实时 A 股行情
- 涨幅前 10 名
- 量比 > 2 的股票
- 用户偏好板块表现
- 板块平均涨幅

**运行**:
```bash
python ~/.openclaw/skills/stock-analysis/scripts/quick_analysis.py
```

---

### 2. 股票推荐

**脚本**: `stock_recommend.py`

**功能**:
- 根据用户偏好筛选
- 量比 > 1.5，涨幅 0-7%
- 板块热点分析
- 操作建议

**运行**:
```bash
python ~/.openclaw/skills/stock-analysis/scripts/stock_recommend.py
```

---

### 3. 早盘报告

**脚本**: `morning_report.py`

**功能**:
- 涨幅前 10 且量比 > 2
- 板块平均涨幅 TOP 10
- 偏好板块表现
- 市场整体概况

**运行**:
```bash
python ~/.openclaw/skills/stock-analysis/scripts/morning_report.py
```

---

### 4. 定时自动分析

**脚本**: `cron_stock_analysis.py`

**功能**:
- 每小时自动运行
- 板块热点
- 推荐标的
- 操作建议

**设置定时任务**:
```bash
openclaw cron add \
  --name "A股数据分析-每小时" \
  --cron "0 * * * *" \
  --tz "Asia/Shanghai" \
  --agent main \
  --message "现在是A股数据分析时间，请执行 stock-analysis 技能的定时分析脚本。" \
  --session isolated
```

---

## 🎯 使用场景

### 场景1：开盘前分析

```
时间: 9:00
操作: 运行 morning_report.py
目的: 了解当日热点，准备交易
```

### 场景2：盘中实时监控

```
时间: 10:30, 11:30, 14:00, 14:30
操作: 运行 quick_analysis.py
目的: 跟踪市场变化，调整策略
```

### 场景3：选股

```
时间: 任意时间
操作: 运行 stock_recommend.py
目的: 根据偏好筛选标的
```

### 场景4：自动监控

```
设置: 每小时自动分析
目的: 不需要手动操作，自动获取推荐
```

---

## ⚠️ 重要提示

### 交易时间

- **交易日**: 周一至周五
- **交易时间**: 9:30 - 15:00
- **数据更新**: 实时（可能有 1-5 分钟延迟）

### 风险管理

- **仓位控制**: 单只股票不超过 20%
- **止损设置**: 建议设置 -7% 止损
- **分批建仓**: 建议 2-3 次买入

### 技术要求

- Python 3.8+
- 已安装 akshare 和 pandas
- 网络连接正常

---

## 🔧 故障排查

### 问题1: akshare 连接失败

**解决方案**:
```bash
pip install --upgrade akshare
```

### 问题2: 编码错误

**解决方案**:
脚本已优化使用 UTF-8 编码，如仍有问题请检查终端编码设置。

### 问题3: 无数据返回

**可能原因**:
- 非交易时间（周末、节假日）
- 市场维护期间
- akshare API 变更

**解决方案**:
- 确认当前时间是否为交易日 9:30-15:00
- 等待交易时间再运行
- 更新 akshare

---

## 📚 相关文档

- **SKILL.md**: 详细的 AI 决策指南和使用说明
- **README.md**: 快速开始指南
- **config.json**: 配置文件说明

---

## 📞 支持

如有问题或建议，请：
1. 查看 SKILL.md 文档
2. 检查 config.json 配置
3. 运行 install.py 重新安装依赖

---

## 🎉 开始使用

```bash
# 运行安装脚本
python ~/.openclaw/skills/stock-analysis/install.py

# 或直接开始分析
python ~/.openclaw/skills/stock-analysis/scripts/quick_analysis.py
```

---

**技能版本**: v1.0
**创建日期**: 2026-02-16
**最后更新**: 2026-02-16

祝你投资顺利！📈
