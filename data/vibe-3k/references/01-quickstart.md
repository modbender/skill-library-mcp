# 01 — 快速开始：核心概念 + 项目启动

## 什么是 Vibe Coding

Andrej Karpathy（OpenAI 联合创始人）2025 年 2 月提出：用自然语言描述需求，让 AI 生成代码，开发者角色从「写代码」变为「引导、审查、迭代」。

**核心循环**：描述意图 → AI 生成 → 审查结果 → 迭代优化

**关键区分**（Simon Willison）：
- 审查了每一行 diff → 正常软件开发
- 接受 AI 输出而不完全理解每个函数 → Vibe Coding

**你是主厨，AI 是厨房团队。你设计菜单、品尝每道菜，但不亲自切每根胡萝卜。**

---

## 启动前准备（Before First Prompt）

```
✅ 先想清楚 What 和 Why，再让 AI 处理 How
✅ 画线框图 / 写用户流程 / 列出核心页面和功能
✅ 明确「Done」的定义
✅ 确定技术栈约束
❌ 不要上来就 prompt "帮我做一个 XXX app"
```

**最重要的 5 分钟**——在碰 AI 之前，写下：
1. 这个项目解决什么问题？
2. 目标用户是谁？
3. 核心功能列表（P0/P1/P2）
4. 技术栈约束
5. 什么叫做「完成」？

---

## 项目规则文件体系

```
项目根目录/
├── .claude/                # Claude Code 规则
│   ├── CLAUDE.md           # 主规则文件
│   └── rules/              # 模块化规则
├── .agent/                 # Google Antigravity 规则
│   └── skills/
├── AGENTS.md               # 通用 Agent 规则（Kimi / OpenClaw 等）
├── .rules                  # 统一规则文件（ruler 生成）
└── docs/
    ├── DESIGN.md            # 设计文档
    ├── PLAN.md              # 当前计划
    └── LOG.md               # 执行日志
```

**推荐工具**：`ruler` — 一套规则同步到多个 Agent

---

## 第一个 Prompt 模板（6 步法）

```
Step 1 — 定义角色：
"你是一个资深 [技术栈] 开发者，专长于 [领域]"

Step 2 — 清晰描述任务：
- 具体需求 + Done 的定义 + 正面描述

Step 3 — 提供上下文：
- 链接文档 / README / API 文档 / MCP Server

Step 4 — 限定范围：
"只修改 src/components/ 目录下的文件"

Step 5 — 指定输出格式：
"输出为 TypeScript，包含类型定义"

Step 6 — 设置安全护栏：
"改动前先给我 plan，等我确认再执行"
```

---

## 项目规则文件模板

根据项目类型选择：

### 模板 A：AI 模型微调 / 量化转换

```markdown
## 项目概述
- 类型：模型微调 / 量化转换
- 框架：PyTorch + Transformers + PEFT / llama.cpp / ONNX Runtime

## 代码规范
- Python 3.11+，type hints 必须
- 配置写入 config.yaml，不硬编码
- 数据路径用 pathlib.Path
- 日志用 logging，不用 print

## 绝对禁止
- 不要修改训练数据 / 模型架构（除非明确要求）
- 不要硬编码 GPU 编号
- 不要忽略 OOM 风险（改 batch size 前先算显存）
- 不要删除 checkpoint

## 工作方式
- 改超参数先说明理由
- 每次实验用独立 output_dir
- 量化前后必须对比精度指标
```

### 模板 B：Android Kotlin 开发

```markdown
## 项目概述
- 平台：Android（Kotlin）
- 架构：MVVM + Jetpack Compose
- 依赖管理：Version Catalog

## 代码规范
- 严格 null safety
- 单向数据流（ViewModel → UI）
- 异步：Coroutines + Flow，禁止 RxJava 新增
- DI：Hilt / Koin

## 绝对禁止
- 不要在 Activity/Fragment 写业务逻辑
- 不要在主线程做 IO
- 不要硬编码 API key
- 不要新增权限（除非讨论过）
```

### 模板 C：macOS 开发

```markdown
## 项目概述
- 平台：macOS（Swift / SwiftUI）
- 并发：Swift Concurrency，禁止 GCD 新增

## 绝对禁止
- 不要 force unwrap（除 IBOutlet）
- 不要引入 CocoaPods（用 SPM）
- 不要新增 App Sandbox 权限（除非讨论过）
```

### 模板 D：Linux 算法服务

```markdown
## 项目概述
- 平台：Linux（FastAPI / C++ / Rust）
- 部署：Docker + K8s / systemd

## 绝对禁止
- 推理路径不做内存分配（预分配 buffer）
- 不要硬编码模型路径/端口/GPU
- 不要用 root 运行服务
- 不要跳过健康检查端点
```
