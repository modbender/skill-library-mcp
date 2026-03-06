# PDF Translate Skill

> Academic-quality PDF translation tool powered by Claude — translates English PDFs into beautifully typeset Chinese documents.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Skill Version](https://img.shields.io/badge/version-4.0.0-blue.svg)](SKILL.md)
[![Claude Compatible](https://img.shields.io/badge/Claude-compatible-green.svg)](https://claude.ai/)
[![Cursor Compatible](https://img.shields.io/badge/Cursor-compatible-green.svg)](https://cursor.com/)

**[中文文档](README_CN.md)**

## Features

- **Markdown-first workflow** — Translate into structured Markdown first, then generate PDF for maximum formatting fidelity
- **Professional typography** — Dark code blocks, alternating-row tables, blue-bordered blockquotes, hierarchical headings
- **Full CJK support** — PingFang SC / STHeiti / Microsoft YaHei / Noto Sans CJK fallback chain; Chinese renders correctly everywhere, including code blocks
- **Dual output** — Produces both `.md` and `.pdf` so you get an editable source and a polished document
- **Academic-quality translation** — Three-step workflow (rewrite → diagnose → polish) that eliminates "translationese"
- **Cross-platform** — macOS, Windows, and Linux with automatic font detection

## Quick Start

### Prerequisites

```bash
# macOS
brew install pango
pip3 install pdfplumber markdown weasyprint

# Linux (Debian/Ubuntu)
sudo apt install libpango1.0-dev
pip3 install pdfplumber markdown weasyprint

# Windows
pip3 install pdfplumber markdown weasyprint
```

### Usage with Claude / Cursor

1. Place (or symlink) this skill into your skills directory:

   ```bash
   # Claude Code
   ln -s /path/to/pdf-translate ~/.claude/skills/pdf-translate

   # Cursor
   ln -s /path/to/pdf-translate .cursor/skills/pdf-translate
   ```

2. Ask in natural language:

   ```
   Translate this PDF: report.pdf
   翻译这个PDF：report.pdf
   ```

3. The skill automatically:
   - Extracts text with `pdfplumber`
   - Translates section-by-section into Chinese Markdown
   - Generates a professionally typeset PDF via `md2pdf.py`

### Standalone Usage

```bash
# Convert a Markdown file to PDF directly
python3 scripts/md2pdf.py input.md output.pdf
```

## How It Works

```
PDF ──► Extract text (pdfplumber)
         │
         ▼
     Analyze structure (headings, code, tables, lists)
         │
         ▼
     Translate section-by-section → Chinese Markdown
         │
         ▼
     Write .md file
         │
         ▼
     md2pdf.py (markdown → HTML → weasyprint → PDF)
         │
         ▼
     Polished .pdf with professional typography
```

### Translation Quality

Following the "translation as rewriting" philosophy:

- **Parataxis over hypotaxis** — Break long sentences, reorder for Chinese flow
- **Active over passive** — Avoid overuse of "被" constructions
- **Concrete over abstract** — Convert nominalizations to verbs
- **Concise over verbose** — Eliminate Europeanized expressions

## Project Structure

```
pdf-translate/
├── SKILL.md                       # Core skill definition (v4.0.0)
├── README.md                      # English documentation
├── README_CN.md                   # Chinese documentation
├── CHANGELOG.md                   # Version history
├── VERSION_HISTORY.md             # Detailed version history
├── LICENSE                        # MIT License
├── CONTRIBUTING.md                # Contribution guidelines
├── requirements.txt               # Python dependencies
├── .gitignore
├── scripts/
│   ├── md2pdf.py                  # Markdown → PDF converter (recommended)
│   ├── translate_pdf.py           # Legacy: basic PDF extraction (reportlab)
│   └── generate_complete_pdf.py   # Legacy: full workflow (reportlab)
└── references/
    ├── translation-standards.md   # Translation quality standards
    ├── font-configuration.md      # Font configuration & mixing rules
    ├── troubleshooting.md         # Troubleshooting guide
    └── complete-example.md        # Complete code examples
```

## PDF Output Showcase

The generated PDF includes:

| Feature | Description |
|---------|-------------|
| Page layout | A4 with automatic pagination and page numbers |
| Headings | 4-level hierarchy with blue accent borders |
| Code blocks | Dark background (#1e293b) with CJK font fallback |
| Tables | Alternating row colors, full borders |
| Blockquotes | Blue left border with light background |
| Lists | Nested ordered and unordered lists |
| Typography | Chinese body text at 10.5pt, justified alignment |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Chinese garbled in code blocks | Use `md2pdf.py` (v4.0 has CJK font fallback) |
| `libgobject` not found on macOS | `DYLD_FALLBACK_LIBRARY_PATH="/opt/homebrew/lib" python3 scripts/md2pdf.py` |
| Chinese characters not rendering | Ensure PingFang SC or STHeiti is installed |
| Broken Markdown formatting | Check that block elements have blank lines before and after |

## Version History

- **v4.0.0** (2026-02-21) — Markdown-first workflow; weasyprint engine; CJK code block fix
- **v3.0.0** (2026-02-02) — Major restructure; progressive disclosure; reference docs
- **v2.3.0** — Full Markdown parser; font mixing functions
- **v2.2.0** — TOC handling; special format support
- **v2.1.0** — STHeiti default; CJK-English font mixing
- **v2.0.0** — Academic-quality translation standards
- **v1.0.0** (2026-01-30) — Initial release

See [CHANGELOG.md](CHANGELOG.md) for full details.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

**Built with Claude + Human Collaboration**
