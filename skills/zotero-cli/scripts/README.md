# zotero-cli Helper Scripts

This directory contains a collection of helper scripts to enhance and automate your zotero-cli experience.

## 📋 Available Scripts

### 1. `quick_search.py`

Quick search with formatted output for different use cases.

**Features:**
- Multiple output formats (console, table, JSON, Markdown)
- Easy copy-paste for different purposes
- Structured output for programmatic use
- Limit results for quick views

**Usage:**
```bash
python quick_search.py <query> [--limit N] [--format {console,table,json,markdown}]
```

**Examples:**

Search and display in table format:
```bash
python quick_search.py "machine learning" --format table
```

Export as JSON for further processing:
```bash
python quick_search.py "\"deep learning\"" --format json > results.json
```

Limit results and display in console:
```bash
python quick_search.py "neural networks" --limit 5 --format console
```

Generate Markdown table for documentation:
```bash
python quick_search.py "attention mechanism" --format markdown > refs.md
```

---

### 2. `export_citations.py`

Export your search results in citation formats for academic writing.

**Features:**
- BibTeX format (for LaTeX)
- RIS format (for EndNote, Mendeley, Zotero)
- Plain text format (for general use)
- Automatic BibTeX key generation

**Usage:**
```bash
python export_citations.py <query> --format {bib,ris,txt}
```

**Examples:**

Export to BibTeX for LaTeX:
```bash
python export_citations.py "machine learning" --format bib > references.bib
```

Then use in your LaTeX document:
```latex
\bibliographystyle{plain}
\bibliography{references}
```

Export to RIS for import to other reference managers:
```bash
python export_citations.py "\"deep learning\"" --format ris > import.ris
```

Export plain text for quick reference:
```bash
python export_citations.py "neural networks" --format txt > refs.txt
```

---

### 3. `batch_process.sh`

Process multiple queries in batch mode.

**Features:**
- Process queries from a text file
- Save results to a file
- Progress tracking with counters
- Support for comments in query files
- Error handling and validation

**Usage:**
```bash
./batch_process.sh <queries_file> [--output <output_file>]
```

**Examples:**

Create a queries file (`queries.txt`):
```text
machine learning
deep learning
neural networks
attention mechanisms
# This is a comment, will be ignored
transformers in NLP
```

Process all queries and display on screen:
```bash
./batch_process.sh queries.txt
```

Process and save to file:
```bash
./batch_process.sh queries.txt --output results.txt
```

Make the script executable:
```bash
chmod +x batch_process.sh
```

---

### 4. `setup_and_check.sh` ⭐ NEW

Quick setup and verification script for zotero-cli. This script helps you get started quickly and verifies your installation.

**Features:**
- **Automatic installation** - Install zotero-cli with recommended method
-**Prerequisites checking** - Verify Python, pip, pipx are installed
- **Configuration guidance** - Step-by-step configuration assistance
- **Functionality testing** - Test basic zotero-cli operations
- **Setup verification** - Ensure everything is working correctly

**Usage:**
```bash
./setup_and_check.sh
```

**What it does:**

1. **Check System Prerequisites**
   - Python 3.7+ installation
   - pip and pipx availability
   - System compatibility

2. **Check zotero-cli Installation**
   - Verify zotero-cli is installed
   - Show version and location
   - Identify installation method

3. **Check Configuration**
   - Verify configuration file exists
   - Check file permissions
   - Offer to run configuration if needed

4. **Check Optional Tools**
   - Pandoc for note format conversion
   - Other useful tools

5. **Test Basic Functionality**
   - Run test query
   - Verify API connectivity
   - Confirm setup success

6. **Show Next Steps**
   - Provide getting started commands
   - Link to relevant documentation

**Interactive Mode:**

The script is interactive and will guide you through the setup process:

```bash
./setup_and_check.sh
```

It will:
- Check your system
- Detect if zotero-cli is installed
- Offer to install if not found
- Guide you through configuration
- Provide helpful next steps

**Use Cases:**

- New users getting started
- Verifying a new installation
- Troubleshooting configuration issues
- Automated setup in scripts

---

### 5. `backup_restore.sh` ⭐ NEW

Backup and restore utility for zotero-cli configuration and data.

