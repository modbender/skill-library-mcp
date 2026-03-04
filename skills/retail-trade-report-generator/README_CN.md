# Retail Trade Weekly Report Generator - 使用指南

## 📁 文件清单

1. **retail_trade_weekly_report_SKILL.md** - 完整的Skill文档（技术规格）
2. **retail_trade_report_generator.py** - Python实现代码
3. **store_mapping.csv** - Store到Region的映射表
4. **README_CN.md** - 本使用指南

## 🚀 快速开始

### 1. 准备输入文件

确保你有**12个Excel文件**（6个本周 + 6个上周）：

**本周文件示例（1月11-17日）：**
- `DRP_Channel_Sales_Report_DRP_1_11-1_17.xlsx`
- `DRP_Special_SIM_Monitor_Report_Daily_TECNO_1_11-1_17.xlsx`
- `License_Store_Performance_Monitor_Report_LS_1_11-1_17.xlsx`
- `DXS_Acquisition_Report_Mobile_Prepaid_1_11-1_17.xlsx`
- `DXS_Acquisition_Report_Mobile_Postpaid_1_11-1_17.xlsx`
- `DXS_Acquisition_Report_FWA_1_11-1_17.xlsx`

**上周文件示例（1月4-10日）：**
- `DRP_Channel_Sales_Report_DRP_1_04-1_10.xlsx`
- `DRP_Special_SIM_Monitor_Report_Daily_TECNO_1_04-1_10.xlsx`
- `License_Store_Performance_Monitor_Report_LS_1_04-1_10.xlsx`
- `DXS_Acquisition_Report_Mobile_Prepaid_1_04-1_10.xlsx`
- `DXS_Acquisition_Report_Mobile_Postpaid_1_04-1_10.xlsx`
- `DXS_Acquisition_Report_FWA_1_04-1_10.xlsx`

### 2. 运行脚本

```python
from retail_trade_report_generator import generate_weekly_report

# 设置路径
input_dir = "/path/to/your/excel/files/"
mapping_csv = "/path/to/store_mapping.csv"
output_path = "/path/to/output/Retail_Trade_Weekly_Report.xlsx"

# 生成报告
report_path = generate_weekly_report(input_dir, mapping_csv, output_path)
print(f"报告已生成：{report_path}")
```

### 3. 查看输出

生成的Excel文件包含5个主要部分：
- Mobile Prepaid（按区域）
- DRP Prepaid Program（按区域）
- Mobile Postpaid（按区域）
- FWA 4G（按区域）
- FWA 5G（按区域）

每个部分都包含：
- 本周ADA数据
- WoW（周环比）
- 按渠道拆分（DRP、DXS、LS）
- 颜色标注（绿色=增长，红色=下降）

## 📊 输出示例

### Mobile Prepaid 表格结构
```
Region | RT Total ADA | WoW  | DXS ADA | WoW  | LS ADA | WoW  | DRP ADA | WoW
--------|-------------|------|---------|------|--------|------|---------|-----
NCR    | 337         | 21%  | 163     | 16%  | 8      | 51%  | 166     | 25%
SLZ    | 401         | 6%   | 64      | -13% | 28     | -17% | 310     | 14%
...
Total  | 1,876       | 6%   | 508     | -7%  | 227    | 18%  | 1,141   | 11%
```

## 🔧 自定义配置

### 修改Store映射

编辑 `store_mapping.csv` 文件：

```csv
Store Name,Region,Aliases
New Store Name,NCR,"Alias1|Alias2|Alias3"
```

**注意事项：**
- Aliases用 `|` 分隔
- 大小写不敏感（自动转换）
- 支持模糊匹配

### 调整区域列表

如需修改区域，编辑 `retail_trade_report_generator.py` 中的：

```python
REGIONS = ['NCR', 'SLZ', 'NLZ', 'CLZ', 'EVIS', 'WVIS', 'MIN', 'Others']
```

## 📋 数据映射关系

### Mobile Prepaid
| 指标 | 来源文件 | 字段 |
|-----|---------|-----|
| DRP ADA | DRP_Channel_Sales_Report | Column 5: MOBILE PREPAID > TOTAL ACTIVATION |
| DXS ADA | DXS_Acquisition_Report_Mobile_Prepaid | Column 4: Total（按Store汇总到Region）|
| LS ADA | License_Store_Performance_Monitor_Report | Column 1: Mobile Prepaid（按Store汇总到Region）|

