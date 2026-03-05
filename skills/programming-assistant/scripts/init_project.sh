#!/bin/bash
# Script to initialize a new programming project with Claude
# Usage: ./init_project.sh <project_name> <directory>

PROJECT_NAME="$1"
TARGET_DIR="$2"

if [ -z "$PROJECT_NAME" ] || [ -z "$TARGET_DIR" ]; then
    echo "Usage: $0 <project_name> <target_directory>"
    exit 1
fi

echo "Initializing new project: $PROJECT_NAME in $TARGET_DIR"

# Create project directory if it doesn't exist
mkdir -p "$TARGET_DIR/$PROJECT_NAME"

# Create standard project structure
mkdir -p "$TARGET_DIR/$PROJECT_NAME"/{src,tests,docs,config}

# Create basic README
cat > "$TARGET_DIR/$PROJECT_NAME/README.md" << EOF
# $PROJECT_NAME

## Description
Brief description of the project goes here.

## Setup
Instructions for setting up the project locally.

## Usage
How to run and use the project.

## Contributing
Guidelines for contributing to the project.
EOF

# Create a basic .gitignore if git is available
if command -v git >/dev/null 2>&1; then
    cd "$TARGET_DIR/$PROJECT_NAME"
    git init
    cat > .gitignore << EOF
# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/

# Build outputs
build/
dist/
*.egg-info/
*.so

# Logs
*.log
logs/

# Environment variables
.env
.env.local

# OS generated files
.DS_Store
Thumbs.db
EOF
fi

echo "Project $PROJECT_NAME initialized successfully in $TARGET_DIR"