---
name: lottery-analyzer
description: 彩票智能分析助手，支持双色球（SSQ）和大乐透（DLT）的深度数据分析、趋势预测和智能推荐。适用于：历史开奖数据统计分析、热号冷号追踪、奇偶和值走势、连号模式识别、智能号码推荐（单注/复式）、7+2/6+2复式方案生成。当用户需要分析彩票数据、生成推荐号码或查看号码热度排名时激活。
---

# 彩票分析助手

智能分析双色球和大乐透彩票数据，提供基于统计学的号码推荐和趋势分析。

## 支持彩票类型

- **双色球 (SSQ)**：6个红球(1-33) + 1个蓝球(1-16)
- **大乐透 (DLT)**：5个前区(1-35) + 2个后区(1-12)

## 快速开始

### 1. 基本分析（使用现有数据文件）

查看之前生成的分析结果：

```bash
read /home/admin/worktemp/ssq_7plus2_analysis.json  # 双色球7+2复式
read /home/admin/worktemp/lottery_ssq_analysis.json  # 最新分析
```

### 2. 分析新的开奖数据

使用核心脚本分析Excel/CSV数据文件：

```bash
python3 ~/.openclaw/skills/lottery-analyzer/scripts/analyze_lottery.py ssq /path/to/data.xlsx 7+2
```

格式说明：
- **ssq** / **dlt**：彩票类型
- **数据路径**：Excel或CSV文件路径
- **格式**：`simple`（单注）或 `7+2`（复式）

### 3. 对话式分析（推荐）

直接告诉需求，用Python脚本实时处理：

```python
# 创建分析器
from lottery_analyzer import LotteryAnalyzer

# 初始化（双色球）
analyzer = LotteryAnalyzer('ssq')

# 加载Excel数据（跳过第一行表头）
analyzer.load_data('./data.xlsx', has_header=True)

# 提取最近50期数据
analyzer.extract_numbers(50)

# 生成统计
stats = analyzer.generate_statistics()

# 生成5组7+2复式推荐
recommendations = analyzer.generate_multiple_recommendations(5, '7+2')

# 保存结果
analyzer.analysis_results = {'statistics': stats, 'recommendations': recommendations}
analyzer.save_results('./lottery_ssq_analysis.json')
```

## 数据文件格式

### Excel格式推荐

双色球Excel模板：
```csv
期号  红球号码        (表头行，可选)
26018   11  15  17  22  25  30  7
26017   1   3   5   18  29  32  4
...
```

大乐透Excel模板：
```csv
期号  前区号码    后区号码  (表头行，可选)
26018   5  12  18  25  28   3  9
26017   8  15  22  26  31   5  12
...
```

### CSV格式

```csv
期号,红1,红2,红3,红4,红5,红6,蓝
26018,11,15,17,22,25,30,7
26017,1,3,5,18,29,32,4
```

## 核心分析功能

### 1. 统计分析

获取详细统计数据：

```python
stats = analyzer.generate_statistics()

# 输出内容：
{
    'red': {
        'hot_numbers': [13, 9, 3, 5, 2, ...],   # 热号（前15）
        'cold_numbers': [21, 11, 16, ...],      # 冷号（前10）
        'avg_number': 16.0,                      # 平均数
        'median': 15.0,                          # 中位数
        'stdev': 9.8                            # 标准差
    },
    'blue': {
        'hot_numbers': [10, 4, 13, ...],
        'cold_numbers': [9, 11, 14, ...]
    },
    'sum': {
        'avg': 95.9,      # 平均和值
        'min': 46,        # 最小和值
        'max': 133        # 最大和值
    }
}
```

### 2. 模式识别

分析近期走势：

```python
patterns = analyzer.analyze_patterns(10)  # 近10期

# 输出内容：
[
    {
        'consecutive': 1,      # 连号对数
        'odd_even': '3:3',     # 奇偶比例
        'big_small': '4:2',    # 大小比例
        'sum': 120,            # 和值
        'sum_range': '101-120' # 和值区间
    },
    ...
]
```

