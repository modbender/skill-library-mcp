---
name: pdf-ocr-tool
description: Intelligent PDF and image to Markdown converter using Ollama GLM-OCR with smart content detection (text/table/figure)
metadata: {"openclaw":{"emoji":"📄","requires":{"bins":["uv","ollama","pdftoppm"],"anyBins":[],"env":[],"config":[]},"install":[{"id":"uv-env","kind":"uv","path":".","bins":["ocr_tool.py"]}]}}
---
# PDF OCR Tool - Intelligent PDF to Markdown Converter

Uses the Ollama GLM-OCR model to intelligently recognize text, tables, and figures in PDF pages, applying the most appropriate prompts for OCR processing and outputting structured Markdown documents.

## Features

- ✅ **Smart Content Detection**: Automatically identifies page content type (text/table/figure)
- ✅ **Mixed Mode**: Splits pages into multiple regions for processing different content types
- ✅ **Multiple Processing Modes**: Supports text, table, figure, mixed, and auto modes
- ✅ **PDF Page-by-Page Processing**: Converts PDF to images and processes each page
- ✅ **Image OCR**: Supports OCR for single images
- ✅ **Custom Prompts**: Adjustable OCR prompts based on requirements
- ✅ **Flexible Configuration**: Customizable Ollama host, port, and model
- ✅ **uv Package Management**: Uses uv for Python dependency management

## Installation

### 1. Prerequisites

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull glm-ocr:q8_0

# Install poppler-utils (for PDF to image conversion)
sudo apt install poppler-utils  # Debian/Ubuntu
brew install poppler            # macOS

# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Install with uv (Recommended)

```bash
cd skills/pdf-ocr-tool
uv venv
source .venv/bin/activate
uv add requests Pillow
```

### 3. Install via ClawHub

```bash
npx clawhub install pdf-ocr-tool
```

### 4. Manual Installation

```bash
# Clone or download skill
git clone <repo> ~/.openclaw/workspace/skills/pdf-ocr-tool

# Create virtual environment and install dependencies
cd ~/.openclaw/workspace/skills/pdf-ocr-tool
uv venv
source .venv/bin/activate
uv add requests Pillow

# Run post-install script
bash hooks/post-install.sh
```

## Usage

### Basic Usage

```bash
# Auto-detect content type (recommended)
python ocr_tool.py --input document.pdf --output result.md

# Specify processing mode
python ocr_tool.py --input document.pdf --output result.md --mode text
python ocr_tool.py --input document.pdf --output result.md --mode table
python ocr_tool.py --input document.pdf --output result.md --mode figure

# Mixed mode: split page into regions
python ocr_tool.py --input document.pdf --output result.md --granularity region

# Process a single image
python ocr_tool.py --input image.png --output result.md --mode mixed
```

### Advanced Configuration

```bash
# Specify Ollama host and port
python ocr_tool.py --input document.pdf --output result.md \
  --host localhost --port 11434

# Use different model
python ocr_tool.py --input document.pdf --output result.md \
  --model glm-ocr:q8_0

# Custom prompt
python ocr_tool.py --input image.png --output result.md \
  --prompt "Convert this table to Markdown format, keeping rows and columns aligned"

# Save figure region images
python ocr_tool.py --input document.pdf --output result.md --save-images
```

### Environment Configuration

```bash
# Set default configuration
export OLLAMA_HOST="localhost"
export OLLAMA_PORT="11434"
export OCR_MODEL="glm-ocr:q8_0"

# Run
python ocr_tool.py --input document.pdf --output result.md
```

## Processing Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `auto` | Auto-detect content type | General use (default) |
| `text` | Pure text recognition | Academic papers, articles, reports |
| `table` | Table recognition | Data tables, financial reports |
| `figure` | Chart/figure recognition | Statistical charts, flowcharts, diagrams |
| `mixed` | Mixed mode | Pages with multiple content types |

### Mixed Mode (Granularity)

