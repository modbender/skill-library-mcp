# 金融分析技能 (Financial Analysis Skill)

## 概述
这是一个用于投资组合分析的技能，支持从免费API获取各类资产行情数据，并提供文字报告和图表可视化。优化版本整合了滚动窗口调仓逻辑和回测功能。

## 功能特性
- ✅ 投资组合分析（资产配置、风险评估、收益分析）
- ✅ 支持多种资产类型：股票、ETF、加密货币等
- ✅ 免费数据源集成（yfinance）
- ✅ 文字报告生成
- ✅ 图表可视化（收益曲线、资产分布、相关性热力图）
- ✅ 风险指标计算（波动率、最大回撤、夏普比率）
- ✅ 支持CSV数据导入（自动处理百分比单位转换）
- ✅ 风险平价组合分析（各资产风险贡献均衡）
- ✅ **滚动窗口风险平价分析**（使用历史一年数据，每月调仓）
- ✅ **避免未来数据**（使用expanding窗口计算波动率）
- ✅ **回测功能**（完整的回测流程）

## 安装依赖

### 1. 安装Python依赖
```bash
pip install pandas numpy matplotlib seaborn
```

### 2. 安装技能
```bash
# 将技能复制到OpenClaw技能目录
cp -r financial-analysis-skill ~/.openclaw/skills/
```

## 使用方法

### 1. 基本使用

#### 运行回测分析
```bash
python optimized_main.py --csv "C:\path\to\marketdata.csv" --output ./backtest_output
```

#### 使用默认数据路径
```bash
python optimized_main.py
```

#### 自定义输出目录
```bash
python optimized_main.py --output ./my_backtest
```

### 2. 查看分析结果

#### 显示分析报告
```bash
python optimized_main.py --show-report
```

#### 显示分析指标
```bash
python optimized_main.py --show-metrics
```

#### 显示资产权重
```bash
python optimized_main.py --show-weights
```

### 3. 直接使用技能类

```python
from optimized_risk_parity_skill import OptimizedRiskParitySkill

# 创建技能实例
skill = OptimizedRiskParitySkill('C:\path\to\marketdata.csv')

# 运行回测
result = skill.run_backtest('C:\path\to\marketdata.csv', './backtest_output')

# 获取报告
report = skill.get_report()
print(report)

# 获取指标
metrics = skill.get_metrics()
print(f"总收益率: {metrics['total_return']*100:.2f}%")
print(f"夏普比率: {metrics['sharpe_ratio']:.2f}")

# 获取权重
weights = skill.get_weights()
for asset, weight in weights.items():
    print(f"{asset}: {weight*100:.2f}%")
```

## 数据格式要求

### CSV文件格式
- 第0行：资产名称（如：CFFEX5五年期国债期货）
- 第1行：数据类型（如：涨跌幅(%)）
- 第2行开始：实际数据
  - 第1列：日期
  - 第2-5列：各资产收益率（百分比格式）

### 示例数据
```
日期,TF.CFE,T.CFE,CU.SHF,AU.SHF
2015-03-20,0.1377,NaN,0.767,-0.1472
2015-03-23,-0.1834,-0.0721,3.9248,1.1373
2015-03-24,-0.0510,-0.1031,0.3662,0.4165
```

## 滚动窗口风险平价分析

### 核心特点
1. **避免未来数据**：使用历史一年数据计算波动率
2. **动态调仓**：每月根据最新波动率重新计算权重
3. **风险平价**：各资产对组合风险贡献相等
4. **回测验证**：完整的回测流程，验证策略效果

### 分析流程
1. **数据加载**：加载CSV数据，处理百分比单位
2. **滚动波动率**：使用expanding窗口计算历史波动率
3. **权重计算**：基于波动率倒数计算风险平价权重
4. **投资组合收益率**：使用滚动权重计算每日收益率
5. **绩效评估**：计算总收益率、年化收益率、夏普比率等
6. **可视化**：生成收益曲线、资产配置、相关性等图表

### 输出文件
- **分析报告**：`rolling_risk_parity_report.txt`
- **详细数据**：`rolling_risk_parity_data.json`
- **可视化图表**：
  - `rolling_risk_parity_returns.png` - 收益曲线图
  - `rolling_risk_parity_allocation.png` - 资产配置饼图
  - `rolling_risk_parity_correlation.png` - 相关性热力图
  - `rolling_asset_returns_comparison.png` - 资产收益对比图
  - `rolling_weight_changes.png` - 滚动权重变化图

## 报告内容
- 投资组合概览
- 收益分析（总收益、年化收益）
- 风险指标（波动率、最大回撤、夏普比率）
- 资产配置分析
- 相关性分析
- 滚动权重变化
- 可视化图表
- 投资建议

## 示例输出

### 分析报告
```
中国市场滚动风险平价组合分析报告
============================================================
生成时间: 2026-02-26 10:25:00
数据来源: C:\Users\wu_zhuoran\.openclaw\workspace\data\marketdata.csv
数据时间范围: 2015-03-23 至 2026-02-25
数据点数: 2656
滚动窗口: 252个交易日（约1年）
调仓频率: 每月

平均投资组合配置:
  五年期国债 (TF.CFE): 46.04% (波动率: 2.46%)
  十年期国债 (T.CFE): 32.55% (波动率: 3.61%)
  沪铜 (CU.SHF): 9.33% (波动率: 17.87%)
  沪金 (AU.SHF): 12.09% (波动率: 14.88%)

收益指标:
  总收益率: 44.78%
  年化收益率: 3.57%

风险指标:
  年化波动率: 3.76%
  最大回撤: -9.48%
  夏普比率: 0.42
```

## 技术实现

### 滚动窗口计算
- 使用`expanding()`窗口而非`rolling()`窗口
- 确保不使用未来数据
- 最小窗口大小为252个交易日（约1年）

### 权重计算
- 基于波动率倒数加权：`权重 = (1/波动率) / ∑(1/波动率)`
- 每月调仓，动态调整权重
- 使用前一天的权重计算当日收益率

### 回测验证
- 完整的回测流程
- 避免数据泄露
- 提供详细的绩效指标

## 注意事项
- 确保数据质量，处理缺失值和异常值
- 滚动窗口大小可根据实际情况调整
- 调仓频率可根据市场情况调整
- 考虑交易成本对回测结果的影响

## 许可证
MIT License

## 贡献
欢迎提交Issue和Pull Request！

## 联系方式
如有问题，请在项目仓库提交Issue。
