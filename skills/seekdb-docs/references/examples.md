# seekdb Documentation Examples

Complete workflow examples for common seekdb documentation queries using **local-first strategy**.

## Example 1: Vector Search Query

**User Query**: "How do I use vector search in seekdb?"

**Process**:

1. **Resolve skill directory**
   ```
   Read SKILL.md → /root/.claude/skills/seekdb/SKILL.md
   Extract: skill directory = /root/.claude/skills/seekdb/
   ```

2. **Load catalog (local-first)**
   ```
   Try local: /root/.claude/skills/seekdb/references/seekdb-docs-catalog.jsonl
   Result: Success ✅
   ```

3. **Search catalog for vector search**
   - Parse JSONL entries
   - Query: "vector search"
   - Found matches:
     ```json
     {"path": "200.develop/600.search/300.vector-search/100.vector-search-intro.md",
      "description": "This document provides an overview of vector search in seekdb, covering core concepts, supported vector data types, indexing methods, and search operations."}
     {"path": "200.develop/600.search/300.vector-search/300.vector-similarity-search.md",
      "description": "This document explains vector similarity search methods in seekdb..."}
     ```

4. **Read documents (local-first)**
   - Try local: `/root/.claude/skills/seekdb/seekdb-docs/200.develop/600.search/300.vector-search/100.vector-search-intro.md`
   - If missing → Remote: `https://raw.githubusercontent.com/oceanbase/seekdb-doc/V1.1.0/en-US/200.develop/600.search/300.vector-search/100.vector-search-intro.md`

5. **Provide answer**

---

## Example 2: Basic Overview Query

**User Query**: "What is seekdb?"

**Process**:

1. **Resolve skill directory**
   ```
   Read SKILL.md → get absolute path
   Extract skill directory
   ```

2. **Load catalog**
   ```
   Local: <skill directory>references/seekdb-docs-catalog.jsonl
   Success ✅
   ```

3. **Search catalog for overview**
   - Query: "seekdb overview" or "what is seekdb"
   - Found entry:
     ```json
     {"path": "100.get-started/10.seekdb-overview/10.seekdb-overview.md",
      "description": "An AI-native search database that unifies relational, vector, text, JSON, and GIS data in a single engine, enabling hybrid search and in-database AI workflows with full MySQL compatibility."}
     ```

4. **Read document**
   - Local: `<skill directory>seekdb-docs/100.get-started/10.seekdb-overview/10.seekdb-overview.md`
   - Success ✅

5. **Extract answer** from local docs

---

## Example 3: Remote Fallback Scenario

**User Query**: "How do I deploy seekdb on macOS?"

**Process**:

1. **Resolve skill directory**
   ```
   Read SKILL.md → /path/to/skills/seekdb/SKILL.md
   Skill directory = /path/to/skills/seekdb/
   ```

2. **Load catalog (local-first)**
   ```
   Try local: /path/to/skills/seekdb/references/seekdb-docs-catalog.jsonl
   Result: File not found ❌
   ```

3. **Fallback to remote catalog**
   ```
   Fetch: https://raw.githubusercontent.com/oceanbase/seekdb-ecology-plugins/main/agent-skills/skills/seekdb/references/seekdb-docs-catalog.jsonl
   Result: Success ✅
   ```

4. **Search catalog**
   - Query: "macOS", "deploy", "systemd"
   - Found entry:
     ```json
     {"path": "400.guides/400.deploy/700.server-mode/100.deploy-by-systemd.md",
      "description": "This document provides instructions for deploying and managing the seekdb database using systemd on RPM-based, DEB-based, and macOS systems, covering installation, configuration, connection, and removal procedures."}
     ```

5. **Read document (remote only, since local missing)**
   ```
   URL: https://raw.githubusercontent.com/oceanbase/seekdb-doc/V1.1.0/en-US/400.guides/400.deploy/700.server-mode/100.deploy-by-systemd.md
   Fetch and parse
   ```

6. **Provide answer**

---

## Example 4: Integration Query

**User Query**: "I want to integrate seekdb with Claude Code"

**Process**:

1. **Resolve path & load catalog** (local success)

2. **Search catalog for integration**
   - Query: "Claude Code", "integration", "AI coding"
   - Found entry:
     ```json
     {"path": "100.get-started/200.ai-coding/200.building-an-ai-programming-assistant-that-understands-vector-databases-with-seekdb-claude-code.md",
      "description": "This tutorial explains how to build a vector-aware AI coding assistant by integrating the seekdb plugin with Claude Code, enabling accurate documentation retrieval and hybrid search application development in Python."}
     ```

3. **Read document** (local)

4. **Extract integration steps** and provide code examples

---

## Example 5: SQL Syntax Query

**User Query**: "What's the syntax for creating a vector column?"

**Process**:

1. **Resolve path & load catalog** (local success)

