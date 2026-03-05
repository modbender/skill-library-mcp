# Bug Records - Project-Specific Bug Documentation

> **Purpose**: Record all bugs fixed in the current project with root cause and fix method only.
> **Update Rule**: MANDATORY update after every bug fix. If previous fix was incomplete, update the record.

---

## Record Template

```markdown
### [BUG-XXX] Brief Description
**Date**: YYYY-MM-DD
**Severity**: P0/P1/P2

**Root Cause**:
[1-2 sentences explaining WHY the bug occurred]

**Fix Method**:
[Concise description of HOW the bug was fixed]

**Files Modified**:
- `path/to/file1.ts`
- `path/to/file2.ts`

**Environment Impact**:
- [ ] Development
- [ ] Staging
- [ ] Production
```

---

## Bug Records

<!-- Add new records below this line, newest first -->

### [BUG-017] Playwright Init NotImplementedError (Windows) - Root Cause Fix
**Date**: 2026-02-09 (updated)
**Severity**: P2

**Root Cause**:
uvicorn 0.36+ 's `asyncio_loop_factory(use_subprocess=True)` 在 `--reload` 模式下（`Config.use_subprocess=True`）
**explicitly selects `SelectorEventLoop`**（instead of Python 3.8+ Windows default `ProactorEventLoop`）。
`SelectorEventLoop` does not support `asyncio.create_subprocess_exec()`，Playwright cannot start Node.js subprocess。

Verification evidence:
```python
# uvicorn 0.40.0 - uvicorn/loops/asyncio.py
def asyncio_loop_factory(use_subprocess: bool = False):
    if sys.platform == "win32" and not use_subprocess:
        return asyncio.ProactorEventLoop  # Normal mode: ProactorEventLoop
    return asyncio.SelectorEventLoop       # reload mode: SelectorEventLoop <- Problem here
```

**Fix Method**:
Added to all startup entries `--loop none` / `loop="none"` parameter, telling uvicorn not to override the event loop factory。
Python 3.8+ Windows defaults to using `WindowsProactorEventLoopPolicy` → `ProactorEventLoop`，支持subprocess创建。
Also kept `playwright_browser_service.py` runtime pre-detection as defense layer。

**Files Modified**:
- `backend/run_dev.py` — Added `loop="none"` 参数
- `backend/app/main.py` — `__main__` 块Added `loop="none"`
- `start-dev.bat` — uvicorn 命令Added `--loop none`
- `dev-with-app.ps1` — uvicorn 命令Added `--loop none`
- `backend/app/services/playwright_browser_service.py` — Improved warning messages with fix suggestions

**Environment Impact**:
- [x] Development
- [ ] Staging
- [ ] Production

---

### [BUG-016] Backend Logs Not Displayed (dev-lan-server.bat)
**Date**: 2026-02-09
**Severity**: P2

**Root Cause**:
`dev-with-app.ps1` did not set when starting backend `PYTHONUNBUFFERED=1` and `PYTHONIOENCODING=utf-8`，
Python stdout/stderr were buffered, logs could not output in real-time to cmd window。

**Fix Method**:
在 `dev-with-app.ps1` 's backendEnv 哈希表中Added `PYTHONUNBUFFERED=1` and `PYTHONIOENCODING=utf-8`。

**Files Modified**:
- `dev-with-app.ps1`

**Environment Impact**:
- [x] Development
- [ ] Staging
- [ ] Production

---

### [BUG-015] AgentExecutor Calls Deleted _get_context_manager Method
**Date**: 2026-02-09
**Severity**: P1

**Root Cause**:
2026-02-09 refactoring deleted `_get_context_manager()` Method（line 378 has comment record），
但line 2218 still calls `self._get_context_manager()`。When Token limit triggers emergency compression，
raises `AttributeError: 'AgentExecutor' object has no attribute '_get_context_manager'`。

**Fix Method**:
Changed `self._get_context_manager()` replaced with inline `from app.services.context_manager import ContextManager; ContextManager()`。
Uses TRUNCATE strategy (pure truncation), does not need llm_call parameter, no-arg constructor is safe。

**Files Modified**:
- `backend/app/services/agent_executor.py`

**Environment Impact**:
- [x] Development
- [ ] Staging
- [ ] Production

---

### [BUG-014] Zhipu API Key Invalid After Restart (ENCRYPTION_KEY Inconsistency)
**Date**: 2026-02-09
**Severity**: P0

