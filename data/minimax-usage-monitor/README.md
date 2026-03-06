# MiniMax Coding Plan Usage Monitor

Monitor your MiniMax Coding Plan usage via API.

## Quick Start

### 1. Get API Key

1. Visit [MiniMax Console](https://platform.minimaxi.com/user-center/payment/coding-plan)
2. Create a Coding Plan Key
3. Copy the key

### 2. Set Environment Variable

**Windows:**
```powershell
[System.Environment]::SetEnvironmentVariable("MINIMAX_CODING_KEY", "your-key", "User")
```

**Linux/Mac:**
```bash
export MINIMAX_CODING_KEY="your-key"
```

### 3. Run

```bash
pip install requests
python check_minimax.py
```

## Commands

```bash
# Basic usage
python check_minimax.py

# With alerts
python check_minimax.py --notify

# JSON output
python check_minimax.py --json
```

## Requirements

- Python 3.8+
- requests

## Integration

Add to OpenClaw HEARTBEAT.md:
```markdown
### MiniMax Usage (Hourly)
- Run: python check_minimax.py --notify
```
