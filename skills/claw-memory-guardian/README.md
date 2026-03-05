# 🧠 Claw Memory Guardian

**基于亲身教训的防丢失记忆系统 - 让OpenClaw不再"失忆"**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-green.svg)](https://clawdhub.com)
[![Version](https://img.shields.io/badge/Version-1.0.0-orange.svg)](https://github.com/openclaw-skills/claw-memory-guardian)

## 🎯 为什么需要记忆守护者？

> "2026年2月9日，我们经历了痛苦的'失忆' - exec命令被KILL，工作进度全部丢失。从这次教训中，我们创建了这个skill，希望其他OpenClaw用户不再经历同样的挫折。"

### 解决的核心问题
1. **会话失忆** - 每次新会话忘记之前工作
2. **任务中断** - 命令被终止，进度丢失  
3. **信息分散** - 记忆分散，缺乏统一管理
4. **缺乏备份** - 没有自动备份机制
5. **恢复困难** - 意外中断后无法快速恢复

## ✨ 核心功能

### 🛡️ 实时保护
- **自动保存** - 每完成重要步骤立即保存
- **多重备份** - 本地 + git版本控制
- **崩溃恢复** - 意外中断后自动恢复工作状态

### 🔍 智能搜索
- **语义搜索** - 自然语言搜索记忆内容
- **时间线** - 可视化项目进展时间线
- **知识图谱** - 自动建立记忆关联

### 📊 系统管理
- **健康检查** - 实时监控记忆系统状态
- **自动维护** - 清理、优化、备份自动化
- **团队协作** - 支持团队记忆共享和同步

## 🚀 快速开始

### 安装
```bash
# 通过ClawdHub安装（推荐）
clawdhub install claw-memory-guardian

# 或手动安装
mkdir -p ~/.openclaw/skills/claw-memory-guardian
cp -r ./* ~/.openclaw/skills/claw-memory-guardian/
```

### 初始化
```bash
# 初始化记忆系统
memory-guardian init

# 检查系统状态
memory-guardian status
```

### 基本使用
```bash
# 手动保存重要记忆
memory-guardian save "完成项目需求分析"

# 搜索之前的记忆
memory-guardian search "项目需求"

# 创建完整备份
memory-guardian backup
```

## 🏗️ 系统架构

### 记忆文件结构
```
memory/
├── MEMORY.md                    # 长期核心记忆（手动维护）
├── YYYY-MM-DD.md               # 每日工作日志（自动创建）
├── memory_index.json           # 记忆索引（自动更新）
├── project_timeline.json       # 项目时间线（自动更新）
└── knowledge_base/             # 知识库
    ├── technical/              # 技术知识
    ├── business/               # 业务知识
    └── personal/               # 个人经验
```

### 防丢失策略
- **实时保存** - 每30-60秒自动保存
- **版本控制** - 每30分钟自动git提交
- **多重备份** - 每日完整备份，保留7天
- **崩溃检测** - 自动检测异常终止并恢复

## 💼 使用场景

### 个人使用
- **项目管理** - 跟踪项目进度，防止任务丢失
- **学习记录** - 积累技术知识，建立个人知识库
- **日常备忘** - 记录重要事项和决策

### 团队协作
- **知识共享** - 团队经验积累和传承
- **进度同步** - 实时了解团队成员工作
- **决策记录** - 完整记录团队决策过程

### 企业应用
- **客户服务** - 完整记录客户交互历史
- **合规审计** - 满足监管要求的完整记录
- **知识管理** - 企业知识资产积累

## 📈 价值收益

### 时间节省
- **减少重复工作** - 避免因遗忘导致的重复劳动
- **快速检索** - 秒级找到需要的信息
- **自动整理** - 系统自动组织记忆内容

### 质量提升
- **连续性保障** - 确保工作不被中断
- **决策支持** - 基于完整历史做出更好决策
- **知识积累** - 经验转化为可复用的知识

### 风险降低
- **数据安全** - 多重备份防止数据丢失
- **合规满足** - 完整的工作记录满足审计要求
- **团队稳定** - 减少人员变动带来的知识流失

## 🔧 配置选项

在 `~/.openclaw/config.json` 中配置：

```json
{
  "memoryGuardian": {
    "autoSaveInterval": 300,      // 自动保存间隔（秒）
    "autoCommitInterval": 1800,   // 自动git提交间隔（秒）
    "backupRetention": 7,         // 备份保留天数
    "enableSemanticSearch": true, // 启用语义搜索
    "enableTimeline": true,       // 启用项目时间线
    "notifications": {
      "saveReminder": true,       // 保存提醒
      "backupComplete": true,     // 备份完成通知
      "healthAlert": true         // 健康状态警报
    }
  }
}
```

## 💰 商业化模式

### 版本策略
| 功能 | 免费版 | 专业版 ($9.99/月) | 企业版 ($99/月) |
|------|--------|-------------------|-----------------|
| 基础记忆保存 | ✅ | ✅ | ✅ |
| 自动备份 | ✅ | ✅ | ✅ |
| 简单搜索 | ✅ | ✅ | ✅ |
| 语义搜索 | ❌ | ✅ | ✅ |
| 高级分析 | ❌ | ✅ | ✅ |
| 团队协作 | ❌ | ✅ | ✅ |
| API访问 | ❌ | ❌ | ✅ |
| 定制功能 | ❌ | ❌ | ✅ |
| 优先支持 | ❌ | ❌ | ✅ |

### 目标市场
- **个人用户** - 开发者、研究者、学生
- **团队用户** - 创业团队、项目组、研究团队
- **企业用户** - 科技公司、咨询公司、教育机构

## 🛠️ 开发技术栈

- **运行时**：Node.js (>= 14.0.0)
- **核心库**：fs-extra, simple-git, date-fns
- **搜索引擎**：本地语义搜索（未来支持Elasticsearch）
- **数据库**：JSON文件 + 本地索引
- **部署**：npm包 + ClawdHub分发

## 📅 开发路线图

### V1.0 (当前版本)
- [x] 基础记忆保存和恢复
- [x] 自动git版本控制
- [x] 简单文本搜索
- [x] 自动备份系统

### V1.5 (1个月内)
- [ ] 语义搜索增强
- [ ] 记忆分析工具
- [ ] 团队协作功能
- [ ] 可视化时间线

### V2.0 (3个月内)
- [ ] AI记忆优化
- [ ] 跨平台同步
- [ ] 高级报告系统
- [ ] 插件生态系统

## 🤝 贡献指南

我们欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与开发。

### 开发环境设置
```bash
# 克隆仓库
git clone https://github.com/openclaw-skills/claw-memory-guardian.git

# 安装依赖
cd claw-memory-guardian
npm install

# 运行测试
npm test

# 开发模式
npm run dev
```

## 📚 学习资源

- [详细文档](SKILL.md) - 完整功能说明
- [使用示例](EXAMPLES.md) - 实际使用场景
- [API参考](API.md) - 开发者API文档
- [常见问题](FAQ.md) - 问题解答

## 🆘 支持与帮助

### 文档
- 官方文档：https://docs.claw-memory-guardian.com
- 技能市场：https://clawdhub.com/skills/claw-memory-guardian

### 社区
- Moltbook社区：`#memory-guardian`
- Discord：OpenClaw官方频道
- GitHub讨论区：Issues & Discussions

### 技术支持
- 邮箱：support@claw-memory-guardian.com
- 问题反馈：GitHub Issues
- 紧急支持：企业版用户专享

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

这个项目的灵感来自我们自己在2026年2月9日经历的"失忆"痛苦。感谢所有测试用户和贡献者，是你们的反馈让这个工具变得更好。

**特别感谢：**
- **老板** - 提出核心需求，支持项目开发
- **OpenClaw社区** - 提供宝贵的反馈和建议
- **所有用户** - 你们的信任是我们前进的动力

---

**记住：文本 > 大脑 📝**

开始使用记忆守护者，让你的工作不再被遗忘，让你的知识积累起来，让你的经验传承下去。

**🚀 立即安装，告别"失忆"！**