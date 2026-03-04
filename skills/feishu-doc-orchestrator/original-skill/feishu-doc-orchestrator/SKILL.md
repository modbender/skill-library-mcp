---
name: feishu-doc-orchestrator
description: 飞书文档创建主编排技能 - 将 Markdown 文件转换为飞书文档，编排多个子技能协作完成，使用文件传递数据以节省 Token。
---

# 飞书文档创建主编排技能

## 快速开始

### 命令行使用
```bash
# 创建文档（自动生成时间戳目录）
python scripts/orchestrator.py input.md "文档标题"

# 使用默认标题（文件名）
python scripts/orchestrator.py input.md

# 指定运行名称
python scripts/orchestrator.py input.md "文档标题" "test-run-01"
```

### 作为技能使用
```
请帮我将 docs/example.md 转换为飞书文档
```

## 工作流程（五步编排）

这个技能编排 5 个子技能协作完成文档创建：

### 第一步：Markdown 解析
调用 `feishu-md-parser` 子技能
- 输入：Markdown 文件路径
- 输出：`workflow/step1_parse/blocks.json`
- 说明：将 Markdown 解析为飞书块格式

### 第二步：文档创建+权限管理 ⭐ 原子操作
调用 `feishu-doc-creator-with-permission` 子技能
- 输入：文档标题
- 输出：`workflow/step2_create_with_permission/doc_with_permission.json`
- 说明：创建文档并**自动完成权限分配**（添加协作者+转移所有权）
- ⚠️ **重要**：文档创建和权限管理合并，确保每次创建都正确分配权限

### 第三步：块添加
调用 `feishu-block-adder` 子技能
- 输入：`step1_parse/blocks.json` + `step2_create_with_permission/doc_with_permission.json`
- 输出：`workflow/step3_add_blocks/add_result.json`
- 说明：分批添加内容块到文档

### 第四步：文档验证
调用 `feishu-doc-verifier` 子技能
- 输入：`step2_create_with_permission/doc_with_permission.json`
- 输出：`workflow/step4_verify/verify_result.json`
- 说明：使用 Playwright 验证文档可访问

### 第五步：日志记录
调用 `feishu-logger` 子技能
- 输入：所有步骤的结果文件
- 输出：`CREATED_DOCS.md` + `created_docs.json`
- 说明：汇总记录到日志文件

## 数据流（文件传递）

```
input.md
    ↓
[feishu-md-parser]
    ↓ workflow/feishu-doc-runs/run-2026-02-10-143022/step1_parse/blocks.json
[feishu-doc-creator-with-permission] ⭐ 创建+权限原子操作
    ↓ workflow/feishu-doc-runs/run-2026-02-10-143022/step2_create_with_permission/doc_with_permission.json
    ├─→ [feishu-block-adder] → workflow/feishu-doc-runs/run-2026-02-10-143022/step3_add_blocks/add_result.json
    └─→ [feishu-doc-verifier] → workflow/feishu-doc-runs/run-2026-02-10-143022/step4_verify/verify_result.json
[feishu-logger]
    ↓
workflow/feishu-logs/CREATED_DOCS.md + created_docs.json
```

## 关键设计原则

### 1. 只传文件路径，不传内容
子技能之间只传递文件路径，不传递实际内容，节省 Token。

### 2. 中间结果保存为文件
每一步的结果都保存到 `workflow/` 目录，可追溯、可断点续传。

### 3. 自然语言编排
主技能用自然语言描述流程，子技能各自独立可测试。

### 4. 单一职责
每个子技能只做一件事：
- `feishu-md-parser`：只解析 Markdown
- `feishu-doc-creator-with-permission`：创建文档并分配权限（原子操作）⭐
- `feishu-block-adder`：只添加块
- `feishu-doc-verifier`：只验证文档
- `feishu-logger`：只记录日志

## 工作流目录结构

