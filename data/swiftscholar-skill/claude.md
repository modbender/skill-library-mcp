## Project overview: swiftscholar-skill

This project provides a local skill based on the **Claude Skills template**:

- Skill name: `swiftscholar-skill`
- Location: `SKILL.md`
- Purpose: guide Claude on how to use the **SwiftScholar HTTP API** to:
  - perform keyword and vector searches over papers,
  - submit URLs / PDFs for parsing,
  - retrieve paper analysis markdown or raw markdown,
  - manage favorite folders and favorite papers,
  - inspect account usage and parse history.

When a conversation involves literature search, paper analysis, or SwiftScholar usage, Claude will consult this skill, choose appropriate API endpoints and parameters, and return organized results (e.g., paper lists, summaries, comparative analysis).

To extend this project later:

- Add more workflow examples to `SKILL.md` as needed; and/or
- Add extra reference files (for example `reference.md`) in the same skill directory and link them from `SKILL.md`.

