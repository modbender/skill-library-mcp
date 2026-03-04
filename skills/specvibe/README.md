# SpecVibe

**An executable, spec-driven framework for building production-ready AI-native applications.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg )](https://opensource.org/licenses/MIT ) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg )](CONTRIBUTING.md) [![ClawHub](https://img.shields.io/badge/ClawHub-v1.0.0-blue )](https://clawhub.ai/skills/badideal-2046/SpecVibe ) 

SpecVibe is not just a collection of guidelines; it is a complete, structured, and executable framework designed to be integrated directly into modern AI coding assistants like Claude Code, OpenClaw, and Cursor. It enforces a rigorous, seven-stage development workflow, ensuring every project is architected, built, tested, and deployed according to 2026 industry best practices.

## Why SpecVibe?

Most AI development guides are passive documents. SpecVibe is an **active framework** that becomes part of your AI assistant's core logic. It bridges the gap between ad-hoc prompting ("vibe coding") and professional software engineering.

| Feature | Standard Guides | SpecVibe Framework |
| :--- | :--- | :--- |
| **Core Philosophy** | Vague best practices | Executable **Spec-Driven** workflow |
| **Coverage** | Focus on one area (e.g., security) | **Full Lifecycle**: Specify, Plan, Test, Implement, Review, Document, Deploy |
| **Integration** | Manual copy-pasting | **Direct Integration** with Claude Code, OpenClaw, etc. |
| **Security Standard** | General advice | Aligned with **OWASP Top 10:2025** |
| **AI Collaboration** | Basic prompt tips | **Delegate/Review/Own** model at every stage |
| **Completeness** | Missing key areas | Includes a11y, i18n, API versioning, and more |

## The 7-Stage Workflow

SpecVibe structures development into seven distinct stages, each with a clear goal and a quality gate.

1.  **Specify**: Define user journeys and requirements in a structured `spec.md`.
2.  **Plan**: Create the technical architecture, data models, and API contracts.
3.  **Test**: Write a comprehensive, failing test suite before writing any code.
4.  **Implement**: Generate code in small, validated chunks to make the tests pass.
5.  **Review**: Perform automated and human code reviews for quality and security.
6.  **Document**: Generate and refine user and developer documentation.
7.  **Deploy**: Automate deployment with CI/CD and ensure full observability.

## Getting Started

Choose the integration method for your preferred AI coding assistant.

### For Claude Code

1.  Clone this repository into your project's `.claude/skills/` directory.
2.  Create a `CLAUDE.md` file in your project root and import the framework:

    ```markdown
    # Project Development Framework
    @import .claude/skills/SpecVibe/SKILL.md
    ```

### For OpenClaw

1.  Clone this repository into `~/.openclaw/skills/`.
2.  OpenClaw will automatically detect and load SpecVibe as a core skill.

### For Cursor / Other Editors

1.  Clone this repository into your project's `.cursor-rules/` (or equivalent) directory.
2.  Use the `cursorrules-template.md` to set up your root rules file, instructing the AI to follow the SpecVibe framework.

## What's Inside?

-   **`SKILL.md`**: The core executable workflow that guides the AI.
-   **11 Reference Guides**: In-depth best practices for every domain, from backend architecture to accessibility.
-   **4 Templates**: Ready-to-use templates for specifications, API contracts, deployment checklists, and AI rule files.

## Contributing

Contributions are welcome. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to report bugs, suggest features, or submit pull requests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
