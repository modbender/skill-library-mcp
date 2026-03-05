# PDF OCR Tool

**Intelligent PDF and Image to Markdown Converter using Ollama GLM-OCR**

[![ClawHub](https://clawhub.ai/badge/pdf-ocr-tool)](https://clawhub.ai/skills/pdf-ocr-tool)
[![GitHub](https://img.shields.io/github/license/nala0222/pdf-ocr-tool)](https://github.com/nala0222/pdf-ocr-tool)

## Overview

PDF OCR Tool is an intelligent document conversion tool that uses the Ollama GLM-OCR model to convert PDFs and images into structured Markdown format. It automatically detects content types (text, tables, figures) and applies the most appropriate prompts for optimal OCR results.

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

### Prerequisites

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

### Install via ClawHub (Recommended)

```bash
npx clawhub install pdf-ocr-tool
```

### Manual Installation

```bash
# Clone or download the skill
cd ~/.openclaw/workspace/skills/pdf-ocr-tool

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv sync

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
python ocr_tool.py --input document.pdf --output result.md --mode auto --granularity region

# Process a single image
python ocr_tool.py --input image.png --output result.md
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

### Environment Variables

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

## Prompt Templates

The tool includes four built-in prompt templates in the `prompts/` directory:

- **text.md**: Text recognition prompts
- **table.md**: Table recognition prompts
- **figure.md**: Figure/chart analysis prompts
- **mixed.md**: Mixed content prompts

All prompts are in English for consistency and can be customized based on your needs.

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
cd ~/.openclaw/workspace/skills/pdf-ocr-tool
source .venv/bin/activate
uv sync  # Reinstall all dependencies
```

## Project Structure

```
pdf-ocr-tool/
├── SKILL.md              # Skill definition
├── README.md             # This file
├── _meta.json            # ClawHub metadata
├── .clawhubignore        # Files to exclude from ClawHub
├── .gitignore            # Git ignore rules
├── pyproject.toml        # Python project config
├── uv.lock              # Dependency lock file
├── ocr_tool.py          # Main CLI entry point
├── analyzer.py          # Page analysis module
├── processor.py         # Region processing module
├── integrator.py        # Markdown integration module
├── prompts.py           # Prompt loader
├── prompts/             # Prompt templates
│   ├── text.md
│   ├── table.md
│   ├── figure.md
│   └── mixed.md
├── utils/               # Utility modules
│   ├── ollama_client.py
│   ├── image_utils.py
│   └── pdf_utils.py
├── hooks/               # Installation hooks
│   ├── post-install.sh
│   └── install-deps.sh
└── tests/               # Test suite
```

## Development

### Running Tests

```bash
cd ~/.openclaw/workspace/skills/pdf-ocr-tool
source .venv/bin/activate
pytest tests/ -v
```

### Building from Source

```bash
# Clone repository
git clone https://github.com/nala0222/pdf-ocr-tool.git
cd pdf-ocr-tool

# Install dependencies
uv venv
source .venv/bin/activate
uv sync
```

## License

MIT License - See LICENSE file for details.

## Credits

- **Ollama**: For the GLM-OCR model
- **OpenClaw**: For the skill framework
- **ClawHub**: For skill distribution

## Support

For issues and feature requests, please visit:
- GitHub: https://github.com/nala0222/pdf-ocr-tool
- ClawHub: https://clawhub.ai/skills/pdf-ocr-tool
