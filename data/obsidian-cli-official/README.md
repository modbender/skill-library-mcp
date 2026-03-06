# Obsidian Official CLI Skill

Complete reference for the official Obsidian CLI (v1.12+). All 115 commands documented.

## What is this?

This OpenClaw skill provides **complete access to Obsidian's official CLI** (v1.12+), enabling AI agents to:

- 📝 **Automate note-taking**: Create daily journals, meeting notes, project logs
- ✅ **Manage tasks**: Toggle task status, filter by completion, track progress
- 🔍 **Search and organize**: Find notes, create links, manage tags
- 🗄️ **Work with databases**: Query bases, create items, manage views
- 🎨 **Customize workspace**: Install themes/plugins, manage workspaces

**For OpenClaw users**: Your AI assistant can now read, write, and organize your Obsidian vault automatically.

**For developers**: Complete CLI reference with 115 commands for building Obsidian automation.

## Prerequisites

- **Obsidian 1.12+** (Early Access)
- **Catalyst license** (paid supporter - $25 one-time)
- **Platform**: macOS, Windows, or Linux
- **Obsidian must be running** (CLI connects via IPC)
- **Obsidian Publish subscription** (optional, $8/month for publish commands)

## Installation

### Via ClawHub (OpenClaw) - All Platforms

```bash
clawhub install obsidian-cli-official
```

### Via Homebrew (macOS/Linux) 🍺

```bash
# Add tap
brew tap alexanderkinging/tap

# Install
brew install obsidian-cli-official

# Test
obs help
```

### Manual Setup

#### macOS

**1. Get Catalyst License**

Visit https://obsidian.md/pricing and purchase Catalyst ($25 one-time).

**2. Enable CLI in Obsidian**

Settings → General → Enable CLI

**3. Add to PATH**

```bash
echo 'export PATH="$PATH:/Applications/Obsidian.app/Contents/MacOS"' >> ~/.zprofile
source ~/.zprofile
```

**4. Test**

```bash
obsidian version
obsidian vault
```

---

#### Windows

**1. Get Catalyst License**

Visit https://obsidian.md/pricing and purchase Catalyst ($25 one-time).

**2. Enable CLI in Obsidian**

Settings → General → Enable CLI

**3. Add to PATH**

**Option A: System Environment Variables**
1. Press `Win + X` → System → Advanced system settings
2. Environment Variables → PATH → Edit
3. Add: `C:\Users\<YourUsername>\AppData\Local\Obsidian`

**Option B: PowerShell Profile**
```powershell
# Edit profile
notepad $PROFILE

# Add this line
$env:PATH += ";$env:LOCALAPPDATA\Obsidian"

# Reload
. $PROFILE
```

**4. Test**

```powershell
obsidian version
obsidian vault
```

---

#### Linux

**1. Get Catalyst License**

Visit https://obsidian.md/pricing and purchase Catalyst ($25 one-time).

**2. Enable CLI in Obsidian**

Settings → General → Enable CLI

**3. Add to PATH**

**Snap:**
```bash
# Already in PATH
obsidian version
```

**Flatpak:**
```bash
# Add alias to ~/.bashrc
echo 'alias obsidian="flatpak run md.obsidian.Obsidian"' >> ~/.bashrc
source ~/.bashrc
```

**AppImage:**
```bash
# Move to ~/.local/bin
mv Obsidian-*.AppImage ~/.local/bin/obsidian
chmod +x ~/.local/bin/obsidian

# Add to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**4. Test**

```bash
obsidian version
obsidian vault
```

## OpenClaw Use Cases

### 📅 Daily Journal Automation

Your AI assistant can maintain your daily journal automatically:

```bash
# Create today's daily note
obsidian daily

# Add morning tasks
obsidian daily:append content="## Morning Tasks\n- [ ] Review emails\n- [ ] Plan the day"

