# 拼多多管家 - 店铺运营自动化系统

## 🎯 技能概述
整合版拼多多商家自动化管家，融合店铺运营、数据分析、竞品监控、自动定价等核心能力。

## 🔧 核心能力

### 1. 店铺运营管理
- 商品上下架自动化
- 库存同步与预警
- 订单自动处理
- 物流跟踪

### 2. 数据分析
- 销售日报/周报/月报
- 流量来源分析
- 转化率监控
- ROI 计算

### 3. 竞品监控
- 价格监控与预警
- 销量追踪
- 评价分析
- 差异化建议

### 4. 智能定价
- 成本 + 利润自动计算
- 竞品价格对比
- 动态定价策略
- 促销活动建议

### 5. 营销自动化
- 详情页自动生成
- 客服话术库
- 促销活动配置
- 评价回复模板

## 📁 文件结构
```
pinduoduo-automation/
├── SKILL.md              # 本文件
├── README.md             # 使用文档
├── config.yaml           # 配置文件
├── scripts/
│   ├── product_manager.sh    # 商品管理
│   ├── order_processor.sh    # 订单处理
│   ├── data_analyzer.sh      # 数据分析
│   ├── competitor_monitor.sh # 竞品监控
│   └── pricing_engine.sh     # 定价引擎
└── reports/              # 报告输出目录
```

## ⚙️ 快速开始

### 1. 配置店铺信息
```bash
# 编辑配置文件
nano ~/.openclaw/workspace/skills/pinduoduo-automation/config.yaml

# 填写店铺 ID、API 密钥等
```

### 2. 运行诊断
```bash
# 检查配置
pinduoduo-automation diagnose

# 测试连接
pinduoduo-automation test-connection
```

### 3. 执行任务
```bash
# 生成销售日报
pinduoduo-automation daily-report

# 监控竞品价格
pinduoduo-automation monitor-competitors

# 自动定价建议
pinduoduo-automation pricing-suggestions
```

## 📊 报告输出
- 每日销售报告：`reports/daily-YYYY-MM-DD.md`
- 竞品分析报告：`reports/competitor-YYYY-MM-DD.md`
- 定价建议报告：`reports/pricing-YYYY-MM-DD.md`

## 🔐 安全说明
- API 密钥加密存储
- 操作日志记录
- 敏感数据脱敏
- 权限最小化原则

## 💰 商业模式
- 自用：免费
- 多店铺管理：按需定制
- 数据分析报告：可对外服务

---
**版本**: 2.0.0 (整合版)
**状态**: 开发中
**优先级**: 最高
