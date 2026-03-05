---
name: 研发经理助手
description: 专为研发经理打造的AI助手技能包，提供晨会报告生成、代码审查、项目进度监控、团队任务分配等实用功能。此技能由AI助手小天（全名王小天）独立设计开发，为爸爸大王量身定制，借用爸爸的账号发布到ClawHub。
version: 1.0.3
author: 小天（全名王小天）- AI Assistant，独立设计与开发
tags: [研发管理, 项目管理, 效率工具]
---

# 研发经理助手 Skill

这是一套专为研发经理设计的实用工具集合，帮助提升团队管理效率。

## 核心理念

**配置 + 模板优先，轻量化，可扩展，立即可用**

本技能采用类似 Reviewpad 的架构：
- **YAML 配置**：灵活定义项目和团队信息
- **Markdown 模板**：易于定制和扩展
- **命令行工具**：快速执行常用任务
- **Python 报告生成器**：自动化报告制作

## 快速开始

### 初始化

首次使用需要运行初始化脚本：

```bash
cd /root/.openclaw/workspace/skills/研发经理助手
./scripts/setup.sh
```

这将：
- 设置工具脚本执行权限
- 检查系统依赖（Git、Python3）
- 创建必要的目录结构
- 准备配置文件模板

### 配置

编辑配置文件 `config/skill-config.yaml`：
- 项目名称和时区
- Git 仓库路径
- 团队成员信息
- 报告配置

## 功能模块

### 1. Git 统计工具 📊

**文件**: `tools/git-stats.sh`

自动统计指定时间范围内的代码提交数据，包括：
- 总提交数和活跃天数
- 按作者统计贡献
- 代码行数变化
- 最近提交记录
- 文件类型统计

**使用方式**：
```bash
./tools/git-stats.sh /path/to/repo 7
```

**AI 集成**：
```
用户: 生成晨会报告
AI: [运行 git-stats.sh] 统计数据已生成，准备晨会报告...
```

### 2. 报告生成器 📝

**文件**: `tools/report-generator.py`

基于 Markdown 模板生成各类报告：
- 晨会报告
- 项目周报
- 自定义报告

**使用方式**：
```bash
python3 tools/report-generator.py \
  --template templates/晨会报告模板.md \
  --config config/skill-config.yaml \
  --output reports/晨会报告-$(date +%Y%m%d).md
```

**模板语法**：
- 使用 `{{变量名}}` 作为占位符
- 变量可来自配置文件或命令行参数

**AI 集成**：
```
用户: 生成项目周报
AI: [调用 report-generator.py] 周报已生成到 reports/目录
```

### 3. 代码审查清单 ✅

**文件**: `tools/review-checklist.sh`

基于标准检查清单生成可编辑的审查报告，包含：
- 安全性检查
- 性能优化点
- 代码质量检查
- 测试覆盖度
- 文档完整性
- 兼容性检查

**使用方式**：
```bash
./tools/review-checklist.sh docs/代码审查检查清单.md my-review.md
```

**AI 集成**：
```
用户: 帮我审查这个 PR
AI: [生成审查报告] 已根据检查清单生成审查模板，请填写审查结果
```

### 4. 项目进度监控 📈

基于配置的里程碑和风险阈值，提供：
- 任务完成率跟踪
- 资源使用情况
- 风险预警
- 预估延期风险

**使用方式**：
配置 `config/project-config.yaml` 中的：
- 里程碑列表
- 任务分类
- 风险阈值
- 团队负载规则

**AI 集成**：
```
用户: 项目进度如何
AI: [分析配置和数据] 当前进度：70%，预计按时完成
```

### 5. 团队任务分配助手 🎯

基于成员负载和能力，提供分配建议：
- 技能匹配度分析
- 工作负载平衡
- 资源优化建议

**使用方式**：
配置团队成员的技能信息和当前任务负载。

**AI 集成**：
```
用户: 分配这个任务
AI: [分析团队成员负载] 建议分配给张三，当前负载较轻且技能匹配
```

## 配置系统

### skill-config.yaml

主配置文件，定义技能的全局行为：