**Root Cause**:
`_resolve_env_files()` 在 `LEADONGAGENT_ENV_FILE` is set（dev-lan-server.bat startup method），
only loads `.env.development`，which has no `ENCRYPTION_KEY`，falling back to `dev_encryption.key` 中's密钥。
但 `backend/.env` 中有不同's `ENCRYPTION_KEY`。两种startup method使用不同密钥Caused API Key decryption failure。

Fix introduced P1 regression: assumed pydantic-settings "first file has highest priority"，but actually `dict.update()` means
**最后's文件胜出**。Caused env_file priority to be reversed。Code Review phase discovered and corrected。

**Fix Method**:
1. Modified `_resolve_env_files()` when specifying explicit env file always includes `backend/.env` and root `.env` 作为兜底。
2. Corrected priority order：base files first (lowest priority)，explicit file last (highest priority)。
3. Corrected non-explicit 分支注释's误导。

**Lessons Learned**:
- 涉及第三方框架line为时，必须阅读框架源码验证实际语义，不能凭假设
- bug-guide.md category 5.1 already had"config loading order"pattern, but was not consulted

**Files Modified**:
- `backend/app/config.py`

**Environment Impact**:
- [x] Development
- [ ] Staging
- [ ] Production

---

### [BUG-013] Local Generation Request Still Writes to Workspace
**Date**: 2026-02-05
**Severity**: P1

**Root Cause**:
1. 本地意图开启后，相对路径仍回落到 workspace 解析逻辑，Caused“本地”请求未生效。
2. Unix 绝对路径检测仅匹配输入开头，Caused“保存到 /home/user/...”被误判为非本地请求。

**Fix Method**:
1. 新增本地路径解析逻辑：相对路径默认写入桌面（若无桌面则写入用户主目录）。
2. 改进路径检测：支持 C:/、C:\ 以及输入中's Unix 绝对路径，并忽略 URL。

**Files Modified**:
- `backend/app/core/langchain/tools.py`
- `backend/app/services/agent_executor.py`

**Environment Impact**:
- [x] Development
- [ ] Staging
- [ ] Production

---

### [BUG-012] Unescaped Quotes in Tool Description Causes Service Startup Failure
**Date**: 2026-02-05
**Severity**: P1

**Root Cause**:
在 `tools.py` 's工具描述字符串中包含未转义's双引号（"帮我写/给我写"），Caused Python 解析时报 `SyntaxError`，服务cannot start。

**Fix Method**:
对字符串中's内部引号进line转义，确保 Python 字符串字面量合法。

**Files Modified**:
- `backend/app/core/langchain/tools.py`

**Environment Impact**:
- [x] Development
- [ ] Staging
- [ ] Production

---

### [BUG-011] OCR Model Used for Chat Causes messages illegal (20015)
**Date**: 2026-02-05
**Severity**: P1

**Root Cause**:
1. Agent 对话未校验模型是否支持 chat messages
2. OCR 专用模型被误配置为对话模型，API 返回 20015

**Fix Method**:
1. 在 LLMManager 中Added非聊天模型检测（OCR 关键词/能力标签）
2. 捕获 20015 错误并输出用户可操作's解决方案提示

**Files Modified**:
- `backend/app/services/llm_manager.py`

**Environment Impact**:
- [x] Development
- [ ] Staging
- [ ] Production

---

### [BUG-010] Models Without Function Call Support (e.g. DeepSeek-OCR) Trigger API 400 Error
**Date**: 2026-02-05
**Severity**: P1

**Root Cause**:
1. `_KNOWN_NO_TOOL_SUPPORT_PATTERNS` 模式列表未包含 "ocr"，Caused OCR 专用模型被误认为支持原生工具调用
2. `AgentExecutor` and `GraphAgentExecutor` 's `_should_use_simulated_mode` 实现Inconsistency
3. When模型does not support Function Call 时，API 返回错误码 20037，但没有用户友好's错误提示

**Fix Method**:
1. 在 `_KNOWN_NO_TOOL_SUPPORT_PATTERNS` Added "ocr" 模式
2. 统一 `GraphAgentExecutor._should_use_simulated_mode` 使用相同's模式列表
3. 在 `llm_manager.stream_with_retry` 中捕获 20037 错误并给出清晰's解决方案提示

**Files Modified**:
- `backend/app/services/agent_executor.py`
- `backend/app/services/graph_agent_executor.py`
- `backend/app/services/llm_manager.py`

**Environment Impact**:
- [x] Development
- [ ] Staging
- [ ] Production

---

### [BUG-009] Fallback typewriter + real streaming causes duplicate preview content
**Date**: 2026-02-04
**Severity**: P1

