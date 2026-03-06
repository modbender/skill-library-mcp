#!/bin/bash
# Dropbox KB Auto - Dependency Installer

set -e

echo "📦 Installing Dropbox KB Auto dependencies..."

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Detected Linux"
    
    # Check if Debian/Ubuntu
    if command -v apt-get &> /dev/null; then
        echo "  Installing system packages via apt..."
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr tesseract-ocr-eng tesseract-ocr-deu poppler-utils python3-pip
    elif command -v yum &> /dev/null; then
        echo "  Installing system packages via yum..."
        sudo yum install -y tesseract tesseract-langpack-eng tesseract-langpack-deu poppler-utils python3-pip
    else
        echo "  ⚠️  Unknown package manager. Please install manually:"
        echo "     - tesseract-ocr (with eng + deu language packs)"
        echo "     - poppler-utils"
    fi
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 Detected macOS"
    
    if command -v brew &> /dev/null; then
        echo "  Installing via Homebrew..."
        brew install tesseract tesseract-lang poppler python3
    else
        echo "  ⚠️  Homebrew not found. Install from https://brew.sh"
        exit 1
    fi
else
    echo "  ⚠️  Unsupported OS: $OSTYPE"
    exit 1
fi

# Install Python dependencies
echo "  Installing Python packages..."
pip3 install --user pypdf openpyxl python-pptx python-docx

# Verify installations
echo ""
echo "✅ Verifying installations..."

check_cmd() {
    if command -v $1 &> /dev/null; then
        echo "  ✓ $1"
    else
        echo "  ✗ $1 - NOT FOUND"
        return 1
    fi
}

check_python_pkg() {
    if python3 -c "import $1" &> /dev/null; then
        echo "  ✓ python: $1"
    else
        echo "  ✗ python: $1 - NOT FOUND"
        return 1
    fi
}

check_cmd tesseract
check_cmd pdftoppm
check_python_pkg pypdf
check_python_pkg openpyxl
check_python_pkg pptx
check_python_pkg docx

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Create Dropbox app at https://www.dropbox.com/developers/apps"
echo "  2. Copy credentials to ~/.openclaw/.env (see .env.example)"
echo "  3. Edit config.json to customize folders"
echo "  4. Run: python3 dropbox-sync.py"
