# Installation Guide

Complete installation guide for AI Agent Tools library.

## 📦 Installation Methods

### Method 1: Direct File Download (Recommended for Quick Start)

The simplest way to get started:

```bash
# Download the main file
wget https://raw.githubusercontent.com/cerbug45/ai-agent-tools/main/ai_agent_tools.py

# Or use curl
curl -O https://raw.githubusercontent.com/cerbug45/ai-agent-tools/main/ai_agent_tools.py
```

Then import in your Python code:

```python
from ai_agent_tools import FileTools, TextTools, DataTools
```

### Method 2: Clone from GitHub (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/cerbug45/ai-agent-tools.git

# Navigate to the directory
cd ai-agent-tools

# Test the installation
python ai_agent_tools.py
```

### Method 3: Install as Python Package (Coming Soon)

```bash
# Using pip (when published to PyPI)
pip install ai-agent-tools

# From GitHub directly
pip install git+https://github.com/cerbug45/ai-agent-tools.git
```

### Method 4: Add as Git Submodule (For Larger Projects)

```bash
# Add to your project as a submodule
git submodule add https://github.com/cerbug45/ai-agent-tools.git libs/ai-agent-tools

# Update the submodule
git submodule update --init --recursive
```

## 🐍 Python Version Requirements

- **Minimum:** Python 3.7
- **Recommended:** Python 3.9 or higher
- **Tested on:** Python 3.7, 3.8, 3.9, 3.10, 3.11

Check your Python version:

```bash
python --version
# or
python3 --version
```

## 📋 System Requirements

### Operating Systems
- ✅ Linux (Ubuntu, Debian, CentOS, etc.)
- ✅ macOS (10.14+)
- ✅ Windows (10/11)

### Dependencies
**None!** This library uses only Python's standard library.

### Optional Development Tools
```bash
# For testing
pip install pytest

# For code formatting
pip install black

# For linting
pip install flake8
```

## 🚀 Quick Setup Guide

### Step 1: Download or Clone

Choose one of the installation methods above.

### Step 2: Verify Installation

```bash
# Test the module
python -c "from ai_agent_tools import FileTools; print('✓ Installation successful!')"
```

### Step 3: Run Tests

```bash
# Run the built-in test suite
python ai_agent_tools.py
```

Expected output:
```
=== AI Ajanları İçin Araçlar Kütüphanesi ===

1. Dosya Araçları:
   ...
✓ Tüm araçlar test edildi!
```

## 🔧 Project Setup

### For Single-File Projects

```bash
# Your project structure
my-project/
├── ai_agent_tools.py  # Downloaded file
└── main.py            # Your code
```

In `main.py`:
```python
from ai_agent_tools import FileTools, TextTools

# Your code here
```

### For Multi-File Projects

```bash
# Recommended project structure
my-project/
├── libs/
│   └── ai_agent_tools.py
├── src/
│   └── main.py
├── tests/
│   └── test_agent.py
└── requirements.txt
```

In your code:
```python
import sys
sys.path.append('./libs')
from ai_agent_tools import FileTools, TextTools
```

### For Python Packages

```bash
# Package structure
my-package/
├── setup.py
├── my_package/
│   ├── __init__.py
│   ├── agent.py
│   └── utils/
│       └── ai_agent_tools.py
└── tests/
```

## 🐳 Docker Setup

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy the library
COPY ai_agent_tools.py /app/

# Copy your application
COPY . /app/

CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t my-ai-agent .
docker run my-ai-agent
```

## 🌐 Virtual Environment Setup

### Using venv (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install in virtual environment
curl -O https://raw.githubusercontent.com/cerbug45/ai-agent-tools/main/ai_agent_tools.py

# Deactivate when done
deactivate
```

### Using conda

```bash
# Create conda environment
conda create -n aiagent python=3.9

# Activate
conda activate aiagent

# Download the library
wget https://raw.githubusercontent.com/cerbug45/ai-agent-tools/main/ai_agent_tools.py

# Deactivate when done
conda deactivate
```

## 🔍 Troubleshooting

### Issue: Module Not Found

**Error:**
```
ModuleNotFoundError: No module named 'ai_agent_tools'
```

**Solution:**
```bash
# Check if file is in the same directory
ls ai_agent_tools.py

# Or add to Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/directory"
```

### Issue: Permission Denied

**Error:**
```
PermissionError: [Errno 13] Permission denied
```

**Solution:**
```bash
# Make file executable (Linux/macOS)
chmod +x ai_agent_tools.py

# Or run with appropriate permissions
sudo python ai_agent_tools.py
```

### Issue: Python Version

**Error:**
```
SyntaxError: invalid syntax
```

**Solution:**
- Ensure you're using Python 3.7+
- Update Python if needed
- Use `python3` instead of `python`

### Issue: Import Errors in Windows

**Solution:**
```python
# Use forward slashes in paths
filepath = "data/file.txt"  # Good
# Not: filepath = "data\\file.txt"
```

## 📱 IDE Setup

### Visual Studio Code

1. Install Python extension
2. Add to workspace:
```json
{
    "python.analysis.extraPaths": ["./libs"]
}
```

### PyCharm

1. Right-click on folder containing `ai_agent_tools.py`
2. Select "Mark Directory as" → "Sources Root"

### Jupyter Notebook

```python
# Add to first cell
import sys
sys.path.append('./path/to/library')
from ai_agent_tools import FileTools, TextTools
```

## 🧪 Running Tests

### Basic Test
```bash
python ai_agent_tools.py
```

### With pytest (if installed)
```bash
pytest tests/ -v
```

### Create Your Own Tests
```python
# test_agent.py
from ai_agent_tools import FileTools, TextTools

def test_email_extraction():
    text = "Contact: user@example.com"
    emails = TextTools.extract_emails(text)
    assert len(emails) == 1
    assert emails[0] == "user@example.com"

if __name__ == "__main__":
    test_email_extraction()
    print("✓ All tests passed!")
```

## 📚 Next Steps

After installation:

1. Read the [SKILL.md](SKILL.md) for complete documentation
2. Check [README.md](README.md) for examples
3. Review the code for available functions
4. Start building your AI agent!

## 🆘 Getting Help

- **Issues:** https://github.com/cerbug45/ai-agent-tools/issues
- **Discussions:** https://github.com/cerbug45/ai-agent-tools/discussions
- **Documentation:** https://github.com/cerbug45/ai-agent-tools/blob/main/SKILL.md

## 📝 License

MIT License - see [LICENSE](LICENSE) file

---

**Installation complete! Happy coding! 🚀**
