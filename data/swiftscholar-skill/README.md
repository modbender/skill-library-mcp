## swiftscholar-skill

This is a local Claude Skills project that teaches Claude how to use the SwiftScholar HTTP API to search, submit, and analyze academic papers.

### Directory structure

- `SKILL.md`  
  Defines the `swiftscholar-skill` skill name, description, when to use it, and how to call the various SwiftScholar API endpoints.

### How to use (Claude Desktop / Claude Code)

1. Place this project inside any code repository or working directory where you want to use the skill, ensuring this file and `.claude/skills/...` are present at the project root.
2. Open this project folder in Claude:
   - Claude Desktop: choose this folder when using “Open folder”.
   - Claude Code (IDE integrations): ensure the workspace root includes this project.
3. In conversation, when you need to:
   - search for papers,
   - submit PDFs/URLs for parsing,
   - fetch analysis markdown,
   - manage favorites or inspect account usage,
   Claude will rely on the `swiftscholar-api` skill instructions to use the SwiftScholar HTTP API.

> Note: you still need to configure `SWIFTSCHOLAR_API_KEY` in the actual HTTP execution environment (e.g., environment variables or a higher-level tool). This project only documents calling strategies and workflows; it does not store secrets.

### License

This project is licensed under the MIT License. See `LICENSE` for details.

