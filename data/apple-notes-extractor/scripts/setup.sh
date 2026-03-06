#!/bin/bash
# Apple Notes Extraction System Setup Script

set -e  # Exit on any error

echo "🍎 Setting up Apple Notes Extraction System..."
echo "=============================================="

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This system only works on macOS"
    exit 1
fi

print_success "Running on macOS"

# Check for required commands
check_command() {
    if command -v "$1" &> /dev/null; then
        print_success "$1 is available"
        return 0
    else
        print_warning "$1 is not available"
        return 1
    fi
}

print_status "Checking dependencies..."

# Check Python
if ! check_command python3; then
    print_error "Python 3 is required. Please install Python 3.8 or later."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(sys.version_info.major, sys.version_info.minor)" | tr ' ' '.')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
    print_success "Python $PYTHON_VERSION meets requirements"
else
    print_error "Python $PYTHON_VERSION is too old. Please upgrade to Python 3.8 or later."
    exit 1
fi

# Check osascript (should be built-in on macOS)
if ! check_command osascript; then
    print_error "osascript is not available. This is unusual for macOS."
    exit 1
fi

# Check Git
if ! check_command git; then
    print_warning "Git is not available. Ruby parser installation may fail."
    echo "You can install Git with: xcode-select --install"
fi

# Check Ruby (optional, will be handled later)
if check_command ruby; then
    RUBY_VERSION=$(ruby -v | grep -o '[0-9]\+\.[0-9]\+')
    print_success "Ruby $RUBY_VERSION is available"
else
    print_warning "Ruby is not available. Full extraction method will be limited."
    echo "You can install Ruby with: brew install ruby"
fi

# Check Bundle (Ruby gem manager)
if check_command bundle; then
    print_success "Bundler is available"
else
    print_warning "Bundler is not available. Installing..."
    if command -v gem &> /dev/null; then
        gem install bundler
        print_success "Bundler installed"
    else
        print_warning "Could not install Bundler. Ruby parser may not work."
    fi
fi

# Create directory structure
print_status "Creating directory structure..."

cd "$ROOT_DIR"

mkdir -p output/{json,markdown,attachments}
mkdir -p configs
mkdir -p tools
mkdir -p workflows

print_success "Directory structure created"

# Make scripts executable
print_status "Setting up script permissions..."

chmod +x scripts/*.py scripts/*.sh 2>/dev/null || true

print_success "Script permissions configured"

# Test Apple Notes access
print_status "Testing Apple Notes access..."

# Simple test to see if Notes app is accessible
TEST_SCRIPT='tell application "Notes" to get name'
if osascript -e "$TEST_SCRIPT" &>/dev/null; then
    print_success "Apple Notes is accessible via AppleScript"
else
    print_warning "Could not access Apple Notes. You may need to:"
    echo "  1. Grant automation permissions in System Preferences > Security & Privacy > Privacy > Automation"
    echo "  2. Allow Terminal (or your terminal app) to control Notes"
    echo "  3. Make sure Notes app is installed and has been opened at least once"
fi

# Create default configuration
print_status "Creating default configuration..."

EXTRACTOR_CONFIG="$ROOT_DIR/configs/extractor.json"
if [[ ! -f "$EXTRACTOR_CONFIG" ]]; then
    cat > "$EXTRACTOR_CONFIG" << 'EOF'
{
  "methods": {
    "simple": {
      "enabled": true,
      "timeout": 30,
      "include_metadata": true
    },
    "full": {
      "enabled": true,
      "timeout": 300,
      "extract_attachments": true,
      "preserve_formatting": true
    }
  },
  "output": {
    "formats": ["json", "markdown"],
    "compress_attachments": false,
    "max_note_size_mb": 10
  },
  "privacy": {
    "exclude_patterns": ["password", "secret", "private"],
    "encrypt_sensitive": false
  },
  "workflows": {
    "auto_export_enabled": false,
    "export_schedule": "daily",
    "integration_endpoints": []
  }
}
EOF
    print_success "Default configuration created"
else
    print_success "Configuration file already exists"
fi

# Create monitor configuration
MONITOR_CONFIG="$ROOT_DIR/configs/monitor.json"
if [[ ! -f "$MONITOR_CONFIG" ]]; then
    cat > "$MONITOR_CONFIG" << 'EOF'
{
  "monitoring": {
    "enabled": false,
    "check_interval_minutes": 30,
    "detect_changes": true,
    "auto_extract_new": true
  },
  "triggers": {
    "new_note_threshold": 1,
    "modification_threshold": 5,
    "batch_processing": true
  },
  "notifications": {
    "enabled": false,
    "methods": ["console"],
    "webhook_url": null
  }
}
EOF
    print_success "Monitor configuration created"
fi

# Create workflow integration examples
WORKFLOW_DIR="$ROOT_DIR/workflows"
if [[ ! -f "$WORKFLOW_DIR/export-to-obsidian.py" ]]; then
    cat > "$WORKFLOW_DIR/export-to-obsidian.py" << 'EOF'
#!/usr/bin/env python3
"""
Example workflow: Export Apple Notes to Obsidian vault
"""
import json
import shutil
from pathlib import Path

def export_to_obsidian(notes_file, obsidian_vault_path):
    """Export notes to Obsidian vault"""
    vault_path = Path(obsidian_vault_path)
    notes_dir = vault_path / "Apple Notes"
    notes_dir.mkdir(exist_ok=True)
    
    with open(notes_file) as f:
        notes = json.load(f)
    
    for note in notes:
        filename = f"{note['title'].replace('/', '-')}.md"
        filepath = notes_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(f"# {note['title']}\n\n")
            f.write(f"Created: {note['created']}\n")
            f.write(f"Modified: {note['modified']}\n\n")
            f.write(note['body'])

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python export-to-obsidian.py <notes_json_file> <obsidian_vault_path>")
        sys.exit(1)
    
    export_to_obsidian(sys.argv[1], sys.argv[2])
EOF
    chmod +x "$WORKFLOW_DIR/export-to-obsidian.py"
    print_success "Workflow examples created"
fi

# Test extraction
print_status "Testing basic extraction..."

cd "$ROOT_DIR"
if python3 scripts/extract-notes.py --method simple --output-dir output/test 2>/dev/null; then
    print_success "Basic extraction test successful"
    # Clean up test output
    rm -rf output/test 2>/dev/null || true
else
    print_warning "Basic extraction test failed. You may need to configure permissions."
fi

# Final setup summary
echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
print_success "Apple Notes Extraction System is ready to use"
echo ""
echo "📖 Quick Start:"
echo "  cd $(basename "$ROOT_DIR")"
echo "  python3 scripts/extract-notes.py --method simple    # Fast text extraction"
echo "  python3 scripts/extract-notes.py --method full      # Complete extraction with attachments"
echo "  python3 scripts/extract-notes.py --method auto      # Automatic method selection"
echo ""
echo "🔧 Configuration:"
echo "  Edit configs/extractor.json to customize extraction settings"
echo "  Edit configs/monitor.json to set up automatic monitoring"
echo ""
echo "📁 Output:"
echo "  JSON files: output/json/"
echo "  Markdown files: output/markdown/"
echo "  Attachments: output/attachments/"
echo ""

if [[ ! -f "$ROOT_DIR/tools/apple_cloud_notes_parser/notes_cloud_ripper.rb" ]]; then
    print_warning "Ruby parser not installed yet"
    echo "  Run with --method full to automatically install the Ruby parser"
    echo "  Or manually: git clone https://github.com/threeplanetssoftware/apple_cloud_notes_parser.git tools/"
fi

print_status "For help and documentation, see README.md"