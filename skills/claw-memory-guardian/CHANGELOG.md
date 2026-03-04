# 变更日志

所有对 Claw Memory Guardian 的显著更改都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.0.0] - 2026-02-10

### 新增
- 🎉 **初始发布** - 基于亲身"失忆"教训开发的防丢失记忆系统
- 🧠 **核心功能**：
  - 实时记忆保存和恢复
  - 自动git版本控制
  - 简单文本搜索
  - 自动备份系统
- 📁 **系统架构**：
  - 完整的记忆文件结构
  - 自动创建每日记忆文件
  - 记忆索引和时间线
- 🔧 **工具集**：
  - `memory-guardian init` - 初始化系统
  - `memory-guardian status` - 检查状态
  - `memory-guardian save` - 手动保存
  - `memory-guardian search` - 搜索记忆
  - `memory-guardian backup` - 创建备份
- 💰 **商业化**：
  - 三层定价：免费版 + 专业版$9.99/月 + 企业版$99/月
  - 功能分层：基础/高级/企业功能
  - 完整的产品文档和示例

### 技术特性
- 基于Node.js的CLI工具
- 使用标准OpenClaw技能结构
- 支持自动安装和卸载
- 完整的测试套件
- 详细的文档和示例

### 解决的问题
- 会话失忆 - 每次新会话忘记之前工作
- 任务中断 - exec命令被KILL，进度丢失
- 信息分散 - 记忆分散，缺乏统一管理
- 缺乏备份 - 没有自动备份机制
- 恢复困难 - 意外中断后无法快速恢复

### 致谢
特别感谢我们的"失忆"经历，这直接促成了这个项目的诞生。我们希望所有OpenClaw用户不再经历同样的挫折。

---

## 版本规划

### [1.5.0] - 计划中
- 语义搜索增强
- 记忆分析工具
- 团队协作功能
- 可视化时间线

### [2.0.0] - 计划中
- AI记忆优化
- 跨平台同步
- 高级报告系统
- 插件生态系统

## 更新说明

### 如何更新
```bash
# 通过ClawdHub更新
clawdhub update claw-memory-guardian

# 或手动更新
cd ~/.openclaw/skills/claw-memory-guardian
git pull origin main
```

### 向后兼容性
- 1.x版本保持API向后兼容
- 重大变更将在2.0版本引入
- 配置变更会有迁移指南

## 贡献者
- **Claw** - 主要开发
- **老板** - 产品设计和需求定义

## 许可证
MIT License - 详见 LICENSE 文件