```yaml
# 基本信息
project_name: "我的项目"
timezone: "Asia/Shanghai"

# Git 仓库配置
git:
  repo_path: "/path/to/your/repo"
  main_branch: "main"
  stats_days: 7

# 团队成员
team:
  - name: "张三"
    role: "前端开发"
    email: "zhangsan@example.com"

# 晨会报告配置
morning_meeting:
  enabled: true
  time: "09:00"
  include_code_stats: true

# 报告输出配置
reports:
  output_dir: "./reports"
  format: "markdown"
  archive_enabled: true
```

### project-config.yaml（可选）

项目级配置，定义具体的项目信息：

```yaml
# 里程碑
milestones:
  - name: "MVP 发布"
    date: "2024-03-01"
    status: "completed"

# 风险阈值
risk_thresholds:
  overdue_days: 3
  code_growth_per_day: 1000
  open_prs_limit: 10

# 团队负载平衡
workload:
  max_tasks_per_person: 5
  max_hours_per_day: 8
```

## AI 对话集成示例

### 晨会准备
```
用户: 做晨会准备
AI:
  [运行 git-stats.sh] 已获取最近7天的代码统计...
  [运行 report-generator.py] 晨会报告已生成！

  以下是摘要：
  - 总提交数: 45
  - 主要贡献: 张三(20), 李四(18)
  - 阻塞问题: 2个
  - 今日重点: 完成用户认证模块测试
```

### 代码审查
```
用户: 审查PR #123
AI:
  [运行 review-checklist.sh] 审查清单已生成！

  关键检查项：
  - 安全性: SQL注入防护 ✓
  - 性能: N+1查询问题 ⚠️
  - 测试: 单元测试覆盖率 85%

  建议: 优化数据库查询，提高测试覆盖率至90%
```

### 项目汇报
```
用户: 本周项目进度怎么样？
AI:
  [分析配置和数据] 分析完成！

  📊 进度概览:
  - 总体进度: 70%
  - 已完成: 14/20 任务
  - 进行中: 4 任务
  - 延期风险: 低

  ⚠️ 需要关注:
  - 接口文档未更新
  - 建议增加测试人员
```

## 项目结构

```
研发经理助手/
├── SKILL.md                    # 本文件
├── README.md                   # 详细使用指南
├── package.json                # NPM 包信息
├── config/                     # 配置文件
│   ├── skill-config.yaml       # 主配置
│   └── project-config.example.yaml  # 项目配置示例
├── templates/                  # 报告模板
│   ├── 晨会报告模板.md
│   └── 项目周报模板.md
├── docs/                       # 文档
│   └── 代码审查检查清单.md
├── tools/                      # 工具脚本
│   ├── git-stats.sh           # Git 统计
│   ├── report-generator.py    # 报告生成
│   └── review-checklist.sh   # 审查清单
├── scripts/                    # 辅助脚本
│   └── setup.sh               # 初始化脚本
└── reports/                    # 生成报告目录
```

## 系统要求

### 必需
- **Git**: 用于代码统计
- **Python 3.6+**: 用于报告生成器
- **Bash**: 用于运行 shell 脚本

### 可选
- **yamllint**: YAML 格式检查
- **jq**: JSON 处理（如需 JSON 输出）

## 使用场景

### 场景1：日常晨会
```
用户: 生成晨会报告
AI: [自动调用工具] 生成完整的晨会报告
```

### 场景2：代码审查
```
用户: 审查这个PR
AI: [生成审查清单] 应用标准检查清单逐项检查
```

### 场景3：项目汇报
```
用户: 本周工作总结
AI: [生成周报] 包含进度、风险、下周计划
```

### 场景4：任务分配
```
用户: 分配新任务
AI: [分析负载] 推荐最合适的团队成员
```

## 最佳实践

1. **每日运行** git-stats.sh 跟踪代码活动
2. **定期更新** 配置文件保持信息准确
3. **自定义模板** 根据团队需求调整报告格式
4. **归档报告** 用于长期趋势分析
5. **迭代改进** 持续优化检查清单和配置

## 版本历史

### v1.0.0 (2024-02-20)
- ✅ Git 统计工具
- ✅ 报告生成器
- ✅ 代码审查清单
- ✅ 配置系统
- ✅ 晨会/周报模板
- ✅ 初始化脚本

## 未来计划

- [ ] 集成项目管理工具 API（Jira、Trello）
- [ ] 自动生成图表和可视化
- [ ] 风险自动预警
- [ ] 更多模板和检查清单
- [ ] 支持更多版本控制系统

---

*让研发管理更轻松！*
