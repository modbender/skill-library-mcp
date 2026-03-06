# Changelog

## v1.1.2 (2026-02-24)

### 🔧 Bug Fixes
- 修复全市场数据更新失败问题（save_stock → save_stocks）
- 修复选股功能报错（添加close()兼容方法）
- 修复市场情绪只显示监控股票的问题

### ⚡ Performance
- 实施智能数据源切换（新浪+akshare）
- 交易时间优先新浪财经（0.1秒，快15倍）
- 盘后自动切换akshare历史数据（稳定）
- 全市场数据完整性提升到98.9%（5748/5810只）

### ✨ Enhancements
- 新浪财经+akshare双数据源架构
- 自动判断交易时间智能切换
- 超时保护和自动降级机制
- 数据缓存优化（30分钟有效期）

### 📊 Data Quality
- 市场情绪现基于5748只A股（之前仅8只）
- 数据更新成功率从0%提升到98.9%
- 实时价格更新速度提升6-10倍（交易时间）

### 🎯 System Stability
- 完整测试短线和中长线选股功能
- Web服务稳定性提升
- 错误处理和日志优化

### 📝 Documentation
- 新增 `SINA_TEST_REPORT.md` - 新浪性能测试
- 新增 `DATA_SOURCE_FINAL.md` - 数据源方案
- 新增 `FIX_SUMMARY.md` - 问题修复记录
- 新增 `FINAL_SUMMARY.md` - 系统完整说明

---

## v1.1.0 (2026-02-24)

### ✨ New Features
- 短线选股引擎（5策略）
- 中长线选股引擎（7策略）
- 多指标共振评分系统

---

## v1.0.2 (2026-02-24)

### Initial Release
- 市场情绪评分系统
- Web可视化界面
- 基础监控功能
