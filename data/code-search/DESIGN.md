# Code Search Skill — 设计文档

## 1. 架构概览

```
Agent 调用流程:
  用户提问 → Agent 判断需要搜索代码 → 读取 SKILL.md → 调用 exec 执行脚本 → 解析结构化输出 → 回复用户

文件结构:
  skills/code-search/
  ├── SKILL.md              # Agent 入口，描述何时/如何使用
  ├── REQUIREMENTS.md       # 需求文档（本轮产出）
  ├── DESIGN.md             # 设计文档（本文件）
  ├── scripts/
  │   ├── search.sh         # 统一入口脚本
  │   └── check-deps.sh     # 依赖检查脚本
  └── README.md             # 使用说明
```

## 2. 设计决策

### 2.1 为什么用 Shell 脚本而不是 Python/Node？

- rg、fd、tree 本身就是 CLI 工具，Shell 封装最轻量
- 不引入额外运行时依赖
- Agent 通过 `exec` 工具调用，Shell 脚本是最自然的接口
- 保持简单，一个脚本搞定

### 2.2 为什么用一个统一入口脚本？

- Agent 只需记住一个命令：`bash scripts/search.sh <子命令> [参数]`
- 减少 SKILL.md 的复杂度
- 子命令：`grep`、`glob`、`tree`、`check`

## 3. 接口设计

### 3.1 统一入口

```bash
bash /root/.openclaw/workspace/skills/code-search/scripts/search.sh <command> [options]
```

### 3.2 grep — 内容搜索

```bash
bash search.sh grep <pattern> [options]

选项：
  --path <dir>        搜索目录，默认当前目录
  --type <ext>        文件类型过滤，如 go, py, ts（可多次指定）
  --literal           字面量模式（不解释正则）
  --max <n>           最大结果数，默认 100
  --context <n>       显示匹配行上下文行数，默认 0
```

**输出格式**（结构化文本，对 AI 友好）：
```
[SEARCH RESULTS: grep]
Pattern: "func main"
Directory: /root/.openclaw/workspace/opencode
Files matched: 3
Total matches: 5
---
FILE: internal/app/app.go (modified: 2026-02-26 09:04)
  42: func main() {
  
FILE: cmd/root.go (modified: 2026-02-26 09:04)
  15: func main() {
  88: // main entry point
---
[END RESULTS]
```

**底层命令映射**：
```bash
rg --json "$pattern" "$path" --max-count "$max" --type "$type" --sort modified
```
脚本解析 rg 的 JSON 输出，重新格式化为上述结构化文本。

### 3.3 glob — 文件名搜索

```bash
bash search.sh glob <pattern> [options]

选项：
  --path <dir>        搜索目录，默认当前目录
  --type <ext>        文件类型过滤
  --max <n>           最大结果数，默认 200
```

**输出格式**：
```
[SEARCH RESULTS: glob]
Pattern: "*.go"
Directory: /root/.openclaw/workspace/opencode
Files found: 137
---
internal/app/app.go
internal/app/lsp.go
internal/config/config.go
...
---
[END RESULTS]
```

**底层命令映射**：
```bash
fd "$pattern" "$path" --max-results "$max" --sort modified
```

### 3.4 tree — 目录结构

```bash
bash search.sh tree [options]

选项：
  --path <dir>        目标目录，默认当前目录
  --depth <n>         最大深度，默认 3
  --size              显示文件大小
```

**输出格式**：
```
[DIRECTORY TREE]
Path: /root/.openclaw/workspace/opencode
Depth: 2
---
.
├── cmd/
│   └── root.go
├── internal/
│   ├── app/
│   ├── config/
│   ├── db/
│   ├── llm/
│   └── tui/
├── go.mod
├── go.sum
└── main.go
---
[END TREE]
```

**底层命令映射**：
```bash
tree -L "$depth" -I ".git|node_modules|__pycache__|.venv|vendor" "$path"
```

### 3.5 check — 依赖检查

```bash
bash search.sh check
```

**输出**：
```
[DEPENDENCY CHECK]
rg (ripgrep):    ✅ installed (14.1.0)
fd (fd-find):    ✅ installed (9.0.0)
tree:            ❌ not found
  Install: yum install -y tree  (or: apt install tree)
---
[STATUS: PARTIAL] 2/3 dependencies available
```

## 4. 默认忽略规则

所有搜索命令默认忽略以下目录/文件：
```
.git, .svn, .hg
node_modules, bower_components
__pycache__, .pytest_cache, .mypy_cache
.venv, venv, env
vendor
.DS_Store, Thumbs.db
*.pyc, *.pyo, *.class, *.o, *.so
dist, build, target, out
```

rg 和 fd 默认已尊重 .gitignore，额外的忽略规则通过参数传入。

## 5. 错误处理

| 场景 | 处理方式 |
|------|----------|
| rg/fd/tree 未安装 | 输出安装指引，不崩溃 |
| 搜索目录不存在 | 输出 `[ERROR] Directory not found: <path>` |
| 无匹配结果 | 输出 `[SEARCH RESULTS: grep]\nNo matches found.\n[END RESULTS]` |
| 结果被截断 | 在输出末尾标注 `[TRUNCATED: showing 100 of 523 matches]` |
| rg/fd 执行超时 | 5秒超时，输出已收集的部分结果 + 超时提示 |

## 6. SKILL.md 设计要点

SKILL.md 是 Agent 选择此 Skill 的入口，需要：
- description 精确匹配搜索场景关键词：搜索代码、查找文件、项目结构、grep、find
- 明确说明三个子命令的使用场景
- 给出常用示例，Agent 可以直接复制使用
- 说明此 Skill 是只读的，不会修改文件

## 7. 依赖安装方案

```bash
# OpenCloudOS / CentOS / RHEL
yum install -y ripgrep fd-find tree

# 如果 yum 源没有 ripgrep/fd：
# ripgrep
curl -LO https://github.com/BurntSushi/ripgrep/releases/download/14.1.1/ripgrep-14.1.1-x86_64-unknown-linux-musl.tar.gz
tar xzf ripgrep-*.tar.gz && cp ripgrep-*/rg /usr/local/bin/

# fd
curl -LO https://github.com/sharkdp/fd/releases/download/v10.2.0/fd-v10.2.0-x86_64-unknown-linux-musl.tar.gz
tar xzf fd-*.tar.gz && cp fd-*/fd /usr/local/bin/
```

## 8. 测试计划

| 测试用例 | 命令 | 预期 |
|----------|------|------|
| 基本内容搜索 | `search.sh grep "func main" --path /root/.openclaw/workspace/opencode` | 返回 main.go 等文件 |
| 字面量搜索 | `search.sh grep "fmt.Println(" --literal --path ...` | 不把括号当正则 |
| 类型过滤 | `search.sh grep "import" --type go --path ...` | 只搜 .go 文件 |
| 文件名搜索 | `search.sh glob "*.go" --path ...` | 返回 137 个 Go 文件 |
| 目录结构 | `search.sh tree --path ... --depth 2` | 展示 2 层结构 |
| 依赖缺失 | 临时 rename rg，运行 grep | 输出安装指引 |
| 空结果 | `search.sh grep "xyznotexist123"` | 输出 No matches found |
| 大量结果截断 | `search.sh grep "the" --max 10` | 标注 TRUNCATED |
