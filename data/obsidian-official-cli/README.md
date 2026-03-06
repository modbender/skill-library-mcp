# Obsidian **Official CLI** Skill

An OpenClaw skill for working with Obsidian vaults using the **official Obsidian CLI (v1.12+)** - not third-party tools, but Obsidian's own built-in command-line interface with full feature support.

## ✨ Official CLI Features

**This skill uses Obsidian's official CLI** - not third-party integrations - giving you access to **all Obsidian features** from the terminal:

- **File Operations**: Create, read, edit, move, and delete notes with full Obsidian integration
- **Advanced Task Management**: Complete task operations with checkboxes, statuses, and custom markers  
- **Database/Bases Support**: Query and manage Obsidian Bases with views and CSV/JSON export
- **Search & Discovery**: Full-text search, tag management, link analysis with Obsidian's search engine
- **Daily Notes & Templates**: Manage daily notes and insert templates with variable resolution
- **Plugin & Theme Management**: Install, enable, disable, and reload plugins/themes directly
- **Obsidian Sync Integration**: Full sync operations, history, and conflict resolution
- **Properties (Frontmatter)**: Read, write, and manage note properties with type validation
- **Workspace Management**: Control layouts, tabs, and saved workspaces
- **Developer Tools**: Console debugging, DOM inspection, screenshots, mobile emulation
- **TUI Mode**: Interactive terminal UI with autocomplete, history, and command palette access

## 📋 Requirements

- **Obsidian 1.12+** with early access (insider builds)
- **Catalyst license** (required for official CLI access)
- **Official CLI enabled** in Obsidian: Settings → General → Command line interface → Enable
- **Obsidian running** (CLI connects to the live Obsidian app for full feature access)

## 🚀 Installation

1. Download the skill file: [`obsidian-official-cli.skill`](obsidian-official-cli.skill)
2. Install via OpenClaw CLI:
   ```bash
   openclaw skills install obsidian-official-cli.skill
   ```

## 💡 Usage Examples

Once installed, the skill will automatically trigger when you mention Obsidian operations:

- "Create a new note called 'Meeting Notes' using Obsidian CLI"
- "Search for all notes containing 'project' with Obsidian's search engine"
- "Show me all incomplete tasks and toggle their status via CLI"
- "Query my Books database and export to CSV"
- "Install the Dataview plugin and enable it"
- "Take a screenshot of my current Obsidian workspace"
- "Show me all orphaned notes in my vault graph"

## 🛠️ Obsidian CLI Setup

1. **Upgrade to Obsidian 1.12+**: Get early access via insider builds
2. **Enable CLI**: Settings → General → Command line interface → Enable
3. **Register command**: Follow the prompt to add `obsidian` to your PATH
4. **Restart terminal**: Or run `source ~/.zprofile` on macOS
5. **Test setup**: Run `obsidian version`

**Note**: Obsidian must be running for CLI commands to work.

## 🔧 Official CLI Command Coverage

**Complete access to Obsidian's official CLI** - every command from the native interface:

### File & Vault Management
- Native file operations with Obsidian's file resolver
- Folder management and vault organization
- Random note selection and unique name generation

### Advanced Content Features
- **Task Management**: Toggle, update status, custom markers (`todo`, `done`, `[-]`)
- **Properties**: Full frontmatter support with type validation (`list`, `text`, etc.)
- **Templates**: Insert with variable resolution and custom paths
- **Daily Notes**: Dedicated commands with append/prepend support

### Database/Knowledge Features
- **Obsidian Bases**: Query views, export CSV/JSON, create entries
- **Search Engine**: Obsidian's full-text search with context and filters  
- **Link Graph**: Backlinks, orphans, deadends via Obsidian's link resolver
- **Tag System**: Complete tag analysis with occurrence counts

### Obsidian Ecosystem Integration
- **Plugin Lifecycle**: Install, enable, disable, reload with Obsidian's plugin manager
- **Theme Engine**: Access to Obsidian's theme system and CSS snippets
- **Sync Service**: Full Obsidian Sync operations, not file-level sync
- **Workspace System**: Save/load layouts, tab management, pane control

### Developer & Power User Features
- **Console Access**: Direct access to Obsidian's developer console
- **DOM Inspection**: Query Obsidian's UI elements and CSS
- **Command Palette**: Execute any registered Obsidian command by ID
- **Mobile Emulation**: Test mobile layouts and responsive behavior

## 🎮 TUI Mode

The skill supports Obsidian's interactive Terminal UI mode with:
- Command autocomplete
- Command history with search
- Keyboard shortcuts
- Multi-command sessions

## 📚 Documentation

The skill includes comprehensive documentation covering:
- Command syntax and parameters
- File targeting patterns (`file=` vs `path=`)
- TUI keyboard shortcuts
- Platform-specific setup instructions
- Troubleshooting guides

## 📁 Repository Structure

```
obsidian-official-cli-skill/
├── SKILL.md                        # Main skill source code
├── obsidian-official-cli.skill     # Packaged skill file  
├── README.md                       # This documentation
├── LICENSE                         # MIT license
├── CHANGELOG.md                    # Version history
└── .gitignore                      # Git ignore rules
```

## 🚀 Installation

Download the skill file from the [releases page](https://github.com/slmoloch/obsidian-official-cli-skill/releases) and install:

```bash
# Download the .skill file from releases, then:
openclaw skills install obsidian-official-cli.skill
```

## 🛠️ Development

**For Developers:**
- `SKILL.md` contains the complete skill implementation
- Edit `SKILL.md` to modify functionality  
- Rebuild with `openclaw skills build` after changes
- Test locally before submitting changes

## 🤝 Contributing

Found an issue or want to improve the skill? 

1. Open an issue describing the problem/enhancement
2. Fork the repository
3. Make your changes to `SKILL.md`
4. Test your changes locally
5. Submit a pull request

## 📄 License

MIT License - feel free to modify and redistribute.

## 🔗 Links

- [Obsidian Official CLI Documentation](https://help.obsidian.md/cli)
- [OpenClaw Documentation](https://docs.openclaw.ai)
- [ClawHub - Skill Marketplace](https://clawhub.com)

---

**Built for OpenClaw** 🦞 | **Supports Obsidian CLI v1.12+** 📝