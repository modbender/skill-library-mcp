# Zotero CLI Skill for OpenClaw

Command-line interface for Zotero - search your Zotero library, add/edit notes, read attachments, and manage bibliographic references from the terminal.

## 📦 What's Included

### Core Documentation
- **[SKILL.md](SKILL.md)** - Complete skill documentation with capabilities, workflows, and API reference
- **[INSTALL.md](INSTALL.md)** - Comprehensive installation guide with PEP 668/pi px support
- **[EXAMPLES.md](EXAMPLES.md)** - Practical usage examples for common research workflows

### Helper Scripts
- **[quick_search.py](scripts/quick_search.py)** - Search with formatted output (console, table, JSON, Markdown)
- **[export_citations.py](scripts/export_citations.py)** - Export citations in BibTeX, RIS, or plain text
- **[batch_process.sh](scripts/batch_process.sh)** - Process multiple queries from a file

### Metadata
- **[_meta.json](_meta.json)** - Skill version and ownership information
- **[.clawhub/origin.json](.clawhub/origin.json)** - Source repository information

## 🚀 Quick Start

### 1. Installation

#### Using pipx (Recommended for PEP 668-compliant systems)
```bash
sudo apt install pipx
pipx ensurepath
pipx install zotero-cli
```

#### Using pip (Generic)
```bash
pip install --user zotero-cli
```

### 2. Configuration
```bash
zotcli configure
```

### 3. Basic Usage
```bash
# Search your library
zotcli query "machine learning"

# Add a note
zotcli add-note "\"deep learning\""

# Read a paper
zotcli read "\"attention mechanisms\""
```

## 🎯 Key Features

### Core Capabilities
- Search your entire Zotero library using SQLite FTS3 syntax
- Add and edit notes on any item
- Read attachments directly with your preferred applications
- Edit notes in your favorite text editor with Markdown support
- Manage citations and bibliographic data without leaving the terminal

### PEP 668 Support
Designed for modern Linux distributions that follow PEP 668 (Debian 11+, Ubuntu 23.04+, Fedora 34+, etc.)

- **pipx integration** for isolated installations
- User-installation alternatives
- Comprehensive troubleshooting for permission errors
- Virtual environment support

### Helper Scripts
Format search results and export citations for different workflows:

```bash
# Quick search with table output
python quick_search.py "neural networks" --format table

# Export to BibTeX for LaTeX
python export_citations.py "attention mechanisms" --format bib > refs.bib

# Batch process multiple queries
./batch_process.sh queries.txt --output results.txt
```

## 📚 Documentation Structure

### Main Documentation
- **SKILL.md** - Complete guide with:
  - Capabilities and features
  - Installation options
  - Quick start guide
  - Core commands
  - Workflow examples
  - Tips and troubleshootings

### Installation Guide
- **INSTALL.md** - Detailed instructions for:
  - All installation methods (pipx, pip, virtual env)
  - Platform-specific notes (Debian, Ubuntu, Arch, Fedora, etc.)
  - PEP 668 compliance considerations
  - Troubleshooting common issues
  - Security best practices

### Usage Examples
- **EXAMPLES.md** - Real-world scenarios:
  - Basic usage patterns
  - Literature review workflows
  - Daily research routines
  - Academic writing integration
  - Collaboration and sharing
  - Automation and productivity
  - Advanced use cases

### Scripts Documentation
- **scripts/README.md** - Helper scripts guide:
  - Quick search with multiple formats
  - Citation export in various formats
  - Batch processing workflows
  - Integration examples

## 🔧 Workflows

### Literature Review
1. Search for papers on your topic
2. Add notes to key publications
3. Export citations for your paper
4. Read PDFs for detailed review

### Academic Writing
1. Research and collect references
2. Export to BibTeX for LaTeX
3. Integrate with Pandoc for Markdown
4. Automatically manage citations

### Daily Research
1. Quick morning scan of recent papers
2. Add notes to relevant publications
3. Export and organize findings
4. Build your knowledge base

## 🌟 Highlights

### PEP 668 Compatibility
- Primary recommendation: `pipx install zotero-cli`
- Alternative: `pip install --user zotero-cli`
- Virtual environment support
- Platform-specific instructions

### Multiple Output Formats
- Console output for quick browsing
- Table format for structured view
- JSON for programmatic processing
- Markdown for documentation

### Citation Management
- BibTeX for LaTeX
- RIS for EndNote/Mendeley
- Plain text for quick reference
- Batch export capabilities

### Productivity Features
- Batch processing
- Quick search scripts
- Keyboard shortcuts (with aliases)
- Weekly/monthly automated searches
- Custom workflows

## 💡 Common Use Cases

1. **Literature Review** - Comprehensive search and note-taking
2. **Academic Writing** - Citation management and export
3. **Daily Research** - Quick paper scanning and reading
4. **Collaboration** - Sharing queries and bibliographies
5. **Automation** - Regular searches and bibliography updates

## 🔗 Integration

Combine with other OpenClaw skills:
- **literature-review** - For multi-database literature searches
- **pubmed-edirect** - For PubMed database integration
- **tavily-search** - For web searches and general research

## 📖 Resources

- **GitHub Repository**: https://github.com/jbaiter/zotero-cli
- **Zotero Documentation**: https://www.zotero.org/support/
- **BibTeX Guide**: https://www.latex-project.org/help/documentation/btxdoc.pdf

## 🤝 Contributing

This skill follows the OpenClaw format and structure. Contributions, bug reports, and feature requests are welcome at the original zotero-cli repository.

## 📄 License

This skill documentation is provided as-is to help users of zotero-cli. The underlying software follows its own license.

---

**Happy researching! 📚🎓**
