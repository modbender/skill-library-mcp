# 🤖 AI Agent Tools

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Issues](https://img.shields.io/github/issues/cerbug45/ai-agent-tools.svg)](https://github.com/cerbug45/ai-agent-tools/issues)

A comprehensive Python utility library designed for AI agents. Provides ready-to-use tools for file operations, text processing, data transformation, memory management, and validation.

## ✨ Features

- 🗂️ **File Operations** - Read, write, list, and check files
- 📝 **Text Processing** - Extract emails, URLs, phone numbers; clean and summarize text
- 🔄 **Data Transformation** - Convert between JSON, CSV, and dictionary formats
- 🧰 **Utilities** - Timestamps, ID generation, calculations
- 💾 **Memory Management** - Store and retrieve data during execution
- ✅ **Validation** - Validate emails, URLs, and phone numbers

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/cerbug45/ai-agent-tools.git
cd ai-agent-tools

# Or just download the file
wget https://raw.githubusercontent.com/cerbug45/ai-agent-tools/main/ai_agent_tools.py
```

### Basic Usage

```python
from ai_agent_tools import FileTools, TextTools, DataTools

# Read a file
content = FileTools.read_file("data.txt")

# Extract emails
emails = TextTools.extract_emails(content)

# Save as JSON
DataTools.save_json({"emails": emails}, "output.json")
```

## 📖 Documentation

For full documentation, see [SKILL.md](SKILL.md)

### Available Tool Categories

| Category | Description | Key Functions |
|----------|-------------|---------------|
| **FileTools** | File operations | `read_file`, `write_file`, `list_files` |
| **TextTools** | Text processing | `extract_emails`, `extract_urls`, `word_count` |
| **DataTools** | Data conversion | `save_json`, `load_json`, `csv_to_dict` |
| **UtilityTools** | General utilities | `get_timestamp`, `generate_id`, `calculate_percentage` |
| **MemoryTools** | Memory management | `store`, `retrieve`, `list_keys` |
| **ValidationTools** | Data validation | `is_valid_email`, `is_valid_url`, `is_valid_phone` |

## 💡 Examples

### Extract Contact Information

```python
from ai_agent_tools import TextTools, ValidationTools

text = """
Contact us:
Email: support@example.com
Phone: 0532 123 45 67
Website: https://example.com
"""

# Extract information
emails = TextTools.extract_emails(text)
phones = TextTools.extract_phone_numbers(text)
urls = TextTools.extract_urls(text)

# Validate
for email in emails:
    if ValidationTools.is_valid_email(email):
        print(f"Valid email: {email}")
```

### Process and Save Data

```python
from ai_agent_tools import DataTools, UtilityTools

# Create structured data
data = [
    {
        "id": UtilityTools.generate_id("user_1"),
        "name": "Alice",
        "timestamp": UtilityTools.get_timestamp()
    },
    {
        "id": UtilityTools.generate_id("user_2"),
        "name": "Bob",
        "timestamp": UtilityTools.get_timestamp()
    }
]

# Save as JSON
DataTools.save_json(data, "users.json")

# Convert to CSV
csv = DataTools.dict_to_csv(data)
print(csv)
```

### Use Memory for State Management

```python
from ai_agent_tools import MemoryTools

memory = MemoryTools()

# Store session data
memory.store("user_id", "12345")
memory.store("session_start", "2026-02-15 10:00:00")

# Retrieve later
user_id = memory.retrieve("user_id")
print(f"Current user: {user_id}")

# List all stored keys
print(f"Stored keys: {memory.list_keys()}")
```

## 🔧 Integration Examples

### With LangChain

```python
from langchain.tools import Tool
from ai_agent_tools import FileTools

def create_agent_tools():
    return [
        Tool(
            name="ReadFile",
            func=FileTools.read_file,
            description="Read contents of a file"
        )
    ]
```

### With OpenAI Function Calling

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "extract_emails",
            "description": "Extract email addresses from text",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to extract emails from"}
                },
                "required": ["text"]
            }
        }
    }
]
```

## 🧪 Testing

Run the built-in test suite:

```bash
python ai_agent_tools.py
```

## 📋 Requirements

- Python 3.7 or higher
- No external dependencies (uses only standard library)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**GitHub:** [@cerbug45](https://github.com/cerbug45)

## 🙏 Acknowledgments

- Built for AI agents and automation workflows
- Designed with simplicity and usability in mind
- Zero dependencies for easy deployment

## 📊 Project Stats

- **Total Functions:** 25+
- **Tool Categories:** 6
- **Lines of Code:** ~300
- **Test Coverage:** Included

## 🔗 Links

- [Full Documentation](SKILL.md)
- [Issue Tracker](https://github.com/cerbug45/ai-agent-tools/issues)
- [GitHub Repository](https://github.com/cerbug45/ai-agent-tools)

---

**Made with ❤️ for AI Agents**
