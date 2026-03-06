---
name: filesystem-mcp
description: Official Filesystem MCP Server for secure file operations with configurable access controls. Read, write, create, delete, move, search files and directories. List directory contents, get file info, edit text files, and manage file permissions. Built-in security sandbox prevents unauthorized access. Essential for agents working with local files, project management, log analysis, content generation, and file organization. Use when agents need filesystem access, file manipulation, directory navigation, or content management.
---

# Filesystem MCP Server

> **Secure File Operations for AI Agents**

Official MCP reference implementation providing safe, sandboxed filesystem access with fine-grained permission controls.

## Why Filesystem MCP?

### 🔒 Security-First Design
- **Sandboxed Access**: Agents can only access explicitly allowed directories
- **Permission Controls**: Read-only, write, or full access per directory
- **Path Validation**: Prevents directory traversal and unauthorized access
- **Audit Trail**: All operations logged for security review

### 🤖 Essential for Agent Workflows
Most agent tasks involve files:
- Reading documentation
- Writing code files
- Analyzing logs
- Generating reports
- Managing project files
- Organizing content

### 📦 Zero External Dependencies
Pure implementation using Node.js built-in modules. No external API dependencies or rate limits.

## Installation

```bash
# Official reference implementation
npm install -g @modelcontextprotocol/server-filesystem

# Or build from source
git clone https://github.com/modelcontextprotocol/servers
cd servers/src/filesystem
npm install
npm run build
```

## Configuration

Add to your MCP client config:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/yourname/Documents",
        "/Users/yourname/Projects"
      ]
    }
  }
}
```

**Arguments** = allowed directories (one or more paths)

### Permission Modes

**Read-Only Access:**
```json
"args": ["--read-only", "/path/to/docs"]
```

**Full Access (default):**
```json
"args": ["/path/to/workspace"]
```

### Example Configurations

#### Development Workspace
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/dev/projects",
        "/Users/dev/workspace"
      ]
    }
  }
}
```

#### Documentation Access (Read-Only)
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "--read-only",
        "/Users/docs/knowledge-base"
      ]
    }
  }
}
```

## Available Tools

### Directory Operations

#### 1. **List Directory** (`list_directory`)
```
Agent: "What files are in my Projects folder?"
Agent: "Show contents of /workspace/src"
```

**Returns:**
- File names
- File types (file, directory, symlink)
- File sizes
- Last modified timestamps

#### 2. **Create Directory** (`create_directory`)
```
Agent: "Create a new folder called 'components'"
Agent: "Make directory /workspace/tests"
```

#### 3. **Move/Rename** (`move_file`)
```
Agent: "Rename old-name.txt to new-name.txt"
Agent: "Move report.pdf to /Documents/Reports/"
```

### File Operations

#### 4. **Read File** (`read_file`)
```
Agent: "Read the contents of config.json"
Agent: "Show me the README.md file"
```

**Supports:**
- Text files (UTF-8)
- JSON, YAML, XML
- Markdown, code files
- Large files (streaming)

#### 5. **Write File** (`write_file`)
```
Agent: "Create a file called notes.txt with meeting notes"
Agent: "Write the generated code to src/index.ts"
```

#### 6. **Edit File** (`edit_file`)
```
Agent: "Replace 'version: 1.0' with 'version: 2.0' in package.json"
Agent: "Add a new function to utils.js"
```

#### 7. **Get File Info** (`get_file_info`)
```
Agent: "When was report.pdf last modified?"
Agent: "What's the size of data.csv?"
```

**Returns:**
- File size (bytes)
- Creation time
- Last modified time
- Permissions
- File type

### Advanced Operations

#### 8. **Search Files** (`search_files`)
```
Agent: "Find all Python files in the project"
Agent: "Search for files containing 'API_KEY'"
```

**Search by:**
- File name pattern (glob)
- File content (regex)
- File type
- Date modified

#### 9. **Delete File** (`delete_file`)
```
Agent: "Delete the temporary log files"
Agent: "Remove old-backup.zip"
```

**Safety:**
- Requires confirmation for large files
- Cannot delete files outside allowed directories
- Logged for audit

## Agent Workflow Examples

### Code Generation
```
Human: "Create a React component for a login form"

Agent:
1. create_directory("/workspace/components")
2. write_file("/workspace/components/LoginForm.tsx", generated_code)
3. write_file("/workspace/components/LoginForm.test.tsx", test_code)
4. "Created LoginForm component at components/LoginForm.tsx"
```

### Log Analysis
```
Human: "Analyze error logs and summarize issues"