**Features:**
- **Full backup** - Configuration, library data, custom content
- **Backup management** - List, clean, and organize backups
- **Restore capability** - Restore from any backup date
- **Automatic cleanup** - Remove old backups (>30 days)
- **Secure permissions** - Proper file permissions for sensitive data

**Usage:**

```bash
# Run a full backup
./backup_restore.sh backup

# List available backups
./backup_restore.sh list

# Restore from a specific backup
./backup_restore.sh restore --date 20240109_100000

# Clean old backups
./backup_restore.sh clean
```

**What Gets Backed Up:**

1. **Configuration File**
   - `~/.config/zotcli/config.ini`
   - Your Zotero userID and API key
   - Custom settings

2. **Library Data**
   - List of all items in your library
   - Query results for reference

3. **Custom Content**
   - Custom scripts
   - Query files
   - Other user-generated content

**Backup Location:**

By default, backups are stored in:
```
~/.zotero-cli-backups/
```

**Backup Naming Convention:**

```
config_YYYYMMDD_HHMMSS.ini
library_list_YYYYMMDD_HHMMSS.txt
queries_YYYYMMDD_HHMMSS.txt
```

**Example Workflow:**

```bash
# Before making major changes, backup first
./backup_restore.sh backup

# After a few months, clean old backups
./backup_restore.sh clean

# List what you have
./backup_restore.sh list

# If needed, restore from a specific date
./backup_restore.sh restore --date 20240109_100000
```

**Restoration Notes:**

- Configuration is fully restored
- Library data is reference-only (notes need to be managed via Zotero)
- Custom scripts and queries are fully restored
- Previous config is backed up before restoration

**Use Cases:**

- Regular backups for safety
- Before upgrading zotero-cli
- Before making config changes
- Moving to a new system
- Disaster recovery

---

### 6. `update_check.sh` ⭐ NEW

Update check and management utility for keeping zotero-cli up to date.

**Features:**
- **Version checking** - Compare current version to PyPI and GitHub
- **Easy updates** - Update with a single command
- **Multiple sources** - Check both PyPI and GitHub releases
- **Installation help** - Install latest version if not installed
- **Changelog access** - Quick access to release notes

**Usage:**

```bash
# Check for updates
./update_check.sh check

# Update to latest version
./update_check.sh update

# View changelog on GitHub
./update_check.sh changelog

# Install latest version
./update_check.sh install
```

**Version Checking:**

The script checks multiple sources:

1. **Current Version** - Your installed version
2. **PyPI** - Official Python Package Index
3. **GitHub** - Latest GitHub releases

**Status Messages:**

- ✅ **"You are running the latest version!"** - No update needed
- ⚠️ **"A new version is available!"** - Update recommended
- ⚠️ **"You are running a newer version"** - You have a dev version
- ⚠️ **"zotero-cli is not installed"** - Need to install first

**Update Methods:**

The script automatically detects your installation method:

```bash
# If installed with pipx
pipx upgrade zotero-cli

# If installed with --user
pip install --upgrade --user zotero-cli
```

**Example Workflow:**

```bash
# Regular update check (add to cron)
./update_check.sh check

# If update is available, update it
./update_check.sh update

# See what's new
./update_check.sh changelog
```

**Automated Updates:**

Add to your crontab for regular checks:

```cron
# Check for updates weekly on Sunday at 9 AM
0 9 * * 0 /path/to/update_check.sh check
```

**Use Cases:**

- Regular maintenance
- Security updates
- New feature availability
- Bug fixes
- Automated updates via cron

---

## 🚀 Quick Start

### First-Time Setup

```bash
# 1. Verify and setup zotero-cli
./setup_and_check.sh

# 2. Create your first backup (for safety)
./backup_restore.sh backup

# 3. Check for updates
./update_check.sh check
```

### Daily Usage

```bash
# Quick search
python quick_search.py "machine learning" --format table

# Export citations
python export_citations.py "topic" --format bib > refs.bib

# Batch research
./batch_process.sh queries.txt --output results.txt
```

### Maintenance

```bash
# Regular backup
./backup_restore.sh backup

# Clean old backups
./backup_restore.sh clean

# Check for updates
./update_check.sh check

# Update if needed
./update_check.sh update
```

---

## 💡 Tips and Tricks

### 1. Create Shortcuts

Add these aliases to your `.bashrc` or `.zshrc`:

