# Quick Start Guide

Get started with zotero-cli in just a few minutes!

## 🚀 5-Minute Setup

### Step 1: Install zotero-cli (1 min)

Choose one of these methods:

#### Option A: pipx (Recommended)
```bash
# Debian/Ubuntu
sudo apt update && sudo apt install pipx -y

# Arch Linux
sudo pacman -S pipx

# Fedora/RHEL
sudo dnf install pipx

# Then install zotero-cli
pipx ensurepath
pipx install zotero-cli
```

#### Option B: pip (Simple)
```bash
pip install --user zotero-cli
export PATH="$HOME/.local/bin:$PATH"
```

### Step 2: Configure (30 sec)

```bash
zotcli configure
```

Follow the prompts to:
- Enter your Zotero userID (found at https://www.zotero.org/settings/keys)
- Generate an API key

### Step 3: Verify (30 sec)

```bash
# Run the setup checker
./scripts/setup_and_check.sh

# Test your first search
zotcli query "test"
```

### Step 4: Start Using! (2 min)

```bash
# Search your library
zotcli query "machine learning"

# Add a note to a paper
zotcli add-note "\"deep learning\""

# Read a PDF
zotcli read "\"attention mechanisms\""
```

## 📋 Essential Commands

| Action | Command |
|--------|---------|
| Search | `zotcli query "topic"` |
| Read | `zotcli read "paper"` |
| Add note | `zotcli add-note "paper"` |
| Edit note | `zotcli edit-note "paper"` |
| Configure | `zotcli configure` |

## 🛠️ Helper Scripts

```bash
# Quick search with table output
python scripts/quick_search.py "topic" --format table

# Export citations for LaTeX
python scripts/export_citations.py "topic" --format bib > refs.bib

# Batch process multiple queries
./scripts/batch_process.sh queries.txt --output results.txt

# Setup and verify installation
./scripts/setup_and_check.sh

# Backup your configuration
./scripts/backup_restore.sh backup

# Check for updates
./scripts/update_check.sh check
```

## 💡 Daily Workflow

### Morning Routine

```bash
# 1. Check for updates
./scripts/update_check.sh check

# 2. Quick scan of recent papers
python scripts/quick_search.py "\"recent publications\"" --format table

# 3. Add notes to interesting papers
zotcli add-note "\"interesting paper title\""
```

### Research Session

```bash
# 1. Define your research topic
TOPIC="transformers in NLP"

# 2. Search and export references
python scripts/export_citations.py "$TOPIC" --format bib > refs.bib

# 3. Add notes to key papers
zotcli add-note "\"attention is all you need\""
zotcli add-note "\"BERT: pre-training\""

# 4. Read PDFs for detailed review
zotcli read "\"transformer mechanisms\""
```

### Weekly Maintenance

```bash
# 1. Backup your configuration
./scripts/backup_restore.sh backup

# 2. Clean old backups
./scripts/backup_restore.sh clean

# 3. Update if needed
./scripts/update_check.sh update
```

## 🎯 Common Tasks

### Task 1: Literature Review

```bash
# Find seminal papers
python scripts/quick_search.py "\"your topic\" survey" --format table

# Export to BibTeX
python scripts/export_citations.py "\"your topic\"" --format bib > review_refs.bib

# Add notes to key publications
zotcli add-note "\"seminal paper\""
zotcli add-note "\"another key paper\""
```

### Task 2: Academic Writing

```bash
# Export all references for a paper
python scripts/export_citations.py "\"paper topic\"" --format bib > references.bib

# Create a LaTeX template
cat > your_paper.tex << 'EOF'
\documentclass{article}
\usepackage[utf8]{inputenc}

\begin{document}

\title{Your Paper Title}
\author{Your Name}
\date{\today}

\maketitle

\section{Introduction}
As discussed in \cite{key_paper}, etc.

\bibliographystyle{plain}
\bibliography{references}

\end{document}
EOF

# Compile
pdflatex your_paper.tex
bibtex your_paper
pdflatex your_paper.tex
pdflatex your_paper.tex
```

### Task 3: Quick Reference Sheet

```bash
# Create a queries file
cat > my_queries.txt << EOF
topic 1
topic 2
topic 3
EOF

# Batch process
./scripts/batch_process.sh my_queries.txt --output reference_sheet.txt

# Format nicely
less reference_sheet.txt
```

## 📚 Next Steps

1. **Read the documentation:**
   - [SKILL.md](SKILL.md) - Complete capabilities and features
   - [INSTALL.md](INSTALL.md) - Detailed installation guide
   - [EXAMPLES.md](EXAMPLES.md) - 20+ usage examples

2. **Explore helper scripts:**
   - [scripts/README.md](scripts/README.md) - All scripts documented

3. **Set up automation:**
   - Add to cron for regular updates
   - Create aliases for common commands
   - Set up weekly backups

## 🔧 Configuration

### Set Your Default Editor

```bash
# Add to ~/.bashrc or ~/.zshrc
export VISUAL=nano  # or vim, emacs, code, etc.
```

### Create Aliases

```bash
# Add to ~/.bashrc or ~/.zshrc
alias zq='zotcli query'
alias zn='zotcli add-note'
alias ze='zotcli edit-note'
alias zr='zotcli read'
alias zc='zotcli configure'
```

### Set Up PATH for pipx

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"
```

## 🔍 Troubleshooting

### Problem: "command not found"
```bash
# Ensure PATH includes pipx location
export PATH="$HOME/.local/bin:$PATH"
# Log out and back in for permanent changes
```

### Problem: "permission denied"
```bash
# Install pipx properly
sudo apt install pipx  # or equivalent for your distro
```

### Problem: "API key error"
```bash
# Reconfigure
zotcli configure
```

### Problem: "editor not found"
```bash
# Set VISUAL environment variable
export VISUAL=nano
```

## 📖 Learn More

- **Full documentation:** See other markdown files in this skill
- **GitHub repository:** https://github.com/jbaiter/zotero-cli
- **Zotero support:** https://www.zotero.org/support/

---

**Happy researching! 📚🎓**

Need help? Check the complete documentation in this skill directory.
