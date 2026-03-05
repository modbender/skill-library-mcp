# zotero-cli Usage Examples

A collection of practical examples demonstrating how to use zotero-cli for various research workflows.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Literature Review Workflow](#literature-review-workflow)
3. [Daily Research Routine](#daily-research-routine)
4. [Academic Writing Integration](#academic-writing-integration)
5. [Collaboration & Sharing](#collaboration--sharing)
6. [Automation & Productivity](#automation--productivity)
7. [Advanced Scenarios](#advanced-scenarios)

---

## Basic Usage

### Example 1: Your First Search

```bash
# Simple topic search
zotcli query "machine learning"

# Search for a phrase (use quotes)
zotcli query "\"deep learning\""

# Search with Boolean operators
zotcli query "neural AND networks"
zotcli query "(deep OR machine) AND learning"
zotcli query "learning NOT neural"
```

### Example 2: Reading Papers

```bash
# Find a paper and read its first PDF attachment
zotcli query "\"attention is all you need\""
# Copy the ID from the output, e.g., F5R83K6P
zotcli read F5R83K6P

# Direct search and read (auto-uses first match)
zotcli read "\"transformer models\""
```

### Example 3: Adding Notes

```bash
# Add a note to a specific paper (using query)
zotcli add-note "\"transformer networks\""
# Your editor will open with a blank note
# Write your note, save, and close
# The note is now in your Zotero library!

# Add a note using item ID
zotcli add-note F5R83K6P
```

### Example 4: Editing Notes

```bash
# Edit an existing note
zotcli edit-note "\"attention mechanisms\""

# Edit by item ID
zotcli edit-note F5R83K6P
```

---

## Literature Review Workflow

### Example 5: Comprehensive Literature Review

```bash
# Step 1: Search for seminal papers on a topic
python quick_search.py "\"transformers in NLP\"" --format table > seminal_papers.txt

# Step 2: Search for recent surveys
zotcli query "\"transformers tutorial\""
zotcli query "\"transformers survey\""
zotcli query "\"transformers review\""

# Step 3: Add notes to key papers
zotcli add-note "\"attention is all you need\""
zotcli add-note "\"BERT: pre-training of deep bidirectional transformers\""
zotcli add-note "\"GPT-3: language models are few-shot learners\""

# Step 4: Export citations for your paper
python export_citations.py "\"transformers in NLP\"" --format bib > transformers.bib

# Step 5: Create a query file for related topics
cat > related_topics.txt << EOF
attention mechanisms
transfer learning
pre-trained models
language understanding
few-shot learning
EOF

# Step 6: Batch process all related topics
./batch_process.sh related_topics.txt --output related_papers.txt

# Step 7: Organize findings
# Review the exported file and categorize papers by sub-topic
```

### Example 6: Systematic Review

```bash
# Define inclusion criteria
zotcli query "\"transformers\" AND NLP AND (2019 OR 2020 OR 2021 OR 2022 OR 2023)"

# Export results for screening
python export_citations.py "\"transformers\" AND NLP AND (2019 OR 2020 OR 2021 OR 2022 OR 2023)" --format json > screening_pool.json

# Process through inclusion/exclusion criteria
# Use the JSON output for programmatic filtering
python - << EOF
import json

with open('screening_pool.json') as f:
    papers = json.load(f)

# Example: Filter by title keywords
included = [p for p in papers if 'attention' in p['title'].lower()]
with open('included_papers.json', 'w') as f:
    json.dump(included, f, indent=2)
EOF

# Extract DOIs for full-text retrieval
python - << 'PYTHON'
import json

with open('screening_pool.json') as f:
    papers = json.load(f)

print('\n'.join([p['id'] for p in papers]))
PYTHON
```

---

## Daily Research Routine

### Example 7: Daily Paper Skimming

```bash
# Create a daily research script: daily_research.sh
cat > daily_research.sh << 'EOF'
#!/bin/bash
echo "📚 Daily Research Skimming"
echo "==========================="

# Today's research topic
TOPIC="$1"

echo "Searching for: $TOPIC"
echo ""

# Quick search
python quick_search.py "$TOPIC" --format table

echo ""
echo "Would you like to add notes to any paper? (Enter 'yes' to continue)"
read response

if [[ "$response" == "yes" ]]; then
    echo "Enter the query string for the paper:"
    read paper_query
    zotcli add-note "$paper_query"
fi

echo "Daily research complete! 🎯"
EOF

chmod +x daily_research.sh

# Use it daily
./daily_research.sh "\"reinforcement learning\""
```

### Example 8: Morning Literature Scan

```bash
# Scan recent papers in your field
cat > morning_scan.txt << 'EOF'
# Today's scan topics
machine learning
deep learning
neural networks
artificial intelligence
computer vision
natural language processing
EOF

./batch_process.sh morning_scan.txt --output morning_scan_results.txt

# Review results over coffee
less morning_scan_results.txt
```

---

## Academic Writing Integration

### Example 9: LaTeX Bibliography Management

```bash
# Research and write your paper
# 1. Research topics
python export_citations.py "\"transformers in NLP\"" --format bib > chapter1_refs.bib

# 2. Add citations to paper
cat > paper.tex << 'EOF'
\documentclass{article}
\usepackage[utf8]{inputenc}

\begin{document}

\title{Transformers in NLP}
\author{Your Name}
\date{\today}

\maketitle

\section{Introduction}
As discussed in \cite{vaswani2017attention}, attention mechanisms have revolutionized NLP \cite{devlin2018bert}.

\section{Related Work}
The transformer architecture \cite{vaswani2017attention} has led to numerous improvements in language understanding.

\bibliographystyle{plain}
\bibliography{chapter1_refs}
\end{document}
EOF

# 3. Compile with bibliography
pdflatex paper.tex
bibtex paper
pdflatex paper.tex
pdflatex paper.tex
```

### Example 10: Markdown & Pandoc Integration

```bash
# Write in Markdown with citations
cat > paper.md << 'EOF'
# Transformers in NLP

## Introduction
The transformer architecture [@vaswani2017attention] has revolutionized natural language processing.

## Related Work
BERT [@devlin2018bert] and GPT-3 [@brown2020language] demonstrate the power of pre-trained transformers.

## Conclusion
The future is bright for transformer-based models.

## References
EOF

# Export citations for Pandoc
python export_citations.py "\"transformers in NLP\"" --format json > citations.json

# Compile to PDF with Pandoc
pandoc paper.md --citeproc --bibliography=citations.json -o paper.pdf
```

### Example 11: Tracking References Throughout a Project

```bash
# Project structure
mkdir my_research_project
cd my_research_project

# Initialize reference tracking
echo "# References for My Project" > README.md
echo "" >> README.md
echo "## Chapter 1: Background" >> README.md

# Search and add references
python quick_search.py "\"machine learning basics\"" --format markdown >> README.md
python export_citations.py "\"machine learning basics\"" --format bib > chapter1.bib

echo "" >> README.md
echo "## Chapter 2: Methods" >> README.md
python quick_search.py "\"deep learning methods\"" --format markdown >> README.md
python export_citations.py "\"deep learning methods\"" --format bib > chapter2.bib

# Combine bibliographies
cat chapter1.bib chapter2.bib > references.bib

# Track in version control
git init
git add -A
git commit -m "Initial references collection"
```

---

## Collaboration & Sharing

### Example 12: Sharing Queries with Team

```bash
# Create a shared queries file
cat > team_queries.txt << 'EOF'
# Research queries for the team

# Topic 1: Transformers
"attention is all you need"
"transformer architecture"
"self-attention mechanism"

# Topic 2: Pre-training
"BERT pre-training"
"GPT language models"
"T5 encoder-decoder"

# Topic 3: Applications
"question answering"
"text classification"
"summarization"
EOF

# Share with team via Git
git add team_queries.txt
git commit -m "Add team research queries"
git push

# Team member pulls and runs
git pull
./batch_process.sh team_queries.txt --output team_results.txt
```

### Example 13: Creating Shared Bibliographies

```bash
# Each team member exports their findings
python export_citations.py "my research topic" --format bib > my_refs.bib

# Combine all references
cat *.bib > team_bibliography.bib

# Remove duplicates (using bibtool if available)
bibtool -r team_bibliography.bib > team_bibliography_clean.bib

# Distribute to team
scp team_bibliography_clean.bib team@server:/shared/
```

---

## Automation & Productivity

### Example 14: Weekly Automated Search

```bash
# Create weekly search automation
cat > weekly_search.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y-%m-%d)
OUTPUT_DIR="weekly_searches/$DATE"
mkdir -p "$OUTPUT_DIR"

# Research topics
declare -a topics=(
    "\"recent machine learning\""
    "\"deep learning applications\""
    "\"natural language processing\""
    "\"computer vision advances\""
)

for topic in "${topics[@]}"; do
    output_file="$OUTPUT_DIR/$(echo $topic | tr ' ' '_').txt"
    echo "Searching: $topic"
    zotcli query "$topic" > "$output_file"
done

echo "Weekly search complete! Results in $OUTPUT_DIR"
EOF

chmod +x weekly_search.sh

# Add to crontab for automated weekly execution
crontab -e
# Add: 0 9 * * 1 /path/to/weekly_search.sh
```

### Example 15: Research Dashboard

```bash
# Create a simple research dashboard
cat > research_dashboard.sh << 'EOF'
#!/bin/bash

clear
echo "================================================"
echo "           📊 Research Dashboard                "
echo "================================================"
echo ""

# Show recent searches
echo "Recent Searches:"
echo "---------------"
ls -lt ~/.config/zotcli/ | head -5
echo ""

# Show total papers in library
echo "Library Overview:"
echo "-----------------"
zotcli query "*" | wc -l
echo "total items found"
echo ""

echo "Current Research Focus:"
echo "-----------------------"
cat current_focus.txt
echo ""

echo "Quick Actions:"
echo "  1. Search library"
echo "  2. Add note"
echo "  3. Read paper"
echo "  4. Export citations"
echo ""

read -p "Select action (1-4) or press Enter to exit: " action

case $action in
    1)
        read -p "Enter search query: " query
        zotcli query "$query"
        ;;
    2)
        read -p "Enter paper query: " query
        zotcli add-note "$query"
        ;;
    3)
        read -p "Enter paper query: " query
        zotcli read "$query"
        ;;
    4)
        read -p "Enter export query: " query
        python export_citations.py "$query" --format bib
        ;;
esac
EOF

chmod +x research_dashboard.sh
```

### Example 16: Keyboard Shortcuts & Aliases

```bash
# Add to ~/.bashrc or ~/.zshrc

# Core aliases
alias zq='zotcli query'
alias zn='zotcli add-note'
alias ze='zotcli edit-note'
alias zr='zotcli read'
alias zc='zotcli configure'

# Advanced aliases
alias zsearch='python ~/zotero-cli/scripts/quick_search.py'
alias zexport='python ~/zotero-cli/scripts/export_citations.py'
alias zbatch='~/zotero-cli/scripts/batch_process.sh'

# Composed workflows
alias zweekly='~/weekly_search.sh'
alias zdaily='~/daily_research.sh'
alias zdashboard='~/research_dashboard.sh'

# Usage examples become much simpler:
zq "machine learning"
zn "\"deep learning\""
zsearch "neural networks" --format table
zexport "attention mechanisms" --format bib
```

---

## Advanced Scenarios

### Example 17: Cross-Platform References

```bash
# Export in multiple formats for different tools
QUERY="\"transformers in NLP\""

# BibTeX for LaTeX
python export_citations.py "$QUERY" --format bib > latex_refs.bib

# RIS for EndNote/Mendeley
python export_citations.py "$QUERY" --format ris > endnote_refs.ris

# JSON for programmatic use
python quick_search.py "$QUERY" --format json > data.json

# Markdown for documentation
python quick_search.py "$QUERY" --format markdown > docs_refs.md

# Plain text for quick reference
python export_citations.py "$QUERY" --format txt > quick_refs.txt
```

### Example 18: Building a Knowledge Graph

```bash
# Step-by-step knowledge graph construction

# 1. Start with a core paper
CORE_PAPER="\"attention is all you need\""
zotcli query "$CORE_PAPER"

# 2. Find papers that cited the core paper
# (Note: zotero-cli doesn't directly support citation search,
#  but you can use the ID to explore)
CORE_ID=$(zotcli query "$CORE_PAPER" | grep -oP '\[\K[^\]]+' | head -1)

# 3. Add notes tracking relationships
zotcli add-note "$CORE_PAPER"
# In the note, add: "Cited by: [list of papers]"

# 4. Expand to related topics
python quick_search.py "\"self-attention\"" --format table > related.txt
python quick_search.py "\"transformer encoder\"" --format table >> related.txt

# 5. Create a visual representation
# (Use tools like yEd, Cytoscape, or online graph tools)
```

### Example 19: Systematic Literature Search with PRISMA

```bash
# PRISMA workflow implementation

# Phase 1: Identification
echo "Phase 1: Identification"
echo "======================="
cat > search_strings.txt << 'EOF'
# Search strings based on research question

# P: Population
natural language processing
text analysis

# I: Intervention
transformers
attention mechanisms
pre-trained models

# O: Outcome
performance
accuracy
efficiency

# Search combinations
transformers AND NLP
attention AND language
pre-training AND understanding
EOF

# Execute searches
./batch_process.sh search_strings.txt --output phase1_identification.txt

# Phase 2: Screening
echo "Phase 2: Screening"
echo "=================="
# Filter by title and abstract (manual or programmatic)

# Phase 3: Eligibility
echo "Phase 3: Eligibility"
echo "===================="
# Full-text review based on inclusion criteria

# Document the process
cat > prisma_flow.md << 'EOF'
# PRISMA Flow Diagram

## Identification
- Records identified through database searching: [N]

## Screening
- Records after duplicates removed: [N]
- Records screened: [N]
- Records excluded: [N]
- Full-text articles assessed for eligibility: [N]

## Eligibility
- Studies included in review: [N]
- Studies excluded: [N]

## Included
- Qualitative synthesis: [N]
- Quantitative synthesis: [N]
EOF

# Track counts programmatically
cat > prisma_counter.sh << 'EOF'
#!/bin/bash
echo "Records identified: $(wc -l < phase1_identification.txt)"
echo "Records screened: $(grep -c "^[A-Z]" phase1_identification.txt)"
echo "Studies included: ???"
chmod +x prisma_counter.sh
```

### Example 20: Meta-Analysis Preparation

```bash
# Prepare data for meta-analysis

# 1. Define search protocol
cat > meta_analysis_protocol.txt << 'EOF'
Research Question: Efficacy of transformer models in NLP

Inclusion Criteria:
- Published in peer-reviewed journals
- English language
- 2015-2023
- Comparison with baseline models
- Performance metrics reported

Exclusion Criteria:
- Non-peer-reviewed preprints
- Missing data
- Incomplete methodology
EOF

# 2. Conduct systematic search
TOPIC="\"transformer models\" AND (accuracy OR precision OR recall OR f1)"

# 3. Extract data
python export_citations.py "$TOPIC" --format json > extraction_pool.json

# 4. Create extraction template
cat > extraction_template.csv << 'EOF'
Study ID,Authors,Year,Task,Baseline,Transformer,Improvement,Sample Size,Notes
EOF

# 5. Extract data programmatically
python - << 'PYTHON'
import json
import csv

with open('extraction_pool.json') as f:
    studies = json.load(f)

with open('extraction_template.csv', 'a') as f:
    writer = csv.writer(f)
    for study in studies:
        # Extract or manually enter data fields
        row = [
            study['id'],
            study['authors'],
            "YYYY",  # Manual extraction
            "Task",  # Manual extraction
            "Baseline",
            "Transformer",
            "Improvement",
            0,
            ""
        ]
        writer.writerow(row)
PYTHON

# 6. Perform statistical analysis (using R, Python, etc.)
# Data is now ready for meta-analysis software
```

---

## Quick Reference Cheatsheet

| Action | Command |
|--------|---------|
| Search | `zotcli query "term"` |
| Read | `zotcli read "query"` |
| Add Note | `zotcli add-note "query"` |
| Edit Note | `zotcli edit-note "query"` |
| Configure | `zotcli configure` |
| Quick Search | `python quick_search.py "query" --format table` |
| Export BibTeX | `python export_citations.py "query" --format bib` |
| Batch Process | `./batch_process.sh queries.txt --output results.txt` |

---

## Need More Examples?

Check the main documentation:
- [SKILL.md](SKILL.md) - Complete skill documentation
- [INSTALL.md](INSTALL.md) - Installation guide
- [scripts/README.md](scripts/README.md) - Helper scripts guide
- [https://github.com/jbaiter/zotero-cli](https://github.com/jbaiter/zotero-cli) - Official repository

---

**Happy researching! 🎓📚**
