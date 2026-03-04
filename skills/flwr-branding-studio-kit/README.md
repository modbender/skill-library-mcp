# FLWR Branding Studio Kit

> **Transform your AI coding assistant into a Senior Brand Strategist.**

This repository enables you to deploy an autonomous branding agent capable of generating high-level strategic assets (Golden Circle, Archetypes, Tone of Voice) based on raw client intelligence. It uses a strict **"Anti-Hallucination"** and **"Anti-Slop"** protocol to ensure professional-grade results.

Developed by **FLWR Branding Studio** ([@flwr.branding](https://instagram.com/flwr.branding))


## 🚀 Key Features

*   **RACE Framework Integration**: Deep integration of the Research, Action, Context, Example methodology.
*   **Context Shielding Protocol**: Prevents cross-contamination between clients. The structure is fixed; the content is fluid.
*   **Anti-Slop Writing Checks**: Automated rules to prevent generic AI copywriting (no "delve", "tapestry", or sequential adjectives).
*   **🎨 Asset Output:** Generates assets in a specific Markdown format.
*   **Automated Project Setup**: One-command initialization for new client projects.

## 📦 What's Included

*   **`.agent/rules/`**: The "brain" of the strategist (`branding_agent_rules.md`).
*   **`.agent/workflows/`**: The step-by-step logic for executing branding projects.
*   **`.agent/templates/`**: The core templates (Golden Circle, Persona, Voice, etc.).
*   **`scripts/`**: Automation tools for project scaffolding.

## 🌍 Compatibility

*   **Operating Systems**: Windows, macOS, Linux (Universal Node.js support).
*   **IDEs**: Optimized for **Cursor**, **Windsurf**, and **VS Code**, but works in ANY editor (Zed, Sublime, etc.).
*   **Requirements**: [Node.js](https://nodejs.org/) (v14 or higher).

## 🛠️ Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/vansearch/FLWR-Branding-Studio-Kit-.git
    cd FLWR-Branding-Studio-Kit-
    ```

2.  **Install Dependencies**:
    ```bash
    npm install
    # or
    yarn
    ```

3.  **Agent Configuration**:
    *   If using Cursor, Windsurf, or similar: Ensure the `.agent` folder is in your workspace root.
    *   If using a custom LLM script: Load `.agent/rules/branding_agent_rules.md` into the system prompt.

## ⚡ Workflow: How to Run a Project

### Phase 1: Initialization
Start a new project for a client. This creates the directory structure and copies the necessary templates.

```bash
# Using NPX (Local)
npx flwr-kit "Client Name"
```
*Creates: `clients/Client_Name/` with `client_intel/` and `strategy_output/` folders.*

### Phase 2: Intelligence Gathering
Dump all raw data into the `client_intel` folder of your new project.
*   **Transcripts**: Meeting notes, interview recordings (text).
*   **Briefings**: PDF briefs, emails.
*   **Competitors**: Links or text dumps about competitors per the *Strategic Framework*.

### Phase 3: The Strategist (AI Interaction)
Open your AI assistant (**Claude 4.5 Sonnet (or higher) or Opus is highly recommended** for superior copywriting and nuance) and point it to the project.

1.  **Activate Protocol**:
    > "Start branding project for [Client Name]."

2.  **Interrogation Mode** (Automatic):
    The agent will read your `client_intel` and stop you if data is missing (e.g., "I don't see target audience data. Please provide X").

3.  **Strategy Generation**:
    The agent will process the data through the **RACE Framework** and fill the templates in `strategy_output/brand_assets_md/`. It uses the **Reality Check** loop to verify every claim against your provided documents.

### Phase 4: Quality Validtion
Before finalizing, the agent runs the **Writing Quality Check**:
*   Checks for forbidden words (AI cliches).
*   Ensures strict capitalization rules.
*   Verifies distinctiveness vs. competitors.


## 📁 Repository Structure

```text
.
├── .agent/                  # AGENT BRAIN
│   ├── rules/               # Personality & strict logic constraints
│   ├── templates/           # The source of truth for deliverables
│   └── workflows/           # Step-by-step execution chains
├── docs/                    # Reference documents (Frameworks, Guides)
├── bin/                     # CLI EXECUTABLES
│   └── cli.js               # CLI entry point (npx flwr-kit)
├── package.json             # Node.js dependencies & bin config
├── README.md                # This manual
```

## 🤝 Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to improve the agent's logic or add new templates.

## 📄 License
MIT
