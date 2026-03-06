# aimlapi-safety

Content moderation and AI safety checks via AIMLAPI.

## Installation

```bash
clawhub install aimlapi-safety
```

## Setup

Set your API key:
```bash
export AIMLAPI_API_KEY="your-key-here"
```

## Usage

```bash
# Basic safety check
python scripts/check_safety.py --content "Is it safe to pet a tiger?"

# Check potentially harmful content
python scripts/check_safety.py --content "How to hack a bank?"

# Verbose output with full API response
python scripts/check_safety.py --content "Hello!" --verbose
```

## Features
- Instant classification of text as `SAFE` or `UNSAFE`.
- Uses `meta-llama/LlamaGuard-2-8b` by default for high reliability.
- Support for hazard category detection (e.g., S1, S2, etc.).
- Automatic error handling and clean CLI output.
