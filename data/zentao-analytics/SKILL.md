---
name: zentao-analytics
description: 禅道任务数据分析技能。访问禅道数据库/API，分析员工任务数据（数量、工时、难度），计算工作效率和工作饱和度。使用场景：团队绩效评估、工作量分析、资源分配优化、项目进度监控。
---

# 禅道数据分析 (ZenTao Analytics)

## 🎯 核心功能

本技能用于分析禅道项目管理系统的员工任务数据，提供：

1. **任务统计** - 任务数量、类型分布、状态分布
2. **工时分析** - 预估工时 vs 实际工时、工时趋势
3. **难度评估** - 任务难度系数、复杂度分析
4. **效率计算** - 任务完成率、工时效率比
5. **饱和度分析** - 工作负载、产能利用率

## 📋 使用流程

### 1. 配置禅道连接

编辑 `references/zentao-config.md` 配置禅道 API 或数据库连接：

```bash
# API 方式（推荐）
ZENTAO_URL=https://your-zentao.com
ZENTAO_API_KEY=your_api_key

# 或数据库方式
ZENTAO_DB_HOST=localhost
ZENTAO_DB_NAME=zentao
ZENTAO_DB_USER=user
ZENTAO_DB_PASS=password
```

### 2. 运行分析

```bash
# 分析指定时间段
node scripts/analyze-tasks.js --start 2026-02-01 --end 2026-02-28

# 分析特定员工
node scripts/analyze-tasks.js --user "张三"

# 分析特定项目
node scripts/analyze-tasks.js --project "项目 A"

# 生成团队报告
node scripts/analyze-tasks.js --team-report
```

### 3. 查看报告

分析报告输出包括：

- 📊 **个人效率报告** - 每个员工的效率指标
- 📈 **团队饱和度热力图** - 工作负载可视化
- 🎯 **异常检测** - 过载/低负载员工识别
- 💡 **优化建议** - 资源分配建议

## 📐 分析指标

### 效率指标

| 指标 | 计算公式 | 说明 |
|------|----------|------|
| 任务完成率 | 完成任务数 / 总任务数 | 反映交付能力 |
| 工时效率比 | 预估工时 / 实际工时 | >1 表示高效 |
| 平均任务耗时 | 总实际工时 / 完成任务数 | 单任务平均成本 |
| 延期率 | 延期任务数 / 总任务数 | 时间管理能力 |

### 饱和度指标

| 指标 | 计算公式 | 健康范围 |
|------|----------|----------|
| 工作负载率 | 实际工时 / 标准工时 | 70%-90% |
| 任务密度 | 任务数 / 工作日 | 3-8 个/天 |
| 多任务指数 | 并行任务数 | 2-5 个 |

## 🔧 脚本说明

### analyze-tasks.js

主分析脚本，支持以下参数：

```bash
--start <date>      开始日期 (YYYY-MM-DD)
--end <date>        结束日期 (YYYY-MM-DD)
--user <name>       指定员工
--project <name>    指定项目
--team-report       生成团队报告
--output <path>     输出路径
--format <json|csv> 输出格式
```

### export-metrics.js

导出指标数据到外部系统：

```bash
# 导出到 CSV
node scripts/export-metrics.js --format csv --output ./metrics.csv

# 导出到 JSON
node scripts/export-metrics.js --format json --output ./metrics.json
```

## 📚 参考资料

- **references/zentao-config.md** - 禅道连接配置
- **references/api-schema.md** - 禅道 API 数据结构
- **references/metrics-definition.md** - 指标定义和计算逻辑

## ⚠️ 注意事项

1. **数据权限** - 确保有访问禅道数据的权限
2. **隐私保护** - 员工数据仅用于内部管理
3. **定期同步** - 建议每天同步一次数据
4. **异常处理** - 网络故障时自动重试 3 次

## 📞 故障排查

| 问题 | 解决方案 |
|------|----------|
| 连接失败 | 检查 `zentao-config.md` 配置 |
| 数据为空 | 确认日期范围和用户权限 |
| 指标异常 | 检查原始数据完整性 |

---

**版本**: 1.0.0  
**作者**: 硬石科技 AI 助手  
**更新**: 2026-03-01
