---
name: Claude Skills 开发框架架构指导手册
description: 本框架基于 Anthropic Claude 的 Tool Use (Skills)
  特性构建，旨在提供一个通过自然语言聊天即可调用各类底层工具的开发脚手架。
  框架遵循高内聚、低耦合的设计原则，使开发者能够专注于“技能（Skill）”本身的编写，而无需过度关心 LLM 对话上下文、工具发现与函数执行的复杂逻辑。
---

# Claude Skills 开发框架架构指导手册

## 1. 项目概述 (Overview)

本框架基于 Anthropic Claude 的 Tool Use (Skills) 特性构建，旨在提供一个通过自然语言聊天即可调用各类底层工具的开发脚手架。
框架遵循高内聚、低耦合的设计原则，使开发者能够专注于“技能（Skill）”本身的编写，而无需过度关心 LLM 对话上下文、工具发现与函数执行的复杂逻辑。

## 2. 架构设计 (Architecture Design)

整个系统分为以下几个分层架构：

- **交互层 (CLI/API Interface)**: 负责接收用户输入，展示 Agent 的回复或执行结果。`main.py`
- **代理层 (Agent Layer)**: 负责维护对话历史、与 Claude API 交互，解析模型返回的 Tool Use 请求。`core/agent.py`
- **注册与调度层 (Registry & Dispatcher)**: 维护系统中所有可用的 Skills（工具），向 LLM 声明这些工具的 JSON Schema，并根据 LLM 的指令找到对应的 Python 函数执行器。`core/registry.py`
- **技能层 (Skills Layer)**: 具体的业务代码抽象类及实现，继承自统一的 BaseSkill。`core/skill_base.py`, `skills/*`

## 3. 核心模块说明 (Core Modules)
