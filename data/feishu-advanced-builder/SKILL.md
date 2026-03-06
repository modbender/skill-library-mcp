---
name: feishu-advanced-builder
description: 飞书高阶构建器。提供飞书基础原生工具之外的深度结构化能力，包括：原生画板（Mermaid/PlantUML）一键生成并嵌入、多维表格（Bitable）精准行列级数据操控、以及超复杂 Markdown 到飞书原生 Block 树的无损转化。适用于研发 DevOps 流转、架构图自动绘制及重度排版文档生成。
---

# Feishu Advanced Builder (飞书高阶构建器)

超越普通纯文本记录，通过“构建器”思维实现飞书环境下的深度结构化数据写入与控制。它直接干预飞书底层的原子块（Block）与数据行记录，适用于汽车软件开发、架构师日常沉淀与复杂的 Auto-RCA 报告输出。

## 🎯 三大核心模块 (Core Capabilities)

### 1. 🎨 画板图谱注入器 (`scripts/feishu-board.js`)
**使用场景**: 故障树智能生成、架构时序设计、业务状态流转图。
将大模型生成的逻辑（如 Mermaid / PlantUML）自动变现为**飞书原生的画板块（Block Type 43）**。
*   一键创建子画板并嵌入文档
*   支持 Mermaid 流程图注入（`syntaxType: mermaid`）
*   支持 PlantUML 时序/类图/脑图注入（`syntaxType: plantuml`）

### 2. 🗄️ 多维表格数据执行器 (`scripts/feishu-bitable.js`)
**使用场景**: Auto-RCA 自动化 Bug 指派、测试状态追踪看板。
它不是简单的读取整张表格，而是像操作 SQL 数据库一样精准干预具体的 Row（行级数据）。
*   在指定的 App ID / Table ID 下创建或更新特定数据条目。
*   支持写入带数据格式限定的字段：多选状态 (Status)、关联人员 (Persons)、日期筛选 (Dates) 等。

### 3. 📜 高级排版转化引擎 (`scripts/feishu-markdown-to-docx.js`)
**使用场景**: PRD/架构文档自动反编译及回写、长篇分析报告输出。
解决复杂的 Markdown 输出到飞书文档时排版崩坏或降级为纯文本的问题。
*   精准映射底层节点：将大模型的列表嵌套、复杂区块引用、代码高亮强制重编译为**飞书原生的对应 Block 结构**，保证最高级别的沉淀美观度。

---

## 🛠️ 安装与鉴权 (Setup)

前提：飞书应用必须拥有相关的多维表 (`bitable:app`)、文档 (`docx:document`) 和 画板 (`board:whiteboard:node`) 高级写入与读取权限。

*   `FEISHU_APP_ID` & `FEISHU_APP_SECRET`: 飞书应用的密钥凭证。

_Note: 这是一个进阶开发者套件，执行前确保你清楚它的结构化数据定位。_
