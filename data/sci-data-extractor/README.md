# Sci-Data-Extractor

> **AI-Powered Scientific Literature Data Extraction Tool** - Intelligently extract structured data from scientific paper PDFs

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## Overview

**Sci-Data-Extractor** is a Claude Code Skill designed to help researchers automatically extract structured data from scientific literature PDFs. Whether data is in tables, charts, or text, it can be intelligently recognized by AI and converted into usable formats (CSV, Markdown tables, etc.).

### Key Features

- **🔍 Multiple OCR Methods**: Support for Mathpix OCR (high-precision) and PyMuPDF (free)
- **🤖 AI-Powered Extraction**: Use Claude Sonnet 4.5 / GPT-4o for data extraction
- **📊 Flexible Output**: Support for Markdown tables and CSV formats
- **🎯 Preset Templates**: Built-in templates for enzyme kinetics, experimental results, literature reviews, etc.
- **🔄 Batch Processing**: Support for batch extraction from multiple literature files
- **⚙️ Highly Configurable**: Support for custom extraction fields and rules

## Installation

### Method 1: One-Click Installation via npx (Recommended)

```bash
npx skills add https://github.com/JackKuo666/sci-data-extractor.git
```

### Method 2: Git Clone

```bash
# Clone to Claude Code skills directory
git clone https://github.com/JackKuo666/sci-data-extractor.git ~/.claude/skills/sci-data-extractor
```

### Method 3: Manual Installation

1. Download the project ZIP or clone to local
2. Copy the `sci-data-extractor` folder to Claude Code skills directory:
   - **macOS/Linux**: `~/.claude/skills/`
   - **Windows**: `%USERPROFILE%\.claude\skills\`
3. Ensure the folder structure is:

```
~/.claude/skills/sci-data-extractor/
├── SKILL.md       # Skill definition file
├── extractor.py   # Core extraction script
├── README.md      # Documentation (English)
├── README_ZH.md   # Documentation (Chinese)
└── requirements.txt # Dependencies
```

### Install Python Dependencies

**Option 1: Using uv (Recommended - Fastest)**

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies in project directory
cd ~/.claude/skills/sci-data-extractor
uv venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows
uv pip install -r requirements.txt
```

**Option 2: Using conda (Best for scientific/research users)**

```bash
cd ~/.claude/skills/sci-data-extractor
conda create -n sci-data-extractor python=3.11 -y
conda activate sci-data-extractor
pip install -r requirements.txt
```

**Option 3: Using venv (Built-in, no extra installation)**

```bash
cd ~/.claude/skills/sci-data-extractor
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Verify Installation

Restart Claude Code or reload skills, then enter in conversation:

```
/extract-data
```

If installed successfully, the skill will be activated.

## Configuration

### Environment Variables

Create a `.env` file or set the following environment variables:

```bash
# Required: LLM API configuration
export EXTRACTOR_API_KEY="your-api-key-here"
export EXTRACTOR_BASE_URL="https://api.anthropic.com"  # or other compatible endpoint

# Optional: Mathpix OCR configuration (for high-quality OCR)
export MATHPIX_APP_ID="your-mathpix-app-id"
export MATHPIX_APP_KEY="your-mathpix-app-key"

# Optional: Default parameters
export EXTRACTOR_MODEL="claude-sonnet-4-5-20250929"
export EXTRACTOR_TEMPERATURE="0.1"
export EXTRACTOR_MAX_TOKENS="16384"
```

### Get API Keys

- **Anthropic Claude**: https://console.anthropic.com/
- **OpenAI**: https://platform.openai.com/api-keys
- **Mathpix OCR**: https://api.mathpix.com/

## Usage

### Using in Claude Code

#### 1. Quick Extraction (Using Preset Templates)

```
/extract-data Extract enzyme kinetics data from paper.pdf
```

#### 2. Custom Extraction

```
/extract-data Extract all clinical trial data from tables in article.pdf
```

#### 3. Batch Processing

```
/batch-extract Process all PDFs in ./literature folder
```

#### 4. Chart Data Extraction

```
/extract-data Extract curve data points from figure3.png
```

### Direct Command Line Usage

#### Basic Usage

```bash
# Extract using PyMuPDF (free)
python extractor.py input.pdf -o output.md

# Extract using Mathpix OCR (high-precision)
python extractor.py input.pdf -o output.md --ocr mathpix
```

#### Using Preset Templates

```bash
# Enzyme kinetics data
python extractor.py paper.pdf --template enzyme -o results.md

# Experimental results data
python extractor.py paper.pdf --template experiment -o results.md

# Literature review data
python extractor.py paper.pdf --template review -o results.md
```

#### Custom Extraction Prompt

```bash
python extractor.py paper.pdf \
  -p "Extract all protein structure-related data, including resolution, R-value, R_free value, etc." \
  -o results.md
