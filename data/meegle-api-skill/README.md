# Meegle API Skill

> OpenClaw skills for Meegle (Feishu Project / Lark Project) Open API

**[中文说明](#中文说明)** | This repository provides a collection of OpenClaw skills that help agents understand and correctly call Meegle Open API for space, work items, comments, views, and related operations.

## Overview

Meegle API Skill splits Meegle OpenAPI into multiple sub-skills by functional area. Before calling any Meegle API, read **meegle-api-credentials** first to obtain domain, access token, context (project_key, user_key), and request headers. Other skills (Users, Space, Work Items, Setting, etc.) assume you have already obtained everything from credentials.

## Required Credentials

Required credentials are declared in [meegle-api-credentials](./meegle-api-credentials/SKILL.md):

| Credential | Description | Where to obtain |
|------------|-------------|-----------------|
| `plugin_id` | Plugin ID | Meegle Developer Platform → Plugin → Basic Information |
| `plugin_secret` | Plugin secret | Meegle Developer Platform → Plugin → Basic Information |
| `domain` | API host | `project.larksuite.com` (international) or `project.feishu.cn` (China) |
| `project_key` | Space identifier (required) | Meegle platform: double-click the project icon |
| `user_key` | User identifier (required) | Meegle platform: double-click the avatar; or from user_access_token response |

Optional: `authorization_code` and `refresh_token` for obtaining `user_access_token`. Request headers and usage are documented in [meegle-api-credentials](./meegle-api-credentials/SKILL.md).

**Configure once via environment variables** (e.g. `MEEGLE_USER_KEY`, `MEEGLE_PROJECT_KEY`, `MEEGLE_PLUGIN_ID`, `MEEGLE_PLUGIN_SECRET`, `MEEGLE_DOMAIN`) so OpenClaw uses them and does not ask every time. See [Environment variables](meegle-api-credentials/SKILL.md#environment-variables) in the credentials skill.

## Skill List

| Order | Sub-skill | When to read |
|-------|-----------|--------------|
| 1 | [meegle-api-credentials](./meegle-api-credentials/SKILL.md) | Domain, token, context (project_key, user_key), request headers. **Read this before any Meegle API call.** |
| 2 | [meegle-api-users](./meegle-api-users/SKILL.md) | User-related OpenAPIs (e.g. user groups, members) |
| 3 | [meegle-api-space](./meegle-api-space/SKILL.md) | Space (project) operations |
| 4 | [meegle-api-work-items](./meegle-api-work-items/SKILL.md) | Create, get, update work items (tasks, stories, bugs, etc.) |
| 5 | [meegle-api-setting](./meegle-api-setting/SKILL.md) | Settings, work item types, fields, process configuration |
| 6 | [meegle-api-comments](./meegle-api-comments/SKILL.md) | Comments on work items or other entities |
| 7 | [meegle-api-views-measurement](./meegle-api-views-measurement/SKILL.md) | Views, kanban, Gantt, charts, measurement |

## Work Item Sub-skills

`meegle-api-work-items` includes:

| Sub-skill | Directory | Description |
|-----------|-----------|-------------|
| Create / Read / Update work items | `work-item-read-and-write/` | Create work items, get details, update work items |
| List & search work items | `work-item-lists/` | Filter, search, full-text search, associated items, universal search |
| Workflows & nodes | `workflows-and-nodes/` | Workflow and node related APIs |
| Tasks | `tasks/` | Task related APIs |
| Attachment | `attachment/` | Work item attachment related APIs |
| Space association | `space-association/` | Space association related APIs |
| Group | `group/` | Work item group related APIs |

## Usage

1. Reference this repository as a Cursor skill, or copy the relevant `SKILL.md` files into your Cursor skills directory.
2. When working on Meegle-related tasks in Cursor, have the AI use the `Read` tool to load the corresponding `SKILL.md` for the needed API area.
3. Before any Meegle API call, have the AI read **meegle-api-credentials** to obtain domain, token, request headers, and context.
4. If you are using **OpenClaw**, you can search for this skill pack on **Clawhub** by name `meegle-api-skill` and install it directly via the Clawhub CLI

## API Regions

- **International**: `https://project.larksuite.com`
- **China (Feishu Project)**: `https://project.feishu.cn`

See [meegle-api-credentials](./meegle-api-credentials/SKILL.md) for domain and authentication details.

## Repository Structure

```
meegle-api-skill/
├── SKILL.md                      # Skill index (entry point)
├── README.md                     # This file
├── meegle-api-credentials/       # Domain, token, context, request headers
├── meegle-api-users/             # User-related OpenAPIs
├── meegle-api-space/             # Space
├── meegle-api-work-items/        # Work items (includes sub-skills)
├── meegle-api-setting/           # Settings
├── meegle-api-comments/          # Comments
└── meegle-api-views-measurement/ # Views and measurement
```

## License

See the LICENSE file in the repository root, if present.

---

## 中文说明

本仓库提供一组 OpenClaw skill，用于让智能体理解并正确调用 Meegle（飞书项目 / Lark Project）开放 API，涵盖空间、工作项、评论、视图等相关能力。

### 概述

Meegle API Skill 按功能拆成多个子 skill。调用任何 Meegle API 前，请先阅读 **meegle-api-credentials**，获取域名、访问令牌、上下文（project_key、user_key）及请求头。其他 skill（用户、空间、工作项、设置等）均假定已从 credentials 中拿到所需信息。

### 必填凭证

必填凭证在 [meegle-api-credentials](./meegle-api-credentials/SKILL.md) 中声明：

| 凭证 | 说明 | 获取方式 |
|------|------|----------|
| `plugin_id` | 插件 ID | Meegle 开发者平台 → 插件 → 基本信息 |
| `plugin_secret` | 插件密钥 | Meegle 开发者平台 → 插件 → 基本信息 |
| `domain` | API 主机 | 国际：`project.larksuite.com`；中国：`project.feishu.cn` |
| `project_key` | 空间标识（必填） | Meegle 平台：双击项目图标 |
| `user_key` | 用户标识（必填） | Meegle 平台：双击头像；或从 user_access_token 响应中获取 |

可选：`authorization_code`、`refresh_token` 用于获取 `user_access_token`。请求头及用法见 [meegle-api-credentials](./meegle-api-credentials/SKILL.md)。

**一次配置：使用环境变量**（如 `MEEGLE_USER_KEY`、`MEEGLE_PROJECT_KEY`、`MEEGLE_PLUGIN_ID`、`MEEGLE_PLUGIN_SECRET`、`MEEGLE_DOMAIN`），OpenClaw 会优先读取，无需每次询问。详见 credentials skill 中的 [Environment variables](meegle-api-credentials/SKILL.md#environment-variables)。

### Skill 列表

| 顺序 | 子 skill | 何时阅读 |
|------|----------|----------|
| 1 | [meegle-api-credentials](./meegle-api-credentials/SKILL.md) | 域名、令牌、上下文（project_key、user_key）、请求头。**调用任何 Meegle API 前必读。** |
| 2 | [meegle-api-users](./meegle-api-users/SKILL.md) | 用户相关 OpenAPI（如用户组、成员） |
| 3 | [meegle-api-space](./meegle-api-space/SKILL.md) | 空间（项目）操作 |
| 4 | [meegle-api-work-items](./meegle-api-work-items/SKILL.md) | 工作项的创建、查询、更新（任务、需求、缺陷等） |
| 5 | [meegle-api-setting](./meegle-api-setting/SKILL.md) | 设置、工作项类型、字段、流程配置 |
| 6 | [meegle-api-comments](./meegle-api-comments/SKILL.md) | 工作项或其他实体的评论 |
| 7 | [meegle-api-views-measurement](./meegle-api-views-measurement/SKILL.md) | 视图、看板、甘特图、图表、度量 |

### 工作项子 skill

`meegle-api-work-items` 包含：

| 子 skill | 目录 | 说明 |
|----------|------|------|
| 工作项创建 / 读 / 更新 | `work-item-read-and-write/` | 创建工作项、获取详情、更新工作项 |
| 工作项列表与搜索 | `work-item-lists/` | 筛选、搜索、全文检索、关联项、全局搜索 |
| 工作流与节点 | `workflows-and-nodes/` | 工作流与节点相关 API |
| 任务 | `tasks/` | 任务相关 API |
| 附件 | `attachment/` | 工作项附件相关 API |
| 空间关联 | `space-association/` | 空间关联相关 API |
| 分组 | `group/` | 工作项分组相关 API |

### 使用方式

1. 将此仓库作为 Cursor skill 引用，或将需要的 `SKILL.md` 复制到 Cursor 的 skills 目录。
2. 在 Cursor 中处理与 Meegle 相关的任务时，让 AI 使用 `Read` 工具加载对应 API 领域的 `SKILL.md`。
3. 调用任何 Meegle API 前，让 AI 先阅读 **meegle-api-credentials**，获取域名、令牌、请求头和上下文。
4. 若使用 **OpenClaw**，可在 **Clawhub** 中按名称 `meegle-api-skill` 搜索该技能包，并通过 Clawhub CLI 直接安装。

### API 区域

- **国际**：`https://project.larksuite.com`
- **中国（飞书项目）**：`https://project.feishu.cn`

域名与鉴权细节见 [meegle-api-credentials](./meegle-api-credentials/SKILL.md)。

### 仓库结构

```
meegle-api-skill/
├── SKILL.md                      # Skill 索引（入口）
├── README.md                     # 本文件
├── meegle-api-credentials/       # 域名、令牌、上下文、请求头
├── meegle-api-users/             # 用户相关 OpenAPI
├── meegle-api-space/             # 空间
├── meegle-api-work-items/        # 工作项（含子 skill）
├── meegle-api-setting/           # 设置
├── meegle-api-comments/          # 评论
└── meegle-api-views-measurement/ # 视图与度量
```

### 许可证

若仓库根目录存在 LICENSE 文件，请以该文件为准。

[↑ 返回顶部](#meegle-api-skill)
