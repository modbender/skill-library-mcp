# arXiv Research Assistant

> Search, fetch, and analyze academic papers from arXiv.org directly from your AI assistant.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![OpenClaw](https://img.shields.io/badge/OpenClaw-compatible-purple.svg)

## Features

- 🔍 **Search Papers** - Query arXiv with natural language
- 📄 **Get Details** - Fetch full paper metadata and abstracts
- 📥 **Download PDFs** - Save papers locally for reading
- 📚 **Reading List** - Track papers in MongoDB (to-read, reading, read, cited)
- 🤖 **AI-Ready** - Works with OpenClaw, Claude, and any AI with shell access

## Installation

### For OpenClaw/ClawHub
```bash
clawhub install ractorrr/arxiv
```

### Manual Installation
```bash
git clone https://github.com/Ractorrr/arxiv-skill.git
cd arxiv-skill
pip install -r requirements.txt
```

## Usage

### Command Line
```bash
# Search for papers
python arxiv_tool.py search "LLM security attacks" --max 5

# Get paper details
python arxiv_tool.py get 2403.04957

# Download PDF
python arxiv_tool.py download 2403.04957

# Save to reading list (requires MongoDB)
python arxiv_tool.py save 2403.04957 --status to-read

# List saved papers
python arxiv_tool.py list
```

### With AI Assistant
Just ask naturally:
- "Search arXiv for prompt injection papers"
- "Find recent papers on LLM jailbreaking"
- "Get details for arXiv 2403.04957"
- "Add this paper to my reading list"

## Configuration

### Environment Variables
```bash
# Optional: MongoDB for paper tracking
export MONGODB_URI="mongodb+srv://..."
export MONGODB_DB_NAME="your_database"

# Optional: Custom papers directory
export ARXIV_PAPERS_DIR="./papers"
```

## Example Output

```
🔍 Found 5 papers for: "prompt injection attack LLM"

📄 Automatic and Universal Prompt Injection Attacks against Large Language Models
   ID: 2403.04957v1
   Authors: Xiaogeng Liu, Zhiyuan Yu, Yizhe Zhang (+2 more)
   Published: 2024-03-07
   Category: cs.AI
   PDF: https://arxiv.org/pdf/2403.04957v1
```

## Use Cases

- **Interview Prep**: Find cutting-edge papers to discuss
- **Content Creation**: Source material for technical posts
- **Literature Review**: Systematic paper discovery
- **Learning**: Deep dive into any technical topic

## License

MIT License - Use freely, attribution appreciated.

## Author

Created by [Ractor](https://github.com/Ractorrr) 🦅
