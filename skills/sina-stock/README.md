# Sina Stock Skill - A 股实时行情

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![ClawHub](https://img.shields.io/badge/ClawHub-sina--stock-blue)](https://clawhub.ai)

获取 A 股实时股票行情数据的 LobsterAI Skill，使用新浪财经 API。无需 API Key，免费使用。

## ✨ 功能特性

- 📈 **实时行情** - 获取当前价格、涨跌幅、成交量、成交额
- 📊 **大盘指数** - 上证指数、深证成指、创业板指、沪深 300 等
- 📉 **个股行情** - 支持任意 A 股股票代码查询
- 💰 **详细数据** - 开盘价、收盘价、最高价、最低价、振幅
- 🆓 **免费使用** - 无需 API Key，直接调用

## 🚀 快速开始

### 安装

通过 ClawHub 安装（推荐）：
```bash
# 在 LobsterAI 中运行
skill install sina-stock
```

或者手动安装：
```bash
# 克隆此仓库
git clone https://github.com/Sunnyfo/sina-stock.git

# 复制到 LobsterAI SKILLs 目录
cp -r sina-stock $SKILLS_ROOT/
```

### 使用示例

```bash
# 获取大盘指数
python3 "$SKILLS_ROOT/sina-stock/scripts/get_stock.py" sh000001 sz399001 sz399006

# 获取个股行情
python3 "$SKILLS_ROOT/sina-stock/scripts/get_stock.py" sh600519 sz000858

# JSON 格式输出
python3 "$SKILLS_ROOT/sina-stock/scripts/get_stock.py" sh000001 --json

# 简化输出
python3 "$SKILLS_ROOT/sina-stock/scripts/get_stock.py" sh000001 --simple
```

## 📊 支持的指数

| 名称 | 代码 | 市场 |
|------|------|------|
| 上证指数 | sh000001 | 沪市 |
| 深证成指 | sz399001 | 深市 |
| 创业板指 | sz399006 | 创业板 |
| 沪深 300 | sh000300 | 跨市场 |
| 上证 50 | sh000016 | 沪市 |
| 中证 500 | sh000905 | 跨市场 |

## 📋 输出示例

### 标准输出
```
============================================================
           A 股股市大盘实时数据
           更新时间：2026-03-02 15:00
============================================================

【上证指数 (sh000001)】
  当前价：   4151.80
  涨跌幅：   -30.79 (-0.74%)
  开盘价：   4162.88
  最高价：   4188.77
  最低价：   4131.37
  成交量：   861,579,218 手
  成交额：   1,345,892,469,395 元

============================================================
数据来源：新浪财经 API
```

### JSON 输出
```json
{
  "time": "2026-03-02 15:00:00",
  "source": "新浪财经 API",
  "count": 1,
  "data": [
    {
      "code": "sh000001",
      "name": "上证指数",
      "current": 4151.80,
      "change": -30.79,
      "change_pct": -0.74,
      "open": 4162.88,
      "prev_close": 4182.59,
      "high": 4188.77,
      "low": 4131.37,
      "volume": 861579218,
      "turnover": 1345892469395
    }
  ]
}
```

## 📖 文档

详细文档请查看：
- [SKILL.md](SKILL.md) - 完整使用文档
- [README.md](README.md) - 快速参考

## 🛠️ 开发

### 项目结构
```
sina-stock/
├── SKILL.md           # 技能文档
├── README.md          # 快速参考
├── _meta.json         # 元数据配置
└── scripts/
    └── get_stock.py   # 主脚本
```

### 本地测试
```bash
# 运行测试
python3 scripts/get_stock.py sh000001 sz399001 sz399006

# 测试 JSON 输出
python3 scripts/get_stock.py sh000001 --json
```

## 📝 注意事项

1. **交易时间**：工作日 9:30-11:30, 13:00-15:00
2. **非交易时间**：返回最后收盘价
3. **请求频率**：建议间隔 1 秒以上，避免被限流
4. **数据延迟**：实时数据，可能有秒级延迟

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🔗 相关链接

- [作者 GitHub](https://github.com/Sunnyfo)
- [LobsterAI](https://lobsterai.com/)
- [ClawHub](https://clawhub.ai/)
- [新浪财经](https://finance.sina.com.cn/)

## 📧 联系方式

如有问题或建议，请提 Issue 或联系作者。

---

**数据来源**: 新浪财经 API (https://finance.sina.com.cn/)

**免责声明**: 本工具仅供学习和研究使用，不构成投资建议。投资有风险，入市需谨慎。