### 3. 智能推荐

多种推荐策略：

```python
# 策略1：均衡推荐（热冷混合）
rec = analyzer.recommend_numbers(strategy='balanced', format_type='7+2')

# 策略2：热号策略（推荐高频号码）
rec = analyzer.recommend_numbers(strategy='hot', format_type='7+2')

# 策略3：冷号策略（博冷门回归）
rec = analyzer.recommend_numbers(strategy='cold', format_type='7+2')

# 策略4：连号策略（包含连号组合）
rec = analyzer.recommend_numbers(strategy='consecutive', format_type='7+2')

# 策略5：区间策略（覆盖多个数字区间）
rec = analyzer.recommend_numbers(strategy='segment', format_type='7+2')
```

## 复式方案说明

### 7+2复式（双色球）

- 组合数：C(7,6) × C(2,1) = 7 × 2 = **14注**
- 费用：14注 × 2元 = **28元**
- 覆盖范围：7个红球中任选6个，2个蓝球中任选1个

### 7+2复式（大乐透）

- 组合数：C(7,5) × C(2,2) = 21 × 1 = **21注**
- 费用：21注 × 2元 = **42元**
- 覆盖范围：7个前区中任选5个，2个后区全选

### 6+2复式（双色球）

- 组合数：C(6,6) × C(2,1) = 1 × 2 = **2注**
- 费用：2注 × 2元 = **4元**
- 覆盖范围：6个红球全选，2个蓝球中任选1个

## 完整工作流示例

### 示例1：分析双色球并生成5组推荐

```bash
# 执行分析
cd ~/.openclaw/skills/lottery-analyzer
python3 scripts/analyze_lottery.py ssq ~/worktemp/ssq1-100.xlsx 7+2

# 查看结果
cat ~/worktemp/lottery_ssq_analysis.json
```

### 示例2：对话式实时分析

```python
# 直接在对话中使用脚本
import sys
sys.path.insert(0, '/home/admin/.openclaw/skills/lottery-analyzer/scripts')
from analyze_lottery import LotteryAnalyzer

# 创建分析器
analyzer = LotteryAnalyzer('ssq')

# 加载数据
success, msg = analyzer.load_data('/home/admin/worktemp/ssq1-100.xlsx', has_header=True)

# 分析最近30期
analyzer.extract_numbers(30)

# 查看热号
print(f"热红球: {analyzer.red_freq.most_common(10)}")

# 生成推荐
recs = analyzer.generate_multiple_recommendations(5, '7+2')

# 格式化输出
for rec in recs:
    print(f"\n第{rec['group']}组: {rec['strategy']}")
    print(f"红球: {' '.join(f'{n:02d}' for n in rec['red_balls'])}")
    print(f"蓝球: {' '.join(f'{n:02d}' for n in rec['blue_balls'])}")
```

## 输出文件位置

分析结果默认保存在：

```
/home/admin/worktemp/lottery_ssq_analysis.json   # 双色球
/home/admin/worktemp/lottery_dlt_analysis.json   # 大乐透
```

## 技术依赖

- pandas（数据处理）
- numpy（数值计算）
- openpyxl（Excel支持）

依赖已预装，无需额外安装。

## 免责声明

本工具仅基于历史数据进行统计分析，**不保证中奖**。彩票本质是随机事件，请理性购彩，量力而行。

分析结果仅供娱乐和参考，切勿过度投入。

## 扩展功能

需要添加自定义分析时，直接在对话中使用Python：

```python
# 自定义分析示例
from analyze_lottery import LotteryAnalyzer

analyzer = LotteryAnalyzer('ssq')
analyzer.load_data('./data.xlsx', has_header=True)
analyzer.extract_numbers(50)

# 自定义统计：计算特定数字出现间隔
for num in range(1, 34):
    occurrences = [i for i, n in enumerate(analyzer.all_red_numbers) if n == num]
    # 计算间隔...
```

脚本完全可扩展，你可以添加任何自定义分析逻辑。