**Root Cause**:
When the 300ms fallback typewriter starts, it appends preview content but does not update the applied-length tracker. If `tool_argument_delta` arrives later, streaming re-applies content from length 0, causing duplicates.

**Fix Method**:
Update `toolArgumentAppliedRef` during each typewriter chunk when the stream key is a tool call ID, keeping applied length in sync to prevent duplicate appends.

**Files Modified**:
- `frontend/src/features/chat/ChatPageV2.tsx`

**Environment Impact**:
- [x] Development
- [ ] Staging
- [ ] Production

---

### [BUG-008] SKILL.md BOM Causes Frontmatter Recognition Failure
**Date**: 2026-02-04
**Severity**: P2

**Root Cause**:
用户本地's SKILL.md 文件首部包含 UTF-8 BOM，Caused解析器无法在首字符位置识别 `---` frontmatter 起始。

**Fix Method**:
以 UTF-8 无 BOM 重新写入文件内容，移除 BOM。

**Files Modified**:
- 用户本地 codex skills 目录下's `SKILL.md`

**Environment Impact**:
- [x] Development
- [ ] Staging
- [ ] Production

---

### [BUG-007] Tool 参数流式预览中断与 ID InconsistencyCaused预览卡死
**Date**: 2026-02-04
**Severity**: P1

**Root Cause**:
1. `tool_argument_delta` 事件处理依赖 `artifacts`，Caused effect 重新挂载时缓冲区重置，流式内容只显示首段。
2. 工具流式阶段使用 `tc-{index}` 临时 ID，但执line阶段使用真实 `tool_call_id`，预览映射无法完成。
3. 工具参数增量 `args` 假设为字符串，遇到 dict 时拼接报错Caused流式中断。

**Fix Method**:
1. 使用 `useRef` 保存流式缓冲区与已应用长度，移除 `artifacts` 依赖，避免重置。
2. 在聚合 `tool_calls` 阶段补齐缺失 `tool_call_id`，与流式阶段保持一致。
3. 对 `tool_call_chunks` 's `args` 做类型保护（dict/list → JSON 字符串）。

**Files Modified**:
- `backend/app/services/agent_executor.py`
- `frontend/src/features/chat/ChatPageV2.tsx`

**Environment Impact**:
- [x] Development
- [ ] Staging
- [ ] Production

---

### [BUG-006] argon2 Hash in pytest Triggers Memory Allocation Failure
**Date**: 2026-01-27
**Severity**: P2

**Root Cause**:
测试环境在创建测试用户时调用 argon2 默认 64MB 内存成本，资源不足Caused `argon2.exceptions.HashingError: Memory allocation error`，进而使 pytest fixture 初始化失败。

**Fix Method**:
为密码哈希上下文增加测试环境降级逻辑（基于 `ENVIRONMENT=testing` 或 `PYTEST_CURRENT_TEST`），在测试模式下调低 argon2 内存/轮次参数。

**Files Modified**:
- `backend/app/core/security.py`

**Environment Impact**:
- [x] Development
- [ ] Staging
- [ ] Production

---

### [BUG-005] UndefinedTableError: system_config table missing
**Date**: 2026-01-25
**Severity**: P0

**Root Cause**:
Database initialization script (`init.sql`) was likely interrupted or failed silently, causing tables like `system_config` and `query_history` to be missing. Additionally, Alembic migration scripts were missing (`alembic/versions` was empty), preventing proper schema management and causing mismatches between SQLAlchemy models and the database.

**Fix Method**:
1. Corrected `knowledge-base/backend/alembic/env.py` to use `settings.database_url` (async) for migrations.
2. Removed incompatible non-ASCII comments from `knowledge-base/backend/alembic.ini` to fix `UnicodeDecodeError`.
3. Created `knowledge-base/backend/.env` to provide correct DB credentials to Alembic.
4. Generated initial migration with `alembic revision --autogenerate`.
5. Fixed `DatatypeMismatchError` in migration script by adding `postgresql_using='to_json(scopes)'` for casting `ARRAY(TEXT)` to `JSON`.
6. Applied migrations with `alembic upgrade head`.

**Files Modified**:
- `knowledge-base/backend/alembic/env.py`
- `knowledge-base/backend/alembic.ini`
- `knowledge-base/backend/alembic/versions/20260125_1201_b787f64036f4_initial_migration.py`
- `knowledge-base/backend/.env` (Created)

**Environment Impact**:
- [x] Development
- [ ] Staging
- [ ] Production

---