# Add meeting notes
obsidian daily:append content="## Meeting with Team\n- Discussed project timeline\n- Next steps: ..."
```

### 📝 Meeting Notes

AI agent creates structured meeting notes from conversations:

```bash
# Create meeting note
obsidian create name="Meeting 2026-03-01" content="# Team Sync\n\n## Attendees\n- Alice\n- Bob\n\n## Discussion\n..."

# Add metadata
obsidian property:set name="type" value="meeting" file="Meeting 2026-03-01"
obsidian property:set name="date" value="2026-03-01" file="Meeting 2026-03-01"

# Bookmark for quick access
obsidian bookmark file="Meeting 2026-03-01.md"
```

### ✅ Task Management

AI agent helps you manage tasks across your vault:

```bash
# List all incomplete tasks
obsidian tasks daily todo

# Toggle task completion
obsidian task daily line=3 toggle

# Find tasks by tag
obsidian search query="- [ ]" path="Projects"
```

### 🔍 Knowledge Search & Organization

AI agent finds and connects relevant information:

```bash
# Search for project notes
obsidian search query="project alpha" path="Work"

# Find related notes
obsidian backlinks file="Project Alpha"

# Check orphaned notes
obsidian orphans
```

### 📊 Database Operations

AI agent manages your Obsidian databases:

```bash
# List all databases
obsidian bases

# Query database
obsidian base:query file="Projects" format=json

# Create new item
obsidian base:create name="New Project" content="Description..."
```

### 🎨 Workspace Customization

AI agent sets up your workspace:

```bash
# Install plugin
obsidian plugin:install id="dataview" enable

# Switch theme
obsidian theme:set name="Minimal"

# Save workspace layout
obsidian workspace:save name="coding"
```

## Quick Examples

```bash
# Daily notes
obsidian daily
obsidian daily:append content="- [ ] Task"

# Files
obsidian create name="Note" content="Hello"
obsidian read file="Recipe"
obsidian search query="meeting"

# Tasks
obsidian tasks daily todo
obsidian task daily line=3 toggle

# Tags & Properties
obsidian tags counts sort=count
obsidian property:set name="status" value="done" file="Note"

# Bookmarks
obsidian bookmark file="important.md"
obsidian bookmarks

# Bases (Database)
obsidian bases
obsidian base:query file="MyBase" format=json

# History
obsidian history file="Note"
obsidian history:restore file="Note" version=3

# Plugins
obsidian plugins filter=community
obsidian plugin:install id="dataview" enable

# Publish (requires subscription)
obsidian publish:status
obsidian publish:add changed

# Developer
obsidian devtools
obsidian eval code="app.vault.getFiles().length"
```

## OpenClaw Integration Tips

### Best Practices

1. **Keep Obsidian running**: CLI requires Obsidian app to be open
2. **Use `file=` for flexibility**: Resolves by name, works across folders
3. **Batch operations**: Combine commands for complex workflows
4. **Error handling**: Check if Obsidian is running before CLI calls

### Common Patterns

**Daily workflow automation:**
```bash
# Morning routine
obsidian daily
obsidian daily:append content="## Today's Goals\n- [ ] Review PRs\n- [ ] Write docs"
obsidian tasks daily todo
```

**Note creation with metadata:**
```bash
# Create note with properties
obsidian create name="Article Idea" content="# New Article\n\nIdea: ..."
obsidian property:set name="status" value="draft" file="Article Idea"
obsidian property:set name="tags" value="writing" file="Article Idea"
obsidian bookmark file="Article Idea.md"
```

**Search and link:**
```bash
# Find related notes and create connections
obsidian search query="machine learning" path="Research"
obsidian backlinks file="ML Overview"
obsidian links file="ML Overview"
```

**Workspace setup:**
```bash
# Set up coding environment
obsidian workspace:load name="coding"
obsidian plugin:enable id="dataview"
obsidian theme:set name="Minimal"
```

### Error Handling

```bash
# Check if Obsidian is running
if pgrep -x "Obsidian" > /dev/null; then
    obsidian daily
else
    echo "Please start Obsidian first"
