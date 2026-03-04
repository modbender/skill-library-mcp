#!/bin/bash
# Initialize a new MLOps project with uv/git/VS Code

set -e

PROJECT_NAME="${1:-my-mlops-project}"

echo "🚀 Initializing MLOps project: $PROJECT_NAME"

# Create directory
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# Check tools
command -v uv >/dev/null 2>&1 || { echo "❌ uv not installed. Run: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
command -v git >/dev/null 2>&1 || { echo "❌ git not installed"; exit 1; }

# Initialize with uv
uv init

# Create src layout
mkdir -p "src/${PROJECT_NAME//-/_}"
touch "src/${PROJECT_NAME//-/_}/__init__.py"

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
.venv/
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing
.pytest_cache/
.coverage
htmlcov/

# Linting
.ruff_cache/
.mypy_cache/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local

# Data & Models (use DVC/LFS if needed)
data/
models/
outputs/
*.pkl
*.joblib
*.h5
*.pt

# OS
.DS_Store
Thumbs.db
EOF

# Create VS Code settings
mkdir -p .vscode
cat > .vscode/settings.json << 'EOF'
{
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": "explicit"
    }
  },
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.analysis.typeCheckingMode": "basic",
  "python.testing.pytestEnabled": true,
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true,
  "editor.rulers": [88],
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/.ruff_cache": true,
    "**/.venv": true
  }
}
EOF

# Initialize git
git init
git branch -M main
git add .
git commit -m "chore: initialize project with uv and vscode settings"

echo "✅ Project initialized!"
echo ""
echo "Next steps:"
echo "  cd $PROJECT_NAME"
echo "  uv add pandas loguru  # Add dependencies"
echo "  uv sync               # Create venv"
echo "  uv run python -c 'import sys; print(sys.executable)'  # Verify"
