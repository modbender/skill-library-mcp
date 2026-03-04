# Auto Context Manager

**AI-Powered Automatic Project Context Management with Adaptive Learning**

<div align="center">

![Version](https://img.shields.io/badge/version-1.1.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-purple)
![ClawdHub](https://img.shields.io/badge/clawdhub-available-orange)

**Smart context switching that learns and adapts to your workflow**

[Features](#features) • [Installation](#installation) • [Quick Start](#quick-start)

</div>

---

## Features

### Core Capabilities

- **Auto Project Detection** - Automatically detects projects from your messages
- **Context Switching** - Seamlessly switches between project contexts
- **Keyword Matching** - Simple and effective keyword-based detection
- **Adaptive Learning** - Learns and improves from your interactions

### Security & Privacy

- **100% Local** - No external requests, no cloud dependencies
- **No API Keys** - Works offline, fully self-contained
- **No Telemetry** - Zero data collection or analytics
- **Open Source** - Transparent and auditable code
- **Data Ownership** - Your data stays on your machine

---

## Installation

### Method 1: ClawdHub (Recommended)

```bash
clawdhub install auto-context-manager
```

### Method 2: Manual Installation

Copy the skill folder to your Clawdbot skills directory.

---

## Quick Start

The system auto-initializes on first use, creating `~/.auto-context/` with default configuration.

### Use it programmatically

```python
from auto_context_manager import AutoContextManager

acm = AutoContextManager()

# Detect project from message
project, confidence = acm.detect_project("Your message here")
print(f"Project: {project} (confidence: {confidence})")
```

### Use via CLI

```bash
python acm.py detect "your message"
python acm.py list
python acm.py current
python acm.py switch project_id
```

---

## Configuration

Edit `~/.auto-context/projects.json` to customize projects:

```json
{
  "projects": {
    "default": {
      "name": "Default / General",
      "description": "General messages and default context",
      "keywords": ["hello", "help", "status", "general"]
    },
    "my-project": {
      "name": "My Project",
      "keywords": ["keyword1", "keyword2"]
    }
  },
  "current_project": "default"
}
```

---

## Requirements

- Python 3.8 or higher
- Optional: ChromaDB for vector-based semantic matching