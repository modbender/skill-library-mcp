# Scientific Graphical Abstract Generator

> **AI-Powered Scientific Visualization Tool** - Generate editable graphical abstracts for research papers

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

**Scientific Graphical Abstract Generator** is a Claude Code Skill designed to help researchers create professional, publication-quality graphical abstracts for scientific papers. It generates editable SVG visualizations that can be customized for journal requirements.

### Key Features

- **Multiple AI Models**: Support for Claude, GPT-4o, DeepSeek, and other multimodal models
- **Editable SVG Output**: Generate vector graphics editable in Inkscape, Illustrator, or any SVG editor
- **Multiple Chart Types**: Bar charts, line charts, pie charts, scatter plots, flowcharts, diagrams
- **Data-Driven Visuals**: Automatically create charts from CSV/JSON data
- **Customizable Styles**: Adjust colors, fonts, layouts to match journal requirements
- **Publication Ready**: High-quality output suitable for scientific journals
- **Template-Based**: Quick generation using predefined templates for common visualizations

## Installation

### Method 1: One-Click Installation via npx (Recommended)

```bash
npx skills add https://github.com/JackKuo666/scientific-graphical-abstract-skill.git
```

### Method 2: Git Clone

```bash
# Clone to Claude Code skills directory
git clone https://github.com/JackKuo666/scientific-graphical-abstract-skill.git ~/.claude/skills/scientific-graphical-abstract-skill
```

### Method 3: Manual Installation

1. Download the project ZIP or clone to local
2. Copy the `scientific-graphical-abstract-skill` folder to Claude Code skills directory:
   - **macOS/Linux**: `~/.claude/skills/`
   - **Windows**: `%USERPROFILE%\.claude\skills\`
3. Ensure the folder structure is:

```
~/.claude/skills/scientific-graphical-abstract-skill/
├── SKILL.md                             # Skill definition file
├── graphical_abstract_generator.py      # Core generator script
├── README.md                            # Documentation
├── requirements.txt                     # Python dependencies
└── .env.example                         # Environment variable examples
```

### Install Python Dependencies

**Option 1: Using uv (Recommended - Fastest)**

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
cd ~/.claude/skills/scientific-graphical-abstract-skill
uv venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows
uv pip install -r requirements.txt
```

**Option 2: Using conda (Best for scientific/research users)**

```bash
cd ~/.claude/skills/scientific-graphical-abstract-skill
conda create -n scientific-abstract python=3.11 -y
conda activate scientific-abstract
pip install -r requirements.txt
```

**Option 3: Using venv (Built-in)**

```bash
cd ~/.claude/skills/scientific-graphical-abstract-skill
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Verify Installation

Restart Claude Code or reload skills, then enter in conversation:

```
/graphical-abstract
```

If installed successfully, the skill will be activated.

## Configuration

### Environment Variables (Optional)

The skill works without any configuration for basic SVG generation. AI model API keys are optional.

Create a `.env` file or set the following environment variables:

```bash
# Optional: Anthropic Claude API Key
ANTHROPIC_API_KEY="your-anthropic-api-key"

# Optional: OpenAI API Key (for GPT-4o)
OPENAI_API_KEY="your-openai-api-key"

# Optional: DeepSeek API Key
DEEPSEEK_API_KEY="your-deepseek-api-key"
```

## Usage

### Using in Claude Code

#### 1. Generate Workflow Diagram

```
/graphical-abstract Create a workflow diagram showing: Sample Preparation → RNA Extraction → Sequencing → Data Analysis → Results Visualization
```

#### 2. Generate Data Chart

```
/graphical-abstract Generate a bar chart showing:
Model A: 85% accuracy
Model B: 92% accuracy
Model C: 78% accuracy

Title: Model Performance Comparison
```

#### 3. Generate Mechanism Diagram

```
/graphical-abstract Design a schematic showing how the drug binds to the enzyme active site, blocking substrate access
```

#### 4. Generate Line Chart from CSV

```
/graphical-abstract Create a line chart from the data in results.csv showing temperature over time
```

### Direct Command Line Usage

#### Generate from Prompt

```bash
# Generate a workflow diagram
python graphical_abstract_generator.py generate \
  --prompt "Create a workflow: Input → Processing → Analysis → Output" \
  --output workflow.svg