2. **Search for SQL/vector column syntax**
   - Query: "vector column", "CREATE TABLE", "vector type"
   - Found entry:
     ```json
     {"path": "200.develop/600.search/300.vector-search/150.vector-data-type.md",
      "description": "This document describes seekdb's vector data types for AI vector search, covering storage of dense and sparse floating-point arrays, index creation, and hybrid search capabilities."}
     ```

3. **Read document** (local)

4. **Provide syntax** with examples

---

## Example 6: Hybrid Search Query

**User Query**: "How does hybrid search work?"

**Process**:

1. **Resolve path & load catalog** (local success)

2. **Search for hybrid search**
   - Query: "hybrid search", "combined search"
   - Found entry:
     ```json
     {"path": "200.develop/600.search/500.hybrid-search.md",
      "description": "This document describes hybrid search in seekdb, combining vector-based semantic search and full-text keyword search for more accurate results through integrated ranking."}
     ```

3. **Read document** (local)

4. **Explain hybrid search concepts** with usage examples

---

## Example 7: Multiple Matches Query

**User Query**: "Tell me about seekdb indexes"

**Process**:

1. **Resolve path & load catalog** (local success)

2. **Search for all index types**
   - Query: "index"
   - Found multiple matches:
     ```json
     {"path": "200.develop/600.search/300.vector-search/200.vector-index/100.vector-index-overview.md", "description": "...vector index types..."}
     {"path": "200.develop/200.design-database-schema/35.multi-model/300.char-and-text/300.full-text-index.md", "description": "This document details the creation and use of full-text indexes in seekdb, covering supported column types, tokenizers, and complex DML operations on indexed tables."}
     {"path": "200.develop/200.design-database-schema/40.create-index-in-develop.md", "description": "...creating indexes..."}
     ```

3. **Read all relevant documents** (local)

4. **Provide comprehensive answer** covering:
   - Vector indexes (HNSW, IVF)
   - Full-text indexes
   - Index creation syntax
   - Best practices

---

## Example 8: Python SDK Query

**User Query**: "How do I use seekdb with Python?"

**Process**:

1. **Resolve path & load catalog** (local success)

2. **Search for Python SDK**
   - Query: "Python", "SDK", "pyseekdb"
   - Found entries:
     ```json
     {"path": "100.get-started/50.use-seekdb-with-sdk/25.using-seekdb-in-python-sdk.md",
      "description": "This document provides a step-by-step guide to using OceanBase's pyseekdb Python SDK for embedded seekdb operations..."}
     {"path": "200.develop/100.connect-to-seekdb/300.sample-program/200.python/100.mysqlclient-connection-to-seekdb-sample-program.md", "description": "This document provides a sample program demonstrating how to connect to seekdb using mysqlclient in Python, including steps for creating tables, inserting data, and querying data."}
     ```

3. **Read documents** (local)

4. **Provide Python setup** and code examples

---

## Example 9: Deployment Query

**User Query**: "How do I deploy seekdb in production?"

**Process**:

1. **Resolve path & load catalog** (local success)

2. **Search deployment guides**
   - Query: "production deployment", "install"
   - Found entries:
     ```json
     {"path": "400.guides/400.deploy/50.deploy-overview.md", "description": "This documentation outlines seekdb's two deployment modes: embedded mode and server mode, and details the specific deployment methods available for each mode."}
     ```

3. **Read deployment guides** (local)

4. **Extract deployment steps**:
   - Prerequisites
   - Installation methods
   - Configuration
   - Best practices

---

## Key Patterns

### Path Resolution (Always First)
1. Read SKILL.md to get absolute path
2. Extract skill directory from path
3. Construct catalog path: `<skill directory>references/seekdb-docs-catalog.jsonl`

### Catalog Loading (Local-First)
1. Try local catalog: `<skill directory>references/seekdb-docs-catalog.jsonl`
2. If missing, fetch remote: `https://raw.githubusercontent.com/oceanbase/seekdb-ecology-plugins/main/agent-skills/skills/seekdb/references/seekdb-docs-catalog.jsonl`
3. Parse JSONL (one JSON object per line)

### Searching
- **Semantic matching**: Match query meaning to description text
- **Multiple results**: Read all relevant entries for comprehensive answers
- **Fields available**: `path` and `description` only

### Document Reading (Local-First)
1. Try local: `<skill directory>seekdb-docs/[File Path]`
2. If missing, fetch remote: `https://raw.githubusercontent.com/oceanbase/seekdb-doc/V1.1.0/en-US/[File Path]`

### Best Practices
- ✅ **Always resolve path first** - Never hardcode paths
- ✅ **Local-first for speed** - Try local before remote
- ✅ **Semantic over keyword** - Understand meaning, not just match words
- ✅ **Read multiple sources** - Comprehensive answers from all relevant docs
- ✅ **Parse JSONL correctly** - Each line is a valid JSON object with `path` and `description`