### [BUG-004] Database Connection Failure & Password Mismatch
**Date**: 2026-01-25
**Severity**: P0

**Root Cause**:
1. PostgreSQL container (Docker) was not publishing port 5432 to the host (`0.0.0.0:5432->5432/tcp` missing).
2. Database initialized with `kb_password` (from previous run) but `.env` was configured with `kb_dev_password`, causing `InvalidPasswordError`.

**Fix Method**:
1. Restarted Docker containers with `docker-compose up -d --force-recreate` to fix port mapping.
2. Updated `knowledge-base/.env` to set `POSTGRES_PASSWORD=kb_password`.
3. (Verification step) Reset DB user password via `docker exec` to ensure consistency.

**Files Modified**:
- `knowledge-base/.env`

**Environment Impact**:
- [x] Development
- [ ] Staging
- [ ] Production

---

### [BUG-003] LightRAG Storage Import Path Error
**Date**: 2026-01-25
**Severity**: P0

**Root Cause**:
`lightrag-hku` v1.4.9.11 's存储类（MilvusVectorDBStorage, Neo4JStorage, PGKVStorage, PGDocStatusStorage）不是从 `lightrag.kg` 直接导出，而是在各自's子模块中。

**Fix Method**:
Modified导入路径为正确's子模块：
- `from lightrag.kg.milvus_impl import MilvusVectorDBStorage`
- `from lightrag.kg.neo4j_impl import Neo4JStorage`
- `from lightrag.kg.postgres_impl import PGDocStatusStorage, PGKVStorage`

**Files Modified**:
- `knowledge-base/backend/app/services/rag_engine.py`

**Environment Impact**:
- [x] Development
- [ ] Staging
- [ ] Production

---

### [BUG-002] Frontend npm Dependencies Not Installed
**Date**: 2026-01-25
**Severity**: P0

**Root Cause**:
`node_modules` 目录不存在，`next` 命令找不到因为 npm 依赖未安装。

**Fix Method**:
在 `knowledge-base/frontend` 目录下执line `npm install` 安装依赖。

**Files Modified**:
- 无代码Modified，仅安装依赖

**Environment Impact**:
- [x] Development
- [ ] Staging
- [ ] Production

---

### [BUG-001] SQLAlchemy Reserved Attribute Name 'metadata'
**Date**: 2026-01-25
**Severity**: P0

**Root Cause**:
`Document` 模型使用 `metadata` 作为属性名，但这是 SQLAlchemy Declarative API 's保留字，用于存储表元数据。

**Fix Method**:
Changed Python 属性名从 `metadata` 改为 `doc_metadata`，同时使用 `mapped_column("metadata", ...)` 保持数据库列名不变。

**Files Modified**:
- `knowledge-base/backend/app/models/document.py`

**Environment Impact**:
- [x] Development
- [ ] Staging
- [ ] Production

---

### [BUG-000] Example: Environment Configuration Mismatch
**Date**: 2024-XX-XX
**Severity**: P1

**Root Cause**:
Bug fix only modified production `.env` file, but development mode uses `.env.development` which was not updated.

**Fix Method**:
1. Identified all environment files: `.env`, `.env.development`, `.env.production`, `.env.local`
2. Applied the same configuration change to ALL relevant environment files
3. Verified startup in both dev and prod modes

**Files Modified**:
- `.env`
- `.env.development`
- `.env.production`

**Environment Impact**:
- [x] Development
- [ ] Staging
- [x] Production

---

## Quick Reference: Common Root Causes

| Category | Root Cause Pattern | Prevention |
|----------|-------------------|------------|
| **Environment** | Config only in one env file | Check ALL env files |
| **Import** | Wrong import path/syntax | Verify module resolution |
| **State** | Race condition/stale state | Add proper synchronization |
| **Type** | Type mismatch/null check | Enable strict TypeScript |
| **API** | Contract mismatch | Verify request/response schema |
| **Dependency** | Version incompatibility | Lock versions, test upgrades |

---

## Statistics

| Month | Total Bugs | P0 | P1 | P2 | Most Common Category |
|-------|------------|----|----|----|--------------------|
| 2026-01 | 3 | 3 | 0 | 0 | Import/Type |
| YYYY-MM | 0 | 0 | 0 | 0 | - |

---

## Update Checklist

After fixing a bug, ensure:
- [ ] New record added with root cause and fix method
- [ ] Previous incomplete fix records updated if applicable
- [ ] Environment impact correctly marked
- [ ] `bug-fixing-guide.md` updated if this is a new pattern
