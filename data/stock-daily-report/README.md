# 📈 A 股每日投资报告 Pro

> ⚠️ **重要声明：本技能仅供个人学习和研究使用，不构成任何投资建议。股市有风险，投资需谨慎。**

## 快速开始

### 1. 安装

```bash
# 使用 clawhub 安装
clawhub install stock-daily-report
```

### 2. 配置

编辑 `config.json`：
```json
{
  "stocks": [
    {"code": "600519", "name": "贵州茅台"}
  ],
  "output_dir": "/tmp",
  "output_format": "both"
}
```

### 3. 运行

```bash
# 生成 HTML + 长图片
python3 generate_report.py --format both

# 指定股票
python3 generate_report.py --stocks 002973,600095 --format both
```

## 功能特性

- ✅ 实时股票数据（新浪财经 API）
- ✅ K 线图（嵌入 HTML，可离线查看）
- ✅ 技术指标（KDJ/MACD/量比/换手率）
- ✅ 操作建议（评级/目标价/止损价）
- ✅ 精简新闻（国际 + 国内）
- ✅ 长图片输出（方便分享）

## 输出示例

生成的 HTML/PNG 报告包含：
- 市场概览（油价、黄金、美元指数）
- 地缘政治风险提示
- 国际/国内重要新闻
- 个股深度分析（K 线图 + 技术指标 + 操作建议）

## 依赖

- Python 3.6+
- matplotlib
- pyppeteer（可选，用于图片生成）

## 许可证

MIT

---

**免责声明：本报告仅供参考，不构成投资建议。股市有风险，投资需谨慎。**
