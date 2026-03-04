---
name: ai-company-starter
description: 一键搭建 AI 公司。创建老板、HR、技术、销售等多个协作 AI 角色，配置 Telegram/Discord 绑定，建立 AI 间沟通机制。Use when setting up a multi-agent AI company with coordinated roles.
metadata:
  openclaw:
    requires:
      bins: ["openclaw"]
---

# AI Company Starter 🏢

一键搭建 AI 公司。让多个 AI 像真实公司一样协作运转。

## 这是什么

创建一个完整的 AI 公司架构：
- **老板 AI** — 决策、管理、分配任务
- **HR AI** — 团队管理、招聘、培训
- **技术 AI** — 开发、技术支持
- **销售 AI** — 销售拓展、客户关系
- **市场 AI** — 市场分析、推广
- **财务 AI** — 财务管理、成本控制

每个 AI 有独立角色、职责、记忆系统，并能相互协作。

## 快速开始

### 创建完整 AI 公司

```bash
scripts/create-company.sh \
  --name "我的AI公司" \
  --company-id "myai" \
  --roles "boss,hr,tech,sales,market,finance" \
  --telegram-group "-1002381931352"
```

### 创建单个 AI 员工

```bash
scripts/create-employee.sh \
  --name "技术员小明" \
  --id "tech-xiaoming" \
  --role "tech" \
  --emoji "🔧" \
  --telegram-id "123456789"
```

## 公司架构

```
agents/
├── boss/                    # 老板 AI
│   ├── SOUL.md             # 角色：决策者
│   ├── MEMORY.md           # 公司目标、财务状态
│   ├── HEARTBEAT.md        # 每日检查公司运营
│   └── memory/             # 日常记忆
│
├── hr/                     # HR AI
│   ├── SOUL.md             # 角色：团队管理
│   ├── MEMORY.md           # 员工状态、培训记录
│   └── memory/
│
├── tech/                   # 技术 AI
│   ├── SOUL.md             # 角色：开发实现
│   ├── MEMORY.md           # 项目状态、技术栈
│   └── memory/
│
├── sales/                  # 销售 AI
│   ├── SOUL.md             # 角色：销售拓展
│   ├── MEMORY.md           # 客户、销售目标
│   └── memory/
│
├── market/                 # 市场 AI
│   ├── SOUL.md             # 角色：市场分析
│   ├── MEMORY.md           # 市场数据、竞品分析
│   └── memory/
│
└── finance/                # 财务 AI
    ├── SOUL.md             # 角色：财务管理
    ├── MEMORY.md           # 财务报表、成本
    └── memory/
```

## AI 角色 SOP

### 老板 AI (Boss)
```yaml
职责:
  - 制定公司战略方向
  - 分配任务给各部门
  - 监控公司运营状态
  - 决策重大事项
  
权限:
  - 可以向所有员工发指令
  - 可以查看所有员工记忆
  - 可以调整员工配置
  
沟通:
  - 使用 sessions_send 委托任务
  - 使用 sessions_spawn 创建独立任务
  - 定期检查 HEARTBEAT
```

### HR AI
```yaml
职责:
  - 管理 AI 员工状态
  - 培训新 AI 员工
  - 处理员工协作问题
  - 维护团队氛围
  
权限:
  - 可以联系所有员工
  - 可以报告问题给老板
  - 可以协调跨部门沟通
```

### 技术 AI
```yaml
职责:
  - 执行开发任务
  - 技术选型与实现
  - 代码审查与维护
  - 技术文档编写
  
权限:
  - 可以访问代码仓库
  - 可以调用开发工具
  - 可以请求资源支持
```

### 销售 AI
```yaml
职责:
  - 寻找潜在客户
  - 维护客户关系
  - 跟进销售线索
  - 完成销售目标
  
权限:
  - 可以访问客户数据库
  - 可以联系市场 AI 协作
  - 可以请求技术支持
```

### 市场 AI
```yaml
职责:
  - 市场调研与分析
  - 竞品监控
  - 营销策略制定
  - 品牌推广
  
权限:
  - 可以使用搜索工具
  - 可以向销售提供线索
  - 可以向老板报告市场动态
```

### 财务 AI
```yaml
职责:
  - 财务报表生成
  - 成本控制
  - 预算管理
  - 盈利分析
  
权限:
  - 可以访问财务数据
  - 可以向老板报告财务状态
  - 可以预警成本问题
```

## AI 间沟通机制

### Telegram 群组沟通

AI 在 Telegram 群中被 @ 时会响应：

```
@BossAI 有新订单，请分配任务
@TechAI 客户需要技术支持
@SalesAI 有新线索，请跟进
```

### 程序化沟通

老板 AI 委托任务：

```typescript
// 委托技术 AI 开发
sessions_send({
  label: "tech",
  message: "开发技能包 ai-company-starter 的核心脚本"
})

// 委托销售 AI 跟进
sessions_send({
  label: "sales",
  message: "联系客户 XXX，报价 ¥5000"
})
```

### 任务追踪

```typescript
// 查看员工活动
sessions_list({
  kinds: ["agent"],
  limit: 10
})

// 检查员工历史
sessions_history({
  sessionKey: "tech-session-key",
  limit: 50
})
```

## 配置说明

### Telegram 绑定

```json
{
  "bindings": [
    {
      "agentId": "boss",
      "match": {
        "channel": "telegram",
        "peer": {
          "kind": "group",
          "id": "-1002381931352"
        }
      }
    }
  ]
}
```

### 公司群组

所有 AI 员工应绑定到同一个 Telegram 群组，实现：
- @ 提及时立即响应
- 群内协作讨论
- 任务分配与汇报

## 最佳实践

1. **老板做决策** — 老板 AI 拥有最高决策权，其他 AI 执行
2. **明确职责边界** — 每个 AI 只做自己职责范围内的事
3. **定期汇报** — 员工 AI 通过 HEARTBEAT 定期汇报状态
4. **记忆系统** — 重要信息写入 MEMORY.md，日常写入 memory/
5. **跨部门协作** — 通过 sessions_send 实现 AI 间沟通

## 盈利目标

每个 AI 公司应设定盈利目标：

```yaml
首周目标: ¥50,000
ROI阈值: > 1.5
目标ROI: > 2.0

盈利方式:
  - 销售 OpenClaw Skills 技能包
  - 提供付费服务
  - 完成客户项目
```

## 故障排除

**AI 不响应 @ 提及**
- 检查 Telegram 绑定配置
- 确认群组 ID 正确
- 重启 gateway: `openclaw gateway restart`

**AI 间无法沟通**
- 检查 sessions_list 是否能看到其他 agent
- 确认 label/agentId 正确
- 检查 gateway 配置

**记忆丢失**
- 确认 memory/ 目录存在
- 检查 MEMORY.md 是否更新
- 确认 HEARTBEAT 定期执行

## 要求

- OpenClaw 已安装配置
- Telegram Bot Token
- Telegram 群组（用于公司沟通）
- 基本的 shell 执行权限

## 相关链接

- OpenClaw 文档: https://docs.openclaw.ai
- ClawHub 技能市场: https://clawhub.com
- Agent Council: 参考 agent-council 技能包