fi
```

## Complete Documentation

See [SKILL.md](SKILL.md) for all 115 commands with full parameter documentation.

## Troubleshooting

### "Cannot connect to Obsidian"
- Ensure Obsidian is running
- Enable CLI in Settings → General → Enable CLI

### "Command not found: obsidian"
```bash
# Add to PATH
export PATH="$PATH:/Applications/Obsidian.app/Contents/MacOS"

# Or use full path
/Applications/Obsidian.app/Contents/MacOS/obsidian version
```

### "File not found"
- Use `file=<name>` for wikilink-style resolution (no path, no .md)
- Use `path=<path>` for exact paths (include folder and .md)

### Multi-vault
```bash
# Target specific vault (must be FIRST parameter)
obsidian vault="Work" daily
obsidian vault="Notes" search query="test"
```

### Publish commands not working
- Requires **Obsidian Publish subscription** ($8/month or $96/year)
- Without subscription: `Error: Command "publish:status" not found`
- Subscribe at: https://obsidian.md/publish

## Resources

- **Official Docs**: https://help.obsidian.md/cli
- **Catalyst License**: https://obsidian.md/pricing
- **GitHub**: https://github.com/alexanderkinging/obsidian-official-cli
- **ClawHub**: https://clawhub.ai/obsidian-cli-official

---

## 中文说明

### 这是什么？

这个 OpenClaw skill 提供了 **Obsidian 官方 CLI 的完整访问**（v1.12+），让 AI agent 能够：

- 📝 **自动化笔记**: 创建日记、会议记录、项目日志
- ✅ **管理任务**: 切换任务状态、筛选、追踪进度
- 🔍 **搜索和整理**: 查找笔记、创建链接、管理标签
- 🗄️ **操作数据库**: 查询 base、创建条目、管理视图
- 🎨 **自定义工作区**: 安装主题/插件、管理工作区

**对于 OpenClaw 用户**: 你的 AI 助手现在可以自动读取、编写和整理你的 Obsidian 库。

**对于开发者**: 完整的 CLI 参考，包含 115 个命令，用于构建 Obsidian 自动化。

### 前置条件

- Obsidian 1.12+ (Early Access)
- Catalyst 许可证（$25 一次性付费）
- 平台：macOS、Windows 或 Linux
- Obsidian 必须运行中
- Obsidian Publish 订阅（可选，$8/月，用于 publish 命令）

### 安装

**通过 ClawHub（所有平台）：**
```bash
clawhub install obsidian-cli-official
```

**通过 Homebrew（macOS/Linux）：**
```bash
brew install alexanderkinging/tap/obsidian-cli-official
```

### 配置

**macOS:**
1. 设置 → 通用 → 启用 CLI
2. 添加到 PATH：`export PATH="$PATH:/Applications/Obsidian.app/Contents/MacOS"`
3. 测试：`obsidian version`

**Windows:**
1. 设置 → 通用 → 启用 CLI
2. 添加到 PATH：系统属性 → 环境变量 → PATH → 添加 `C:\Users\<用户名>\AppData\Local\Obsidian`
3. 测试：`obsidian version`

**Linux:**
1. 设置 → 通用 → 启用 CLI
2. 根据安装方式配置（Snap/Flatpak/AppImage）
3. 测试：`obsidian version`

### OpenClaw 使用场景

**日记自动化:**
```bash
obsidian daily
obsidian daily:append content="## 今日任务\n- [ ] 审查代码\n- [ ] 写文档"
```

**会议记录:**
```bash
obsidian create name="会议 2026-03-01" content="# 团队同步\n\n..."
obsidian property:set name="类型" value="会议" file="会议 2026-03-01"
```

**任务管理:**
```bash
obsidian tasks daily todo
obsidian task daily line=3 toggle
```

**知识搜索:**
```bash
obsidian search query="项目" path="工作"
obsidian backlinks file="项目概览"
```

详细文档见 [SKILL.md](SKILL.md)。