# Generate with specific style
python graphical_abstract_generator.py generate \
  --prompt "Research methodology diagram" \
  --style journal \
  --output diagram.svg

# Generate with specific dimensions
python graphical_abstract_generator.py generate \
  --prompt "Experimental setup" \
  --width 1200 --height 800 \
  --output setup.svg
```

#### Generate from Data File

```bash
# Generate bar chart from JSON
python graphical_abstract_generator.py generate \
  --data data.json \
  --type bar \
  --title "Sales by Quarter" \
  --output chart.svg

# Generate line chart from CSV
python graphical_abstract_generator.py generate \
  --data results.csv \
  --type line \
  --title "Temperature Over Time" \
  --output line.svg

# Generate pie chart with custom color
python graphical_abstract_generator.py generate \
  --data distribution.json \
  --type pie \
  --color "#50E3C2" \
  --output pie.svg
```

#### Use Templates

```bash
# Workflow template
python graphical_abstract_generator.py template \
  --type workflow \
  --output workflow.svg

# Mechanism diagram template
python graphical_abstract_generator.py template \
  --type mechanism \
  --output mechanism.svg
```

## Command Reference

### generate
Generate a graphical abstract.

| Option | Description |
|--------|-------------|
| `--prompt` | Description of what to visualize |
| `--data` | Data file (CSV/JSON) for charts |
| `--type` | Chart type: bar, line, pie, scatter, flowchart, diagram, auto |
| `--model` | AI model: claude, gpt4o, deepseek (default: claude) |
| `--style` | Style: minimal, professional, colorful, journal |
| `--title` | Chart title (default: "Chart") |
| `--output` | Output SVG file path (required) |
| `--width` | Canvas width (default: 800) |
| `--height` | Canvas height (default: 600) |
| `--color` | Primary color (default: "#4A90E2") |

### template
Use predefined templates for common visualizations.

| Option | Description |
|--------|-------------|
| `--type` | Template type: workflow, mechanism, comparison, timeline (required) |
| `--prompt` | Specific requirements |
| `--output` | Output SVG file path (required) |

## Data Format

### JSON Format

```json
[
  {"label": "Model A", "value": 85},
  {"label": "Model B", "value": 92},
  {"label": "Model C", "value": 78}
]
```

### CSV Format

```csv
label,value
Model A,85
Model B,92
Model C,78
```

## Output Format

All outputs are in **SVG format** which offers:

### Benefits of SVG

- **Editable**: Open in Inkscape, Adobe Illustrator, or any text editor
- **Scalable**: Infinite resolution without quality loss
- **Web-ready**: Can be embedded directly in websites
- **Publication quality**: Meets most journal requirements

### SVG Structure

The generated SVG files have a clean, organized structure:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
  <!-- Editable groups with clear IDs -->
  <g id="chart-area">...</g>
  <g id="labels">...</g>
  <g id="legend">...</g>
</svg>
```

### Editing SVG

You can edit the generated SVG files in:

- **Inkscape** (Free, open-source)
- **Adobe Illustrator** (Commercial)
- **Figma** (Web-based)
- **Any text editor** (for direct XML editing)

## Supported AI Models

### Claude (Recommended)

- **Best for**: Complex diagrams, scientific illustrations
- **Vision capabilities**: Excellent
- **API**: Anthropic Claude API
- **Use when**: You need high-quality, detailed visualizations

### GPT-4o

- **Best for**: Charts, data visualization
- **Vision capabilities**: Very good
- **API**: OpenAI API
- **Use when**: Working with structured data and charts

### DeepSeek

- **Best for**: Technical diagrams, cost-effective
- **Vision capabilities**: Good
- **API**: DeepSeek API
- **Use when**: Budget-conscious or need technical precision

## Use Cases

### Case 1: Research Workflow Visualization

