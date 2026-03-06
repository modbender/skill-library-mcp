# xai-image-gen - Deployment Notes

## Package Contents

```
xai-image-gen/
├── LICENSE              # MIT license
├── README.md            # Quick start guide
├── SKILL.md             # Full documentation
├── skill.json           # Skill metadata
├── requirements.txt     # Python dependencies
├── xai-gen             # Main executable CLI
├── test.sh             # Test suite
└── *.png               # Demo/test images
```

## Installation Methods

### Method 1: Manual Install
```bash
cd ~/.openclaw/workspace/skills
git clone <repo> xai-image-gen
# or copy the folder
cd xai-image-gen
pip3 install -r requirements.txt
chmod +x xai-gen
export XAI_API_KEY="your-key"
```

### Method 2: ClawHub (when published)
```bash
clawhub install xai-image-gen
export XAI_API_KEY="your-key"
```

## Publishing to ClawHub

```bash
cd ~/.openclaw/workspace/skills/xai-image-gen
clawhub publish
```

## Testing

```bash
# Run test suite
./test.sh

# Manual test
./xai-gen "test prompt" --verbose
```

## Requirements

- Python 3.7+
- `requests` library (auto-installed from requirements.txt)
- xAI API key from https://console.x.ai
- Internet connection

## Platform Support

✅ Linux (Raspberry Pi tested)  
✅ macOS  
✅ Windows (via WSL or native Python)  
✅ ARM64/ARMv7 compatible

## API Details

- Endpoint: https://api.x.ai/v1/images/generations
- Model: grok-imagine-image
- Authentication: Bearer token (XAI_API_KEY)
- Output: JPEG images via URL or base64

## Troubleshooting

**API Key Error:**
```bash
export XAI_API_KEY="xai-your-key-here"
# Add to ~/.bashrc or ~/.zshrc for persistence
```

**Permission Error:**
```bash
chmod +x xai-gen
```

**Module Not Found:**
```bash
pip3 install requests
# or
pip3 install -r requirements.txt
```

## Version History

- **1.0.0** (2026-02-07): Initial release
  - Core CLI functionality
  - URL and base64 output formats
  - Batch generation support
  - Comprehensive error handling
  - ClawHub-ready packaging
