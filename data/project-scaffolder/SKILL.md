---
name: project-scaffolder
description: Scaffold new projects with best-practice templates for Next.js,
  Express, Python, Go, and more.
---


# Project Scaffolder

Generate project boilerplate with sensible defaults and best practices.

## Requirements

- Node.js 18+ (for JS/TS projects)
- Python 3.8+ (for Python projects)
- `git` for version control initialization

## Instructions

1. **Ask the user**: framework/template, project name, and target directory.
2. **Create the project** using the appropriate template below.
3. **Post-scaffold**: Initialize git, create `.gitignore`, and optionally install dependencies (ask first).

## Templates

### Next.js (App Router + TypeScript)
```bash
npx create-next-app@latest my-app --typescript --tailwind --eslint --app --src-dir --use-npm
```

### Express.js API
```bash
mkdir my-api && cd my-api
npm init -y
npm install express cors helmet dotenv
npm install -D nodemon
mkdir -p src/{routes,middleware}
```
Create `src/index.js` with Express boilerplate (cors, helmet, JSON parser, health endpoint).
Add to `package.json` scripts: `"dev": "nodemon src/index.js"`, `"start": "node src/index.js"`.

### Python CLI Tool
```bash
mkdir my-tool && cd my-tool
python3 -m venv .venv
source .venv/bin/activate
```
Create `main.py` with argparse skeleton, `requirements.txt`, and `README.md`.

### Python FastAPI
```bash
mkdir my-api && cd my-api
python3 -m venv .venv
pip install fastapi uvicorn
```
Create `main.py` with FastAPI app, health endpoint, and CORS middleware.

### Static HTML Site
```bash
mkdir my-site && cd my-site
mkdir -p {css,js,img}
```
Create `index.html` (responsive viewport, linked CSS/JS), `css/style.css`, `js/main.js`.

### Go CLI
```bash
mkdir my-cli && cd my-cli
go mod init github.com/user/my-cli
```
Create `main.go` with flag parsing skeleton.

### Common Post-scaffold Steps
```bash
git init
# Generate appropriate .gitignore (node_modules/, .env, .venv/, __pycache__/, etc.)
git add -A && git commit -m "chore: initial scaffold"
```

## Edge Cases

- **Directory exists**: Warn and ask before overwriting. Never silently overwrite.
- **Missing runtime**: Check `which node`/`which python3` before scaffolding. Report missing dependencies.
- **Custom templates**: If user describes a custom stack, combine relevant parts rather than using a fixed template.

## Security

- Never include real API keys or secrets in scaffolded `.env` files — use placeholders like `YOUR_API_KEY_HERE`.
- Always include `.env` in `.gitignore`.
- Set secure defaults (helmet for Express, CORS restrictions, etc.).

## Notes

- Ask before running `npm install` or `pip install` (may take time or need network).
- Adapt templates to user's preferences (TypeScript vs JS, npm vs yarn vs pnpm).
- Always create a README.md with basic setup instructions.
