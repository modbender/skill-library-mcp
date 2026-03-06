# Suggested ClawHub Comment (Transparency + Business Value)

v1.2.1: the runtime source is maintained directly in this repository and packaged with the skill. Install script copies repository source locally and runs `npm install --ignore-scripts` to fetch npm dependencies from the registry. Playwright downloads browser binaries on first browser-mode use; API-only tasks (including all Prospairrow tasks) do not require browser binaries.

Business value:

- no supply chain risk: all code ships with the skill, nothing fetched at runtime
- faster onboarding: one script installs the full runtime
- consistent MCP task execution for Prospairrow workflows
- improved reliability via documented runbooks and troubleshooting
