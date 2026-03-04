#!/bin/bash
# post-install hook for pdf-ocr-tool skill

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "📦 pdf-ocr-tool: Setting up environment..."

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ ollama is not installed. Please install ollama first:"
    echo "   curl -fsSL https://ollama.com/install.sh | sh"
    exit 1
fi

# Check if pdftoppm is installed
if ! command -v pdftoppm &> /dev/null; then
    echo "⚠️  pdftoppm not found. Install poppler-utils for PDF support:"
    echo "   sudo apt install poppler-utils # Debian/Ubuntu"
    echo "   brew install poppler # macOS"
    echo "   (Skipping PDF support, image OCR will still work)"
fi

# Navigate to skill directory
cd "${SKILL_DIR}"

# Run the main installation script
if [ -f "${SKILL_DIR}/hooks/install-deps.sh" ]; then
    bash "${SKILL_DIR}/hooks/install-deps.sh"
else
    echo "❌ install-deps.sh not found!"
    exit 1
fi

# Check Ollama service
echo ""
echo "Checking Ollama service..."
if curl -s "http://localhost:11434/api/tags" > /dev/null 2>&1; then
    echo "✅ Ollama service is running"
    # Check if GLM-OCR model is installed
    if ollama list | grep -q "glm-ocr"; then
        echo "✅ GLM-OCR model found"
    else
        echo "⚠️  GLM-OCR model not found. Install with:"
        echo "   ollama pull glm-ocr:q8_0"
    fi
else
    echo "⚠️  Ollama service is not running. Start with:"
    echo "   ollama serve"
fi

echo ""
echo "✅ pdf-ocr-tool setup complete!"
