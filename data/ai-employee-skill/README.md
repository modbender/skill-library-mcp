# AI员工协作技能包

> 让多个AI角色像真实团队一样协作工作

## 产品定位

这是一个**AI团队协作框架**，帮助用户：
1. 配置多个AI角色（老板、产品、技术、测试、运营等）
2. 自动分配和追踪任务
3. 监控工作进度
4. 生成工作报告

## 核心价值

| 痛点 | 解决方案 |
|------|----------|
| 一个人管不过来多个项目 | AI团队自动分工协作 |
| 任务分配混乱 | 智能任务分发系统 |
| 不知道进度如何 | 实时状态监控面板 |
| 写周报日报太烦 | 自动生成工作报告 |

## 快速开始

### 1. 安装

```bash
git clone <repo-url>
cd ai-employee-skill
npm install
```

### 2. 配置员工

编辑 `config/employees.json`：

```json
{
  "company": "我的AI公司",
  "employees": [
    {
      "id": "boss",
      "name": "老板AI",
      "role": "CEO",
      "responsibilities": ["战略决策", "资源分配"],
      "model": "gpt-4",
      "memoryPath": "./memory/boss"
    },
    {
      "id": "pm",
      "name": "产品AI",
      "role": "产品经理",
      "responsibilities": ["需求分析", "PRD撰写"],
      "model": "gpt-4",
      "memoryPath": "./memory/pm"
    }
  ]
}
```

### 3. 定义工作流

编辑 `config/workflow.json`：

```json
{
  "flows": [
    {
      "name": "产品开发流程",
      "steps": [
        {"role": "boss", "action": "assign", "next": "pm"},
        {"role": "pm", "action": "design", "next": "tech"},
        {"role": "tech", "action": "develop", "next": "test"},
        {"role": "test", "action": "verify", "next": "boss"}
      ]
    }
  ]
}
```

### 4. 启动

```bash
npm start
```

## 命令参考

### 员工管理

```bash
# 招聘新员工
/hire <role> --name <名字> --skills <技能列表>

# 查看员工列表
/employees

# 查看员工详情
/employee <id>

# 解雇员工
/fire <id>
```

### 任务管理

```bash
# 创建任务
/task create <任务描述>

# 分配任务
/task assign <taskId> <员工ID>

# 查看任务状态
/task status <taskId>

# 完成任务
/task complete <taskId> <结果描述>
```

### 监控和报告

```bash
# 团队状态
/status

# 今日工作
/today

# 生成日报
/report daily

# 生成周报
/report weekly

# 召开会议
/meeting <主题>
```

## 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                      AI员工协作系统                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ 员工管理器  │  │ 任务分发器  │  │ 状态监控器  │         │
│  │ EmployeeMgr │  │ TaskDispatch│  │StatusMonitor│         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                 │
│         └────────────────┼────────────────┘                 │
│                          │                                  │
│                   ┌──────┴──────┐                          │
│                   │  工作流引擎  │                          │
│                   │WorkflowEngine│                          │
│                   └──────┬──────┘                          │
│                          │                                  │
│         ┌────────────────┼────────────────┐                 │
│         │                │                │                 │
│  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐        │
│  │   记忆系统   │  │   汇报系统   │  │   通知系统   │        │
│  │MemorySystem │  │ReportGener  │  │NotifySystem │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 文件说明

| 文件 | 用途 |
|------|------|
| `scripts/employee-manager.js` | 员工增删改查、角色配置 |
| `scripts/task-dispatcher.js` | 任务创建、分配、追踪 |
| `scripts/status-monitor.js` | 实时状态监控、健康检查 |
| `scripts/report-generator.js` | 日报周报月报生成 |
| `scripts/meeting-coordinator.js` | 多AI会议协调 |
| `templates/*.md` | 员工角色模板 |
| `config/*.json` | 系统配置文件 |

## 扩展开发

### 添加新角色

1. 创建 `templates/custom-ai.md`：
```markdown
# 自定义AI角色

## 核心指令
描述这个角色的工作职责...

## 职责范围
- 职责1
- 职责2

## 工作流程
1. 步骤1
2. 步骤2
```

2. 在 `config/employees.json` 中添加配置

### 自定义工作流

在 `config/workflow.json` 中定义新的流程：

```json
{
  "name": "内容创作流程",
  "trigger": "content_request",
  "steps": [
    {"role": "pm", "action": "topic_selection"},
    {"role": "writer", "action": "draft"},
    {"role": "editor", "action": "review"},
    {"role": "publisher", "action": "publish"}
  ]
}
```

## 最佳实践

1. **角色分工明确**：每个AI员工有清晰的职责边界
2. **任务粒度适中**：任务不宜太大也不宜太碎
3. **定期回顾记忆**：清理过时信息，保持记忆有效
4. **设置超时机制**：避免某个环节卡住
5. **人工介入关键点**：重要决策由人工确认

## 常见问题

### Q: 如何让AI员工记住之前的工作？
A: 系统会自动将工作记录保存到 `memory/` 目录，下次启动时自动加载。

### Q: 如何处理任务失败？
A: 任务失败会自动通知相关员工和管理员，可以重新分配或升级处理。

### Q: 支持多少个AI员工？
A: 理论上无限制，但建议不超过10个以保持协作效率。

## 更新日志

### v1.0.0 (2026-03-02)
- 初始版本发布
- 支持5种基础角色
- 任务分发和追踪
- 状态监控和报告生成

---

*AI-Company 出品*