When using `--granularity region`:
- Page is split vertically into multiple regions (default: 3)
- Each region is independently analyzed for content type
- Corresponding prompts are used for OCR
- Final results are combined into complete Markdown

## Output Format

### PDF Output Example

```markdown
# PDF to Markdown Result
**Total Pages**: 15
**Model**: glm-ocr:q8_0
**Mode**: auto
**Generated**: 2026-02-27T01:00:00+08:00

---

## Page 1
*Type: mixed*

### Region 1 (text)
[OCR recognized text content]

### Region 2 (table)
<table>
<tr><th>Column 1</th><th>Column 2</th></tr>
<tr><td>Data 1</td><td>Data 2</td></tr>
</table>

### Region 3 (figure)
[Chart description]
![Chart](./images/page_1_region_3.png)

---
```

### Image Output Example

```markdown
# image.png OCR Result
Model: glm-ocr:q8_0
Mode: table

---

[OCR recognized result]
```

## Prompt Templates

The tool includes four built-in prompt templates in the `prompts/` directory:

### Text Mode (`prompts/text.md`)
```
Convert the text in this region to Markdown format.
- Preserve paragraph structure and heading levels
- Handle lists correctly
- Preserve mathematical formulas
- Maintain citations and references
```

### Table Mode (`prompts/table.md`)
```
Convert the table in this region to Markdown table format.
- Maintain row and column alignment
- Preserve all data and values
- Handle merged cells
- Preserve headers and units
```

### Figure Mode (`prompts/figure.md`)
```
Analyze the chart or image in this region:
1. Chart type (bar, line, pie, flowchart, etc.)
2. Titles and axis labels
3. Data trends and key observations
4. Important values and anomalies
Describe in Markdown format.
```

## Using in OpenClaw

```python
import subprocess
from pathlib import Path

# Process PDF (auto mode)
subprocess.run([
    "python", "skills/pdf-ocr-tool/ocr_tool.py",
    "--input", "/path/to/document.pdf",
    "--output", "/tmp/result.md",
    "--mode", "auto"
])

# Read result
with open("/tmp/result.md", "r") as f:
    markdown_content = f.read()

# Process single image (table mode)
subprocess.run([
    "python", "skills/pdf-ocr-tool/ocr_tool.py",
    "--input", "/path/to/table.png",
    "--output", "/tmp/table.md",
    "--mode", "table"
])

# Mixed mode for complex PDF
subprocess.run([
    "python", "skills/pdf-ocr-tool/ocr_tool.py",
    "--input", "/path/to/mixed.pdf",
    "--output", "/tmp/mixed.md",
    "--granularity", "region",  # Split into regions
    "--save-images"  # Save figure images
])
```

## Troubleshooting

### Model Not Installed
```bash
ollama pull glm-ocr:q8_0
```

### Service Not Running
```bash
ollama serve
```

### Missing pdftoppm
```bash
sudo apt install poppler-utils  # Debian/Ubuntu
brew install poppler            # macOS
```

### Poor OCR Results
- Try different modes: `--mode text` or `--mode mixed`
- Use custom prompts: `--prompt "your prompt here"`
- Check image quality (resolution, clarity)
- Try mixed mode: `--granularity region`

### Dependency Issues
```bash
cd skills/pdf-ocr-tool
source .venv/bin/activate
uv sync  # Reinstall all dependencies
```

## Related Resources

- [Ollama API Documentation](https://docs.ollama.com/api/generate)
- [GLM-OCR Model Page](https://ollama.com/library/glm-ocr)
- [poppler-utils](https://poppler.freedesktop.org/)
- [uv Package Manager](https://github.com/astral-sh/uv)

## Version History

- **v1.2.0** - English prompts, install-deps.sh, fixed .gitignore
- **v1.1.0** - Added mixed mode, region splitting, pyproject.toml
- **v1.0.0** - Initial version with basic OCR functionality

## Credits

This tool is developed and maintained by the OpenClaw community.

## License

MIT License