```bash
# Quick search alias
alias zotsearch='python ~/zotero-cli/scripts/quick_search.py'

# Export citations alias
alias zotexport='python ~/zotero-cli/scripts/export_citations.py'

# Batch process alias
alias zotbatch='~/zotero-cli/scripts/batch_process.sh'

# Setup alias
alias zotsetup='~/zotero-cli/scripts/setup_and_check.sh'

# Backup alias
alias zotbackup='~/zotero-cli/scripts/backup_restore.sh backup'

# Update alias
alias zotupdate='~/zotero-cli/scripts/update_check.sh update'
```

### 2. Make Scripts Executable

```bash
chmod +x *.sh *.py
```

### 3. Add Scripts to PATH

For easier access, add scripts directory to PATH:

```bash
echo 'export PATH="$HOME/zotero-cli/scripts:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Then use without full path:
```bash
setup_and_check.sh
backup_restore.sh backup
```

### 4. Integration with Cron

Automate regular tasks:

```cron
# Weekly backup
0 9 * * 0 /path/to/backup_restore.sh backup

# Weekly update check
0 10 * * 0 /path/to/update_check.sh check

# Monthly cleanup
0 0 1 * * /path/to/backup_restore.sh clean
```

### 5. Create Research Templates

Create reusable template files:

```bash
# Create a template query file
cat > research_template.txt << 'EOF'
# Research queries template
# Replace TOPIC with your actual research topic

TOPIC
"TOPIC survey"
"TOPIC review"
"TOPIC tutorial"
EOF

# Use with sed to create specific queries
sed 's/TOPIC/machine learning/g' research_template.txt > ml_queries.txt
./batch_process.sh ml_queries.txt --output ml_results.txt
```

---

## 🔧 Troubleshooting

### Script Not Executable

```bash
chmod +x script_name.sh
chmod +x script_name.py
```

### Python Module Not Found

Ensure you're using the correct Python:

```bash
which python3
export PATH="/path/to/python/bin:$PATH"
```

### zotcli Command Not Found

Ensure zotero-cli is installed and in your PATH:

```bash
pipx ensurepath
# Log out and back in, or:
export PATH="$HOME/.local/bin:$PATH"
```

### Permission Denied on Scripts

```bash
chmod 755 script_name.sh
```

### Backup/Restore Issues

- Ensure you have write permissions to `~/.zotero-cli-backups`
- Check if backup directory exists
- Verify date format (YYYYMMDD_HHMMSS)

### Update Issues

- Use the installation method that matches your current setup
- Check internet connectivity
- Verify pip/pipx is available
- Try update as root if permission errors occur (not recommended)

---

## 📚 Documentation Index

For more information, see:

- **[SKILL.md](./SKILL.md)** - Complete skill documentation
- **[INSTALL.md](./INSTALL.md)** - Installation guide
- **[EXAMPLES.md](./EXAMPLES.md)** - Usage examples
- **[README.md](./README.md)** - Project overview

---

## 🤝 Contributing

If you have ideas for new scripts or improvements:

1. Test thoroughly before submitting
2. Add documentation
3. Include usage examples
4. Follow existing code style
5. Make scripts executable

---

## 📄 License

These scripts are provided as-is for helping users of zotero-cli. They follow the same license as zotero-cli.

---

## 🔗 External Resources

- [zotero-cli GitHub](https://github.com/jbaiter/zotero-cli)
- [Zotero Documentation](https://www.zotero.org/support/)
- [BibTeX Guide](https://www.latex-project.org/help/documentation/btxdoc.pdf)
- [Pandoc Manual](https://pandoc.org/MANUAL.html)
- [Python Packaging](https://packaging.python.org/)

---

## 📖 Quick Reference

| Script | Purpose | Common Command |
|--------|---------|----------------|
| `quick_search.py` | Search with formatted output | `python quick_search.py "query" --format table` |
| `export_citations.py` | Export citations | `python export_citations.py "query" --format bib` |
| `batch_process.sh` | Process multiple queries | `./batch_process.sh queries.txt --output results.txt` |
| `setup_and_check.sh` | Setup and verify | `./setup_and_check.sh` |
| `backup_restore.sh` | Backup and restore | `./backup_restore.sh backup` |
| `update_check.sh` | Check for updates | `./update_check.sh check` |

---

**Happy researching! 📚🎓**