### Mobile Postpaid
| 指标 | 来源文件 | 字段 |
|-----|---------|-----|
| DRP ADA | DRP_Channel_Sales_Report | Column 1: MOBILE POSTPAID > TOTAL ACTIVATION |
| DXS ADA | DXS_Acquisition_Report_Mobile_Postpaid | Column 12: Total |
| LS ADA | License_Store_Performance_Monitor_Report | Column 3: Mobile Postpaid |

### FWA 4G
| 指标 | 来源文件 | 字段 |
|-----|---------|-----|
| DRP ADA | DRP_Channel_Sales_Report | Column 9: 4G WiFi 980 SIM_Sum |
| DXS ADA | DXS_Acquisition_Report_FWA | Column 1: DITO Home Prepaid 4G WiFi 980 |
| LS ADA | License_Store_Performance_Monitor_Report | Column 29 (AD): DITO Home Prepaid 4G WiFi 980 SIM |

### FWA 5G
| 指标 | 来源文件 | 字段 |
|-----|---------|-----|
| DRP ADA | DRP_Channel_Sales_Report | Column 10 + Column 11（求和）|
| DXS ADA | DXS_Acquisition_Report_FWA | Total - 4G列 |
| LS ADA | License_Store_Performance_Monitor_Report | Unli 5G + WiFi 4990（求和）|

### DRP Prepaid Program
| 指标 | 来源文件 | 字段 |
|-----|---------|-----|
| Double Data ADA | DRP_Channel_Sales_Report | Column 6: Double Data_Sum |
| CAMON 40 | DRP_Special_SIM_Monitor_Report_Daily_TECNO | Column 1: CARMON Activation |
| POVA 7 | DRP_Special_SIM_Monitor_Report_Daily_TECNO | Column 2: POVA Activation |
| TECNO ADA | 计算字段 | CAMON 40 + POVA 7 |

## ⚙️ WoW计算公式

```python
WoW = (本周值 - 上周值) / 上周值 × 100%

# 特殊情况：
# - 上周值 = 0：显示 "-"
# - 本周值 = 0 且 上周值 > 0：显示 "-100%"
# - 格式化为整数百分比（如 "21%"、"-13%"）
```

## 🎨 颜色编码

- **绿色（粗体）**: WoW > 0%（增长）
- **红色（粗体）**: WoW < 0%（下降）
- **黑色**: WoW = 0%（持平）
- **灰色**: WoW = "-"（无法计算）

## ❗ 常见问题

### Q1: "Expected 6 current week files, found X"
**A:** 检查文件命名和日期格式，确保有完整的6个文件，且日期能被正确识别。

### Q2: Store没有匹配到Region
**A:** 检查 `store_mapping.csv`，添加缺失的Store或其别名。未匹配的Store会自动归类到 "Others"。

### Q3: WoW显示异常
**A:** 检查上周和本周文件的日期范围，确保上周日期早于本周。

### Q4: 某个Region的数据为0
**A:** 检查原始Excel文件中该Region是否有数据，或Store映射是否正确。

### Q5: 数值精度问题
**A:** 小于10的值显示1位小数，大于等于10的值显示整数。

## 📞 技术支持

如需修改计算逻辑或添加新功能，请参考：
- `retail_trade_weekly_report_SKILL.md` - 完整技术文档
- `retail_trade_report_generator.py` - 源代码（有详细注释）

## 📝 更新日志

### v1.0 (2026-02-02)
- ✅ 初始版本发布
- ✅ 支持12个Excel文件自动识别和分组
- ✅ WoW计算和颜色标注
- ✅ Store到Region映射（支持别名和模糊匹配）
- ✅ 5个产品类型的完整报表
- ✅ 自动格式化和边框样式

## 🔮 未来功能（可选）

- [ ] 添加图表（柱状图、折线图）
- [ ] 支持导出为PDF
- [ ] 自动发送邮件报告
- [ ] 历史趋势分析（多周对比）
- [ ] 数据异常检测和预警

---

**如有任何问题或建议，请联系技术团队。**
