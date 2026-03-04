---
name: stock-daily-report
description: A 股每日报告生成器 - 含 K 线图、技术指标、市场分析（仅供学习参考）
---

# 📈 A 股每日报告 Pro

> ⚠️ **重要声明：本技能仅供个人学习和研究使用，不构成任何投资建议。股市有风险，投资需谨慎。**

专业级 A 股市场报告生成器 - 支持生成 HTML 和长图片格式

## ⚠️ 免责声明

**使用本技能即表示您同意以下条款：**

1. **仅供学习参考** - 本技能生成的所有内容仅供个人学习、研究和技术交流使用
2. **不构成投资建议** - 报告中的技术分析、市场评论等内容仅供参考，不构成任何投资建议或推荐
3. **数据准确性** - 数据来源于公开 API（新浪财经），不保证数据的准确性、完整性和及时性
4. **市场风险** - 股市有风险，入市需谨慎。用户应独立判断，自行承担风险
5. **法律责任** - 因使用本技能产生的任何损失或法律纠纷，开发者不承担任何责任
6. **合规使用** - 用户应确保使用本技能符合当地法律法规和监管要求

**请勿将本技能用于：**
- 商业目的
- 非法证券咨询活动
- 任何可能违反法律法规的用途

## 功能特性

- ✅ **实时行情数据** - 从新浪财经获取实时数据
- ✅ **K 线图** - 嵌入 HTML，支持下载离线查看
- ✅ **技术指标** - KDJ、MACD、量比、换手率、振幅
- ✅ **分析参考** - 技术评级、价格区间、风险提示、仓位参考
- ✅ **精简新闻** - 国际 + 国内重要新闻
- ✅ **Base64 嵌入** - K 线图直接嵌入 HTML，无需额外文件
- ✅ **长图片输出** - 支持生成 PNG 长图，方便分享

## 安装

```bash
# 使用 clawhub 安装
clawhub install stock-daily-report
```

## 使用方法

### 方式 1：直接运行

```bash
# 生成 HTML 报告（使用默认配置）
python3 generate_report.py

# 生成 HTML + 长图片
python3 generate_report.py --format both

# 只生成图片
python3 generate_report.py --format image
```

### 方式 2：配置自选股

编辑 `config.json`：
```json
{
  "stocks": [
    {"code": "600519", "name": "贵州茅台"}
  ],
  "output_dir": "/tmp",
  "report_prefix": "stock-report",
  "output_format": "both"
}
```

### 方式 3：命令行参数

```bash
# 指定股票代码
python3 generate_report.py --stocks 002973,600095,000973

# 指定输出格式和文件
python3 generate_report.py --stocks 002973 --format both --output /tmp/my-report

# 使用配置文件
python3 generate_report.py --config /path/to/config.json
```

## 定时任务

### 方式 1：仅生成报告

编辑 crontab：
```bash
crontab -e
```

添加（交易日 9:25 生成，集合竞价后）：
```bash
25 9 * * 1-5 cd /path/to/stock-daily-report && python3 generate_report.py --format both
```

### 方式 2：生成并推送到飞书

编辑 crontab：
```bash
crontab -e
```

添加（交易日 9:25 生成并推送）：
```bash
25 9 * * 1-5 cd /path/to/stock-daily-report && python3 schedule_push.py
```

**注意：** 推送功能需要配置飞书 channel，确保 openclaw message 命令可用。

## 输出说明

生成的报告包含：

### HTML / PNG 内容
- 📰 国际新闻（2 条）
- 📋 国内新闻（2 条）
- ⚠️ 地缘政治风险提示
- 📊 市场影响概览（油价、黄金、美元指数、人民币）
- 🎯 个股深度分析（每只股票）：
  - K 线图（蜡烛图 + 均线 + 支撑/压力位）
  - 技术指标（KDJ/MACD/量比/换手率）
  - K 线形态分析
  - 操作建议（评级/目标价/止损价/仓位）

### 技术指标说明
- **KDJ**: 金叉向上/死叉向下/超买区/超卖区/震荡
- **MACD**: 金叉多头/死叉空头/金叉/死叉/粘合
- **量比**: 明显放量/温和放量/明显缩量/成交量正常
- **评级**: 强烈看好/看好/中性偏多/观望/谨慎

## 文件结构

```
stock-daily-report/
├── SKILL.md                 # 技能说明
├── generate_report.py       # 主脚本
├── auto_run.sh             # 自动运行脚本
├── config.json             # 配置文件
├── _meta.json              # ClawHub 元数据
└── README.md               # 使用说明
```

## 依赖

- Python 3.6+
- matplotlib
- pyppeteer（图片生成可选）

安装依赖：
```bash
pip install matplotlib pyppeteer
```

## 配置说明

### config.json

```json
{
  "stocks": [
    {"code": "股票代码", "name": "股票名称"}
  ],
  "output_dir": "/tmp",           // 输出目录
  "report_prefix": "stock-report", // 文件名前缀
  "output_format": "both"          // html, image, 或 both
}
```

## 常见问题

### Q: 为什么 K 线图显示乱码？
A: 确保系统安装了中文字体（如 Noto Sans CJK）。本技能已配置使用系统字体。

### Q: 图片生成失败？
A: 安装 pyppeteer：`pip install pyppeteer`，首次运行会自动下载 Chromium。

### Q: 数据不准确？
A: 数据来源于新浪财经公开 API，可能存在延迟。请以交易所官方数据为准。

### Q: 可以用于商业用途吗？
A: **不可以**。本技能仅供个人学习和研究使用。

## 许可证

MIT License

## 版本

v1.0.0 - 初始版本

---

**再次提醒：本技能仅供学习参考，不构成投资建议。投资有风险，入市需谨慎。**
