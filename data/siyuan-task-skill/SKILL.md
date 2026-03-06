---
name: siyuan-task
description: Manage tasks in SiYuan Note via its HTTP API. Create, query, update, and organize tasks stored in the 任务清单 document (with a TASK database) and sub-documents for related materials. Use when the user mentions SiYuan, task management, or needs to track work items.
compatibility: Requires Python 3.7+ and network access to SiYuan Note instance.
metadata:
  author: walter
  version: "1.0"
allowed-tools: Bash(python3:*)
---

# SiYuan Note Task Management

Manage tasks in SiYuan Note (思源笔记) via Python scripts. All connection settings are in `config.env` — modify that file when the SiYuan instance address or credentials change.

## Configuration

Edit `config.env` in the skill root directory. Only 3 items need manual configuration:

```env
SIYUAN_API_URL=http://100.64.0.11:52487
SIYUAN_API_TOKEN=xxxxxxxxxxxxxxxx
SIYUAN_NOTEBOOK_NAME=work
```

Note: `SIYUAN_NOTEBOOK_ID` is auto-resolved from `SIYUAN_NOTEBOOK_NAME` at runtime. You can still set it explicitly to skip the lookup.

Then run `init` to auto-create the database and write remaining config:

```bash
cd <skill_root>/scripts
python3 task_ops.py init
```

This creates the 任务清单 document, the TASK database, all columns, and writes AV_ID / COL_* IDs back to `config.env` automatically. If the 任务清单 document already contains a TASK database (e.g. copied from another notebook), `init` will detect and reuse it instead of creating a duplicate.

## Task Data Model

Tasks are stored as rows in a **TASK database (Attribute View)** block inside the 任务清单 document. Each row has these columns:

| Column | Chinese | Type | Values / Colors |
|--------|---------|------|-----------------|
| 主键 | 任务名称 | block | Primary key — task name |
| 任务内容 | 任务内容 | text | Task description / details (what the task is about) |
| 相关方 | 相关方 | text | Free text |
| 重要程度 | 重要程度 | select | 高(红) / 中(绿) / 低(灰) |
| 紧急程度 | 紧急程度 | select | 高(红) / 中(绿) / 低(灰) |
| 状态 | 状态 | select | 未开始(灰) / 进行中(绿) / 结束(红) / 挂起(蓝) |
| 备注 | 备注 | text | Extra notes / supplementary remarks (not the main task info) |
| 创建时间 | 创建时间 | created | Auto |
| 开始时间 | 开始时间 | date | Timestamp |
| 结束时间 | 结束时间 | date | Timestamp |
| 更新时间 | 更新时间 | updated | Auto |

Database IDs (auto-generated in `config.env` by `init` command):
- `AV_ID` — Attribute View ID
- `AV_BLOCK_ID` — AV block ID
- `COL_*` — Column IDs for each field

Each task automatically gets a sub-document under `/任务清单/{task_name}` with this template:

```markdown
# 任务描述

# 任务附件

# 下一步
```

The sub-document name always matches the task name. The task's primary key in the database is linked to the sub-document (non-detached), showing a document icon. Renaming a task also renames its sub-document. Deleting a task also deletes its sub-document.

## Scripts

All scripts are in the `scripts/` directory. Run from that directory:

```bash
cd <skill_root>/scripts
```

### siyuan_api.py — Base API Client

Low-level client wrapping all SiYuan HTTP API endpoints. Used by `task_ops.py` internally. Can also be imported directly for custom operations:

```python
from siyuan_api import SiYuanClient
client = SiYuanClient()
result = client.sql_query("SELECT * FROM blocks WHERE type = 'd' LIMIT 5")
```

Key methods: `sql_query`, `create_doc`, `append_block`, `update_block`, `delete_block`, `set_block_attrs`, `get_block_attrs`, `get_child_blocks`, `get_block_kramdown`, `export_md`, `upload_asset`, `push_msg`. See `references/API.md` for full SiYuan API reference.

### task_ops.py — Task CRUD Operations

High-level CLI for task management. All commands output JSON.

**Create a task** (auto-creates sub-document with template):

```bash
python3 task_ops.py create "任务名称" content="任务内容" importance="高" urgency="中" notes="备注信息"
```

Parameter mapping:
- `content` → 任务内容 (task description / main information about the task)
- `notes` → 备注 (supplementary remarks, not the main task info)
- `stakeholders` → 相关方
- `importance` → 重要程度 (高/中/低)
- `urgency` → 紧急程度 (高/中/低)
- `status` → 状态 (default: 未开始)

**List all tasks:**

```bash
python3 task_ops.py list
```

**Find tasks by status:**

```bash
python3 task_ops.py find "进行中"
```

**Change task status** (pass row_id from `list` output):

```bash
python3 task_ops.py start <row_id>
python3 task_ops.py complete <row_id>
python3 task_ops.py suspend <row_id>
```

**Rename a task** (also renames sub-document):

```bash
python3 task_ops.py rename <row_id> "新名称"
```

**Attach image to task sub-document** (uploads file and inserts into section):

```bash
python3 task_ops.py attach-image <row_id> /path/to/image.png
python3 task_ops.py attach-image <row_id> /path/to/image.png section="任务描述"
```

Default section is `任务附件`. On macOS, save clipboard image first: `osascript -e 'set png to (the clipboard as «class PNGf»)' -e 'set f to open for access (POSIX file "/tmp/clip.png") with write permission' -e 'write png to f' -e 'close access f'`

**List sub-documents:**

```bash
python3 task_ops.py list-docs
```

**Delete a task** (also deletes sub-document):

```bash
python3 task_ops.py delete <row_id>
```

**Migrate database** (apply schema changes and reorder columns):

```bash
python3 task_ops.py migrate
```

## Programmatic Usage

For complex workflows, import `TaskManager` directly in Python:

```python
import sys; sys.path.insert(0, "<skill_root>/scripts")
from task_ops import TaskManager

tm = TaskManager()

# Create task (auto-creates sub-document with template)
result = tm.create_task("实现用户登录", content="OAuth2 集成", importance="高", urgency="高")
row_id = result["row_id"]
doc_id = result["doc_id"]

# Rename task (also renames sub-document)
tm.rename_task(row_id, "实现OAuth2登录")

# Status transitions
tm.start_task(row_id)
tm.complete_task(row_id)

# Delete task (also deletes sub-document)
tm.delete_task(row_id)

# Attach image to task sub-document (default section: 任务附件)
tm.attach_image_to_task(row_id, "/path/to/image.png")
tm.attach_image_to_task(row_id, "/path/to/image.png", section="任务描述")
```

## Important Notes

1. The 任务清单 document and TASK database are auto-created on first use
2. Tasks are stored as database rows (Attribute View), not plain blocks
3. `row_id` from `list` output is used for all update/delete operations
4. `创建时间` and `更新时间` columns are auto-managed by SiYuan
5. Block references use SiYuan format: `((<block_id> "anchor text"))`
6. All API responses have `code` field — `0` means success
