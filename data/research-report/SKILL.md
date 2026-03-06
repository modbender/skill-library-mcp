---
name: research-report
description: "Research technical projects/papers and generate comprehensive reports with PDF export. Modes: lite (analysis + writing) or full (+ environment setup + experiments). Params: iterations, mode, project-path, output. Use for paper analysis, code review, technical reports, research documentation."
metadata: {"openclaw": {"requires": {"bins": ["pandoc"]}, "primaryEnv": "", "emoji": "📝"}}
---

# Research Report Generator

Analyze technical projects/papers and produce comprehensive reports with PDF export.

## Modes

### Lite Mode (default)
- Literature search + paper analysis
- Code reading (local or remote)
- Multi-iteration report writing
- PDF generation via md2pdf skill
- **No environment setup or experiment runs**

### Full Mode
- Everything in lite mode +
- Conda/virtualenv setup
- Dependency installation
- Experiment execution
- Result analysis

## Usage

```bash
bash {baseDir}/scripts/research-report.sh \
  --topic "Spatial Forcing" \
  --mode lite \
  --iterations 3 \
  --output both
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--topic` | (required) | Paper/project name or arXiv ID |
| `--mode` | `lite` | `lite` or `full` |
| `--iterations` | `3` | Report revision iterations |
| `--output` | `both` | `md`, `pdf`, or `both` |
| `--project-path` | (auto) | Local code directory (optional) |
| `--workspace` | (current) | Workspace directory |

## Workflow

### Phase 1: Discovery
1. Search arXiv + project pages
2. Fetch related papers (citations + references)
3. Identify key technologies and dependencies

### Phase 2: Analysis
1. Read source code (if `--project-path` provided)
2. Analyze architecture from docs/code
3. Map technology stack

### Phase 3: Report Writing (× iterations)
1. Draft outline
2. Write sections iteratively
3. Add diagrams (Mermaid/ASCII)
4. Refine explanations

### Phase 4: Export (Full mode only)
1. Setup conda env
2. Install dependencies
3. Run experiments
4. Append results to report

### Phase 5: PDF Generation
1. Call md2pdf skill
2. Send to user via Telegram

## Output Structure

```
<workspace>/
├── reports/
│   ├── <topic>_report_v1.md
│   ├── <topic>_report_v2.md
│   ├── <topic>_report_final.md
│   └── <topic>_report_final.pdf
├── memory/YYYY-MM-DD.md (appended)
└── logs/<topic>_research.log
```

## Report Template

The generated report follows this structure:

1. **Executive Summary** - 100-word overview
2. **Motivation** - Problem statement + why it matters
3. **Background** - Prerequisites explained intuitively
4. **Core Method** - Technical details with analogies
5. **Code Analysis** - Key files walkthrough
6. **Experiments** - Setup + results (full mode)
7. **Troubleshooting** - Common issues + fixes
8. **References** - Papers + repos + docs

## Dependencies

**Required:**
- pandoc (for PDF export)
- texlive-xetex (CJK + math support)

**Full mode only:**
- conda/miniconda
- CUDA toolkit (if GPU experiments)

## Integration

This skill automatically:
- Uses `md2pdf` skill for PDF conversion
- Appends to `memory/YYYY-MM-DD.md`
- Creates structured report directory

## Examples

**Lite mode, 5 iterations:**
```bash
research-report --topic "VGGT" --iterations 5 --mode lite
```

**Full mode with local code:**
```bash
research-report --topic "Spatial Forcing" \
  --project-path ~/Spatial-Forcing/openvla-SF \
  --mode full \
  --iterations 3
```

**PDF only output:**
```bash
research-report --topic "OpenVLA" --output pdf
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| PDF generation fails | Check `pandoc --version`, install texlive-xetex |
| CJK characters missing | Install `fonts-noto-cjk`, verify with `fc-list :lang=zh` |
| Math formulas not rendered | Ensure markdown uses `$...$` / `$$...$$` syntax |
| Full mode conda fails | Run `conda update -n base conda` first |
