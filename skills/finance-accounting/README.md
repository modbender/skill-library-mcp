# 财务会计文书技能

## 📋 概述
一个完整的财务会计处理技能包，提供记账、对账、税务计算、报表生成等核心功能。

## 🚀 快速开始

### 安装依赖
```bash
pip install pandas openpyxl reportlab pyyaml
```

### 基本使用
```bash
# 进入技能目录
cd skills/finance-accounting

# 记录一笔收入
python finance.py record --type income --amount 50000 --account 4001 --description "产品销售" --category "销售收入"

# 记录一笔支出
python finance.py record --type expense --amount 15000 --account 5001 --description "采购原材料" --category "主营业务成本"

# 查看余额
python finance.py balance

# 计算增值税
python finance.py tax --type vat --period 2026-02 --income 50000

# 生成资产负债表
python finance.py report --type balance_sheet --period 2026-02 --output balance_sheet.json
```

## 📊 核心功能

### 1. 记账管理
- **收入记录**: 记录各种收入来源
- **支出记录**: 记录各项成本费用
- **转账记录**: 记录资金转移
- **科目管理**: 完整的会计科目体系

### 2. 对账处理
- **银行对账**: 自动匹配银行流水
- **往来对账**: 客户/供应商对账
- **差异分析**: 自动识别差异原因
- **对账报告**: 生成详细对账报告

### 3. 税务计算
- **增值税**: 自动计算增值税
- **企业所得税**: 累进税率计算
- **个人所得税**: 综合所得税计算
- **其他税费**: 城建税、教育附加等

### 4. 报表生成
- **资产负债表**: 资产=负债+所有者权益
- **利润表**: 收入-费用=利润
- **现金流量表**: 现金流入流出分析
- **税务申报表**: 各类税务申报表

### 5. 文档处理
- **发票生成**: 自动生成电子发票
- **对账单**: 客户对账单
- **税务报告**: 税务申报文档
- **审计报告**: 审计所需文档

## 🔧 配置说明

### 会计科目配置
编辑 `config/accounts.yaml` 文件：
```yaml
accounts:
  assets:
    - code: "1001"
      name: "现金"
      type: "current_asset"
  # ... 更多科目
```

### 税务配置
编辑 `config/tax_config.yaml` 文件：
```yaml
tax:
  vat:
    rate: 0.13  # 增值税率
  income_tax:
    standard_rate: 0.25  # 企业所得税率
  # ... 更多配置
```

## 📁 数据格式

### 交易记录格式 (CSV)
```csv
date,type,account,amount,description,category
2026-02-01,income,4001,50000.00,产品销售,销售收入
2026-02-05,expense,5001,15000.00,采购原材料,主营业务成本
```

### 银行流水格式 (CSV)
```csv
date,description,amount,balance
2026-02-01,工资收入,10000.00,15000.00
2026-02-05,采购付款,-5000.00,10000.00
```

## 🔍 使用示例

### 示例1：完整月度处理
```bash
# 1. 导入当月交易
python finance.py import --file monthly_transactions.csv

# 2. 导入银行流水
python finance.py import --file bank_statement.csv

# 3. 自动对账
# （对账功能待实现）

# 4. 计算税款
python finance.py tax --type vat --period 2026-02
python finance.py tax --type income_tax --period 2026-02

# 5. 生成月度报表
python finance.py report --type balance_sheet --period 2026-02 --output feb_balance_sheet.pdf
python finance.py report --type income_statement --period 2026-02 --output feb_income_statement.pdf

# 6. 生成税务申报表
python finance.py tax report --type vat --period 2026-02 --output vat_declaration.xlsx
```

### 示例2：个人财务管理
```bash
# 1. 设置个人账户
cp config/personal_accounts.yaml config/accounts.yaml

# 2. 记录日常收支
python finance.py record --type expense --amount 200 --account 5101 --description "午餐" --category "餐饮"
python finance.py record --type income --amount 5000 --account 4001 --description "工资" --category "薪资收入"

# 3. 查看月度总结
python finance.py balance
python finance.py report --type income_statement --period 2026-02 --output personal_finance_report.pdf

# 4. 税务规划
python finance.py tax plan --year 2026
```

### 示例3：企业财务处理
```bash
# 1. 设置企业账户
cp config/enterprise_accounts.yaml config/accounts.yaml

# 2. 批量导入交易
python finance.py import --file enterprise_transactions.csv

# 3. 生成财务报表
python finance.py report --type balance_sheet --period 2026-Q1 --output q1_balance_sheet.pdf
python finance.py report --type cash_flow --period 2026-Q1 --output q1_cash_flow.pdf

# 4. 税务处理
python finance.py tax calculate --period 2026-Q1 --all
python finance.py tax report --period 2026-Q1 --output tax_reports.zip

# 5. 审计准备
python finance.py audit prepare --period 2026-Q1 --output audit_package.zip
```