### 项目根目录下的新结构
```
项目根目录/
└── workflow/
    ├── feishu-doc-runs/           # 所有运行记录（每次运行独立子文件夹）
    │   ├── run-2026-02-10-143022/
    │   │   ├── step1_parse/
    │   │   │   ├── blocks.json       # 解析后的块数据
    │   │   │   └── metadata.json     # 解析元数据
    │   │   ├── step2_create_with_permission/
    │   │   │   └── doc_with_permission.json  # 文档信息+权限状态 ⭐
    │   │   ├── step3_add_blocks/
    │   │   │   └── add_result.json   # 块添加结果
    │   │   └── step4_verify/
    │   │       └── verify_result.json      # 验证结果
    │   ├── run-2026-02-10-150845/
    │   └── run-2026-02-10-161233/
    └── feishu-logs/               # 汇总日志文件
        ├── CREATED_DOCS.md        # Markdown 格式的创建日志
        └── created_docs.json      # JSON 格式的创建日志
```

### 关键改进
- **每次运行独立子文件夹**：使用时间戳命名（`run-YYYY-MM-DD-HHMMSS`），避免相互污染
- **工作流数据与技能目录分离**：所有运行数据存储在项目 `workflow/` 目录下
- **可自定义运行名称**：可以指定有意义的运行名称，如 `test-run-01`、`demo-01` 等

## 输出结果

成功完成后，你会得到：
1. **文档 URL**：可直接访问的飞书文档链接
2. **workflow/feishu-logs/CREATED_DOCS.md**：Markdown 格式的创建日志
3. **workflow/feishu-logs/created_docs.json**：JSON 格式的创建日志
4. **workflow/feishu-doc-runs/run-YYYY-MM-DD-HHMMSS/**：本次运行的完整中间结果，可追溯每一步

## 配置要求

需要配置 `.claude/feishu-config.env`：
```ini
FEISHU_APP_ID = "cli_xxx"
FEISHU_APP_SECRET = "xxxxxxxx"
FEISHU_API_DOMAIN = "https://open.feishu.cn"
FEISHU_AUTO_COLLABORATOR_ID = "ou_xxx"
```

## 使用示例

### 示例1：基本使用
```
请帮我将 .claude/skills/feishu-doc-creator/test_doc.md 转换为飞书文档
```

### 示例2：指定标题
```
请将 docs/report.md 转为飞书文档，标题设为"周报-2026-01-22"
```

### 示例3：断点续传
如果某一步失败，可以手动修改中间结果后继续：
```
# 第2步创建+权限失败，手动重新执行
python .claude/skills/feishu-doc-creator-with-permission/scripts/doc_creator_with_permission.py "文档标题" workflow/feishu-doc-runs/run-2026-02-10-143022/step2_create_with_permission
```

## 常见问题

### Q1: 某一步失败了怎么办？
A: 查看 `workflow/feishu-doc-runs/run-YYYY-MM-DD-HHMMSS/stepX_*/` 目录下的 JSON 文件，可以手动修复后继续下一步。

### Q2: 如何只执行某一步？
A: 直接调用对应的子技能脚本，传入正确的文件路径。

### Q3: 工作流数据存储在哪里？
A: 所有工作流数据存储在项目的 `workflow/` 目录下：
- `workflow/feishu-doc-runs/` - 每次运行的独立子文件夹
- `workflow/feishu-logs/` - 汇总的日志文件

这样不会污染 skills 目录。

### Q3: Token 节省效果如何？
A: 文件传递方式比内容传递节省约 60-80% 的 Token。

---

## ⚠️ 重要调试说明

### Callout 块颜色问题

如果创建的 callout（高亮块）没有颜色和边框：

**原因**：Callout 块的颜色字段必须直接放在 `callout` 对象下，不能嵌套在 `style` 中。

**验证方法**：检查 API 返回的 callout 对象是否包含颜色字段：
```python
# 如果只有 emoji_id 而没有 background_color，说明格式错误
returned_callout = result["data"]["children"][0].get("callout", {})
```

**解决方案**：已在 `feishu-md-parser` 和 `feishu-block-adder` 中修复。

**详细排查**：见 `TROUBLESHOOTING.md`（问题 1）

**测试脚本**：`test_callout_only.py` - 单独测试 callout 格式