```

#### Output CSV Format

```bash
python extractor.py paper.pdf --template enzyme -o results.csv --format csv
```

#### Print Results to Terminal

```bash
python extractor.py paper.pdf --template enzyme -o results.md --print
```

## Preset Templates

### Template 1: Enzyme Kinetics Data (`enzyme`)

Extracted fields:
- Enzyme (enzyme name)
- Organism (source organism)
- Substrate (substrate name)
- Km / Unit_Km (Michaelis constant)
- Kcat / Unit_Kcat (catalytic constant)
- Kcat_Km / Unit_Kcat_Km (catalytic efficiency)
- Temperature (temperature)
- pH (acidity/alkalinity)
- Mutant (mutant information)
- Cosubstrate (co-substrate)

### Template 2: Experimental Results Data (`experiment`)

Extracted fields:
- Experiment (experiment name)
- Condition (experimental conditions)
- Result (result value)
- Unit (unit of measurement)
- Standard_Deviation (standard deviation)
- Sample_Size (sample size n)
- p_value (statistical significance)

### Template 3: Literature Review Data (`review`)

Extracted fields:
- Author (author names)
- Year (publication year)
- Journal (journal name)
- Title (article title)
- DOI (digital object identifier)
- Key_Findings (main findings)
- Methodology (research methods)

## Use Cases

### Case 1: Build Enzyme Kinetics Database

```bash
# Batch extract enzyme kinetics data from multiple papers
for file in literature/*.pdf; do
    python extractor.py "$file" --template enzyme -o "results/$(basename "$file" .pdf).csv" --format csv
done
```

### Case 2: Extract Clinical Trial Data

```bash
python extractor.py clinical_trial.pdf \
  -p "Extract all clinical trial data including patient count, treatment protocol, response rate, and side effects" \
  -o clinical_data.csv --format csv
```

### Case 3: Organize Literature Review

```bash
python extractor.py review_paper.pdf --template review -o references.md
```

### Case 4: Extract Material Properties Data

```bash
python extractor.py materials.pdf \
  -p "Extract all mechanical property data of materials, including strength, modulus, elongation at break, etc." \
  -o materials.csv --format csv
```

## Output Formats

### Markdown Table

```markdown
| Enzyme | Organism | Substrate | Km | Unit_Km | Kcat | Unit_Kcat |
|--------|----------|-----------|-----|---------|------|-----------|
| HEX1 | Saccharomyces cerevisiae | Glucose | 0.12 | mM | 1840 | s^-1 |
```

### CSV Format

```csv
Enzyme,Organism,Substrate,Km,Unit_Km,Kcat,Unit_Kcat
HEX1,Saccharomyces cerevisiae,Glucose,0.12,mM,1840,s^-1
```

## Project Structure

```
sci-data-extractor/
├── SKILL.md              # Claude Code skill definition
├── extractor.py          # Core extraction script
├── batch_extract.py      # Batch processing script
├── README.md             # Documentation (English)
├── README_ZH.md          # Documentation (Chinese)
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variable examples
└── examples/             # Usage examples
    └── custom_prompts.txt # Custom prompt examples
```

## Technical Architecture

```
┌─────────────────┐
│   PDF Input     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│   OCR Processing Layer  │
│  • Mathpix OCR (opt.)   │
│  • PyMuPDF (default)    │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│   Text Preprocessing    │
│  • Remove references    │
│  • Clean formatting     │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│   AI Extraction Layer   │
│  • Claude Sonnet 4.5    │
│  • GPT-4o               │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│   Output Formatting     │
│  • Markdown tables      │
│  • CSV                  │
└────────┬────────────────┘
         │
         ▼
┌─────────────────┐
│ Structured Data │
└─────────────────┘
```

## Dependencies

- **Python 3.11+**
- **PyMuPDF**: PDF text extraction
- **OpenAI**: LLM API calls (compatible with Claude)
- **Requests** (optional): Mathpix OCR calls

## FAQ

### Q: What's the difference between Mathpix OCR and PyMuPDF?

**A:**
- **Mathpix OCR**: High precision, can recognize formulas and complex tables, but requires paid API
- **PyMuPDF**: Completely free, suitable for plain text content, less effective at formula recognition

### Q: How to handle documents exceeding token limits?

**A:** The tool automatically segments long documents into multiple parts and merges the results. For large tables or extensive data extraction, you can increase the `EXTRACTOR_MAX_TOKENS` environment variable (default: 16384, max: 32768 or higher).

### Q: Is the extracted data accurate?

**A:** AI extraction accuracy depends on document clarity and data structure. Recommendations:
1. Manually verify extraction results
2. Use Mathpix OCR for important data to improve precision
3. Optimize extraction by adjusting prompts

### Q: Can I extract chart data from images?

**A:** Yes! Claude Code supports image analysis and can recognize charts and extract data points.

### Q: How to customize extraction fields?

**A:** Use the `-p` parameter to provide custom prompts, for example:

```bash
python extractor.py paper.pdf \
  -p "Extract all data from Table 1, including sample name, concentration, absorbance, fluorescence intensity" \
  -o results.md
```

## Contributing

Contributions are welcome! Feel free to submit issues, feature requests, or pull requests.

1. Fork this project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Citation

If this project helps your research, please cite:

```bibtex
@software{sci_data_extractor,
  title={Sci-Data-Extractor: AI-Powered Scientific Literature Data Extraction},
  author={JackKuo},
  year={2025},
  url={https://github.com/JackKuo666/sci-data-extractor}
}
```

## License

This project is licensed under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** License.

## Related Resources

- [Original Project: Automated Enzyme Kinetics Extractor](https://huggingface.co/spaces/jackkuo/Automated-Enzyme-Kinetics-Extractor)
- [Related Paper: Enzyme Co-Scientist](https://www.biorxiv.org/content/10.1101/2025.03.02.153459v1)
- [Claude Code Skills Documentation](https://docs.anthropic.com/en/docs/claude-code/skills)

## Contact

- GitHub: [JackKuo666/sci-data-extractor](https://github.com/JackKuo666/sci-data-extractor)
- GitHub Issues: [Submit Issues](https://github.com/JackKuo666/sci-data-extractor/issues)

## 中文文档

Chinese documentation is available at [README_ZH.md](README_ZH.md).

---

**Note**: This tool is for academic research use only. Please comply with copyright regulations and cite original literature when using extracted data.