```bash
python graphical_abstract_generator.py generate \
  --prompt "Sample collection → DNA extraction → PCR amplification → Gel electrophoresis → Sequencing → Data analysis" \
  --type flowchart \
  --output research_workflow.svg
```

### Case 2: Data Publication

```bash
python graphical_abstract_generator.py generate \
  --data experimental_results.json \
  --type bar \
  --title "Treatment Effects" \
  --style journal \
  --output figure1.svg
```

### Case 3: Mechanism of Action

```bash
python graphical_abstract_generator.py template \
  --type mechanism \
  --prompt "Show how the inhibitor binds to the active site" \
  --output mechanism.svg
```

### Case 4: Comparison Chart

```bash
python graphical_abstract_generator.py generate \
  --prompt "Create a comparison chart showing: Method A (95%), Method B (87%), Method C (92%)" \
  --type bar \
  --color "#4A90E2" \
  --output comparison.svg
```

## Project Structure

```
scientific-graphical-abstract-skill/
├── SKILL.md                            # Claude Code skill definition
├── graphical_abstract_generator.py     # Core generator script
├── README.md                           # Documentation
├── requirements.txt                    # Python dependencies
└── .env.example                        # Environment variable examples
```

## Dependencies

- **Python 3.8+**
- **matplotlib**: Plotting and visualization
- **plotly**: Interactive plotting
- **pandas**: Data manipulation
- **numpy**: Numerical computing
- **svgwrite**: SVG writing (optional)
- **cairosvg**: SVG to PNG conversion (optional)

## FAQ

### Q: Do I need API keys to use this skill?

**A:** No, the built-in SVG generator works without API keys. API keys are optional and only needed for advanced AI-powered generation.

### Q: Can I edit the generated SVG?

**A:** Yes! All SVG files are fully editable. You can open them in Inkscape, Adobe Illustrator, or any text editor.

### Q: What formats can I convert the SVG to?

**A:** SVG can be converted to PNG, PDF, EPS, and other formats using tools like Inkscape, cairosvg, or online converters.

### Q: How do I customize the colors?

**A:** Use the `--color` parameter to set the primary color, or edit the SVG file directly to change any colors.

### Q: Can I use this for publication?

**A:** Yes, the SVG output is publication-quality. You may need to adjust fonts and colors to match journal requirements.

## Troubleshooting

### Issue: "Module not found"

**Solution:** Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: SVG won't open

**Solution:** Make sure you have an SVG viewer installed. You can use web browsers, Inkscape, or online SVG viewers.

### Issue: Text appears garbled

**Solution:** The SVG uses standard fonts. If you see garbled text, try opening the SVG in a different viewer or editor.

## Tips for Best Results

1. **Provide detailed descriptions**: More specific prompts yield better results
2. **Use structured data**: CSV/JSON files produce more accurate charts
3. **Specify dimensions**: Adjust width/height for your intended use
4. **Choose appropriate styles**: "journal" style for publications, "colorful" for presentations
5. **Edit after generation**: SVG files are fully editable, so refine the output as needed

## Related Projects

- [LLM-Scientific-Graphical-Abstract-Generator](https://github.com/JackKuo666/LLM-Scientific-Graphical-Abstract-Generator): Original concept project
- [sci-data-extractor](https://github.com/JackKuo666/sci-data-extractor): Extract data from scientific papers
- [semanticscholar-search-skill](https://github.com/JackKuo666/semanticScholar-search-skill): Search academic papers

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## Contact

- GitHub: [JackKuo666/scientific-graphical-abstract-skill](https://github.com/JackKuo666/scientific-graphical-abstract-skill)
- GitHub Issues: [Submit Issues](https://github.com/JackKuo666/scientific-graphical-abstract-skill/issues)

## License

This project is licensed under the **MIT License**.

## Acknowledgments

- Built based on the [LLM-Scientific-Graphical-Abstract-Generator](https://github.com/JackKuo666/LLM-Scientific-Graphical-Abstract-Generator) concept
- Built based on the [sci-data-extractor](https://github.com/JackKuo666/sci-data-extractor) skill template
- SVG generation powered by matplotlib and plotly
