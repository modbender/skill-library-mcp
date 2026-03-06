# Prompts Loader
"""Load prompt templates from markdown files."""

from pathlib import Path
from typing import Optional

# Prompt cache (loaded on first access)
_prompts_cache = {}

def get_prompt(name: str, prompts_dir: Optional[Path] = None) -> str:
    """
    Load a prompt template from markdown file.
    
    Args:
        name: Prompt name (text, table, figure, mixed)
        prompts_dir: Custom prompts directory path (default: prompts/ in same directory)
    
    Returns:
        Prompt content as string
    """
    # Check cache first
    if name in _prompts_cache:
        return _prompts_cache[name]
    
    # Determine prompts directory
    if prompts_dir is None:
        prompts_dir = Path(__file__).parent / "prompts"
    
    prompt_file = prompts_dir / f"{name}.md"
    
    if prompt_file.exists():
        content = prompt_file.read_text(encoding="utf-8")
        _prompts_cache[name] = content
        return content
    
    # Fallback to default prompts
    return _get_default_prompt(name)

def _get_default_prompt(name: str) -> str:
    """Get built-in default prompt if markdown file not found."""
    prompts = {
        "text": (
            "Convert the text in this region to Markdown format.\n\n"
            "## Requirements\n"
            "- Preserve paragraph structure and heading levels (#, ##, ###)\n"
            "- Handle lists correctly (- or 1.)\n"
            "- Preserve mathematical formulas (use $ or $$)\n"
            "- Maintain citations and reference format\n"
            "- Preserve code blocks (use ```)\n"
            "- Pay attention to special symbols and formatting\n\n"
            "## Notes\n"
            "- Do not omit any text content\n"
            "- Maintain original heading hierarchy\n"
            "- Correctly identify technical terms and proper nouns\n"
            "- Preserve the original language (do not translate)\n"
        ),
        "table": (
            "Convert the table in this region to Markdown table format.\n\n"
            "## Requirements\n"
            "- Maintain row and column alignment\n"
            "- Preserve all data and numerical values\n"
            "- Handle merged cells (use appropriate Markdown syntax)\n"
            "- If multiple tables exist, label them separately\n"
            "- Preserve headers and units\n"
            "- Correctly identify number formats (thousands separators, decimals, etc.)\n\n"
            "## Format Specifications\n"
            "- Use standard Markdown table syntax\n"
            "- Alignment: numbers right-aligned, text left-aligned\n"
            "- Preserve the original table's hierarchical structure\n\n"
            "## Notes\n"
            "- Do not omit any cells\n"
            "- Pay attention to numerical units\n"
            "- Preserve table titles and captions\n"
        ),
        "figure": (
            "Analyze the chart or image in this region and describe it in Markdown format.\n\n"
            "## Analysis Items\n\n"
            "### 1. Chart Type\n"
            "Identify and specify the chart type:\n"
            "- Bar Chart\n"
            "- Line Chart\n"
            "- Pie Chart\n"
            "- Scatter Plot\n"
            "- Flowchart\n"
            "- Architecture Diagram\n"
            "- Other (please specify)\n\n"
            "### 2. Titles and Labels\n"
            "- Chart title\n"
            "- Axis labels (X-axis, Y-axis)\n"
            "- Legend description\n"
            "- Units\n\n"
            "### 3. Data Analysis\n"
            "- Data trends (increasing, decreasing, fluctuating)\n"
            "- Maximum and minimum values\n"
            "- Anomalies or special observations\n"
            "- Key data points\n\n"
            "### 4. Interpretation and Insights\n"
            "- Main message the chart conveys\n"
            "- Meaning behind the data\n"
            "- Relationship with other content\n\n"
            "## Output Format\n"
            "Use Markdown format including:\n"
            "- Appropriate heading levels\n"
            "- Lists and emphasis\n"
            "- Tables if necessary for data organization\n"
            "- Clear and structured descriptions\n\n"
            "## Notes\n"
            "- Describe objectively, avoid over-interpretation\n"
            "- Pay attention to numerical units\n"
            "- Preserve technical terms and terminology\n"
        ),
        "mixed": (
            "Convert the entire page to Markdown format.\n\n"
            "## Requirements\n"
            "- Include all text, tables, and figure descriptions\n"
            "- Represent tables using Markdown table syntax\n"
            "- Describe charts/figures in detail with content and trends\n"
            "- Maintain the original page structure and order\n"
            "- Correctly identify boundaries of different regions\n\n"
            "## Notes\n"
            "- Pay attention to transitions between different regions\n"
            "- Preserve the logical structure of the page\n"
            "- If uncertain about something, label it honestly\n"
        ),
    }
    return prompts.get(name, "")

# Convenience functions for direct import
def TEXT_PROMPT(): return get_prompt("text")
def TABLE_PROMPT(): return get_prompt("table")
def FIGURE_PROMPT(): return get_prompt("figure")
def MIXED_PROMPT(): return get_prompt("mixed")

__all__ = ["get_prompt", "TEXT_PROMPT", "TABLE_PROMPT", "FIGURE_PROMPT", "MIXED_PROMPT"]