Agent:
1. list_directory("/var/log/app")
2. read_file("/var/log/app/error.log")
3. search_files(pattern="ERROR", path="/var/log/app")
4. generate_summary()
5. write_file("/reports/error-summary.md", summary)
```

### Project Organization
```
Human: "Organize my documents by type"

Agent:
1. list_directory("/Documents")
2. For each file:
   - get_file_info(file)
   - Determine file type
   - create_directory("/Documents/[type]")
   - move_file(file, destination_folder)
```

### Documentation Generation
```
Human: "Generate API documentation from code comments"

Agent:
1. search_files(pattern="*.ts", path="/src")
2. For each file:
   - read_file(file)
   - extract_doc_comments()
3. Generate markdown docs
4. write_file("/docs/API.md", generated_docs)
```

## Security Model

### Sandbox Enforcement

**What Agents CAN Do:**
- ✅ Access explicitly allowed directories
- ✅ Create/read/write files within allowed paths
- ✅ List directory contents
- ✅ Search within allowed paths

**What Agents CANNOT Do:**
- ❌ Access parent directories (`../`)
- ❌ Access system files (`/etc/`, `/sys/`)
- ❌ Follow symlinks outside allowed paths
- ❌ Execute binaries or scripts
- ❌ Modify file permissions

### Path Validation

```
Allowed: /Users/dev/projects
Agent tries: /Users/dev/projects/src/index.ts → ✅ Allowed
Agent tries: /Users/dev/projects/../secret → ❌ Blocked
Agent tries: /etc/passwd → ❌ Blocked
```

### Best Practices

1. **Principle of Least Privilege**
   - Grant only necessary directories
   - Use `--read-only` when write not needed

2. **Never Allow Root Access**
   - Don't add `/` or system directories
   - Restrict to user workspace

3. **Audit Agent Actions**
   - Review MCP server logs regularly
   - Monitor for unexpected file access patterns

4. **Separate Sensitive Data**
   - Keep credentials, keys in separate directories
   - Don't include in allowed paths

## Use Cases

### 📝 Content Management
Agents generate blog posts, reports, documentation and save to organized folders.

### 🤖 Code Assistants
Read project files, generate code, create tests, update configurations.

### 📊 Data Analysis
Read CSV/JSON data files, analyze, generate reports and visualizations.

### 🗂️ File Organization
Scan directories, categorize files, move to appropriate folders, cleanup duplicates.

### 📚 Knowledge Base
Index markdown files, search documentation, extract information, update wikis.

### 🔍 Log Analysis
Parse log files, identify errors, generate summaries, create alerts.

## Performance

### Large Files
- Streaming for files >10MB
- Incremental reads supported
- Memory-efficient processing

### Directory Scanning
- Recursive search optimized
- Glob pattern matching
- Ignore patterns (e.g., `node_modules/`)

### Concurrent Operations
- Safe for parallel file access
- Atomic write operations
- File locking where needed

## Troubleshooting

### "Permission denied" Error
- Verify path is in allowed directories
- Check filesystem permissions
- Ensure MCP server has read/write access

### "Path not found" Error
- Confirm directory exists
- Check for typos in path
- Verify path format (absolute vs relative)

### Read-Only Mode Issues
- Can't write in `--read-only` mode
- Reconfigure server with write access if needed

## vs Other File Access Methods

| Method | Security | Agent Integration | Setup |
|--------|----------|-------------------|-------|
| **Filesystem MCP** | ✅ Sandboxed | ✅ Auto-discovered | Simple |
| **Direct FS Access** | ❌ Full system | ❌ Manual | None |
| **File Upload/Download** | ✅ Manual control | ⚠️ Limited | Complex |
| **Cloud Storage API** | ✅ API-level | ⚠️ Requires SDK | Complex |

## Resources

- **GitHub**: https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem
- **MCP Docs**: https://modelcontextprotocol.io/
- **Security Best Practices**: https://modelcontextprotocol.io/docs/concepts/security

## Advanced Configuration

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "node",
      "args": [
        "/path/to/filesystem-server/build/index.js",
        "/workspace",
        "/documents"
      ],
      "env": {
        "MAX_FILE_SIZE": "10485760",
        "ENABLE_LOGGING": "true",
        "LOG_PATH": "/var/log/mcp-filesystem.log"
      }
    }
  }
}
```

---

**Safe, secure filesystem access for agents**: From code generation to log analysis, Filesystem MCP is the foundation for agent file operations.
