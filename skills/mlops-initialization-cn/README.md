# MLOps 项目初始化

Modern Python project setup using `uv` package manager.

## Features

- 📦 **Project Initialization** - Create complete project structure
- 📋 **Configuration Templates** - pyproject.toml, VS Code settings
- 🔧 **Git Setup** - .gitignore, initial commit
- ✅ **Validation** - Ensure environment correctness

## Quick Start

```bash
# Initialize new project
./scripts/init-project.sh my-mlops-project

# Add dependencies
uv add pandas numpy scikit-learn

# Sync environment
uv sync
```

## Author

Converted from [MLOps Coding Course](https://github.com/MLOps-Courses/mlops-coding-skills)

## License

MIT
