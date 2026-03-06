#!/bin/bash
# install-deps.sh - Install Python dependencies for pdf-ocr-tool skill
# Priority: Local copy > GitHub raw URL

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_NAME="pdf-ocr-tool"
GITHUB_USER="nala0222"
GITHUB_REPO="pdf-ocr-tool"
GITHUB_BRANCH="master"

echo "📦 Installing dependencies for ${SKILL_NAME}..."

# Function to copy file from local or GitHub
copy_file() {
    local file=$1
    local local_path="${SKILL_DIR}/${file}"
    local github_url="https://raw.githubusercontent.com/${GITHUB_USER}/${GITHUB_REPO}/refs/heads/${GITHUB_BRANCH}/${file}"
    
    if [ -f "${local_path}" ]; then
        echo "✅ Found local ${file}"
        cp "${local_path}" "${SKILL_DIR}/.tmp_${file}"
        return 0
    else
        echo "⚠️  Local ${file} not found, trying GitHub..."
        if curl -sLf "${github_url}" -o "${SKILL_DIR}/.tmp_${file}"; then
            echo "✅ Downloaded ${file} from GitHub"
            return 0
        else
            echo "❌ Failed to get ${file} from both local and GitHub"
            return 1
        fi
    fi
}

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
}

# Navigate to skill directory
cd "${SKILL_DIR}"

# Copy pyproject.toml and uv.lock
echo "📋 Copying dependency files..."
copy_file "pyproject.toml" || exit 1
copy_file "uv.lock" || exit 1

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "🔧 Creating virtual environment..."
    uv venv
fi

# Install dependencies
echo "📥 Installing dependencies..."
source .venv/bin/activate
uv sync

# Clean up temporary files
rm -f .tmp_pyproject.toml .tmp_uv.lock

# Verify installation
echo ""
echo "✅ Dependencies installed successfully!"
echo ""
echo "Verifying installation..."
python3 -c "import requests; import PIL; print('✅ All packages imported successfully')"

echo ""
echo "🎉 ${SKILL_NAME} setup complete!"
echo ""
echo "Usage:"
echo "  # Auto-detect content type (recommended)"
echo "  python ocr_tool.py --input document.pdf --output result.md"
echo ""
echo "  # Specific mode"
echo "  python ocr_tool.py --input document.pdf --output result.md --mode text"
echo "  python ocr_tool.py --input document.pdf --output result.md --mode table"
echo "  python ocr_tool.py --input document.pdf --output result.md --mode figure"
echo ""
echo "  # Mixed mode (split page into regions)"
echo "  python ocr_tool.py --input document.pdf --output result.md --granularity region"
echo ""
echo "  # Custom configuration"
echo "  python ocr_tool.py --input image.png --output result.md --host localhost --port 11434 --model glm-ocr:q8_0"
