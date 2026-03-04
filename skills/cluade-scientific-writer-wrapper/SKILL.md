---
name: scientific-writer
description: AI-powered scientific writing tool. Generate publication-ready papers, grant proposals, posters, and more with real-time research and verified citations.
metadata:
  {
    "openclaw": {
      "emoji": "🔬",
      "requires": {
        "bins": ["python3", "pip"],
        "env": ["ANTHROPIC_API_KEY"]
      }
    }
  }
---

# Scientific Writer

AI-powered scientific writing tool that combines deep research with well-formatted outputs.

## Installation

```bash
pip install scientific-writer
```

## Prerequisites

- Python 3.10-3.12
- ANTHROPIC_API_KEY (required)
- OPENROUTER_API_KEY (optional for research lookup)

Set API keys:
```bash
export ANTHROPIC_API_KEY='your_key'
# or create .env file
echo "ANTHROPIC_API_KEY=your_key" > .env
```

## Usage

### As Python API

```python
import asyncio
from scientific_writer import generate_paper

async def main():
    async for update in generate_paper(
        query="Create a Nature paper on CRISPR gene editing...",
        data_files=["editing_efficiency.csv", "western_blot.png"]
    ):
        if update["type"] == "progress":
            print(f"[{update['stage']}] {update['message']}")
        else:
            print(f"✓ PDF: {update['files']['pdf_final']}")

asyncio.run(main())
```

### Via OpenClaw exec

```bash
# Run scientific writer
python3 -c "
import asyncio
from scientific_writer import generate_paper

async def main():
    async for update in generate_paper(
        query='Create a paper on your topic...',
        data_files=[]
    ):
        print(update)

asyncio.run(main())
"
```

## Available Skills (when used as plugin)

- `scientific-schematics` - AI diagram generation (CONSORT, neural networks, pathways)
- `research-lookup` - Real-time literature search
- `peer-review` - Systematic manuscript evaluation
- `citation-management` - BibTeX and reference handling
- `clinical-reports` - Medical documentation
- `research-grants` - NSF, NIH, DOE proposal support
- `scientific-slides` - Research presentations
- `latex-posters` - Conference poster generation
- `hypothesis-generation` - Scientific hypothesis development

## Output

- Scientific papers (Nature, Science, NeurIPS format)
- Grant proposals (NSF, NIH, DOE)
- Conference posters (LaTeX beamerposter)
- Literature reviews
- Clinical reports

## Notes

- Requires ANTHROPIC_API_KEY for Claude to work
- Place data files in `data/` folder (images → figures/, data → data/)
- Outputs saved to `writing_outputs/`