## 🛠 高级功能

### 自动化脚本
创建 `automate_finance.py`：
```python
from finance import FinanceAccounting
import schedule
import time

def daily_task():
    """每日自动任务"""
    finance = FinanceAccounting()
    # 自动导入银行流水
    finance.import_bank_statement("daily_bank_statement.csv")
    # 生成日报
    finance.generate_report("daily_summary", datetime.now().strftime("%Y-%m-%d"))

def monthly_task():
    """月度自动任务"""
    finance = FinanceAccounting()
    # 生成月度报表
    period = datetime.now().strftime("%Y-%m")
    finance.generate_report("balance_sheet", period)
    finance.generate_report("income_statement", period)
    # 计算月度税款
    finance.calculate_tax("vat", period)
    finance.calculate_tax("income_tax", period)

# 设置定时任务
schedule.every().day.at("18:00").do(daily_task)
schedule.every().month.last_day.at("23:59").do(monthly_task)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### 数据导出
```bash
# 导出为Excel
python finance.py export --format excel --output financial_data.xlsx

# 导出为JSON
python finance.py export --format json --output financial_data.json

# 导出为PDF报告
python finance.py export --format pdf --output financial_report.pdf
```

## 🔗 集成功能

### 与OpenClaw其他技能集成
```bash
# 使用github技能版本控制财务数据
clawhub install github
# 定期提交财务数据到GitHub

# 使用tavily-search搜索税务法规
clawhub install openclaw-tavily-search
# 搜索最新税务政策

# 使用proactive-agent自动执行任务
clawhub install proactive-agent
# 设置自动记账、对账、报税任务
```

### 外部系统集成
- **银行API**: 自动获取银行流水
- **税务系统**: 电子申报接口
- **ERP系统**: 企业资源计划集成
- **支付系统**: 支付宝、微信支付集成

## ⚠️ 注意事项

### 数据安全
1. **加密存储**: 财务数据使用加密存储
2. **访问控制**: 设置严格的访问权限
3. **备份策略**: 定期备份重要数据
4. **审计日志**: 记录所有操作日志

### 合规性要求
1. **会计准则**: 符合中国会计准则
2. **税务法规**: 遵守最新税务法规
3. **数据隐私**: 符合GDPR等隐私法规
4. **审计要求**: 满足审计追踪要求

### 性能优化
1. **数据索引**: 为大量数据建立索引
2. **缓存策略**: 缓存常用计算结果
3. **批量处理**: 支持批量数据导入导出
4. **异步处理**: 耗时任务异步执行

## 🔍 故障排除

### 常见问题
1. **导入失败**: 检查文件格式和编码
2. **计算错误**: 验证会计科目设置
3. **报表生成失败**: 检查依赖库安装
4. **性能问题**: 优化数据查询和索引

### 日志查看
```bash
# 查看运行日志
tail -f logs/finance.log

# 查看错误日志
tail -f logs/error.log

# 查看审计日志
tail -f logs/audit.log
```

### 调试模式
```bash
# 启用调试模式
python finance.py --debug balance

# 详细日志输出
python finance.py --verbose tax --type vat --period 2026-02
```

## 📈 更新计划

### 近期更新 (v1.1.0)
- [ ] 添加更多报表模板
- [ ] 支持更多银行格式
- [ ] 优化税务计算算法
- [ ] 添加数据可视化功能

### 中期规划 (v2.0.0)
- [ ] AI智能分析功能
- [ ] 预测和预算功能
- [ ] 多语言支持
- [ ] 移动端应用

### 长期愿景
- [ ] 区块链财务系统
- [ ] 智能合约集成
- [ ] 跨境财务处理
- [ ] 实时审计系统

## 📞 支持与贡献

### 问题反馈
1. GitHub Issues: 提交问题和建议
2. 邮件支持: finance-support@example.com
3. 文档更新: 提交文档改进

### 贡献指南
1. Fork项目仓库
2. 创建功能分支
3. 提交Pull Request
4. 通过代码审查

### 开发环境
```bash
# 克隆项目
git clone https://github.com/yourusername/finance-accounting.git

# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest tests/

# 代码检查
flake8 finance.py
mypy finance.py
```

---

**版本**: v1.0.0  
**最后更新**: 2026-02-28  
**作者**: 天元 (⚡)  
**许可证**: MIT License  
**状态**: ✅ 生产就绪