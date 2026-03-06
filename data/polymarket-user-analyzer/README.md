# Polymarket User Analyzer Skill

## 📊 功能

分析任何 Polymarket 用户的交易策略和表现，生成详细的策略报告。

## ✨ 特性

- 从用户名自动提取钱包地址
- 获取完整交易历史
- 分析交易模式和策略特征
- 计算盈利表现和 ROI
- 识别策略类型（价值投资、动量交易、套利等）

## 📦 安装

1. 下载 `polymarket-user-analyzer.skill` 文件
2. 在 OpenClaw 中安装：
   ```bash
   openclaw skills install polymarket-user-analyzer.skill
   ```

## 🚀 使用方法

```bash
# 分析用户（通过用户名）
node scripts/analyze_user.js @vague-sourdough

# 分析用户（通过钱包地址）
node scripts/analyze_user.js 0x8c74b4eef9a894433B8126aA11d1345efb2B0488

# 保存详细报告
node scripts/analyze_user.js @username --output report.json

# 获取更多交易记录
node scripts/analyze_user.js @username --limit 200
```

## 📈 分析指标

- **基本统计**: 交易次数、总投入、平均仓位
- **市场偏好**: 市场类型分布、资产分布
- **交易模式**: 方向偏好、入场价格分析、仓位管理
- **表现指标**: 总盈亏、ROI、胜率
- **策略分类**: 自动识别策略类型

## 🔒 隐私说明

本工具仅分析公开的链上数据。Polymarket 的所有交易都是公开的，任何人都可以查看。

本工具：
- ✅ 不访问私人信息
- ✅ 不需要认证
- ✅ 不存储或传输数据到外部服务器
- ✅ 不违反任何服务条款

## 📝 示例输出

```
======================================================================
📊 Polymarket Strategy Analysis: @vague-sourdough
======================================================================

【Overview】
Wallet: 0x8c74b4eef9a894433B8126aA11d1345efb2B0488
Total Trades: 25
Capital Deployed: $125.00
Average Position: $5.00
Position Sizing: Fixed

【Strategy Classification】
Type: Systematic Scalper (fixed size, high frequency)

【Market Focus】
  Short-term Crypto: 25 trades (100.0%)

【Performance】
Total Invested: $125.00
Total Redeemed: $252.39
Net P&L: $127.39
ROI: 101.91%
======================================================================
```

## 🎯 使用场景

- 学习成功交易者的策略
- 研究市场参与者行为
- 验证声称的交易表现
- 开发自己的交易策略
- 分析市场情绪和定位

## 📄 License

MIT

## 🙏 致谢

感谢 Polymarket 提供公开的数据 API。
